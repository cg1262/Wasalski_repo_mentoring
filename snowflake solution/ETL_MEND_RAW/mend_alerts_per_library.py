def get_alerts_per_library(jwtToken,  unique_uuid):
    import pandas as pd
    import requests
    headers = {
        'Authorization': f'Bearer {jwtToken}',
        'Content-Type': 'application/json'
    }
    
    
    all_security_alerts_data = []
    page_size = 1000 # Using a smaller page size for example, adjust as needed (max 10000)
    
    for project_token in unique_uuid:
        page = 0
        while True:
            url_security_alerts_library = f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/projects/{project_token}/alerts/security/groupBy/component"
            params = {"pageSize": str(page_size), "page": str(page)}
            response = requests.get(url_security_alerts_library, headers=headers, params=params)
                # Raise an exception for bad status codes (4xx client error or 5xx server error)
            response.raise_for_status()
            data_page = response.json()
    
                # Extract the list of alerts, default to empty list if 'retVal' is missing or null
            alerts = data_page.get('retVal', [])
    
                # Add project token to each alert record for context
            for alert in alerts:
                alert['projectToken'] = project_token
            all_security_alerts_data.extend(alerts)
    
                # If the number of returned alerts is less than the page size, it's the last page
            if len(alerts) < page_size:
                break
    
                # Increment page number for the next request
            page += 1
    
    
    df_security_alerts = pd.DataFrame(all_security_alerts_data)
    return df_security_alerts