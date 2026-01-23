from typing import List

from fastapi import APIRouter, BackgroundTasks

from apps.service.tender_service import bid_plagiarism_check
from apps.web.dto.tender_task import TenderTaskDto
from apps.web.vo.similarity_respose import BaseResponse

tender_router = APIRouter(prefix="/api/tender", tags=["标书"])

@tender_router.post("/tender_check", response_model=BaseResponse)
def tender_check(tender_task_dto: TenderTaskDto, background_tasks: BackgroundTasks):
    """
    标书检测
    """
    bid_plagiarism_check(tender_task_dto, background_tasks)
    return BaseResponse.success()