from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.images.models import Image
from app.modules.tags.items import ImageTagsUpdateItem, TagCreateItem, TagUpdateItem
from app.modules.tags.models import ImageTag, Tag, TagBrief, TagPublic

router = APIRouter(prefix="/api/tags", tags=["tags"])
image_tags_router = APIRouter(prefix="/api/images", tags=["tags"])

MAX_TAG_NAME_LEN = 32


def _validate_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标签名不能为空")
    if len(name) > MAX_TAG_NAME_LEN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"标签名不能超过 {MAX_TAG_NAME_LEN} 个字符")
    return name


def _get_owned_tag(tag_id: int, user: User, db: Session) -> Tag:
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.owner_id == user.id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    return tag


def _get_owned_image(image_id: int, user: User, db: Session) -> Image:
    image = db.query(Image).filter(Image.id == image_id, Image.owner_id == user.id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    return image


@router.get("", response_model=list[TagPublic])
def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Tag, func.count(ImageTag.image_id))
        .outerjoin(ImageTag, ImageTag.tag_id == Tag.id)
        .filter(Tag.owner_id == current_user.id)
        .group_by(Tag.id)
        .order_by(Tag.created_at.desc())
        .all()
    )
    return [
        TagPublic(id=tag.id, name=tag.name, image_count=count, created_at=tag.created_at)
        for tag, count in rows
    ]


@router.post("", response_model=TagPublic)
def create_tag(
    item: TagCreateItem,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = _validate_name(item.name)
    exists = db.query(Tag).filter(Tag.owner_id == current_user.id, Tag.name == name).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标签已存在")
    tag = Tag(owner_id=current_user.id, name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return TagPublic(id=tag.id, name=tag.name, image_count=0, created_at=tag.created_at)


@router.put("/{tag_id}", response_model=TagPublic)
def rename_tag(
    tag_id: int,
    item: TagUpdateItem,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tag = _get_owned_tag(tag_id, current_user, db)
    name = _validate_name(item.name)
    exists = (
        db.query(Tag)
        .filter(Tag.owner_id == current_user.id, Tag.name == name, Tag.id != tag_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标签已存在")
    tag.name = name
    db.commit()
    db.refresh(tag)
    count = db.query(func.count(ImageTag.image_id)).filter(ImageTag.tag_id == tag.id).scalar() or 0
    return TagPublic(id=tag.id, name=tag.name, image_count=count, created_at=tag.created_at)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tag = _get_owned_tag(tag_id, current_user, db)
    db.delete(tag)
    db.commit()


@image_tags_router.get("/{image_id}/tags", response_model=list[TagBrief])
def list_image_tags(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image = _get_owned_image(image_id, current_user, db)
    return image.tags


@image_tags_router.put("/{image_id}/tags", response_model=list[TagBrief])
def set_image_tags(
    image_id: int,
    item: ImageTagsUpdateItem,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image = _get_owned_image(image_id, current_user, db)
    tag_ids = list(dict.fromkeys(item.tag_ids))
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids), Tag.owner_id == current_user.id).all()
    if len(tags) != len(tag_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="包含无效的标签")
    image.tags = tags
    db.commit()
    db.refresh(image)
    return image.tags