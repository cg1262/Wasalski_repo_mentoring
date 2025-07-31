def get_vulnerabilities_project(jwtToken):
    import pandas as pd
    import requests
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    vulnerabilities_project = []
    page = 0
    page_size = 10000
    is_last_page = False
    headers = {
        'Authorization': f'Bearer {jwtToken}',

    }
    while not is_last_page:
        url = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{orgUuid}/summary/projects/vulnerableLibraryCount?search=projectName:like:"
                
        params = {
            "page": str(page),
            "pageSize": str(page_size)
        }
                
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
                
        print(f"Page {page} Vulnerabilities Project: ", data)
        vulnerabilities_project.append(data)
        page += 1
        is_last_page = data['additionalData']['isLastPage']
    
    vulnerabilities_project_df = pd.DataFrame(vulnerabilities_project)['retVal'].iloc[0]
    vulnerabilities_project_df = pd.DataFrame(vulnerabilities_project_df)
    return vulnerabilities_project_df