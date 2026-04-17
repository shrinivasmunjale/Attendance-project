from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AttendanceBase(BaseModel):
    student_id: int
    date: str
    status: str = "present"
    confidence: Optional[float] = None
    camera_id: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    date: str
    total_students: int
    present: int
    absent: int
    late: int
