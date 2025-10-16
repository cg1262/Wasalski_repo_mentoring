# in config file password are being stored, to be changed after deployment to databricks
from config import personal_access_token, ado_sub_id_secret

import requests
import pandas as pd
from requests.auth import HTTPBasicAuth 
import json
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor

class ServiceBronze():

    ###################################################
    # Init
    ###################################################
#######       
    def __init__(self):
        self.organization_name = "Phlexglobal"
        self.personal_access_token = personal_access_token
        self.auth = HTTPBasicAuth('', self.personal_access_token)
        self.params = {'$top': 5000}
        self.pipelines = 2441
        self.sub_id = ado_sub_id_secret
        self.unique_projects = self.get_unique_projects()
        self.unique_pipeline_runs = self.get_unique_pipeline_runs()

    ###################################################
    # Basic
    ###################################################
#######    
    def get_ado_projects(self): 
        url_projects = f"https://dev.azure.com/Phlexglobal/_apis/projects?api-version=7.1"
        
        response = requests.get(url_projects, auth=self.auth, params = self.params)
        
        resp = response.json()['value']
        df_projects = pd.DataFrame(resp)
        unique_ids = df_projects['id'] .astype(str).unique().tolist()
        
        new_order = ['id', 'url', 'name', 'state', 'revision', 'visibility', 'description', 'lastUpdateTime']
        df_projects = df_projects[new_order]
        
        df_projects.columns = ['ID', 'URL', 'NAME', 'STATE', 'REVISION', 'VISIBILITY',  'DESCRIPTION', 'LASTUPDATETIME']
        return df_projects

#######     

    def get_pipeline_runs(self):
      
        url = f"https://dev.azure.com/Phlexglobal/{self.sub_id}/_apis/pipelines/{self.pipelines}/runs?api-version=7.1"
        response = requests.get(url, auth=self.auth, params=self.params)
        
        resp = response.json()
        
        df = pd.DataFrame(resp['value']) 
        
        # Filter by name containing 'PEL'
        filtered_df = df[df['name'].str.contains('PEL', case=False, na=False)].copy()
        filtered_df['issue_key'] = filtered_df['name'].astype(str).str.split('#').str[1]
        filtered_df['env'] = filtered_df['name'].astype(str).str.split('#').str[-1]
            
        return filtered_df
#######  

    ###################################################
    # Uniques
    ###################################################
#######    

    def get_unique_projects(self):
        unique_ids = self.get_ado_projects()['ID'].astype(str).unique().tolist()
        return unique_ids
        
#######  
    def get_unique_pipeline_runs(self):
        unique_names = self.get_pipeline_runs()['issue_key'].astype(str).unique().tolist()
        return unique_names



    ###################################################
    # Loops
    ###################################################
####### 

    def get_ado_approvals(self): 
    
        url_projects = f"https://dev.azure.com/Phlexglobal/_apis/projects?api-version=7.1"  
    
        approvals = []
    
        def unique_projects(unique_projects):
            url_approvals = f"https://dev.azure.com/Phlexglobal/{unique_projects}/_apis/pipelines/approvals?api-version=7.1"
            response = requests.get(url_approvals, auth=self.auth, params = self.params)
            resp = response.json()['value']
            approvals.extend(resp)
    
        with ThreadPoolExecutor(max_workers=15) as executor:
            runs_list = list(executor.map(unique_projects, self.unique_projects))

        df_approvals = pd.DataFrame(approvals)
    
        return df_approvals
    
# ########################### 

    def get_ado_definitions(self): 

        def fetch_definitions(project):
            url_definitions = f"https://dev.azure.com/Phlexglobal/{project}/_apis/build/definitions?api-version=7.1"
            response = requests.get(url_definitions, auth=self.auth, params=self.params)
            return response.json()['value']

        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_definitions, self.unique_projects))

        definitions = [item for sublist in results for item in sublist]

        df_definitions = pd.DataFrame(definitions)
        df_definitions['PROJECTID'] = df_definitions['project'].apply(lambda x: x['id'])
        df_definitions['PROJECTNAME'] = df_definitions['project'].apply(lambda x: x['name'])

        return df_definitions

