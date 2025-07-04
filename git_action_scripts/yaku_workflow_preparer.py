import os
import sys
import json
import requests
import shutil
from yaku_utils import YakuClient

"""
1. Get a test-cases list that need to be automated
2. Construct scripts and configuration 
3. Send a request of starting workflow to YAKU
"""
current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_script_path))
automation_dir = os.path.join(project_root,'automation') 
source_dir = os.path.join(automation_dir,'utils')
testcase_dir= os.path.join(automation_dir,'testcase')
print(project_root)

def get_test_list()->list:
    server=os.environ.get('JIRA_SERVER')
    t=os.environ.get('JIRA_API_TOKEN')
    TEST_EXECUTION_KEY=os.environ.get('TEST_EXECUTION_KEY')
    # jira_utils = JiraUtils(
    #     server=os.environ.get('JIRA_SERVER'),
    #     username=os.environ.get('JIRA_USERNAME'),
    #     api_token=os.environ.get('JIRA_API_TOKEN')
    # )
    #result=jira_utils.get_test_execution_by_key(TEST_EXECUTION_KEY)
    return ['ADTOPS-1163','ADTOPS-1619']
    
def construct_files(test_list):
    for target_dir_name in test_list:
        target_dir_path = os.path.join(testcase_dir, target_dir_name)
        print(f"Target directory for '{target_dir_name}': {target_dir_path}")
        print(f"Ensured target directory '{target_dir_path}' exists.")
        for filename in os.listdir(source_dir):
            if filename.endswith('.py') or filename.endswith('.json'):
                source_file_path = os.path.join(source_dir, filename)
                destination_file_path = os.path.join(target_dir_path, filename)
                try:
                    shutil.copy2(source_file_path, destination_file_path)
                    print(f"Copied '{source_file_path}' to '{destination_file_path}'")
                except FileNotFoundError:
                    print(f"Error: Source file '{source_file_path}' not found.")
                except Exception as e:
                    print(f"Error copying '{source_file_path}' to '{destination_file_path}': {e}")


def get_files_in_directory(directory_path):
    """
    Retrieves a list of all files in the specified directory (excluding subdirectories and files within them).
    Args:
        directory_path (str): The path to the directory to be inspected.
    Returns:
        list: A list containing the names of all files directly within the directory. 
            Returns an empty list if the directory does not exist or is not a directory.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a valid directory or does not exist.")
        return []
    file_list = []
    for item_name in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item_name)
        if os.path.isfile(item_path):
            file_list.append(item_path) 
    return file_list

def execute_tests(test_list):
    YAKU_API_TOKEN=os.environ.get('YAKU_API_TOKEN')
    yaku_client=YakuClient("http://127.0.0.1:3000/",1,YAKU_API_TOKEN)
    for i in test_list:
        create_result=yaku_client.create_config(f"appname_version_{i}",f"{i} test case for appname")
        config_id=create_result.response_data()['id']
        main_config_file=os.path.join(testcase_dir, i,'qg-config.yaml')
        yaku_client.upload_file(config_id,main_config_file)
        test_case_path=os.path.join(testcase_dir, i)
        other_files=get_files_in_directory(test_case_path)
        for f in other_files:
            result=yaku_client.upload_file(config_id,f)
        yaku_client.run_config(config_id)

if __name__ == '__main__':
    if project_root not in sys.path:
        sys.path.insert(0, project_root) 
    from automation.utils.jira_utils import JiraUtils
    print("jira_util imported successfully!")
    test_list=get_test_list()
    if len(test_list)>0:
        construct_files(test_list)
        execute_tests(test_list)
    
    # issue_key = os.environ.get('ISSUE_KEY')
    # issue = jira_utils.get_test_execution_by_key(issue_key)
    # if issue:
    #     print(f"Test Execution {issue_key} found: {issue['summary']}")
    # else:
    #     print(f"Test Execution {issue_key} not found.")
