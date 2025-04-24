import os
import pickle  # for token storage
import json
from datetime import datetime, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar'
]

CALENDAR_ID = 'c_cd145b86092760e679df8ba1915278a36b426ac2db11dff5e16e54c4bb5013ab@group.calendar.google.com'

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

def list_all_events(service, max_results: int = 250, calendar_id: str = CALENDAR_ID):
    now = datetime.now(timezone.utc).isoformat() + 'Z'
    events_result = (
        service.events()
               .list(
                   calendarId=calendar_id,
                   timeMin=now,
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


def delete_task(service, title: str, start_time: str, max_results: int = 50, calendar_id: str = CALENDAR_ID):
    """
    Deletes an event from the specified calendar matching the given title and start time.
    `start_time` must be in ISO 8601 format (e.g., "2025-04-20T10:00").
    """
    # Fetch current events from the correct calendar
    existing_events = list_all_events(service, max_results=max_results, calendar_id=calendar_id)

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


def backup_calendar_to_json(service, out_path="task_data.json", calendar_id: str = CALENDAR_ID):
    events = list_all_events(service, calendar_id=calendar_id)
    by_date = {}

    for e in events:
        summary = e.get("summary")
        start = e.get("start", {}).get("dateTime")
        end = e.get("end", {}).get("dateTime")
        if not summary or not start:
            continue

        date = start[:10]  # "YYYY-MM-DD"
        time = start[11:16]  # "HH:MM"
        duration = None

        if start and end:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            hours = (end_dt - start_dt).total_seconds() / 3600
            duration = f"{hours:g} hours\t" if hours != 1 else "1 hour\t"

        event_obj = {
            "task": summary,
            "time": time,
            "duration": duration
        }

        if date not in by_date:
            by_date[date] = []
        by_date[date].append(event_obj)

    with open(out_path, "w") as f:
        json.dump(by_date, f, indent=2)
    print(f"📝 Backup saved to {out_path}")