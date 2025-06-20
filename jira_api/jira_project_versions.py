def get_jira_project_versions():
    
    import requests
    import pandas as pd
    import json
    from datetime import datetime
    import time
    from snowflake.snowpark.context import get_active_session
    from requests.auth import HTTPBasicAuth
    time.sleep(1)
    
    results = get_active_session().sql("SELECT PROD.RAW.jira_username()").collect()
    jira_username = results[0][0]

    results = get_active_session().sql("SELECT PROD.RAW.jira_api_token()").collect()
    jira_api_token = results[0][0]

    if not jira_username or not jira_api_token:
        return {"status": "error", "message": "Missing credentials"}

 


    headers = {
    "Accept": "application/json"
    }

    params = {
        "expand": 'description,projectKeys,lead,issueTypes,url,insight,deletedby'
    }

    response = requests.get(
    url = "https://xxz.atlassian.net/rest/api/3/project",
    headers=headers,
    auth=HTTPBasicAuth(jira_username, jira_api_token),
    params=params
    )

    projects = pd.DataFrame(response.json())

    projects_unique = projects['id'].astype(str).unique().tolist()

    all_versions = []

    for i in projects_unique:
        start_at = 0
        is_last = False

        while not is_last:

            headers = {
                "Accept": "application/json"
            }

            params = {
                'startAt': start_at,
                'maxResults': 50
            }

            response = requests.get(
            url = f"https://xxz.atlassian.net/rest/api/3/project/{i}/version",
            headers=headers, 
            auth=HTTPBasicAuth(jira_username, jira_api_token), 
            params=params)
            data = response.json()

            sprints_batch = data.get('values', [])
            all_versions.extend(sprints_batch)

            is_last = data.get('isLast', True)
            start_at += len(sprints_batch)

    # Wrzuć wszystko do DataFrame
    sprints_df = pd.DataFrame(all_versions)
    return sprints_df
