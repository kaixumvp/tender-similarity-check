import abc
from typing import List, Optional, Union

import jieba
import numpy as np


class BaseVectorizer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_vector_dim(self) -> int:
        """获取向量维度（必须实现）"""
        pass

    @abc.abstractmethod
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        生成文本向量（核心方法）
        :param texts: 单个文本字符串 或 文本列表
        :return: 向量数组（shape: [文本数, 向量维度]）
        """
        pass

    def preprocess_text(self, text: str) -> str:
        """
        通用文本预处理（可被子类重写）
        :param text: 原始文本
        :return: 预处理后的文本
        """
        # 基础清洗：去除特殊字符、多余空格
        text = text.replace("\n", "").replace("\r", "").strip()
        # 中文分词（可根据需求关闭）
        words = jieba.lcut(text)
        return " ".join(words)
    
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

class Doc2VecVectorizer(BaseVectorizer):
    """Doc2Vec向量生成器"""
    def __init__(self, model_path: Optional[str] = None, 
                 vector_size: int = 128, 
                 epochs: int = 50,
                 train_corpus: Optional[List[str]] = None):
        """
        :param model_path: 预训练Doc2Vec模型路径（优先加载）
        :param vector_size: 向量维度（训练新模型时生效）
        :param epochs: 训练轮数（训练新模型时生效）
        :param train_corpus: 训练语料（无预训练模型时需传入）
        """
        self.vector_size = vector_size
        self.epochs = epochs
        self.model = self._load_or_train_model(model_path, train_corpus)

    def _load_or_train_model(self, model_path: Optional[str], train_corpus: Optional[List[str]]) -> Doc2Vec:
        """加载预训练模型或训练新模型"""
        # 加载预训练模型
        if model_path:
            return Doc2Vec.load(model_path)
        # 训练新模型
        if not train_corpus:
            raise ValueError("无预训练模型时，必须传入train_corpus用于训练！")
        
        # 构建TaggedDocument
        tagged_docs = [
            TaggedDocument(
                words=self.preprocess_text(text).split(),
                tags=[idx]
            ) for idx, text in enumerate(train_corpus)
        ]
        
        # 训练模型
        model = Doc2Vec(
            vector_size=self.vector_size,
            window=5,
            min_count=2,
            workers=4,
            dm=1
        )
        model.build_vocab(tagged_docs)
        model.train(tagged_docs, total_examples=model.corpus_count, epochs=self.epochs)
        return model

    def get_vector_dim(self) -> int:
        return self.model.vector_size

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """生成Doc2Vec向量"""
        # 统一转为列表处理
        if isinstance(texts, str):
            texts = [texts]
        
        vectors = []
        for text in texts:
            # 预处理文本
            processed_text = self.preprocess_text(text).split()
            # 生成向量
            vec = self.model.infer_vector(processed_text, epochs=self.epochs)
            vectors.append(vec)
        
        return np.array(vectors)

class QwenEmbeddingVectorizer(BaseVectorizer):
    def __init__(self, api_key: str = "ms-9c27e58a-3c49-426a-9d39-2631c44c0073", model_name: str = "Qwen/Qwen3-Embedding-8B"):
        self.api_key = api_key
        self.model_name = model_name
        # 初始化通义千问客户端...

    def get_vector_dim(self) -> int:
        return 4096  # 通义千问向量维度

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        # 调用通义千问API生成向量...
        """
        获取文本的向量表示。使用 Qwen3-Embedding。
        """
        from openai import OpenAI

        client = OpenAI(
            base_url='https://api-inference.modelscope.cn/v1',
            api_key=self.api_key, # ModelScope Token
        )

        response = client.embeddings.create(
            model=self.model_name, # ModelScope Model-Id, required
            input=texts,
            encoding_format="float"
        )
        print(response.data[0].embedding)
        return response.data[0].embedding