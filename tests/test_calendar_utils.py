import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from calendar_utils import list_upcoming_events, create_event

class FakeService:
    """
    Mimics the shape of service.events().list(...).execute()
    and service.events().insert(...).execute()
    """
    def __init__(self, items=None):
        self._items = items or []
        self.insert_args = None

    def events(self):
        return self

    def list(self, calendarId, timeMin, maxResults, singleEvents, orderBy):
        # store the parameters for sanity-checking if you like
        self.last_list_kwargs = {
            "calendarId": calendarId,
            "timeMin": timeMin,
            "maxResults": maxResults,
            "singleEvents": singleEvents,
            "orderBy": orderBy,
        }
        return self

    def insert(self, calendarId, body):
        # record what was passed in, and reuse this object
        self.insert_args = (calendarId, body)
        return self

    def execute(self):
        # if insert_args is set, return an “inserted” event dict
        if self.insert_args:
            cal_id, body = self.insert_args
            return {"calendarId": cal_id, **body}
        # otherwise we’re coming from list()
        return {"items": self._items}


def test_list_upcoming_events_empty():
    fake = FakeService(items=[])
    events = list_upcoming_events(fake, max_results=3)
    assert events == []


def test_list_upcoming_events_non_empty():
    sample = [
        {"id": "evt1", "summary": "First"},
        {"id": "evt2", "summary": "Second"},
    ]
    fake = FakeService(items=sample)
    events = list_upcoming_events(fake, max_results=2)
    assert events == sample


def test_create_event_returns_body_plus_calendarId():
    body = {
        "summary": "My Test Event",
        "start": {"dateTime": "2025-01-01T10:00:00Z"},
        "end": {"dateTime": "2025-01-01T11:00:00Z"},
    }
    fake = FakeService()
    result = create_event(fake, body)
    # should echo back calendarId='primary' plus all keys of body
    assert result["calendarId"] == "primary"
    assert result["summary"] == "My Test Event"
    assert result["start"]["dateTime"] == "2025-01-01T10:00:00Z"
    assert result["end"]["dateTime"] == "2025-01-01T11:00:00Z"
    # ensure insert was called with correct args
    assert fake.insert_args == ("primary", body)
