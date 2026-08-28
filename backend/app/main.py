import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.database import engine
from app.modules import registry  # noqa: F401 触发所有模型注册到 metadata
from app.modules.admin.views import router as admin_router
from app.modules.apikeys.views import router as apikeys_router
from app.modules.auth.views import router as auth_router
from app.modules.images.views import router as images_router
from app.modules.settings.views import router as settings_router
from app.modules.tags.views import image_tags_router, router as tags_router

app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS: 允许前端跨域访问 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(images_router)
app.include_router(tags_router)
app.include_router(image_tags_router)
app.include_router(apikeys_router)
app.include_router(admin_router)
app.include_router(settings_router)

# 本地存储时, 将上传目录挂载为静态文件服务, 供 /uploads 路径访问
if settings.drive == "local":
    os.makedirs(settings.upload_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(bind=engine)
    _ensure_admin()


def _ensure_admin():
    from sqlmodel import Session

    from app.core.security import get_password_hash
    from app.modules.auth.models import User

    with Session(engine) as db:
        admin = db.query(User).filter(User.username == settings.admin_username).first()
        if not admin:
            admin = User(
                username=settings.admin_username,
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                is_admin=True,
                is_active=True,
            )
            db.add(admin)
            db.commit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=settings.debug)
