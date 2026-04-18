"""
Face recognizer using OpenCV DNN + ONNX ArcFace model.
No TensorFlow or DeepFace required.

Models used:
  - Face detection:  OpenCV Haar cascade (built-in)
  - Face embedding:  ArcFace ONNX model (downloaded on first run)
"""
import os
import cv2
import numpy as np
import pickle
import urllib.request
from typing import Optional, Tuple

# Fix for PyTorch 2.6+ (in case ONNX runtime uses torch internally)
try:
    import torch
    _original_load = torch.load
    def _patched_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return _original_load(*args, **kwargs)
    torch.load = _patched_load
except ImportError:
    pass  # torch not installed, skip patch

from app.config import get_settings

settings = get_settings()

EMBEDDINGS_CACHE = "data/embeddings_cache.pkl"

# Lightweight ArcFace ONNX model (~100 MB) from ONNX Model Zoo
# Alternative URLs in case primary fails
ARCFACE_MODEL_URLS = [
    # Primary: ONNX Model Zoo (GitHub)
    "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/arcface/model/arcface-lresnet100e-opset8.onnx",
    # Backup: Direct from Hugging Face
    "https://huggingface.co/datasets/Xenova/onnx-models/resolve/main/arcface_lresnet100e_opset8.onnx",
]
ARCFACE_MODEL_PATH = "models_weights/arcface.onnx"


def _download_model():
    """Download ArcFace ONNX model if not present."""
    if os.path.exists(ARCFACE_MODEL_PATH):
        return
    os.makedirs("models_weights", exist_ok=True)
    
    print("[Recognizer] Downloading ArcFace ONNX model (~100 MB)...")
    
    for url in ARCFACE_MODEL_URLS:
        try:
            print(f"[Recognizer] Trying: {url}")
            # Use longer timeout and retry logic
            import urllib.request
            import socket
            
            # Set longer timeout
            socket.setdefaulttimeout(300)  # 5 minutes
            
            urllib.request.urlretrieve(url, ARCFACE_MODEL_PATH)
            print("[Recognizer] Download complete.")
            return
        except Exception as e:
            print(f"[Recognizer] Download failed from {url}: {e}")
            if os.path.exists(ARCFACE_MODEL_PATH):
                os.remove(ARCFACE_MODEL_PATH)
            continue
    
    raise RuntimeError("Failed to download ArcFace model from all sources")


def _preprocess_face(face_img: np.ndarray) -> np.ndarray:
    """Resize and normalize face image for ArcFace input (112x112)."""
    face = cv2.resize(face_img, (112, 112))
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    face = face.astype(np.float32) / 255.0
    face = (face - 0.5) / 0.5          # normalize to [-1, 1]
    face = np.transpose(face, (2, 0, 1))  # HWC -> CHW
    face = np.expand_dims(face, axis=0)   # add batch dim
    return face


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two embedding vectors."""
    a = a / (np.linalg.norm(a) + 1e-10)
    b = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a, b))


class FaceDetector:
    """Lightweight face detector using OpenCV Haar cascade."""

    def __init__(self):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.cascade = cv2.CascadeClassifier(cascade_path)

    def detect_and_crop(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect the largest face in image and return cropped region."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

        if len(faces) == 0:
            return None

        # Pick the largest face
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        # Add small padding
        pad = int(0.1 * w)
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(image.shape[1], x + w + pad)
        y2 = min(image.shape[0], y + h + pad)
        return image[y1:y2, x1:x2]


class FaceRecognizer:
    def __init__(self):
        self.face_db_path = settings.face_db_path
        self.threshold = settings.face_recognition_threshold
        self.embeddings: dict = {}        # {student_id: [embedding, ...]}
        self.face_detector = FaceDetector()
        self._session = None              # lazy-loaded ONNX session
        self._load_embeddings()

    def _get_session(self):
        """Lazy-load ONNX runtime session."""
        if self._session is None:
            import onnxruntime as ort
            _download_model()
            self._session = ort.InferenceSession(
                ARCFACE_MODEL_PATH,
                providers=["CPUExecutionProvider"],
            )
        return self._session

    def _get_embedding(self, face_img: np.ndarray) -> Optional[np.ndarray]:
        """Get ArcFace embedding for a face image."""
        if face_img is None or face_img.size == 0:
            return None
        try:
            session = self._get_session()
            input_name = session.get_inputs()[0].name
            blob = _preprocess_face(face_img)
            outputs = session.run(None, {input_name: blob})
            embedding = outputs[0][0]
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"[Recognizer] Embedding error: {e}")
            return None

    def _load_embeddings(self):
        """Load pre-computed embeddings from cache or build from scratch."""
        if os.path.exists(EMBEDDINGS_CACHE):
            with open(EMBEDDINGS_CACHE, "rb") as f:
                self.embeddings = pickle.load(f)
            print(f"[Recognizer] Loaded embeddings for {len(self.embeddings)} students.")
        else:
            self.build_embeddings()

    def build_embeddings(self):
        """
        Build face embeddings from student_faces directory.
        Structure: data/student_faces/<student_id>/<image>.jpg
        """
        self.embeddings = {}
        if not os.path.exists(self.face_db_path):
            print("[Recognizer] Face DB path not found. Skipping.")
            return

        for student_id in os.listdir(self.face_db_path):
            student_dir = os.path.join(self.face_db_path, student_id)
            if not os.path.isdir(student_dir):
                continue

            student_embeddings = []
            for img_file in os.listdir(student_dir):
                img_path = os.path.join(student_dir, img_file)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                
                # Try to detect and crop face, fallback to full image if detection fails
                face = self.face_detector.detect_and_crop(img)
                if face is None or face.size == 0:
                    face = img
                
                emb = self._get_embedding(face)
                if emb is not None:
                    student_embeddings.append(emb)

            if student_embeddings:
                self.embeddings[student_id] = student_embeddings

        os.makedirs(os.path.dirname(EMBEDDINGS_CACHE), exist_ok=True)
        with open(EMBEDDINGS_CACHE, "wb") as f:
            pickle.dump(self.embeddings, f)

        print(f"[Recognizer] Built embeddings for {len(self.embeddings)} students.")

    def recognize(self, face_crop: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Identify a student from a face crop.
        Returns (student_id, confidence) or (None, 0.0).
        """
        if face_crop is None or face_crop.size == 0:
            return None, 0.0

        # Try to detect face in the crop, fallback to using the crop itself
        face = self.face_detector.detect_and_crop(face_crop)
        if face is None or face.size == 0:
            face = face_crop
        
        query_emb = self._get_embedding(face)
        if query_emb is None:
            return None, 0.0

        best_match = None
        best_score = -1.0

        for student_id, embeddings in self.embeddings.items():
            for emb in embeddings:
                score = _cosine_similarity(query_emb, emb)
                if score > best_score:
                    best_score = score
                    best_match = student_id

        if best_score >= self.threshold:
            return best_match, round(best_score, 3)

        return None, round(max(0.0, best_score), 3)

    def register_student_face(self, student_id: str, image: np.ndarray) -> bool:
        """Save a new face image and rebuild embeddings."""
        student_dir = os.path.join(self.face_db_path, student_id)
        os.makedirs(student_dir, exist_ok=True)

        existing = len(os.listdir(student_dir))
        img_path = os.path.join(student_dir, f"{existing + 1}.jpg")
        cv2.imwrite(img_path, image)

        # Invalidate cache and rebuild
        if os.path.exists(EMBEDDINGS_CACHE):
            os.remove(EMBEDDINGS_CACHE)
        self.build_embeddings()
        return True
