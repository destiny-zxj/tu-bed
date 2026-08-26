import io
import os
import uuid
from datetime import datetime

from PIL import Image as PILImage
from qiniu import Auth, BucketManager, put_data

from app.core.config import settings


def is_allowed_extension(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in settings.allowed_extensions


def _configured() -> bool:
    return bool(
        settings.qiniu_access_key
        and settings.qiniu_secret_key
        and settings.qiniu_bucket
        and settings.qiniu_domain
    )


def _make_key(original_name: str) -> str:
    ext = os.path.splitext(original_name)[1].lower()
    date_sub = datetime.now().strftime("%Y/%m/%d")
    return f"images/{date_sub}/{uuid.uuid4().hex}{ext}"


def save_upload(file_bytes: bytes, original_name: str) -> dict:
    """上传文件到七牛云对象存储, 返回文件元信息字典。

    storage_path / filename 字段现表示七牛对象 key, url 为七牛外链。
    """
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in settings.allowed_extensions:
        raise ValueError("不支持的文件格式")
    if not _configured():
        raise ValueError("七牛云存储未正确配置 (请检查 QINIU_* 环境变量)")

    key = _make_key(original_name)
    auth = Auth(settings.qiniu_access_key, settings.qiniu_secret_key)
    token = auth.upload_token(settings.qiniu_bucket, key, 3600)
    ret, info = put_data(token, key, file_bytes)
    if info is None or info.status_code != 200 or ret.get("key") != key:
        err = info.error if info else "未知错误"
        raise ValueError(f"上传到七牛云失败: {err}")

    url = f"{settings.qiniu_domain.rstrip('/')}/{key}"

    width = height = None
    try:
        with PILImage.open(io.BytesIO(file_bytes)) as img:
            width, height = img.size
    except Exception:
        pass

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "url": url,
        "width": width,
        "height": height,
    }


def delete_file(key: str) -> None:
    """从七牛云删除指定对象 key。"""
    if not key or not _configured():
        return
    auth = Auth(settings.qiniu_access_key, settings.qiniu_secret_key)
    bucket = BucketManager(auth)
    # 忽略 "资源不存在" (612) 等错误, 仅做尽力删除
    bucket.delete(settings.qiniu_bucket, key)
