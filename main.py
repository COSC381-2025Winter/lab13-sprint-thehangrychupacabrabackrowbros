from calendar_utils import get_calendar_service

def main():
    # 1) Get the authorized Calendar service
    service = get_calendar_service()

    # 2) Call the Calendar API: list the next 5 upcoming events
    import datetime
    now_iso = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now_iso,
        maxResults=5,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    # 3) Print out what we got
    if not events:
        print("No upcoming events found.")
    else:
        print("Your next 5 events:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {start} | {event.get('summary', '(no title)')}")

if __name__ == '__main__':
    main()
