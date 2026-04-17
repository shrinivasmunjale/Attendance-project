import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, SessionLocal
from app.api import students, attendance, cameras, auth
from app.config import get_settings

settings = get_settings()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("attendance")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Student Attendance System",
    description="Automated attendance tracking using CCTV + YOLO + Face Recognition",
    version="1.0.0",
)

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(cameras.router)


def _seed_admin():
    """Create a default admin user if no users exist."""
    from app.models.user import User
    from app.api.auth import hash_password

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username="admin",
                email="admin@attendai.local",
                hashed_password=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            logger.info("✅ Default admin created  →  username: admin  password: admin123")
            logger.warning("⚠️  Change the default password after first login!")
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data on startup."""
    init_db()
    _seed_admin()
    logger.info("✅ Database initialized")
    logger.info("✅ Attendance System API is running at http://localhost:8000")
    logger.info("📖 API docs: http://localhost:8000/docs")


@app.get("/")
def root():
    return {
        "message": "Student Attendance System API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
