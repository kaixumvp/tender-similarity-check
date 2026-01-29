import asyncio
from io import BytesIO
from itertools import combinations
from typing import List

from fastapi import BackgroundTasks

from apps import AppContext
from apps.document_parser.base import HDocument
from apps.document_parser.pdf_parser import PdfParser
from apps.repository.entity.file_entity import FileRecordEntity
from apps.repository.entity.tender_entity import BidPlagiarismCheckTask, SubBidPlagiarismCheckTask
from apps.service.milnus_service import create_tender_vector_milvus_db
from apps.web.dto.tender_task import TenderTaskDto

app_context = AppContext()

def create_plagiarism_check_tasks(tender_task_dto: TenderTaskDto) -> List:
    """
    创建标书查重任务
    :param tender_task_dto: 标书文件集合，标书文件id
    """

    # 根据文件id获取文件管理表中获取对象的信息数据，如文件的类型，文件路径file_path
    with app_context.db_session_factory() as session:
        bid_task = BidPlagiarismCheckTask(
            task_name=tender_task_dto.task_name,
            check_type=tender_task_dto.task_type
        )
        session.add(bid_task)
        file_record_list:List[FileRecordEntity] = session.query(FileRecordEntity).filter(FileRecordEntity.id.in_(tender_task_dto.file_ids)).all()
        session.commit()
        session.begin()
        sub_task_array = []
        for file_record_a, file_record_b in combinations(file_record_list, 2):
            # id = Column(Integer, primary_key=True, index=True)
            # process_status = Column(String(20), default="processing")  # 进度状态：completed, processing, parsed, failed
            # bid_plagiarism_check_task_id = Column(Integer, nullable=False)
            # left_file_id = Column(Integer, nullable=False)
            # right_file_id = Column(Integer, nullable=False)
            # similarity_number = Column(Integer, nullable=False)
            sub_task = SubBidPlagiarismCheckTask(
                bid_plagiarism_check_task_id = bid_task.id,
                left_file_id = file_record_a.id,
                right_file_id = file_record_b.id
            )
            sub_task_array.append(sub_task)
        session.add_all(sub_task_array)
    task_array = []
    for sub_task in sub_task_array:
        task_dict = {
            "id": sub_task.id,
            "bid_plagiarism_check_task_id": sub_task.bid_plagiarism_check_task_id,
            "left_file_id": sub_task.left_file_id,
            "right_file_id": sub_task.right_file_id,
        }
        task_array.append(task_dict)
    return task_array


async def start_plagiarism_check(tasks:List, background_tasks: BackgroundTasks):
    """
    开始异步执行查重检测
    :param tasks: 检测任务
    :param background_tasks: 后台任务对象，用于异步执行任务，fastApi自带
    """
    for task in tasks:
        # 遍历每个任务，并开始执行检测任务

        #background_tasks.add_task(asyncio.to_thread, plagiarism_check_tasks(task))
        #plagiarism_check_tasks(task)
        background_tasks.add_task(plagiarism_check_tasks(task))


def plagiarism_check_tasks(task:SubBidPlagiarismCheckTask):
    """
    任务执行
    :param task: 任务数据，并非任务本身，实体数据
    """
    CheckTask(task).execute()


async def bid_plagiarism_check(tender_task_dto: TenderTaskDto, background_tasks: BackgroundTasks):
    """
    标书查重
    :param tender_task_dto: 标书任务上传数据
    :param background_tasks: 后台任务对象，用于异步执行任务，fastApi自带
    :return:
    """
    # 创建标书任务
    tasks: List = create_plagiarism_check_tasks(tender_task_dto)
    # 异步启动标书查重
    await start_plagiarism_check(tasks, background_tasks)

async def service_tender_check_list():
    with app_context.db_session_factory() as session:
        tasks = session.query(BidPlagiarismCheckTask).all()
    task_array = []
    for task in tasks:
        task_dict = {
            "task_name": task.task_name,
            "check_type": task.check_type,
            "file_name_list": task.file_name_list,
            "process_status": task.process_status,
        }
        task_array.append(task_dict)
    return task_array

async def service_tender_check_list_sub(task_id):
    with app_context.db_session_factory() as session:
        tasks = session.query(SubBidPlagiarismCheckTask).filter_by(SubBidPlagiarismCheckTask.bid_plagiarism_check_task_id == task_id).all()
    task_array = []
    for task in tasks:
        with app_context.db_session_factory() as session:
            left_file = session.query(FileRecordEntity).get(task.left_file_id)
            right_file = session.query(FileRecordEntity).get(task.right_file_id)
        task_dict = {
            "similarity_number": task.similarity_number,
            "left_file_name": left_file.file_name,
            "right_file_name": right_file.file_name,
            "process_status": task.process_status,
        }
        task_array.append(task_dict)
    return task_array

class CheckTask:
    """
    检查标书任务
    """

    def __init__(self, task):
        self.task = task

    def execute(self):
        """
        执行比对任务
        """
        left_file_id = self.task["left_file_id"]
        right_file_id = self.task["right_file_id"]
        with app_context.db_session_factory() as session:
            file_record_a = session.query(FileRecordEntity).get(left_file_id)
            file_record_b = session.query(FileRecordEntity).get(right_file_id)
            self._file_record_handle(file_record_a)
            self._file_record_handle(file_record_b)
            sub_task:SubBidPlagiarismCheckTask = session.query(SubBidPlagiarismCheckTask).get(self.task["id"])
            sub_task.process_status = "completed"
            session.add(sub_task)

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
            # 处理其他格式的
            pass
