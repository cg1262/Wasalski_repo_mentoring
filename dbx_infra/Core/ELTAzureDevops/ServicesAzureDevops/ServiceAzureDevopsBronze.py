import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import json
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import time
from pyspark.sql import SparkSession
from Core.Services.ServiceSaveToDelta import upserting_data


class ServiceBronze:
    """
    Interacting with Azure DevOps API
    """

    def __init__(self, dbutils, spark):
        """
        Initialize Azure DevOps client.

        Args:
            dbutils: Databricks utilities for accessing secrets
            spark: Spark session
        """
        self.spark = spark
        self.dbutils = dbutils

        # Get credentials from secrets
        self.personal_access_token = dbutils.secrets.get(scope="engineering-metrics-keys", key="ado-pat-secret-key")
        self.ado_sub_id = dbutils.secrets.get(scope="engineering-metrics-keys", key="ado-sub-id-secret-key")

        self.organization_name = "Phlexglobal"
        self.auth = HTTPBasicAuth('', self.personal_access_token)
        self.params = {'$top': 5000}
        self.pipelines_number_list = [2441]
        self.sub_id = self.ado_sub_id

        self.catalog_schema = 'engineering_metrics.bronze.'
        self.table_schema = 'azure_devops_'

        # Initialize project_ids
        self.project_ids = [row['id'] for row in self.unique_projects()]

    ###################################################
    # Basic
    ###################################################

    def projects(self, checking_data=None):
        """
        Fetch Azure DevOps projects

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with projects data
        """
        url_projects = f"https://dev.azure.com/{self.organization_name}/_apis/projects?api-version=7.1"

        response_raw = requests.get(url_projects, auth=self.auth, params=self.params)
        response_json = response_raw.json()['value']

        dataframe_pd = pd.DataFrame(response_json)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name=f"{self.table_schema}projects",
                source_dataframe=dataframe_spark,
                target_column="id",
                source_column="id"
            )

        return dataframe_spark

    def pipeline_runs(self, checking_data=None):
        """
        Fetch Azure DevOps pipeline runs with filtering and ranking

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with pipeline runs data
        """
        def extract_between_hashes(text):
            parts = text.split('#')
            if len(parts) >= 4:
                return parts[2]
            return None

        list_to_extend = []
        unique_names, filtered_df = self.unique_pipeline_runs()

        for i in unique_names:
            name_df = filtered_df[filtered_df['issue_key'] == i].copy()

            name_df['rank'] = (name_df.groupby('state')['finishedDate']
                                .rank(method='min', ascending=True))

            succeeded_df = name_df[name_df['result'] == 'succeeded']
            if not succeeded_df.empty:
                min_succeeded_rank = succeeded_df['rank'].min()
                name_df['first_is_succeeded'] = (
                        (name_df['result'] == 'succeeded') &
                        (name_df['rank'] == min_succeeded_rank)
                    )
            else:
                name_df['first_is_succeeded'] = False

            list_to_extend.append(name_df)

        dataframe_pd = pd.concat(list_to_extend, ignore_index=True).drop(columns='templateParameters')
        dataframe_pd['extracted_name_for_issue_key'] = dataframe_pd['name'].apply(extract_between_hashes)

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name=f"{self.table_schema}pipeline_runs",
                source_dataframe=dataframe_spark,
                target_column="id",
                source_column="id"
            )

        return dataframe_spark

    ###################################################
    # Uniques
    ###################################################

    def unique_projects(self):
        """Get unique project IDs"""
        projects_df = self.projects(checking_data=True).select('id').distinct().collect()
        return projects_df

    def unique_pipeline_runs(self):
        """Get unique pipeline runs filtered by PEL"""
        for i in self.pipelines_number_list:
            url = f"https://dev.azure.com/{self.organization_name}/{self.sub_id}/_apis/pipelines/{i}/runs?api-version=7.1"
            response_raw = requests.get(url, auth=self.auth, params=self.params)
            response_json = response_raw.json()
            df = pd.DataFrame(response_json['value'])

            dataframe_pd = df[df['name'].str.contains('PEL', case=False, na=False)].copy()
            dataframe_pd['issue_key'] = dataframe_pd['name'].astype(str).str.split('#').str[1]
            dataframe_pd['env'] = dataframe_pd['name'].astype(str).str.split('#').str[-1]
            unique_names = dataframe_pd['issue_key'].unique().tolist()

        return unique_names, dataframe_pd

    ###################################################
    # Loops
    ###################################################

    def approvals(self, checking_data=None):
        """
        Fetch Azure DevOps pipeline approvals

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with approvals data
        """
        list_to_extend = []

        for i in self.project_ids:
            url_approvals = (
                f"https://dev.azure.com/{self.organization_name}/{i}/_apis/pipelines/approvals?api-version=7.1"
            )
            response_raw = requests.get(url_approvals, auth=self.auth, params=self.params)
            response_json = response_raw.json()['value']
            list_to_extend.extend(response_json)

        dataframe_pd = pd.DataFrame(list_to_extend)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name=f"{self.table_schema}approvals",
                source_dataframe=dataframe_spark,
                target_column="id",
                source_column="id"
            )

        return dataframe_spark

    def repos(self, checking_data=None):
        """
        Fetch Azure DevOps repositories

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with repositories data
        """
        list_to_extend = []

        for i in self.project_ids:
            url_repos = f"https://dev.azure.com/{self.organization_name}/{i}/_apis/git/repositories?api-version=4.1"
            response_raw = requests.get(url_repos, auth=self.auth, params=self.params)
            response_json = response_raw.json()['value']
            list_to_extend.extend(response_json)

        dataframe_pd = pd.DataFrame(list_to_extend)
        dataframe_pd['proj_id'] = dataframe_pd['project'].apply(lambda x: x['id'])
        dataframe_pd['project_name'] = dataframe_pd['project'].apply(lambda x: x['name'])
        dataframe_pd['upsert_column'] = dataframe_pd['project_name'] + '_' + dataframe_pd['id']
        dataframe_pd = dataframe_pd.drop(columns=['project'])

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name=f"{self.table_schema}repos",
                source_dataframe=dataframe_spark,
                target_column="upsert_column",
                source_column="upsert_column"
            )

        return dataframe_spark

    def definitions(self, checking_data=None):
        """
        Fetch Azure DevOps build definitions using parallel processing

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with definitions data
        """
        list_to_extend = []

        def fetch_definitions(project):
            url_definitions = f"https://dev.azure.com/{self.organization_name}/{project}/_apis/build/definitions?api-version=7.1"
            response_raw = requests.get(url_definitions, auth=self.auth, params=self.params)
            response_json = response_raw.json()['value']
            return response_json

        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_definitions, self.project_ids))

        # Flatten the list of lists
        for result in results:
            list_to_extend.extend(result)

        dataframe_pd = pd.DataFrame(list_to_extend)
        dataframe_pd['projectId'] = dataframe_pd['project'].apply(lambda x: x['id'])
        dataframe_pd['projectName'] = dataframe_pd['project'].apply(lambda x: x['name'])

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name=f"{self.table_schema}definitions",
                source_dataframe=dataframe_spark,
                target_column="id",
                source_column="id"
            )

        return dataframe_spark

    def pipelines(self, checking_data=None):
        """
        Fetch Azure DevOps pipelines

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with pipelines data
        """
        list_to_extend = []

        for i in self.project_ids:
            url_pipelines = (
                f"https://dev.azure.com/{self.organization_name}/{i}/_apis/pipelines?api-version=7.1"
            )
            response_raw = requests.get(
                url_pipelines,
                auth=self.auth,
                params=self.params
            )
            response_json = response_raw.json()['value']

            for pipeline in response_json:
                pipeline['project_id'] = i

            list_to_extend.extend(response_json)

        dataframe_pd = pd.DataFrame(list_to_extend)

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name=f"{self.table_schema}pipelines",
                source_dataframe=dataframe_spark,
                target_column="ID",
                source_column="ID"
            )

        return dataframe_spark

    def source_providers(self, checking_data=None):
        """
        Fetch Azure DevOps source providers using parallel processing

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with source providers data
        """
        list_to_extend = []

        def fetch_source_providers(project):
            url_src_providers = f"https://dev.azure.com/{self.organization_name}/{project}/_apis/sourceproviders?api-version=7.1"
            response_raw = requests.get(url_src_providers, auth=self.auth, params=self.params)
            response_json = response_raw.json()['value']
            return response_json

        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_source_providers, self.project_ids))

        # Flatten the list of lists
        for result in results:
            list_to_extend.extend(result)

        dataframe_pd = pd.DataFrame(list_to_extend)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd['upsert_key'] = dataframe_pd['name'] + dataframe_pd['supportedTriggers'] + dataframe_pd['supportedCapabilities']
        dataframe_pd['upsert_key'] = dataframe_pd['upsert_key'].drop_duplicates()
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name=f"{self.table_schema}source_providers",
                source_dataframe=dataframe_spark,
                target_column="upsert_key",
                source_column="upsert_key"
            )

        return dataframe_spark

    def builds(self, checking_data=None, test_one_build=None):
        """
        Fetch Azure DevOps builds for yesterday from all repositories
        """
        # Time range setup (used in both if and else)
        yesterday = datetime.now() - timedelta(days=1)
        min_time = yesterday.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        max_time = yesterday.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Get all repos
        repos_df = self.repos(checking_data=True).select('id', 'project_name').collect()
        
        all_builds = []
        
        if test_one_build == True:
            # Hardcoded test values
            project_name = '123'
            repo_id = '123'
            
            base_url = f"https://dev.azure.com/{self.organization_name}/{project_name}/_apis/build/builds"
            params = {
                "repositoryId": repo_id,
                "minTime": min_time,
                "maxTime": max_time,
                "repositoryType": "TfsGit",
                "api-version": "7.1"
            }
            
            response = requests.get(
                f"{base_url}?{urlencode(params)}",
                headers={"Accept": "application/json"},
                auth=HTTPBasicAuth("", self.personal_access_token)
            )
            
            parsed_data = response.json()['value']
            return pd.DataFrame(parsed_data)
        
        else:
            # Iterate through repos from dataframe
            for row in repos_df:
                project_name = row['project_name']
                repo_id = row['id']
                
                base_url = f"https://dev.azure.com/{self.organization_name}/{project_name}/_apis/build/builds"
                params = {
                    "repositoryId": repo_id,
                    "minTime": min_time,
                    "maxTime": max_time,
                    "repositoryType": "TfsGit",
                    "api-version": "7.1"
                }
                
                try:
                    response = requests.get(
                        f"{base_url}?{urlencode(params)}",
                        headers={"Accept": "application/json"},
                        auth=HTTPBasicAuth("", self.personal_access_token)
                    )
                    
                    if response.status_code == 200:
                        builds = response.json().get('value', [])
                        for build in builds:
                            build['project_name'] = project_name
                            build['repo_id'] = repo_id
                        all_builds.extend(builds)
                    print(f"Fetched {project_name}/{repo_id}")      

                except Exception as e:
                    print(f"Error fetching builds for {project_name}/{repo_id}: {e}")
                    continue
            
            # Convert all builds to DataFrame
            dataframe_pd = pd.DataFrame(all_builds)
            return dataframe_pd

    
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)
        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}builds",
                    source_dataframe=dataframe_spark,
                    target_column="id",
                    source_column="id"
                )

        return dataframe_spark

    def pull_requests(self, checking_data=None):
        """
        Fetch Azure DevOps pull requests from 2024 to now for all repositories

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with pull requests data
        """
        # Time range setup (used in both if and else)
        yesterday = datetime.now() - timedelta(days=1)
        min_time = yesterday.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        max_time = yesterday.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%dT%H:%M:%SZ")
        utc_now = datetime.utcnow()
        

        # Get all repos to fetch PRs for
        repos_df = self.repos(checking_data=True).select('id', 'project_name').collect()

        all_prs = []


        for repo_row in repos_df:
            repo_id = repo_row['id']
            project_name = repo_row['project_name']
            base_url = f"https://dev.azure.com/{self.organization_name}/{project_name}/_apis/git/repositories/{repo_id}/pullrequests?searchCriteria.status=all&searchCriteria.minTime={min_time}&earchCriteria.maxTime={max_time}&searchCriteria.timeRangeType=created&api-version=7.1"
            # # Parse project dict if it's a string
            # if isinstance(project_name, str):
            #     try:
            #         project_dict = json.loads(project_name)
            #         project_name = project_dict.get('project_name', project_name)
            #     except:
            #         pass

            try:
                response = requests.get(
                    base_url,
                    headers={"Accept": "application/json"},
                    auth=HTTPBasicAuth("", self.personal_access_token)
                )
                
                if response.status_code == 200:
                    builds = response.json().get('value', [])
                    for build in builds:
                        build['project_name'] = project_name
                        build['repo_id'] = repo_id
                    all_prs.extend(builds)
                    print(f"Checked {project_name}/{repo_id}")      

            except Exception as e:
                    print(f"Error fetching builds for {project_name}/{repo_id}: {e}")
                    continue
            
            # Convert all builds to DataFrame
        
        dataframe_pd = pd.DataFrame(all_prs)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd['upsert_column'] = dataframe_pd['pullRequestId'] +  '_' + dataframe_pd['codeReviewId'] +  '_' + dataframe_pd['repo_id']
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)
        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}pull_requests",
                    source_dataframe=dataframe_spark,
                    target_column="upsert_column",
                    source_column="upsert_column"
                )

        return dataframe_spark

    def branches(self, checking_data=None):
        """
        Fetch Azure DevOps branches for all repositories using parallel processing

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with branches data
        """
        # Get all repos and projects
        repos_df = self.repos(checking_data=True).select('id', 'project_name').collect()

        def fetch_branches(repo_row):
            repo_id = repo_row['id']
            project_name = repo_row['project_name']

            # Parse project dict if it's a string
            if isinstance(project_name, str):
                try:
                    project_dict = json.loads(project_name)
                    project_name = project_dict.get('project_name', project_name)
                except:
                    pass

            url = f"https://dev.azure.com/{self.organization_name}/{project_name}/_apis/sourceProviders/TfsGit/branches"
            params = {
                "repository": repo_id,
                "api-version": "7.1"
            }

            try:
                response = requests.get(url, auth=self.auth, params=params)
                if response.status_code == 200:
                    branches_data = response.json()
                    if 'value' in branches_data and isinstance(branches_data['value'], list):
                        return [
                            {
                                'repository_id': repo_id,
                                'project_name': project_name,
                                'branch_name': branch.replace('refs/heads/', ''),
                                'branch_full_name': branch
                            }
                            for branch in branches_data['value']
                        ]
            except Exception as e:
                print(f"Error fetching branches for repo {repo_id}: {str(e)}")
            return []

        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_branches, repos_df))

        # Flatten the list of lists
        all_branches = []
        for result in results:
            all_branches.extend(result)

        if all_branches:
            dataframe_pd = pd.DataFrame(all_branches)
            dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
            dataframe_pd['upsert_column'] = dataframe_pd['repository_id'] +  '_' + dataframe_pd['branch_name'] +  '_' + dataframe_pd['project_name']
            dataframe_spark = self.spark.createDataFrame(dataframe_pd)

            if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}branches",
                    source_dataframe=dataframe_spark,
                    target_column="upsert_column",
                    source_column="upsert_column"
                )

            return dataframe_spark
        else:
            # Return empty dataframe if no branches found
            return self.spark.createDataFrame([], schema="branch_name STRING")

    def commits(self, checking_data=None):
        """
        Fetch Azure DevOps commits for all branches using parallel processing with retry logic

        Args:
            checking_data: If True, skip saving to Delta table

        Returns:
            DataFrame: Spark DataFrame with commits data
        """
        # Get all branches
        branches_df = self.branches(checking_data=True).select('repository_id', 'branch_name', 'project_name').collect()

        def fetch_commits_with_retry(branch_row):
            repo_id = branch_row['repository_id']
            branch_name = branch_row['branch_name']
            project_name = branch_row['project_name']

            url = f"https://dev.azure.com/{self.organization_name}/_apis/git/repositories/{repo_id}/commits?searchCriteria.itemVersion.version={branch_name}&api-version=7.1"
    

            retries = 3
            backoff_factor = 2

            for attempt in range(retries):
                try:
                    response = requests.get(url, auth=self.auth)

                    commits_data = response.json()
                    commits = commits_data.get("value", [])

                    # Add context to each commit
                    for commit in commits:
                        commit['repository_id'] = repo_id
                        commit['branch_name'] = branch_name
                        commit['project_name'] = project_name

                    return commits

                except requests.exceptions.RequestException as e:
                    if attempt < retries - 1:
                        time.sleep(backoff_factor ** attempt)
                    else:
                        print(f"Error fetching commits for repo {repo_id}, branch {branch_name}: {str(e)}")
                        return []

            return []

        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_commits_with_retry, branches_df))

        # Flatten the list of lists
        all_commits = []
        for result in results:
            all_commits.extend(result)

        if all_commits:
            dataframe_pd = pd.DataFrame(all_commits)
            dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
            dataframe_pd['upsert_column'] = dataframe_pd['commitId'] + '_' + dataframe_pd['repository_id'] + '_' + dataframe_pd['branch_name']  
            dataframe_spark = self.spark.createDataFrame(dataframe_pd)

            if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}commits",
                    source_dataframe=dataframe_spark,
                    target_column="upsert_column",
                    source_column="upsert_column"
                )

            return dataframe_spark
        else:
            # Return empty dataframe if no commits found
            return self.spark.createDataFrame([], schema="commitId STRING")
