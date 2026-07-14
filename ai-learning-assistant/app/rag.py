from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


MATERIALS_DIR = Path(__file__).resolve().parent.parent / "materials"
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120


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
