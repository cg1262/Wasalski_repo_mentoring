def get_jira_boards():
    """
    Fetches all Jira boards using the Jira Agile API with pagination.
    
    Args:
        username =
        api_token = 
        
    Returns:
        tuple: (DataFrame of all boards, list of unique board IDs)
    """
    from requests.auth import HTTPBasicAuth
    from snowflake.snowpark.context import get_active_session
    import requests
    import pandas as pd
    
    results = get_active_session().sql("SELECT PROD.RAW.jira_username()").collect()
    username = results[0][0]

    results = get_active_session().sql("SELECT PROD.RAW.jira_api_token()").collect()
    api_token = results[0][0]
    
    startAt = 0
    maxResults = 50
    all_boards = []
    auth = HTTPBasicAuth(username, api_token)

    while True:

        headers = {
        "Accept": "application/json"
        }
        params = {
            "startAt": startAt,
            "maxResults": maxResults
        }

        response = requests.get(
            url="https://xxz.atlassian.net/rest/agile/1.0/board",
            headers=headers,
            auth=auth,
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

    if all_boards:
        all_boards_df = pd.DataFrame(all_boards)
        all_boards_df.reset_index()
        return all_boards_df




def get_unique_boards():
    """
    Fetches all Jira boards using the Jira Agile API with pagination.
    
    Args:
        username =
        api_token = 
        
    Returns:
        tuple: (DataFrame of all boards, list of unique board IDs)
    """
    from requests.auth import HTTPBasicAuth
    from snowflake.snowpark.context import get_active_session
    import requests
    
    results = get_active_session().sql("SELECT PROD.RAW.jira_username()").collect()
    username = results[0][0]

    results = get_active_session().sql("SELECT PROD.RAW.jira_api_token()").collect()
    api_token = results[0][0]

    startAt = 0
    maxResults = 50
    all_boards = []
    auth = HTTPBasicAuth(username, api_token)

    while True:

        headers = {
        "Accept": "application/json"
        }
        params = {
            "startAt": startAt,
            "maxResults": maxResults
        }

        response = requests.get(
            url="https://phlexglobal.atlassian.net/rest/agile/1.0/board",
            headers=headers,
            auth=auth,
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

    if all_boards:
        all_boards_df = pd.DataFrame(all_boards)
        all_boards_df.reset_index()
        unique_boards = all_boards_df['id'].astype(str).unique().tolist()
        
        return unique_boards