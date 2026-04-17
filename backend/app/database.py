import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("attendance.db")

# Global Motor client — reused across requests
_client: AsyncIOMotorClient = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_url)
    return _client


async def init_db():
    """Initialize Beanie with all document models."""
    from app.models.student import Student
    from app.models.attendance import AttendanceRecord
    from app.models.user import User

    client = get_client()
    db = client[settings.mongodb_db_name]

    await init_beanie(
        database=db,
        document_models=[Student, AttendanceRecord, User],
    )
    logger.info("✅ MongoDB connected — db: %s", settings.mongodb_db_name)
