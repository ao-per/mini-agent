from pathlib import Path

from registry import ToolRegistry
from tools.search_notes import SearchNotesTool


def make_registry(notes_root: Path) -> tuple[ToolRegistry, SearchNotesTool]:
    tool = SearchNotesTool(notes_root=notes_root)
    registry = ToolRegistry()
    registry.register(tool)
    return registry, tool


def test_search_is_limited_to_configured_notes_root(tmp_path: Path) -> None:
    notes_root = tmp_path / "notes"
    notes_root.mkdir()
    (notes_root / "inside.md").write_text("project alpha", encoding="utf-8")
    (tmp_path / "outside.md").write_text("project alpha secret", encoding="utf-8")
    registry, _ = make_registry(notes_root)

    result = registry.execute("search_notes", {"query": "alpha"})

    assert result.success is True
    assert result.output == [
        {
            "file": "inside.md",
            "matches": "  L1: project alpha",
        }
    ]


def test_model_cannot_override_notes_directory(tmp_path: Path) -> None:
    notes_root = tmp_path / "notes"
    notes_root.mkdir()
    registry, tool = make_registry(notes_root)

    result = registry.execute(
        "search_notes",
        {
            "query": "secret",
            "directory": str(tmp_path),
        },
    )
    parameters = tool.schema()["function"]["parameters"]

    assert result.success is False
    assert result.error_code == "INVALID_ARGUMENTS"
    assert "directory" not in parameters["properties"]


def test_large_note_is_skipped(tmp_path: Path) -> None:
    notes_root = tmp_path / "notes"
    notes_root.mkdir()
    large_note = notes_root / "large.md"
    large_note.write_text("secret content", encoding="utf-8")
    registry, tool = make_registry(notes_root)
    tool.MAX_FILE_SIZE_BYTES = 5

    result = registry.execute("search_notes", {"query": "secret"})

    assert result.success is True
    assert result.output == [{"message": "No markdown files matching 'secret'."}]
