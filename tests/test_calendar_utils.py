import datetime
import calendar_utils
from calendar_utils import list_upcoming_events, create_event

class DummyService:
    def events(self):
        return self

    def list(self, calendarId, timeMin, maxResults, singleEvents, orderBy):
        return self

    def insert(self, calendarId, body):
        class Req:
            def execute(self_inner):
                return {'id': 'abc123', **body}
        return Req()

    def execute(self):
        return {
            'items': [
                {
                    'start': {'dateTime': '2025-01-01T10:00:00Z'},
                    'summary': 'Test Event'
                }
            ]
        }

def test_list_upcoming_events(monkeypatch):
    # freeze now so list_upcoming_events uses a known datetime
    monkeypatch.setattr(calendar_utils.datetime, 'datetime', datetime.datetime)
    dummy = DummyService()
    events = list_upcoming_events(dummy, max_results=1)
    assert isinstance(events, list)
    assert events[0]['summary'] == 'Test Event'

def test_create_event_response():
    dummy = DummyService()
    body = {
        'summary': 'New Event',
        'start': {'dateTime': '2025-02-02T12:00:00Z'},
        'end': {'dateTime': '2025-02-02T13:00:00Z'}
    }
    response = create_event(dummy, body)
    assert response['id'] == 'abc123'
    assert response['summary'] == 'New Event'
