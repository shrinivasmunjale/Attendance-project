from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import cv2
import asyncio
import base64
from datetime import datetime
from app.database import get_db
from app.models.attendance import Attendance
from app.models.student import Student
from app.ml.pipeline import AttendancePipeline
from app.config import get_settings

router = APIRouter(prefix="/cameras", tags=["cameras"])
settings = get_settings()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@router.websocket("/stream")
async def camera_stream(websocket: WebSocket):
    """
    WebSocket endpoint for live camera feed with real-time attendance detection.
    Sends annotated frames back to frontend.
    """
    await manager.connect(websocket)

    # Get DB session (manual since WebSocket doesn't support Depends directly)
    from app.database import SessionLocal
    db = SessionLocal()

    async def on_attendance_callback(student_id: str, confidence: float, frame):
        """Called when a student is recognized."""
        # Find student in DB
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return

        # Mark attendance
        today = str(datetime.now().date())
        existing = (
            db.query(Attendance)
            .filter(Attendance.student_id == student.id, Attendance.date == today)
            .first()
        )

        if not existing:
            record = Attendance(
                student_id=student.id,
                date=today,
                time_in=datetime.now(),
                status="present",
                confidence=confidence,
                camera_id="main",
            )
            db.add(record)
            db.commit()

            # Notify frontend
            await manager.broadcast({
                "type": "attendance_marked",
                "student_id": student_id,
                "name": student.name,
                "confidence": confidence,
            })

    pipeline = AttendancePipeline(on_attendance=on_attendance_callback)
    cap = cv2.VideoCapture(int(settings.camera_source) if settings.camera_source.isdigit() else settings.camera_source)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame through ML pipeline
            annotated = await pipeline.process_frame(frame)

            # Encode frame as JPEG
            _, buffer = cv2.imencode(".jpg", annotated)
            frame_base64 = base64.b64encode(buffer).decode("utf-8")

            # Send to frontend
            await websocket.send_json({
                "type": "frame",
                "data": frame_base64,
            })

            await asyncio.sleep(0.03)  # ~30 FPS

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        cap.release()
        db.close()


@router.get("/status")
def camera_status():
    """Check if camera is accessible."""
    cap = cv2.VideoCapture(int(settings.camera_source) if settings.camera_source.isdigit() else settings.camera_source)
    is_opened = cap.isOpened()
    cap.release()
    return {"camera_accessible": is_opened, "source": settings.camera_source}
