from apps.algorithms.embedding import QwenEmbeddingVectorizer
from apps.document_parser.base_parser import HDocument
from apps.document_parser.pdf_parser import PdfParser
from apps.service.milnus_service import create_tender_vector_milnus_db
from apps.splitting import overlapping_splitting


def test_pdf_parser():
    file_path = "D:/pyproject/tender-similarity-check/document/南沙区2026-2027年市政道路绿化养护项目招标文件（2026011103）.pdf"
    pdf_parser = PdfParser()
    filedocument = pdf_parser.parse(file_path, "2026011103")
    print("---------------------------------------------------")
    documents:list[HDocument] = pdf_parser.overlapping_splitting(filedocument, 5000, 100)
    milvus_vector_db = create_tender_vector_milnus_db(4096)
    milvus_vector_db.insert_data(documents)
    #for document in documents:
        #print("单个page的类型：", type(document))
        #vectorizer = QwenEmbeddingVectorizer()
        #vec_list = vectorizer.encode(document.text)
        
        #collection = milvus_vector_db.get_collection()
        #collection.insert()
        #print(f"文件页数：{str(document.page)}，开始位置：{document.start_index}", f"文本内容：{document.text}")


def test_text_splite():
    file_path = "D:/pyproject/tender-similarity-check/document/南沙区2026-2027年市政道路绿化养护项目招标文件（2026011103）.pdf"
    pdf_parser = PdfParser()
    pdf_test = pdf_parser.parse(file_path)
    chunks = overlapping_splitting(pdf_test, 2000)   #100个字符拆分一个片段，重叠25个字符拆分
    print(f"片段数量：{chunks}")
    for chunk in chunks:
        print(f"[处理前片段：{chunk}---------字符长度：{len(chunk)}]")
        result_text = pdf_parser.preprocess_text(chunk)
        print(f"[处理后片段：{result_text}---------字符长度：{len(result_text)}]")
        #get_embedding(chunk)