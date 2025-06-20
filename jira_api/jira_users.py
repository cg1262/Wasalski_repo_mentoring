def get_jira_users():

    import pandas as pd
    import requests
    from requests.auth import HTTPBasicAuth

    # Pagination setup
    start_at = 0
    max_results = 100
    all_users = []
    from snowflake.snowpark.context import get_active_session
    results = get_active_session().sql("SELECT PROD.RAW.jira_username()").collect()
    jira_username = results[0][0]

    results = get_active_session().sql("SELECT PROD.RAW.jira_api_token()").collect()
    jira_api_token = results[0][0]
    
    while True:
        params = {
            "startAt": start_at,
            "maxResults": max_results
        }
        response = requests.get(
            url = "https://xxz.atlassian.net/rest/api/3/users", 
            auth=HTTPBasicAuth(jira_username, jira_api_token), 
            params=params)
        
        users = response.json()
        
        if not users:
            break
        all_users.extend(users)
        start_at += max_results

    # Convert to DataFrame after fetching all users
    users_df = pd.DataFrame(all_users)
    return users_df
