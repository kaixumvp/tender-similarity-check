from fastapi import Depends
from minio import Minio

# 依赖函数：返回 MinIO 客户端
def get_minio_client() -> Minio:
    from apps.repository.minio_repository import minio_client
    return minio_client