from typing import List
from fastapi import APIRouter, Depends, UploadFile
from minio import Minio

from apps.repository.dependencies import get_minio_client
from apps.web.vo.similarity_respose import BaseResponse
from config import minio_config


router = APIRouter(prefix="/api/file", tags=["文件"])


@router.post("/upload-multiple", response_model=BaseResponse)
def tender_file_upload(
        files: List[UploadFile], 
        minio:Minio = Depends(get_minio_client)
    ):
    for file in files:
        minio.put_object(bucket_name=minio_config["bucket_name"], 
            object_name=f"files/{file.filename}",
            data = file.file,          # ✅ 直接传入 file.file
            length = file.size or -1,  # 注意：file.size 可能为 None
            content_type = file.content_type
        )
    return BaseResponse.success(message="文件上传成功")