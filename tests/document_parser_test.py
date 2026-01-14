from apps.document_parser.pdf_parser import PdfParser
from apps.splitting import overlapping_splitting


def test_pdf_parser():
    file_path = "D:/pyproject/tender-similarity-check/document/南沙区2026-2027年市政道路绿化养护项目招标文件（2026011103）.pdf"
    pdf_parser = PdfParser()
    pdf_test = pdf_parser.parse(file_path)
    print(f"test_pdf_parser:{pdf_test}")


def test_text_splite():
    file_path = "D:/pyproject/tender-similarity-check/document/南沙区2026-2027年市政道路绿化养护项目招标文件（2026011103）.pdf"
    pdf_parser = PdfParser()
    pdf_test = pdf_parser.parse(file_path)
    chunks = overlapping_splitting(pdf_test, 500)   #100个字符拆分一个片段，重叠25个字符拆分
    for chunk in chunks:
        print(f"[片段：{chunk}---------字符长度：{len(chunk)}]")
        #get_embedding(chunk)