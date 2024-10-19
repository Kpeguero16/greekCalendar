import os
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_credentials():
    creds = None
    if os.environ.get('GOOGLE_OAUTH_TOKEN'):
        creds = Credentials.from_authorized_user_info(json.loads(os.environ['GOOGLE_OAUTH_TOKEN']), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_config(
                json.loads(os.environ['GOOGLE_OAUTH_CLIENT_CONFIG']),
                SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')

            auth_url, _ = flow.authorization_url(prompt='consent')

            print(f'Please go to this URL and authorize the application: {auth_url}')
            code = input('Enter the authorization code: ')

            flow.fetch_token(code=code)
            creds = flow.credentials

        os.environ['GOOGLE_OAUTH_TOKEN'] = creds.to_json()

    return creds


if __name__ == '__main__':
    get_credentials()