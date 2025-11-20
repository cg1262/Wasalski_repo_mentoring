import pandas as pd
import requests
import datetime
import time
ACCOUNT_ID = 1801997
from pyspark.sql import SparkSession

import config as cfg

new_relic_personal_access_token = cfg.new_relic_personal_access_token


class ServiceBronze:
    def __init__(self):
        self.spark = SparkSession.builder.getOrCreate()
        self.new_relic_personal_access_token = new_relic_personal_access_token
        self.ACCOUNT_ID = ACCOUNT_ID
        self.headers = {'Content-Type': 'application/json', 'API-Key': self.new_relic_personal_access_token}
        self.API_URL = 'https://api.newrelic.com/graphql'
        self.max_retries = 20
        self.delay = 5
        self.billing = cfg.billing_account_id
        
        # Oblicz zakres: poprzedni dzień
        self.today = datetime.date.today()
        self.timestamp_date = self.today
        self.yesterday = self.today - datetime.timedelta(days=1)

        # for manual checkings
        # self.today = pd.to_datetime('2025-08-05').date()
       
        self.current_month = self.today.month
        self.current_year = self.today.year

        self.previous_month = self.current_month - 1
        self.previous_year = self.yesterday.year

        self.start_time = self.yesterday.isoformat()
        self.end_time = self.today.isoformat()

        self.covered_month = self.yesterday.month
        self.covered_year = self.yesterday.year
        
        self.cov_day = self.today - datetime.timedelta(days=1)


        # for manual checkings
        # self.today = pd.to_datetime('2025-08-05').date()
        self.nrql_percentage_query = cfg.nrql_percentage_query
        # neuron monthly
        self.overall_success_rate_neuron_us = cfg.overall_success_rate_neuron_us

        self.overall_success_rate_neuron_eun = cfg.overall_success_rate_neuron_eun
        
        self.documents_stuck_in_ai_all = cfg.documents_stuck_in_ai_all

        self.no_of_entered_docs = cfg.no_of_entered_docs
        self.new_relic_personal_access_token = new_relic_personal_access_token

        #vision monthly
        
        self.overall_succ_rate_of_vis_us_q = cfg.overall_succ_rate_of_vis_us
        
        self.overall_succ_rate_of_vis_eun_q = cfg.overall_succ_rate_of_vis_eun

        self.stuck_docu_count_eun = cfg.stuck_docu_count_eun
        
        self.stuck_docu_count_us = cfg.stuck_docu_count_us

        self.avg_time_successful_docu_us = cfg.avg_time_successful_docu_us
        
        self.avg_time_successful_docu_eun = cfg.avg_time_successful_docu_eun
        self.new_relic_personal_access_token = new_relic_personal_access_token

