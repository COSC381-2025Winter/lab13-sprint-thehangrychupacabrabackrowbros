import sys
import os
import pytest
from calendar_utils import list_upcoming_events, create_event, delete_task

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class FakeService:
    """
    Mimics the shape of service.events().list(...).execute(),
    service.events().insert(...).execute(), and service.events().delete(...).execute()
    """
    def __init__(self, items=None):
        self._items = items or []
        self.insert_args = None
        self.deleted_event = None  # Added for testing deletion

    def events(self):
        return self

    def list(self, calendarId, timeMin, maxResults, singleEvents, orderBy):
        # Store the parameters for sanity-checking if you like
        self.last_list_kwargs = {
            "calendarId": calendarId,
            "timeMin": timeMin,
            "maxResults": maxResults,
            "singleEvents": singleEvents,
            "orderBy": orderBy,
        }
        return self

    def insert(self, calendarId, body):
        # Record what was passed in, and reuse this object
        self.insert_args = (calendarId, body)
        return self

    def delete(self, calendarId, eventId):
        # Only mock deletion if the event ID actually matches
        matching_event = next(
            (event for event in self._items if event["id"] == eventId), None
        )
        if matching_event:
            self.deleted_event = {
                "calendarId": calendarId,
                "eventId": eventId,
            }
        else:
            self.deleted_event = None  # Ensure it's not set when no event is found

        return self

    def execute(self):
        # If insert_args is set, return an “inserted” event dict
        if self.insert_args:
            cal_id, body = self.insert_args
            return {"calendarId": cal_id, **body}
        # If delete_args is set, return a mock delete response
        elif self.deleted_event:
            return self.deleted_event
        # Otherwise, we’re coming from list()
        return {"items": self._items}


    def execute(self):
        # If insert_args is set, return an “inserted” event dict
        if self.insert_args:
            cal_id, body = self.insert_args
            return {"calendarId": cal_id, **body}
        # If delete_args is set, return a mock delete response
        elif self.deleted_event:
            return self.deleted_event
        # Otherwise, we’re coming from list()
        return {"items": self._items}


# Test for `list_upcoming_events`
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


# Test for `create_event`
def test_create_event_returns_body_plus_calendarId():
    body = {
        "summary": "My Test Event",
        "start": {"dateTime": "2025-01-01T10:00:00Z"},
        "end": {"dateTime": "2025-01-01T11:00:00Z"},
    }
    fake = FakeService()
    result = create_event(fake, body)
    # Should echo back calendarId='primary' plus all keys of body
    assert result["calendarId"] == "primary"
    assert result["summary"] == "My Test Event"
    assert result["start"]["dateTime"] == "2025-01-01T10:00:00Z"
    assert result["end"]["dateTime"] == "2025-01-01T11:00:00Z"
    # Ensure insert was called with correct args
    assert fake.insert_args == ("primary", body)


# Test for `delete_task`
def test_delete_task_finds_and_deletes_event():
    # Event matches title and datetime
    sample = [
        {
            "id": "evt123",
            "summary": "Test Meeting",
            "start": {"dateTime": "2025-04-20T10:00:00Z"},
        }
    ]
    fake = FakeService(items=sample)

    delete_task(fake, "Test Meeting", "2025-04-20T10:00")

    assert fake.deleted_event["calendarId"] == "primary"
    assert fake.deleted_event["eventId"] == "evt123"


def test_delete_task_no_match_does_not_delete():
    sample = [
        {
            "id": "evt456",
            "summary": "Different Meeting",
            "start": {"dateTime": "2025-04-20T11:00:00Z"},
        }
    ]
    fake = FakeService(items=sample)

    delete_task(fake, "Test Meeting", "2025-04-20T10:00")

    # Instead of checking attribute, check that delete_event was not set
    assert fake.deleted_event is None



# Test for `delete_task` print output
def test_delete_task_prints_success(capsys):
    sample = [
        {
            "id": "evt999",
            "summary": "Zoom Call",
            "start": {"dateTime": "2025-04-20T14:30:00Z"},
        }
    ]
    fake = FakeService(items=sample)
    delete_task(fake, "Zoom Call", "2025-04-20T14:30")

    captured = capsys.readouterr()
    assert "🗑️ Deleted: Zoom Call at 2025-04-20T14:30" in captured.out
