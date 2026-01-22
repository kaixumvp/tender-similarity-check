from sqlalchemy import Column, Integer, String

from apps.repository.entity import Base


class BidPlagiarismCheckTask(Base):
    """
    标书查重任务
    """
    __tablename__ = "bid_plagiarism_check_task"

    id = Column(Integer, primary_key=True, index=True)


class SubBidPlagiarismCheckTask(Base):
    """
    标书查重任务
    """
    __tablename__ = "sub_bid_plagiarism_check_task"

    id = Column(Integer, primary_key=True, index=True)
    process_status = Column(String(20), default="processing")  # 进度状态：completed, processing, parsed, failed