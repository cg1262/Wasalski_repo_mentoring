def get_sonarcloud_measures_component():

    metrics_keys = [
    'accepted_issues', 'files', 'ncloc', 'maintainability_issues', 'reliability_issues', 
      'security_hotspots', 'security_issues', 'line_coverage', 
      'duplicated_lines', 'duplicated_lines_density'
    ]

    import requests
    import pandas as pd
    import datetime 
    import time
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.sonarcloud_api_key()").collect()
    api_key = results[0][0]
    
    headers = {
    "Authorization": f"Bearer {api_key}",
    }
    params = {
        "organization": "phlexglobal",
        "ps": 500,  # page size
        "p": 1      # page number
    }

    all_components = []  # list to store all components

    total_results = 0 

    # Execute initial query to get the total number of results
    url_components = "https://sonarcloud.io/api/components/search"
    response_components = requests.get(url_components, headers=headers, params=params)
    components_data = response_components.json()

    # Get total number of results
    total_results = components_data['paging']['total']
    total_pages = (total_results // params['ps']) + (1 if total_results % params['ps'] > 0 else 0)

    # Add components to the general list
    all_components.extend(components_data['components'])

    # Loop to collect data from each page, if there is more than one page
    while params["p"] < total_pages:
        params["p"] += 1  # Go to the next page
        response_components = requests.get(url_components, headers=headers, params=params)
        components_data = response_components.json()
        
        # Add components from the current page
        all_components.extend(components_data['components'])

    # Convert data to DataFrame
    df_components = pd.DataFrame(all_components)

    # Rearranging columns because inserting in SQL requires given order to load up data properly
    new_order = ['organization', 'key', 'name', 'qualifier', 'project']
    df_components = df_components[new_order]

    # Chaning naming to uppercase
    df_components.columns = ['ORGANIZATION', 'KEY', 'NAME', 'QUALIFIER', 'PROJECT']


    # We need list of unique component for Measure Components endpoint
    component = df_components['KEY'].unique().tolist()
    # List to store all measures for components
    all_measures_component = []

    # Loop through each component
    for comp_id in component:
            # Loop through each metric key
            for j in metrics_keys:
                url_labels = f"https://sonarcloud.io/api/measures/component"
                # Make API request to get component measures
                response_labels = requests.get(url_labels, headers=headers, 
                params = {
                    "organization": "phlexglobal",
                    "metricKeys" : j,
                    # "metricKeys" : 'accepted_issues',
                    'component' : comp_id
                }
                )
                # Parse response to JSON
                labels_data = response_labels.json()
                
                # Create data structure for the component and its measures
                data = {
                'id': labels_data['component']['id'],
                'key': labels_data['component']['key'],
                'name': labels_data['component']['name'],
                'qualifier': labels_data['component']['qualifier'],
                'measures': labels_data['component']['measures']
                }


                # Add components to the general list
                all_measures_component.append(data)
                # Add delay to avoid API rate limiting
                time.sleep(0.1)
                # print(all_measures_component)
            # print(comp_id)

    # Convert data to DataFrame
    df_measures_component = pd.DataFrame(all_measures_component)


    new_order = ['id', 'key', 'name', 'qualifier', 'measures']
    df_measures_component = df_measures_component[new_order]
    df_measures_component.columns = ['ID', 'KEY', 'NAME', 'QUALIFIER', 'MEASURES']
    return df_measures_component