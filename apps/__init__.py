import logging
from fastapi import FastAPI
from minio import Minio, S3Error
#from openai import AsyncOpenAI
from pymilvus import connections
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class AppContext:

    _instance = None  # ← 类变量，存储唯一实例


    def __new__(cls, app: FastAPI = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.app = app
        return cls._instance

    @staticmethod
    def start(app):
        app_context = AppContext(app).init_context()
        from apps.web.api import file_api, tender_api
        app_context.app.include_router(file_api.file_router)
        app_context.app.include_router(tender_api.tender_router)

    def init_context(self):
        from config import data_config, milvus_config, minio_config, mysql_config
        logger = logging.getLogger("uvicorn")
        self.logger = logger
        if self.app:
            self.app.state.app_context = self
            self.app.state.app_config = data_config
            self.app.state.milvus_config = milvus_config
            self.app.state.minio_config = minio_config
            self.app.state.mysql_config = mysql_config
        self.app_config = data_config
        self.milvus_config = milvus_config
        self.minio_config = minio_config
        self.mysql_config = mysql_config
        self._init_mysql()
        self._init_milvus()
        self._init_minio()
        #self._init_models()
        return self

    def _init_mysql(self):
        """
        初始化mysql数据库连接
        """
        mysql_conf = self.mysql_config
        # 创建引擎
        engine = create_engine(
            mysql_conf["database_url"],
            pool_pre_ping=True,  # 自动重连
            pool_recycle=mysql_conf["pool_recycle"],  # 5分钟回收连接（防 MySQL 8h 超时）
            echo=True  # 生产设为 False
        )
        self.engine = engine
        # 创建会话工厂
        db_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        if self.app:
            self.app.state.db_engine = engine
            self.app.state.db_session_factory = db_session_factory
        self.db_engine = engine
        self.db_session_factory = db_session_factory
        # 自动建表（仅开发环境建议使用！）
        # 基类
        from apps.repository.entity import Base
        from apps.repository.entity.file_entity import FileRecordEntity
        from apps.repository.entity.tender_entity import BidPlagiarismCheckTask, SubBidPlagiarismCheckTask, DocumentSimilarityRecord
        Base.metadata.create_all(bind=engine)

    def _init_milvus(self):
        host = self.milvus_config["host"]
        port = self.milvus_config["port"]
        db_name = self.milvus_config["db_name"]
        connections.connect(
            alias="default",
            host=host,
            port=port,
            db_name=db_name,
        )
        if self.app:
            self.app.state.milvus_connections = connections
        self.milvus_connections = connections


    def _init_minio(self):
        """
        初始化minio
        """
        minio_client = Minio(
            endpoint=self.minio_config["host"],
            access_key=self.minio_config["access_key"],
            secret_key=self.minio_config["secret_key"],
            secure=False
        )
        if self.app:
            self.app.state.minio_client = minio_client
        self.minio_client = minio_client
        try:
            if not minio_client.bucket_exists(self.minio_config["bucket_name"]):
                minio_client.make_bucket(self.minio_config["bucket_name"])
        except S3Error as e:
            if "BucketAlreadyOwnedByYou" not in str(e):
                raise

    # def _init_models(self):
    #     model_config = self.app_config["model"]
    #     models_dict = {}
    #     if self.app_config["model"]:
    #         for key, value in model_config.items():
    #             client = AsyncOpenAI(
    #                 base_url=value["hostname"],  # 指向 vLLM 启动的 OpenAI 兼容服务
    #                 api_key=value["api_key"]  # 本地部署可忽略，填任意值即可
    #             )
    #             models_dict[key] = client
    #     self.models = models_dict


