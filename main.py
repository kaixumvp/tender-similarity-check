# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apps.repository.minio_repository import ensure_bucket_exists
from apps.web.api import file_api

import uvicorn

from config import minio_config



@asynccontextmanager
async def start_app(app: FastAPI):
    ensure_bucket_exists(minio_config["bucket_name"])
    yield

app = FastAPI(
    title="标书检测应用",
    version="1.0.0",
    lifespan=start_app
)

# 注册子路由（自动带全局前缀）
app.include_router(file_api.router)

if __name__ == "__main__":
    """启动 FastAPI 应用"""
    uvicorn.run(
        "main:app",      # 模块:实例
        host="0.0.0.0",
        port=8000,
        reload=True,         # 开发时开启自动重载
        log_level="info"
    )

