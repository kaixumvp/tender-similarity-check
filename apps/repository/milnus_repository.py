from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from sentence_transformers import SentenceTransformer

# ------------------- 1. 初始化配置 -------------------
# Milvus 连接配置
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "tender_vector_collection"  # 标书向量集合名
VECTOR_DIM = 384  # Sentence-BERT生成的向量维度
TOP_K = 3  # 查询返回Top3相似结果

# ------------------- 2. 工具函数：文本转向量 -------------------
def text_to_vector(texts):
    """将文本列表转为向量列表"""
    model = SentenceTransformer('all-MiniLM-L6-v2')  # 轻量级文本向量模型
    vectors = model.encode(texts, convert_to_numpy=True).tolist()
    return vectors

# ------------------- 3. Milvus 核心操作 -------------------
class MilvusVectorDB:
    def __init__(self, config, fields, collection_name):
        # 连接Milvus服务
        connections.connect(
            alias="default",
            host=MILVUS_HOST,
            port=MILVUS_PORT
        )
        self.fields = fields
        self.collection_name = collection_name
        #self.collection = self._create_collection()
    
    def get_collection(self, collection_name):
        if utility.has_collection(collection_name):
            return Collection(name=collection_name)
        else:
            return self._create_collection()

    def _create_collection(self):
        """创建Milvus集合（表）"""
        # 定义字段：主键ID + 文本内容 + 向量字段
        # fields = [
        #     FieldSchema(
        #         name="id",
        #         dtype=DataType.INT64,
        #         is_primary=True,
        #         auto_id=True  # 自动生成ID
        #     ),
        #     FieldSchema(
        #         name="text_content",
        #         dtype=DataType.VARCHAR,
        #         max_length=4000  # 文本最大长度
        #     ),
        #     FieldSchema(
        #         name="text_vector",
        #         dtype=DataType.FLOAT_VECTOR,
        #         dim=VECTOR_DIM  # 向量维度需与模型输出一致
        #     )
        # ]
        # 定义集合Schema
        schema = CollectionSchema(self.fields, description="标书文本向量集合")
        collection = Collection(name=COLLECTION_NAME, schema=schema)
        return collection
    
    def create_index(self, field_name, index_params):
        """
        创建索引
        # 创建向量索引（必须创建索引才能高效查询）
        index_params = {
            "index_type": "IVF_FLAT",  # 基础索引，适合小数据量
            "metric_type": "COSINE",   # 相似度度量：余弦相似度（文本检索首选）
            "params": {"nlist": 128}   # 索引参数，nlist越大查询越准但速度越慢
        }
        """
        self.get_collection(self.collection_name).create_index(field_name=field_name, index_params=index_params)

    def insert_data(self, texts):
        """插入文本数据（存储）"""
        # 文本转向量
        vectors = text_to_vector(texts)
        # 构造插入数据
        data = [
            texts,  # text_content字段
            vectors  # text_vector字段
        ]
        # 插入Milvus
        insert_result = self.collection.insert(data)
        self.collection.flush()  # 刷盘，确保数据持久化
        print(f"插入成功，插入ID：{insert_result.primary_keys}")
        print(f"集合总数据量：{self.collection.num_entities}")
        return insert_result

    def search_similar(self, query_text):
        """相似性查询"""
        # 1. 查询文本转向量
        query_vector = text_to_vector([query_text])
        # 2. 加载集合到内存（查询前必须加载）
        self.collection.load()
        # 3. 定义查询参数
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}  # 查询参数，nprobe越大越准但速度越慢
        }
        # 4. 执行查询
        results = self.collection.search(
            data=query_vector,          # 查询向量
            anns_field="text_vector",   # 向量字段名
            param=search_params,
            limit=TOP_K,                # 返回TopK
            output_fields=["text_content"]  # 返回的字段（除向量外）
        )
        # 5. 解析结果
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "id": hit.id,
                    "similarity": hit.score,  # 相似度得分（余弦相似度：0~1，越高越相似）
                    "text": hit.entity.get("text_content")
                })
        return search_results

# ------------------- 4. 测试：存储+查询 -------------------
if __name__ == "__main__":
    # 初始化Milvus客户端
    milvus_db = MilvusVectorDB()

    # 示例标书文本（模拟你之前处理的招标文件内容）
    tender_texts = [
        "南沙区2026-2027年市政道路绿化养护项目，养护范围包含10条主干道，预算500万元",
        "2026年南沙区绿化养护项目要求：每月修剪绿植2次，雨季增加巡检频次，质保期1年",
        "市政道路绿化养护招标文件：投标人需具备城市园林绿化一级资质，近3年有同类项目业绩",
        "南沙区绿化养护项目评标标准：技术分60分，商务分40分，价格分采用低价优先法"
    ]

    # 步骤1：存储（插入）标书文本向量
    milvus_db.insert_data(tender_texts)

    # 步骤2：查询相似文本
    query_text = "南沙区绿化养护项目 预算 资质要求"
    similar_results = milvus_db.search_similar(query_text)

    # 打印查询结果
    print("\n=== 相似文本查询结果 ===")
    for i, res in enumerate(similar_results, 1):
        print(f"\n排名{i}（相似度：{res['similarity']:.4f}）：")
        print(f"文本：{res['text']}")