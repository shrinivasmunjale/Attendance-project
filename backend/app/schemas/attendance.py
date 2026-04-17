from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AttendanceCreate(BaseModel):
    student_id: str          # student_id string e.g. "STU001"
    date: str
    status: str = "present"
    confidence: Optional[float] = None
    camera_id: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: str
    student_id: str
    name: str
    date: str
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    status: str
    confidence: Optional[float] = None
    camera_id: Optional[str] = None
    created_at: Optional[datetime] = None


class AttendanceSummary(BaseModel):
    date: str
    total_students: int
    present: int
    absent: int
    late: int