# ########################### 

    def get_ado_pipelines(self):
        
        def fetch_pipelines(project):
            url_pipelines = f"https://dev.azure.com/Phlexglobal/{project}/_apis/pipelines?api-version=7.1"
            response = requests.get(url_pipelines, auth=self.auth, params=self.params)
            resp = response.json()['value']
            
            # Add project_id to each pipeline
            for pipeline in resp:
                pipeline['project_id'] = project
            
            return resp
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_pipelines, self.unique_projects))
        
        # Flatten the list of lists
        pipelines = [item for sublist in results for item in sublist]
        
        df_pipelines = pd.DataFrame(pipelines)
        
        return df_pipelines


# ########################### 

    def get_ado_source_providers(self):
        
        def fetch_source_providers(project):
            url_src_providers = f"https://dev.azure.com/Phlexglobal/{project}/_apis/sourceproviders?api-version=7.1"
            response = requests.get(url_src_providers, auth=self.auth, params=self.params)
            return response.json()['value']
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_source_providers, self.unique_projects))
        
        # Flatten the list of lists
        src_providers = [item for sublist in results for item in sublist]
        
        df_source_providers = pd.DataFrame(src_providers)
        
        return df_source_providers
# ########################### 
    def get_ado_repos(self):

        repos = []
        for i in self.get_unique_projects():
            url_repos =f"https://dev.azure.com/PhlexGlobal/{i}/_apis/git/repositories?api-version=4.1"
            response = requests.get(url_repos,auth=self.auth, params=self.params)
            resp = response.json()['value']
            repos.extend(resp)
        df_repos = pd.DataFrame(repos)
      
        df_repos['proj_id'] = df_repos['project'].apply(lambda x: x['id'])
    
        return df_repos


# ########################### 
   
    def get_ado_definitions(self): 
    
        def fetch_definitions(project):
            url_definitions = f"https://dev.azure.com/Phlexglobal/{project}/_apis/build/definitions?api-version=7.1"
            response = requests.get(url_definitions, auth=self.auth, params=self.params)
            return response.json()['value']
    
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_definitions, self.unique_projects))
        
        # Flatten the list of lists
        definitions = [item for sublist in results for item in sublist]
        
        df_definitions = pd.DataFrame(definitions)
        
        df_definitions['projectId'] = df_definitions['project'].apply(lambda x: x['id'])
        df_definitions['projectName'] = df_definitions['project'].apply(lambda x: x['name'])
        
        return df_definitions

# ########################### 
    def get_ado_pipelines(self):
    
        def fetch_pipelines(project):
            url_pipelines = f"https://dev.azure.com/Phlexglobal/{project}/_apis/pipelines?api-version=7.1"
            response = requests.get(url_pipelines, auth=self.auth, params=self.params)
            resp = response.json()['value']
            
            # Add project_id to each pipeline
            for pipeline in resp:
                pipeline['project_id'] = project
            
            return resp
    
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_pipelines, self.unique_projects))
        
        # Flatten the list of lists
        pipelines = [item for sublist in results for item in sublist]
        
        df_pipelines = pd.DataFrame(pipelines)
        
        return df_pipelines
# ########################### 
    def get_ado_source_providers(self):
        
        def fetch_source_providers(project):
            url_src_providers = f"https://dev.azure.com/Phlexglobal/{project}/_apis/sourceproviders?api-version=7.1"
            response = requests.get(url_src_providers, auth=self.auth, params=self.params)
            return response.json()['value']
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(fetch_source_providers, self.get_unique_projects()))
        
        # Flatten the list of lists
        src_providers = [item for sublist in results for item in sublist]
        
        df_source_providers = pd.DataFrame(src_providers)
        
        return df_source_providers

# ########################### 
#     def get_pipeline_runs_2(self):

#         def extract_between_hashes(text):
#             parts = text.split('#')
#             if len(parts) >= 4:  # Ensuring we have at least three # separators
#                 return parts[2]  # Index 2 is between 2nd and 3rd #
#             return None
    
