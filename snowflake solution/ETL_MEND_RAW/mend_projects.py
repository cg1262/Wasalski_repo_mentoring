def get_projects(jwtToken):
        ## snowflake ready: 
    import requests
    import pandas as pd
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    headers = {
        'Authorization': f'Bearer {jwtToken}',

    }

    base_projects_url = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/orgs/{orgUuid}/projects"
    all_projects = []  # empty list to store all projects
    has_more = True # flag to control pagination
    cursor = None # cursor for pagination

    # Initial parameters - max limit is 10000 according to documentation
    params = {
        "limit": "1000",  # Requesting 1000 items per page
        "populateApplications": "true"  # Include application details in the response
    }

    print("Fetching projects data with pagination...")

    # Continue fetching while there are more pages
    while has_more:
        # Add cursor to parameters if we're not on the first page
        if cursor:
            params["cursor"] = cursor
        
        # Make the request
        response_projects = requests.get(base_projects_url, headers=headers, params=params)
        
        # Check if the request was successful
        if response_projects.status_code != 200:
            # print(f"Error fetching projects data: {response_projects.status_code}")
            # print(response_projects.text)
            break
        
        # Parse the JSON response
        response_data = response_projects.json()
        
        # Extract projects data from the response
        projects = response_data.get('response', [])
        
        # If we got no projects or empty response, break the loop
        if not projects:
            has_more = False
            continue
        
        # Append the current page's data to the list
        all_projects.extend(projects)
        # print(f"Retrieved {len(projects)} projects. Total so far: {len(all_projects)}")
        
        # Check if there's a cursor for the next page
        additional_data = response_data.get('additionalData', {})
        cursor = additional_data.get('cursor')
        
        # If no cursor is returned, we've reached the end
        if not cursor:
            has_more = False

    # print(f"Finished fetching projects. Total projects retrieved: {len(all_projects)}")

    # Convert the list of projects to a DataFrame
    projects_data = pd.DataFrame(all_projects)

    # Display the shape of the DataFrame
    # print(f"DataFrame shape: {projects_data.shape}")

    # Display the DataFrame
    unique_uuid = projects_data['uuid'].unique().tolist()

    print(projects_data.reset_index().columns)

    unique_uuid = projects_data['uuid'].unique().tolist()
    policy_violations = projects_data['applicationUuid'].tolist()
    return projects_data