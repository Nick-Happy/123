import os
import pandas as pd
import math
from tqdm import tqdm


def split_csv_with_header_insertion(file_path, output_dir, chunk_size_kb=100, encoding='utf-8'):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取文件大小 (bytes)
    try:
        file_size = os.path.getsize(file_path)
        print(f"文件大小: {file_size} bytes")
    except Exception as e:
        print(f"获取文件大小时出错: {e}")
        return

    # 读取CSV文件
    try:
        df = pd.read_csv(file_path, encoding=encoding)
    except UnicodeDecodeError as e:
        print(f"读取CSV文件时编码错误: {e}")
        return
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return

    # 表头
    header = df.columns.tolist()

    # 在每隔一行插入表头
    rows = []
    for i in range(len(df)):
        rows.append(df.iloc[i].tolist())
        if i < len(df) - 1:  # 不在最后一行后插入
            rows.append(header)

    # 转换回DataFrame
    new_df = pd.DataFrame(rows, columns=df.columns)

    # 计算每个chunk的大小
    chunk_size = chunk_size_kb * 1024  # 转换为bytes

    # 估算每行的大小
    num_rows = new_df.shape[0]
    estimated_row_size = file_size / (num_rows - df.shape[0])  # 每行的估计大小

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
        chunk_df = new_df.iloc[start_row:end_row]
        output_file_path = os.path.join(output_dir, f"{base_name}_{i + 1}.csv")
        chunk_df.to_csv(output_file_path, index=False)
        print(f"保存chunk {i + 1}到: {output_file_path}")


# 使用示例
file_path = 'D:\\PycharmProjects\\pythonProject4\\split_No\\adamId_1671489753.csv'
output_directory = 'D:\\PycharmProjects\\pythonProject4\\split_Yes'
split_csv_with_header_insertion(file_path, output_directory, chunk_size_kb=100, encoding='ISO-8859-1')
