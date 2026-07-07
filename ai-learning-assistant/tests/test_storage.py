import json
from pathlib import Path

from app import storage
from app.models import Student


def use_tmp_storage(tmp_path: Path) -> None:
    storage.DATA_FILE = tmp_path / "student.json"
    storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"


def test_load_student_returns_default_when_file_missing(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)

    assert storage.load_student() == storage.create_default_student()


def test_save_and_load_student_round_trip(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    student: Student = {
        "name": "Alice",
        "goal": "Learn pytest",
        "python_level": "beginner",
        "notes": ["Write storage tests"],
    }

    storage.save_student(student)

    assert storage.DATA_FILE.exists()
    assert storage.load_student() == student


def test_load_student_backs_up_broken_json(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.DATA_FILE.write_text("{ bad json", encoding="utf-8")

    assert storage.load_student() == storage.create_default_student()
    assert not storage.DATA_FILE.exists()
    assert storage.BROKEN_DATA_FILE.exists()
    assert storage.BROKEN_DATA_FILE.read_text(encoding="utf-8") == "{ bad json"


def test_load_student_normalizes_partial_data(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.DATA_FILE.write_text(
        json.dumps(
            {
                "name": "Carol",
                "notes": ["Only partial data", 123],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert storage.load_student() == {
        "name": "Carol",
        "goal": "",
        "python_level": "",
        "notes": ["Only partial data"],
    }


def test_load_student_accepts_utf8_bom(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.DATA_FILE.write_text(
        json.dumps(
            {
                "name": "Dora",
                "goal": "Read BOM",
                "python_level": "basic",
                "notes": ["UTF-8 with BOM"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8-sig",
    )

    assert storage.load_student()["name"] == "Dora"
