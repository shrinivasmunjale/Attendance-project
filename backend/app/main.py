import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import students, attendance, cameras, auth
from app.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("attendance")

app = FastAPI(
    title="Student Attendance System",
    description="Automated attendance tracking using CCTV + YOLO + Face Recognition",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(cameras.router)


async def _seed_admin():
    """Create default admin if no users exist."""
    from app.models.user import User
    from app.api.auth import hash_password

    if await User.count() == 0:
        admin = User(
            username="admin",
            email="admin@attendai.local",
            hashed_password=hash_password("admin123"),
            role="admin",
        )
        await admin.insert()
        logger.info("✅ Default admin created  →  username: admin  password: admin123")
        logger.warning("⚠️  Change the default password after first login!")


@app.on_event("startup")
async def startup_event():
    await init_db()
    await _seed_admin()
    logger.info("✅ Attendance System API running at http://localhost:8000")
    logger.info("📖 API docs: http://localhost:8000/docs")


@app.get("/")
def root():
    return {"message": "Student Attendance System API", "docs": "/docs", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0", "db": "mongodb"}
