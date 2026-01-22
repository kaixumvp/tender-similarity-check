from typing import List

from fastapi import APIRouter, BackgroundTasks

from apps.service.tender_service import bid_plagiarism_check
from apps.web.vo.similarity_respose import BaseResponse

tender_router = APIRouter(prefix="/api/tender", tags=["标书"])

@tender_router.post("/tender_check", response_model=BaseResponse)
def tender_check(file_ids: List[str], background_tasks: BackgroundTasks):
    """
    标书检测
    """
    bid_plagiarism_check(file_ids, background_tasks)
    return BaseResponse.success()