from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
from app.models.attendance import Attendance
from app.models.student import Student


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def mark_present(
        self,
        student_db_id: int,
        confidence: float = 1.0,
        camera_id: str = "main",
    ) -> Optional[Attendance]:
        """Mark a student as present. Skips if already marked today."""
        today = str(date.today())

        existing = (
            self.db.query(Attendance)
            .filter(
                Attendance.student_id == student_db_id,
                Attendance.date == today,
            )
            .first()
        )

        if existing:
            return existing  # Already marked

        record = Attendance(
            student_id=student_db_id,
            date=today,
            time_in=datetime.now(),
            status="present",
            confidence=confidence,
            camera_id=camera_id,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_daily_report(self, report_date: str) -> List[dict]:
        """Get full attendance report for a date."""
        students = self.db.query(Student).all()
        records = {
            r.student_id: r
            for r in self.db.query(Attendance).filter(Attendance.date == report_date).all()
        }

        report = []
        for student in students:
            record = records.get(student.id)
            report.append({
                "student_id": student.student_id,
                "name": student.name,
                "department": student.department,
                "status": record.status if record else "absent",
                "time_in": str(record.time_in) if record and record.time_in else None,
                "confidence": record.confidence if record else None,
            })

        return report
