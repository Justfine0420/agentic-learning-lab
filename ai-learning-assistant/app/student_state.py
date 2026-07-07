from app.storage import create_default_student


student = create_default_student()


def replace_student(new_student: dict) -> None:
    student.clear()
    student.update(new_student)
