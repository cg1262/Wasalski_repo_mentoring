

def get_jira_issues_projects(project_ids):

    
    import requests
    import pandas as pd
    import json
    from datetime import datetime
    import time
    from snowflake.snowpark.context import get_active_session
    time.sleep(1)
    from requests.auth import HTTPBasicAuth

    results = get_active_session().sql("SELECT PROD.RAW.jira_username()").collect()
    jira_username = results[0][0]

    results = get_active_session().sql("SELECT PROD.RAW.jira_api_token()").collect()
    jira_api_token = results[0][0]

    if not jira_username or not jira_api_token:
        return {"status": "error", "message": "Missing credentials"}
    
    all_issues = []
    errors = []

    for pid in project_ids:
        start_at = 0
        max_results = 1000

        while True:
            params = {
                "jql": f"project = {pid} AND updated >= -1d",
                "maxResults": max_results,
                "startAt": start_at,
                "expand": "schema,changelog,transitions,editmeta,properties,renderedFields,versionedRepresentations"
            }
            url = "https://phlexglobal.atlassian.net/rest/api/3/search"
            headers = {"Accept": "application/json"}

            response = requests.get(url, auth=(jira_username, jira_api_token), headers=headers, params=params)

            if response.status_code != 200:
                error_detail = {
                    "project": pid,
                    "status_code": response.status_code,
                    "response": response.text
                }
                print(f"[ERROR] Failed to fetch project {pid}: {response.status_code}")
                errors.append(error_detail)
                break  # Przerywamy tylko ten projekt, przechodzimy do kolejnego

            data = response.json()
            issues_list = data.get('issues', [])
            all_issues.extend(issues_list)

            total = data.get('total', 0)
            start_at += max_results

            if start_at >= total:
                print(f"[INFO] Project {pid} done, total: {total}")
                break

    if not all_issues:
        print("[INFO] No issues retrieved.")
        return pd.DataFrame()  # Zwróć pusty DataFrame jeśli brak danych

    issues_df = pd.DataFrame(all_issues)

    # --- Funkcja pomocnicza: wyciąganie daty aktualizacji ---
    def extract_updated(versioned):
        if isinstance(versioned, str):
            try:
                versioned = json.loads(versioned)
            except:
                return None
        if isinstance(versioned, dict):
            updated_field = versioned.get('updated')
            if isinstance(updated_field, dict):
                first_value = next(iter(updated_field.values()), None)
                if isinstance(first_value, str):
                    return first_value.split('T')[0]
            elif isinstance(updated_field, str):
                return updated_field.split('T')[0]
        return None

    issues_df['updated'] = issues_df.get('versionedRepresentations', None).apply(extract_updated)
    issues_df['updated'] = pd.to_datetime(issues_df['updated'], errors='coerce').dt.date

    # --- Zamiana złożonych struktur na JSON ---
    for col in ['versionedRepresentations', 'renderedFields', 'transitions', 'editmeta', 'changelog']:
        if col in issues_df.columns:
            issues_df[col] = issues_df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )

    issues_df.reset_index(drop=True, inplace=True)
    issues_df = issues_df.drop(columns='updated')
    if errors:
        print("\n[WARNING] Some projects could not be fetched:")
        for err in errors:
            print(f"- Project: {err['project']}, Status: {err['status_code']}, Message: {err['response']}")

    return issues_df
