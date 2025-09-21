import os
import requests
from jira import JIRA
from typing import Optional, Dict


class JiraUtils:
    def __init__(self, server: str, api_token: str):
        """
        Initialize Jira client with token authentication.
        
        :param server: Jira server URL
        :param api_token: Jira API token
        """
        options = {
            'server': server,
            'headers': {
                'Authorization': f'Bearer {api_token}'
            }
        }
        self.jira = JIRA(options)
        self.api_token = api_token  # Store token for other API calls

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
    def get_test_by_plan(self, test_plan_key: str) -> Optional[Dict]:
        """
        Get test cases from a test plan using Xray API 2.0.
        
        :param test_plan_key: The test plan issue key (e.g., 'SDTOPA-3')
        :return: Dictionary containing test cases or None if failed
        """
        try:
            # Construct the Xray API URL
            xray_url = f"{self.jira._options['server']}/rest/raven/2.0/api/testplan/{test_plan_key}/test"
            
            # Set up headers with token authentication
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_token}'
            }
            
            # Make the request to Xray API
            response = requests.get(xray_url, headers=headers)
            response.raise_for_status()  # Raise exception for non-200 status codes
            
            # Parse response and extract keys
            test_cases = response.json()
            test_keys = [item['key'] for item in test_cases if 'key' in item]
            
            print(f"Found {len(test_keys)} test cases in test plan {test_plan_key}")
            return test_keys
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching test cases from test plan {test_plan_key}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def get_testcase_by_test_execution(self, test_execution_key: str) -> Optional[Dict]:
        """Get all test cases in a test execution using Xray API"""
        try:
            xray_url = f"{self.jira._options['server']}/rest/raven/2.0/api/testexec/{test_execution_key}/test"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_token}'
            }
            
            response = requests.get(xray_url, headers=headers)
            response.raise_for_status()
            test_cases = response.json()
            return [test['key'] for test in test_cases if 'key' in test]
            
        except Exception as e:
            print(f"Error getting test cases from execution {test_execution_key}: {e}")
            return None
            
    def update_test_execution_tests(self, test_execution_key: str, tests_to_add: list = None, tests_to_remove: list = None) -> bool:
        """
        Update test cases in a test execution using Xray API.
        
        :param test_execution_key: The test execution issue key
        :param tests_to_add: List of test case keys to add
        :param tests_to_remove: List of test case keys to remove
        :return: True if successful, False otherwise
        """
        try:
            xray_url = f"{self.jira._options['server']}/rest/raven/1.0/api/testexec/{test_execution_key}/test"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_token}'
            }
            
            request_body = {
                "add": tests_to_add if tests_to_add else [],
                "remove": tests_to_remove if tests_to_remove else []
            }
            
            response = requests.post(xray_url, headers=headers, json=request_body)
            response.raise_for_status()
            
            add_count = len(tests_to_add) if tests_to_add else 0
            remove_count = len(tests_to_remove) if tests_to_remove else 0
            print(f"Successfully updated test execution {test_execution_key}:")
            if add_count > 0:
                print(f"- Added {add_count} test cases")
            if remove_count > 0:
                print(f"- Removed {remove_count} test cases")
                
            return True
            
        except Exception as e:
            print(f"Error updating test cases in execution {test_execution_key}: {e}")
            return False

    def create_test_execution(self, test_plan_key: str, title: str, subtitle: str, project_key: str) -> Optional[Dict]:
        """
        Create a new Test Execution and link test cases from the specified Test Plan.
        
        :param test_plan_key: The Jira Test Plan issue key (e.g., 'TESTPLAN-123')
        :param title: Main title for the test execution
        :param subtitle: Subtitle for the test execution
        :param project_key: Jira project key where the Test Execution will be created
        :return: Created Test Execution dict or None if creation failed
        """
        try:
            # Generate the execution name following the convention: "Execution - title - subtitle"
            execution_name = f"Execution - {title} - {subtitle}"
            
            # First, verify the test plan exists and get its test cases
            test_plan_issue = self.jira.issue(test_plan_key)
            if test_plan_issue.fields.issuetype.name.lower() != 'test plan':
                print(f"Issue {test_plan_key} is not a Test Plan.")
                return None
            
            # Get test cases from the test plan using Xray API
            test_case_keys = self.get_test_by_plan(test_plan_key)
            
            if not test_case_keys:
                print(f"No test cases found in Test Plan {test_plan_key}")
                return None
            
            # Create the Test Execution issue
            issue_dict = {
                'project': {'key': project_key},
                'summary': execution_name,
                'issuetype': {'name': 'Test Execution'},
                'description': f'Test Execution created for Test Plan: {test_plan_key}\nTitle: {title}\nSubtitle: {subtitle}'
            }
            
            new_issue = self.jira.create_issue(fields=issue_dict)
            print(f"Created Test Execution: {new_issue.key}")
            
            # Link test cases to test execution using Xray API
            try:
                xray_link_url = f"{self.jira._options['server']}/rest/raven/2.0/api/testexec/{new_issue.key}/test"
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_token}'
                }
                
                # Prepare request body with add/remove format
                request_body = {
                    "add": test_case_keys,
                    "remove": []  # Empty list as we're only adding tests
                }
                
                response = requests.post(
                    xray_link_url,
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                
                print(f"Successfully linked {len(test_case_keys)} test cases to Test Execution {new_issue.key}")
                linked_count = len(test_case_keys)
            except Exception as link_error:
                print(f"Warning: Could not link test cases to execution {new_issue.key}: {link_error}")
                linked_count = 0
            
            return {
                "key": new_issue.key,
                "summary": new_issue.fields.summary,
                "status": new_issue.fields.status.name,
                "linked_test_cases": linked_count,
                "test_plan": test_plan_key
            }
            
        except Exception as e:
            print(f"Error creating Test Execution: {e}")
            return None

if __name__ == "__main__":
    # Example usage with token authentication
    JIRA_SERVER = os.environ.get('JIRA_SERVER', 'http://localhost:8080')
    JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
    
    if not JIRA_API_TOKEN:
        print("Error: JIRA_API_TOKEN environment variable is not set")
        exit(1)
        
    jira_utils = JiraUtils(
        server=JIRA_SERVER,
        api_token=JIRA_API_TOKEN
    )
 
    # Create a test execution
    result = jira_utils.create_test_execution(
        test_plan_key="SDTOPA-3",
        title="Test-Exec-Title",
        subtitle="Test-Exec-Subtitle",
        project_key="SDTOPA"
    )
    
    if result:
        print(f"Created test execution: {result['key']}")
        # # Example: Update test cases in the execution
        # jira_utils.update_test_execution_tests(
        #     test_execution_key=result['key'],
        #     tests_to_add=["SDTOPA-1", "SDTOPA-2"],
        #     tests_to_remove=["SDTOPA-3"]
        # )
        
        # Get current test cases in the execution
        test_cases = jira_utils.get_testcase_by_test_execution(result['key'])
        if test_cases:
            print("\nCurrent test cases in execution:")
            for test_key in test_cases:
                print(f"- {test_key}")
    else:
        print("Failed to create test execution")