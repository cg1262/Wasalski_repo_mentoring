from requests.auth import HTTPBasicAuth
import requests
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from pyspark.sql import SparkSession
# Start time
import time
from Core.Services.ServiceSaveToDelta import upserting_data

class ServiceBronze:
    ###################################################
    # Init
    ###################################################
#######        
    def __init__(self, dbutils, spark):
        self.spark = SparkSession.builder.getOrCreate()
        self.username = dbutils.secrets.get(scope = "engineering-metrics-keys", key = "jira-username-secret-key")
        self.api_token = dbutils.secrets.get(scope = "engineering-metrics-keys", key = "jira-secret-key")
        self.auth = HTTPBasicAuth(self.username, self.api_token)
        self.headers = {"Accept": "application/json"}
        self.catalog_schema = 'engineering_metrics.bronze.'
        self.table_schema = 'jira_'
        self.base_url = "https://phlexglobal.atlassian.net"
        self.max_results = 50
        self.max_workers = 15

    ###################################################
    # Basic
    ###################################################

 #######       
    def boards(self, checking_data=False):
        """
        Fetches all Jira boards using the Jira Agile API with pagination.

        Returns:
            DataFrame of all boards
        """
        startAt = 0
        all_boards = []
        start_time = time.time()
        while True:
            params = {
                "startAt": startAt,
                "maxResults": self.max_results
            }

            response = requests.get(
                url=f"{self.base_url}/rest/agile/1.0/board",
                headers=self.headers,
                auth=self.auth,
                params=params
            )
        
            if response.status_code == 200:
                data = response.json()
                all_boards.extend(data.get("values", []))
                if data.get("isLast", True):
                    break
                startAt += self.max_results
            else:
                print(f"Błąd {response.status_code}: {response.text}")
                break
        
        dataframe_pd = pd.DataFrame(all_boards)
        dataframe_pd['projectId'] = dataframe_pd['location'].apply(
            lambda x: x.get('projectId') if isinstance(x, dict) else None
        )
        dataframe_pd['projectKey'] = dataframe_pd['location'].apply(
            lambda x: x.get('projectKey') if isinstance(x, dict) else None
        )
        dataframe_pd.reset_index(drop=True, inplace=True)  # Fixed reset_index
        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Rows: {len(dataframe_pd)}")

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd = dataframe_pd.drop_duplicates("id")
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}boards",
                    source_dataframe=dataframe_spark,
                    target_column="id",
                    source_column="id"
                )


        return dataframe_spark

    
 #######       
    def issue_fields(self, checking_data=False):
        start_time = time.time()
        response = requests.get(
            url = f'{self.base_url}/rest/api/3/field',
            headers=self.headers,
            auth=self.auth
          )
        data = response.json()
        # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        dataframe_pd = pd.DataFrame(data)
        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Rows: {len(dataframe_pd)}")
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd = dataframe_pd.drop_duplicates("id")
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}issue_fields",
                    source_dataframe=dataframe_spark,
                    target_column="id",
                    source_column="id"
                )


        return dataframe_spark
    
#######    
    def projects(self, checking_data=False):
        start_time = time.time()

        params = {
            "expand": 'description,projectKeys,lead,issueTypes,url,insight,deletedby'
        }

        response = requests.get(
            url = f"{self.base_url}/rest/api/3/project",
            headers=self.headers,
            auth=self.auth,
            params=params
        )
    
        dataframe_pd = pd.DataFrame(response.json())
    
        # Ensure 'id' is numeric
        # projects['id'] = pd.to_numeric(projects['id'], errors='coerce').fillna(0).astype(int)
        dataframe_pd = dataframe_pd.drop(columns='properties')
        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Rows: {len(dataframe_pd)}")

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd = dataframe_pd.drop_duplicates("id")
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}projects",
                    source_dataframe=dataframe_spark,
                    target_column="id",
                    source_column="id"
                )


        return dataframe_spark
    
#######   
    def users(self, checking_data=False):
        start_time = time.time()
        start_at = 0
        all_users = []

        while True:
            params = {
                "startAt": start_at,
                "maxResults": self.max_results
            }
            response = requests.get(
                url = f"{self.base_url}/rest/api/3/users",
                auth=self.auth,
                params=params)

            users = response.json()

            if not users:
                break
            all_users.extend(users)
            start_at += self.max_results
    
        dataframe_pd = pd.DataFrame(all_users)
        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Rows: {len(dataframe_pd)}")

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))

        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}users",
                    source_dataframe=dataframe_spark,
                    target_column="accountId",
                    source_column="accountId"
                )


        return dataframe_spark
    



    ###################################################
    # Unique
    ###################################################
#######    
    def unique_boards(self):
        """
        """
        # unique_boards = self.boards()['id'].astype(str).unique().tolist()
        unique_boards = self.boards().select('id').distinct().collect()
        return unique_boards

