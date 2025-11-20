
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time
import datetime
from pyspark.sql import SparkSession
from Core.Services.ServiceSaveToDelta import upserting_data

class ServiceBronze:
    
    def __init__(self, dbutils, spark):
        self.spark = SparkSession.builder.getOrCreate()
        self.email = dbutils.secrets.get(scope = "engineering-metrics-keys", key = "mend-email-secret-key")
        self.orgUuid = dbutils.secrets.get(scope = "engineering-metrics-keys", key = "mend-org-uuid-secret-key")
        self.userKey = dbutils.secrets.get(scope = "engineering-metrics-keys", key = "mend-user-key-secret-key")
        self.login_body = {
            "email": self.email,
            "orgUuid": self.orgUuid,
            "userKey": self.userKey
        }
        self.basic_url = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/orgs/{self.orgUuid}"
        self.catalog_schema = 'engineering_metrics.bronze.'
        self.table_schema = 'mend_'

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

    def headers(self):
        headers = {
            "Authorization": f"Bearer {self.authenticate_user()}"
        }
        return headers

    ###################################################
    # BASIC
    ###################################################
    def applications(self, checking_data = None):
        headers_applications = {
            "Authorization": f"Bearer {self.authenticate_user()}"
        }
        
        url_applications = f"{self.basic_url}/applications"
        all_aplications = []
        applications_cursor = None

        applications_params = {
            "limit": 1000, 
            "cursor": None, 
        }
        
        while True:

            if applications_cursor:
                applications_params["cursor"] = applications_cursor
        

            response_applications = requests.get(url_applications, headers=self.headers(), params=applications_params)
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
            dataframe_pd = pd.DataFrame(all_aplications)
        else:
            print("\nNo application data fetched, temporary table not created.")
            dataframe_pd = pd.DataFrame()

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)


        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}applications",
                    source_dataframe=dataframe_spark,
                    target_column="uuid",
                    source_column="uuid"
                )

        return dataframe_spark 

    def projects(self, checking_data = None):
        headers = {
            'Authorization': f'Bearer {self.authenticate_user()}',
        }
    
        base_projects_url = f"{self.basic_url}/projects"
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
            

            response_projects = requests.get(base_projects_url, headers=self.headers(), params=params)
            

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
    
        dataframe_pd = pd.DataFrame(all_projects)
        
        dataframe_pd.reset_index().columns
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)


        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}projects",
                    source_dataframe=dataframe_spark,
                    target_column="uuid",
                    source_column="uuid"
                )


        return dataframe_spark

    def alert_types(self, checking_data = None):
    
        url_alert_types = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{self.orgUuid}/summary/alertTypes"
        response_alert_types = requests.get(url_alert_types, headers=self.headers())
        alert_types_data = response_alert_types.json()
    
        dataframe_pd = pd.DataFrame(alert_types_data).reset_index().rename(columns={'index': 'PATH'})
        dataframe_pd = dataframe_pd[['PATH', 'retVal']]
        dataframe_pd['row'] = 0

        dataframe_pd = dataframe_pd.pivot(index='row', columns='PATH', values='retVal').reset_index().drop('row', axis=1)
        dataframe_pd['current_timestamp'] = datetime.datetime.now()

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            dataframe_spark.write \
                .format("delta") \
                .option("overwriteSchema", "true") \
                .mode("append") \
                .saveAsTable(f"{self.catalog_schema}{self.table_schema}alert_types")


        return dataframe_spark

    def vulnerabilities_project(self, checking_data = None):
        vulnerabilities_project = []
        page = 0
        page_size = 10000
        is_last_page = False
        headers = {
            'Authorization': f'Bearer {self.authenticate_user()}',
        }
        
        while not is_last_page:
            url = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{self.orgUuid}/summary/projects/vulnerableLibraryCount?search=projectName:like:"
                    
            params = {
                "page": str(page),
                "pageSize": str(page_size)
            }
                    
            response = requests.get(url, headers=self.headers(), params=params)
            data = response.json()
                    
            # print(f"Page {page} Vulnerabilities Project: ", data)
            vulnerabilities_project.append(data)
            page += 1
            is_last_page = data['additionalData']['isLastPage']
        
        dataframe_pd = pd.DataFrame(vulnerabilities_project)['retVal'].iloc[0]
        dataframe_pd = pd.DataFrame(dataframe_pd)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

   
        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}vulnerabilities_project",
                    source_dataframe=dataframe_spark,
                    target_column="uuid",
                    source_column="uuid"
                )


        return dataframe_spark
    
    def alerts_severity(self, checking_data = None):
        all_aplications = []
        applications_cursor = None

        url_alerts_severity = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{self.orgUuid}/summary/alertCountPerSeverity"
        
        response_alerts_severity = requests.get(url_alerts_severity, headers=self.headers())
        alerts_severity_data = response_alerts_severity.json()
        print("Alerts Severity: ", alerts_severity_data)
        dataframe_pd = pd.DataFrame([alerts_severity_data['retVal']])

        dataframe_pd['current_timestamp'] = datetime.datetime.now()

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            dataframe_spark.write \
                .format('delta') \
                .option("overwriteSchema", "true") \
                    .mode("overwrite") \
                .saveAsTable(f"{self.catalog_schema}{self.table_schema}alerts_severity")

        return dataframe_spark

    def labels(self, checking_data = None):

        url_labels = f"{self.basic_url}/labels"
        response_labels = requests.get(url_labels, headers=self.headers())  # Fixed: removed extra parenthesis
        dataframe_pd = response_labels.json()
    
        dataframe_pd = pd.DataFrame(dataframe_pd['response'])
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}labels",
                    source_dataframe=dataframe_spark,
                    target_column="uuid",
                    source_column="uuid"
                )

        return dataframe_spark
    
    ###################################################
    # UNIQUES
    ###################################################
    def unique_product_uuids(self):
        df = self.applications()
        unique_product_uuids = [
            row['uuid'] for row in 
            df.withColumn('uuid', df['uuid'].cast('string'))
            .select('uuid')
            .distinct()
            .collect()
        ]
        return unique_product_uuids

    def unique_uuid(self):
        df = self.projects()
        unique_project_uuid = [
            row['uuid'] for row in 
            df.withColumn('uuid', df['uuid'].cast('string'))
            .select('uuid')
            .distinct()
            .collect()
        ]
        return unique_project_uuid

    def unique_policy_violations(self):
        df = self.projects()
        unique_project_application_uuid = [
            row['applicationUuid'] for row in 
            df.withColumn('applicationUuid', df['applicationUuid'].cast('string'))
            .select('applicationUuid')
            .distinct()
            .collect()
        ]
        return unique_project_application_uuid
    
        
    ###################################################
    # LOOPS
    ###################################################


    
    def alerts_per_project(self, checking_data = None):
        all_security_findings = []  # Initialize list to store all findings from all projects

        for project_uuid in self.unique_uuid():
            url_security_alerts_project = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{project_uuid}/dependencies/findings/security"
            params = {"limit": "10000"}
            response_security_alerts_project = requests.get(url_security_alerts_project, headers=self.headers(), params=params)
            security_alerts_project_data = response_security_alerts_project.json()['response']
            all_security_findings.extend(security_alerts_project_data)
        
        dataframe_pd = pd.DataFrame(all_security_findings)

        dataframe_pd['status'] = dataframe_pd['findingInfo'].apply(lambda x: x.get('status') if x else None)
        dataframe_pd['detected_at'] = dataframe_pd['findingInfo'].apply(lambda x: x.get('detectedAt') if x else None)
        dataframe_pd['modified_at'] = dataframe_pd['findingInfo'].apply(lambda x: x.get('modifiedAt') if x else None)

        
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))


        dataframe_spark = self.spark.createDataFrame(dataframe_pd)


        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}alerts_per_project",
                    source_dataframe=dataframe_spark,
                    target_column="uuid",
                    source_column="uuid"
                )

        return dataframe_spark
    
    def alerts_per_library(self, checking_data = None):
        all_security_alerts_data = []
        page_size = 1000  # Using a smaller page size for example, adjust as needed (max 10000)
        
        for project_token in self.unique_uuid():
            page = 0
            while True:
                url_security_alerts_library = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/projects/{project_token}/alerts/security/groupBy/component"
                params = {"pageSize": str(page_size), "page": str(page)}
                response = requests.get(url_security_alerts_library, headers=self.headers(), params=params)
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
        
        dataframe_pd = pd.DataFrame(all_security_alerts_data)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))

        dataframe_pd['upsert_key'] = dataframe_pd['uuid'] + dataframe_pd['project'] + dataframe_pd['product'] 

        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        # dataframe_spark = dataframe_spark.dropDuplicates(['upsert_key'])

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}alerts_per_library",
                    source_dataframe=dataframe_spark,
                    target_column="upsert_key",
                    source_column="upsert_key"
                )

        return dataframe_spark

    def libraries(self, checking_data = None):
        params = {
            "limit": "10000", 
        }
    
        all_libraries = []  
        # count_libraries = 0
    

        for project_uuid in self.unique_uuid():
            # print(f"Fetching library no {count_libraries}")
            # count_libraries += 1
            # print(f"Fetching libraries for project {project_uuid}...")
            has_more = True 
            cursor = None 
            
            while has_more:
                if cursor:
                    params["cursor"] = cursor
                
                url_libraries = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{project_uuid}/dependencies/libraries"
                response_libraries = requests.get(url_libraries, headers=self.headers(), params=params)
                
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
                
        dataframe_pd = pd.DataFrame(all_libraries)
        
        dataframe_pd = dataframe_pd.drop(columns=['locations','workflowUuids'])
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))

        dataframe_pd['upsert_key'] = dataframe_pd['uuid'] + dataframe_pd['project_uuid']

        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        # dataframe_spark = dataframe_spark.dropDuplicates(['upsert_key'])

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}libraries",
                    source_dataframe=dataframe_spark,
                    target_column="upsert_key",
                    source_column="upsert_key"
                )

        return dataframe_spark
    
    def license_policy_violations(self, checking_data = None):
        policy_violations_list = []
        for product_uuid in self.unique_policy_violations():
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
                response = requests.get(url_licence_policy_violations, headers=self.headers(), params=params)
                data = response.json()
        

                if 'retVal' in data and isinstance(data['retVal'], list):
                    policy_violations_list.extend(data['retVal'])
        
                is_last_page = data.get('body', {}).get('additionalData', {}).get('isLastPage', True)
                if not isinstance(is_last_page, bool):
                    is_last_page = data.get('additionalData', {}).get('isLastPage', True)
        
                page += 1
        
        dataframe_pd = pd.DataFrame(policy_violations_list)
        
        dataframe_pd['status'] = dataframe_pd['alertInfo'].apply(lambda x: x.get('status') if isinstance(x, dict) else None)
        dataframe_pd['detected_at'] = dataframe_pd['alertInfo'].apply(lambda x: x.get('detectedAt') if isinstance(x, dict) else None)
        dataframe_pd['modified_at'] = dataframe_pd['alertInfo'].apply(lambda x: x.get('modifiedAt') if isinstance(x, dict) else None)
        
        dataframe_pd = dataframe_pd.reset_index(drop=True)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))

        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name=f"{self.table_schema}license_policy_violations",
                    source_dataframe=dataframe_spark,
                    target_column="uuid",
                    source_column="uuid"
                )


        return dataframe_spark
        
    def project_due_diligence(self, checking_data = None):
        all_due_diligence = []  
        params = {
            'limit': "10000"
        }
        
        def projects_unique_uuid(project_unique_uuid):
            due_diligence_url = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{project_unique_uuid}/dependencies/libraries/licenses"
            response_due_diligence = requests.get(due_diligence_url, headers=self.headers(), params=params) 
            due_diligence = response_due_diligence.json().get('response', [])
            return due_diligence

        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(executor.map(projects_unique_uuid, self.unique_uuid()))

        # Flatten the list of lists
        for result in results:
            all_due_diligence.extend(result)
        dataframe_pd = pd.DataFrame(all_due_diligence)

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_pd['upsert_key'] = dataframe_pd['uuid'] + dataframe_pd['project']

        dataframe_spark = self.spark.createDataFrame(dataframe_pd)


        if checking_data != True:
                dataframe_spark = dataframe_spark.dropDuplicates(['upsert_key'])
                upserting_data(
                    target_table_name=f"{self.table_schema}project_due_diligence",
                    source_dataframe=dataframe_spark,
                    target_column="upsert_key",
                    source_column="upsert_key"
                )

        return dataframe_spark
