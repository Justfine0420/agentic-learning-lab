import json
from pathlib import Path

import httpx

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import (
    LLMSettings,
    OllamaEmbeddingSettings,
    get_ollama_embedding_settings,
    normalize_ollama_embedding_base_url,
)
from app.llm import call_chat_completion
from app.models import MaterialAnswer


MATERIALS_DIR = Path(__file__).resolve().parent.parent / "materials"
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120
MATERIAL_ANSWER_UNAVAILABLE = "当前资料中没有找到足够依据回答这个问题。"
MATERIAL_ANSWER_SYSTEM_INSTRUCTIONS = (
    "你是一个基于学习资料回答问题的 Python 和 AI Agent 学习助教。"
    "你只能使用用户提供的资料片段回答，不能补充资料外知识。"
    "如果资料片段不足以回答问题，必须直接说明资料不足。"
)


def load_local_materials(materials_dir: Path = MATERIALS_DIR) -> list[Document]:
    if not materials_dir.exists():
        raise FileNotFoundError(f"Materials directory does not exist: {materials_dir}")
    if not materials_dir.is_dir():
        raise NotADirectoryError(f"Materials path is not a directory: {materials_dir}")

    material_paths = sorted(
        (
            path
            for path in materials_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".md"
        ),
        key=lambda path: path.name.lower(),
    )

    return [
        Document(
            page_content=material_path.read_text(encoding="utf-8"),
            metadata={
                "source": material_path.relative_to(materials_dir.parent).as_posix(),
            },
        )
        for material_path in material_paths
    ]


def split_material_documents(
    documents: list[Document],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(documents)


def build_material_vector_store(
    documents: list[Document],
    embeddings: Embeddings,
) -> InMemoryVectorStore:
    vector_store = InMemoryVectorStore(embedding=embeddings)
    if documents:
        vector_store.add_documents(documents)
    return vector_store


def build_ollama_embeddings(
    settings: OllamaEmbeddingSettings | None = None,
) -> OllamaEmbeddings:
    current_settings = settings or get_ollama_embedding_settings()
    model = current_settings.model.strip()
    if model == "":
        raise ValueError("OLLAMA_EMBEDDING_MODEL must not be empty")

    return OllamaEmbeddings(
        model=model,
        base_url=normalize_ollama_embedding_base_url(current_settings.base_url),
    )


def retrieve_material_chunks(
    query: str,
    vector_store: InMemoryVectorStore,
    *,
    k: int = 3,
) -> list[Document]:
    if query.strip() == "":
        raise ValueError("query must not be empty")
    if k < 1:
        raise ValueError("k must be greater than 0")

    return vector_store.similarity_search(query, k=k)


def get_material_source(document: Document) -> str:
    source = document.metadata.get("source")
    if not isinstance(source, str) or source.strip() == "":
        raise ValueError("Material document is missing source metadata.")
    return source.strip()


def extract_material_sources(documents: list[Document]) -> list[str]:
    sources: list[str] = []
    seen: set[str] = set()
    for document in documents:
        source = get_material_source(document)
        if source not in seen:
            sources.append(source)
            seen.add(source)
    return sources


def format_material_context(documents: list[Document]) -> str:
    context_blocks = []
    for index, document in enumerate(documents, start=1):
        source = get_material_source(document)
        content = document.page_content.strip()
        context_blocks.append(f"[{index}]\n来源：{source}\n内容：{content}")
    return "\n\n".join(context_blocks)


def build_material_answer_messages(
    question: str,
    documents: list[Document],
) -> list[dict[str, str]]:
    if question.strip() == "":
        raise ValueError("question must not be empty")

    schema = json.dumps(MaterialAnswer.model_json_schema(), ensure_ascii=False, indent=2)
    sources = extract_material_sources(documents)
    source_lines = "\n".join(f"- {source}" for source in sources) or "- 无"
    user_content = "\n\n".join(
        [
            "资料片段：",
            format_material_context(documents) or "无可用资料片段",
            "允许引用的 sources：",
            source_lines,
            f"问题：{question.strip()}",
            "请只返回一个 JSON 对象，不要返回 Markdown，不要返回代码块。",
            "JSON 必须符合下面的 schema：",
            schema,
            "回答规则：",
            "1. answer 必须使用中文，并且只能基于资料片段。",
            f"2. 如果资料不足，answer 必须是：{MATERIAL_ANSWER_UNAVAILABLE}",
            "3. sources 只能包含上方允许引用的 sources；资料不足时 sources 必须为空数组。",
        ]
    )

    return [
        {"role": "system", "content": MATERIAL_ANSWER_SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": user_content},
    ]


def parse_material_answer(content: str, allowed_sources: list[str]) -> MaterialAnswer:
    try:
        result = MaterialAnswer.model_validate_json(content)
    except ValueError as error:
        raise ValueError("LLM response was not a valid material answer.") from error

    allowed_source_set = set(allowed_sources)
    deduped_sources: list[str] = []
    seen: set[str] = set()
    for source in result.sources:
        if source not in allowed_source_set:
            raise ValueError("Material answer cited an unknown source.")
        if source not in seen:
            deduped_sources.append(source)
            seen.add(source)

    answer = result.answer.strip()
    if allowed_sources and not deduped_sources and answer != MATERIAL_ANSWER_UNAVAILABLE:
        raise ValueError("Material answer did not cite any provided source.")

    return result.model_copy(update={"answer": answer, "sources": deduped_sources})


def generate_material_answer(
    question: str,
    documents: list[Document],
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
) -> MaterialAnswer:
    if question.strip() == "":
        raise ValueError("question must not be empty")
    if not documents:
        return MaterialAnswer(answer=MATERIAL_ANSWER_UNAVAILABLE, sources=[])

    messages = build_material_answer_messages(question, documents)
    content = call_chat_completion(
        messages,
        settings=settings,
        client=client,
        response_format={"type": "json_object"},
    )
    return parse_material_answer(content, allowed_sources=extract_material_sources(documents))


def answer_material_question(
    question: str,
    vector_store: InMemoryVectorStore,
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
    k: int = 3,
) -> MaterialAnswer:
    chunks = retrieve_material_chunks(question, vector_store, k=k)
    return generate_material_answer(question, chunks, settings=settings, client=client)


def answer_question_from_local_materials(
    question: str,
    *,
    k: int = 3,
    materials_dir: Path = MATERIALS_DIR,
    embeddings: Embeddings | None = None,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
) -> MaterialAnswer:
    if question.strip() == "":
        raise ValueError("question must not be empty")
    if k < 1:
        raise ValueError("k must be greater than 0")

    documents = load_local_materials(materials_dir)
    chunks = split_material_documents(documents)
    if not chunks:
        return generate_material_answer(question, [], settings=settings, client=client)

    current_embeddings = embeddings or build_ollama_embeddings()
    vector_store = build_material_vector_store(chunks, current_embeddings)
    return answer_material_question(
        question,
        vector_store,
        settings=settings,
        client=client,
        k=k,
    )
