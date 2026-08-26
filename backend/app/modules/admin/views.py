from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, require_admin
from app.core.storage import delete_file
from app.modules.admin.items import UserCreateItem, UserUpdateItem
from app.modules.admin.models import DashboardStats
from app.modules.apikeys.models import ApiKey
from app.modules.auth.models import User, UserPublic
from app.modules.images.models import Image, ImagePublic

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ---------- 用户管理 ----------
@router.get("/users", response_model=list[UserPublic])
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


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
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Image)
    total = q.count()
    items = (
        q.order_by(Image.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    )
    return {"total": total, "items": items}  # type: ignore[arg-type]


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_image(image_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    delete_file(image.storage_path)
    db.delete(image)
    db.commit()


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
