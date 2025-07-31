def authenticate_user():
    """

    """
    import requests

    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_orgUuid_jwtToken()").collect()
    orgUuid = results[0][0]
    # orgUuid = "71003aaf-b8e7-4e7b-a622-736b775a0eff"

    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_user_key_jwtToken()").collect()
    userKey = results[0][0]
    # userKey = "8ded55a66bb04810bc4ce5d227cff997dd178fe0b56b4495b77b16417ab1032b"

    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    results = session.sql("SELECT PROD.RAW.mend_email_jwtToken()").collect()
    email = results[0][0]
    # email = "ajoyce@phlexglobal.com"

    
    base_url = "https://api-saas-eu.whitesourcesoftware.com"
    # Endpoint do logowania
    url_login = "https://api-saas-eu.whitesourcesoftware.com/api/v3.0/login"
    login_body = {
        "email": email,
        "orgUuid": orgUuid,
        "userKey": userKey
    }
    
    # Wykonanie żądania POST do logowania
    response_login = requests.post(url_login, json=login_body)
    response_login.raise_for_status()
    login_data = response_login.json()
    refresh_token = login_data['response']['refreshToken']
    
    # Uzyskanie access token'a używającego refresh token'a
    url_access_token = f"{url_login}/accessToken"
    refresh_token_headers = {
        "wss-refresh-token": refresh_token
    }
    
    # Wykonanie żądania POST do uzyskania JWT tokena
    access_token_response = requests.post(url_access_token, headers=refresh_token_headers)
    access_token_response.raise_for_status()
    access_token_data = access_token_response.json()
    jwt_token = access_token_data['response']['jwtToken']
    
    return jwt_token

# Następnie użyj headers w każdym wywołaniu API