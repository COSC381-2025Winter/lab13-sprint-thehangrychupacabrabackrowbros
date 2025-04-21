import os
import pickle
import json
import datetime
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar'
]

# ✅ Your shared calendar ID
CALENDAR_ID = 'c_cd145b86092760e679df8ba1915278a36b426ac2db11dff5e16e54c4bb5013ab@group.calendar.google.com'

def add_tasks_from_json(service, json_path="task_data.json", max_results=250):
    with open(json_path, 'r') as file:
        tasks = json.load(file)

    existing_events = list_all_events(service, max_results=max_results)

    existing_lookup = set(
        (e['summary'], e['start']['dateTime'][:16])
        for e in existing_events if 'summary' in e and 'start' in e and 'dateTime' in e['start']
    )

    for task in tasks:
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

        if task_key not in existing_lookup:
            create_event(service, event)
            print(f"✅ Created: {event['summary']} at {event['start']['dateTime']}")
        else:
            print(f"⚠️ Skipped duplicate: {event['summary']} at {event['start']['dateTime']}")

def get_calendar_service():
    creds = None
    token_path = 'token.pickle'
    creds_path = 'credentials.json'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token_file:
            creds = pickle.load(token_file)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token_file:
            pickle.dump(creds, token_file)

    service = build('calendar', 'v3', credentials=creds)
    return service

def list_all_events(service, max_results: int = 250, calendar_id: str = CALENDAR_ID):
    """
    Returns all events (up to max_results) from the calendar, ignoring timeMin filter.
    """
    events_result = (
        service.events()
               .list(
                   calendarId=calendar_id,
                   maxResults=max_results,
                   singleEvents=True,
                   orderBy='startTime'
               )
               .execute()
    )
    return events_result.get('items', [])

def create_event(service, event_body: dict, calendar_id: str = CALENDAR_ID):
    return service.events().insert(
        calendarId=calendar_id,
        body=event_body
    ).execute()

def delete_task(service, title: str, start_time: str, max_results: int = 250, calendar_id: str = CALENDAR_ID):
    existing_events = list_all_events(service, max_results=max_results, calendar_id=calendar_id)

    print("\n--- Existing Events ---")
    for e in existing_events:
        print(f"{e.get('summary', '')} @ {e.get('start', {}).get('dateTime', '')}")
    print("-----------------------\n")

    for event in existing_events:
        event_title = event.get('summary', '')
        event_start = event.get('start', {}).get('dateTime', '')

        # Compare both title and starting time (to the minute)
        if event_title == title and event_start[:16] == start_time[:16]:
            event_id = event['id']
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            print(f"🗑️ Deleted: {title} at {start_time}")
            return

    print(f"❌ No matching event found for deletion: {title} at {start_time}")

if __name__ == '__main__':
    service = get_calendar_service()

    # Test Event
    test_event = {
        'summary': 'Test Event to Delete',
        'start': {
            'dateTime': '2025-04-20T14:00:00',
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': '2025-04-20T15:00:00',
            'timeZone': 'America/New_York',
        },
    }

    create_event(service, test_event)
    print("✅ Test event created.")
    time.sleep(2)  # Allow Google to register the event

    delete_task(service, 'Test Event to Delete', '2025-04-20T14:00')
