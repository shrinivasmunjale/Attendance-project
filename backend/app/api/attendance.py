from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.attendance import Attendance
from app.models.student import Student
from app.schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceSummary

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("/", response_model=List[AttendanceResponse])
def list_attendance(
    date_filter: Optional[str] = Query(None, alias="date"),
    student_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    """List attendance records with optional filters."""
    query = db.query(Attendance)

    if date_filter:
        query = query.filter(Attendance.date == date_filter)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)

    return query.offset(skip).limit(limit).all()


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

    # Check if already marked today
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


@router.get("/export")
def export_attendance(
    date_filter: str = Query(str(date.today()), alias="date"),
    db: Session = Depends(get_db),
):
    """Export attendance as JSON for a given date."""
    records = db.query(Attendance).filter(Attendance.date == date_filter).all()
    result = []
    for r in records:
        student = db.query(Student).filter(Student.id == r.student_id).first()
        result.append({
            "student_id": student.student_id if student else "N/A",
            "name": student.name if student else "N/A",
            "date": r.date,
            "status": r.status,
            "time_in": str(r.time_in) if r.time_in else None,
            "confidence": r.confidence,
        })
    return result
