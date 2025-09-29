# Databricks notebook source
username = ''
api_token = ''

# COMMAND ----------

from requests.auth import HTTPBasicAuth
import requests
import pandas as pd
import json


# Start time
import time
start_time = time.time()

class Jira():
    def __init__(self):
        self.username = username
        self.api_token = api_token
        self.auth = HTTPBasicAuth(self.username, self.api_token)
        self.headers = {"Accept": "application/json"}
    
    def get_jira_boards(self):
        """
        Fetches all Jira boards using the Jira Agile API with pagination.
        
        Returns:
            DataFrame of all boards
        """
        time.sleep(1)
        startAt = 0
        maxResults = 50
        all_boards = []
        
        while True: 
            params = {
                "startAt": startAt,
                "maxResults": maxResults
            }
        
            response = requests.get(
                url="https://phlexglobal.atlassian.net/rest/agile/1.0/board",
                headers=self.headers,
                auth=self.auth,
                params=params
            )
        
            if response.status_code == 200:
                data = response.json()
                all_boards.extend(data.get("values", []))
                if data.get("isLast", True):
                    break
                startAt += maxResults
            else:
                print(f"Błąd {response.status_code}: {response.text}")
                break
        
        all_boards_df = pd.DataFrame(all_boards)
        all_boards_df.reset_index(drop=True, inplace=True)  # Fixed reset_index
        return all_boards_df
    
    def get_unique_boards(self):
        """
        Gets unique board IDs from all Jira boards.
        
        Returns:
            list of unique board IDs
        """
        unique_boards = self.get_jira_boards()['id'].astype(str).unique().tolist()
        return unique_boards

    def get_jira_issue_fields(self):

          response = requests.get(
            url = 'https://phlexglobal.atlassian.net/rest/api/3/field',
            headers=self.headers,
            auth=self.auth
          )
          data = response.json()
          # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
          issue_fields = pd.DataFrame(data)
        
          return issue_fields

    def get_jira_projects(self):

    
        params = {
            "expand": 'description,projectKeys,lead,issueTypes,url,insight,deletedby'
        }
    
        response = requests.get(
            url = "https://phlexglobal.atlassian.net/rest/api/3/project",
            headers=self.headers,
            auth=self.auth,
            params=params
        )
    
        projects = pd.DataFrame(response.json())
    
        # Ensure 'id' is numeric
        # projects['id'] = pd.to_numeric(projects['id'], errors='coerce').fillna(0).astype(int)
        projects = projects.drop(columns='properties')
        return projects
    def get_unique_jira_projects(self):
        
        unique_projects = self.get_jira_projects()['id'].astype(str).unique().tolist()
        return sorted(unique_projects, reverse=True)
        
    def get_jira_project_versions(self):

        time.sleep(1)
        projects_unique = self.get_unique_jira_projects()
    
        all_versions = []
    
        for i in projects_unique:
            start_at = 0
            is_last = False
    
            while not is_last:
    
                params = {
                    'startAt': start_at,
                    'maxResults': 50
                }
    
                response = requests.get(
                url = f"https://phlexglobal.atlassian.net/rest/api/3/project/{i}/version",
                headers=self.headers, 
                auth=self.auth, 
                params=params)
                data = response.json()
    
                sprints_batch = data.get('values', [])
                all_versions.extend(sprints_batch)
    
                is_last = data.get('isLast', True)
                start_at += len(sprints_batch)
    
        project_versions_df = pd.DataFrame(all_versions)
        return project_versions_df

    def get_jira_sprints(self):

        board_ids = self.get_unique_boards()
    
        startAt = 0
        maxResults = 50
        all_sprints = []
    
        for i in board_ids:
            start_at = 0 
            while True:
                url = f"https://phlexglobal.atlassian.net/rest/agile/1.0/board/{i}/sprint"
    
                params = {
                    "startAt": start_at,
                    "maxResults": maxResults
                }
    
                response = requests.get(
                    url,
                    headers=self.headers,
                    auth=self.auth,
                    params=params
                )
    
                if response.status_code != 200:
                    print(f"Error for board {i}: {response.status_code}, {response.text}")
                    break
    
                sprints = response.json()
                if not sprints.get("values"):  # No more sprints
                    break
                all_sprints.extend(sprints.get("values", []))
                start_at += maxResults
                print(f"Board {i}. Status code: {response.status_code}, Retrieved {len(sprints.get('values', []))} sprints")
        all_sprints = pd.DataFrame(all_sprints)
        return all_sprints
    
    def get_jira_users(self):

        start_at = 0
        max_results = 100
        all_users = []
        
        while True:
            params = {
                "startAt": start_at,
                "maxResults": max_results
            }
            response = requests.get(
                url = "https://phlexglobal.atlassian.net/rest/api/3/users", 
                auth=self.auth, 
                params=params)
            
            users = response.json()
            
            if not users:
                break
            all_users.extend(users)
            start_at += max_results
    
        users_df = pd.DataFrame(all_users)
        return users_df

    def get_jira_issues_projects(self, days_back=2, project=[], date_from=None, date_to=None):
        """
        Fetches issues from all Jira projects
        
        Args:
            days_back (int): how many days back (if dates not provided)
            date_from (str): atart date (format: 'YYYY-MM-DD')
            date_to (str): end date (format: 'YYYY-MM-DD')
        
        Returns:
            pd.DataFrame: df with issues or empty df on error
        """
        
        all_issues = []
        errors = []

        

        if project != []:
            unique_jira_proj = project
        else:
            unique_jira_proj = self.get_unique_jira_projects()
        
        
        for pid in unique_jira_proj:
            start_at = 0
            max_results = 50 
            

            if date_from and date_to:
                jql_query = f"project = {pid} AND updated >= '{date_from}' AND updated <= '{date_to}'"
            else:
                jql_query = f"project = {pid} AND updated >= -{days_back}d"
            
            project_issues = []
            
            while True:
                params = {
                    "jql": jql_query,
                    "maxResults": max_results,
                    "startAt": start_at,
                    "expand": "versionedRepresentations,renderedFields, transitions,editmeta,changelog",
                    "fields": "*all",
                    
                }
                
                url = "https://phlexglobal.atlassian.net/rest/api/3/search/jql"
                
                try:
                    response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
                    
                    if response.status_code != 200:
                        errors.append({
                            "project": pid,
                            "status_code": response.status_code,
                            "response": response.text
                        })
                        break
                    
                    data = response.json()
                    issues_list = data.get('issues', [])
                    total = data.get('total', 0)
                    
                    if not issues_list:
                        break
                    

                    for issue in issues_list:
                        issue['source_project_id'] = pid
                    
                    project_issues.extend(issues_list)
                    
                    if len(issues_list) < max_results or start_at + max_results >= total:
                        break
                        
                    start_at += max_results
                        
                except (requests.RequestException, json.JSONDecodeError) as e:
                    errors.append({
                        "project": pid,
                        "error": str(e)
                    })
                    break
            
            all_issues.extend(project_issues)
            print(f"project nr {pid} added")
        if not all_issues:
            return pd.DataFrame()
        
        issues_df = pd.DataFrame(all_issues)
        
        def extract_updated(versioned):
            if isinstance(versioned, str):
                try:
                    versioned = json.loads(versioned)
                except:
                    return None
            if isinstance(versioned, dict):
                updated_field = versioned.get('updated')
                if isinstance(updated_field, dict):
                    first_value = next(iter(updated_field.values()), None)
                    if isinstance(first_value, str):
                        return first_value.split('T')[0]
                elif isinstance(updated_field, str):
                    return updated_field.split('T')[0]
            return None
    
        issues_df['updated'] = issues_df.get('versionedRepresentations', None).apply(extract_updated)
        issues_df['updated'] = pd.to_datetime(issues_df['updated'], errors='coerce').dt.date
    
        for col in ['versionedRepresentations', 'renderedFields', 'transitions', 'editmeta', 'changelog']:
            if col in issues_df.columns:
                issues_df[col] = issues_df[col].apply(
                    lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
                )
    
        issues_df.reset_index(drop=True, inplace=True)
        
        return issues_df
    
# Usage
api = Jira()