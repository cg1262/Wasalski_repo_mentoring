def get_labels(jwtToken):
    import pandas as pd
    import requests
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    headers = {
        "Authorization": f"Bearer {jwtToken}"
        }

    # ——— ## ———— ## ————
    # Stream: Labels
    # This stream gets labels associated with the organization.
    url_labels = f"https://api-saas-eu.whitesourcesoftware.com/api/v3.0/orgs/{orgUuid}/labels"
    response_labels = requests.get(url_labels, headers=headers)
    labels_data = response_labels.json()

    labels_data = pd.DataFrame(labels_data['response'])

    # Assume df_labels holds the final DataFrame for this notebook
    # <<<< ADJUST THE DATAFRAME VARIABLE NAME BELOW IF IT'S DIFFERENT >>>>

    # Display the DataFrame (optional, for confirmation in notebooks)
    return labels_data
