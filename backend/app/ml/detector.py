"""
YOLO-based person detector.
Auto-downloads YOLOv8n weights on first run via ultralytics.
"""
import logging
import os
import cv2
import numpy as np

# Fix for PyTorch 2.6+ weights_only restriction
# Monkey-patch torch.load to use weights_only=False by default
import torch
_original_load = torch.load
def _patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load

from ultralytics import YOLO
from typing import List, Tuple
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("attendance.detector")


def _ensure_yolo_model(path: str) -> str:
    """
    Return model path. If the file doesn't exist, let ultralytics
    auto-download yolov8n.pt into the models_weights directory.
    """
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logger.info("YOLOv8 weights not found at %s — downloading...", path)
        # ultralytics downloads to cwd by default; we move it after
        model = YOLO("yolov8n.pt")
        src = "yolov8n.pt"
        if os.path.exists(src) and src != path:
            os.rename(src, path)
        logger.info("YOLOv8 weights saved to %s", path)
        return path
    return path


class YOLODetector:
    _instance = None   # singleton so model loads once

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        model_path = _ensure_yolo_model(settings.yolo_model_path)
        logger.info("Loading YOLO model from %s ...", model_path)
        self.model = YOLO(model_path)
        # Warm up with a dummy frame so first real frame is fast
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        self.model(dummy, verbose=False)
        logger.info("YOLO model ready ✅")
        self.confidence = settings.yolo_confidence
        self.person_class_id = 0
        self._initialized = True

    def detect_persons(self, frame: np.ndarray) -> List[dict]:
        """
        Detect persons in a frame.
        Returns list of dicts: {bbox, confidence, class}
        """
        results = self.model(
            frame,
            conf=self.confidence,
            classes=[self.person_class_id],
            verbose=False,
        )
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                # Skip very small detections (likely noise)
                if (x2 - x1) < 30 or (y2 - y1) < 60:
                    continue
                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "confidence": conf,
                    "class": "person",
                })
        return detections

    def crop_face_region(
        self, frame: np.ndarray, bbox: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """
        Crop the face region from a person bounding box.
        Takes the top 35% of the person bbox as the face area.
        """
        x1, y1, x2, y2 = bbox
        height = y2 - y1
        face_y2 = y1 + int(height * 0.35)
        # Clamp to frame bounds
        face_y2 = min(face_y2, frame.shape[0])
        x1 = max(0, x1)
        x2 = min(x2, frame.shape[1])
        face_crop = frame[y1:face_y2, x1:x2]
        return face_crop

    @staticmethod
    def is_face_quality_ok(face_crop: np.ndarray, min_size: int = 40) -> bool:
        """
        Basic face quality check:
        - Minimum size
        - Not too blurry (Laplacian variance)
        """
        if face_crop is None or face_crop.size == 0:
            return False
        h, w = face_crop.shape[:2]
        if h < min_size or w < min_size:
            return False
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 20.0:   # too blurry
            return False
        return True

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[dict],
        labels: List[str] = None,
    ) -> np.ndarray:
        """Draw bounding boxes and labels on frame."""
        annotated = frame.copy()
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det["bbox"]
            label = labels[i] if labels and i < len(labels) else "Unknown"
            conf = det["confidence"]

            # Green for identified, red for unknown
            color = (0, 200, 0) if label not in ("Unknown", "Detecting...") else (0, 60, 220)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Label background
            text = f"{label} {conf:.0%}"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
            cv2.putText(
                annotated, text,
                (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                (255, 255, 255), 1,
            )
        return annotated
