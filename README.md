# TuBed · 图床系统

一个支持服务端部署的图床系统，提供简洁美观的 Web 界面（管理系统 + 客户端系统）和 REST API。

## 技术栈

- **前端**：Vue 3 + TypeScript + Vite + Naive UI + Pinia + Vue Router
- **后端**：FastAPI (Python) + SQLModel（基于 SQLAlchemy + Pydantic），依赖由 `uv` 管理（Python 3.12）
- **数据库**：MySQL
- **存储**：支持 5 种存储驱动，通过 `DRIVE` 配置切换：
  - 本地磁盘（默认，按 `app_tubed/{用户名}/YYYYMM/DD/` 分目录）
  - 七牛云对象存储（Qiniu）
  - S3 兼容对象存储（AWS S3 / MinIO 等）
  - 阿里云 OSS
  - 腾讯云 COS

## 功能特性

- 用户体系：管理员 / 普通用户，JWT 登录鉴权
- 客户端系统：图片上传（点击/拖拽，带进度）、我的图片管理、标签管理、API 密钥管理
- 标签系统：创建 / 重命名 / 删除标签，为图片打标签，按标签筛选图片
- 账户设置：用户自助修改邮箱与密码
- 管理后台：仪表盘统计、用户管理（增删改、启用/禁用）、全站图片管理（支持批量删除、按文件名/用户/日期筛选）、在线存储配置（Web 界面切换存储驱动并实时生效，无需重启）
- REST API：支持 `Bearer Token` 与 `API Key` 两种方式上传，便于第三方集成
- 图片存储于本地磁盘（默认）、七牛云、S3 兼容对象存储、阿里云 OSS 或腾讯云 COS，按 `app_tubed/{用户名}/YYYYMM/DD/` 分目录
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
│       │   └── storage.py   # 存储驱动：本地磁盘 / 七牛云 / S3 兼容 / 阿里云 OSS / 腾讯云 COS 上传与删除
│       ├── modules/         # 业务模块 (每个含 views / models / items)
│       │   ├── registry.py  # 集中导入所有模型, 确保建表
│       │   ├── auth/        # 认证：User 模型、LoginItem、路由
│       │   ├── images/      # 图片：Image 模型、ImageListQueryItem、路由
│       │   ├── tags/        # 标签：Tag / ImageTag 模型、路由（标签增删改、图片打标签）
│       │   ├── apikeys/     # API 密钥：ApiKey 模型、ApiKeyCreateItem、路由
│       │   ├── settings/    # 设置：用户邮箱/密码修改、管理员在线存储配置（实时生效）
│       │   └── admin/       # 管理后台：统计/用户/图片管理（含批量删除）路由
│       └── uploads/         # 上传文件目录（本地存储时）
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── api/             # axios 请求封装 (request.ts / index.ts)
│   │   ├── stores/          # Pinia 状态 (auth.ts)
│   │   ├── layouts/         # 客户端 / 管理后台布局
│   │   ├── views/
│   │   │   ├── client/      # 客户端：上传 / 我的图片 / 我的标签
│   │   │   ├── admin/       # 管理后台：仪表盘 / 用户 / 图片 / API Key / 设置
│   │   │   └── LoginView.vue
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
# 2. 默认使用本地存储（DRIVE=local），无需额外配置；如需七牛云，将 DRIVE 改为 qiniu 并补充 QINIU_* 环境变量；如需 S3 兼容存储，将 DRIVE 改为 s3 并补充 S3_* 环境变量；如需阿里云 OSS，将 DRIVE 改为 oss 并补充 OSS_* 环境变量；如需腾讯云 COS，将 DRIVE 改为 cos 并补充 COS_* 环境变量（见下方配置说明）
docker compose up -d --build
```

启动后：
- 前端：`http://<服务器IP>:5173`
- 管理后台：`http://<服务器IP>:5173/admin`
- 后端 API：`http://<服务器IP>:8000`
- 默认管理员账号：`admin` / `admin123456`（请在 `.env` 中修改）