#         runs = []
        
#         unique_names, filtered_df = self.get_unique_pipeline_runs()
        
#         for i in unique_names:  # iterate over unique_names
#             name_df = filtered_df[filtered_df['issue_key'] == i].copy()
            
#             name_df['rank'] = (name_df.groupby('state')['finishedDate']
#                                 .rank(method='min', ascending=True))
        
#             succeeded_df = name_df[name_df['result'] == 'succeeded']
#             if not succeeded_df.empty:
#                 min_succeeded_rank = succeeded_df['rank'].min()
#                 name_df['first_is_succeeded'] = (
#                         (name_df['result'] == 'succeeded') & 
#                         (name_df['rank'] == min_succeeded_rank)
#                     )
#             else:
#                     name_df['first_is_succeeded'] = False
                
#             runs.append(name_df)
        
       
#         final_df = pd.concat(runs, ignore_index=True).drop(columns='templateParameters')

#         final_df['extracted_name_for_issue_key'] = final_df['name'].apply(extract_between_hashes)
#         return final_df
      
#     def get_pipeline_runs_parallel(self):

#         def extract_between_hashes(text):
#             parts = text.split('#')
#             if len(parts) >= 4:  # Ensuring we have at least three # separators
#                 return parts[2]  # Index 2 is between 2nd and 3rd #
#             return None
    
#         runs = []
        
#         unique_names, filtered_df = self.get_unique_pipeline_runs()
        
#         for i in unique_names:  # iterate over unique_names
#             name_df = filtered_df[filtered_df['issue_key'] == i].copy()
            
#             name_df['rank'] = (name_df.groupby('state')['finishedDate']
#                                 .rank(method='min', ascending=True))
        
#             succeeded_df = name_df[name_df['result'] == 'succeeded']
#             if not succeeded_df.empty:
#                 min_succeeded_rank = succeeded_df['rank'].min()
#                 name_df['first_is_succeeded'] = (
#                         (name_df['result'] == 'succeeded') & 
#                         (name_df['rank'] == min_succeeded_rank)
#                     )
#             else:
#                     name_df['first_is_succeeded'] = False
                
#             runs.append(name_df)
        
       
#         final_df = pd.concat(runs, ignore_index=True).drop(columns='templateParameters')



#         final_df['extracted_name_for_issue_key'] = final_df['name'].apply(extract_between_hashes)
#         return final_df
    
# ########################### 
#     def get_builds_handler(PROJECT_NAME, REPO_ID):
#         # Define the variables
#         api_version = "7.1"


#         yesterday = datetime.now() - timedelta(days=1)
#         yesterday_year = yesterday.year
#         yesterday_month = yesterday.month
#         yesterday_day_no = yesterday.day
        
#         min_time = datetime(yesterday_year, yesterday_month, yesterday_day_no, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")  # Start date
#         max_time = datetime(yesterday_year, yesterday_month, yesterday_day_no, 23, 59, 59).strftime("%Y-%m-%dT%H:%M:%SZ")  # End date



#         # Base URL
#         base_url = f"https://dev.azure.com/phlexglobal/{PROJECT_NAME}/_apis/build/builds"
#         params = {
#             "repositoryId": REPO_ID,
#             "minTime": min_time,
#             "maxTime": max_time,
#             "repositoryType": "TfsGit",
#             "api-version": api_version
#         }
#         url = f"{base_url}?{urlencode(params)}"

#         # Headers
#         headers = {
#             "Accept": "application/json"
#         }
        
#         # Make GET request
#         response = requests.get(
#             url,
#             headers=headers,
#             auth=HTTPBasicAuth("", pat)
#         )

#         try:
#             parsed_data = response.json()
#             value = parsed_data.get("value", [])
#             count = parsed_data.get("count", 0)
#             builds = []
        
