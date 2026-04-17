"""
YOLO-based person and face detector.
Uses YOLOv8 to detect persons in a frame, then crops face regions.
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
from app.config import get_settings

settings = get_settings()


class YOLODetector:
    def __init__(self):
        self.model = YOLO(settings.yolo_model_path)
        self.confidence = settings.yolo_confidence
        # Class 0 = person in COCO dataset
        self.person_class_id = 0

    def detect_persons(self, frame: np.ndarray) -> List[dict]:
        """
        Detect persons in a frame.
        Returns list of dicts with bbox, confidence.
        """
        results = self.model(frame, conf=self.confidence, classes=[self.person_class_id])
        detections = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
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
        Crop the upper-body/face region from a person bounding box.
        Assumes face is in the top ~35% of the person bbox.
        """
        x1, y1, x2, y2 = bbox
        height = y2 - y1
        face_y2 = y1 + int(height * 0.35)
        face_crop = frame[y1:face_y2, x1:x2]
        return face_crop

    def draw_detections(
        self, frame: np.ndarray, detections: List[dict], labels: List[str] = None
    ) -> np.ndarray:
        """Draw bounding boxes and labels on frame."""
        annotated = frame.copy()
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det["bbox"]
            label = labels[i] if labels and i < len(labels) else "Unknown"
            conf = det["confidence"]

            color = (0, 255, 0) if label != "Unknown" else (0, 0, 255)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                annotated,
                f"{label} ({conf:.2f})",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )
        return annotated
