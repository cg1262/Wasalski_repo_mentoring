
def get_license_policy_violations(jwtToken, policy_violations):
    import requests
    import pandas as pd
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    policy_violations_list = []
    headers = {
        "Authorization": f"Bearer {jwtToken}"
        }
    # for product_uuid in unique_product_uuids:
    for product_uuid in policy_violations:  # lub unique_product_uuids
        page = 0
        is_last_page = False
    
        while not is_last_page:
            params = {
                'pageSize': '10000',
                'page': str(page)
            }
            url_licence_policy_violations = (
                f"https://api-saas-eu.whitesourcesoftware.com/api/v2.0/products/{product_uuid}/alerts/legal"
            )
            response = requests.get(url_licence_policy_violations, headers=headers, params=params)
            data = response.json()
    
            # Dodaj wyniki z tej strony do listy
            if 'retVal' in data and isinstance(data['retVal'], list):
                policy_violations_list.extend(data['retVal'])
    
            # Sprawdź czy to ostatnia strona
            is_last_page = data.get('body', {}).get('additionalData', {}).get('isLastPage', True)
            # Jeśli nie ma body, spróbuj bezpośrednio z głównego poziomu (dostosuj w zależności od API)
            if not isinstance(is_last_page, bool):
                is_last_page = data.get('additionalData', {}).get('isLastPage', True)
    
            page += 1
    
    # Tworzenie DataFrame z zebranych danych
    policy_violations_df = pd.DataFrame(policy_violations_list)
    
    # Jeżeli alertInfo jest słownikiem, wyciągnij potrzebne pola
    policy_violations_df['status'] = policy_violations_df['alertInfo'].apply(lambda x: x.get('status') if isinstance(x, dict) else None)
    policy_violations_df['detected_at'] = policy_violations_df['alertInfo'].apply(lambda x: x.get('detectedAt') if isinstance(x, dict) else None)
    policy_violations_df['modified_at'] = policy_violations_df['alertInfo'].apply(lambda x: x.get('modifiedAt') if isinstance(x, dict) else None)
    
    policy_violations_df = policy_violations_df[[
        'name', 'type', 'uuid', 'project', 'component',
        'policyName', 'status', 'detected_at', 'modified_at'
    ]]
    
    # Display the DataFrame (optional, for confirmation in notebooks)
    policy_violations_df = policy_violations_df.drop_duplicates(subset=['uuid'])
    policy_violations_df = policy_violations_df.reset_index(drop=True)
    return policy_violations_df