from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, func

from apps.repository.entity import Base


class FileRecordEntity(Base):
    __tablename__ = "file_record"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)  # 原始文件名
    file_path = Column(String(512), nullable=False, unique=True)  # 存储路径（唯一）
    file_size = Column(BigInteger, nullable=False)  # 文件大小（字节）
    mime_type = Column(String(100), nullable=False)  # MIME 类型
    #hash = Column(String(64), nullable=False, index=True)  # SHA256 哈希（64字符）

    uploaded_by = Column(Integer, nullable=True)  # 上传人ID（可为空）
    business_id = Column(String(100), nullable=True, index=True)  # 业务ID（字符串兼容多种类型）

    #status = Column(String(20), default="uploaded")  # 状态：uploaded, processing, parsed, failed
    #error_message = Column(Text, nullable=True)  # 解析失败时的错误信息

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<FileRecord(id={self.id}, name='{self.file_name}', status='{self.status}')>"