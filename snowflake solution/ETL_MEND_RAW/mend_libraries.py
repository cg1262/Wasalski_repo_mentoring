def get_libraries(jwtToken):
    import pandas as pd
    import requests
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    #project to get unique_uuids
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

    # print("Fetching projects data with pagination...")

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

    # print(projects_data.reset_index().columns)

    ##### end of projects


    params = {
    "limit": "10000",  # Requesting 1000 items per page
    }

    all_libraries = []  # Empty list to store all libraries
    # count_libraries = 0

    # Iterate over each project UUID
    for project_uuid in unique_uuid:

        # print(f"Fetching library no {count_libraries}")
        # count_libraries += 1
        # print(f"Fetching libraries for project {project_uuid}...")
        has_more = True  # Reset pagination flag for each project
        cursor = None  # Reset cursor for each project
        
        while has_more:
            # Add cursor to parameters if we're not on the first page
            if cursor:
                params["cursor"] = cursor
            
            # Construct the URL for fetching libraries
            url_libraries = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/projects/{project_uuid}/dependencies/libraries"
            response_libraries = requests.get(url_libraries, headers=headers, params=params)
            
            # Check if the request was successful
            if response_libraries.status_code != 200:
                # print(f"Error fetching libraries for project {project_uuid}: {response_libraries.status_code}")
                print(response_libraries.text)
                break
            
            # Parse the JSON response
            libraries_data = response_libraries.json()
            
            # Extract libraries from the response
            libraries = libraries_data.get('response', [])
            
            # Add project_uuid to each library
            for library in libraries:
                library['project_uuid'] = project_uuid
            
            # Append the current page's data to the list
            all_libraries.extend(libraries)
            # print(f"Retrieved {len(libraries)} libraries for project {project_uuid}. Total so far: {len(all_libraries)}")
            
            # Check if there's a cursor for the next page
            additional_data = libraries_data.get('additionalData', {})
            cursor = additional_data.get('cursor')
            
            # If no cursor is returned, we've reached the end
            has_more = bool(cursor)
            
    all_libraries_df = pd.DataFrame(all_libraries)
                # wide1 = wide1.drop('row', axis = 1)

        
    return all_libraries_df