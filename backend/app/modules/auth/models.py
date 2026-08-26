from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=64, unique=True, index=True)
    email: Optional[str] = Field(default=None, max_length=128, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    is_admin: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow)

    images: list["Image"] = Relationship(back_populates="owner", cascade_delete=True)
    api_keys: list["ApiKey"] = Relationship(back_populates="owner", cascade_delete=True)


class UserPublic(SQLModel):
    id: int
    username: str
    email: Optional[str] = None
    is_admin: bool
    is_active: bool
    created_at: datetime
