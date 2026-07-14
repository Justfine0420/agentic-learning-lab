from pathlib import Path

import pytest
from langchain_core.documents import Document

from app.rag import load_local_materials, split_material_documents


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


def test_split_material_documents_preserves_metadata_and_overlap() -> None:
    documents = [
        Document(
            page_content="abcdefghij",
            metadata={"source": "materials/example.md", "topic": "testing"},
        )
    ]

    chunks = split_material_documents(documents, chunk_size=4, chunk_overlap=1)

    assert [chunk.page_content for chunk in chunks] == ["abcd", "defg", "ghij"]
    assert [chunk.metadata for chunk in chunks] == [
        {"source": "materials/example.md", "topic": "testing"},
        {"source": "materials/example.md", "topic": "testing"},
        {"source": "materials/example.md", "topic": "testing"},
    ]


def test_split_material_documents_returns_empty_list_for_no_documents() -> None:
    assert split_material_documents([]) == []


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap", "message"),
    [
        (0, 0, "chunk_size must be greater than 0"),
        (4, -1, "chunk_overlap must be greater than or equal to 0"),
        (4, 4, "chunk_overlap must be smaller than chunk_size"),
    ],
)
def test_split_material_documents_rejects_invalid_sizes(
    chunk_size: int,
    chunk_overlap: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        split_material_documents([], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
