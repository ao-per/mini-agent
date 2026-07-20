from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from tools.base import Tool


class SearchNotesArgs(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    query: str = Field(
        min_length=1,
        description=(
            "The keyword or phrase to search for in markdown notes. "
            "Case-insensitive substring matching is used."
        ),
    )
    max_results: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of matching files to return (1-50).",
    )


class SearchNotesTool(Tool):
    MAX_SCANNED_FILES = 500
    MAX_FILE_SIZE_BYTES = 1_000_000
    MAX_MATCHED_LINES_PER_FILE = 20
    MAX_LINE_LENGTH = 500

    name = "search_notes"
    description = (
        "Search local markdown (.md) files for notes matching a keyword. "
        "Returns a list of matching files with the file path and "
        "lines containing the keyword."
    )
    args_model = SearchNotesArgs

    def __init__(self, notes_root: Path) -> None:
        self.notes_root = notes_root.expanduser().resolve()

    def run(self, arguments: BaseModel) -> list[dict[str, str]]:
        if not isinstance(arguments, SearchNotesArgs):
            raise TypeError("Expected SearchNotesArgs")

        root = self.notes_root
        if not root.is_dir():
            raise ValueError(f"Notes directory does not exist: {root}")

        keyword = arguments.query.lower()
        results: list[dict[str, str]] = []
        count = 0

        scanned_files = 0
        for md_file in sorted(root.rglob("*.md")):
            if count >= arguments.max_results:
                break

            if scanned_files >= self.MAX_SCANNED_FILES:
                break
            scanned_files += 1

            try:
                if md_file.is_symlink():
                    continue

                resolved_file = md_file.resolve()
                resolved_file.relative_to(root)
                if resolved_file.stat().st_size > self.MAX_FILE_SIZE_BYTES:
                    continue

                text = resolved_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError, ValueError):
                continue

            matched_lines: list[str] = []
            for line_no, line in enumerate(text.splitlines(), start=1):
                if keyword in line.lower():
                    safe_line = line.strip()[: self.MAX_LINE_LENGTH]
                    matched_lines.append(f"  L{line_no}: {safe_line}")
                    if len(matched_lines) >= self.MAX_MATCHED_LINES_PER_FILE:
                        break

            if matched_lines:
                results.append(
                    {
                        "file": str(resolved_file.relative_to(root)),
                        "matches": "\n".join(matched_lines),
                    }
                )
                count += 1

        if not results:
            return [{"message": f"No markdown files matching '{arguments.query}'."}]

        return results
