import os
import pickle  # for token storage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define the Google Calendar API scope; modify if you need additional scopes.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Authenticates the user via OAuth2 and returns a Google Calendar API service object.
    It first checks for stored credentials in 'token.pickle'. If these credentials are missing or invalid,
    the function runs the OAuth2 flow using 'credentials.json', saves the new token to 'token.pickle',
    and then returns the service object.
    """
    creds = None
    token_file = 'token.pickle'  # File to store the user's access and refresh tokens.
    
    # Check if token file exists and load credentials.
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials available, or if they have expired, initiate the OAuth flow.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Initiate the OAuth2 flow using the credentials.json file.
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    # Build and return the Google Calendar API service object.
    service = build('calendar', 'v3', credentials=creds)
    return service

if __name__ == "__main__":
    service = get_calendar_service()
    print("Google Calendar service created successfully!")
