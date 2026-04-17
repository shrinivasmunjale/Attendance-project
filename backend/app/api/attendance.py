import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.attendance import Attendance
from app.models.student import Student
from app.schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceSummary

router = APIRouter(prefix="/attendance", tags=["attendance"])
logger = logging.getLogger("attendance.api")


def _enrich(record: Attendance) -> dict:
    """Add student name/id string to an attendance record dict."""
    data = {
        "id": record.id,
        "student_id": record.student.student_id if record.student else str(record.student_id),
        "name": record.student.name if record.student else "Unknown",
        "date": record.date,
        "time_in": record.time_in,
        "time_out": record.time_out,
        "status": record.status,
        "confidence": record.confidence,
        "camera_id": record.camera_id,
        "created_at": record.created_at,
    }
    return data


@router.get("/")
def list_attendance(
    date_filter: Optional[str] = Query(None, alias="date"),
    student_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    """List attendance records with optional filters. Includes student name."""
    query = db.query(Attendance).options(joinedload(Attendance.student))

    if date_filter:
        query = query.filter(Attendance.date == date_filter)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)

    records = query.offset(skip).limit(limit).all()
    return [_enrich(r) for r in records]


@router.get("/summary", response_model=AttendanceSummary)
def attendance_summary(
    date_filter: str = Query(str(date.today()), alias="date"),
    db: Session = Depends(get_db),
):
    """Get attendance summary for a specific date."""
    total_students = db.query(Student).count()
    records = db.query(Attendance).filter(Attendance.date == date_filter).all()

    present = sum(1 for r in records if r.status == "present")
    late = sum(1 for r in records if r.status == "late")
    absent = total_students - present - late

    return AttendanceSummary(
        date=date_filter,
        total_students=total_students,
        present=present,
        absent=max(0, absent),
        late=late,
    )


@router.post("/", response_model=AttendanceResponse)
def mark_attendance(record: AttendanceCreate, db: Session = Depends(get_db)):
    """Manually mark attendance for a student."""
    student = db.query(Student).filter(Student.id == record.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == record.student_id,
            Attendance.date == record.date,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already marked for today")

    db_record = Attendance(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/{record_id}")
def delete_attendance(record_id: int, db: Session = Depends(get_db)):
    """Delete an attendance record (admin correction)."""
    record = db.query(Attendance).filter(Attendance.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}


@router.get("/export")
def export_attendance(
    date_filter: str = Query(str(date.today()), alias="date"),
    db: Session = Depends(get_db),
):
    """Export full attendance report for a given date as JSON."""
    records = (
        db.query(Attendance)
        .options(joinedload(Attendance.student))
        .filter(Attendance.date == date_filter)
        .all()
    )
    return [_enrich(r) for r in records]


@router.get("/report/range")
def attendance_range_report(
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """Get attendance records between two dates."""
    records = (
        db.query(Attendance)
        .options(joinedload(Attendance.student))
        .filter(Attendance.date >= start, Attendance.date <= end)
        .order_by(Attendance.date)
        .all()
    )
    return [_enrich(r) for r in records]
