import os
import pickle  # for token storage
import json
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
        # Skip malformed or incomplete tasks
        if not task.get('start') or not task.get('end') or not task.get('title'):
            continue

        event = {
            'summary': task['title'],
            'description': task.get('description', ''),
            'start': {
                'dateTime': task['start'],
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
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    events_result = (
        service.events()
               .list(
                   calendarId='432a356b9fd99deec8bfe1cf5f9980e1de8a4387106bcbdc6d5ed34244315d1d@group.calendar.google.com',
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
        calendarId='432a356b9fd99deec8bfe1cf5f9980e1de8a4387106bcbdc6d5ed34244315d1d@group.calendar.google.com',
        body=event_body
    ).execute()

def delete_task(service, title: str, start_time: str, max_results: int = 50):
    """
    Deletes an event from the calendar matching the given title and start time.
    `start_time` must be in ISO 8601 format (e.g., "2025-04-20T10:00").
    """
    # Fetch current events
    existing_events = list_upcoming_events(service, max_results=max_results)

    for event in existing_events:
        event_title = event.get('summary', '')
        event_start = event.get('start', {}).get('dateTime', '')

        # Match title and first 16 chars of ISO time (to match to the minute)
        if event_title == title and event_start[:16] == start_time[:16]:
            event_id = event['id']
            service.events().delete(calendarId='432a356b9fd99deec8bfe1cf5f9980e1de8a4387106bcbdc6d5ed34244315d1d@group.calendar.google.com', eventId=event_id).execute()
            print(f"🗑️ Deleted: {title} at {start_time}")
            return

    print(f"❌ No matching event found for deletion: {title} at {start_time}")



    
if __name__ == '__main__':
    service = get_calendar_service()

    # Create a test event
    test_event = {
        'summary': 'Test Event to Delete',
        'start': {
            'dateTime': '2025-04-21T14:00:00',
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': '2025-04-21T15:00:00',
            'timeZone': 'America/New_York',
        },
    }

    # Create the event
    create_event(service, test_event)
    print("✅ Test event created.")

    # Now delete the event
    delete_task(service, 'Test Event to Delete', '2025-04-20T14:00')
