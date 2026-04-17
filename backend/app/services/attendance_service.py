"""
Attendance service — business logic layer.
Uses Beanie (MongoDB) for all DB operations.
"""
import logging
from datetime import datetime, date
from typing import List, Optional
from app.models.attendance import AttendanceRecord
from app.models.student import Student

logger = logging.getLogger("attendance.service")


async def mark_present(
    student_id: str,
    confidence: float = 1.0,
    camera_id: str = "main",
) -> Optional[AttendanceRecord]:
    """Mark a student as present. Skips if already marked today."""
    today = str(date.today())

    existing = await AttendanceRecord.find_one(
        AttendanceRecord.student_id == student_id,
        AttendanceRecord.date == today,
    )
    if existing:
        return existing

    student = await Student.find_one(Student.student_id == student_id)
    record = AttendanceRecord(
        student_id=student_id,
        student_name=student.name if student else "",
        date=today,
        time_in=datetime.now(),
        status="present",
        confidence=confidence,
        camera_id=camera_id,
    )
    await record.insert()
    logger.info("Marked present: %s (conf=%.2f)", student_id, confidence)
    return record


async def get_daily_report(report_date: str) -> List[dict]:
    """Get full attendance report for a date, including absent students."""
    students = await Student.find_all().to_list()
    records = {
        r.student_id: r
        for r in await AttendanceRecord.find(
            AttendanceRecord.date == report_date
        ).to_list()
    }

    report = []
    for student in students:
        record = records.get(student.student_id)
        report.append({
            "student_id": student.student_id,
            "name": student.name,
            "department": student.department,
            "status": record.status if record else "absent",
            "time_in": record.time_in.isoformat() if record and record.time_in else None,
            "confidence": record.confidence if record else None,
        })
    return report
