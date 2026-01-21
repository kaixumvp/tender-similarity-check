from typing import List
from fastapi import APIRouter, Depends, UploadFile
from minio import Minio

from apps.repository.dependencies import get_minio_client
from apps.web.vo.similarity_respose import BaseResponse


router = APIRouter(prefix="/api/tender", tags=["标书"])

@router.post("/tender_check", response_model=BaseResponse)
def tender_check(file_ids: List[str]):
    """
    标书检测
    """
    pass