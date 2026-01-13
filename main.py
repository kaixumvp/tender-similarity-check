import re
import jieba
import pycorrector
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class BidDocumentChecker:
    """标书查重与错别字纠错工具类"""
    
    def __init__(self):
        # 初始化TF-IDF向量化器（中文分词）
        self.vectorizer = TfidfVectorizer(
            tokenizer=jieba.lcut,  # 使用jieba分词
            lowercase=False,       # 中文不需要小写
            stop_words=self._get_stop_words()  # 加载停用词
        )
    
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
    
    def correct_typo(self, text):
        """错别字纠错"""
        # 使用pycorrector进行纠错
        corrected_text, detail = pycorrector.Corrector().correct(sentence=text)
        # 整理纠错详情
        correction_info = []
        for item in detail:
            correction_info.append({
                '原词': item['raw'],
                '纠错后': item['corrected'],
                '位置': item['start_idx']
            })
        return corrected_text, correction_info
    
    def calculate_similarity(self, text1, text2):
        """计算两个文本的相似度（纯文字层面，非语义）"""
        # 对文本进行预处理
        text1 = self.preprocess_text(text1)
        text2 = self.preprocess_text(text2)
        
        # 纠错
        text1_corrected, correction1 = self.correct_typo(text1)
        text2_corrected, correction2 = self.correct_typo(text2)
        
        # TF-IDF向量化
        tfidf_matrix = self.vectorizer.fit_transform([text1_corrected, text2_corrected])
        
        # 计算余弦相似度（0-1之间，越接近1越相似）
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # 提取高重复片段（可选，这里提取前10个高频词的交集）
        # 获取词汇表和权重
        feature_names = self.vectorizer.get_feature_names_out()
        tfidf_scores1 = tfidf_matrix[0].toarray()[0]
        tfidf_scores2 = tfidf_matrix[1].toarray()[0]
        
        # 筛选高频词（权重前10%）
        threshold1 = np.percentile(tfidf_scores1, 90)
        threshold2 = np.percentile(tfidf_scores2, 90)
        high_freq_words1 = [feature_names[i] for i, score in enumerate(tfidf_scores1) if score >= threshold1]
        high_freq_words2 = [feature_names[i] for i, score in enumerate(tfidf_scores2) if score >= threshold2]
        
        # 高频词交集（高重复特征）
        common_high_freq_words = list(set(high_freq_words1) & set(high_freq_words2))
        
        return {
            '重复率': round(similarity * 100, 2),  # 转换为百分比，保留2位小数
            '文本1纠错详情': correction1,
            '文本2纠错详情': correction2,
            '文本1纠错后': text1_corrected[:200] + '...' if len(text1_corrected) > 200 else text1_corrected,
            '文本2纠错后': text2_corrected[:200] + '...' if len(text2_corrected) > 200 else text2_corrected,
            '高重复特征词': common_high_freq_words[:10]  # 取前10个
        }

# ------------------- 测试示例 -------------------
if __name__ == "__main__":
    # 初始化查重工具
    checker = BidDocumentChecker()
    
    # 模拟两份标书文本
    bid_text1 = """
    本公司具备承览大型工程的资质和能力，拥有多年轻松验的项目经验，
    能够按照甲方要求按质按量完成工程建设，工期保证在180天以内，
    报价为人民币880万元整。
    """
    
    bid_text2 = """
    我司具备承揽大型工程的资质和能力，拥有多年经验的项目经验，
    能够按照甲方要求按质按量完成工程建设，工期保证在180天之内，
    报价为人民币880万元整。
    """
    
    # 执行查重和纠错
    result = checker.calculate_similarity(bid_text1, bid_text2)
    
    # 输出结果
    print("===== 标书查重&纠错报告 =====")
    print(f"重复率：{result['重复率']}%")
    print("\n--- 文本1纠错详情 ---")
    if result['文本1纠错详情']:
        for item in result['文本1纠错详情']:
            print(f"原词：{item['原词']} → 纠错后：{item['纠错后']}（位置：{item['位置']}）")
    else:
        print("无错别字")
    
    print("\n--- 文本2纠错详情 ---")
    if result['文本2纠错详情']:
        for item in result['文本2纠错详情']:
            print(f"原词：{item['原词']} → 纠错后：{item['纠错后']}（位置：{item['位置']}）")
    else:
        print("无错别字")
    
    print("\n--- 高重复特征词 ---")
    print(result['高重复特征词'])