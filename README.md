# TuBed · 图床系统

一个支持服务端部署的图床系统，提供简洁美观的 Web 界面（管理系统 + 客户端系统）和 REST API。

## 技术栈

- **前端**：Vue 3 + TypeScript + Vite + Naive UI + Pinia + Vue Router
- **后端**：FastAPI (Python) + SQLModel（基于 SQLAlchemy + Pydantic），依赖由 `uv` 管理（Python 3.12）
- **数据库**：MySQL
- **存储**：本地磁盘（默认）、七牛云对象存储（Qiniu）或 S3 兼容对象存储（AWS S3 / MinIO 等，按日期分目录），通过 `DRIVE` 配置切换

## 功能特性

- 用户体系：管理员 / 普通用户，JWT 登录鉴权
- 客户端系统：图片上传（点击/拖拽）、我的图片管理、API 密钥管理
- 管理后台：仪表盘统计、用户管理（增删改、启用/禁用）、全站图片管理
- REST API：支持 `Bearer Token` 与 `API Key` 两种方式上传，便于第三方集成
- 图片存储于本地磁盘（默认）、七牛云或 S3 兼容对象存储，按 `app_tubed/YYYYMM/DD/` 分目录
- 一键 Docker 部署

## 目录结构

```
tu-bed/
├── backend/                 # FastAPI 后端 (uv 管理, Python 3.12)
│   ├── pyproject.toml       # 依赖声明 (uv)
│   ├── uv.lock              # 锁定依赖版本
│   ├── .env.example         # 环境变量示例
│   ├── start.sh             # 本地开发启动脚本
│   ├── Dockerfile
│   └── app/
│       ├── main.py          # 应用入口、装配模块路由、建表、初始化管理员
│       ├── core/            # 公共基础设施
│       │   ├── config.py    # 配置（读取 .env）
│       │   ├── database.py  # 引擎与会话
│       │   ├── security.py  # 密码哈希、JWT、API Key、鉴权依赖
│       │   └── storage.py   # 存储驱动：本地磁盘 / 七牛云 / S3 兼容对象存储上传与删除
│       ├── modules/         # 业务模块 (每个含 views / models / items)
│       │   ├── registry.py  # 集中导入所有模型, 确保建表
│       │   ├── auth/        # 认证：User 模型、LoginItem、路由
│       │   ├── images/      # 图片：Image 模型、ImageListQueryItem、路由
│       │   ├── apikeys/     # API 密钥：ApiKey 模型、ApiKeyCreateItem、路由
│       │   └── admin/       # 管理后台：统计/用户/图片管理路由
│       └── uploads/         # 上传文件目录
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── api/             # axios 请求封装 (request.ts / index.ts)
│   │   ├── stores/          # Pinia 状态 (auth.ts)
│   │   ├── layouts/         # 客户端 / 管理后台布局
│   │   ├── views/           # 页面 (admin/ 与 client/ 子目录)
│   │   ├── router/          # 路由与权限守卫
│   │   └── utils/           # 工具函数 (format.ts)
│   ├── Dockerfile           # 构建 + nginx 托管
│   └── nginx.conf           # 静态托管 + /api、/uploads 反向代理
└── docker-compose.yml       # 一键编排（MySQL + 后端 + 前端）
```

## 快速开始（Docker 部署，推荐）

```bash
# 0. 配置 `.env`
cp .env.example .env
# 1. 按需修改 docker-compose.yml 中的 SECRET_KEY 和管理员账号
# 2. 默认使用本地存储（DRIVE=local），无需额外配置；如需七牛云，将 DRIVE 改为 qiniu 并补充 QINIU_* 环境变量；如需 S3，将 DRIVE 改为 s3 并补充 S3_* 环境变量（见下方配置说明）
docker compose up -d --build
```

启动后：
- 前端：`http://<服务器IP>:5173`
- 管理后台：`http://<服务器IP>:5173/admin`
- 后端 API：`http://<服务器IP>:8000`
- 默认管理员账号：`admin` / `admin123456`（请在 `.env` 中修改）

