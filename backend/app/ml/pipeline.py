"""
Full ML pipeline: YOLO detection → face crop → recognition → attendance marking.
"""
import cv2
import numpy as np
import asyncio
from datetime import datetime, date
from typing import Callable, Optional
from app.ml.detector import YOLODetector
from app.ml.recognizer import FaceRecognizer
from app.ml.tracker import SimpleTracker


class AttendancePipeline:
    def __init__(self, on_attendance: Optional[Callable] = None):
        """
        on_attendance: async callback(student_id, confidence, frame)
                       called when a student is recognized.
        """
        self.detector = YOLODetector()
        self.recognizer = FaceRecognizer()
        self.tracker = SimpleTracker()
        self.on_attendance = on_attendance

        # Track which students have been marked today to avoid duplicates
        self.marked_today: set = set()
        self.current_date = str(date.today())

        # Re-recognize every N frames per track to reduce compute
        self.recognize_interval = 10
        self.frame_count: dict = {}   # track_id -> frames since last recognition

    def reset_daily(self):
        """Reset daily attendance tracking."""
        today = str(date.today())
        if today != self.current_date:
            self.marked_today.clear()
            self.current_date = today

    async def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a single video frame.
        Returns annotated frame with bounding boxes and labels.
        """
        self.reset_daily()

        # Step 1: Detect persons
        detections = self.detector.detect_persons(frame)

        # Step 2: Update tracker
        detections = self.tracker.update(detections)

        labels = []
        for det in detections:
            track_id = det.get("track_id")
            existing_label = self.tracker.get_label(track_id)

            # Use cached label if available
            if existing_label:
                labels.append(existing_label)
                continue

            # Throttle recognition per track
            frames_since = self.frame_count.get(track_id, self.recognize_interval)
            if frames_since < self.recognize_interval:
                self.frame_count[track_id] = frames_since + 1
                labels.append("Detecting...")
                continue

            self.frame_count[track_id] = 0

            # Step 3: Crop face and recognize
            face_crop = self.detector.crop_face_region(frame, det["bbox"])
            student_id, confidence = self.recognizer.recognize(face_crop)

            if student_id:
                self.tracker.set_label(track_id, student_id)
                labels.append(student_id)

                # Step 4: Mark attendance (once per student per day)
                if student_id not in self.marked_today and self.on_attendance:
                    self.marked_today.add(student_id)
                    await self.on_attendance(student_id, confidence, frame)
            else:
                labels.append("Unknown")

        # Step 5: Annotate frame
        annotated = self.detector.draw_detections(frame, detections, labels)
        return annotated

    def process_frame_sync(self, frame: np.ndarray) -> np.ndarray:
        """Synchronous wrapper for process_frame."""
        return asyncio.get_event_loop().run_until_complete(self.process_frame(frame))
