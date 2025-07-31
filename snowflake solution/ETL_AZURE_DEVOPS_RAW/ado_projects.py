def get_ado_projects(): 
    
    import requests
    import pandas as pd
    from requests.auth import HTTPBasicAuth 
    from snowflake.snowpark.context import get_active_session
    
    session = get_active_session()
    results = session.sql("SELECT ado_secrets()").collect()
    personal_access_token = results[0][0]
    params = {
    '$top': 5000
    }

    url_projects = f"https://dev.azure.com/Phlexglobal/_apis/projects?api-version=7.1"
    auth = HTTPBasicAuth('', personal_access_token)
    response = requests.get(url_projects, auth=auth, params = params)
    
    resp = response.json()['value']
    df_projects = pd.DataFrame(resp)
    unique_ids = df_projects['id'] .astype(str).unique().tolist()
    
    new_order = ['id', 'url', 'name', 'state', 'revision', 'visibility', 'description', 'lastUpdateTime']
    df_projects = df_projects[new_order]
    
    df_projects.columns = ['ID', 'URL', 'NAME', 'STATE', 'REVISION', 'VISIBILITY',  'DESCRIPTION', 'LASTUPDATETIME']
    return df_projects

# Kasper's solution
# import requests
# from requests.auth import HTTPBasicAuth
# import _snowflake

# def flatten_projects(data):
#     counter = data["count"]
#     # Modify this function to format the projects as needed
#     return [{"counter": counter, "id": project["id"], "name": project["name"]} for project in data.get("value", [])]

# def get_ado_projects(personal_access_token):
#     # Retrieve the PAT from Snowflake secret
#     # pat = _snowflake.get_generic_secret_string('pat')
    
#     # Azure DevOps API URL for projects
#     url = "https://dev.azure.com/phlexglobal/_apis/projects?api-version=2.0"
    
#     # Headers
#     headers = {
#         "Accept": "application/json"
#     }
    
#     # Make the GET request with Basic Auth
#     response = requests.get(url, headers=headers, auth=HTTPBasicAuth("", personal_access_token))
    
#     # Check the response
#     if response.status_code == 200:
#         # Return the flattened JSON response if successful
#         return flatten_projects(response.json())
#     else:
#         # Return an error message if the request fails
#         return {"error": response.status_code, "message": response.text}