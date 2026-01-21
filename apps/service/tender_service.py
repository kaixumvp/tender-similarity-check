from itertools import combinations
from typing import List

from fastapi import BackgroundTasks

from apps import AppContext
from apps.repository.entity.file_entity import FileRecordEntity

app_context = AppContext()

def create_plagiarism_check_tasks(file_ids) -> List:
    """
    创建标书查重任务
    :param file_ids: 标书文件集合，标书文件id
    """
    # 根据文件id获取文件管理表中获取对象的信息数据，如文件的类型，文件路径file_path
    with app_context.db_session_factory() as session:
         file_record_list = session.query(FileRecordEntity).filter_by(FileRecordEntity.id.in_(file_ids)).all()
    return list(combinations(file_record_list, 2))


def start_plagiarism_check(tasks, background_tasks: BackgroundTasks):
    """
    开始异步执行查重检测
    :param tasks: 检测任务
    :param background_tasks: 后台任务对象，用于异步执行任务，fastapi自带
    """
    for task in tasks:
        # 遍历每个任务，并开始执行检测任务
        background_tasks.add_task(plagiarism_check_tasks(task))
    pass


def plagiarism_check_tasks(task):
    """
    任务执行
    :param task: 任务数据，并非任务本身，实体数据
    """
    file_record_a, file_record_b = task
    minio_client = app_context.minio_client
    # 查询文件内容


def bid_plagiarism_check(file_ids: List[str], background_tasks: BackgroundTasks):
    """
    标书查重
    :param file_ids: 标书文件集合，标书id
    :param background_tasks: 后台任务对象，用于异步执行任务，fastapi自带
    :return:
    """
    # 创建标书任务
    tasks: List = create_plagiarism_check_tasks(file_ids)
    # 异步启动标书查重
    start_plagiarism_check(tasks, background_tasks)