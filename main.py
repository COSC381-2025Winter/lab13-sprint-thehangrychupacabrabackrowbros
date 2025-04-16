from calendar_utils import get_calendar_service, list_upcoming_events

def main():
    # 1. Get the Google Calendar service
    service = get_calendar_service()

    # 2. Fetch upcoming calendar events (default max_results=10)
    events = list_upcoming_events(service)

    # 3. Print out upcoming events nicely formatted
    if not events:
        print("No upcoming events found.")
    else:
        print("Upcoming events:")
        for event in events:
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            event_title = event.get('summary', '(No title)')
            print(f"🔸 {start_time} | {event_title}")

if __name__ == "__main__":
    main()