#             for build in value:
#                 parsed_build = {
#                     "URI": build.get("uri"),
#                     "URL": build.get("url"),
#                     "LOGS": build.get("logs"),
#                     "TAGS": build.get("tags", []),
#                     "PLANS": build.get("plans", []),
#                     "QUEUE": build.get("queue"),
#                     "_LINKS": build.get("_links"),
#                     "REASON": build.get("reason"),
#                     "RESULT": build.get("result"),
#                     "STATUS": build.get("status"),
#                     "PROJECT": build.get("project"),
#                     "PRIORITY": build.get("priority"),
#                     "QUEUETIME": build.get("queueTime"),
#                     "STARTTIME": build.get("startTime"),
#                     "DEFINITION": build.get("definition"),
#                     "FINISHTIME": build.get("finishTime"),
#                     "PARAMETERS": None,  # This field is missing in JSON; set to None
#                     "PROPERTIES": build.get("properties"),
#                     "REPOSITORY": build.get("repository"),
#                     "BUILDNUMBER": build.get("buildNumber"),
#                     "REQUESTEDBY": build.get("requestedBy"),
#                     "TRIGGERINFO": build.get("triggerInfo"),
#                     "REQUESTEDFOR": build.get("requestedFor"),
#                     "SOURCEBRANCH": build.get("sourceBranch"),
#                     "LASTCHANGEDBY": build.get("lastChangedBy"),
#                     "SOURCEVERSION": build.get("sourceVersion"),
#                     "LASTCHANGEDDATE": build.get("lastChangedDate"),
#                     "ORCHESTRATIONPLAN": build.get("orchestrationPlan"),
#                     "RETAINEDBYRELEASE": build.get("retainedByRelease"),
#                     "VALIDATIONRESULTS": build.get("validationResults", []),
#                     "TEMPLATEPARAMETERS": build.get("templateParameters"),
#                     "BUILDNUMBERREVISION": build.get("buildNumberRevision"),
#                     "APPENDCOMMITMESSAGETORUNNAME": build.get("appendCommitMessageToRunName"),
#                 }
                
#                 builds.append(parsed_build)
            
#             return {"count": count, "builds": builds}  # Fix the unhashable type issue

#         except Exception as e:
#             return {"error": str(e)}


#     def get_builds_handler_parallel(PROJECT_NAME, REPO_ID):
#         # Define the variables
#         api_version = "7.1"


#         yesterday = datetime.now() - timedelta(days=1)
#         yesterday_year = yesterday.year
#         yesterday_month = yesterday.month
#         yesterday_day_no = yesterday.day
        
#         min_time = datetime(yesterday_year, yesterday_month, yesterday_day_no, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")  # Start date
#         max_time = datetime(yesterday_year, yesterday_month, yesterday_day_no, 23, 59, 59).strftime("%Y-%m-%dT%H:%M:%SZ")  # End date



#         # Base URL
#         base_url = f"https://dev.azure.com/phlexglobal/{PROJECT_NAME}/_apis/build/builds"
#         params = {
#             "repositoryId": REPO_ID,
#             "minTime": min_time,
#             "maxTime": max_time,
#             "repositoryType": "TfsGit",
#             "api-version": api_version
#         }
#         url = f"{base_url}?{urlencode(params)}"

#         # Headers
#         headers = {
#             "Accept": "application/json"
#         }
        
#         # Make GET request
#         response = requests.get(
#             url,
#             headers=headers,
#             auth=HTTPBasicAuth("", pat)
#         )

#         try:
#             parsed_data = response.json()
#             value = parsed_data.get("value", [])
#             count = parsed_data.get("count", 0)
#             builds = []
        
