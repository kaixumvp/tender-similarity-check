from langchain_core.language_models import LLM
from openai import OpenAI, AsyncOpenAI, api_key
from mineru_vl_utils import MinerUClient
from PIL import Image
import base64
import io
llm = LLM(
    model="OpenDataLab/MinerU2.5-2509-1.2B"
)

client = MinerUClient(
    backend="vllm-engine",
    vllm_llm=llm,
    api_key=""
)

# ===================== 核心配置 =====================
# 本地/服务器 vLLM 部署的 OpenAI 兼容服务地址（默认端口 8000）
BASE_URL = "https://ms-ens-27d9631a-6fa5.api-inference.modelscope.cn/v1"
# 模型名称（与 vLLM 部署时的模型名一致）
MODEL_NAME = "OpenDataLab/MinerU2.5-2509-1.2B"
# 可选：若服务配置了 API-KEY 则填写，本地部署一般无需设置
API_KEY = "ms-9c27e58a-3c49-426a-9d39-2631c44c0073"  # 无则填任意字符串（如 "no-key"）

# ===================== 初始化 OpenAI 客户端 =====================
client = AsyncOpenAI(
    base_url=BASE_URL,  # 指向 vLLM 启动的 OpenAI 兼容服务
    api_key=API_KEY  # 本地部署可忽略，填任意值即可
)


# ===================== 工具函数：图片转 Base64 编码 =====================
def image_to_base64(image: Image.Image) -> str:
    """将 PIL.Image 转换为 OpenAI 接口支持的 Base64 字符串"""
    buffer = io.BytesIO()
    # 保存图片为 PNG 格式（兼容所有常见图片格式）
    image.save(buffer, format="PNG")
    # 编码为 Base64 并转换为字符串
    base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    # 返回 OpenAI 要求的「格式前缀+Base64 串」
    return f"data:image/png;base64,{base64_str}"


# ===================== 核心调用：图片内容提取（替代 two_step_extract） =====================
if __name__ == "__main__":
    # 1. 加载图片（与原代码路径一致）
    image_path = "D:/pyproject/tender-similarity-check/document/屏幕截图 2025-07-29 222309.png"
    image = Image.open(image_path)

    # 2. 图片转 Base64 编码
    image_b64 = image_to_base64(image)

    # 3. 调用 OpenAI 兼容接口（chat.completions）提取图片内容
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_b64}}
                ]
            }
        ],
        # 推理参数（适配 MinerU 1.2B，可根据需求调整）
        max_tokens=2048,  # 最大生成长度
        temperature=0.3,  # 低温度保证结果稳定性（结构化提取推荐 0.2-0.5）
        top_p=0.9,
        stream=False  # 非流式返回，直接获取完整结果
    )

    # 4. 解析提取结果（与原 extracted_blocks 格式对齐）
    extracted_blocks = response.choices[0].message.content.strip()
    # 打印结果
    print("图片内容提取结果：")
    print(extracted_blocks)