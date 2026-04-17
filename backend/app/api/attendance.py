import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime
from app.models.attendance import AttendanceRecord
from app.models.student import Student
from app.schemas.attendance import AttendanceCreate, AttendanceSummary

router = APIRouter(prefix="/attendance", tags=["attendance"])
logger = logging.getLogger("attendance.api")


@router.get("/")
async def list_attendance(
    date_filter: Optional[str] = Query(None, alias="date"),
    student_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
):
    """List attendance records with optional filters."""
    query = {}
    if date_filter:
        query["date"] = date_filter
    if student_id:
        query["student_id"] = student_id

    records = await AttendanceRecord.find(query).skip(skip).limit(limit).to_list()
    return [_serialize(r) for r in records]


@router.get("/summary", response_model=AttendanceSummary)
async def attendance_summary(
    date_filter: str = Query(str(date.today()), alias="date"),
):
    """Get attendance summary for a specific date."""
    total_students = await Student.count()
    records = await AttendanceRecord.find(AttendanceRecord.date == date_filter).to_list()

    present = sum(1 for r in records if r.status == "present")
    late    = sum(1 for r in records if r.status == "late")
    absent  = max(0, total_students - present - late)

    return AttendanceSummary(
        date=date_filter,
        total_students=total_students,
        present=present,
        absent=absent,
        late=late,
    )


@router.post("/")
async def mark_attendance(record: AttendanceCreate):
    """Manually mark attendance for a student."""
    student = await Student.find_one(Student.student_id == record.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = await AttendanceRecord.find_one(
        AttendanceRecord.student_id == record.student_id,
        AttendanceRecord.date == record.date,
    )
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already marked for today")

    db_record = AttendanceRecord(
        student_id=record.student_id,
        student_name=student.name,
        date=record.date,
        status=record.status,
        confidence=record.confidence,
        camera_id=record.camera_id,
        time_in=datetime.utcnow(),
    )
    await db_record.insert()
    return _serialize(db_record)


@router.delete("/{record_id}")
async def delete_attendance(record_id: str):
    """Delete an attendance record."""
    from beanie import PydanticObjectId
    record = await AttendanceRecord.get(PydanticObjectId(record_id))
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    await record.delete()
    return {"message": "Record deleted"}


@router.get("/export")
async def export_attendance(
    date_filter: str = Query(str(date.today()), alias="date"),
):
    """Export attendance for a given date."""
    records = await AttendanceRecord.find(AttendanceRecord.date == date_filter).to_list()
    return [_serialize(r) for r in records]


@router.get("/report/range")
async def attendance_range_report(
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str   = Query(..., description="End date YYYY-MM-DD"),
):
    """Get attendance records between two dates."""
    records = await AttendanceRecord.find(
        AttendanceRecord.date >= start,
        AttendanceRecord.date <= end,
    ).sort("date").to_list()
    return [_serialize(r) for r in records]


def _serialize(r: AttendanceRecord) -> dict:
    return {
        "id":           str(r.id),
        "student_id":   r.student_id,
        "name":         r.student_name,
        "date":         r.date,
        "time_in":      r.time_in.isoformat() if r.time_in else None,
        "time_out":     r.time_out.isoformat() if r.time_out else None,
        "status":       r.status,
        "confidence":   r.confidence,
        "camera_id":    r.camera_id,
        "created_at":   r.created_at.isoformat() if r.created_at else None,
    }
