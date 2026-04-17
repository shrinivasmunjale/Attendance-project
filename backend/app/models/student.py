from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)  # e.g. "STU001"
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    department = Column(String, nullable=True)
    semester = Column(Integer, nullable=True)
    face_registered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    attendance_records = relationship("Attendance", back_populates="student")

    def __repr__(self):
        return f"<Student {self.student_id} - {self.name}>"
