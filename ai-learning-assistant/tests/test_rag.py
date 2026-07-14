from pathlib import Path

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.config import OllamaEmbeddingSettings
from app.rag import (
    build_ollama_embeddings,
    build_material_vector_store,
    load_local_materials,
    retrieve_material_chunks,
    split_material_documents,
)


class KeywordEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        normalized = text.lower()
        keyword_groups = (
            ("python", "type", "annotation"),
            ("fastapi", "api", "route"),
            ("langchain", "agent", "tool"),
        )
        return [
            float(sum(keyword in normalized for keyword in keywords))
            for keywords in keyword_groups
        ]


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


def test_retrieve_material_chunks_returns_the_most_similar_source() -> None:
    documents = [
        Document(
            page_content="Python type annotations clarify function signatures.",
            metadata={"source": "materials/python.md"},
        ),
        Document(
            page_content="FastAPI routes expose HTTP APIs.",
            metadata={"source": "materials/fastapi.md"},
        ),
        Document(
            page_content="LangChain agents choose tools.",
            metadata={"source": "materials/langchain.md"},
        ),
    ]
    vector_store = build_material_vector_store(documents, KeywordEmbeddings())

    chunks = retrieve_material_chunks("How do Python type annotations work?", vector_store, k=1)

    assert [chunk.page_content for chunk in chunks] == [
        "Python type annotations clarify function signatures."
    ]
    assert chunks[0].metadata == {"source": "materials/python.md"}


def test_retrieve_material_chunks_returns_empty_list_for_an_empty_store() -> None:
    vector_store = build_material_vector_store([], KeywordEmbeddings())

    assert retrieve_material_chunks("Python", vector_store) == []


def test_build_ollama_embeddings_uses_explicit_local_settings() -> None:
    embeddings = build_ollama_embeddings(
        OllamaEmbeddingSettings(
            base_url="http://127.0.0.1:11434/v1/",
            model=" qwen3-embedding:latest ",
        )
    )

    assert embeddings.base_url == "http://127.0.0.1:11434"
    assert embeddings.model == "qwen3-embedding:latest"


def test_build_ollama_embeddings_rejects_empty_model() -> None:
    with pytest.raises(ValueError, match="OLLAMA_EMBEDDING_MODEL must not be empty"):
        build_ollama_embeddings(
            OllamaEmbeddingSettings(
                base_url="http://127.0.0.1:11434",
                model=" ",
            )
        )


@pytest.mark.parametrize(
    ("query", "k", "message"),
    [
        ("", 1, "query must not be empty"),
        ("   ", 1, "query must not be empty"),
        ("Python", 0, "k must be greater than 0"),
    ],
)
def test_retrieve_material_chunks_rejects_invalid_query_or_k(
    query: str,
    k: int,
    message: str,
) -> None:
    vector_store = build_material_vector_store([], KeywordEmbeddings())

    with pytest.raises(ValueError, match=message):
        retrieve_material_chunks(query, vector_store, k=k)
