from typing import List

from fastapi import APIRouter, Depends, UploadFile, Form
from minio import Minio

from apps.repository.dependencies import get_minio_client
from apps.service.file_service import upload_file
from apps.web.vo.similarity_respose import BaseResponse

router = APIRouter(prefix="/api/file", tags=["文件"])


@router.post("/upload-multiple", response_model=BaseResponse)
def tender_file_upload(
        files: List[UploadFile],
        business_id: str = Form(...)
    ):
    """
    标书文件上传接口
    :param files: 接收上传文件
    :param business_id: 业务id根据实际的功能指定，标书指定tender
    """
    # for file in files:
    #     minio.put_object(
    #         bucket_name=AppContext().minio_config["bucket_name"],
    #         object_name=f"files/{file.filename}",
    #         data = file.file,          # ✅ 直接传入 file.file
    #         length = file.size or -1,  # 注意：file.size 可能为 None
    #         content_type = file.content_type
    #     )
    file_ids = upload_file(files, business_id)
    return BaseResponse.success(message="文件上传成功", data=file_ids)