#!/usr/bin/env python3
"""Test building face embeddings"""
import sys

print("=" * 60)
print("  Building Face Embeddings")
print("=" * 60)
print()

try:
    from app.ml.recognizer import FaceRecognizer
    
    print("Initializing FaceRecognizer...")
    recognizer = FaceRecognizer()
    
    print(f"✅ Recognizer initialized")
    print(f"   Face DB path: {recognizer.face_db_path}")
    print(f"   Threshold: {recognizer.threshold}")
    print()
    
    print("Building embeddings from face photos...")
    recognizer.build_embeddings()
    
    print()
    print(f"✅ Embeddings built successfully!")
    print(f"   Total students: {len(recognizer.embeddings)}")
    
    for student_id, embeddings in recognizer.embeddings.items():
        print(f"   - {student_id}: {len(embeddings)} embeddings")
    
    if len(recognizer.embeddings) == 0:
        print()
        print("⚠️  WARNING: No embeddings were created!")
        print("   Possible issues:")
        print("   1. No face photos in data/student_faces/")
        print("   2. ArcFace model download failed")
        print("   3. Face detection failed on all photos")
        sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("  Success!")
print("=" * 60)
