from beanie import Document, Indexed
from typing import Optional
from datetime import datetime


class User(Document):
    username: Indexed(str, unique=True)
    email: Indexed(str, unique=True)
    hashed_password: str
    role: str = "teacher"       # admin / teacher
    is_active: bool = True
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "users"

    def __repr__(self):
        return f"<User {self.username} role={self.role}>"
