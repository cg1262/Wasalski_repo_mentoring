def get_project_due_diligence(jwtToken, unique_uuid):
    import pandas as pd
    import requests
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    headers = {
        'Authorization': f'Bearer {jwtToken}',
        'Content-Type': 'application/json'
    }
    
    all_due_diligence = []  # empty list to store all due diligence data
    params = {
             'limit': "10000"
        }
    for i in unique_uuid:
        due_diligence_url = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{i}/dependencies/libraries/licenses"
        response_due_diligence = requests.get(due_diligence_url, headers=headers, params=params) 
        due_diligence = response_due_diligence.json().get('response', [])
        all_due_diligence.extend(due_diligence)

    
    return pd.DataFrame(all_due_diligence)