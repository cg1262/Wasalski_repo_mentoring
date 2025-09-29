# Databricks notebook source
mabl_api_key = ''

# COMMAND ----------

import requests
import pandas as pd
import time
from datetime import datetime


class Mabl:
    """
    A Python client for interacting with Mabl's API.
    
    This client handles authentication and provides methods for common operations
    like fetching and creating applications, environments, tests, and results.
    """
    
    def __init__(self):
        """
        Initialize the Mabl API client.
        
        Args:
            api_key: Your Mabl API key (get from Settings > APIs in Mabl app)
            workspace_id: Your workspace ID (optional, but required for many operations)
        """
        self.api_key = mabl_api_key
        self.workspace_id = 'CCzzejRVpGB9mMg8c4dbqw-w'
        # Common headers
        self.headers = {
                "accept": "application/json",
                "authorization": "Basic bWF0ZXVzei53YXNhbHNraUBzb2Z0d2FyZW1pbmQuY29tOlNKTzVrNTN5WnNZRWxmb3lIaXI5YlE="
            }
    



########## application
    def get_all_applications(self):
        """

        """
        response = requests.get(url=f"https://api.mabl.com/applications?workspace_id={self.workspace_id}", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df
    

    # get applications by id:
    def get_applications_by_id(self):
        """

        """
        response = requests.get(url=f"https://api.mabl.com/applications?workspace_id={self.workspace_id}/:id", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df
        


##########  credentials 
    def get_credentials(self):
        """

        """
        response = requests.get(url=f"https://api.mabl.com/credentials?organization_id={self.workspace_id}", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
    
    def get_credentials_by_id(self):
        """

        """
        response = requests.get(url=f"https://api.mabl.com/credentials?organization_id={self.workspace_id}?:id?with_secrets=true&with_computed_totp_count=0", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
        



########### DataTable
    def get_data_tables(self):
        """

        """
        response = requests.get(url=f"https://api.mabl.com/dataTables?workspace_id={self.workspace_id}", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
    
    def get_data_table(self):
        """

        """
        response = requests.get(url=f"https://api.mabl.com/dataTables/:data_table_id", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
    
    def get_variables_names(self):
        """

        """
        response = requests.get(url=f"https://api.mabl.com/dataTables/:data_table_id/variableNames", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 

    def get_scenarios(self):
        """

        """
        response = requests.get(url=f"https://api.mabl.com/dataTables/scenarios?:data_table_id=123", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
    
    def get_scenario(self):
        response = requests.get(url=f"https://api.mabl.com/dataTables/scenarios/:123", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
        



############# DatabaseConnection

    def get_database_connection_by_workspace(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/database/connections?workspace_id={self.workspace_id}", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 


    def get_database_connection(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/database/connections/{id}", headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
        



################ Environment

    def get_environments_by_workspace(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/environments?workspace_id={self.workspace_id}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
    
    def get_unique_environment_id(self):
        return self.get_environments_by_workspace90['id'].unique().tolist()
    
    def get_environments_by_id(self):
        response = requests.get(url=f"https://api.mabl.com/environments/{i}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 
        



################ Event

# Query Deployment Events
    def get_query_deployments_events(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/events/deployment?workspace_id={self.workspace_id}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df 

# Get a deployment result summary
    def get_deployment_result(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/execution/result/event/{i}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df
    

# Query Deployment Events by revision
    def get_deployment_events_by_revision(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/events/deployment/revision?workspace_id={self.workspace_id}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df
    



################ Flow

# Get flow metadata ??
    def get_flow_metadata(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/flows/{i}/metadata" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df
    



############## Issue

# Query workspace issues
    def get_workspace_issues(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/workspaces/{self.workspace_id}/issues" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df

# Get issue
    def get_issue(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/issues/{i}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df
    



################ LinkAgent

# Download Link Agent
    def get_download_link_agent(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/link/agents/distribution-redirect?branch={branch}&auto_update=true" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df

# Query Link Agents

    def get_query_link_agents(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/link/agents?workspace_id={self.workspace_id}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return get_application_df
    



################## LinkLabel

# Query Link Labels

    def get_query_link_labels(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/link/labels?workspace_id={self.workspace_id}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame(results)
        return results
        



######### Mailbox

# Get information on Mailboxes by workspace ID
    def get_information_on_mailboxes_by_workspace(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/mailbox/address/workspace/{self.workspace_id}" , headers=self.headers)
        print(response.json())
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df

# # Get Mailbox
    def get_mailbox(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/mailbox/address/{email_address_or_id}" , headers=self.headers)
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df
    



# ###################### Reporting

# # Get a test run summary
    def get_test_run_summary(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/results/testRun/{test_run_id}" , headers=self.headers)
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df


# # Get a plan run summary
    def get_plan_run_summary(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/results/planRun/{plan_run_id}" , headers=self.headers)
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df


# Get test run summaries over a time range
    def get_test_run_summaries_over_time_range(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/results/workspace/{self.workspace_id}/testRuns?limit=500" , headers=self.headers)
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df


# Retrieve activity feed entries
    def get_retrieve_activity_feed_entries(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/workspaces/{self.workspace_id}/reports/activityFeed?limit=100" , headers=self.headers)
        results = response.json().get('entries', {})
        get_application_df = pd.DataFrame(results)
        return get_application_df

# Get a test run artifact export
    def get_test_run_artifact_export(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/report/runArtifacts/export/{export_id}" , headers=self.headers)
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df
    


################## Test

# Get test metadata
    def get_test_run_artifact_export(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/test/{id}/metadata" , headers=self.headers)
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df
    

#################### Users

# Query users
    def get_query_users(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/users?workspace_id={self.workspace_id}&include_historic=false" , headers=self.headers)
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df

# Retrieve workspace user
    def get_retrieve_workspace_user(self):
        # Get database connections by workspace
        response = requests.get(url=f"https://api.mabl.com/workspaces/{self.workspace_id}/users/id" , headers=self.headers)
        results = response.json()
        get_application_df = pd.DataFrame([results])
        return get_application_df
    

api =  Mabl()

api.get_all_applications() 