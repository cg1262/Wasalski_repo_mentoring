def get_jira_sprints():
    
    import requests
    from requests.auth import HTTPBasicAuth
    import json
    import pandas as pd
    startAt = 0
    maxResults = 50
    all_boards = []
    
    from snowflake.snowpark.context import get_active_session
    results = get_active_session().sql("SELECT PROD.RAW.jira_username()").collect()
    jira_username = results[0][0]

    results = get_active_session().sql("SELECT PROD.RAW.jira_api_token()").collect()
    jira_api_token = results[0][0]
    
    headers = {
        "Accept": "application/json"
    }

    # Fetch all boards
    while True:
        params = {
            "startAt": startAt,
            "maxResults": maxResults
        }

        response = requests.get(
            url="https://xxz.atlassian.net/rest/agile/1.0/board",
            headers=headers,
            auth=HTTPBasicAuth(jira_username, jira_api_token),
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

    # Extract board IDs from the all_boards list
    board_ids = [str(board['id']) for board in all_boards if 'id' in board]

    all_sprints = []

    # Fetch all sprints for each board
    for i in board_ids:
        start_at = 0  # Reset start_at for each board
        while True:
            url = f"https://xxz.atlassian.net/rest/agile/1.0/board/{i}/sprint"

            params = {
                "startAt": start_at,
                "maxResults": maxResults
            }

            headers = {
                "Accept": "application/json"
            }

            response = requests.get(
                url,
                headers=headers,
                auth=HTTPBasicAuth(jira_username, jira_api_token),
                params=params
            )

            if response.status_code != 200:
                print(f"Error for board {i}: {response.status_code}, {response.text}")
                break

            sprints = response.json()
            if not sprints.get("values"):  # No more sprints
                break
            all_sprints.extend(sprints.get("values", []))
            start_at += maxResults
            print(f"Board {i}. Status code: {response.status_code}, Retrieved {len(sprints.get('values', []))} sprints")
    all_sprints = pd.DataFrame(all_sprints)
    return all_sprints