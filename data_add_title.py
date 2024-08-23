import pandas as pd
from tqdm import tqdm
import os
import glob
import time

# Define file paths
input_directory = r"E:\自用\数据\日报数据未处理\gaiming"
product_info_file_path = r"E:\自用\数据\日报数据未处理\data_title\product_information_0716All_utf8_noDes_2.csv"
output_directory = r"E:\自用\数据\日报数据未处理\2023_add_title_yes"

# Create output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Load product information data with specified encoding
product_info_data = pd.read_csv(product_info_file_path, encoding='UTF-8')

# # Get all input files matching the naming pattern
input_files = glob.glob(os.path.join(input_directory, "keyword_total_*.csv"))

# Record start time
start_time = time.time()

# Process each input file
for input_file_path in tqdm(input_files, desc="Processing files"):
    
    input_data = pd.read_csv(input_file_path, sep=',', encoding='utf-8')
 
    # Strip whitespace from column names
    input_data.columns = input_data.columns.str.strip()

    # Convert specified columns to integers
    int_columns = ['org_id', 'adam_id', 'keyword_id', 'impressions', 'taps', 'installs', 'cpt_bid']
    # for column in int_columns:
    #     input_data[column] = input_data[column].fillna(0).astype(int)

    # Convert 'spend' to float with 2 decimal places
    # input_data['spend'] = input_data['spend'].astype(float).round(2)

    # Remove rows that are completely empty or have only zeros
    # input_data = input_data.dropna(how='all', subset=['keyword_name', 'countries_or_regions'])

    # Ensure 'title' and 'subtitle' columns are filled using product info data
    # print("Before merge, input data columns:", input_data.columns)
    # print("Product info data columns:", product_info_data.columns)

    # Perform merge operation
    merged_data = pd.merge(
        input_data,
        product_info_data[['adam_id', 'countries_or_regions', 'title', 'subtitle']],
        on=['adam_id', 'countries_or_regions'],
        how='left',
        suffixes=('', '_new')
    )

    # Debug print the columns of the merged data
    # print("After merge, merged data columns:", merged_data.columns)

    # Check if 'title_new' and 'subtitle_new' exist
    # if 'title_new' in merged_data.columns and 'subtitle_new' in merged_data.columns:
    #     # Fill in missing 'title' and 'subtitle' columns
    #     merged_data['title'].fillna(merged_data['title_new'], inplace=True)
    #     merged_data['subtitle'].fillna(merged_data['subtitle_new'], inplace=True)
    #     # Drop the temporary '_new' columns
    #     merged_data.drop(columns=['title_new', 'subtitle_new'], inplace=True)
    # else:
    #     print(f"警告: 未找到'title_new'或'subtitle_new'列，无法填充缺失值。")

    # Save processed data to the output directory with specified format
    output_file_name = os.path.basename(input_file_path)
    output_file_path = os.path.join(output_directory, output_file_name)

    # Write to CSV ensuring proper format for all columns
    merged_data.to_csv(output_file_path, index=False, sep=',', encoding='utf-8')

    print(f"文件已保存到: {output_file_path}")

# Record end time
end_time = time.time()
elapsed_time = end_time - start_time

print(f"总共耗时: {elapsed_time:.2f} 秒")
