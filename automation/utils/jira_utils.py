import os
from jira import JIRA
from typing import Optional, Dict


class JiraUtils:
    def __init__(self, server: str, username: str, api_token: str):
        """Initialize Jira client."""
        options = {'server': server}
        self.jira = JIRA(options, basic_auth=(username, api_token))

    def get_test_execution_by_key(self, issue_key: str) -> Optional[Dict]:
        """
        Retrieve a Test Execution issue using its Jira issue key.
        
        :param issue_key: The Jira issue key (e.g., 'TESTEXEC-123')
        :return: Issue dict or None if not found
        """
        try:
            issue = self.jira.issue(issue_key)
            if issue.fields.issuetype.name.lower() == 'test execution':
                return {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name
                }
            else:
                print(f"Issue {issue_key} is not a Test Execution.")
        except Exception as e:
            print(f"Error fetching issue {issue_key}: {e}")
        return None

    def get_test_execution_by_summary(self, summary: str, project_key: str) -> Optional[Dict]:
        """
        Search for a Test Execution issue using its summary (title).
        
        :param summary: Summary of the issue (exact match)
        :param project_key: Jira project key to scope the search
        :return: First matching issue dict or None
        """
        jql = f'project = "{project_key}" AND issuetype = "Test Execution" AND summary ~ "{summary}"'
        try:
            issues = self.jira.search_issues(jql, maxResults=1)
            if issues:
                issue = issues[0]
                return {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name
                }
        except Exception as e:
            print(f"Error searching for Test Execution by summary: {e}")
        return None
    def get_test_execution_by_title(self, title: str) -> Optional[Dict]:
        """
        Search for a Test Execution issue using its title.

        :param title: Title of the issue (exact match)
        :param project_key: Jira project key to scope the search
        :return: First matching issue dict or None  
        """
        jql = f'issuetype = "Test Execution" AND summary ~ "{title}"'
        try:
            issues = self.jira.search_issues(jql, maxResults=1)
            if issues:
                issue = issues[0]
                return {
                    "key": issue.key,   
                    "summary": issue.fields.summary,    
                }
        except Exception as e:
            print(f"Error searching for Test Execution by title: {e}")
    def get_testcase_by_test_execution(self, test_execution_key: str) -> Optional[Dict]:
        jql = f'issue in testExecutionTests("{test_execution_key}")'
        issues = self.jira.search_issues(jql, maxResults=100)
        return [issue.key for issue in issues]
