from sqlalchemy import Column, Integer, String, Float

from apps.repository.entity import Base


class BidPlagiarismCheckTask(Base):
    """
    标书查重任务
    """
    __tablename__ = "bid_plagiarism_check_task"

    id = Column(Integer, primary_key=True, index=True)
    check_type = Column(Integer, nullable=False)
    task_name = Column(String(100), nullable=False)
    file_name_list = Column(String(255),default="", nullable=False)
    process_status = Column(String(20), default="processing")  # 进度状态：completed, processing, parsed, failed



class SubBidPlagiarismCheckTask(Base):
    """
    标书查重子任务
    """
    __tablename__ = "sub_bid_plagiarism_check_task"

    id = Column(Integer, primary_key=True, index=True)
    process_status = Column(String(20), default="processing")  # 进度状态：completed, processing, parsed, failed
    bid_plagiarism_check_task_id = Column(Integer, nullable=False)
    left_file_id = Column(Integer, nullable=False)
    right_file_id = Column(Integer, nullable=False)
    similarity_number = Column(Integer, default=0, nullable=False)

class DocumentSimilarityRecord(Base):
    """
        文档相似度记录
    """
    __tablename__ = "document_similarity_record"
    id = Column(Integer, primary_key=True, index=True)
    bid_plagiarism_check_task_id = Column(Integer, nullable=False)
    sub_bid_plagiarism_check_task_id = Column(Integer, nullable=False)
    left_file_id = Column(Integer, nullable=False)
    left_file_page = Column(Integer, nullable=False)
    left_file_page_start_index = Column(Integer, nullable=False)
    left_file_page_chunk = Column(String(255), nullable=False)
    right_file_id = Column(Integer, nullable=False)
    right_file_page = Column(Integer, nullable=False)
    right_file_page_start_index = Column(Integer, nullable=False)
    right_file_page_chunk = Column(String(255), nullable=False)
    similarity = Column(Float, nullable=False)