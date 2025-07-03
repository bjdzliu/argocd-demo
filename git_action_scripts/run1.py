import os
import sys
import json
import requests

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
    
if __name__ == '__main__':
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    if project_root not in sys.path:
        sys.path.insert(0, project_root) 

    from automation.utils.jira_utils import JiraUtils
    print("jira_util imported successfully!")
    test_list=get_test_list()
    print(test_list)


    # issue_key = os.environ.get('ISSUE_KEY')
    # issue = jira_utils.get_test_execution_by_key(issue_key)
    # if issue:
    #     print(f"Test Execution {issue_key} found: {issue['summary']}")
    # else:
    #     print(f"Test Execution {issue_key} not found.")
