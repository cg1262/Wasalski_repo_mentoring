def get_ado_pipelines():

    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT ado_secrets()").collect()
    personal_access_token = results[0][0]
    
    import requests
    import pandas as pd
    from requests.auth import HTTPBasicAuth 

    params = {
        "$top": 5000,
        "api-version": "7.1"
    }

    headers = {
        "Accept": "application/json",  
    }

    url_projects = f"https://dev.azure.com/Phlexglobal/_apis/projects?api-version=7.1"
    auth = HTTPBasicAuth('', personal_access_token)
    response = requests.get(url_projects, auth=auth, params = params)
    
    resp = response.json()['value']
    df_projects = pd.DataFrame(resp)
    unique_ids = df_projects['id'] .astype(str).unique().tolist()
    
    
    pipelines = []
    for i in unique_ids:
        url_pipelines = f"https://dev.azure.com/Phlexglobal/{i}/_apis/pipelines?api-version=7.1"
        response = requests.get(url_pipelines, auth=auth)
        resp = response.json()['value']
        pipelines.extend(resp)
        
    df_pipelines = pd.DataFrame(pipelines)

    new_order = [
        'id', 
        'url', 
        'name', 
        '_links', 
        'folder', 
        'revision'
    ]

    df_pipelines = df_pipelines[new_order]

    df_pipelines.columns = [
        'ID', 
        'URL', 
        'NAME', 
        '_LINKS', 
        'FOLDER', 
        'REVISION'
    ]
    return df_pipelines