from pathlib import Path

import httpx
import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.config import LLMSettings, OllamaEmbeddingSettings
from app.rag import (
    MATERIAL_ANSWER_UNAVAILABLE,
    answer_material_question,
    answer_question_from_local_materials,
    build_material_answer_messages,
    build_ollama_embeddings,
    build_material_vector_store,
    generate_material_answer,
    load_local_materials,
    parse_material_answer,
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


class FakeLLMClient:
    def __init__(self, response_data: dict):
        self.response_data = response_data
        self.request: dict | None = None

    def post(self, url: str, *, headers: dict[str, str], json: dict) -> httpx.Response:
        self.request = {
            "url": url,
            "headers": headers,
            "json": json,
        }
        request = httpx.Request("POST", url)
        return httpx.Response(200, json=self.response_data, request=request)


def make_settings() -> LLMSettings:
    return LLMSettings(
        provider="ollama",
        api_key="ollama",
        api_key_env="OLLAMA_API_KEY",
        base_url="http://localhost:11434/v1",
        model="qwen3:8b",
        requires_api_key=False,
    )


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


def test_build_material_answer_messages_contains_context_sources_and_schema() -> None:
    documents = [
        Document(
            page_content="Python type annotations clarify function signatures.",
            metadata={"source": "materials/python.md"},
        )
    ]

    messages = build_material_answer_messages("类型标注有什么用？", documents)

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    user_content = messages[1]["content"]
    assert "资料片段" in user_content
    assert "Python type annotations clarify function signatures." in user_content
    assert "materials/python.md" in user_content
    assert "只返回一个 JSON 对象" in user_content
    assert "answer" in user_content
    assert "sources" in user_content


def test_parse_material_answer_returns_model_and_deduplicates_sources() -> None:
    content = """
    {
      "answer": "类型标注写在函数参数和返回值上。",
      "sources": ["materials/python.md", "materials/python.md"]
    }
    """

    result = parse_material_answer(content, allowed_sources=["materials/python.md"])

    assert result.answer == "类型标注写在函数参数和返回值上。"
    assert result.sources == ["materials/python.md"]


def test_parse_material_answer_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="valid material answer"):
        parse_material_answer("答案：复习类型标注。", allowed_sources=["materials/python.md"])


def test_parse_material_answer_rejects_unknown_sources() -> None:
    content = """
    {
      "answer": "类型标注写在函数参数和返回值上。",
      "sources": ["materials/unknown.md"]
    }
    """

    with pytest.raises(ValueError, match="unknown source"):
        parse_material_answer(content, allowed_sources=["materials/python.md"])


def test_parse_material_answer_requires_source_for_grounded_answer() -> None:
    content = """
    {
      "answer": "类型标注写在函数参数和返回值上。",
      "sources": []
    }
    """

    with pytest.raises(ValueError, match="did not cite"):
        parse_material_answer(content, allowed_sources=["materials/python.md"])


def test_parse_material_answer_allows_unavailable_answer_without_sources() -> None:
    content = f"""
    {{
      "answer": "{MATERIAL_ANSWER_UNAVAILABLE}",
      "sources": []
    }}
    """

    result = parse_material_answer(content, allowed_sources=["materials/python.md"])

    assert result.answer == MATERIAL_ANSWER_UNAVAILABLE
    assert result.sources == []


def test_generate_material_answer_uses_json_mode_and_allowed_sources() -> None:
    client = FakeLLMClient(
        {
            "choices": [
                {
                    "message": {
                        "content": (
                            "{\"answer\":\"类型标注写在函数参数和返回值上。\","
                            "\"sources\":[\"materials/python.md\"]}"
                        )
                    }
                }
            ]
        }
    )
    documents = [
        Document(
            page_content="Python type annotations clarify function signatures.",
            metadata={"source": "materials/python.md"},
        )
    ]

    result = generate_material_answer(
        "类型标注有什么用？",
        documents,
        settings=make_settings(),
        client=client,
    )

    assert result.answer == "类型标注写在函数参数和返回值上。"
    assert result.sources == ["materials/python.md"]
    assert client.request is not None
    assert client.request["url"] == "http://localhost:11434/v1/chat/completions"
    assert client.request["json"]["model"] == "qwen3:8b"
    assert client.request["json"]["response_format"] == {"type": "json_object"}
    user_message = client.request["json"]["messages"][1]["content"]
    assert "Python type annotations clarify function signatures." in user_message
    assert "materials/python.md" in user_message


