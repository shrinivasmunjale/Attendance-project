#!/usr/bin/env python3
"""Test face recognition system"""
import sys
import os
import pickle

print("=" * 60)
print("  Face Recognition System Test")
print("=" * 60)
print()

# Check face photos
faces_dir = "data/student_faces"
if not os.path.exists(faces_dir):
    print("❌ Face directory not found:", faces_dir)
    sys.exit(1)

students = [d for d in os.listdir(faces_dir) if os.path.isdir(os.path.join(faces_dir, d))]
print(f"✅ Students with face photos: {len(students)}")
for student_id in students:
    student_dir = os.path.join(faces_dir, student_id)
    photos = [f for f in os.listdir(student_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    print(f"   - {student_id}: {len(photos)} photos")

print()

# Check embeddings cache
cache_file = "data/embeddings_cache.pkl"
if not os.path.exists(cache_file):
    print("❌ Embeddings cache not found!")
    print("   Run: Go to Settings → Rebuild Face Embeddings")
    sys.exit(1)

print(f"✅ Embeddings cache exists: {cache_file}")
print(f"   Size: {os.path.getsize(cache_file)} bytes")

# Load and check embeddings
try:
    with open(cache_file, "rb") as f:
        embeddings = pickle.load(f)
    
    print(f"✅ Embeddings loaded successfully")
    print(f"   Students in cache: {len(embeddings)}")
    
    for student_id, emb_list in embeddings.items():
        print(f"   - {student_id}: {len(emb_list)} embeddings")
        if len(emb_list) > 0:
            print(f"     Embedding shape: {emb_list[0].shape}")
    
    if len(embeddings) == 0:
        print()
        print("⚠️  WARNING: Embeddings cache is empty!")
        print("   Go to Settings → Rebuild Face Embeddings")
        sys.exit(1)
    
except Exception as e:
    print(f"❌ Error loading embeddings: {e}")
    sys.exit(1)

print()

# Test face recognizer
print("Testing FaceRecognizer initialization...")
try:
    from app.ml.recognizer import FaceRecognizer
    recognizer = FaceRecognizer()
    print(f"✅ FaceRecognizer initialized")
    print(f"   Loaded {len(recognizer.embeddings)} students")
    print(f"   Recognition threshold: {recognizer.threshold}")
    
    if len(recognizer.embeddings) == 0:
        print()
        print("⚠️  WARNING: No embeddings loaded!")
        print("   Possible issues:")
        print("   1. No face photos uploaded")
        print("   2. Embeddings not rebuilt after uploading photos")
        print("   3. ArcFace model not downloaded")
        print()
        print("   Solution: Go to Settings → Rebuild Face Embeddings")
        sys.exit(1)
    
except Exception as e:
    print(f"❌ Error initializing recognizer: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test with a sample face photo
print("Testing recognition with sample photo...")
try:
    import cv2
    import numpy as np
    
    # Get first student's first photo
    first_student = students[0]
    student_dir = os.path.join(faces_dir, first_student)
    photos = [f for f in os.listdir(student_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    if len(photos) == 0:
        print("⚠️  No photos found for testing")
    else:
        test_photo = os.path.join(student_dir, photos[0])
        print(f"   Testing with: {test_photo}")
        
        img = cv2.imread(test_photo)
        if img is None:
            print(f"❌ Could not read image: {test_photo}")
        else:
            print(f"   Image loaded: {img.shape}")
            
            # Test recognition
            student_id, confidence = recognizer.recognize(img)
            
            if student_id:
                print(f"✅ Recognition successful!")
                print(f"   Recognized as: {student_id}")
                print(f"   Confidence: {confidence:.3f}")
                
                if student_id == first_student:
                    print(f"   ✅ Correct match!")
                else:
                    print(f"   ⚠️  Matched different student (expected {first_student})")
            else:
                print(f"❌ Recognition failed")
                print(f"   Best confidence: {confidence:.3f}")
                print(f"   Threshold: {recognizer.threshold}")
                print()
                print("   Possible issues:")
                print("   1. Face not detected in photo")
                print("   2. Confidence below threshold")
                print("   3. Poor photo quality")
                print()
                print("   Try:")
                print("   - Upload clearer photos")
                print("   - Lower threshold in .env: FACE_RECOGNITION_THRESHOLD=0.5")
                print("   - Rebuild embeddings")

except Exception as e:
    print(f"❌ Error during recognition test: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("  Test Complete")
print("=" * 60)
