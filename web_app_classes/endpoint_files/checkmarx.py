import requests
import pandas as pd

from dotenv import load_dotenv
import os

load_dotenv()

class CheckmarxAPI:
    """
    Class to interact with Checkmarx API using JWT authentication.
    """
    def __init__(self):
        # Initialize with required parameters
        self.token_url = "https://us.iam.checkmarx.net/auth/realms/cor/protocol/openid-connect/token" #url for token retrieval
        self.api_url = "https://us.ast.checkmarx.net/api" # Base URL for other endpoints
        self.api_key = os.getenv("LUKE_API_KEY")  # API
        # self.api_key = 'api key'
        self.jwt = None
        self.limit = 100

    def get_jwt_token(self):
        """
        retrieving jwt token
        """
        payload = {
                "grant_type": "refresh_token",
                "client_id": "ast-app",
                "refresh_token": self.api_key
        }
            
        response = requests.post(self.token_url, data=payload)
        self.jwt = response.json().get('access_token')
        if response.status_code != 200 or not self.jwt:
            print("Something is wrong, status code:", response.status_code)
        else:
            return self.jwt


    def get_applications(self):
        """
        Retrieve all applications with pagination.
        """
        if not self.jwt:
            self.get_jwt_token()
            if not self.jwt:
                print("Failed to obtain JWT token")

        applications_endpoint = f"{self.api_url}/applications"
        
        headers = {
            "Authorization": f"{self.jwt}",
            "Accept": "application/json; version=1.0"
        }
        
        offset = 0
        all_applications = []
        
        try:
            while True:
                params = {"limit": self.limit, "offset": offset}
                response = requests.get(applications_endpoint, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                applications = data.get('applications', [])
                
                if not applications:
                    break
                    
                all_applications.extend(applications)
                offset += self.limit
                
                if len(applications) < self.limit:
                    break
            
            return pd.DataFrame(all_applications)
            
        except requests.RequestException as e:
            print(f"Applications request error: {e}")
            return pd.DataFrame()
        
    def get_scans_2(self):
        """
        Retrieve all applications with pagination.
        """
        if not self.jwt:
            self.get_jwt_token()
            if not self.jwt:
                print("Failed to obtain JWT token")

        applications_endpoint = f"{self.api_url}/scans"
        
        headers = {
            "Authorization": f"{self.jwt}",
            "Accept": "application/json; version=1.0"
        }
        response = requests.get(applications_endpoint, headers=headers)
        data = response.json()
        return pd.DataFrame(data)

        # offset = 0
        # all_applications = []
        
        # try:
        #     while True:
        #         params = {"limit": self.limit, "offset": offset}
        #         response = requests.get(applications_endpoint, headers=headers, params=params)
        #         response.raise_for_status()
                
        #         data = response.json()
        #         applications = data.get('scans', [])
                
        #         if not applications:
        #             break
                    
        #         all_applications.extend(applications)
        #         offset += self.limit
                
        #         if len(applications) < self.limit:
        #             break
            
        #     return pd.DataFrame(all_applications)
            
        # except requests.RequestException as e:
        #     print(f"Applications request error: {e}")
        #     return pd.DataFrame()
        
    def get_scans(self):
        """
        Retrieve all applications with pagination.
        """
        if not self.jwt:
            self.get_jwt_token()
            if not self.jwt:
                print("Failed to obtain JWT token")

        applications_endpoint = f"{self.api_url}/scans"
        
        headers = {
            "Authorization": f"{self.jwt}",
            "Accept": "application/json; version=1.0"
        }
        
        offset = 0
        all_applications = []
        
        try:
            while True:
                params = {"limit": self.limit, "offset": offset}
                response = requests.get(applications_endpoint, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                applications = data.get('scans', [])
                
                if not applications:
                    break
                    
                all_applications.extend(applications)
                offset += self.limit
                
                if len(applications) < self.limit:
                    break
            
            return pd.DataFrame(all_applications)
            
        except requests.RequestException as e:
            print(f"Scans request error: {e}")
            return pd.DataFrame()
        
                    
# api = CheckmarxAPI()
# jwt_token = api.get_jwt_token()