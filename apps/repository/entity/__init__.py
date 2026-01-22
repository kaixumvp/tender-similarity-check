from sqlalchemy import Column, DateTime, func, Integer
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    create_by = Column(Integer, nullable=True)
    status = Column(Integer, default=1)  # 状态：1-使用证, -1-已废弃