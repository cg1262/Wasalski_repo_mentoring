def get_sonarcloud_issues():
    import requests
    import pandas as pd
    import datetime 
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.sonarcloud_api_key()").collect()
    api_key = results[0][0]
    
    current_year = datetime.datetime.now().year
    headers = {
    "Authorization": f"Bearer {api_key}",
}
    all_issues = []  # list to store all issues
    year_tofind = 2017  # Starting from 2017 to fetch everything
    months = range(1,13)

    # Main outer loop - iterate through years starting from 2017 up to current year
    while year_tofind <= current_year:
        # Inner loop - iterate through all months (1-12) for each year
        for month in months:
            # Create API query parameters for the specific month and year
            params = {
                "organization": 'phlexglobal',  # Organization identifier in SonarCloud
                "ps": 500,  # Page size - number of results per page (maximum 500)
                "p": 1,     # Initial page number
                "createdBefore": f"{year_tofind}-{month+1:02d}-01",  # End date: first day of next month
                "createdAfter": f"{year_tofind}-{month:02d}-01",     # Start date: first day of current month
            }

            # Define the SonarCloud API endpoint for issue search
            url_issues = "https://sonarcloud.io/api/issues/search"
            # Execute API request with defined parameters
            response_issues = requests.get(url_issues, headers=headers, params=params)
            # Parse JSON response
            issues_data = response_issues.json()

            # Extract total number of results from the response
            # Instead of getting errors we will get {} and 0 for total if there is no data
            total_results = issues_data.get('paging', {}).get('total', 0)

            # Skip to next month if no results found for current month
            if total_results == 0:
                continue

            # Calculate total number of pages based on total results and page size
            # If there's a remainder, add one more page
            total_pages = (total_results // params['ps']) + (1 if total_results % params['ps'] > 0 else 0)

            # Add reponse to the list
            all_issues.extend(issues_data.get('issues', []))

            # Pagination loop - fetch all remaining pages of results
            while params["p"] < total_pages:
                params["p"] += 1  # Increment page number
                # Execute API request for the next page
                response_issues = requests.get(url_issues, headers=headers, params=params)
                # Parse JSON response
                issues_data = response_issues.json()
                
                # Add issues from the current page to our collection
                all_issues.extend(issues_data.get('issues', []))

        # After processing all months for current year, move to next year
        year_tofind += 1

    # Convert data to DataFrame
    df_issues = pd.DataFrame(all_issues)

    # Rearranging columns because inserting in SQL requires given order to load up data properly
    new_order = ['key', 'rule', 'severity', 'component', 'project', 'line', 'hash', 'textRange', 'flows', 
                'status', 'message', 'effort', 'debt', 'assignee', 'author', 'tags', 
                'creationDate', 'updateDate', 'type', 'organization', 'cleanCodeAttribute', 
                'cleanCodeAttributeCategory', 'impacts', 'issueStatus', 'externalRuleEngine', 
                'resolution', 'closeDate']
    df_issues = df_issues[new_order]

    # Chaning naming to uppercase
    df_issues.columns = ['KEY', 'RULE', 'SEVERITY', 'COMPONENT', 'PROJECT', 'LINE', 'HASH', 'TEXTRANGE', 
                        'FLOWS', 'STATUS', 'MESSAGE', 'EFFORT', 'DEBT', 'ASSIGNEE', 
                        'AUTHOR', 'TAGS', 'CREATIONDATE', 'UPDATEDATE', 'TYPE', 'ORGANIZATION', 
                        'CLEANCODEATTRIBUTE', 'CLEANCODEATTRIBUTECATEGORY', 'IMPACTS', 
                        'ISSUESTATUS', 'EXTERNALRULEENGINE', 'RESOLUTION', 'CLOSEDATE']
    return df_issues