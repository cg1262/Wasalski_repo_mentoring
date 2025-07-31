def get_ado_approvals(): 
    
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


    approvals = []

    for i in unique_ids:
        url_approvals = f"https://dev.azure.com/Phlexglobal/{i}/_apis/pipelines/approvals?api-version=7.1"
        response = requests.get(url_approvals, auth=auth)
        resp = response.json()['value']
        approvals.extend(resp)

    df_approvals = pd.DataFrame(approvals)


    new_order = ['id', 'steps', '_links', 'status', 'pipeline', 'createdOn', 'executionOrder', 'lastModifiedOn', 'blockedApprovers', 'minRequiredApprovers']
    df_approvals = df_approvals[new_order]

    df_approvals.columns = ['ID', 'STEPS', '_LINKS', 'STATUS', 'PIPELINE', 'CREATEDON', 'EXECUTIONORDER', 'LASTMODIFIEDON', 'BLOCKEDAPPROVERS', 'MINREQUIREDAPPROVERS']

    return df_approvals
