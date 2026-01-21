# app/main.py
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from apps import AppContext

@asynccontextmanager
async def start_app(app_context: FastAPI):
    AppContext.start(app_context)
    yield

app = FastAPI(
    title="标书检测应用",
    version="1.0.0",
    lifespan=start_app
)

# 注册子路由（自动带全局前缀）

if __name__ == "__main__":
    """启动 FastAPI 应用"""
    uvicorn.run(
        "main:app",      # 模块:实例
        host="0.0.0.0",
        port=8000,
        reload=True,         # 开发时开启自动重载
        log_level="info"
    )

