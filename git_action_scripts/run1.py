import os
import sys
import json
import requests

if __name__ == '__main__':
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    if project_root not in sys.path:
        sys.path.insert(0, project_root) # 将项目根目录添加到搜索路径的最前面

    from automation.utils.jira_utils import JiraUtils
    server=os.environ.get('JIRA_SERVER')
    print("jira server is ",server)
    jira_utils = JiraUtils(
        server=os.environ.get('JIRA_SERVER'),
        username=os.environ.get('JIRA_USERNAME'),
        api_token=os.environ.get('JIRA_API_TOKEN')
    )
    print("jira_util imported successfully!")
    # issue_key = os.environ.get('ISSUE_KEY')
    # issue = jira_utils.get_test_execution_by_key(issue_key)
    # if issue:
    #     print(f"Test Execution {issue_key} found: {issue['summary']}")
    # else:
    #     print(f"Test Execution {issue_key} not found.")
