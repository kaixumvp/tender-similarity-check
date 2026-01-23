"""
标书查重vo, 用于前端显示结果
"""
from typing import Any, Optional

from pydantic import BaseModel


class BaseResponse(BaseModel):  # 修正拼写：Response
    code: int = 1
    message: str = "success"
    data: Optional[Any] = None

    @classmethod
    def success(cls, data: Any = None, message: str = "success"):
        return cls(code=1, data=data, message=message)

    @classmethod
    def error(cls, code: int = -1, message: str = "error", data: Any = None):
        return cls(code=code, data=data, message=message)

    
class ContrastVO:
    def __init__(self, document, contrast_document_array:list):
        self.document = document
        self.contrast_document_array = contrast_document_array