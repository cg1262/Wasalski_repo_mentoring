# Databricks notebook source
import requests
import pandas as pd
import time
import json

class CheckmarxAPI:
    """
    """
    def __init__(self):
        
        self.token_url = "https://us.iam.checkmarx.net/auth/realms/cor/protocol/openid-connect/token" #url for token retrieval
        # self.api_key = os.getenv("LUKE_API_KEY")  # API read from local env
        self.jwt = None
        self.token_timestamp = None  # Track when token was obtained. Token expires in 30 minutes so we need to be ahead of that.
        self.token_refresh_threshold = 28 * 60  # 28 minutes in seconds
        self.limit = 100
        self.api_key = results
        
    # token part
    def get_jwt_token(self):
        """
        - retrieving jwt token to authenticate API requests with automatic refresh
        - if the token is older than the refresh threshold (28 minutes) we need to get a new one
        - otherwise we can use the existing token
        - returns the JWT token as a string
        - JWT token is crucial to get access_token for API requests
        """
        # Check if we need to refresh token
        if self.token_timestamp: # if it's True / not None
            elapsed_time = time.time() - self.token_timestamp # Calculate elapsed time since token was obtained
            if elapsed_time < self.token_refresh_threshold: # If token is still valid (less than 28 minutes old)
                return self.jwt  # Token is still valid, return existing token 
        
        # getting new access token
        payload = {
            "grant_type": "refresh_token",
            "client_id": "ast-app", 
            "refresh_token": self.api_key
        }
            
        response = requests.post(self.token_url, data=payload) # POST to get new token
        # response.raise_for_status()  # Raise an error for bad responses
        self.jwt = response.json().get('access_token') # extracting token from response and assigning to self.jwt
        
        if response.status_code != 200 or not self.jwt: # double check if we got the token
            print("Check it, status code:", response.status_code)
            return None
        else:
            self.token_timestamp = time.time()
            return self.jwt
    
    # data part
    def get_applications(self):
        """
        Retrieve all applications using pagination to handle large datasets.
        
        - API returns max 100 applications per request (our limit = 100)
        - if we have i.e. 143 total applications, we need 2 requests:
          request 1: offset=0, limit=100 → gets applications 1-100 (100 returned)
          request 2: offset=100, limit=100 → gets applications 101-143 (43 returned)
        - no more iteration when count < limit (43 < 100 = last page)
        """
        # Get valid authentication token
        if not self.get_jwt_token():
            return pd.DataFrame()  # creating empty df if auth fails

        applications_endpoint = "https://us.ast.checkmarx.net/api/applications"
        headers = {
            "Authorization": f"{self.jwt}",
            "Accept": "application/json; version=1.0"
        }
        
        # pagination variables
        applications_offset = 0  # offset for pagination, to be increased by limit each loop
        all_applications = []    # master list to collect all applications across pages
        
        try:
            while True:
                params = {
                    "limit": self.limit,      
                    "offset": applications_offset 
                }
                
                response = requests.get(
                    applications_endpoint, 
                    headers=headers, 
                    params=params)
                
                response.raise_for_status()  # error if HTTP request failed
    
                data = response.json()

                applications = data.get('applications', [])  
                
                if not applications: # if empty
                    break
                    
                # adding this page's applications to our master list
                all_applications.extend(applications)
                
                # preparing for next page
                applications_offset += self.limit  # moving offset forward (0→100→200)
                
                # check if this was the last page
                if len(applications) < self.limit:
                    break
            
            
            return pd.DataFrame(all_applications)
        # instead of throwing an error, we catch it and return empty DataFrame so snowflake notebook doesn't break
        except requests.RequestException as e:
            print(f"error: {e}")
            return pd.DataFrame()  # return empty DataFrame on any error
        
    def get_scans(self):
        """
        Retrieve all scans using pagination to handle large datasets.
        
        - API returns max 100 scans per request (our limit = 100)
        - If there are i.e. 320 total scans, we need 4 requests:
          Request 1: offset=0, limit=100 → gets scans 1-100 (100 returned)
          Request 2: offset=100, limit=100 → gets scans 101-200 (100 returned)
        - We stop when returned count < limit (20 < 100 = last page)
        """
        # Get valid authentication token
        if not self.get_jwt_token():
            return pd.DataFrame()  # Returns empty dataframe if auth fails
    
        scans_endpoint = "https://us.ast.checkmarx.net/api/scans"
        headers = {
            "Authorization": f"{self.jwt}",
            "Accept": "application/json; version=1.0"
        }
        
        # pagination variables
        scans_offset = 0  # offset for pagination, to be increased by limit each loop
        all_scans = []    # master list to collect all scans across pages
        
        try: 
            while True:
                params = {
                    "limit": self.limit, 
                    "offset": scans_offset
                }
                
                response = requests.get(scans_endpoint, headers=headers, params=params)
                # response.raise_for_status()  # we could uncomment this for stricter error handling
                
                data = response.json()
                scans = data.get('scans', [])
                
                if not scans:
                    break
                    
                all_scans.extend(scans)
                
                scans_offset += self.limit  # moving offset forward (0>100>200)
                
                if len(scans) < self.limit:
                    break
            
            df_scans = pd.DataFrame(all_scans)
            if 'tags' in df_scans.columns:
                df_scans = df_scans.drop(columns='tags')
            return df_scans
        
        # instead of throwing an error, we catch it and return empty DataFrame so snowflake notebook doesn't break    
        except requests.RequestException as e:
            print(f"error: {e}")
            return pd.DataFrame()  # return empty DataFrame on any error

    def get_unique_scans(self):
        """
        """
        unique_scans = self.get_scans()['id'].unique().tolist()
        return unique_scans
    
                    
api = CheckmarxAPI()
jwt_token = api.get_jwt_token()