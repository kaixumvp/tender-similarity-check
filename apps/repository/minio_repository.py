# app/core/minio_client.py
from minio import Minio
from minio.error import S3Error
from config import minio_config  # 假设你有配置模块

# 创建全局唯一的 MinIO 客户端（单例）
minio_client = Minio(
    endpoint=minio_config["host"],
    access_key=minio_config["access_key"],
    secret_key=minio_config["secret_key"],
    secure=False
)

def ensure_bucket_exists(bucket_name: str):
    """确保 Bucket 存在"""
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
    except S3Error as e:
        if "BucketAlreadyOwnedByYou" not in str(e):
            raise