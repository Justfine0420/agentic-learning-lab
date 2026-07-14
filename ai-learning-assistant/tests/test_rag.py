from pathlib import Path

import pytest

from app.rag import load_local_materials


def test_load_local_materials_returns_sorted_documents_with_sources(tmp_path: Path) -> None:
    materials_dir = tmp_path / "materials"
    materials_dir.mkdir()
    (materials_dir / "z.md").write_text("Zebra material", encoding="utf-8")
    (materials_dir / "a.md").write_text("Alpha material", encoding="utf-8")
    (materials_dir / "B.MD").write_text("Beta material", encoding="utf-8")
    (materials_dir / "ignore.txt").write_text("Not a Markdown material", encoding="utf-8")

    documents = load_local_materials(materials_dir)

    assert [document.page_content for document in documents] == [
        "Alpha material",
        "Beta material",
        "Zebra material",
    ]
    assert [document.metadata for document in documents] == [
        {"source": "materials/a.md"},
        {"source": "materials/B.MD"},
        {"source": "materials/z.md"},
    ]


def test_load_local_materials_returns_empty_list_when_no_markdown_exists(tmp_path: Path) -> None:
    materials_dir = tmp_path / "materials"
    materials_dir.mkdir()
    (materials_dir / "ignore.txt").write_text("Not a Markdown material", encoding="utf-8")

    assert load_local_materials(materials_dir) == []


def test_load_local_materials_rejects_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Materials directory does not exist"):
        load_local_materials(tmp_path / "missing-materials")


def test_load_local_materials_rejects_file_path(tmp_path: Path) -> None:
    material_file = tmp_path / "materials.md"
    material_file.write_text("Not a directory", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="Materials path is not a directory"):
        load_local_materials(material_file)
