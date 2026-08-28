from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, require_admin
from app.core.storage import delete_file
from app.modules.admin.items import ImageBatchDeleteItem, UserCreateItem, UserListQueryItem, UserUpdateItem
from app.modules.admin.models import DashboardStats
from app.modules.apikeys.models import ApiKey
from app.modules.auth.models import User, UserPublic
from app.modules.images.models import Image, ImagePublic

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ---------- 用户管理 ----------
@router.get("/users", response_model=dict)
def list_users(
    query: UserListQueryItem = Depends(),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    page = max(1, query.page)
    page_size = min(max(1, query.page_size), 100)
    q = db.query(User)
    total = q.count()
    items = (
        q.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "items": [UserPublic.model_validate(i) for i in items],
    }


@router.post("/users", response_model=UserPublic)
def create_user(item: UserCreateItem, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == item.username).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user = User(
        username=item.username,
        email=item.email,
        hashed_password=get_password_hash(item.password),
        is_admin=item.is_admin,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    item: UserUpdateItem,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    data = item.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        user.hashed_password = get_password_hash(data.pop("password"))
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    db.delete(user)
    db.commit()


# ---------- 图片管理 ----------
@router.get("/images", response_model=dict)
def list_all_images(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="按文件名关键字模糊搜索"),
    owner_id: Optional[int] = Query(None, description="按所属用户筛选"),
    start_date: Optional[str] = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Image)
    if keyword:
        like = f"%{keyword.strip()}%"
        q = q.filter(Image.original_name.ilike(like))
    if owner_id is not None:
        q = q.filter(Image.owner_id == owner_id)
    if start_date:
        q = q.filter(Image.created_at >= start_date)
    if end_date:
        q = q.filter(Image.created_at < f"{end_date} 23:59:59")
    total = q.count()
    items = (
        q.options(selectinload(Image.tags), selectinload(Image.owner))
        .order_by(Image.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "items": [
            ImagePublic.model_validate(i).model_copy(update={"owner_username": i.owner.username if i.owner else None})
            for i in items
        ],
    }


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_image(image_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    delete_file(image.storage_path, image.storage_drive)
    db.delete(image)
    db.commit()


@router.post("/images/batch-delete", status_code=status.HTTP_200_OK, response_model=dict)
def batch_delete_images(
    item: ImageBatchDeleteItem,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not item.image_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未提供图片 ID")
    # 去重并查询存在的记录
    unique_ids = list(dict.fromkeys(item.image_ids))
    images = db.query(Image).filter(Image.id.in_(unique_ids)).all()
    found_ids = {img.id for img in images}
    # 删除物理文件与数据库记录
    for img in images:
        delete_file(img.storage_path, img.storage_drive)
        db.delete(img)
    db.commit()
    deleted = len(images)
    skipped = len(unique_ids) - deleted
    return {
        "deleted": deleted,
        "skipped": skipped,
        "missing_ids": [i for i in unique_ids if i not in found_ids],
    }


# ---------- 统计 ----------
@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_images = db.query(Image).count()
    total_bytes = sum(row[0] for row in db.query(Image.size).all())
    return DashboardStats(
        total_users=total_users,
        total_images=total_images,
        total_storage_bytes=total_bytes,
    )
