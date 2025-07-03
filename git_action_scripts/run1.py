import os
import sys
import json
import requests

from utils.jira_utils import JiraUtils

if __name__ == '__main__':
    jira_utils = JiraUtils(
        server=os.environ.get('JIRA_SERVER'),
        username=os.environ.get('JIRA_USERNAME'),
        api_token=os.environ.get('JIRA_API_TOKEN')
    )
    print("hello world")
    # issue_key = os.environ.get('ISSUE_KEY')
    # issue = jira_utils.get_test_execution_by_key(issue_key)
    # if issue:
    #     print(f"Test Execution {issue_key} found: {issue['summary']}")
    # else:
    #     print(f"Test Execution {issue_key} not found.")
