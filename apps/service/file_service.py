import os
import tempfile
import zipfile
from pathlib import Path
from typing import List

from apps import AppContext
from apps.repository.entity.file_entity import FileRecordEntity

app_context = AppContext()
minio_client = app_context.minio_client

def upload_file(files, business_id)->List[int]:
    """
    上传文件
    :param files: 文件集合
    :param business_id 业务id，根据实际功能指定业务模块的标识符，目前标书使用tender
    """
    file_record_list = []
    for file in files:
        if business_id == "tender" and file.filename.endswith(".zip"):
            file_record_list.append(zip_unzip(file, business_id))

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(file.file.read())
            p = Path(file_path)
            # TODO: 上传到 MinIO / 保存到数据库 / OCR 扫描等
            minio_client.fput_object(
                bucket_name=app_context.minio_config["bucket_name"],
                object_name=f"files/{business_id}/{file.filename}",
                file_path=file_path,  # ✅ 直接传入 file.file
                content_type=file.content_type
            )
            file_record_list.append(FileRecordEntity(
                file_size=p.stat().st_size,
                mime_type=p.suffix[1:] if p.suffix else "",
                file_name=file.filename,
                file_path=f"files/{business_id}/{file.filename}",
                business_id=business_id,
            ))
    with app_context.db_session_factory() as session:
        session.add_all(file_record_list)
        session.commit()
        file_ids = [file_record.id for file_record in file_record_list]
    return file_ids


def zip_unzip(file, business_id):
    file_record_list = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, file.filename)

        # 写入临时 ZIP 文件
        with open(zip_path, "wb") as f:
            f.write(file.file.read())
        # 安全解压
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # 检查文件数量
                if len(zip_ref.namelist()) > MAX_FILES:
                    pass

                extracted_files = []
                for member in zip_ref.namelist():
                    # 跳过目录
                    if member.endswith("/"):
                        continue

                    # 安全路径检查（关键！）
                    target_path = os.path.join(tmp_dir, member)
                    if not is_safe_path(tmp_dir, target_path):
                        continue

                    # 可选：检查扩展名
                    if ALLOWED_EXTENSIONS and not any(member.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                        continue  # 跳过不允许的文件

                    # 解压文件
                    zip_ref.extract(member, tmp_dir)

                    # 👇 在这里处理解压后的文件（示例：打印路径）
                    print(f"Processing: {target_path}")
                    # TODO: 上传到 MinIO / 保存到数据库 / OCR 扫描等
                    minio_client.fput_object(
                        bucket_name=app_context.minio_config["bucket_name"],
                        object_name=f"files/{business_id}/{member}",
                        file_path=target_path,  # ✅ 直接传入 file.file
                        content_type=file.content_type
                    )
                    p = Path(target_path)
                    file_record_list.append(FileRecordEntity(
                        file_size = p.stat().st_size,
                        mime_type = p.suffix[1:] if p.suffix else "",
                        file_name = p.name,
                        file_path=f"files/{business_id}/{member}",
                        business_id=business_id,
                    ))

        except zipfile.BadZipFile:
            pass
    return file_record_list


# 允许的文件扩展名（可选）
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILES = 100  # 防止 zip 炸弹
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def is_safe_path(basedir: str, path: str) -> bool:
    """防止路径遍历攻击（Zip Slip 漏洞）"""
    return os.path.realpath(path).startswith(basedir)

