#!/usr/bin/env bash
# 后端本地开发启动脚本 (使用 uv 管理虚拟环境, Python 3.12)
set -e

cd "$(dirname "$0")"

echo ">>> 使用 uv 同步依赖 (Python 3.12) ..."
uv sync

echo ">>> 启动 FastAPI 服务 ..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
