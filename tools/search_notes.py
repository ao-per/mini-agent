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
    directory: str = Field(
        default=".",
        description=(
            "The root directory to search in. "
            "Defaults to the current working directory."
        ),
    )
    max_results: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of matching files to return (1-50).",
    )


class SearchNotesTool(Tool):
    name = "search_notes"
    description = (
        "Search local markdown (.md) files for notes matching a keyword. "
        "Returns a list of matching files with the file path and "
        "lines containing the keyword."
    )
    args_model = SearchNotesArgs

    def run(self, arguments: BaseModel) -> list[dict[str, str]]:
        if not isinstance(arguments, SearchNotesArgs):
            raise TypeError("Expected SearchNotesArgs")

        root = Path(arguments.directory).resolve()
        if not root.is_dir():
            raise ValueError(f"Not a directory: {arguments.directory}")

        keyword = arguments.query.lower()
        results: list[dict[str, str]] = []
        count = 0

        for md_file in sorted(root.rglob("*.md")):
            if count >= arguments.max_results:
                break

            try:
                text = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            matched_lines: list[str] = []
            for line_no, line in enumerate(text.splitlines(), start=1):
                if keyword in line.lower():
                    matched_lines.append(f"  L{line_no}: {line.strip()}")

            if matched_lines:
                results.append(
                    {
                        "file": str(md_file),
                        "matches": "\n".join(matched_lines),
                    }
                )
                count += 1

        if not results:
            return [{"message": f"No markdown files matching '{arguments.query}'."}]

        return results