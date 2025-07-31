def get_alert_types(jwtToken):
    import pandas as pd
    import requests
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    
    headers = {
        'Authorization': f'Bearer {jwtToken}'
    }

    url_alert_types = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{orgUuid}/summary/alertTypes"
    response_alert_types = requests.get(url_alert_types, headers=headers)
    alert_types_data = response_alert_types.json()

    # ---- # ---- Endpoint specific logic ---- # ----

    # Create Pandas DataFrame
    if alert_types_data:  # Check if data was actually fetched

        df = pd.DataFrame(alert_types_data).reset_index().rename(columns={'index': 'PATH'})
        df = df[['PATH', 'retVal']]
        
        # # --- Option 1: add a dummy index and pivot ---
        df['row'] = 0
        wide1 = df.pivot(index='row', columns='PATH', values='retVal').reset_index().drop('row', axis = 1 )
        
    else:
        print("\nNo alert types data fetched, temporary table not created.")

    return wide1