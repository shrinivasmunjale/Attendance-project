from beanie import Document, Indexed, Link
from typing import Optional
from datetime import datetime
from pydantic import Field


class AttendanceRecord(Document):
    student_id: str                          # student_id string (e.g. "STU001")
    student_name: str = ""                   # denormalized for fast reads
    date: Indexed(str)                       # "YYYY-MM-DD"
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    status: str = "present"                  # present / absent / late
    confidence: Optional[float] = None
    camera_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "attendance"
