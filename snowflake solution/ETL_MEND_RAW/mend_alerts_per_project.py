def get_alerts_per_project(jwtToken,unique_uuid):
    import pandas as pd
    import requests
    orgUuid = "71003aaf-b8e7-4e7b-a622-736b775a0eff"
    all_security_findings = []  # Initialize list to store all findings from all projects
    headers = {
        'Authorization': f'Bearer {jwtToken}',

    }
    for project_uuid in unique_uuid:
        url_security_alerts_project = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{project_uuid}/dependencies/findings/security"
        params = {"limit": "10000"}
        response_security_alerts_project = requests.get(url_security_alerts_project, headers=headers, params = params)
        security_alerts_project_data = response_security_alerts_project.json()['response']
        all_security_findings.extend(security_alerts_project_data)
    
    
    df_final_alerts = pd.DataFrame(all_security_findings)
    # Now df_final_alerts contains all findings from all projects
    # You can display it or process it further
    df_final_alerts['status'] = df_final_alerts['findingInfo'].apply(lambda x: x.get('status') if x else None)
    df_final_alerts['detected_at'] = df_final_alerts['findingInfo'].apply(lambda x: x.get('detectedAt') if x else None)
    df_final_alerts['modified_at'] = df_final_alerts['findingInfo'].apply(lambda x: x.get('modifiedAt') if x else None)
    df_final_alerts.drop(columns=['findingInfo'])
    
    list_of_alerts_cleaned = df_final_alerts[['name', 'type', 'uuid', 'topFix', 'project','component',
    'application', 'exploitable', 'vulnerability' ,'threatAssessment', 'scoreMetadataVector','status', 'detected_at','modified_at']]
    
   
    # Display the DataFrame (optional, for confirmation in notebooks)
    # list_of_alerts_cleaned.columns
    return list_of_alerts_cleaned