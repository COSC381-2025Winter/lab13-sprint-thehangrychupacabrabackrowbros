import pytest
import datetime
import json
from unittest.mock import Mock, patch, mock_open
from calendar_utils import add_tasks_from_json

# Sample task data to be used in test
mock_task_data = [
    {
        "title": "Test Task 1",
        "description": "Test description 1",
        "start": "2025-04-20T10:00:00",
        "end": "2025-04-20T11:00:00",
        "timeZone": "America/New_York"
    }
]

# Simulated existing calendar event (to test duplicates)
mock_existing_events = [
    {
        "summary": "Existing Event",
        "start": {"dateTime": "2025-04-20T09:00:00"}
    },
    {
        "summary": "Test Task 1",
        "start": {"dateTime": "2025-04-20T10:00:00"}
    }
]

@pytest.fixture
def mock_service():
    # Mock the Google Calendar service
    service = Mock()
    events = service.events.return_value
    events.list.return_value.execute.return_value = {"items": mock_existing_events}
    events.insert.return_value.execute.return_value = {"htmlLink": "http://calendar.google.com/testevent"}
    return service

@patch("calendar_utils.json.load")
@patch("builtins.open", new_callable=mock_open)
def test_add_tasks_skips_duplicate(mock_open_fn, mock_json_load, mock_service):
    mock_json_load.return_value = mock_task_data

    # Call the function
    add_tasks_from_json(mock_service, json_path="task_data.json")

    # Since it's a duplicate, insert should not be called
    mock_service.events.return_value.insert.assert_not_called()

@patch("calendar_utils.json.load")
@patch("builtins.open", new_callable=mock_open)
def test_add_tasks_adds_new_event(mock_open_fn, mock_json_load, mock_service):
    # Slightly alter time so it's not a duplicate
    new_task = mock_task_data[0].copy()
    new_task["start"] = "2025-04-20T12:00:00"
    new_task["end"] = "2025-04-20T13:00:00"
    mock_json_load.return_value = [new_task]

    # Call the function
    add_tasks_from_json(mock_service, json_path="task_data.json")

    # Should call insert for the new event
    mock_service.events.return_value.insert.assert_called_once()