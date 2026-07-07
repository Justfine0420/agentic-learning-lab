from app.models import Student
from app.storage import create_default_student


student: Student = create_default_student()


def replace_student(new_student: Student) -> None:
    student.clear()
    student.update(new_student)