#######    
    def unique_projects(self):
        
        # unique_projects = self.projects()['id'].astype(str).unique().tolist()
        unique_projects = self.projects().select('id').distinct().collect()
        return unique_projects


    def project_versions(self, checking_data=False):
        start_time = time.time()
        all_versions = []

        def fetch_versions(project_id):
            start_at = 0
            is_last = False

            while not is_last:
                params = {
                    'startAt': start_at,
                    'maxResults': self.max_results
                }
                response = requests.get(
                    url=f"{self.base_url}/rest/api/3/project/{project_id}/version",
                    headers=self.headers,
                    auth=self.auth,
                    params=params
                )
                data = response.json()
                sprints_batch = data.get('values', [])
                all_versions.extend(sprints_batch)
                is_last = data.get('isLast', True)
                start_at += len(sprints_batch)

        # Extract project IDs from Row objects
        project_rows = self.unique_projects()
        project_ids = [row['id'] for row in project_rows]

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            list(executor.map(fetch_versions, project_ids))

        dataframe_pd = pd.DataFrame(all_versions)
        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Rows: {len(dataframe_pd)}")
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd = dataframe_pd.drop_duplicates("id")
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}project_versions",
                    source_dataframe=dataframe_spark,
                    target_column="id",
                    source_column="id"
                )


        return dataframe_spark
    
    def sprints(self, checking_data=False):
        start_time = time.time()
        board_rows = self.unique_boards()
        board_ids = [row['id'] for row in board_rows]
        all_sprints = []

        def fetch_sprints_for_board(board_id):
            start_at = 0
            while True:
                url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"
                params = {
                    "startAt": start_at,
                    "maxResults": self.max_results
                }
                response = requests.get(
                    url,
                    headers=self.headers,
                    auth=self.auth,
                    params=params
                )
                if response.status_code != 200:
                    print(f"Error for board {board_id}: {response.status_code}, {response.text}")
                    break
                sprints = response.json()
                if not sprints.get("values"):
                    break
                all_sprints.extend(sprints.get("values", []))
                start_at += self.max_results
                print(f"Board {board_id}. Status code: {response.status_code}, Retrieved {len(sprints.get('values', []))} sprints")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            list(executor.map(fetch_sprints_for_board, board_ids))

        dataframe_pd = pd.DataFrame(all_sprints)

        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Rows: {len(dataframe_pd)}")
        
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd = dataframe_pd.drop_duplicates("id")
        
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}sprints",
                    source_dataframe=dataframe_spark,
                    target_column="id",
                    source_column="id"
                )


        return dataframe_spark

    def issues_projects(self, checking_data=False, days_back=2, project=[], date_from=None, date_to=None):
        start_time = time.time()
        all_issues = []
        errors = []
        lock = Lock()

        if project:
            unique_proj = project
        else:
            project_rows = self.unique_projects()
            unique_proj = [row['id'] for row in project_rows]

        def fetch_project_issues(pid):
            """Fetch all issues for a single project"""
            start_at = 0
            project_issues = []

            if date_from and date_to:
                jql_query = f"project = {pid} AND updated >= '{date_from}' AND updated <= '{date_to}'"
            else:
                jql_query = f"project = {pid} AND updated >= -{days_back}d"

            while True:
                params = {
                    "jql": jql_query,
                    "maxResults": self.max_results,
                    "startAt": start_at,
                    "expand": "versionedRepresentations,renderedFields,transitions,editmeta,changelog",
                    "fields": "*all",
                }

                url = f"{self.base_url}/rest/api/3/search/jql"
                
                try:
                    response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
                    
                    if response.status_code != 200:
                        with lock:
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

                    if len(issues_list) < self.max_results or start_at + self.max_results >= total:
                        break

                    start_at += self.max_results
                        
                except (requests.RequestException, json.JSONDecodeError) as e:
                    with lock:
                        errors.append({"project": pid, "error": str(e)})
                    break
            
            print(f"Project {pid}: fetched {len(project_issues)} issues")
            return project_issues
        
        # Execute in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_project_issues, unique_proj))
        
        # Flatten results
        for result in results:
            all_issues.extend(result)
        
        if not all_issues:
            print("No issues found")
            return pd.DataFrame()
        
        dataframe_pd = pd.DataFrame(all_issues)
        
        # Extract updated date
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
        
        if 'versionedRepresentations' in dataframe_pd.columns:
            dataframe_pd['updated'] = dataframe_pd['versionedRepresentations'].apply(extract_updated)
            dataframe_pd['updated'] = pd.to_datetime(dataframe_pd['updated'], errors='coerce').dt.date
        
        # Convert complex objects to JSON strings
        for col in ['versionedRepresentations', 'renderedFields', 'transitions', 'editmeta', 'changelog']:
            if col in dataframe_pd.columns:
                dataframe_pd[col] = dataframe_pd[col].apply(
                    lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
                )
        
        dataframe_pd.reset_index(drop=True, inplace=True)
        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")
        print(f"Rows: {len(dataframe_pd)}")
        
        if errors:
            print(f"Errors encountered: {len(errors)}")
        
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd = dataframe_pd.drop_duplicates("id")
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}issues_projects",
                    source_dataframe=dataframe_spark,
                    target_column="id",
                    source_column="id"
                )


        return dataframe_spark