#             for build in value:
#                 parsed_build = {
#                     "URI": build.get("uri"),
#                     "URL": build.get("url"),
#                     "LOGS": build.get("logs"),
#                     "TAGS": build.get("tags", []),
#                     "PLANS": build.get("plans", []),
#                     "QUEUE": build.get("queue"),
#                     "_LINKS": build.get("_links"),
#                     "REASON": build.get("reason"),
#                     "RESULT": build.get("result"),
#                     "STATUS": build.get("status"),
#                     "PROJECT": build.get("project"),
#                     "PRIORITY": build.get("priority"),
#                     "QUEUETIME": build.get("queueTime"),
#                     "STARTTIME": build.get("startTime"),
#                     "DEFINITION": build.get("definition"),
#                     "FINISHTIME": build.get("finishTime"),
#                     "PARAMETERS": None,  # This field is missing in JSON; set to None
#                     "PROPERTIES": build.get("properties"),
#                     "REPOSITORY": build.get("repository"),
#                     "BUILDNUMBER": build.get("buildNumber"),
#                     "REQUESTEDBY": build.get("requestedBy"),
#                     "TRIGGERINFO": build.get("triggerInfo"),
#                     "REQUESTEDFOR": build.get("requestedFor"),
#                     "SOURCEBRANCH": build.get("sourceBranch"),
#                     "LASTCHANGEDBY": build.get("lastChangedBy"),
#                     "SOURCEVERSION": build.get("sourceVersion"),
#                     "LASTCHANGEDDATE": build.get("lastChangedDate"),
#                     "ORCHESTRATIONPLAN": build.get("orchestrationPlan"),
#                     "RETAINEDBYRELEASE": build.get("retainedByRelease"),
#                     "VALIDATIONRESULTS": build.get("validationResults", []),
#                     "TEMPLATEPARAMETERS": build.get("templateParameters"),
#                     "BUILDNUMBERREVISION": build.get("buildNumberRevision"),
#                     "APPENDCOMMITMESSAGETORUNNAME": build.get("appendCommitMessageToRunName"),
#                 }
                
#                 builds.append(parsed_build)
            
#             return {"count": count, "builds": builds}  # Fix the unhashable type issue

#         except Exception as e:
#             return {"error": str(e)}


# ############################ 
#     def get_pull_request_handler(PROJECT_NAME, REPO_ID):
#         # Define the variables
#         api_version = "7.1"
#         pat = _snowflake.get_generic_secret_string('pat')
#         # Get yesterday's date
#         yesterday = datetime.utcnow() - timedelta(days=14)
#         min_time = yesterday.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")
#         max_time = yesterday.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%dT%H:%M:%SZ")
#         year_2024 = datetime(2024, 1, 1).strftime("%Y-%m-%dT%H:%M:%SZ")
#         utc_now = datetime.utcnow()
#         utc_now_min = utc_now - timedelta(days=14)
        
#         base_url = f"https://dev.azure.com/phlexglobal/{PROJECT_NAME}/_apis/git/repositories/{REPO_ID}/pullrequests?searchCriteria.status=all&searchCriteria.minTime={year_2024}&searchCriteria.maxTime={utc_now}&searchCriteria.timeRangeType=created&api-version=7.1"

#         # Retrieve the PAT securely from Snowflake secrets
#         # pat = _snowflake.get_generic_secret_string('pat')
        
#         # Headers
#         headers = {
#             "Accept": "application/json"
#         }
        
#         # Make GET request
#         response = requests.get(
#             base_url,
#             headers=headers,
#             auth=HTTPBasicAuth("", pat)
#         )

#         try:
#             parsed_data = response.json()
#             count = parsed_data.get("count", 0)
#             value = parsed_data.get("value", [])
            
#             flattened_prs = []
#             for pr in value:
#                 flat_pr = {
#                     'repository': pr.get('repository', {}),
#                     'pullRequestId': pr.get('pullRequestId'),
#                     'codeReviewId': pr.get('codeReviewId'),
#                     'status': pr.get('status'),
#                     'createdBy': pr.get('createdBy', {}),
#                     'creationDate': pr.get('creationDate'),
#                     'closedDate': pr.get('closedDate'),
#                     'title': pr.get('title'),
#                     'description': pr.get('description'),
#                     'sourceRefName': pr.get('sourceRefName'),
#                     'targetRefName': pr.get('targetRefName'),
#                     'mergeStatus': pr.get('mergeStatus'),
#                     'isDraft': pr.get('isDraft'),
#                     'mergeId': pr.get('mergeId'),
#                     'lastMergeSourceCommit': pr.get('lastMergeSourceCommit', {}),
#                     'lastMergeTargetCommit': pr.get('lastMergeTargetCommit', {}),
#                     'lastMergeCommit': pr.get('lastMergeCommit', {}),
#                     'reviewers': pr.get('reviewers', []),
#                     'url': pr.get('url'),
#                     'completionOptions': pr.get('completionOptions', {}),
#                     'supportsIterations': pr.get('supportsIterations')
#                 }
#                 flattened_prs.append(flat_pr)
            
