from abc import ABC, abstractmethod
import re


class BaseParser(ABC):

    @abstractmethod
    def parse(file) -> str:
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

    
    def overlapping_splitting(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
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
        chunks = []
        sentences = re.split(r'([。！？\.!?])', text)
        # 将句号等标点符号重新附着到前面的句子上
        sentences = [sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '') for i in range(0, len(sentences), 2)]

        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk + sentence) <= chunk_size:
                current_chunk += sentence
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # 新块从当前句子开始，但要考虑重叠
                # 这里简化处理，直接开始新块
                # 更复杂的重叠策略可以在这里实现
                current_chunk = sentence
                # 如果当前句子本身就超过了 chunk_size，需要更精细的处理
                if len(current_chunk) > chunk_size:
                    # 按字符硬切（最后手段）
                    temp_chunks = [current_chunk[i:i+chunk_size-overlap] for i in range(0, len(current_chunk), chunk_size-overlap)]
                    if temp_chunks and len(temp_chunks[-1]) < overlap and len(chunks) > 0: # 如果最后一个块太短，合并到上一个
                        chunks[-1] += temp_chunks.pop()
                    chunks.extend(temp_chunks)
                    current_chunk = "" # 当前句子已被完全处理

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks