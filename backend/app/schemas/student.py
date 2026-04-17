from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    student_id: str
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None


class StudentResponse(StudentBase):
    id: str
    face_registered: bool
    created_at: datetime

    class Config:
        from_attributes = True
