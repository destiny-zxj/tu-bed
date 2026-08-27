from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ImageTag(SQLModel, table=True):
    __tablename__ = "image_tags"

    image_id: Optional[int] = Field(default=None, foreign_key="images.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_tag_owner_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=32)
    created_at: datetime = Field(default_factory=utcnow)

    images: list["Image"] = Relationship(back_populates="tags", link_model=ImageTag)


class TagBrief(SQLModel):
    id: int
    name: str


class TagPublic(SQLModel):
    id: int
    name: str
    image_count: int
    created_at: datetime