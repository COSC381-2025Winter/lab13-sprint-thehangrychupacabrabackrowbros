import os
import pickle  # for token storage
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def add_task(service, title: str, description: str, start_datetime: datetime.datetime, duration_minutes: int = 60):
    """
    Adds a new task (event) to Google Calendar.
    """
    end_datetime = start_datetime + datetime.timedelta(minutes=duration_minutes)

    event_body = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/New_York',  # change as needed
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/New_York',
        },
    }

    event = create_event(service, event_body)
    print(f"📅 Task '{title}' created successfully: {event.get('htmlLink')}")

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

def list_upcoming_events(service, max_results: int = 10):
    """
    Returns the next `max_results` events on the user's primary calendar.
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC
    events_result = (
        service.events()
               .list(
                   calendarId='primary',
                   timeMin=now,
                   maxResults=max_results,
                   singleEvents=True,
                   orderBy='startTime'
               )
               .execute()
    )
    return events_result.get('items', [])

def create_event(service, event_body: dict):
    """
    Creates an event on the user's primary calendar.
    `event_body` must follow the Google Calendar API spec.
    """
    return service.events().insert(
        calendarId='primary',
        body=event_body
    ).execute()

# Quick smoke test when run as a script
if __name__ == '__main__':
    service = get_calendar_service()
    print(f"✅ Google Calendar service created: {service}")
