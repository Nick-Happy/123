import os
import requests
from tqdm import tqdm


def upload_csv_files(folder_path, upload_url, knowledge_base_name):
    # Initialize an empty list to store the paths of found CSV files
    csv_files = []
    # Initialize a variable to record the total number of found CSV files
    total_files = 0

    # Use os.walk to traverse the specified folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        # Traverse all files in the current folder
        for file in files:
            # If the file is a CSV file and matches the required pattern, add its path to csv_files list
            # if file.endswith(".csv") and file.startswith("adamId_"):
            if file.endswith(".csv") and file.startswith("adamId_"):
                csv_files.append(os.path.join(root, file))
    # Update the total number of found CSV files
    total_files = len(csv_files)
    # Print the total number of found CSV files
    print("Total CSV files found:", total_files)

    # Initialize a variable to record the number of uploaded files
    uploaded_count = 0


    with tqdm(total=total_files, desc="Uploading") as pbar:
        # Traverse all found CSV files
        for csv_file in csv_files:
            # Prepare the file to be uploaded, including file name, file object, and file type
            files = {'files': (os.path.basename(csv_file), open(csv_file, 'rb'), 'text/csv')}
            # Prepare the data to be uploaded, including some setting parameters and the knowledge base name
            data = {
                'to_vector_store': 'true',
                'override': 'false',
                'not_refresh_vs_cache': 'false',
                'chunk_size': '1000',
                'chunk_overlap': '300',
                'zh_title_enhance': 'true',
                'knowledge_base_name': knowledge_base_name
            }
            # Send a POST request to upload the file
            response = requests.post(upload_url, files=files, data=data)
            # Update the number of uploaded files
            uploaded_count += 1
            # Update the progress bar
            pbar.update(1)
            # Update the postfix of the progress bar to show the number of uploaded files
            pbar.set_postfix({"Uploaded": uploaded_count})
            # Print the server's response
            print("Response:", response.text)


if __name__ == "__main__":
    # Set the folder path containing the CSV files to be uploaded
    # folder_path = "D:\\PycharmProjects\\pythonProject3\\待上传文件\\上传文件测试数据文件夹"
    folder_path = "D:\PycharmProjects\pythonProject4\split_Yes"
    # Set the API upload address of LangChainChatChat
    upload_url = ' http://192.168.1.111:7861/knowledge_base/upload_docs'
    # Set the name of the knowledge base to upload to
    knowledge_base_name = "test_self"
    # Call the function to start uploading CSV files
    upload_csv_files(folder_path, upload_url, knowledge_base_name)