######################################################################
        # self.today = pd.to_datetime('2025-08-17').date()
        # self.current_month = datetime.date.today().month
        # self.current_year = datetime.date.today().year

        # self.previous_month = self.current_month - 1
        
        
        # self.yesterday = self.today - datetime.timedelta(days=1)
        # self.start_time = self.yesterday.isoformat()
        # self.end_time = self.today.isoformat()
        # self.current_date = datetime.datetime.now().date()
        # self.previous_year = self.yesterday.year

        # neuron daily
        # current day - 1 - covered day
        self.avg_neuron_end_to_end_duration_us = f"SELECT SUM(duration) / COUNT(duration) as 'Overall Duration in Neuron (in seconds)' FROM (SELECT filter(MIN(timestamp), WHERE `message` like '%MLOpsTrigger: Completed Processing data for ReferenceID:%' and cluster_name = 'aksshared-sharedprod-aks-use' AND namespace_name = 'neuroncore-prod') / 1000 - filter(MIN(timestamp), WHERE `message` like '%AxonNeuron: Started posting data to % queue for ReferenceID: %' and cluster_name = 'aksshared-sharedprod-aks-use' AND namespace_name = 'neuroncore-prod') / 1000 as duration FROM Log WHERE `Duration (in seconds)` != '' FACET CorrelationId LIMIT MAX) WHERE duration > 0 \
        SINCE '{self.yesterday}' UNTIL '{self.end_time}'"

        self.avg_neuron_end_to_end_duration_eun = f"SELECT SUM(duration) / COUNT(duration) as 'Overall Duration in Neuron (in seconds)' FROM (SELECT filter(MIN(timestamp), WHERE `message` like '%MLOpsTrigger: Completed Processing data for ReferenceID:%' and cluster_name = 'aksshared-sharedprod-aks-use' AND namespace_name = 'neuroncore-prod') / 1000 - filter(MIN(timestamp), WHERE `message` like '%AxonNeuron: Started posting data to % queue for ReferenceID: %' and cluster_name = 'aksshared-sharedprod-aks-use' AND namespace_name = 'neuroncore-prod') / 1000 as duration FROM Log WHERE `Duration (in seconds)` != '' FACET CorrelationId LIMIT MAX) WHERE duration > 0 \
        SINCE '{self.yesterday}' UNTIL '{self.end_time}'"
        self.new_relic_personal_access_token = new_relic_personal_access_token

        #vision daily for manual checkings
        # self.cov_day = 19
        # self.timestamp_date = self.cov_day + 1

        # self.avg_time_successful_docu_us = f"SELECT SUM(duration) / COUNT(duration) as 'Average Duration (in seconds)' FROM (SELECT filter(MIN(timestamp), WHERE `message` like 'SuccessCallback to % endpoint' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.ResponseHandler.Api') / 1000 - filter(MIN(timestamp), WHERE `message` like 'DocumentProcess API received a request for DocumentId: %, File Extension: %, Priority: %' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod') / 1000 as duration FROM Log WHERE `Duration (in seconds)` != '' FACET CorrelationId LIMIT MAX) WHERE duration > 0 \
        # SINCE '2025-08-{self.cov_day}' until '2025-08-{self.timestamp_date}'"
        
        # self.avg_time_successful_docu_eun = f"SELECT SUM(duration) / COUNT(duration) as 'Average Duration (in seconds)' FROM (SELECT filter(MIN(timestamp), WHERE `message` like 'SuccessCallback to % endpoint' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.ResponseHandler.Api') / 1000 - filter(MIN(timestamp), WHERE `message` like 'DocumentProcess API received a request for DocumentId: %, File Extension: %, Priority: %' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod') / 1000 as duration FROM Log WHERE `Duration (in seconds)` != '' FACET CorrelationId LIMIT MAX) WHERE duration > 0 \
        # SINCE '2025-08-{self.cov_day}'  until '2025-08-{self.timestamp_date}'"

        # self.total_doc_entered_vision_us = f"SELECT uniqueCount(CorrelationId) as 'Documents' FROM Log WHERE `message` like 'DocumentProcess API received a request for DocumentId:%' and cluster_name = 'aksshared-sharedprod-aks-use' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.DocumentProcess.Api' \
        # SINCE '2025-08-{self.cov_day}' until '2025-08-{self.timestamp_date}'"
        
        # self.total_doc_entered_vision_eun = f"SELECT uniqueCount(CorrelationId) as 'Documents' FROM Log WHERE `message` like 'DocumentProcess API received a request for DocumentId:%' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.DocumentProcess.Api' \
        # SINCE '2025-08-{self.cov_day}' until '2025-08-{self.timestamp_date}'"


        self.avg_time_successful_docu_us = f"SELECT SUM(duration) / COUNT(duration) as 'Average Duration (in seconds)' FROM (SELECT filter(MIN(timestamp), WHERE `message` like 'SuccessCallback to % endpoint' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.ResponseHandler.Api') / 1000 - filter(MIN(timestamp), WHERE `message` like 'DocumentProcess API received a request for DocumentId: %, File Extension: %, Priority: %' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod') / 1000 as duration FROM Log WHERE `Duration (in seconds)` != '' FACET CorrelationId LIMIT MAX) WHERE duration > 0 \
        SINCE '{self.cov_day}' until '{self.timestamp_date}'"
        
        self.avg_time_successful_docu_eun = f"SELECT SUM(duration) / COUNT(duration) as 'Average Duration (in seconds)' FROM (SELECT filter(MIN(timestamp), WHERE `message` like 'SuccessCallback to % endpoint' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.ResponseHandler.Api') / 1000 - filter(MIN(timestamp), WHERE `message` like 'DocumentProcess API received a request for DocumentId: %, File Extension: %, Priority: %' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod') / 1000 as duration FROM Log WHERE `Duration (in seconds)` != '' FACET CorrelationId LIMIT MAX) WHERE duration > 0 \
        SINCE '{self.cov_day}'  until '{self.timestamp_date}'"

        self.total_doc_entered_vision_us = f"SELECT uniqueCount(CorrelationId) as 'Documents' FROM Log WHERE `message` like 'DocumentProcess API received a request for DocumentId:%' and cluster_name = 'aksshared-sharedprod-aks-use' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.DocumentProcess.Api' \
        SINCE '{self.cov_day}' until '{self.timestamp_date}'"
        
        self.total_doc_entered_vision_eun = f"SELECT uniqueCount(CorrelationId) as 'Documents' FROM Log WHERE `message` like 'DocumentProcess API received a request for DocumentId:%' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.DocumentProcess.Api' \
        SINCE '{self.cov_day}' until '{self.timestamp_date}'"
        
        # #vision daily
        # self.avg_time_successful_docu_us = f"SELECT SUM(duration) / COUNT(duration) as 'Average Duration (in seconds)' FROM (SELECT filter(MIN(timestamp), WHERE `message` like 'SuccessCallback to % endpoint' and cluster_name = 'aksshared-sharedprod-aks-use' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.ResponseHandler.Api') / 1000 - filter(MIN(timestamp), WHERE `message` like 'DocumentProcess API received a request for DocumentId: %, File Extension: %, Priority: %' and cluster_name = 'aksshared-sharedprod-aks-use' and namespace_name = 'phlexvision-prod') / 1000 as duration FROM Log WHERE `Duration (in seconds)` != '' FACET CorrelationId LIMIT MAX) WHERE duration > 0 \
        # SINCE yesterday until today"
        
        # self.avg_time_successful_docu_eun = f"SELECT SUM(duration) / COUNT(duration) as 'Average Duration (in seconds)' FROM (SELECT filter(MIN(timestamp), WHERE `message` like 'SuccessCallback to % endpoint' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod' and applicationName = 'PhlexVision.ResponseHandler.Api') / 1000 - filter(MIN(timestamp), WHERE `message` like 'DocumentProcess API received a request for DocumentId: %, File Extension: %, Priority: %' and cluster_name = 'aksshared-sharedprod-aks-eun' and namespace_name = 'phlexvision-prod') / 1000 as duration FROM Log WHERE `Duration (in seconds)` != '' FACET CorrelationId LIMIT MAX) WHERE duration > 0 \
        # SINCE yesterday until today"



    def test_billing(self):
        graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                  nrql(query: "{self.billing}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
        response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
        response_json = response.json()
        return response_json
        
    def nrql_percentage(self):
        
        error = True
        retry_count = 0
        
        while error and retry_count < self.max_retries:
            
            time.sleep(self.delay)
            retry_count += 1
            graphql_query = f"""
                {{
                  actor {{
                    account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.nrql_percentage_query}") {{
                        results
                      }}
                    }}
                  }}
                }}
                """
    
                    
            response_data = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response_data.json()

            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
            else:
                error = False
                percentage = response_data.get('data', {}) \
                                                    .get('actor', {}) \
                                                    .get('account', {}) \
                                                    .get('nrql', {}) \
                                                    .get('results', [{}])[0] \
                                                    .get('percentage', 0.0)
                                
                new_relic_data = pd.DataFrame([{'percentage': percentage, 'timestamp_date': self.today}])
                new_relic_data['percentage'] = new_relic_data['percentage'].astype(float)

        spark_df = self.spark.createDataFrame(new_relic_data)             
        return new_relic_data

    # neuron monthly    
    def success_of_neuron_us(self):
        error_occurred = True
        retry_count = 0
        max_retries = 20
        
        while error_occurred and retry_count < max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.overall_success_rate_neuron_us}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if (response_data.get('errors') or 
                response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None):
                
                error_occurred = True
                print(f"Got error, retrying in 15 seconds... (Attempt {retry_count}/{max_retries})")
                
            else:
                error_occurred = False
                
                success_of_neuron_us = response_data.get('data', {}) \
                                              .get('actor', {}) \
                                              .get('account', {}) \
                                              .get('nrql', {}) \
                                              .get('results', [{}])[0] \
                                              .get('Success rate of Neuron', 0.0)
                
                success_of_neuron_us_data = pd.DataFrame([{ 'metrics_name':'Success rate of Neuron US', 
                                            'value': success_of_neuron_us, 
                                            'timestamp_date': self.today,
                                            'region':'US',
                                         'covered_month': self.previous_month,
                                                            'covered_year': self.previous_year,
                                          'is_first_day': True if self.today == 1 else False}])
                success_of_neuron_us_data['value'] = success_of_neuron_us_data['value'].astype(float)
                
                print(f"Success! Got value: {success_of_neuron_us}")
                spark_df = self.spark.createDataFrame(success_of_neuron_us_data)
                return spark_df
                
        
        # If we exit the loop due to max retries being reached
        if retry_count >= max_retries:
            print('No data fetched after 20 retries')
            return None

    def success_of_neuron_eun(self):
        error_occurred = True
        retry_count = 0
        max_retries = 20
        
        while error_occurred and retry_count < max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.overall_success_rate_neuron_eun}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if (response_data.get('errors') or 
                response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None):
                
                error_occurred = True
                print(f"Got error, retrying in 15 seconds... (Attempt {retry_count}/{max_retries})")
                
            else:
                error_occurred = False
                
                success_of_neuron_eun = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Success rate of Neuron', 0.0)
                
                success_of_neuron_eun_data = pd.DataFrame([{ 'metrics_name':'Success rate of Neuron EUN', 
                                                             'value': success_of_neuron_eun, 
                                                             'timestamp_date': self.today
                                                           , 'region':'EUN'
                                                           ,'covered_month': self.previous_month,
                                                             'covered_year': self.previous_year,
                                          'is_first_day': True if self.today == 1 else False}])
                success_of_neuron_eun_data['value'] = success_of_neuron_eun_data['value'].astype(float)
                
                print(f"Success! Got value: {success_of_neuron_eun}")
                spark_df = self.spark.createDataFrame(success_of_neuron_eun_data)
                return spark_df
        
        # If we exit the loop due to max retries being reached
        if retry_count >= max_retries:
            print('No data fetched after 20 retries')
            return None


    def documents_stuck_in_ai(self):
        error_occurred = True
        retry_count = 0
        max_retries = 20
        
        while error_occurred and retry_count < max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.documents_stuck_in_ai_all}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if (response_data.get('errors') or 
                response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None):
                
                error_occurred = True
                print(f"Got error, retrying in 15 seconds... (Attempt {retry_count}/{max_retries})")
                
            else:
                error_occurred = False
                
                documents_stuck_in_ai_value_all = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('AI', 0.0)
                
                documents_stuck_in_ai_all_data = pd.DataFrame([{ 'metrics_name':'Documents Stuck in AI (Both Prod regions) ALL', 
                                                                 'value': documents_stuck_in_ai_value_all, 
                                                                 'timestamp_date': self.today
                                                               , 'region':'ALL'
                                                               ,'covered_month': self.previous_month,
                                                                 'covered_year': self.previous_year,
                                          'is_first_day': True if self.today == 1 else False}])
                documents_stuck_in_ai_all_data['value'] = documents_stuck_in_ai_all_data['value'].astype(float)
                
                print(f"Success! Got value: {documents_stuck_in_ai_value_all}")
                spark_df = self.spark.createDataFrame(documents_stuck_in_ai_all_data)
                return spark_df
        
        # If we exit the loop due to max retries being reached
        if retry_count >= max_retries:
            print('No data fetched after 20 retries')
            return None
          
    def no_of_entered_documents(self):
        error_occurred = True
        retry_count = 0
        max_retries = 20
        
        while error_occurred and retry_count < max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.no_of_entered_docs}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if (response_data.get('errors') or 
                response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None):
                
                error_occurred = True
                print(f"Got error, retrying in 15 seconds... (Attempt {retry_count}/{max_retries})")
                
            else:
                error_occurred = False
                
                no_of_entered_documents_all = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('No Of Docs Entered Neuron', 0.0)
                
                documents_stuck_in_ai_all_data = pd.DataFrame([{ 'metrics_name':'No Of Docs Entered Neuron ALL', 
                                                                 'value': no_of_entered_documents_all, 
                                                                 'timestamp_date': self.today
                                                               , 'region':'ALL'
                                                               ,'covered_month': self.previous_month,
                                                                 'covered_year': self.previous_year,
                                          'is_first_day': True if self.today == 1 else False}])
                documents_stuck_in_ai_all_data['value'] = documents_stuck_in_ai_all_data['value'].astype(float)

                # documents_stuck_in_ai_all_data = pd.DataFrame([{ 'metrics_name':'No Of Docs Entered Neuron ALL', 
                #                                                  'value': documents_stuck_in_ai_value_all, 
                #                                                  'timestamp_date': self.today
                #                                                , 'region':'ALL'
                #                                                ,'covered_month': 6,
                #                                                  'covered_year': 2025,
                #                           'is_first_day': True}])
                documents_stuck_in_ai_all_data['value'] = documents_stuck_in_ai_all_data['value'].astype(float)
                
                print(f"Success! Got value: {no_of_entered_documents_all}")
                spark_df = self.spark.createDataFrame(documents_stuck_in_ai_all_data)     
                return spark_df
        
        # If we exit the loop due to max retries being reached
        if retry_count >= max_retries:
            print('No data fetched after 20 retries')
            return None

