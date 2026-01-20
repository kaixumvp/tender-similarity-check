from typing import List
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from sentence_transformers import SentenceTransformer

from apps.algorithms.embedding import OllamaQwenEmbeddingVectorizer, QwenEmbeddingVectorizer
from apps.document_parser.base import HDocument

# ------------------- 1. 初始化配置 -------------------
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
        host = config["host"]
        port = config["port"]
        connections.connect(
            alias="default",
            host=host,
            port=port
        )
        self.fields = fields
        self.collection_name = collection_name
        self.collection = None
        self.get_collection()
    
    def get_collection(self) -> Collection:
        if utility.has_collection(self.collection_name):
            if self.collection:
                return self.collection
            self.collection = Collection(name=self.collection_name)
            return self.collection
        else:
            self.collection = self._create_collection()
            return self.collection

    def _create_collection(self):
        """创建Milvus集合（表）"""
        
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
        self.get_collection().create_index(field_name=field_name, index_params=index_params)

    def insert_data(self, documents: list[HDocument]):
        """插入文本数据（存储）"""
        # 文本转向量
        #vectorizer = QwenEmbeddingVectorizer()
        vectorizer = OllamaQwenEmbeddingVectorizer()
         # 构造插入数据
        data = []
        vec_list = []
        file_ids = []
        pages = []
        start_indexes = []
        texts = []
        for document in documents:
            if document.text.strip():
                print(f"文件页数：{str(document.page)}，开始位置：{document.start_index}", f"文本内容：{document.text}")
                vectors = vectorizer.encode(document.text)
                print(f"向量数据: {vectors}")
                vec_list.append(vectors)
                file_ids.append(document.file_id)
                pages.append(document.page)
                start_indexes.append(document.start_index)
                texts.append(document.text)
                # data.append({
                #     vec_list,  # vector字段
                #     document.file_id,  # file_id字段
                #     document.page, #page字段
                #     document.start_index, #开始位置
                #     document.text #文本内容
                # })
       
        # 插入Milvus
        insert_result = self.get_collection().insert([file_ids, pages, start_indexes, texts, vec_list])
        self.collection.flush()  # 刷盘，确保数据持久化
        print(f"插入成功，插入ID：{insert_result.primary_keys}")
        print(f"集合总数据量：{self.collection.num_entities}")
        self.collection.load()
        return insert_result
    
    def query_data(self, expr:str, output_fields:list[str] = None):
        self.collection.load()
        return self.collection.query(expr=expr, output_fields=output_fields)

    def search_similar(self, expr, query_vector):
        """相似性查询"""
        # 1. 查询文本转向量
       # query_vector = text_to_vector([query_text])
        # 2. 加载集合到内存（查询前必须加载）
        self.collection.load()
        # 3. 定义查询参数
        search_params = {
            "metric_type":"COSINE",
            
            "params": {"nprobe": 128, "similarity":0.85}  # 查询参数，nprobe越大越准但速度越慢
        }
        # 4. 执行查询
        results = self.collection.search(
            data=query_vector,          # 查询向量
            expr=expr,
            anns_field="vector",   # 向量字段名
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