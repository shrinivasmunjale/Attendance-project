import logging
import asyncio
import base64
import cv2
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database import SessionLocal
from app.models.attendance import Attendance
from app.models.student import Student
from app.ml.pipeline import AttendancePipeline
from app.config import get_settings

router = APIRouter(prefix="/cameras", tags=["cameras"])
settings = get_settings()
logger = logging.getLogger("attendance.cameras")


class ConnectionManager:
    """Manages active WebSocket connections for broadcasting events."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        logger.info("WebSocket connected. Active: %d", len(self.active))

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        logger.info("WebSocket disconnected. Active: %d", len(self.active))

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


def _open_camera(source: str):
    """Open camera from int index or RTSP URL."""
    src = int(source) if source.isdigit() else source
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera source: {source}")
    # Reduce buffer to minimize latency
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


@router.websocket("/stream")
async def camera_stream(websocket: WebSocket):
    """
    WebSocket endpoint — streams annotated camera frames to the frontend
    and fires attendance events when students are recognized.
    """
    await manager.connect(websocket)
    db = SessionLocal()

    async def on_attendance(student_id: str, confidence: float, frame):
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            logger.warning("Recognized unknown student_id=%s (not in DB)", student_id)
            return

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
            logger.info("Attendance marked: %s (%s) conf=%.2f", student.name, student_id, confidence)

        await manager.broadcast({
            "type": "attendance_marked",
            "student_id": student_id,
            "name": student.name,
            "confidence": confidence,
        })

    pipeline = AttendancePipeline(on_attendance=on_attendance)

    try:
        cap = _open_camera(settings.camera_source)
    except RuntimeError as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        manager.disconnect(websocket)
        db.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Camera read failed — retrying...")
                await asyncio.sleep(0.1)
                continue

            # Process frame through ML pipeline
            annotated = await pipeline.process_frame(frame)

            # Encode as JPEG and send as base64
            _, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 75])
            frame_b64 = base64.b64encode(buffer).decode("utf-8")

            await websocket.send_json({"type": "frame", "data": frame_b64})

            # ~25 FPS cap
            await asyncio.sleep(0.04)

    except WebSocketDisconnect:
        logger.info("Client disconnected from stream")
    except Exception as e:
        logger.error("Stream error: %s", e)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        cap.release()
        manager.disconnect(websocket)
        db.close()


@router.get("/status")
def camera_status():
    """Check if the configured camera source is accessible."""
    try:
        cap = _open_camera(settings.camera_source)
        accessible = cap.isOpened()
        cap.release()
    except Exception:
        accessible = False
    return {
        "camera_accessible": accessible,
        "source": settings.camera_source,
        "active_streams": len(manager.active),
    }
