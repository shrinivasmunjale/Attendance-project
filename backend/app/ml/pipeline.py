"""
Full ML pipeline: YOLO detection → face crop → recognition → attendance marking.
Fully async-safe for use inside FastAPI WebSocket handlers.
"""
import cv2
import numpy as np
import asyncio
import logging
from datetime import date
from typing import Callable, Optional

from app.ml.detector import YOLODetector
from app.ml.recognizer import FaceRecognizer
from app.ml.tracker import SimpleTracker

logger = logging.getLogger("attendance.pipeline")


class AttendancePipeline:
    def __init__(self, on_attendance: Optional[Callable] = None):
        """
        on_attendance: async callback(student_id, confidence, frame)
                       called when a student is recognized for the first time today.
        """
        self.detector = YOLODetector()
        self.recognizer = FaceRecognizer()
        self.tracker = SimpleTracker()
        self.on_attendance = on_attendance

        # Track which students have been marked today to avoid duplicates
        self.marked_today: set = set()
        self.current_date = str(date.today())

        # Re-recognize every N frames per track to reduce CPU load
        self.recognize_interval = 10
        self.frame_count: dict = {}   # track_id -> frames since last recognition

    def _reset_daily(self):
        """Reset daily attendance tracking at midnight."""
        today = str(date.today())
        if today != self.current_date:
            self.marked_today.clear()
            self.current_date = today
            logger.info("Daily attendance reset for %s", today)

    async def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a single video frame through the full pipeline.
        Returns annotated frame with bounding boxes and labels.
        """
        self._reset_daily()

        # Step 1: Detect persons via YOLO
        detections = self.detector.detect_persons(frame)

        # Step 2: Update multi-object tracker
        detections = self.tracker.update(detections)

        labels = []
        for det in detections:
            track_id = det.get("track_id")
            existing_label = self.tracker.get_label(track_id)

            # Use cached label if already identified
            if existing_label:
                labels.append(existing_label)
                continue

            # Throttle recognition — only run every N frames per track
            frames_since = self.frame_count.get(track_id, self.recognize_interval)
            if frames_since < self.recognize_interval:
                self.frame_count[track_id] = frames_since + 1
                labels.append("Detecting...")
                continue

            self.frame_count[track_id] = 0

            # Step 3: Crop face region and run recognition in thread pool
            # (CPU-bound work — offload so we don't block the event loop)
            face_crop = self.detector.crop_face_region(frame, det["bbox"])
            student_id, confidence = await asyncio.get_event_loop().run_in_executor(
                None, self.recognizer.recognize, face_crop
            )

            if student_id:
                self.tracker.set_label(track_id, student_id)
                labels.append(student_id)
                logger.debug("Recognized %s (conf=%.2f)", student_id, confidence)

                # Step 4: Fire attendance callback once per student per day
                if student_id not in self.marked_today and self.on_attendance:
                    self.marked_today.add(student_id)
                    try:
                        await self.on_attendance(student_id, confidence, frame)
                    except Exception as e:
                        logger.error("Attendance callback error: %s", e)
            else:
                labels.append("Unknown")

        # Step 5: Draw annotated bounding boxes on frame
        annotated = self.detector.draw_detections(frame, detections, labels)
        return annotated
