from pymilvus import DataType, FieldSchema

from apps import AppContext
from apps.repository.milnus_repository import MilvusVectorDB


def create_tender_vector_milvus_db(vector_dim) -> MilvusVectorDB:
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
            dtype=DataType.INT64,
            max_length=50
        ),
        FieldSchema(
            name="page",
            dtype=DataType.INT16
        ),
        FieldSchema(
            name="start_index",
            dtype=DataType.INT32
        ),
        FieldSchema(
            name="text_content",
            dtype=DataType.VARCHAR,
            max_length=8000  # 文本最大长度
        ),
        FieldSchema(
            name="vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=vector_dim  # 向量维度需与模型输出一致
        )
    ]
    index_params = {
        "index_type": "IVF_FLAT",  # 基础索引，适合小数据量
        "metric_type": "COSINE",  # 相似度度量：余弦相似度（文本检索首选）
        "params": {"nlist": 128}  # 索引参数，nlist越大查询越准但速度越慢
    }
    return MilvusVectorDB(fields, "tender_vector_collection", "vector", index_params)

