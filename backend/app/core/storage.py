import io
import os
import uuid
from datetime import datetime

from PIL import Image as PILImage

from app.core.config import settings


def is_allowed_extension(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in settings.allowed_extensions


def _make_key(original_name: str, username: str = "") -> str:
    ext = os.path.splitext(original_name)[1].lower()
    date_sub = datetime.now().strftime("%Y%m/%d")
    safe_user = (username or "anonymous").strip().replace("/", "_") or "anonymous"
    return f"app_tubed/{safe_user}/{date_sub}/{uuid.uuid4().hex}{ext}"


def _read_image_size(file_bytes: bytes) -> tuple:
    width = height = None
    try:
        with PILImage.open(io.BytesIO(file_bytes)) as img:
            width, height = img.size
    except Exception:
        pass
    return width, height


def _s3_configured() -> bool:
    return bool(
        settings.s3_endpoint_url
        and settings.s3_access_key
        and settings.s3_secret_key
        and settings.s3_bucket
    )


def _qiniu_configured() -> bool:
    return bool(
        settings.qiniu_access_key
        and settings.qiniu_secret_key
        and settings.qiniu_bucket
        and settings.qiniu_domain
    )


def _save_local(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """保存文件到本地磁盘, 返回文件元信息字典。

    storage_path / filename 字段为相对 upload_dir 的路径, url 为本地访问地址。
    """
    key = _make_key(original_name, username)
    abs_path = os.path.join(settings.upload_dir, key)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    url = f"{settings.public_base_url.rstrip('/')}/{key}"
    width, height = _read_image_size(file_bytes)

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "url": url,
        "width": width,
        "height": height,
    }


def _save_qiniu(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """上传文件到七牛云对象存储, 返回文件元信息字典。

    storage_path / filename 字段为七牛对象 key, url 为七牛外链。
    """
    from qiniu import Auth, put_data

    if not _qiniu_configured():
        raise ValueError("七牛云存储未正确配置 (请检查 QINIU_* 环境变量)")

    key = _make_key(original_name, username)
    auth = Auth(settings.qiniu_access_key, settings.qiniu_secret_key)
    token = auth.upload_token(settings.qiniu_bucket, key, 3600)
    ret, info = put_data(token, key, file_bytes)
    if info is None or info.status_code != 200 or ret.get("key") != key:
        err = info.error if info else "未知错误"
        raise ValueError(f"上传到七牛云失败: {err}")

    url = f"{settings.qiniu_domain.rstrip('/')}/{key}"
    width, height = _read_image_size(file_bytes)

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "url": url,
        "width": width,
        "height": height,
    }


def _save_s3(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """上传文件到 S3 兼容对象存储, 返回文件元信息字典。

    storage_path / filename 字段为 S3 对象 key, url 为对象外链。
    """
    import boto3
    import mimetypes
    from botocore.exceptions import ClientError, BotoCoreError

    if not _s3_configured():
        raise ValueError("S3 存储未正确配置 (请检查 S3_* 环境变量)")

    key = _make_key(original_name, username)
    content_type, _ = mimetypes.guess_type(original_name)
    if not content_type:
        content_type = "application/octet-stream"

    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url or None,
        region_name=settings.s3_region_name or None,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )
    try:
        client.put_object(
            Bucket=settings.s3_bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
    except (ClientError, BotoCoreError) as e:
        raise ValueError(f"上传到 S3 失败: {e}")

    if settings.s3_public_domain:
        url = f"{settings.s3_public_domain.rstrip('/')}/{key}"
    else:
        endpoint = settings.s3_endpoint_url.rstrip("/")
        url = f"{endpoint}/{settings.s3_bucket}/{key}"
    width, height = _read_image_size(file_bytes)

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "url": url,
        "width": width,
        "height": height,
    }


def save_upload(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """根据 DRIVE 配置选择本地 / 七牛云 / S3 存储, 返回文件元信息字典。"""
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in settings.allowed_extensions:
        raise ValueError("不支持的文件格式")

    drive = settings.drive
    if drive == "qiniu":
        return _save_qiniu(file_bytes, original_name, username)
    if drive == "s3":
        return _save_s3(file_bytes, original_name, username)
    return _save_local(file_bytes, original_name, username)


def _delete_local(key: str) -> None:
    """从本地磁盘删除文件, 仅允许删除 upload_dir 内的文件。"""
    if not key:
        return
    abs_path = os.path.join(settings.upload_dir, key)
    real_upload = os.path.realpath(settings.upload_dir)
    real_target = os.path.realpath(abs_path)
    if not real_target.startswith(real_upload + os.sep):
        return
    try:
        os.remove(abs_path)
    except OSError:
        pass


def _delete_qiniu(key: str) -> None:
    """从七牛云删除指定对象 key。"""
    from qiniu import Auth, BucketManager

    if not key or not _qiniu_configured():
        return
    auth = Auth(settings.qiniu_access_key, settings.qiniu_secret_key)
    bucket = BucketManager(auth)
    # 忽略 "资源不存在" (612) 等错误, 仅做尽力删除
    bucket.delete(settings.qiniu_bucket, key)


def _delete_s3(key: str) -> None:
    """从 S3 兼容对象存储删除指定对象 key。"""
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError

    if not key or not _s3_configured():
        return
    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url or None,
        region_name=settings.s3_region_name or None,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )
    try:
        client.delete_object(Bucket=settings.s3_bucket, Key=key)
    except (ClientError, BotoCoreError):
        # 仅做尽力删除, 忽略错误
        pass


def delete_file(key: str) -> None:
    """根据 DRIVE 配置删除本地文件 / 七牛云对象 / S3 对象。"""
    drive = settings.drive
    if drive == "qiniu":
        _delete_qiniu(key)
    elif drive == "s3":
        _delete_s3(key)
    else:
        _delete_local(key)