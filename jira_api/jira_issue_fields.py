def get_jira_issue_fields():

  import pandas as pd
  import requests
  from requests.auth import HTTPBasicAuth
  import json
  from snowflake.snowpark.context import get_active_session
  results = get_active_session().sql("SELECT PROD.RAW.jira_username()").collect()
  jira_username = results[0][0]

  results = get_active_session().sql("SELECT PROD.RAW.jira_api_token()").collect()
  jira_api_token = results[0][0]
  headers = {
    "Accept": "application/json"
  }

  response = requests.get(
    url = 'https://xxz.atlassian.net/rest/api/3/field',
    headers=headers,
    auth=HTTPBasicAuth(jira_username, jira_api_token)
  )
  data = response.json()
  # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
  issue_fields = pd.DataFrame(data)

  return issue_fields