# Databricks notebook source
personal_access_token = ''

# COMMAND ----------

import requests
import pandas as pd
from requests.auth import HTTPBasicAuth 
import json

class Azure_DevOps:
    def __init__(self):
        self.organization_name = "Phlexglobal"
        self.personal_access_token = personal_access_token
        self.auth = HTTPBasicAuth('', self.personal_access_token)
        self.params = {'$top': 5000}
        self.pipelines = [2441]
        
        # to be changed into secret
        self.sub_id = sub_id
    
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


    def get_unique_projects(self):
        unique_ids = self.get_ado_projects()['ID'] .astype(str).unique().tolist()
        return unique_ids
        
    def get_ado_approvals(self): 
    
        url_projects = f"https://dev.azure.com/Phlexglobal/_apis/projects?api-version=7.1"  
    
        approvals = []
    
        for i in self.get_unique_projects():
            url_approvals = f"https://dev.azure.com/Phlexglobal/{i}/_apis/pipelines/approvals?api-version=7.1"
            response = requests.get(url_approvals, auth=self.auth, params = self.params)
            resp = response.json()['value']
            approvals.extend(resp)
    
        df_approvals = pd.DataFrame(approvals)
    
    
        new_order = ['id', 'steps', '_links', 'status', 'pipeline', 'createdOn', 'executionOrder', 'lastModifiedOn', 'blockedApprovers', 'minRequiredApprovers']
        df_approvals = df_approvals[new_order]
    
        df_approvals.columns = ['ID', 'STEPS', '_LINKS', 'STATUS', 'PIPELINE', 'CREATEDON', 'EXECUTIONORDER', 'LASTMODIFIEDON', 'BLOCKEDAPPROVERS', 'MINREQUIREDAPPROVERS']
    
        return df_approvals

    def get_ado_definitions(self): 
    
        definitions = []
    
        for i in self.get_unique_projects():
    
            url_definitions = f"https://dev.azure.com/Phlexglobal/{i}/_apis/build/definitions?api-version=7.1"
            response = requests.get(url_definitions, auth=self.auth, params = self.params)
            resp = response.json()['value']
            definitions.extend(resp)
            
        df_definitions = pd.DataFrame(definitions)
    
    
        new_order = [
            'id', 
            'uri', 
            'url', 
            'name', 
            'path', 
            'type', 
            'queue', 
            '_links', 
            'drafts', 
            'project', 
            'quality', 
            'revision', 
            'authoredBy', 
            'createdDate', 
            'queueStatus'
        ]
    
        df_definitions = df_definitions[new_order]
    
        df_definitions.columns = [
            'ID', 
            'URI', 
            'URL', 
            'NAME', 
            'PATH', 
            'TYPE', 
            'QUEUE', 
            '_LINKS', 
            'DRAFTS', 
            'PROJECT', 
            'QUALITY', 
            'REVISION', 
            'AUTHOREDBY', 
            'CREATEDDATE', 
            'QUEUESTATUS'
        ]
    
        df_definitions['PROJECTID'] = df_definitions['PROJECT'].apply(lambda x: x['id'])
        df_definitions['PROJECTNAME'] = df_definitions['PROJECT'].apply(lambda x: x['name'])
    
        return df_definitions

    
    def get_ado_pipelines(self):
        pipelines = []
        for i in self.get_unique_projects():
            url_pipelines = f"https://dev.azure.com/Phlexglobal/{i}/_apis/pipelines?api-version=7.1"
            response = requests.get(url_pipelines, auth=self.auth, params=self.params)
            resp = response.json()['value']

            for pipeline in resp:
                pipeline['project_id'] = i
                
            pipelines.extend(resp)
            
        df_pipelines = pd.DataFrame(pipelines)
        
    
        new_order = [
            'id', 
            'url', 
            'name', 
            '_links', 
            'folder', 
            'revision',
            'project_id'
        ]
    
        df_pipelines = df_pipelines[new_order]
    
        df_pipelines.columns = [
            'ID', 
            'URL', 
            'NAME', 
            '_LINKS', 
            'FOLDER', 
            'REVISION',
            'PROJECT_ID'
        ]
        return df_pipelines
        
    def get_ado_source_providers(self):

        src_providers = []
        for i in self.get_unique_projects():
            url_src_providers = f"https://dev.azure.com/Phlexglobal/{i}/_apis/sourceproviders?api-version=7.1"
            response = requests.get(url_src_providers, auth=self.auth, params=self.params)
            resp = response.json()['value']
            src_providers.extend(resp)
        df_source_providers = pd.DataFrame(src_providers)
    
    
        new_order = [
            'name', 
            'supportedTriggers', 
            'supportedCapabilities'
        ]
    
        df_source_providers = df_source_providers[new_order]
    
        df_source_providers.columns = [
            'NAME', 
            'SUPPORTEDTRIGGERS', 
            'SUPPORTEDCAPABILITIES'
        ]   
        return df_source_providers

    def get_ado_repos(self):

        repos = []
        for i in self.get_unique_projects():
            url_repos =f"https://dev.azure.com/PhlexGlobal/{i}/_apis/git/repositories?api-version=4.1"
            response = requests.get(url_repos,auth=self.auth, params=self.params)
            resp = response.json()['value']
            repos.extend(resp)
        df_repos = pd.DataFrame(repos)
    
        new_order = [
            'id', 
            'url', 
            'name', 
            'size', 
            'sshUrl', 
            'webUrl', 
            'project', 
            'remoteUrl', 
            'isDisabled', 
            'defaultBranch', 
            'isInMaintenance'
        ]
    
        df_repos = df_repos[new_order]
    
    
        df_repos.columns = [
            'ID', 
            'URL', 
            'NAME', 
            'SIZE', 
            'SSHURL', 
            'WEBURL', 
            'PROJECT', 
            'REMOTEURL', 
            'ISDISABLED', 
            'DEFAULTBRANCH', 
            'ISINMAINTENANCE'
        ]
    
        df_repos['proj_id'] = df_repos['PROJECT'].apply(lambda x: x['id'])
    
        df_repos_uniques = df_repos['ID'].astype(str).unique().tolist()
    
        return df_repos

    def get_unique_pipeline_runs(self):
      
        for i in self.pipelines:
            url = f"https://dev.azure.com/Phlexglobal/{self.sub_id}/_apis/pipelines/{i}/runs?api-version=7.1"
            response = requests.get(url, auth=self.auth, params=self.params)
        
            resp = response.json()
        
            df = pd.DataFrame(resp['value']) 
        
            # Filter by name containing 'PEL'
            filtered_df = df[df['name'].str.contains('PEL', case=False, na=False)].copy()
            filtered_df['issue_key'] = filtered_df['name'].astype(str).str.split('#').str[1]
            filtered_df['env'] = filtered_df['name'].astype(str).str.split('#').str[-1]
            unique_names = filtered_df['issue_key'].unique().tolist()
            
        return unique_names, filtered_df
        
    def get_pipeline_runs(self):

        def extract_between_hashes(text):
            parts = text.split('#')
            if len(parts) >= 4:  # Ensuring we have at least three # separators
                return parts[2]  # Index 2 is between 2nd and 3rd #
            return None
    
        runs = []
        
        unique_names, filtered_df = self.get_unique_pipeline_runs()
        
        for i in unique_names:  # iterate over unique_names
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
                
            runs.append(name_df)
        
       
        final_df = pd.concat(runs, ignore_index=True).drop(columns='templateParameters')



        final_df['extracted_name_for_issue_key'] = final_df['name'].apply(extract_between_hashes)
        return final_df
        
api = Azure_DevOps()
        