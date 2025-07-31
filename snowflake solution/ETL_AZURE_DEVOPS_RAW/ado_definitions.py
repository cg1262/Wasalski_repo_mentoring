def get_ado_definitions():

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

    # projects
    url_projects = f"https://dev.azure.com/Phlexglobal/_apis/projects?api-version=7.1"
    auth = HTTPBasicAuth('', personal_access_token)
    response = requests.get(url_projects, auth=auth, params = params)
    
    resp = response.json()['value']
    df_projects = pd.DataFrame(resp)
    unique_ids = df_projects['id'] .astype(str).unique().tolist()


    definitions = []

    for i in unique_ids:

        url_definitions = f"https://dev.azure.com/Phlexglobal/{i}/_apis/build/definitions?api-version=7.1"
        response = requests.get(url_definitions, auth=auth)
        resp = response.json()['value']
        definitions.extend(resp)
    df_definitions = pd.DataFrame(definitions)


    new_order = [
        'id', 
        'uri', 
        'url', 
        'name', 
        'path', 
        'type', 
        'queue', 
        '_links', 
        'drafts', 
        'project', 
        'quality', 
        'revision', 
        'authoredBy', 
        'createdDate', 
        'queueStatus'
    ]

    df_definitions = df_definitions[new_order]

    df_definitions.columns = [
        'ID', 
        'URI', 
        'URL', 
        'NAME', 
        'PATH', 
        'TYPE', 
        'QUEUE', 
        '_LINKS', 
        'DRAFTS', 
        'PROJECT', 
        'QUALITY', 
        'REVISION', 
        'AUTHOREDBY', 
        'CREATEDDATE', 
        'QUEUESTATUS'
    ]

    df_definitions['PROJECTID'] = df_definitions['PROJECT'].apply(lambda x: x['id'])
    df_definitions['PROJECTNAME'] = df_definitions['PROJECT'].apply(lambda x: x['name'])

    return df_definitions

