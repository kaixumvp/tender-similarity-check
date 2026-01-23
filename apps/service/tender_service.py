from io import BytesIO
from itertools import combinations
from typing import List

from fastapi import BackgroundTasks

from apps import AppContext
from apps.document_parser.base import HDocument
from apps.document_parser.pdf_parser import PdfParser
from apps.repository.entity.file_entity import FileRecordEntity
from apps.repository.entity.tender_entity import BidPlagiarismCheckTask
from apps.service.milnus_service import create_tender_vector_milvus_db
from apps.web.dto.tender_task import TenderTaskDto

app_context = AppContext()

def create_plagiarism_check_tasks(tender_task_dto: TenderTaskDto) -> List:
    """
    创建标书查重任务
    :param file_ids: 标书文件集合，标书文件id
    """

    # 根据文件id获取文件管理表中获取对象的信息数据，如文件的类型，文件路径file_path
    with app_context.db_session_factory() as session:
        session.add(BidPlagiarismCheckTask())
        file_record_list = session.query(FileRecordEntity).filter_by(FileRecordEntity.id.in_(tender_task_dto.file_ids)).all()
    return list(combinations(file_record_list, 2))


def start_plagiarism_check(tasks, background_tasks: BackgroundTasks):
    """
    开始异步执行查重检测
    :param tasks: 检测任务
    :param background_tasks: 后台任务对象，用于异步执行任务，fastApi自带
    """
    for task in tasks:
        # 遍历每个任务，并开始执行检测任务
        background_tasks.add_task(plagiarism_check_tasks(task))


def plagiarism_check_tasks(task):
    """
    任务执行
    :param task: 任务数据，并非任务本身，实体数据
    """
    file_record_a, file_record_b = task
    CheckTask(file_record_a, file_record_b).execute()


def bid_plagiarism_check(tender_task_dto: TenderTaskDto, background_tasks: BackgroundTasks):
    """
    标书查重
    :param file_ids: 标书文件集合，标书id
    :param task_name: 任务名称
    :param background_tasks: 后台任务对象，用于异步执行任务，fastApi自带
    :return:
    """
    # 创建标书任务
    tasks: List = create_plagiarism_check_tasks(tender_task_dto)
    # 异步启动标书查重
    start_plagiarism_check(tasks, background_tasks)

class CheckTask:
    """
    检查标书任务
    """

    def __init__(self, file_record_a: FileRecordEntity, file_record_b: FileRecordEntity):
        self.file_record_a = file_record_a
        self.file_record_b = file_record_b

    def execute(self):
        """
        执行比对任务
        """
        self._file_record_handle(self.file_record_a)
        self._file_record_handle(self.file_record_b)

    def _file_record_handle(self, file_record: FileRecordEntity):
        """
        文件处理功能
        :param file_record: 文件管理数据表计入
        """
        file_path = file_record.file_path
        business_id = file_record.business_id
        minio_client = app_context.minio_client
        with minio_client.get_object(business_id, file_path) as response:
            file_data = response.read()  # 自动 close + release_conn
        pdf_stream = BytesIO(file_data)
        if file_record.mime_type == "pdf":
            pdf_parser = PdfParser()
            file_document = pdf_parser.parse(stream=pdf_stream, file_id=file_record.id)
            documents: list[HDocument] = pdf_parser.overlapping_splitting(file_document, 5000, 100)
            milvus_vector_db = create_tender_vector_milvus_db(1024)
            milvus_vector_db.insert_data(documents)
        else:
            pass
