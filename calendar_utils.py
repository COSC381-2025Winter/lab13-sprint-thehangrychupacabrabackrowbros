import os
import pickle  # for token storage
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def add_tasks_from_json(service, json_path="task_data.json", max_results=50):
    """
    Loads tasks from a JSON file and inserts only those not already in the calendar.
    """
    # Load tasks from the JSON file
    with open(json_path, 'r') as file:
        tasks = json.load(file)

    # Fetch current events from calendar
    existing_events = list_upcoming_events(service, max_results=max_results)

    # Normalize existing events for easier comparison
    existing_lookup = set(
        (e['summary'], e['start']['dateTime'][:16])  # e.g., ("Meeting", "2025-04-20T10:00")
        for e in existing_events if 'summary' in e and 'start' in e and 'dateTime' in e['start']
    )

    for task in tasks:
        # Format the task into an event body
        event = {
            'summary': task['title'],
            'description': task.get('description', ''),
            'start': {
                'dateTime': task['start'],  # Must be in ISO 8601 format
                'timeZone': task.get('timeZone', 'America/New_York'),
            },
            'end': {
                'dateTime': task['end'],
                'timeZone': task.get('timeZone', 'America/New_York'),
            },
        }

        task_key = (event['summary'], event['start']['dateTime'][:16])

        # Only create event if it’s not already on the calendar
        if task_key not in existing_lookup:
            create_event(service, event)
            print(f"✅ Created: {event['summary']} at {event['start']['dateTime']}")
        else:
            print(f"⚠️ Skipped duplicate: {event['summary']} at {event['start']['dateTime']}")

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
    add_tasks_from_json(service)
    print(f"✅ Google Calendar service created: {service}")
