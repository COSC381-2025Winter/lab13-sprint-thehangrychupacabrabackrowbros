import os
import pickle  # for token storage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    """Authenticate via OAuth2 and return a Google Calendar service object."""
    creds = None
    token_path = 'token.pickle'
    creds_path = 'credentials.json'

    # Load existing credentials
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token_file:
            creds = pickle.load(token_file)

    # If no valid credentials, perform the OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token_file:
            pickle.dump(creds, token_file)

    # Build the Calendar API service
    service = build('calendar', 'v3', credentials=creds)
    return service

# Quick smoke test when run as a script
if __name__ == '__main__':
    service = get_calendar_service()
    print(f"✅ Google Calendar service created: {service}")
