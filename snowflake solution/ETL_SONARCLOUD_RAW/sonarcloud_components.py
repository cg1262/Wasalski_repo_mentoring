def get_sonarcloud_components():
    # ---- # ---- Components 
    import requests
    import pandas as pd
    import datetime 
    import time
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.sonarcloud_api_key()").collect()
    api_key = results[0][0]
    
    headers = {
    "Authorization": f"Bearer {api_key}",
    }
    params = {
        "organization": "phlexglobal",
        "ps": 500,  # page size
        "p": 1      # page number
    }

    all_components = []  # list to store all components

    total_results = 0 

    # Execute initial query to get the total number of results
    url_components = "https://sonarcloud.io/api/components/search"
    response_components = requests.get(url_components, headers=headers, params=params)
    components_data = response_components.json()

    # Get total number of results
    total_results = components_data['paging']['total']
    total_pages = (total_results // params['ps']) + (1 if total_results % params['ps'] > 0 else 0)

    # Add components to the general list
    all_components.extend(components_data['components'])

    # Loop to collect data from each page, if there is more than one page
    while params["p"] < total_pages:
        params["p"] += 1  # Go to the next page
        response_components = requests.get(url_components, headers=headers, params=params)
        components_data = response_components.json()
        
        # Add components from the current page
        all_components.extend(components_data['components'])

    # Convert data to DataFrame
    df_components = pd.DataFrame(all_components)

    # Rearranging columns because inserting in SQL requires given order to load up data properly
    new_order = ['organization', 'key', 'name', 'qualifier', 'project']
    df_components = df_components[new_order]

    # Chaning naming to uppercase
    df_components.columns = ['ORGANIZATION', 'KEY', 'NAME', 'QUALIFIER', 'PROJECT']
    return df_components