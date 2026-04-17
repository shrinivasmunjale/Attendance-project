"""
Simple IoU-based multi-object tracker.
Assigns consistent track IDs to detected persons across frames.
"""
import numpy as np
from typing import List, Dict, Tuple


def iou(boxA: Tuple, boxB: Tuple) -> float:
    """Compute Intersection over Union between two bounding boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_area = max(0, xB - xA) * max(0, yB - yA)
    if inter_area == 0:
        return 0.0

    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return inter_area / float(areaA + areaB - inter_area)


class SimpleTracker:
    def __init__(self, iou_threshold: float = 0.3, max_lost: int = 30):
        self.iou_threshold = iou_threshold
        self.max_lost = max_lost
        self.tracks: Dict[int, dict] = {}   # track_id -> {bbox, lost, label}
        self.next_id = 1

    def update(self, detections: List[dict]) -> List[dict]:
        """
        Update tracker with new detections.
        Returns detections enriched with track_id.
        """
        if not self.tracks:
            # Initialize tracks for first frame
            for det in detections:
                self.tracks[self.next_id] = {
                    "bbox": det["bbox"],
                    "lost": 0,
                    "label": None,
                }
                det["track_id"] = self.next_id
                self.next_id += 1
            return detections

        # Match detections to existing tracks via IoU
        track_ids = list(self.tracks.keys())
        matched = set()
        assigned_tracks = set()

        for det in detections:
            best_iou = self.iou_threshold
            best_track = None

            for tid in track_ids:
                if tid in assigned_tracks:
                    continue
                score = iou(det["bbox"], self.tracks[tid]["bbox"])
                if score > best_iou:
                    best_iou = score
                    best_track = tid

            if best_track is not None:
                self.tracks[best_track]["bbox"] = det["bbox"]
                self.tracks[best_track]["lost"] = 0
                det["track_id"] = best_track
                matched.add(best_track)
                assigned_tracks.add(best_track)
            else:
                # New track
                self.tracks[self.next_id] = {
                    "bbox": det["bbox"],
                    "lost": 0,
                    "label": None,
                }
                det["track_id"] = self.next_id
                self.next_id += 1

        # Increment lost counter for unmatched tracks
        for tid in track_ids:
            if tid not in matched:
                self.tracks[tid]["lost"] += 1

        # Remove stale tracks
        self.tracks = {
            tid: t for tid, t in self.tracks.items() if t["lost"] <= self.max_lost
        }

        return detections

    def set_label(self, track_id: int, label: str):
        """Assign a recognized student label to a track."""
        if track_id in self.tracks:
            self.tracks[track_id]["label"] = label

    def get_label(self, track_id: int) -> str:
        """Get the label for a track."""
        track = self.tracks.get(track_id)
        return track["label"] if track else None
