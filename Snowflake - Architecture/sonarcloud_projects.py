def get_sonarcloud_projects():    # ---- # ---- Projects

    import requests
    import pandas as pd
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.sonarcloud_api_key()").collect()
    api_key = results[0][0]
    
    headers = {
    "Authorization": f"Bearer {api_key}",
    }

    # Parameters for query
    params = {
        "organization": "xxxz",
        "ps": 500,  # page size
        "p": 1      # page number
    }

    all_projects = []  # List to store all components
    total_results = 0  # Total number of results

    # Execute initial query to get the total number of results
    url_labels = "https://sonarcloud.io/api/projects/search"
    response_labels = requests.get(url_labels, headers=headers, params=params)
    labels_data = response_labels.json()

    # Get total number of results
    total_results = labels_data['paging']['total']
    total_pages = (total_results // params['ps']) + (1 if total_results % params['ps'] > 0 else 0)

    # Add components to the general list
    all_projects.extend(labels_data['components'])

    # Loop to collect data from each page, if there is more than one page
    while params["p"] < total_pages:
        params["p"] += 1  # Go to the next page
        response_labels = requests.get(url_labels, headers=headers, params=params)
        labels_data = response_labels.json()
        
        # Add components from the current page
        all_projects.extend(labels_data['components'])



    df_projects = pd.DataFrame(all_projects)

    new_order = ['organization', 'key', 'name', 'qualifier', 'visibility', 'lastAnalysisDate', 'revision']
    df_projects = df_projects[new_order]


    df_projects.columns = ['ORGANIZATION', 'KEY', 'NAME', 'QUALIFIER', 'VISIBILITY', 'LASTANALYSISDATE', 'REVISION']
    
    return df_projects