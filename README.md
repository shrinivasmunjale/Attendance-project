# AttendAI — CCTV-Based Student Attendance System

Automated student attendance using CCTV cameras, YOLOv8 person detection, and DeepFace recognition.

## Stack

| Layer | Tech |
|---|---|
| Detection | YOLOv8 (Ultralytics) |
| Recognition | DeepFace (ArcFace model) |
| Tracking | IoU-based multi-object tracker |
| Backend | FastAPI + SQLAlchemy + SQLite |
| Frontend | React + Vite + Tailwind CSS |
| Deployment | Docker + docker-compose |

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Download YOLOv8 weights (auto-downloads on first run via ultralytics):
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

Copy the downloaded `yolov8n.pt` to `backend/models_weights/`.

Start the API:
```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

### 3. Register Students

**Step 1** — Add student via UI or API:
```bash
POST /students
{ "student_id": "STU001", "name": "John Doe", "department": "CS", "semester": 3 }
```

**Step 2** — Collect face samples:
```bash
cd ml_training
python collect_faces.py --student_id STU001 --samples 30
```

**Step 3** — Build embeddings:
```bash
python train_recognizer.py
```

### 4. Start Attendance

1. Open the app at http://localhost:5173
2. Login (register first via `POST /auth/register`)
3. Go to **Live Monitor**
4. Click **Start** to begin camera feed
5. Students walking in front of the camera will be automatically detected and marked present

## Docker Deployment

```bash
docker-compose up --build
```

Frontend: http://localhost  
Backend API: http://localhost:8000

## Project Structure

```
attendance-system/
├── backend/          # FastAPI + ML pipeline
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── ml/       # YOLO + face recognition pipeline
│   │   ├── models/   # DB models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   └── data/         # Student face images
├── frontend/         # React + Vite
│   └── src/
│       ├── pages/    # Dashboard, LiveMonitor, Students, Attendance
│       ├── components/
│       ├── api/      # Axios API calls
│       └── store/    # Zustand state
├── ml_training/      # Face collection & embedding scripts
└── docker-compose.yml
```

## CCTV Camera Setup

Edit `backend/.env`:
```
# Webcam
CAMERA_SOURCE=0

# IP Camera / CCTV (RTSP)
CAMERA_SOURCE=rtsp://username:password@192.168.1.100:554/stream
```

## Notes

- Face recognition threshold can be tuned in `.env` (`FACE_RECOGNITION_THRESHOLD`)
- Each student needs at least 10–20 face images for reliable recognition
- The system marks attendance once per student per day
- Confidence score is stored with each attendance record
