import pytest
import calendar_utils

class FakeEventsList:
    def __init__(self, items):
        self._items = items
    def list(self, calendarId, timeMin, maxResults, singleEvents, orderBy):
        return self
    def execute(self):
        return {"items": self._items}

class FakeEventsInsert:
    def __init__(self, body):
        self._body = body
    def insert(self, calendarId, body):
        self._body = body
        return self
    def execute(self):
        # mimic API returning the created event
        return {"created": True, **self._body}

def test_list_upcoming_events_returns_items(monkeypatch):
    fake_items = [
        {"id": "1", "summary": "Test Event", "start": {"dateTime": "2025-01-01T10:00:00Z"}}
    ]
    fake_service = type("S", (), {"events": lambda self: FakeEventsList(fake_items)})()
    result = calendar_utils.list_upcoming_events(fake_service, max_results=1)
    assert result == fake_items

def test_list_upcoming_events_defaults_empty(monkeypatch):
    fake_service = type("S", (), {"events": lambda self: FakeEventsList([])})()
    result = calendar_utils.list_upcoming_events(fake_service)
    assert result == []

def test_create_event_calls_insert_and_returns_body(monkeypatch):
    event_body = {"summary": "New Meeting", "start": {"dateTime": "2025-02-02T14:00:00Z"}, "end": {"dateTime": "2025-02-02T15:00:00Z"}}
    fake_service = type("S", (), {"events": lambda self: FakeEventsInsert(event_body)})()
    created = calendar_utils.create_event(fake_service, event_body)
    assert created.get("created") is True
    assert created["summary"] == event_body["summary"]
    assert created["start"] == event_body["start"]
    assert created["end"] == event_body["end"]
