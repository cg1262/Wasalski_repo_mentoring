import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json
from snowflake.snowpark.context import get_active_session

class Jira():
    def __init__(self):
        session = get_active_session()
        self.jira_username = session.sql("SELECT PROD.RAW.jira_username()").collect()[0][0]
        self.jira_api_token = session.sql("SELECT PROD.RAW.jira_api_token()").collect()[0][0]
        self.auth=HTTPBasicAuth(self.jira_username, self.jira_api_token)
        self.headers = {
            "Accept": "application/json"
        }

    def get_jira_issue_fields(self):
        """

        """
        url = 'https://xxz.atlassian.net/rest/api/3/field'
        response = requests.get(
            url = url,
            headers=self.headers,
            auth=self.auth
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch issue fields: {response.status_code} - {response.text}")
        else:
            data_issue_fields = pd.DataFrame(response.json())

        return data_issue_fields
    
    def get_jira_boards(self, startAt, maxResults):
        """

        """
        
        url="https://xxz.atlassian.net/rest/agile/1.0/board"

        # pagination - to be considered stored as a function because it is used with other endpoints
        startAt = 0
        maxResults = 50
        all_boards = []
        

        while True:

            headers = self.headers,
            params = {
                "startAt": startAt,
                "maxResults": maxResults
            }

            response = requests.get(
                url= url,
                headers=headers,
                auth=self.auth,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                all_boards.extend(data.get("values", []))
                if data.get("isLast", True):
                    break
                startAt += maxResults
            else:
                print(f"Błąd {response.status_code}: {response.text}")
                break
        # end of pagination
        
        if all_boards:
            data_all_boards = pd.DataFrame(all_boards)
            data_all_boards.reset_index()

        return data_all_boards
