# Databricks notebook source
sonarcloud_api_key = ''

# COMMAND ----------

import requests
import pandas as pd
import time

class SonarcloudApi:
    
    def __init__(self):
        self.sonarcloud_api_key = sonarcloud_api_key
        self.headers = {"Authorization": f"Bearer {self.sonarcloud_api_key}"}
        self.organization = 'phlexglobal'
        self.page_size = 500
        self.page_number = 1
        self.months = range(1,13)
        self.current_year = datetime.datetime.now().year
        
    def get_sonarcloud_issues(self):

        all_issues = []  
        year_tofind = 2017
        # iterates through years starting from 2017 up to current year
        while year_tofind <= self.current_year:
            # iterates through all months (1-12) for each year
            for month in self.months:
                params = {
                    "organization": self.organization, 
                    "ps": self.page_size,  
                    "p": self.page_number ,     
                    "createdBefore": f"{year_tofind}-{month+1:02d}-01",  
                    "createdAfter": f"{year_tofind}-{month:02d}-01",     
                }
    

                url_issues = "https://sonarcloud.io/api/issues/search"

                response_issues = requests.get(url_issues, headers=self.headers, params=params)

                issues_data = response_issues.json()
    

                total_sonarcloud_api_key = issues_data.get('paging', {}).get('total', 0)
    
                # skip to next month if no sonarcloud_api_key found for current month
                if total_sonarcloud_api_key == 0:
                    continue
    
                # Calculate total number of pages based on total sonarcloud_api_key and page size
                # If there's a remainder, add one more page
                total_pages = (total_sonarcloud_api_key // params['ps']) + (1 if total_sonarcloud_api_key % params['ps'] > 0 else 0)
    
                all_issues.extend(issues_data.get('issues', []))
    
                # Pagination loop - fetch all remaining pages of sonarcloud_api_key
                while params["p"] < total_pages:
                    params["p"] += 1 

                    response_issues = requests.get(url_issues, headers=self.headers, params=params)

                    issues_data = response_issues.json()

                    all_issues.extend(issues_data.get('issues', []))
    
            year_tofind += 1

        df_issues = pd.DataFrame(all_issues)
    
        new_order = ['key', 'rule', 'severity', 'component', 'project', 'line', 'hash', 'textRange', 'flows', 
                    'status', 'message', 'effort', 'debt', 'assignee', 'author', 'tags', 
                    'creationDate', 'updateDate', 'type', 'organization', 'cleanCodeAttribute', 
                    'cleanCodeAttributeCategory', 'impacts', 'issueStatus', 'externalRuleEngine', 
                    'resolution', 'closeDate']
        df_issues = df_issues[new_order]
    
        df_issues.columns = ['KEY', 'RULE', 'SEVERITY', 'COMPONENT', 'PROJECT', 'LINE', 'HASH', 'TEXTRANGE', 
                            'FLOWS', 'STATUS', 'MESSAGE', 'EFFORT', 'DEBT', 'ASSIGNEE', 
                            'AUTHOR', 'TAGS', 'CREATIONDATE', 'UPDATEDATE', 'TYPE', 'ORGANIZATION', 
                            'CLEANCODEATTRIBUTE', 'CLEANCODEATTRIBUTECATEGORY', 'IMPACTS', 
                            'ISSUESTATUS', 'EXTERNALRULEENGINE', 'RESOLUTION', 'CLOSEDATE']
        return df_issues

    def get_sonarcloud_components(self):
        
        params = {
                "organization": self.organization, 
                "ps": self.page_size, 
                "p": self.page_number    
        }
    
        all_components = [] 
    
        total_sonarcloud_api_key = 0 
    

        url_components = "https://sonarcloud.io/api/components/search"
        response_components = requests.get(url_components, headers=self.headers, params=params)
        components_data = response_components.json()

        total_sonarcloud_api_key = components_data['paging']['total']
        total_pages = (total_sonarcloud_api_key // params['ps']) + (1 if total_sonarcloud_api_key % params['ps'] > 0 else 0)
    

        all_components.extend(components_data['components'])
    
        while params["p"] < total_pages:
            params["p"] += 1 
            response_components = requests.get(url_components, headers=self.headers, params=params)
            components_data = response_components.json()
            
            all_components.extend(components_data['components'])
    
        df_components = pd.DataFrame(all_components)
    
        new_order = ['organization', 'key', 'name', 'qualifier', 'project']
        df_components = df_components[new_order]
    
        df_components.columns = ['ORGANIZATION', 'KEY', 'NAME', 'QUALIFIER', 'PROJECT']
        return df_components
        
    def get_unique_sonarcloud_components(self):
        unique = self.get_sonarcloud_components()['KEY'].unique().tolist()        
        return unique
        
    def get_sonarcloud_measures_component(self):
        metrics_keys = ['accepted_issues', 'files', 'ncloc', 'maintainability_issues', 'reliability_issues', 'security_hotspots', 'security_issues', 'line_coverage', 
      'duplicated_lines', 'duplicated_lines_density']
   
        all_measures_component = []
        for comp_id in self.get_unique_sonarcloud_components():

                for j in metrics_keys:
                    url_labels = f"https://sonarcloud.io/api/measures/component"

                    response_labels = requests.get(url_labels, headers=self.headers, 
                    params = {
                        "organization": self.organization,
                        "metricKeys" : j,
                        # "metricKeys" : 'accepted_issues',
                        'component' : comp_id
                    }
                    )
                    labels_data = response_labels.json()
                    
                    data = {
                    'id': labels_data['component']['id'],
                    'key': labels_data['component']['key'],
                    'name': labels_data['component']['name'],
                    'qualifier': labels_data['component']['qualifier'],
                    'measures': labels_data['component']['measures']
                    }
    
    
                    all_measures_component.append(data)
                    time.sleep(0.1)

        df_measures_component = pd.DataFrame(all_measures_component)
    
    
        new_order = ['id', 'key', 'name', 'qualifier', 'measures']
        df_measures_component = df_measures_component[new_order]
        df_measures_component.columns = ['ID', 'KEY', 'NAME', 'QUALIFIER', 'MEASURES']
        return df_measures_component

    def get_sonarcloud_metrics(self):

        params = {
            "organization": self.organization,
            "ps": self.page_size,  
            "p": self.page_number     
        }
    

        url_labels = "https://sonarcloud.io/api/metrics/search"
        response_labels = requests.get(url_labels, headers=self.headers, params=params)
        labels_data = response_labels.json()['metrics']
    
        df_metrics = pd.DataFrame(labels_data)
    
        new_order = ['id', 'key', 'name', 'type', 'domain', 'direction', 'description', 'qualitative', 'hidden', 'decimalScale']
        df_metrics = df_metrics[new_order]
    
        df_metrics.columns = ['ID', 'KEY', 'NAME', 'TYPE', 'DOMAIN', 'DIRECTION', 'DESCRIPTION', 'QUALITATIVE', 'HIDDEN', 'DECIMALSCALE']
    
        return df_metrics

    def get_sonarcloud_projects(self):    # ---- # ---- Projects

        params = {
            "organization": self.organization,
            "ps": self.page_size, 
            "p": self.page_number      
        }

        all_projects = [] 
        total_sonarcloud_api_key = 0 
    
        url_labels = "https://sonarcloud.io/api/projects/search"
        response_labels = requests.get(url_labels, headers=self.headers, params=params)
        labels_data = response_labels.json()

        total_sonarcloud_api_key = labels_data['paging']['total']
        total_pages = (total_sonarcloud_api_key // params['ps']) + (1 if total_sonarcloud_api_key % params['ps'] > 0 else 0)
    

        all_projects.extend(labels_data['components'])
    

        while params["p"] < total_pages:
            params["p"] += 1  # Go to the next page
            response_labels = requests.get(url_labels, headers=self.headers, params=params)
            labels_data = response_labels.json()
            
            all_projects.extend(labels_data['components'])
    
    
    
        df_projects = pd.DataFrame(all_projects)
    
        new_order = ['organization', 'key', 'name', 'qualifier', 'visibility', 'lastAnalysisDate', 'revision']
        df_projects = df_projects[new_order]
    
    
        df_projects.columns = ['ORGANIZATION', 'KEY', 'NAME', 'QUALIFIER', 'VISIBILITY', 'LASTANALYSISDATE', 'REVISION']
        
        return df_projects

    def get_sonarcloud_measures_component(self):

        metrics_keys = [
        'accepted_issues', 'files', 'ncloc', 'maintainability_issues', 'reliability_issues', 
          'security_hotspots', 'security_issues', 'line_coverage', 
          'duplicated_lines', 'duplicated_lines_density'
        ]

        
        component = self.get_sonarcloud_components()['KEY'].unique().tolist()
        all_measures_component = []

        for comp_id in component:
                for j in metrics_keys:
                    url_labels = f"https://sonarcloud.io/api/measures/component"
                    response_labels = requests.get(url_labels, headers=self.headers, 
                    params = {
                        "organization": "phlexglobal",
                        "metricKeys" : j,
                        # "metricKeys" : 'accepted_issues',
                        'component' : comp_id
                    }
                    )
                    labels_data = response_labels.json()
                    

                    data = {
                    'id': labels_data['component']['id'],
                    'key': labels_data['component']['key'],
                    'name': labels_data['component']['name'],
                    'qualifier': labels_data['component']['qualifier'],
                    'measures': labels_data['component']['measures']
                    }
    
    
                    all_measures_component.append(data)
  
                    time.sleep(0.1)


        df_measures_component = pd.DataFrame(all_measures_component)
    
    
        new_order = ['id', 'key', 'name', 'qualifier', 'measures']
        df_measures_component = df_measures_component[new_order]
        df_measures_component.columns = ['ID', 'KEY', 'NAME', 'QUALIFIER', 'MEASURES']
        return df_measures_component
    
api = SonarcloudApi()