# neuron daily
    
    def avg_neuron_e2e_duration_us(self):
        error_occurred = True
        retry_count = 0
        max_retries = 20
        
        while error_occurred and retry_count < max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.avg_neuron_end_to_end_duration_us}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if (response_data.get('errors') or 
                response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None):
                
                error_occurred = True
                print(f"Got error, retrying in 15 seconds... (Attempt {retry_count}/{max_retries})")
                
            else:
                error_occurred = False
                
                avg_neuron_e2e_duration_us = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Overall Duration in Neuron (in seconds)', 0.0)
                
                avg_neuron_e2e_duration_us_data = pd.DataFrame([{ 'metrics_name':'Overall Duration in Neuron (in seconds) US'
                                                                  ,'value': avg_neuron_e2e_duration_us
                                                                    ,'timestamp_date': self.today
                                                                   ,'covered_date': self.yesterday
                                                                , 'region':'US'
                                                                   , 'covered_month' : self.covered_month
                                                                   , 'covered_year' : self.covered_year
                                                                  ,'is_first_day': True if self.today == 1 else False}])
                avg_neuron_e2e_duration_us_data['value'] = avg_neuron_e2e_duration_us_data['value'].astype(float)
                
                print(f"Success! Got value: {avg_neuron_e2e_duration_us}")
                spark_df = self.spark.createDataFrame(avg_neuron_e2e_duration_us_data)    
                return spark_df
        
        # If we exit the loop due to max retries being reached
        if retry_count >= max_retries:
            print('No data fetched after 20 retries')
            return None
    
    def avg_neuron_e2e_duration_eun(self):
        error_occurred = True
        retry_count = 0
        max_retries = 20
        
        while error_occurred and retry_count < max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.avg_neuron_end_to_end_duration_eun}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if (response_data.get('errors') or 
                response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None):
                
                error_occurred = True
                print(f"Got error, retrying in 15 seconds... (Attempt {retry_count}/{max_retries})")
                
            else:
                error_occurred = False
                
                avg_neuron_e2e_duration_eun = response_data.get('data', {}) \
                                              .get('actor', {}) \
                                              .get('account', {}) \
                                              .get('nrql', {}) \
                                              .get('results', [{}])[0] \
                                              .get('Overall Duration in Neuron (in seconds)', 0.0)
                
                avg_neuron_e2e_duration_eun_data = pd.DataFrame([{ 'metrics_name':'Overall Duration in Neuron (in seconds) EUN'
                                                                   ,'value': avg_neuron_e2e_duration_eun
                                                                , 'timestamp_date': self.today
                                                                  , 'covered_date': self.yesterday
                                                                 , 'region':'EUN'
                                                                   , 'covered_month' : self.covered_month
                                                                   , 'covered_year' : self.covered_year
                                                                   ,'is_first_day': True if self.today == 1 else False}])
                avg_neuron_e2e_duration_eun_data['value'] = avg_neuron_e2e_duration_eun_data['value'].astype(float)
                
                print(f"Success! Got value: {avg_neuron_e2e_duration_eun}")
                spark_df = self.spark.createDataFrame(avg_neuron_e2e_duration_eun_data)    
                return spark_df
        
        # If we exit the loop due to max retries being reached
        if retry_count >= max_retries:
            print('No data fetched after 20 retries')
            return None
    
    def overall_succ_rate_of_vis_us(self):
        error = True
        retry_count = 0
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            osr_graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.overall_succ_rate_of_vis_us_q}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': osr_graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                
                success_rate_vision_us = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Success rate of Vision', 0.0)
                
                success_rate_vision_us_data = pd.DataFrame([{ 'metrics_name':'Success rate of Vision US', 'value': success_rate_vision_us, 'timestamp_date': self.today, 'region':'US'}])
                success_rate_vision_us_data['value'] = success_rate_vision_us_data['value'].astype(float)
                
                print(f"ok: {success_rate_vision_us}")
                spark_df = self.spark.createDataFrame(success_rate_vision_us_data)  
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None
    
    def overall_succ_rate_of_vis_eun(self):
        error = True
        retry_count = 0
        max_retries = 20
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            osreun_graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.overall_succ_rate_of_vis_eun_q}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': osreun_graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                
                success_rate_vision_eun = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Success rate of Vision', 0.0)
                
                success_rate_vision_eun_data = pd.DataFrame([{ 'metrics_name':'Success rate of Vision EUN', 'value': success_rate_vision_eun, 'timestamp_date': self.today, 'region':'EU'}])
                success_rate_vision_eun_data['value'] = success_rate_vision_eun_data['value'].astype(float)
                
                print(f"ok: {success_rate_vision_eun}")
                spark_df = self.spark.createDataFrame(success_rate_vision_eun_data)  
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None

    def documents_us_data(self):
        error = True
        retry_count = 0
        max_retries = 20
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            dusd_graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.stuck_docu_count_us}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': dusd_graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                
                documents_us = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Documents', 0.0)
                
                documents_us_data = pd.DataFrame([{ 'metrics_name':'Documents US', 'value': documents_us, 'timestamp_date': self.today, 'region':'US'}])
                documents_us_data['value'] = documents_us_data['value'].astype(float)
                
                print(f"ok: {documents_us}")
                spark_df = self.spark.createDataFrame(documents_us_data)  
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None
    
    def documents_eun_data(self):
        error = True
        retry_count = 0
        max_retries = 20
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            deund_graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.stuck_docu_count_eun}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': deund_graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                
                documents_eun = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Documents', 0.0)
                
                documents_eun_data = pd.DataFrame([{ 'metrics_name':'Documents EUN', 'value': documents_eun, 'timestamp_date': self.today, 'region':'EU'}])
                documents_eun_data['value'] = documents_eun_data['value'].astype(float)
                
                print(f"ok: {documents_eun}")
                spark_df = self.spark.createDataFrame(documents_eun_data)  
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None
    
    def avg_duraiton_us(self):
        error = True
        retry_count = 0
        max_retries = 20
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.avg_time_successful_docu_us}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                
                avg_duraiton_us = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Average Duration (in seconds)', 0.0)
                
                avg_duraiton_us_data = pd.DataFrame([{ 'metrics_name':'Average Duration (in seconds) US', 'value': avg_duraiton_us, 'timestamp_date': self.start_time, 'region':'US'}])
                
                print(f"ok: {avg_duraiton_us}")
                spark_df = self.spark.createDataFrame(avg_duraiton_us_data)  
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None
    
    def avg_duraiton_eun(self):
        error = True
        retry_count = 0
        max_retries = 20
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.avg_time_successful_docu_eun}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                
                avg_duraiton_eun = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Average Duration (in seconds)', 0.0)
                
                avg_duraiton_eun_data = pd.DataFrame([{
                    'metrics_name':'Average Duration (in seconds) EUN', 
                    'value': avg_duraiton_eun, 
                    'timestamp_date': self.start_time, 'region':'EU'
                }])
                
                print(f"ok: {avg_duraiton_eun}")
                spark_df = self.spark.createDataFrame(avg_duraiton_eun_data) 
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None
        
    def documents_entered_us(self):
        error = True
        retry_count = 0
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            dusd_graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.total_doc_entered_vision_us}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': dusd_graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                documents_us = response_data.get('data', {}) \
                                      .get('actor', {}) \
                                      .get('account', {}) \
                                      .get('nrql', {}) \
                                      .get('results', [{}])[0] \
                                      .get('Documents', 0.0)
                
                documents_us_data = pd.DataFrame([{ 'metrics_name':'Documents entered US', 'value': documents_us, 'timestamp_date': self.cov_day,'region':'US'}])
                documents_us_data['value'] = documents_us_data['value'].astype(float)
                
                print(f"ok: {documents_us}")
                spark_df = self.spark.createDataFrame(documents_us_data) 
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None

    def documents_entered_eun(self):
        error = True
        retry_count = 0
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            dusd_graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.total_doc_entered_vision_eun}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': dusd_graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                documents_us = response_data.get('data', {}) \
                                      .get('actor', {}) \
                                      .get('account', {}) \
                                      .get('nrql', {}) \
                                      .get('results', [{}])[0] \
                                      .get('Documents', 0.0)
                
                documents_eun_data = pd.DataFrame([{ 'metrics_name':'Documents entered EUN', 'value': documents_us, 'timestamp_date': self.cov_day,'region':'EU'}])
                documents_eun_data['value'] = documents_eun_data['value'].astype(float)
                
                print(f"ok: {documents_us}")
                spark_df = self.spark.createDataFrame(documents_eun_data) 
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None
        
    def avg_duraiton_us(self):
        error = True
        retry_count = 0
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.avg_time_successful_docu_us}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                
                avg_duraiton_us = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Average Duration (in seconds)', 0.0)
                
                avg_duraiton_us_data = pd.DataFrame([{ 'metrics_name':'Average Duration (in seconds) US', 'value': avg_duraiton_us, 'timestamp_date': self.cov_day, 'region':'US'}])
                
                print(f"ok: {avg_duraiton_us}")
                spark_df = self.spark.createDataFrame(avg_duraiton_us_data) 
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None
    
    def avg_duraiton_eun(self):
        error = True
        retry_count = 0
        
        while error and retry_count < self.max_retries:
            time.sleep(15)
            retry_count += 1
            
            graphql_query = f"""
            {{
              actor {{
                account(id: {self.ACCOUNT_ID}) {{
                      nrql(query: "{self.avg_time_successful_docu_eun}") {{
                    results
                  }}
                }}
              }}
            }}
            """
            
            response = requests.post(self.API_URL, json={'query': graphql_query}, headers=self.headers)
            response_data = response.json()
            print(response_data)
            
            if response_data.get('data', {}).get('actor', {}).get('account', {}).get('nrql') is None:
                
                error = True
                print(f"error, retry number ({retry_count}/{self.max_retries})")
                
            else:
                error = False
                
                avg_duraiton_eun = response_data.get('data', {}) \
                                          .get('actor', {}) \
                                          .get('account', {}) \
                                          .get('nrql', {}) \
                                          .get('results', [{}])[0] \
                                          .get('Average Duration (in seconds)', 0.0)
                
                avg_duraiton_eun_data = pd.DataFrame([{
                    'metrics_name':'Average Duration (in seconds) EUN', 
                    'value': avg_duraiton_eun, 
                    'timestamp_date': self.cov_day, 'region':'EU'
                }])
                
                print(f"ok: {avg_duraiton_eun}")
                spark_df = self.spark.createDataFrame(avg_duraiton_eun_data) 
                return spark_df
        
        if retry_count >= self.max_retries:
            print(f'No data after {self.max_retries} retries')
            return None

    