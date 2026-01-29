from typing import List

from pydantic import BaseModel


class TenderTaskDto(BaseModel):
    task_name: str
    task_type: int
    file_ids: List[int]