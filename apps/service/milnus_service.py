from pymilvus import DataType, FieldSchema
from apps.repository.milnus_repository import MilvusVectorDB
from config import milvus_config


def create_tender_vector_milnus_db(vector_dim) -> MilvusVectorDB:
    # 定义字段：主键ID + 文件唯一 + 标识符 + 文件页 + 片段在文档页中的位置 + 片段的文本内容 + 向量字段
    fields = [
        FieldSchema(
            name="id",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=True  # 自动生成ID
        ),
        FieldSchema(
            name="file_id",
            dtype=DataType.VARCHAR,
            max_length=50
        ),
        FieldSchema(
            name="page",
            dtype=DataType.INT8
        ),
        FieldSchema(
            name="start_index",
            dtype=DataType.INT32
        ),
        FieldSchema(
            name="text_content",
            dtype=DataType.VARCHAR,
            max_length=5500  # 文本最大长度
        ),
        FieldSchema(
            name="vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=vector_dim  # 向量维度需与模型输出一致
        )
    ]
    return MilvusVectorDB(milvus_config, fields, "tender_vector_collection")