from pathlib import Path

from langchain_core.documents import Document


MATERIALS_DIR = Path(__file__).resolve().parent.parent / "materials"


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
