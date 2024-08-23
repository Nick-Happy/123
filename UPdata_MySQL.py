import pandas as pd
import mysql.connector
from tqdm import tqdm

# 读取CSV文件
file_path = r"C:\Users\Administrator\Desktop\adamId_1141795249.csv"
data = pd.read_csv(file_path)

# 连接到MySQL数据库
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '251016',
    'database': 'dbgpt'
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# 创建表（如果表不存在）
create_table_query = """
CREATE TABLE IF NOT EXISTS adamId_1141795249 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    org_id INT,
    adam_id INT,
    countries_or_regions VARCHAR(255),
    hourly VARCHAR(255),
    keyword_id INT,
    keyword_name VARCHAR(255),
    impressions INT,
    installs INT,
    taps INT,
    spend double,
    currency VARCHAR(255),
    cpt_bid double
)
"""
cursor.execute(create_table_query)

# 插入数据
for index, row in tqdm(data.iterrows()):
    insert_query = """
    INSERT INTO adamId_1141795249 (org_id, adam_id, countries_or_regions, hourly, keyword_id, keyword_name, impressions, installs, taps, spend, currency, cpt_bid)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (row['org_id'], row['adam_id'], row['countries_or_regions'], row['hourly'], row['keyword_id'], row['keyword_name'], row['impressions'], row['installs'], row['taps'], row['spend'], row['currency'], row['cpt_bid'])
    cursor.execute(insert_query, values)

# 提交更改并关闭连接
connection.commit()
cursor.close()
connection.close()