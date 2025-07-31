def get_ado_repos():

    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql('SELECT ado_secrets()').collect()
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



    params = {
        '$top': 5000
    }
    repos = []
    for i in unique_ids:
        response = requests.get(f"https://dev.azure.com/PhlexGlobal/{i}/_apis/git/repositories?api-version=4.1"
    , auth=auth)
        resp = response.json()['value']
        repos.extend(resp)
    df_repos = pd.DataFrame(repos)

    new_order = [
        'id', 
        'url', 
        'name', 
        'size', 
        'sshUrl', 
        'webUrl', 
        'project', 
        'remoteUrl', 
        'isDisabled', 
        'defaultBranch', 
        'isInMaintenance'
    ]

    df_repos = df_repos[new_order]


    df_repos.columns = [
        'ID', 
        'URL', 
        'NAME', 
        'SIZE', 
        'SSHURL', 
        'WEBURL', 
        'PROJECT', 
        'REMOTEURL', 
        'ISDISABLED', 
        'DEFAULTBRANCH', 
        'ISINMAINTENANCE'
    ]

    df_repos['proj_id'] = df_repos['PROJECT'].apply(lambda x: x['id'])

    df_repos_uniques = df_repos['ID'].astype(str).unique().tolist()

    return df_repos