import logging
import asyncio
import base64
import cv2
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.models.attendance import AttendanceRecord
from app.models.student import Student
from app.ml.pipeline import AttendancePipeline
from app.config import get_settings

router = APIRouter(prefix="/cameras", tags=["cameras"])
settings = get_settings()
logger = logging.getLogger("attendance.cameras")


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

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
    src = int(source) if source.isdigit() else source
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera source: {source}")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


@router.websocket("/stream")
async def camera_stream(websocket: WebSocket):
    """WebSocket: streams annotated frames and fires attendance events."""
    await manager.connect(websocket)

    async def on_attendance(student_id: str, confidence: float, frame):
        student = await Student.find_one(Student.student_id == student_id)
        if not student:
            return

        today = str(datetime.now().date())
        existing = await AttendanceRecord.find_one(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.date == today,
        )
        if not existing:
            record = AttendanceRecord(
                student_id=student_id,
                student_name=student.name,
                date=today,
                time_in=datetime.now(),
                status="present",
                confidence=confidence,
                camera_id="main",
            )
            await record.insert()
            logger.info("Attendance marked: %s conf=%.2f", student.name, confidence)

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
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.1)
                continue

            annotated = await pipeline.process_frame(frame)
            _, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 75])
            frame_b64 = base64.b64encode(buffer).decode("utf-8")

            await websocket.send_json({"type": "frame", "data": frame_b64})
            await asyncio.sleep(0.04)

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error("Stream error: %s", e)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        cap.release()
        manager.disconnect(websocket)


@router.get("/status")
def camera_status():
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
