# in config file password are being stored, to be changed after deployment to databricks

import os
import requests
import pandas as pd
from json import loads, dumps
from  concurrent.futures import ThreadPoolExecutor

from config import  orgUuid, userKey, email

class ServiceBronze:
    
    def __init__(self):
        self.orgUuid = orgUuid
        self.userKey = userKey
        self.email = email
        self.login_body = {
            "email": email,
            "orgUuid": orgUuid,
            "userKey": userKey
        }
        self.url_applications = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/orgs/{self.orgUuid}"

    ###################################################
    # AUTH
    ###################################################
    def authenticate_user(self):
        """
        Authenticates user and returns JWT token
        """
        url_login = "https://api-saas-eu.whitesourcesoftware.com/api/v3.0/login"
        
        response_login = requests.post(url_login, json=self.login_body)
        response_login.raise_for_status()
        login_data = response_login.json()
        refresh_token = login_data['response']['refreshToken']
        
        url_access_token = f"{url_login}/accessToken"
        refresh_token_headers = {
            "wss-refresh-token": refresh_token
        }
        
        access_token_response = requests.post(url_access_token, headers=refresh_token_headers)
        access_token_response.raise_for_status()
        access_token_data = access_token_response.json()
        
        jwt_token = access_token_data['response']['jwtToken']
        
        return jwt_token

    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.authenticate_user()}"
        }
        return headers

    ###################################################
    # BASIC
    ###################################################
    def get_applications(self):
        headers_applications = {
            "Authorization": f"Bearer {self.authenticate_user()}"
        }
        
        url_applications = f"{self.url_applications}/applications"
        all_aplications = []
        applications_cursor = None

        applications_params = {
            "limit": 1000, 
            "cursor": None, 
        }
        
        while True:

            if applications_cursor:
                applications_params["cursor"] = applications_cursor
        

            response_applications = requests.get(url_applications, headers=self.get_headers(), params=applications_params)
            applications_data = response_applications.json()

            applications = applications_data.get('response', [])
            all_aplications.extend(applications)
        
            # Check if there is a next page
            
            # if there is another page output would look like this:
            # {'additionalData': {'totalItems': 96,
            # 'paging': {'next': 'https://api-saas-eu.whitesourcesoftware.com/api/v3.0/orgs/71003aaf-b8e7-4e7b-a622-736b775a0eff/applications?limit=50&cursor=1'}},
            
            # if there is no additional page:
            # {'additionalData': {'totalItems': 96, 'paging': {}},
            cursor = applications_data['additionalData'].get('paging', {}).get('next')
            if not cursor:
                break

        
        if all_aplications: 
            all_applications_df = pd.DataFrame(all_aplications)
        else:
            print("\nNo application data fetched, temporary table not created.")
            all_applications_df = pd.DataFrame()
            
        return all_applications_df 

    def get_projects(self):
        headers = {
            'Authorization': f'Bearer {self.authenticate_user()}',
        }
    
        base_projects_url = f"{self.url_applications}/projects"
        all_projects = [] 
        has_more = True
        cursor = None 
    

        params = {
            "limit": "1000", 
            "populateApplications": "true"
        }
    
        print("Fetching projects data with pagination...")
    

        while has_more:

            if cursor:
                params["cursor"] = cursor
            

            response_projects = requests.get(base_projects_url, headers=self.get_headers(), params=params)
            

            if response_projects.status_code != 200:
                # print(f"Error fetching projects data: {response_projects.status_code}")
                # print(response_projects.text)
                break
            

            response_data = response_projects.json()
            

            projects = response_data.get('response', [])
            

            if not projects:
                has_more = False
                continue
            

            all_projects.extend(projects)
            # print(f"Retrieved {len(projects)} projects. Total so far: {len(all_projects)}")
            

            additional_data = response_data.get('additionalData', {})
            cursor = additional_data.get('cursor')
            

            if not cursor:
                has_more = False
    
        projects_data = pd.DataFrame(all_projects)
        
        print(projects_data.reset_index().columns)
    
        return projects_data

    def get_alert_types(self):
    
        url_alert_types = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{self.orgUuid}/summary/alertTypes"
        response_alert_types = requests.get(url_alert_types, headers=self.get_headers())
        alert_types_data = response_alert_types.json()
    
        df = pd.DataFrame(alert_types_data).reset_index().rename(columns={'index': 'PATH'})
        df = df[['PATH', 'retVal']]
        df['row'] = 0
        wide1 = df.pivot(index='row', columns='PATH', values='retVal').reset_index().drop('row', axis=1)
    
        return wide1

    def get_vulnerabilities_project(self):
        vulnerabilities_project = []
        page = 0
        page_size = 10000
        is_last_page = False
        headers = {
            'Authorization': f'Bearer {self.authenticate_user()}',
        }
        
        while not is_last_page:
            url = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{orgUuid}/summary/projects/vulnerableLibraryCount?search=projectName:like:"
                    
            params = {
                "page": str(page),
                "pageSize": str(page_size)
            }
                    
            response = requests.get(url, headers=self.get_headers(), params=params)
            data = response.json()
                    
            print(f"Page {page} Vulnerabilities Project: ", data)
            vulnerabilities_project.append(data)
            page += 1
            is_last_page = data['additionalData']['isLastPage']
        
        vulnerabilities_project_df = pd.DataFrame(vulnerabilities_project)['retVal'].iloc[0]
        vulnerabilities_project_df = pd.DataFrame(vulnerabilities_project_df)
        
        return vulnerabilities_project_df
    
    def get_alerts_severity(self):
        all_aplications = []
        applications_cursor = None

        url_alerts_severity = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{orgUuid}/summary/alertCountPerSeverity"
        
        response_alerts_severity = requests.get(url_alerts_severity, headers=self.get_headers())
        alerts_severity_data = response_alerts_severity.json()
        print("Alerts Severity: ", alerts_severity_data)
        df_alerts_severity_data = pd.DataFrame([alerts_severity_data['retVal']])
       
        return df_alerts_severity_data

    def get_labels(self):
        # ——— ## ———— ## ————
        # Stream: Labels
        # This stream gets labels associated with the organization.
        url_labels = f"{self.url_applications}/labels"
        response_labels = requests.get(url_labels, headers=self.get_headers())  # Fixed: removed extra parenthesis
        labels_data = response_labels.json()
    
        labels_data = pd.DataFrame(labels_data['response'])
    
        # Assume df_labels holds the final DataFrame for this notebook
        # <<<< ADJUST THE DATAFRAME VARIABLE NAME BELOW IF IT'S DIFFERENT >>>>
    
        # Display the DataFrame (optional, for confirmation in notebooks)
        return labels_data
    
    ###################################################
    # UNIQUES
    ###################################################
    def get_unique_product_uuids(self):
        unique_product_uuids = self.get_applications()['uuid'].unique().tolist()
        return unique_product_uuids
        
    def get_unique_uuid(self):
        unique_uuid = self.get_projects()['uuid'].unique().tolist()
        return unique_uuid  # Fixed: was returning undefined 'unique_projects'
        
    def get_unique_policy_violations(self):
        policy_violations = self.get_projects()['applicationUuid'].tolist()
        return policy_violations
        
    ###################################################
    # LOOPS
    ###################################################


    
    def get_alerts_per_project(self):
        all_security_findings = []  # Initialize list to store all findings from all projects

        for project_uuid in self.get_unique_uuid():
            url_security_alerts_project = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{project_uuid}/dependencies/findings/security"
            params = {"limit": "10000"}
            response_security_alerts_project = requests.get(url_security_alerts_project, headers=self.get_headers(), params=params)
            security_alerts_project_data = response_security_alerts_project.json()['response']
            all_security_findings.extend(security_alerts_project_data)
        
        df_final_alerts = pd.DataFrame(all_security_findings)
        # Now df_final_alerts contains all findings from all projects
        # You can display it or process it further
        df_final_alerts['status'] = df_final_alerts['findingInfo'].apply(lambda x: x.get('status') if x else None)
        df_final_alerts['detected_at'] = df_final_alerts['findingInfo'].apply(lambda x: x.get('detectedAt') if x else None)
        df_final_alerts['modified_at'] = df_final_alerts['findingInfo'].apply(lambda x: x.get('modifiedAt') if x else None)
        df_final_alerts.drop(columns=['findingInfo'])
        
        list_of_alerts_cleaned = df_final_alerts[['name', 'type', 'uuid', 'topFix', 'project', 'component',
                                                   'application', 'exploitable', 'vulnerability', 'threatAssessment', 
                                                   'scoreMetadataVector', 'status', 'detected_at', 'modified_at']]
        
        # Display the DataFrame (optional, for confirmation in notebooks)
        # list_of_alerts_cleaned.columns
        return list_of_alerts_cleaned
        
    def get_libraries(self):
        params = {
            "limit": "10000", 
        }
    
        all_libraries = []  
        # count_libraries = 0
    

        for project_uuid in self.get_unique_uuid():
            # print(f"Fetching library no {count_libraries}")
            # count_libraries += 1
            # print(f"Fetching libraries for project {project_uuid}...")
            has_more = True 
            cursor = None 
            
            while has_more:
                if cursor:
                    params["cursor"] = cursor
                
                url_libraries = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{project_uuid}/dependencies/libraries"
                response_libraries = requests.get(url_libraries, headers=self.get_headers(), params=params)
                
                if response_libraries.status_code != 200:
                    # print(f"Error fetching libraries for project {project_uuid}: {response_libraries.status_code}")
                    print(response_libraries.text)
                    break
                
                libraries_data = response_libraries.json()
                

                libraries = libraries_data.get('response', [])
                

                for library in libraries:
                    library['project_uuid'] = project_uuid
                
                all_libraries.extend(libraries)
                # print(f"Retrieved {len(libraries)} libraries for project {project_uuid}. Total so far: {len(all_libraries)}")
                
                additional_data = libraries_data.get('additionalData', {})
                cursor = additional_data.get('cursor')
                

                has_more = bool(cursor)
                
        all_libraries_df = pd.DataFrame(all_libraries)
        # wide1 = wide1.drop('row', axis = 1)
    
        return all_libraries_df
    
    def get_license_policy_violations(self):
        policy_violations_list = []
        for product_uuid in self.get_unique_policy_violations():
            page = 0
            is_last_page = False
        
            while not is_last_page:
                params = {
                    'pageSize': '10000',
                    'page': str(page)
                }
                url_licence_policy_violations = (
                    f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/products/{product_uuid}/alerts/legal"
                )
                response = requests.get(url_licence_policy_violations, headers=self.get_headers(), params=params)
                data = response.json()
        

                if 'retVal' in data and isinstance(data['retVal'], list):
                    policy_violations_list.extend(data['retVal'])
        
                is_last_page = data.get('body', {}).get('additionalData', {}).get('isLastPage', True)
                if not isinstance(is_last_page, bool):
                    is_last_page = data.get('additionalData', {}).get('isLastPage', True)
        
                page += 1
        
        policy_violations_df = pd.DataFrame(policy_violations_list)
        
        policy_violations_df['status'] = policy_violations_df['alertInfo'].apply(lambda x: x.get('status') if isinstance(x, dict) else None)
        policy_violations_df['detected_at'] = policy_violations_df['alertInfo'].apply(lambda x: x.get('detectedAt') if isinstance(x, dict) else None)
        policy_violations_df['modified_at'] = policy_violations_df['alertInfo'].apply(lambda x: x.get('modifiedAt') if isinstance(x, dict) else None)
        
        policy_violations_df = policy_violations_df[[
            'name', 'type', 'uuid', 'project', 'component',
            'policyName', 'status', 'detected_at', 'modified_at'
        ]]

        policy_violations_df = policy_violations_df.drop_duplicates(subset=['uuid'])
        policy_violations_df = policy_violations_df.reset_index(drop=True)
        return policy_violations_df
        
    def get_project_due_diligence(self):
        all_due_diligence = []  
        params = {
            'limit': "10000"
        }
        
        def get_projects_unique_uuid(project_unique_uuid):
            due_diligence_url = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{project_unique_uuid}/dependencies/libraries/licenses"
            response_due_diligence = requests.get(due_diligence_url, headers=self.get_headers(), params=params) 
            due_diligence = response_due_diligence.json().get('response', [])
            return due_diligence

        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(get_projects_unique_uuid, self.get_unique_uuid()))

        # Flatten the list of lists
        for result in results:
            all_due_diligence.extend(result)
        
        return pd.DataFrame(all_due_diligence)

    def get_alerts_per_library(self):
        all_security_alerts_data = []
        page_size = 1000  # Using a smaller page size for example, adjust as needed (max 10000)
        
        for project_token in self.get_unique_uuid():
            page = 0
            while True:
                url_security_alerts_library = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/projects/{project_token}/alerts/security/groupBy/component"
                params = {"pageSize": str(page_size), "page": str(page)}
                response = requests.get(url_security_alerts_library, headers=self.get_headers(), params=params)
                # Raise an exception for bad status codes (4xx client error or 5xx server error)
                response.raise_for_status()
                data_page = response.json()
        
                # Extract the list of alerts, default to empty list if 'retVal' is missing or null
                alerts = data_page.get('retVal', [])
        
                # Add project token to each alert record for context
                for alert in alerts:
                    alert['projectToken'] = project_token
                all_security_alerts_data.extend(alerts)
        
                # If the number of returned alerts is less than the page size, it's the last page
                if len(alerts) < page_size:
                    break
        
                # Increment page number for the next request
                page += 1
        
        df_security_alerts = pd.DataFrame(all_security_alerts_data)
        return df_security_alerts