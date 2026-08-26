from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApiKey(SQLModel, table=True):
    __tablename__ = "api_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=128)
    key_hash: str = Field(max_length=255, unique=True, index=True)
    prefix: str = Field(max_length=16)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow)
    last_used_at: Optional[datetime] = None

    owner: Optional["User"] = Relationship(back_populates="api_keys")


class ApiKeyPublic(SQLModel):
    id: int
    name: str
    prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None


class ApiKeyCreated(ApiKeyPublic):
    key: str  # 仅在创建时返回一次明文
