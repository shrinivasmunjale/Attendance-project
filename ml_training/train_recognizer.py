"""
Build/rebuild face recognition embeddings from the student_faces directory.
Run this after adding new student face images.
Usage: python train_recognizer.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

from app.ml.recognizer import FaceRecognizer


def main():
    print("Building face recognition embeddings...")
    recognizer = FaceRecognizer()
    recognizer.build_embeddings()
    print(f"Done! Embeddings built for {len(recognizer.embeddings)} students.")
    for sid in recognizer.embeddings:
        print(f"  - {sid}: {len(recognizer.embeddings[sid])} embeddings")


if __name__ == "__main__":
    main()
