import os
import json
import pytest
from datetime import datetime
from pathlib import Path

from calendar_utils import (
    list_all_events,
    create_event,
    delete_task,
    backup_calendar_to_json
)

# Automatically clean up tests/test_data_temp.json before & after every test
@pytest.fixture(autouse=True)
def clean_test_data_temp():
    file_path = Path("tests/test_data_temp.json")
    if file_path.exists():
        file_path.unlink()
    yield
    if file_path.exists():
        file_path.unlink()

# ---- Fake Google API service for testing ----
class FakeService:
    def __init__(self, items=None):
        self._items = items or []
        self.inserted = []
        self.deleted = []

    def events(self):
        return self

    def list(self, **kwargs):
        return self

    def insert(self, calendar_id, body):
        self.inserted.append((calendarId, body))
        return self

    def delete(self, calendar_id, event_id):
        self.deleted.append((calendarId, eventId))
        return self

    def execute(self):
        if self.inserted:
            return {"status": "confirmed", **self.inserted[-1][1]}
        return {"items": self._items}

# -------------------- TESTS --------------------

def test_list_all_events_empty():
    fake = FakeService([])
    result = list_all_events(fake, max_results=5)
    assert result == []

def test_create_event_success():
    fake = FakeService()
    event = {
        "summary": "Unit Test Event",
        "start": {"dateTime": "2025-01-01T10:00:00"},
        "end": {"dateTime": "2025-01-01T11:00:00"},
        "description": ""
    }
    result = create_event(fake, event)
    assert result["summary"] == "Unit Test Event"
    assert result["status"] == "confirmed"

def test_delete_task_found(capfd):
    fake = FakeService([
        {"id": "abc123", "summary": "Meeting", "start": {"dateTime": "2025-04-20T10:00:00"}}
    ])
    delete_task(fake, "Meeting", "2025-04-20T10:00")
    out = capfd.readouterr().out
    assert "🗑️ Deleted: Meeting" in out
    assert fake.deleted[0][1] == "abc123"

def test_delete_task_not_found(capfd):
    fake = FakeService([
        {"id": "abc123", "summary": "Other", "start": {"dateTime": "2025-04-20T11:00:00"}}
    ])
    delete_task(fake, "Meeting", "2025-04-20T10:00")
    out = capfd.readouterr().out
    assert "❌ No matching event found for deletion" in out
    assert len(fake.deleted) == 0

def test_backup_calendar_to_json(capfd):
    fake = FakeService([
        {
            "summary": "Backup Task",
            "start": {"dateTime": "2025-04-20T09:00:00"},
            "end": {"dateTime": "2025-04-20T10:30:00"}
        },
        {
            "summary": "No end event",
            "start": {"dateTime": "2025-04-21T14:00:00"}
        },
        {
            "summary": "Invalid",
            "start": {},
            "end": {}
        }
    ])

    test_path = "tests/test_data_temp.json"
    backup_calendar_to_json(fake, test_path)

    assert os.path.exists(test_path)

    with open(test_path) as f:
        data = json.load(f)
        assert "2025-04-20" in data
        assert data["2025-04-20"][0]["task"] == "Backup Task"
        assert data["2025-04-20"][0]["duration"] == "1.5 hours\t"

    out = capfd.readouterr().out
    assert "📝 Backup saved to" in out