"""Settings endpoints.

Provides user-level account management (email / password) and admin-level
system configuration (storage driver + per-driver settings).

Storage configuration changes are persisted to the ``.env`` file AND applied
to the live ``Settings`` singleton so they take effect immediately without a
server restart.
"""
from __future__ import annotations

from pathlib import Path

from dotenv import set_key
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings, settings
from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, verify_password
from app.modules.auth.models import User
from app.modules.settings.items import (
    EmailUpdate,
    PasswordUpdate,
    StorageConfig,
    StorageConfigUpdate,
    SUPPORTED_DRIVERS,
)

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _env_path() -> Path:
    """Locate the ``.env`` file pydantic-settings actually reads.

    ``core.config.Settings`` declares ``env_file=".env"`` (relative to the
    current working directory). Honour that, but fall back to the repo's
    ``backend/.env`` so the file is still found when the process is launched
    from a different directory (e.g. inside a container).
    """
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        return cwd_env
    return Path(__file__).resolve().parents[3] / ".env"


# ---------------------------------------------------------------------------
# User info
# ---------------------------------------------------------------------------
@router.put("/user/email", summary="修改当前用户邮箱")
async def update_email(
    payload: EmailUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    existing = await db.scalar(
        select(User).where(User.email == payload.email, User.id != user.id)
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被其他用户使用")

    user.email = payload.email
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.put("/user/password", summary="修改当前用户密码")
async def update_password(
    payload: PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确")

    user.hashed_password = get_password_hash(payload.new_password)
    db.add(user)
    await db.commit()
    return {"message": "密码修改成功"}


# ---------------------------------------------------------------------------
# Storage config (admin)
# ---------------------------------------------------------------------------
def _storage_as_dict(s) -> dict:
    return {
        "drive": s.drive,
        "upload_dir": s.upload_dir,
        "public_base_url": s.public_base_url,
        "qiniu_access_key": s.qiniu_access_key,
        "qiniu_secret_key": s.qiniu_secret_key,
        "qiniu_bucket": s.qiniu_bucket,
        "qiniu_domain": s.qiniu_domain,
        "s3_endpoint_url": s.s3_endpoint_url,
        "s3_region_name": s.s3_region_name,
        "s3_access_key": s.s3_access_key,
        "s3_secret_key": s.s3_secret_key,
        "s3_bucket": s.s3_bucket,
        "s3_public_domain": s.s3_public_domain,
        "oss_endpoint": s.oss_endpoint,
        "oss_bucket_name": s.oss_bucket_name,
        "oss_access_key_id": s.oss_access_key_id,
        "oss_access_key_secret": s.oss_access_key_secret,
        "oss_public_url": s.oss_public_url,
        "cos_region": s.cos_region,
        "cos_bucket": s.cos_bucket,
        "cos_secret_id": s.cos_secret_id,
        "cos_secret_key": s.cos_secret_key,
        "cos_public_url": s.cos_public_url,
    }


@router.get("/storage", summary="获取存储配置", response_model=StorageConfig)
async def get_storage_config(
    _: User = Depends(get_current_user),
) -> StorageConfig:
    return StorageConfig(**_storage_as_dict(settings))


@router.put("/storage", summary="更新存储配置（实时生效，并持久化到 .env）")
async def update_storage_config(
    payload: StorageConfigUpdate,
    _: User = Depends(get_current_user),
) -> StorageConfig:
    s = settings
    data = payload.model_dump(exclude_unset=True)

    if "drive" in data and data["drive"] not in SUPPORTED_DRIVERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的存储驱动")

    # 1) apply to the live settings singleton (no restart needed)
    for key, value in data.items():
        if value is None:
            continue
        setattr(s, key, value)

    # 2) persist to .env so the change survives restarts
    merged = {**_storage_as_dict(s), **data}
    env_updates = StorageConfig(**merged).to_env_dict()
    for env_key, env_value in env_updates.items():
        set_key(str(_env_path()), env_key, str(env_value))

    # 3) clear the cached settings so a subsequent get_settings() re-reads
    #    the (now updated) .env, keeping the singleton consistent on reload.
    get_settings.cache_clear()

    return StorageConfig(**_storage_as_dict(settings))
