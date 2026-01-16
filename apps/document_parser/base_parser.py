from abc import ABC, abstractmethod
import re

from apps.document_parser.base import HDocument, HFiledocument


class BaseParser(ABC):
   
    @abstractmethod
    def parse(self, file, file_id) -> HFiledocument:
        """
        文档解析器功能，将文件中的内容转化为可读字符串
        
        :param file: 需要解析的文件
        :return: 返回解析的文本内容，字符串类型
        :rtype: str
        """ 
        pass
    
    def clean_text(self, text: str) -> str:
        """
        清除掉干扰的内容

        :param text: 需要清除前的文本内容
        :return: 返回清除后的文本内容
        :rtype: str
        """
        return text.strip().replace("\n", " ").replace("\r", "")
    
    def topic_splitting(text: str) -> list[str]:
        """
        主题切分，将文档按照主题章节进行切分
        
        :param text: 文档内容
        :type text: str
        :return: 切分后的片段数据，数组类型
        :rtype: list[str]
        """
        pass

    def _get_stop_words(self):
        """加载中文停用词（无实际语义的词，如：的、了、在）"""
        stop_words = [
            '的', '了', '在', '是', '我', '你', '他', '她', '它', '我们', '你们', '他们',
            '和', '或', '但', '如果', '就', '都', '也', '还', '只', '个', '本', '该',
            '及', '与', '等', '对', '对于', '关于', '根据', '按照', '为了', '由于',
            '之', '其', '所', '以', '而', '并', '又', '且', '即', '则', '因', '故'
        ]
        return stop_words
    
    def preprocess_text(self, text):
        """文本预处理：去特殊符号、去多余空格、统一格式"""
        # 去除特殊符号（保留中文、英文、数字）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
        # 去除多余空格（多个空格合并为一个，首尾空格去除）
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    
    def langchain_text_splitting(file_path: str, chunk_size: int = 2000, overlap: int = 100) -> list[str]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import PyPDFLoader

        # Use the PyPDFLoader to load and parse the PDF
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        print(f'Loaded {len(pages)} pages from the PDF')

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 2000,
            chunk_overlap  = 100,
            length_function = len,
            add_start_index = True,
        )

        documents = text_splitter.split_documents(pages)
        return [document.page_content for document in documents]

    
    def overlapping_splitting(self, filedocument: HFiledocument, chunk_size: int = 2000, overlap: int = 100) -> list[HDocument]:
        """
        重叠切片逻辑，将长文本内容切割成不同的小段，选择重叠切片，真强语义的连贯性
        
        :param text: 需要切片的文本内容
        :type text: str
        :param chunk_size: 切片大小
        :type chunk_size: int
        :param overlap: 重叠部分的长度
        :type overlap: int
        :return: 返回字符串数组，为切好的多片段数据
        :rtype: list[str]
        """
        documents:list[HDocument] = []
        for pageducument in filedocument:
            text = pageducument.page_content
            punctuations: str = r'，  。！？；…'
            text = re.sub(r'\s+', ' ', text).strip()
            text_length = len(text)
            current_start = 0
            if text_length <= chunk_size:
                document = HDocument(pageducument.file_id, pageducument.page, current_start, text[current_start:])
                documents.append(document)
                continue
            # 编译正则：匹配任意结束标点（用于快速查找）
            punctuation_pattern = re.compile(f'[{punctuations}]')
            chunks = []
            
            while current_start < text_length:
                # 1. 计算目标结束位置（当前起始 + 目标长度）
                target_end = current_start + chunk_size
                
                # 2. 处理边界：如果目标结束超过文本长度，直接取剩余部分
                if target_end >= text_length:
                    chunks.append(text[current_start:])
                    document = HDocument(pageducument.file_id, pageducument.page, current_start, text[current_start:])
                    documents.append(document)
                    break
                
                # 3. 检查目标结束位置是否是标点
                if text[target_end] in punctuations:
                    split_end = target_end + 1  # 包含标点
                else:
                    # 4. 向后找最近的标点（最多搜索200字符，避免无标点极端情况）
                    match = punctuation_pattern.search(text, target_end, target_end + 200)
                    if match:
                        split_end = match.end()  # 匹配到的标点结束位置
                    else:
                        # 兜底：找不到标点则按目标长度切分
                        split_end = target_end
                
                # 5. 截取当前块并加入列表
                current_chunk = text[current_start:split_end]
                chunks.append(current_chunk)
                document = HDocument(pageducument.file_id, pageducument.page, current_start, current_chunk)
                documents.append(document)
                # 6. 更新下一块的起始位置（当前结束 - 重叠长度）
                current_start = split_end - overlap
                
                # 防护：避免起始位置回退过多（比如重叠长度大于当前块）
                if current_start < 0:
                    current_start = 0
                # 防护：避免死循环（相邻起始位置无变化）
                if current_start >= text_length or (len(chunks) >= 2 and current_start == chunks[-2]):
                    break
            
        return documents

