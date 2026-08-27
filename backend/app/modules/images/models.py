from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.modules.tags.models import ImageTag, TagBrief  # noqa: F401


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    filename: str = Field(max_length=255)
    original_name: str = Field(max_length=255)
    storage_path: str = Field(max_length=512)
    url: str = Field(max_length=512)
    mime_type: str = Field(max_length=64)
    size: int
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime = Field(default_factory=utcnow)

    owner: Optional["User"] = Relationship(back_populates="images")
    tags: list["Tag"] = Relationship(back_populates="images", link_model=ImageTag)


class ImagePublic(SQLModel):
    id: int
    owner_id: int
    owner_username: Optional[str] = None
    url: str
    original_name: str
    mime_type: str
    size: int
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    tags: list[TagBrief] = []
