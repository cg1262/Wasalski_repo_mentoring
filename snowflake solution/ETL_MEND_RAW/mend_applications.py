def get_applications(jwtToken):
    
    import requests
    import pandas as pd
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    
    ## snowflake ready python script:

    # API CALL to get data for applications. 
    # jwtToken and orgUuid are being generated in the login_and_access_token cell

    # In params limit is set to 1000 - max from documentation

    # cursor: Parameter indicates the starting point for retrieving results

    # ---- # ----- # Applications # --- # ---- #
    headers_applications = {
            "Authorization": f"Bearer {jwtToken}"
            }
        
    url_applications = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/orgs/{orgUuid}/applications"
    all_aplications = []
    applications_cursor = None
        
        # Initial parameters - max limit is 10000 according to documentation
    applications_params = {
            "limit": 1000,  # Requesting 1000 items per page
            "cursor" : None,  # If Cursor is not empty it indicates there is more data to fetch
            # and we need to iterate through all pages
        }
        
    while True:
            # Add the cursor to the parameters if it exists
            if applications_cursor:
                applications_params["cursor"] = applications_cursor
        
            # making request
            response_applications = requests.get(url_applications, headers=headers_applications, params=applications_params)
            applications_data = response_applications.json()
        
            # extracting data and extending all_aplications list
            applications = applications_data.get('response', [])
            all_aplications.extend(applications)
        
            # Check if there is a next page
            
            # if there is another page output would look like this:
            # {'additionalData': {'totalItems': 96,
            #'paging': {'next': 'https://api-saas-eu.whitesourcesoftware.com/api/v3.0/orgs/71003aaf-b8e7-4e7b-a622-736b775a0eff/applications?limit=50&cursor=1'}},
            
            # if there is no additional page:
            # {'additionalData': {'totalItems': 96, 'paging': {}},
            cursor = applications_data['additionalData'].get('paging', {}).get('next')
            if not cursor:
                break


    # ---- # ---- Endpoint specific logic ---- # ----

    if all_aplications: # Check if data was actually fetched
        all_applications_df = pd.DataFrame(all_aplications)


    else:
        print("\nNo application data fetched, temporary table not created.")
    unique_product_uuids = all_applications_df['uuid'].unique().tolist()
    return all_applications_df