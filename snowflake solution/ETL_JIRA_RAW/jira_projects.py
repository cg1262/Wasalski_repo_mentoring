def get_jira_projects():

    from requests.auth import HTTPBasicAuth
    from snowflake.snowpark.context import get_active_session
    import requests
    import pandas as pd
    
    results = get_active_session().sql("SELECT PROD.RAW.jira_username()").collect()
    jira_username = results[0][0]

    results = get_active_session().sql("SELECT PROD.RAW.jira_api_token()").collect()
    jira_api_token = results[0][0]


    # Auth and headers
    headers = {
        "Accept": "application/json"
    }

    # Query parameters
    params = {
        "expand": 'description,projectKeys,lead,issueTypes,url,insight,deletedby'
    }

    # Fetch projects
    response = requests.get(
        url = "https://phlexglobal.atlassian.net/rest/api/3/project",
        headers=headers,
        auth=HTTPBasicAuth(jira_username, jira_api_token),
        params=params
    )

    # Convert response to DataFrame
    projects = pd.DataFrame(response.json())

    # Ensure 'id' is numeric
    # projects['id'] = pd.to_numeric(projects['id'], errors='coerce').fillna(0).astype(int)
    projects = projects.drop(columns='properties')
    return projects