#             return {"count": count, "pullRequests": flattened_prs}

#         except Exception as e:
#             return {"error": str(e)}

#     def get_pull_request_handler_parallel(PROJECT_NAME, REPO_ID):
#         # Define the variables
#         api_version = "7.1"
#         pat = _snowflake.get_generic_secret_string('pat')
#         # Get yesterday's date
#         yesterday = datetime.utcnow() - timedelta(days=14)
#         min_time = yesterday.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")
#         max_time = yesterday.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%dT%H:%M:%SZ")
#         year_2024 = datetime(2024, 1, 1).strftime("%Y-%m-%dT%H:%M:%SZ")
#         utc_now = datetime.utcnow()
#         utc_now_min = utc_now - timedelta(days=14)
        
#         base_url = f"https://dev.azure.com/phlexglobal/{PROJECT_NAME}/_apis/git/repositories/{REPO_ID}/pullrequests?searchCriteria.status=all&searchCriteria.minTime={year_2024}&searchCriteria.maxTime={utc_now}&searchCriteria.timeRangeType=created&api-version=7.1"

#         # Retrieve the PAT securely from Snowflake secrets
#         # pat = _snowflake.get_generic_secret_string('pat')
        
#         # Headers
#         headers = {
#             "Accept": "application/json"
#         }
        
#         # Make GET request
#         response = requests.get(
#             base_url,
#             headers=headers,
#             auth=HTTPBasicAuth("", pat)
#         )

#         try:
#             parsed_data = response.json()
#             count = parsed_data.get("count", 0)
#             value = parsed_data.get("value", [])
            
#             flattened_prs = []
#             for pr in value:
#                 flat_pr = {
#                     'repository': pr.get('repository', {}),
#                     'pullRequestId': pr.get('pullRequestId'),
#                     'codeReviewId': pr.get('codeReviewId'),
#                     'status': pr.get('status'),
#                     'createdBy': pr.get('createdBy', {}),
#                     'creationDate': pr.get('creationDate'),
#                     'closedDate': pr.get('closedDate'),
#                     'title': pr.get('title'),
#                     'description': pr.get('description'),
#                     'sourceRefName': pr.get('sourceRefName'),
#                     'targetRefName': pr.get('targetRefName'),
#                     'mergeStatus': pr.get('mergeStatus'),
#                     'isDraft': pr.get('isDraft'),
#                     'mergeId': pr.get('mergeId'),
#                     'lastMergeSourceCommit': pr.get('lastMergeSourceCommit', {}),
#                     'lastMergeTargetCommit': pr.get('lastMergeTargetCommit', {}),
#                     'lastMergeCommit': pr.get('lastMergeCommit', {}),
#                     'reviewers': pr.get('reviewers', []),
#                     'url': pr.get('url'),
#                     'completionOptions': pr.get('completionOptions', {}),
#                     'supportsIterations': pr.get('supportsIterations')
#                 }
#                 flattened_prs.append(flat_pr)
            
#             return {"count": count, "pullRequests": flattened_prs}

#         except Exception as e:
#             return {"error": str(e)}
        


# ######################### 
#     def get_branches_handler(project, repo):
#         # API URL
#         url = f"https://dev.azure.com/phlexglobal/{project}/_apis/sourceProviders/TfsGit/branches?repository={repo}&api-version=7.1"
#         # Retrieve PAT securely from Snowflake secrets
#         pat = _snowflake.get_generic_secret_string('pat')

#         # Headers
#         headers = {
#             "Accept": "application/json"
#         }

#         # Make the GET request
#         response = requests.get(url, headers=headers, auth=HTTPBasicAuth("", pat))

#         # Handle response
#         if response.status_code == 200:
#             branches = response.json()

