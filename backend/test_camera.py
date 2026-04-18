#!/usr/bin/env python3
"""Quick camera test script"""
import cv2
import sys

print("Testing camera access...")
print("-" * 50)

# Try camera index 0 (default laptop camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot open camera 0")
    print("Trying camera 1...")
    cap = cv2.VideoCapture(1)
    
if not cap.isOpened():
    print("❌ Cannot open camera 1")
    print("\nPossible issues:")
    print("1. Camera is being used by another application")
    print("2. Camera permissions not granted")
    print("3. No camera available")
    sys.exit(1)

print("✅ Camera opened successfully!")

# Try to read a frame
ret, frame = cap.read()
if ret:
    print(f"✅ Can read frames: {frame.shape}")
    print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
    print(f"   Channels: {frame.shape[2]}")
else:
    print("❌ Cannot read frames from camera")
    cap.release()
    sys.exit(1)

# Test reading multiple frames
success_count = 0
for i in range(10):
    ret, frame = cap.read()
    if ret:
        success_count += 1

print(f"✅ Successfully read {success_count}/10 test frames")

cap.release()
print("\n" + "=" * 50)
print("✅ Camera test PASSED - Your camera is working!")
print("=" * 50)
