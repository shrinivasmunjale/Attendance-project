"""
Collect face samples for a student using webcam.
Usage: python collect_faces.py --student_id STU001 --samples 30
"""
import cv2
import os
import argparse

FACE_DB_PATH = "../backend/data/student_faces"


def collect_faces(student_id: str, num_samples: int = 30):
    student_dir = os.path.join(FACE_DB_PATH, student_id)
    os.makedirs(student_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    count = 0
    print(f"Collecting {num_samples} face samples for {student_id}. Press 'q' to quit.")

    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for x, y, w, h in faces:
            face_crop = frame[y : y + h, x : x + w]
            img_path = os.path.join(student_dir, f"{count + 1}.jpg")
            cv2.imwrite(img_path, face_crop)
            count += 1

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Captured: {count}/{num_samples}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Collecting Faces", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Done! Saved {count} images to {student_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--student_id", required=True, help="Student ID (e.g. STU001)")
    parser.add_argument("--samples", type=int, default=30, help="Number of face samples")
    args = parser.parse_args()
    collect_faces(args.student_id, args.samples)
