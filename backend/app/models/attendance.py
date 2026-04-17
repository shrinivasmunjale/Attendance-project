from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(String, nullable=False)          # "YYYY-MM-DD"
    time_in = Column(DateTime, nullable=True)
    time_out = Column(DateTime, nullable=True)
    status = Column(String, default="present")     # present / absent / late
    confidence = Column(Float, nullable=True)      # face recognition confidence
    camera_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    student = relationship("Student", back_populates="attendance_records")

    def __repr__(self):
        return f"<Attendance student_id={self.student_id} date={self.date}>"
