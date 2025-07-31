def get_alerts_severity(jwtToken):
    import pandas as pd
    import requests
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    
    headers_severity = {
        "Authorization": f"Bearer {jwtToken}"
        }

    url_applications = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/orgs/{orgUuid}/applications"
    all_aplications = []
    applications_cursor = None

    # ——— ## ———— ## ————
    # Stream: Alerts - Severity
    # Retrieves alert count per severity.
    url_alerts_severity = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/orgs/{orgUuid}/summary/alertCountPerSeverity"
    response_alerts_severity = requests.get(url_alerts_severity, headers=headers_severity)
    alerts_severity_data = response_alerts_severity.json()
    print("Alerts Severity: ", alerts_severity_data)
    df_alerts_severity_data = pd.DataFrame([alerts_severity_data['retVal']])



    return df_alerts_severity_data