> 注意：默认使用本地存储（`DRIVE=local`），图片保存在 `UPLOAD_DIR` 目录并通过 `/uploads` 路径访问。如需切换为七牛云，将 `DRIVE` 设为 `qiniu`，并在 `docker-compose.yml` 的 `backend` 服务中配置 `QINIU_ACCESS_KEY`、`QINIU_SECRET_KEY`、`QINIU_BUCKET`、`QINIU_DOMAIN`；如需 S3 兼容存储（AWS S3 / MinIO 等），将 `DRIVE` 设为 `s3` 并配置 `S3_ENDPOINT_URL`、`S3_ACCESS_KEY`、`S3_SECRET_KEY`、`S3_BUCKET`（及可选的 `S3_REGION_NAME`、`S3_PUBLIC_DOMAIN`），否则上传接口会报"存储未正确配置"。

## 本地开发

### 后端

```bash
cd backend
uv sync                # 创建 .venv (Python 3.12) 并安装依赖
cp .env.example .env   # 修改数据库连接、存储驱动（DRIVE）等信息
# 确保本地有 MySQL，并创建数据库 tubed
uv run uvicorn app.main:app --reload   # 或 uv run python -m app.main
```

### 前端

```bash
cd frontend
npm install            # 或 yarn
npm run dev            # 默认 http://localhost:5173，代理 /api、/uploads 到 :8000
```

## API 概览

| 方法 | 路径 | 说明 | 鉴权 |
| --- | --- | --- | --- |
| GET | `/api/health` | 健康检查 | 公开 |
| POST | `/api/auth/login` | 用户名密码登录 | 公开 |
| GET | `/api/auth/me` | 获取当前用户 | Token |
| POST | `/api/images/upload` | 上传图片（支持 `api_key` 参数） | Token / Key |
| GET | `/api/images` | 我的图片列表 | Token |
| DELETE | `/api/images/{id}` | 删除我的图片 | Token |
| GET | `/api/apikeys` | 列出我的 API Key | Token |
| POST | `/api/apikeys` | 创建 API Key（明文仅返回一次） | Token |
| DELETE | `/api/apikeys/{id}` | 删除 API Key | Token |
| GET | `/api/admin/stats` | 仪表盘统计 | 管理员 |
| GET/POST/PUT/DELETE | `/api/admin/users` | 用户管理 | 管理员 |
| GET/DELETE | `/api/admin/images` | 全站图片管理 | 管理员 |

### 使用 API Key 上传示例

```bash
curl -X POST "http://<host>:8000/api/images/upload?api_key=YOUR_KEY" \
  -F "file=@/path/to/image.png"
```

返回结果中的 `url` 即为图片公开访问地址（本地存储为 `/uploads/...`，七牛云 / S3 为对应外链）。

## 配置说明（`.env`）

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | MySQL 连接串 |
| `SECRET_KEY` | JWT 签名密钥（务必修改） |
| `DRIVE` | 存储驱动：`local`（本地磁盘，默认）、`qiniu`（七牛云对象存储）或 `s3`（S3 兼容对象存储） |
| `UPLOAD_DIR` | 上传文件保存目录（本地存储时生效） |
| `MAX_UPLOAD_SIZE_MB` | 单文件最大体积 |
| `ALLOWED_EXTENSIONS` | 允许的文件扩展名 |
| `PUBLIC_BASE_URL` | 图片公开访问前缀（本地存储时生效，默认 `/uploads`） |
| `QINIU_ACCESS_KEY` | 七牛云 AccessKey（获取地址：七牛控制台） |
| `QINIU_SECRET_KEY` | 七牛云 SecretKey |
| `QINIU_BUCKET` | 七牛云空间名称 |
| `QINIU_DOMAIN` | 七牛云外链域名（无需结尾斜杠） |
| `S3_ENDPOINT_URL` | S3 服务地址（如 AWS `https://s3.amazonaws.com` 或自建 MinIO `http://127.0.0.1:9000`） |
| `S3_REGION_NAME` | S3 区域（AWS 如 `ap-east-1`，自建可留空） |
| `S3_ACCESS_KEY` | S3 AccessKey / Access Key ID |
| `S3_SECRET_KEY` | S3 SecretKey / Secret Access Key |
| `S3_BUCKET` | S3 存储桶名称 |
| `S3_PUBLIC_DOMAIN` | 对象访问外链域名（无需结尾斜杠，留空则用 `ENDPOINT_URL/BUCKET/KEY`） |
| `ADMIN_USERNAME/PASSWORD/EMAIL` | 初始管理员（首次启动自动创建） |