> 注意：默认使用本地存储（`DRIVE=local`），图片保存在 `UPLOAD_DIR` 目录并通过 `/uploads` 路径访问。如需切换其他存储，将 `DRIVE` 设为对应驱动（`qiniu` / `s3` / `oss` / `cos`），并在 `docker-compose.yml` 的 `backend` 服务中补充对应环境变量（各驱动变量见下方配置说明表），否则上传接口会报"存储未正确配置"。也可在部署后通过管理后台 → 设置页面在线切换，无需重启服务。

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
| GET | `/api/tags` | 我的标签列表 | Token |
| POST | `/api/tags` | 创建标签 | Token |
| PUT | `/api/tags/{id}` | 重命名标签 | Token |
| DELETE | `/api/tags/{id}` | 删除标签 | Token |
| POST | `/api/tags/{id}/images` | 为图片打 / 取消标签 | Token |
| GET | `/api/tags/{id}/images` | 按标签筛选图片 | Token |
| GET | `/api/apikeys` | 列出我的 API Key | Token |
| POST | `/api/apikeys` | 创建 API Key（明文仅返回一次） | Token |
| DELETE | `/api/apikeys/{id}` | 删除 API Key | Token |
| PUT | `/api/settings/me` | 修改当前用户邮箱 / 密码 | Token |
| GET | `/api/admin/stats` | 仪表盘统计 | 管理员 |
| GET/POST/PUT/DELETE | `/api/admin/users` | 用户管理 | 管理员 |
| GET/DELETE | `/api/admin/images` | 全站图片管理（支持批量删除、按文件名 / 用户 / 日期筛选） | 管理员 |
| GET/PUT | `/api/admin/settings/storage` | 读取 / 在线修改存储配置（实时写入 `.env` 并生效，无需重启） | 管理员 |

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
| `DRIVE` | 存储驱动：`local`（本地磁盘，默认）、`qiniu`（七牛云）、`s3`（S3 兼容）、`oss`（阿里云 OSS）或 `cos`（腾讯云 COS） |
| `UPLOAD_DIR` | 上传文件保存目录（仅 `DRIVE=local` 时生效） |
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
| `OSS_ENDPOINT` | 阿里云 OSS Endpoint（如 `https://oss-cn-hangzhou.aliyuncs.com`，仅 `DRIVE=oss` 时生效） |
| `OSS_BUCKET_NAME` | 阿里云 OSS Bucket 名称 |
| `OSS_ACCESS_KEY_ID` | 阿里云 AccessKeyId |
| `OSS_ACCESS_KEY_SECRET` | 阿里云 AccessKeySecret |
| `OSS_PUBLIC_URL` | 对象访问外链域名（无需结尾斜杠，留空则用 `ENDPOINT/BUCKET/KEY`） |
| `COS_REGION` | 腾讯云 COS 区域（如 `ap-guangzhou`，仅 `DRIVE=cos` 时生效） |
| `COS_BUCKET` | 腾讯云 COS Bucket（如 `example-1250000000`） |
| `COS_SECRET_ID` | 腾讯云 SecretId |
| `COS_SECRET_KEY` | 腾讯云 SecretKey |
| `COS_PUBLIC_URL` | 对象访问外链域名（无需结尾斜杠，留空则用 `https://BUCKET.cos.REGION.myqcloud.com/KEY`） |
| `ADMIN_USERNAME/PASSWORD/EMAIL` | 初始管理员（首次启动自动创建） |

### 在线存储配置

管理员无需手动编辑 `.env` 与重启服务，可直接在 **管理后台 → 设置** 页面切换存储驱动（local / qiniu / s3 / oss / cos）并填写对应密钥与 Bucket。提交后后端会即时校验并写入 `.env`，新配置**立即生效**，后续上传将自动使用新存储。

> 注意：在线配置仅写入并热更新运行期配置，建议保留并备份 `.env` 以保证容器重启后配置不丢失。