def test_generate_material_answer_returns_unavailable_without_documents() -> None:
    client = FakeLLMClient({"choices": [{"message": {"content": "{}"}}]})

    result = generate_material_answer(
        "类型标注有什么用？",
        [],
        settings=make_settings(),
        client=client,
    )

    assert result.answer == MATERIAL_ANSWER_UNAVAILABLE
    assert result.sources == []
    assert client.request is None


def test_generate_material_answer_rejects_empty_question() -> None:
    with pytest.raises(ValueError, match="question must not be empty"):
        generate_material_answer("   ", [], settings=make_settings())


def test_generate_material_answer_rejects_documents_without_source_metadata() -> None:
    client = FakeLLMClient({"choices": [{"message": {"content": "{}"}}]})

    with pytest.raises(ValueError, match="missing source metadata"):
        generate_material_answer(
            "类型标注有什么用？",
            [Document(page_content="Python type annotations clarify function signatures.")],
            settings=make_settings(),
            client=client,
        )

    assert client.request is None


def test_answer_material_question_retrieves_chunks_before_generating_answer() -> None:
    documents = [
        Document(
            page_content="Python type annotations clarify function signatures.",
            metadata={"source": "materials/python.md"},
        ),
        Document(
            page_content="FastAPI routes expose HTTP APIs.",
            metadata={"source": "materials/fastapi.md"},
        ),
    ]
    vector_store = build_material_vector_store(documents, KeywordEmbeddings())
    client = FakeLLMClient(
        {
            "choices": [
                {
                    "message": {
                        "content": (
                            "{\"answer\":\"类型标注能说明函数签名。\","
                            "\"sources\":[\"materials/python.md\"]}"
                        )
                    }
                }
            ]
        }
    )

    result = answer_material_question(
        "How do Python type annotations work?",
        vector_store,
        settings=make_settings(),
        client=client,
        k=1,
    )

    assert result.answer == "类型标注能说明函数签名。"
    assert result.sources == ["materials/python.md"]
    assert client.request is not None
    user_message = client.request["json"]["messages"][1]["content"]
    assert "Python type annotations clarify function signatures." in user_message
    assert "FastAPI routes expose HTTP APIs." not in user_message


def test_answer_question_from_local_materials_builds_pipeline_with_injected_embeddings(
    tmp_path: Path,
) -> None:
    materials_dir = tmp_path / "materials"
    materials_dir.mkdir()
    (materials_dir / "python.md").write_text(
        "Python type annotations clarify function signatures.",
        encoding="utf-8",
    )
    (materials_dir / "fastapi.md").write_text(
        "FastAPI routes expose HTTP APIs.",
        encoding="utf-8",
    )
    client = FakeLLMClient(
        {
            "choices": [
                {
                    "message": {
                        "content": (
                            "{\"answer\":\"类型标注能说明函数签名。\","
                            "\"sources\":[\"materials/python.md\"]}"
                        )
                    }
                }
            ]
        }
    )

    result = answer_question_from_local_materials(
        "How do Python type annotations work?",
        materials_dir=materials_dir,
        embeddings=KeywordEmbeddings(),
        settings=make_settings(),
        client=client,
        k=1,
    )

    assert result.answer == "类型标注能说明函数签名。"
    assert result.sources == ["materials/python.md"]
    assert client.request is not None
    user_message = client.request["json"]["messages"][1]["content"]
    assert "Python type annotations clarify function signatures." in user_message
    assert "FastAPI routes expose HTTP APIs." not in user_message


def test_answer_question_from_local_materials_returns_unavailable_for_empty_materials(
    tmp_path: Path,
) -> None:
    materials_dir = tmp_path / "materials"
    materials_dir.mkdir()
    client = FakeLLMClient({"choices": [{"message": {"content": "{}"}}]})

    result = answer_question_from_local_materials(
        "资料里有 LangGraph 吗？",
        materials_dir=materials_dir,
        embeddings=KeywordEmbeddings(),
        settings=make_settings(),
        client=client,
    )

    assert result.answer == MATERIAL_ANSWER_UNAVAILABLE
    assert result.sources == []
    assert client.request is None


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
