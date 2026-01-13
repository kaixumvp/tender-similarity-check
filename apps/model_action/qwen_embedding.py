from typing import List


def get_embedding(text: str) -> List[float]:
    """
    获取文本的向量表示。使用 Qwen3-Embedding。
    """
    from openai import OpenAI

    client = OpenAI(
        base_url='https://api-inference.modelscope.cn/v1',
        api_key='ms-9c27e58a-3c49-426a-9d39-2631c44c0073', # ModelScope Token
    )

    response = client.embeddings.create(
        model='Qwen/Qwen3-Embedding-8B', # ModelScope Model-Id, required
        input=text,
        encoding_format="float"
    )

    print(response.data[0].embedding)
    return response.data[0].embedding