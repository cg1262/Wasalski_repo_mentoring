def get_ado_source_providers():

    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT ado_secrets()").collect()
    personal_access_token = results[0][0]

    import requests
    import pandas as pd
    from requests.auth import HTTPBasicAuth 

    params = {
    '$top': 5000
    }

    url_projects = f"https://dev.azure.com/Phlexglobal/_apis/projects?api-version=7.1"
    auth = HTTPBasicAuth('', personal_access_token)
    response = requests.get(url_projects, auth=auth, params = params)
    
    resp = response.json()['value']
    df_projects = pd.DataFrame(resp)
    unique_ids = df_projects['id'] .astype(str).unique().tolist()



    src_providers = []
    for i in unique_ids:
        url_src_providers = f"https://dev.azure.com/Phlexglobal/{i}/_apis/sourceproviders?api-version=7.1"
        response = requests.get(url_src_providers, auth=auth)
        resp = response.json()['value']
        src_providers.extend(resp)
    df_source_providers = pd.DataFrame(src_providers)



    new_order = [
        'name', 
        'supportedTriggers', 
        'supportedCapabilities'
    ]

    df_source_providers = df_source_providers[new_order]

    df_source_providers.columns = [
        'NAME', 
        'SUPPORTEDTRIGGERS', 
        'SUPPORTEDCAPABILITIES'
    ]   
    return df_source_providers