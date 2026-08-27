from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user, hash_api_key
from app.core.storage import delete_file, is_allowed_extension, save_upload
from app.core.config import settings
from app.modules.auth.models import User
from app.modules.apikeys.models import ApiKey
from app.modules.images.items import ImageListQueryItem
from app.modules.images.models import Image, ImagePublic
from app.modules.tags.models import ImageTag

router = APIRouter(prefix="/api/images", tags=["images"])


def _resolve_api_key_user(api_key: str, db: Session) -> Optional[User]:
    if not api_key:
        return None
    key_hash = hash_api_key(api_key)
    record = db.query(ApiKey).filter(ApiKey.key_hash == key_hash, ApiKey.is_active.is_(True)).first()
    if not record:
        return None
    record.last_used_at = datetime.now(timezone.utc)
    db.commit()
    return record.owner


def _get_uploader(api_key: Optional[str], current_user: Optional[User], db: Session) -> User:
    if current_user is not None:
        return current_user
    if api_key:
        user = _resolve_api_key_user(api_key, db)
        if user:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未认证")


@router.post("/upload", response_model=ImagePublic)
async def upload_image(
    file: UploadFile = File(...),
    api_key: str = Query(None, description="API Key (用于无登录态上传)"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    uploader = _get_uploader(api_key, current_user, db)

    if file.size and file.size > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件超过最大限制 {settings.max_upload_size_mb}MB",
        )
    if not is_allowed_extension(file.filename or ""):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="不支持的文件格式")

    content = await file.read()
    try:
        meta = save_upload(content, file.filename or "upload.bin", uploader.username)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    image = Image(
        owner_id=uploader.id,
        filename=meta["filename"],
        original_name=meta["original_name"],
        storage_path=meta["storage_path"],
        url=meta["url"],
        mime_type=file.content_type or "application/octet-stream",
        size=len(content),
        width=meta["width"],
        height=meta["height"],
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.get("", response_model=dict)
def list_images(
    query: ImageListQueryItem = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    page = max(1, query.page)
    page_size = min(max(1, query.page_size), 100)
    q = db.query(Image).filter(Image.owner_id == current_user.id)
    if query.tag_id is not None:
        q = q.join(ImageTag, ImageTag.image_id == Image.id).filter(ImageTag.tag_id == query.tag_id)
    total = q.count()
    items = (
        q.options(selectinload(Image.tags))
        .order_by(Image.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "items": [ImagePublic.model_validate(i) for i in items],
    }


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image = db.query(Image).filter(Image.id == image_id, Image.owner_id == current_user.id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    delete_file(image.storage_path)
    db.delete(image)
    db.commit()
