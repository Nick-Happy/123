import os
import pandas as pd
from tqdm import tqdm
import time

# Define the path to the directory containing the files
source_path = r'E:/自用/数据/日报数据未处理/2023'

# Define the path to the directory where cleaned files will be saved
destination_path = r'E:/自用/数据/日报数据未处理/today_yes'

# Ensure the destination directory exists, create if it does not
os.makedirs(destination_path, exist_ok=True)

# List of fields to remove
ziduan = [
    "id", "channel_id", "campaign_id", "ad_group_id", 
    "crate_time", "keyword_status", "new_downloads", 
    "re_downloads", "lat_on_installs", "lat_off_installs", "match_type","modification_time"
]

# List all files in the specified source directory
file_list = os.listdir(source_path)

# Iterate over each file in the directory using tqdm for the progress bar
for file in tqdm(file_list, desc="Processing files", unit="file"):
    # Construct the full file path for reading
    file_path = os.path.join(source_path, file)
    
    # Check if the file is a CSV file (adjust this check if your files are not CSVs)
    if file.endswith('.csv'):
        start_time = time.time()  # Record the start time
        
        # try:
            # Attempt to read the file with the default encoding
        df = pd.read_csv(file_path, encoding='utf-8')
        # except UnicodeDecodeError:
        #     try:
        #         # Try a different encoding, e.g., ISO-8859-1
        #         df = pd.read_csv(file_path, encoding='ISO-8859-1')
        #     except UnicodeDecodeError:
        #         # Try another encoding, e.g., GBK (for Chinese characters)
        #         df = pd.read_csv(file_path, encoding='gbk')

        # Drop the specified columns if they exist in the DataFrame
        df_cleaned = df.drop(columns=[col for col in ziduan if col in df.columns], errors='ignore')
        
        # Construct the full file path for saving
        cleaned_file_path = os.path.join(destination_path, f"cleaned_{file}")
        
        # Save the cleaned DataFrame to the destination directory
        df_cleaned.to_csv(cleaned_file_path, index=False,encoding='utf-8')
        
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        print(f"Processed and saved cleaned data for file: {file} to {cleaned_file_path} in {elapsed_time:.2f} seconds")