#             # Ensure 'value' exists and is a list
#             if 'value' in branches and isinstance(branches['value'], list):
#                 # Extract branch names and remove 'refs/heads/' prefix
#                 branches_name = [i.replace('refs/heads/', '') for i in branches['value']]
#                 return branches_name
#             else:
#                 # Handle unexpected API structure
#                 return [f"Unexpected response format: {branches}"]
#         else:
#             # Handle API errors
#             return [f"Error: {response.status_code}, {response.text}"]
        
#     def get_branches_handler_parallel(project, repo):
#         # API URL
#         url = f"https://dev.azure.com/phlexglobal/{project}/_apis/sourceProviders/TfsGit/branches?repository={repo}&api-version=7.1"
#         # Retrieve PAT securely from Snowflake secrets
#         pat = _snowflake.get_generic_secret_string('pat')

#         # Headers
#         headers = {
#             "Accept": "application/json"
#         }

#         # Make the GET request
#         response = requests.get(url, headers=headers, auth=HTTPBasicAuth("", pat))

#         # Handle response
#         if response.status_code == 200:
#             branches = response.json()

#             # Ensure 'value' exists and is a list
#             if 'value' in branches and isinstance(branches['value'], list):
#                 # Extract branch names and remove 'refs/heads/' prefix
#                 branches_name = [i.replace('refs/heads/', '') for i in branches['value']]
#                 return branches_name
#             else:
#                 # Handle unexpected API structure
#                 return [f"Unexpected response format: {branches}"]
#         else:
#             # Handle API errors
#             return [f"Error: {response.status_code}, {response.text}"]
        

# ######################################## 

#     def get_commits_handler(repo, branch):
#         # API URL
#         url = f"https://dev.azure.com/phlexglobal/_apis/git/repositories/{repo}/commits?searchCriteria.itemVersion.version={branch}&api-version=7.1"

#         pat = _snowflake.get_generic_secret_string('pat')
#         # Headers
#         headers = {
#             "Accept": "application/json"
#         }

#         # Retry logic with exponential backoff
#         retries = 3
#         backoff_factor = 2
#         for attempt in range(retries):
#             try:
#                 # Make the GET request
#                 response = requests.get(url, headers=headers, auth=HTTPBasicAuth("", pat))
#                 response.raise_for_status()  # Raise an exception for HTTP errors
                
#                 # Parse response JSON
#                 commits = response.json()

#                 # Extract commit count and metadata
#                 if response.status_code == 200:
#                     return commits
#                 else:
#                     # Handle unexpected API structure
#                     return {"error": "Unexpected API response", "response": commits}
#             except requests.exceptions.RequestException as e:
#                 if attempt < retries - 1:
#                     time.sleep(backoff_factor ** attempt)  # Exponential backoff
#                 else:
#                     # Return error after exhausting retries
#                     return {"error": "Request failed", "message": str(e)}
                
#     def get_commits_handler_parallel(repo, branch):
#         # API URL
#         url = f"https://dev.azure.com/phlexglobal/_apis/git/repositories/{repo}/commits?searchCriteria.itemVersion.version={branch}&api-version=7.1"

#         pat = _snowflake.get_generic_secret_string('pat')
#         # Headers
#         headers = {
#             "Accept": "application/json"
#         }

#         # Retry logic with exponential backoff
#         retries = 3
#         backoff_factor = 2
#         for attempt in range(retries):
#             try:
#                 # Make the GET request
#                 response = requests.get(url, headers=headers, auth=HTTPBasicAuth("", pat))
#                 response.raise_for_status()  # Raise an exception for HTTP errors
                
#                 # Parse response JSON
#                 commits = response.json()

#                 # Extract commit count and metadata
#                 if response.status_code == 200:
#                     return commits
#                 else:
#                     # Handle unexpected API structure
#                     return {"error": "Unexpected API response", "response": commits}
#             except requests.exceptions.RequestException as e:
#                 if attempt < retries - 1:
#                     time.sleep(backoff_factor ** attempt)  # Exponential backoff
#                 else:
#                     # Return error after exhausting retries
#                     return {"error": "Request failed", "message": str(e)}