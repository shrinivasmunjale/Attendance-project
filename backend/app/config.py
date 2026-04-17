from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Attendance System"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./attendance.db"

    # JWT Auth
    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    # YOLO
    yolo_model_path: str = "models_weights/yolov8n.pt"
    yolo_confidence: float = 0.5

    # Face recognition
    face_db_path: str = "data/student_faces"
    face_recognition_threshold: float = 0.6

    # Camera
    camera_source: str = "0"  # 0 for webcam, or RTSP URL for CCTV

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
