import requests
import pandas as pd
from requests.auth import HTTPBasicAuth 
from snowflake.snowpark.context import get_active_session

session = get_active_session()
results = session.sql("SELECT ado_secrets()").collect()
personal_access_token = results[0][0]
auth = HTTPBasicAuth('', personal_access_token)


pipelines = [2441]

# to be changed into secret
sub_id = '8642d1ba-f201-45c8-955d-2347876e4145'


for i in pipelines:
    url = f"https://dev.azure.com/Phlexglobal/{sub_id}/_apis/pipelines/{i}/runs?api-version=7.1"
    response = requests.get(url, auth=auth)

    resp = response.json()

    df = pd.DataFrame(resp['value']) 

    # Filter by name containing 'PEL'
    filtered_df = df[df['name'].str.contains('PEL', case=False, na=False)].copy()
    filtered_df['issue_key'] = filtered_df['name'].astype(str).str.split('#').str[1]
    filtered_df['env'] = filtered_df['name'].astype(str).str.split('#').str[-1]
    unique_names = filtered_df['issue_key'].unique().tolist()

    runs = []

    for i in unique_names:

        name_df = filtered_df[filtered_df['issue_key'] == i].copy()
        
   
        name_df['rank'] = (name_df.groupby('state')['finishedDate']
                        .rank(method='min', ascending=True))

        succeeded_df = name_df[name_df['result'] == 'succeeded'] #spliited for issue_key/jira_key
        if not succeeded_df.empty:
            min_succeeded_rank = succeeded_df['rank'].min()
            name_df['first_is_succeeded'] = (
                (name_df['result'] == 'succeeded') & 
                (name_df['rank'] == min_succeeded_rank)
            )
        else:
            name_df['first_is_succeeded'] = False
        
        runs.append(name_df)


final_df = pd.concat(runs, ignore_index=True).drop(columns = 'templateParameters')


