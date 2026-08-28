"""Pydantic schemas for the settings module."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# User info
# ---------------------------------------------------------------------------
class EmailUpdate(BaseModel):
    email: EmailStr


class PasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)


# ---------------------------------------------------------------------------
# Storage config
# ---------------------------------------------------------------------------
SUPPORTED_DRIVERS = {"local", "s3", "qiniu", "oss", "cos"}


class StorageConfig(BaseModel):
    """Full storage configuration as exposed to the settings UI.

    Field names mirror ``core.config.Settings`` so the response can be
    consumed directly by the frontend form and persisted back to ``.env``.
    """

    drive: str = Field(..., description="存储驱动: local | s3 | qiniu | oss | cos")

    # local
    upload_dir: str | None = None
    public_base_url: str | None = None

    # qiniu
    qiniu_access_key: str | None = None
    qiniu_secret_key: str | None = None
    qiniu_bucket: str | None = None
    qiniu_domain: str | None = None

    # s3
    s3_endpoint_url: str | None = None
    s3_region_name: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str | None = None
    s3_public_domain: str | None = None

    # ali oss
    oss_endpoint: str | None = None
    oss_bucket_name: str | None = None
    oss_access_key_id: str | None = None
    oss_access_key_secret: str | None = None
    oss_public_url: str | None = None

    # tencent cos
    cos_region: str | None = None
    cos_bucket: str | None = None
    cos_secret_id: str | None = None
    cos_secret_key: str | None = None
    cos_public_url: str | None = None

    def to_env_dict(self) -> dict[str, Any]:
        """Return a flat mapping of env var name -> value for persistence."""

        mapping = {
            "DRIVE": self.drive,
            "UPLOAD_DIR": self.upload_dir,
            "PUBLIC_BASE_URL": self.public_base_url,
            "QINIU_ACCESS_KEY": self.qiniu_access_key,
            "QINIU_SECRET_KEY": self.qiniu_secret_key,
            "QINIU_BUCKET": self.qiniu_bucket,
            "QINIU_DOMAIN": self.qiniu_domain,
            "S3_ENDPOINT_URL": self.s3_endpoint_url,
            "S3_REGION_NAME": self.s3_region_name,
            "S3_ACCESS_KEY": self.s3_access_key,
            "S3_SECRET_KEY": self.s3_secret_key,
            "S3_BUCKET": self.s3_bucket,
            "S3_PUBLIC_DOMAIN": self.s3_public_domain,
            "OSS_ENDPOINT": self.oss_endpoint,
            "OSS_BUCKET_NAME": self.oss_bucket_name,
            "OSS_ACCESS_KEY_ID": self.oss_access_key_id,
            "OSS_ACCESS_KEY_SECRET": self.oss_access_key_secret,
            "OSS_PUBLIC_URL": self.oss_public_url,
            "COS_REGION": self.cos_region,
            "COS_BUCKET": self.cos_bucket,
            "COS_SECRET_ID": self.cos_secret_id,
            "COS_SECRET_KEY": self.cos_secret_key,
            "COS_PUBLIC_URL": self.cos_public_url,
        }
        return {k: v for k, v in mapping.items() if v is not None}


class StorageConfigUpdate(BaseModel):
    """Partial update payload; only provided fields are changed."""

    drive: str | None = None
    upload_dir: str | None = None
    public_base_url: str | None = None
    qiniu_access_key: str | None = None
    qiniu_secret_key: str | None = None
    qiniu_bucket: str | None = None
    qiniu_domain: str | None = None
    s3_endpoint_url: str | None = None
    s3_region_name: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str | None = None
    s3_public_domain: str | None = None
    oss_endpoint: str | None = None
    oss_bucket_name: str | None = None
    oss_access_key_id: str | None = None
    oss_access_key_secret: str | None = None
    oss_public_url: str | None = None
    cos_region: str | None = None
    cos_bucket: str | None = None
    cos_secret_id: str | None = None
    cos_secret_key: str | None = None
    cos_public_url: str | None = None
