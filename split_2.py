import os
import pandas as pd
import math
from tqdm import tqdm

def split_csv(file_path, output_dir, chunk_size_kb=100, encoding='utf-8'):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取文件大小 (bytes)
    file_size = os.path.getsize(file_path)
    print(f"文件大小: {file_size} bytes")

    try:
        # 读取CSV文件
        df = pd.read_csv(file_path, encoding=encoding)
    except UnicodeDecodeError:
        print(f"无法使用编码 {encoding} 读取文件 {file_path}. 尝试其他编码...")
        # 尝试其他常见编码
        for enc in ['ISO-8859-1', 'utf-16', 'cp1252']:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                encoding = enc
                print(f"成功使用编码 {encoding} 读取文件 {file_path}.")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise Exception(f"无法读取文件 {file_path} 使用所有尝试的编码.")

    # 计算每个chunk的大小
    chunk_size = chunk_size_kb * 1024  # 转换为bytes

    # 估算每行的大小
    num_rows = df.shape[0]
    estimated_row_size = file_size / num_rows  # 每行的估计大小

    # 计算每个chunk的行数
    rows_per_chunk = math.floor(chunk_size / estimated_row_size)
    print(f"每个chunk的行数: {rows_per_chunk}")

    # 获取原文件名（不包括路径和扩展名）
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    # 切分并保存CSV文件
    num_chunks = math.ceil(num_rows / rows_per_chunk)
    for i in range(num_chunks):
        start_row = i * rows_per_chunk
        end_row = min((i + 1) * rows_per_chunk, num_rows)
        chunk_df = df.iloc[start_row:end_row]
        output_file_path = os.path.join(output_dir, f"{base_name}_{i + 1}.csv")
        chunk_df.to_csv(output_file_path, index=False, encoding=encoding)
        print(f"保存chunk {i + 1}到: {output_file_path}")

def process_all_csv_files(input_dir, output_dir, chunk_size_kb=100):
    # 获取所有CSV文件
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

    # 处理每个CSV文件并显示进度条
    for file in tqdm(csv_files, desc="处理CSV文件"):
        file_path = os.path.join(input_dir, file)
        split_csv(file_path, output_dir, chunk_size_kb)

# 使用示例
input_directory = 'D:\\PycharmProjects\\pythonProject4\\split_No'
output_directory = 'D:\\PycharmProjects\\pythonProject4\\split_Yes'
process_all_csv_files(input_directory, output_directory, chunk_size_kb=100)
