"""Database models."""
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Integer, String

from app.database import Base


class RoleEnum(str, enum.Enum):
    ADMIN = "Admin"
    USER = "User"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone_number = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(RoleEnum, values_callable=lambda e: [m.value for m in e], native_enum=False),
        nullable=False,
        default=RoleEnum.USER,
    )
    created_date = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
