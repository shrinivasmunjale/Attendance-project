import logging
import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from datetime import datetime
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.ml.recognizer import FaceRecognizer

router = APIRouter(prefix="/students", tags=["students"])
logger = logging.getLogger("attendance.students")


def _to_response(s: Student) -> StudentResponse:
    return StudentResponse(
        id=str(s.id),
        student_id=s.student_id,
        name=s.name,
        email=s.email,
        department=s.department,
        semester=s.semester,
        face_registered=s.face_registered,
        created_at=s.created_at,
    )


@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate):
    """Create a new student."""
    existing = await Student.find_one(Student.student_id == student.student_id)
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")

    db_student = Student(**student.model_dump())
    await db_student.insert()
    logger.info("Student created: %s", student.student_id)
    return _to_response(db_student)


@router.get("/", response_model=List[StudentResponse])
async def list_students(skip: int = 0, limit: int = 100):
    """List all students."""
    students = await Student.find_all().skip(skip).limit(limit).to_list()
    return [_to_response(s) for s in students]


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str):
    """Get a student by their string student_id (e.g. STU001)."""
    student = await Student.find_one(Student.student_id == student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return _to_response(student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: str, update: StudentUpdate):
    """Update student information."""
    student = await Student.find_one(Student.student_id == student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    await student.set(update_data)
    return _to_response(student)


@router.delete("/{student_id}")
async def delete_student(student_id: str):
    """Delete a student."""
    student = await Student.find_one(Student.student_id == student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    await student.delete()
    return {"message": "Student deleted successfully"}


@router.post("/rebuild-embeddings")
async def rebuild_embeddings():
    """Rebuild face recognition embeddings from all registered student faces."""
    recognizer = FaceRecognizer()
    recognizer.build_embeddings()
    return {"message": f"Embeddings rebuilt for {len(recognizer.embeddings)} students"}


@router.post("/{student_id}/register-face")
async def register_face(student_id: str, file: UploadFile = File(...)):
    """Upload and register a student's face image."""
    student = await Student.find_one(Student.student_id == student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    recognizer = FaceRecognizer()
    success = recognizer.register_student_face(student.student_id, img)
    if not success:
        raise HTTPException(status_code=500, detail="Face registration failed")

    await student.set({"face_registered": True, "updated_at": datetime.utcnow()})
    return {"message": "Face registered successfully"}
