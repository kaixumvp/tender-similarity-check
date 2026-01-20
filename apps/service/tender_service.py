from typing import List

from fastapi import BackgroundTasks
from itertools import combinations

from apps.repository.dependencies import get_minio_client
from config import minio_config


def create_plagiarism_check_tasks(file_ids) -> List:
    """
    创建标书查重任务
    :param file_ids: 标书文件集合，标书文件id
    """
    minio_client = get_minio_client()
    for file_id in file_ids:
        minio_client.get_object(
            bucket_name=minio_config["bucket_name"],
            object_name=f"files/{file_id}" )

    for file_id_1, file_id_2 in combinations(file_ids, 2):
        pass
    return []


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

    return None

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