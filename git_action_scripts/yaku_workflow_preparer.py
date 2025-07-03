import os
import sys
import json
import requests
import shutil
"""
1. Get a test-cases list that need to be automated
2. Construct scripts and configuration 
3. Send a request of starting workflow to YAKU
"""

def get_test_list()->list:
    server=os.environ.get('JIRA_SERVER')
    t=os.environ.get('JIRA_API_TOKEN')
    print('token is:',t)
    TEST_EXECUTION_KEY=os.environ.get('TEST_EXECUTION_KEY')
    jira_utils = JiraUtils(
        server=os.environ.get('JIRA_SERVER'),
        username=os.environ.get('JIRA_USERNAME'),
        api_token=os.environ.get('JIRA_API_TOKEN')
    )
    #result=jira_utils.get_test_execution_by_key(TEST_EXECUTION_KEY)
    return ['ADTOPS-1163','ADTOPS-1619']
    
def construct_files(test_list):
    source_dir = os.path.join('automation', 'utils') 
    print(f"Source directory: {source_dir}")
    for target_dir_name in test_list:
        target_dir_path = os.path.join(source_dir, target_dir_name)
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

if __name__ == '__main__':
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    if project_root not in sys.path:
        sys.path.insert(0, project_root) 
    from automation.utils.jira_utils import JiraUtils
    print("jira_util imported successfully!")
    test_list=get_test_list()
    if len(test_list)>0:
        construct_files(test_list)
    
    # issue_key = os.environ.get('ISSUE_KEY')
    # issue = jira_utils.get_test_execution_by_key(issue_key)
    # if issue:
    #     print(f"Test Execution {issue_key} found: {issue['summary']}")
    # else:
    #     print(f"Test Execution {issue_key} not found.")
