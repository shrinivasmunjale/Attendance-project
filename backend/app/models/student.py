from beanie import Document, Indexed
from pydantic import EmailStr
from typing import Optional
from datetime import datetime


class Student(Document):
    student_id: Indexed(str, unique=True)   # e.g. "STU001"
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    face_registered: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "students"   # MongoDB collection name

    def __repr__(self):
        return f"<Student {self.student_id} - {self.name}>"
