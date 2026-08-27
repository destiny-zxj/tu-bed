from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "tu-bed"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    database_url: str = "mysql+pymysql://root:root@127.0.0.1:3306/tubed"

    secret_key: str = "change-me-to-a-long-random-secret-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
    public_base_url: str = "/uploads"

    # 存储驱动: local (本地磁盘) / qiniu (七牛云对象存储) / s3 (S3 兼容对象存储), 默认 local
    drive: str = "local"

    # 七牛云对象存储配置
    qiniu_access_key: str = ""
    qiniu_secret_key: str = ""
    qiniu_bucket: str = ""
    # 七牛外链域名, 例如 https://cdn.example.com (无需结尾斜杠)
    qiniu_domain: str = ""

    # S3 兼容对象存储配置
    s3_endpoint_url: str = ""  # S3 服务地址, 例如 https://s3.amazonaws.com 或自建 MinIO 地址
    s3_region_name: str = ""  # 区域, 例如 ap-east-1 (AWS 可为空, 自建可随意填)
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = ""
    # 访问对象的外链域名, 例如 https://cdn.example.com (无需结尾斜杠)。
    # 留空则使用 endpoint_url + bucket 的形式拼接。
    s3_public_domain: str = ""

    admin_username: str = "admin"
    admin_password: str = "admin123456"
    admin_email: str = "admin@example.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
