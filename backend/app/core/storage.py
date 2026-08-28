import io
import os
import uuid
from datetime import datetime

from PIL import Image as PILImage

from app.core.config import get_settings


def _settings():
    """Always read the live settings singleton so runtime config changes
    (e.g. via the settings API) take effect without a server restart."""
    return get_settings()


def is_allowed_extension(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in _settings().allowed_extensions


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


def _s3_configured(s) -> bool:
    return bool(
        s.s3_endpoint_url and s.s3_access_key and s.s3_secret_key and s.s3_bucket
    )


def _qiniu_configured(s) -> bool:
    return bool(
        s.qiniu_access_key and s.qiniu_secret_key and s.qiniu_bucket and s.qiniu_domain
    )


def _oss_configured(s) -> bool:
    return bool(
        s.oss_endpoint
        and s.oss_bucket_name
        and s.oss_access_key_id
        and s.oss_access_key_secret
    )


def _cos_configured(s) -> bool:
    return bool(s.cos_region and s.cos_bucket and s.cos_secret_id and s.cos_secret_key)


def _save_local(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """保存文件到本地磁盘, 返回文件元信息字典。"""
    s = _settings()
    key = _make_key(original_name, username)
    abs_path = os.path.join(s.upload_dir, key)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    url = f"{s.public_base_url.rstrip('/')}/{key}"
    width, height = _read_image_size(file_bytes)

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "drive": "local",
        "url": url,
        "width": width,
        "height": height,
    }


def _save_qiniu(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """上传文件到七牛云对象存储, 返回文件元信息字典。"""
    from qiniu import Auth, put_data

    s = _settings()
    if not _qiniu_configured(s):
        raise ValueError("七牛云存储未正确配置 (请检查 QINIU_* 环境变量)")

    key = _make_key(original_name, username)
    auth = Auth(s.qiniu_access_key, s.qiniu_secret_key)
    token = auth.upload_token(s.qiniu_bucket, key, 3600)
    ret, info = put_data(token, key, file_bytes)
    if info is None or info.status_code != 200 or ret.get("key") != key:
        err = info.error if info else "未知错误"
        raise ValueError(f"上传到七牛云失败: {err}")

    url = f"{s.qiniu_domain.rstrip('/')}/{key}"
    width, height = _read_image_size(file_bytes)

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "drive": "qiniu",
        "url": url,
        "width": width,
        "height": height,
    }


def _save_s3(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """上传文件到 S3 兼容对象存储, 返回文件元信息字典。"""
    import boto3
    import mimetypes
    from botocore.exceptions import ClientError, BotoCoreError

    s = _settings()
    if not _s3_configured(s):
        raise ValueError("S3 存储未正确配置 (请检查 S3_* 环境变量)")

    key = _make_key(original_name, username)
    content_type, _ = mimetypes.guess_type(original_name)
    if not content_type:
        content_type = "application/octet-stream"

    client = boto3.client(
        "s3",
        endpoint_url=s.s3_endpoint_url or None,
        region_name=s.s3_region_name or None,
        aws_access_key_id=s.s3_access_key,
        aws_secret_access_key=s.s3_secret_key,
    )
    try:
        client.put_object(
            Bucket=s.s3_bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
    except (ClientError, BotoCoreError) as e:
        raise ValueError(f"上传到 S3 失败: {e}")

    if s.s3_public_domain:
        url = f"{s.s3_public_domain.rstrip('/')}/{key}"
    else:
        endpoint = s.s3_endpoint_url.rstrip("/")
        url = f"{endpoint}/{s.s3_bucket}/{key}"
    width, height = _read_image_size(file_bytes)

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "drive": "s3",
        "url": url,
        "width": width,
        "height": height,
    }


def _save_oss(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """上传文件到阿里云 OSS, 返回文件元信息字典。"""
    import mimetypes
    from oss2 import Auth as OssAuth
    from oss2.exceptions import OssError

    s = _settings()
    if not _oss_configured(s):
        raise ValueError("阿里云 OSS 未正确配置 (请检查 OSS_* 环境变量)")

    key = _make_key(original_name, username)
    content_type, _ = mimetypes.guess_type(original_name)
    if not content_type:
        content_type = "application/octet-stream"

    import oss2

    auth = OssAuth(s.oss_access_key_id, s.oss_access_key_secret)
    bucket = oss2.Bucket(auth, s.oss_endpoint, s.oss_bucket_name)
    try:
        bucket.put_object(key, file_bytes, headers={"Content-Type": content_type})
    except OssError as e:
        raise ValueError(f"上传到阿里云 OSS 失败: {e}")

    if s.oss_public_url:
        url = f"{s.oss_public_url.rstrip('/')}/{key}"
    else:
        url = f"{s.oss_endpoint.rstrip('/')}/{s.oss_bucket_name}/{key}"
    width, height = _read_image_size(file_bytes)

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "drive": "oss",
        "url": url,
        "width": width,
        "height": height,
    }


def _save_cos(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """上传文件到腾讯云 COS, 返回文件元信息字典。"""
    import mimetypes
    from qcloud_cos import CosConfig, CosS3Client
    from qcloud_cos.cos_exception import CosServiceError

    s = _settings()
    if not _cos_configured(s):
        raise ValueError("腾讯云 COS 未正确配置 (请检查 COS_* 环境变量)")

    key = _make_key(original_name, username)
    content_type, _ = mimetypes.guess_type(original_name)
    if not content_type:
        content_type = "application/octet-stream"

    config = CosConfig(
        Region=s.cos_region,
        SecretId=s.cos_secret_id,
        SecretKey=s.cos_secret_key,
    )
    client = CosS3Client(config)
    try:
        client.put_object(
            Bucket=s.cos_bucket,
            Body=file_bytes,
            Key=key,
            ContentType=content_type,
        )
    except CosServiceError as e:
        raise ValueError(f"上传到腾讯云 COS 失败: {e}")

    if s.cos_public_url:
        url = f"{s.cos_public_url.rstrip('/')}/{key}"
    else:
        url = f"https://{s.cos_bucket}.cos.{s.cos_region}.myqcloud.com/{key}"
    width, height = _read_image_size(file_bytes)

    return {
        "filename": key,
        "original_name": original_name,
        "storage_path": key,
        "rel_path": key,
        "drive": "cos",
        "url": url,
        "width": width,
        "height": height,
    }


def save_upload(file_bytes: bytes, original_name: str, username: str = "") -> dict:
    """根据 drive 配置选择存储驱动, 返回文件元信息字典。"""
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in _settings().allowed_extensions:
        raise ValueError("不支持的文件格式")

    drive = _settings().drive
    if drive == "qiniu":
        return _save_qiniu(file_bytes, original_name, username)
    if drive == "s3":
        return _save_s3(file_bytes, original_name, username)
    if drive == "oss":
        return _save_oss(file_bytes, original_name, username)
    if drive == "cos":
        return _save_cos(file_bytes, original_name, username)
    return _save_local(file_bytes, original_name, username)


def _delete_local(key: str) -> None:
    """从本地磁盘删除文件, 仅允许删除 upload_dir 内的文件。"""
    if not key:
        return
    s = _settings()
    abs_path = os.path.join(s.upload_dir, key)
    real_upload = os.path.realpath(s.upload_dir)
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

    s = _settings()
    if not key or not _qiniu_configured(s):
        return
    auth = Auth(s.qiniu_access_key, s.qiniu_secret_key)
    bucket = BucketManager(auth)
    bucket.delete(s.qiniu_bucket, key)


def _delete_s3(key: str) -> None:
    """从 S3 兼容对象存储删除指定对象 key。"""
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError

    s = _settings()
    if not key or not _s3_configured(s):
        return
    client = boto3.client(
        "s3",
        endpoint_url=s.s3_endpoint_url or None,
        region_name=s.s3_region_name or None,
        aws_access_key_id=s.s3_access_key,
        aws_secret_access_key=s.s3_secret_key,
    )
    try:
        client.delete_object(Bucket=s.s3_bucket, Key=key)
    except (ClientError, BotoCoreError):
        pass


def _delete_oss(key: str) -> None:
    """从阿里云 OSS 删除指定对象 key。"""
    import oss2

    s = _settings()
    if not key or not _oss_configured(s):
        return
    auth = oss2.Auth(s.oss_access_key_id, s.oss_access_key_secret)
    bucket = oss2.Bucket(auth, s.oss_endpoint, s.oss_bucket_name)
    try:
        bucket.delete_object(key)
    except oss2.exceptions.OssError:
        pass


def _delete_cos(key: str) -> None:
    """从腾讯云 COS 删除指定对象 key。"""
    from qcloud_cos import CosConfig, CosS3Client

    s = _settings()
    if not key or not _cos_configured(s):
        return
    config = CosConfig(
        Region=s.cos_region,
        SecretId=s.cos_secret_id,
        SecretKey=s.cos_secret_key,
    )
    client = CosS3Client(config)
    try:
        client.delete_object(Bucket=s.cos_bucket, Key=key)
    except Exception:
        pass


def delete_file(key: str, drive: str = None) -> None:
    """根据图片记录使用的存储驱动删除对应存储中的对象。

    drive 为空 (历史数据或调用方未传入) 时回退到当前全局 drive 配置。
    """
    drive = drive or _settings().drive
    if drive == "qiniu":
        _delete_qiniu(key)
    elif drive == "s3":
        _delete_s3(key)
    elif drive == "oss":
        _delete_oss(key)
    elif drive == "cos":
        _delete_cos(key)
    else:
        _delete_local(key)
