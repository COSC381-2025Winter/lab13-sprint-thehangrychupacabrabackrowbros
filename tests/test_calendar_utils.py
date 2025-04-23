import sys
import os
import json
import pytest
from datetime import datetime, timezone
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calendar_utils import add_tasks_from_json, delete_task, list_upcoming_events, create_event

class FakeService:
    def __init__(self, items=None):
        self._items = items or []
        self.inserted = []
        self.deleted = []

    def events(self):
        return self

    def list(self, **kwargs):
        return self

    def insert(self, calendarId, body):
        self.inserted.append((calendarId, body))
        return self

    def delete(self, calendarId, eventId):
        self.deleted.append((calendarId, eventId))
        return self

    def execute(self):
        if self.inserted:
            return {"status": "confirmed", **self.inserted[-1][1]}
        return {"items": self._items}

def test_list_upcoming_events_empty():
    fake = FakeService([])
    assert list_upcoming_events(fake, max_results=2) == []

def test_create_event_executes():
    service = FakeService()
    event = {
        "summary": "Unit Test Event",
        "start": {"dateTime": "2025-01-01T10:00:00Z"},
        "end": {"dateTime": "2025-01-01T11:00:00Z"}
    }
    result = create_event(service, event)
    assert result["summary"] == "Unit Test Event"

def test_add_tasks_from_json_skips_duplicates(tmp_path):
    json_path = tmp_path / "tasks.json"
    tasks = [
        {
            "title": "Duplicate",
            "start": "2025-04-20T10:00:00-04:00",
            "end": "2025-04-20T11:00:00-04:00"
        }
    ]
    json_path.write_text(json.dumps(tasks))
    fake = FakeService([{"summary": "Duplicate", "start": {"dateTime": "2025-04-20T10:00:00-04:00"}}])
    add_tasks_from_json(fake, str(json_path))

def test_add_tasks_from_json_creates_event(tmp_path):
    json_path = tmp_path / "tasks.json"
    tasks = [
        {
            "title": "New Task",
            "start": "2025-04-20T12:00:00-04:00",
            "end": "2025-04-20T13:00:00-04:00"
        }
    ]
    json_path.write_text(json.dumps(tasks))
    fake = FakeService([])
    add_tasks_from_json(fake, str(json_path))
    assert fake.inserted

def test_delete_task_finds_and_deletes(capfd):
    fake = FakeService([
        {"id": "1", "summary": "Meeting", "start": {"dateTime": "2025-04-20T10:00:00"}}
    ])
    delete_task(fake, "Meeting", "2025-04-20T10:00")
    out = capfd.readouterr().out
    assert "Deleted" in out

def test_delete_task_no_match(capfd):
    fake = FakeService([
        {"id": "2", "summary": "Other", "start": {"dateTime": "2025-04-20T11:00:00"}}
    ])
    delete_task(fake, "Meeting", "2025-04-20T10:00")
    out = capfd.readouterr().out
    assert "No matching event" in out
