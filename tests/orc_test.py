# import os
# import pandas as pd
# from paddleocr import PPStructure, save_structure_res
#
#
# def ppstructure_table_detect(img_path, save_dir="./table_output"):
#     """
#     PPStructure 表格识别基础函数
#     :param img_path: 表格图片路径（Windows用r""原始字符串）
#     :param save_dir: 结果保存目录（自动创建）
#     :return: 识别结果（字典）、表格DataFrame（若有表格）
#     """
#     # 1. 初始化PPStructure引擎（表格识别核心配置）
#     table_engine = PPStructure(
#         table=True,  # 必开！表格识别总开关，False则不识别表格
#         show_log=False,  # 关闭冗余日志，简化输出
#         lang="ch",  # 语言配置：ch(中英混合/纯中文)、en(纯英文)
#         ocr_version="PP-OCRv4",  # 文字识别模型版本，2.7.0适配PP-OCRv4
#         table_max_len=640  # 表格模型输入最大边长，适配大尺寸表格（默认488，可调大）
#     )
#
#     # 2. 检查图片路径是否存在
#     if not os.path.exists(img_path):
#         raise FileNotFoundError(f"表格图片不存在：{img_path}")
#
#     # 3. 创建结果保存目录
#     if not os.path.exists(save_dir):
#         os.makedirs(save_dir)
#
#     # 4. 执行表格识别（核心步骤）
#     # result：列表，包含图片中所有结构化结果（表格/纯文本块/公式等）
#     result = table_engine(img_path)
#
#     # 5. 保存可视化结果（带表格框选的图片，方便核对）
#     img_name = os.path.basename(img_path).split(".")[0]  # 提取图片名（无后缀）
#     save_structure_res(result, save_dir, img_name)  # 保存可视化图片到save_dir
#
#     # 6. 解析表格结果并导出Excel
#     table_df = None  # 存储表格DataFrame
#     for idx, res in enumerate(result):
#         if res["type"] == "table":  # 筛选出表格类型结果（排除纯文本/公式）
#             print(f"检测到第{idx + 1}个表格，正在解析...")
#             # 表格核心结果：res["res"] 包含html结构、单元格坐标、文字等
#             table_html = res["res"]["html"]  # 表格HTML结构（核心，用于解析行列）
#
#             # 7. HTML转DataFrame（自动还原行列/合并单元格）
#             try:
#                 # pandas读取HTML表格，自动处理行列结构
#                 tables = pd.read_html(table_html)
#                 if tables:
#                     table_df = tables[0]
#                     # 8. 导出Excel（无索引，方便后续编辑）
#                     excel_path = os.path.join(save_dir, f"{img_name}_表格{idx + 1}.xlsx")
#                     table_df.to_excel(excel_path, index=False, engine="openpyxl")
#                     print(f"表格{idx + 1}导出成功：{excel_path}")
#             except Exception as e:
#                 print(f"表格{idx + 1}解析失败：{str(e)}")
#                 print(f"原始HTML结构：{table_html[:500]}...")  # 打印前500字符排查问题
#         # 若需提取纯文本块（表格外的文字），可在此处处理
#         elif res["type"] == "text":
#             text = res["res"]["text"]
#             print(f"纯文本：{text}")
#
#     print(f"表格识别完成，所有结果已保存至：{save_dir}")
#     return result, table_df
#
#
# # 主函数调用（核心：替换为你的表格图片路径）
# def test_orc():
#     # Windows路径用r""原始字符串，避免反斜杠转义；Linux/Mac用普通路径
#     TABLE_IMG_PATH = r"D:\pyproject\tender-similarity-check\document/屏幕截图 2025-07-29 222309.png"
#     # 执行识别
#     ppstructure_table_detect(TABLE_IMG_PATH)