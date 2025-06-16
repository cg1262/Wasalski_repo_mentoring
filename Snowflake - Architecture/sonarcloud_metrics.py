def get_sonarcloud_metrics():
   # ---- # ---- Metrics
    import requests
    import pandas as pd
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.sonarcloud_api_key()").collect()
    api_key = results[0][0]
    
    headers = {
    "Authorization": f"Bearer {api_key}",
    }
    params = {
        "organization": "xxxz",
        "ps": 500,  # page size
        "p": 1      # page number
    }


    all_metrics = []  # List to store all components
    total_results = 0  # Total number of results

    # Execute initial query to get the total number of results
    url_labels = "https://sonarcloud.io/api/metrics/search"
    response_labels = requests.get(url_labels, headers=headers, params=params)
    labels_data = response_labels.json()['metrics']

    df_metrics = pd.DataFrame(labels_data)

    new_order = ['id', 'key', 'name', 'type', 'domain', 'direction', 'description', 'qualitative', 'hidden', 'decimalScale']
    df_metrics = df_metrics[new_order]

    df_metrics.columns = ['ID', 'KEY', 'NAME', 'TYPE', 'DOMAIN', 'DIRECTION', 'DESCRIPTION', 'QUALITATIVE', 'HIDDEN', 'DECIMALSCALE']

    return df_metrics