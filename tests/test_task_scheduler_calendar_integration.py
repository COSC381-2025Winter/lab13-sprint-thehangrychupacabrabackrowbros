import sys
import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import task_scheduler_gui as gui

# 🔁 Fixture: resets GUI + state between test runs
@pytest.fixture(autouse=True)
def clear_gui_state():
    gui.all_tasks.clear()
    gui.checkbox_refs.clear()

@patch("task_scheduler_gui.get_calendar_service")
@patch("task_scheduler_gui.list_all_events")
def test_fetch_calendar_tasks_returns_formatted_list(mock_list, mock_service):
    # Arrange mock event
    mock_list.return_value = [{
        "summary": "Test Event",
        "start": {"dateTime": "2025-04-20T10:00:00"},
        "end": {"dateTime": "2025-04-20T11:00:00"}
    }]
    
    # Act
    tasks = gui.fetch_calendar_tasks()
    
    # Assert
    assert isinstance(tasks, list)
    assert tasks[0]["task_name"] == "Test Event"
    assert tasks[0]["duration"] == "1 hour\t"
    assert tasks[0]["date"].isoformat().startswith("2025-04-20T10:00")


@patch("task_scheduler_gui.get_calendar_service")
@patch("task_scheduler_gui.list_all_events")
def test_fetch_calendar_tasks_with_missing_fields(mock_list, mock_service):
    # Events with missing summary or dateTime should be skipped
    mock_list.return_value = [
        {"summary": "", "start": {"dateTime": "2025-04-20T10:00:00"}},
        {"summary": "Missing start"},
        {"start": {"dateTime": "2025-04-20T10:00:00"}}
    ]
    
    tasks = gui.fetch_calendar_tasks()
    assert tasks == []


@patch("task_scheduler_gui.fetch_calendar_tasks")
def test_refresh_task_list_periodically_runs_without_crashing(mock_fetch):
    mock_fetch.return_value = []
    gui.app.after(1, lambda: gui.app.quit())  # Quit quickly after run
    gui.refresh_task_list_periodically()
    assert mock_fetch.called  # Ensure the fetch_calendar_tasks function was called

from unittest.mock import patch, MagicMock
from datetime import datetime

@patch("task_scheduler_gui.get_calendar_service", side_effect=Exception("Fail"))
def test_clear_completed_tasks_no_service(mock_service):
    # Set up a mocked checkbox that is "checked"
    checkbox_mock = MagicMock()
    checkbox_mock.get.return_value = 1

    frame_mock = MagicMock()
    gui.checkbox_refs.clear()
    gui.checkbox_refs.append((
        {"task_name": "Fake", "start_datetime": datetime.now()},
        checkbox_mock,
        frame_mock
    ))

    gui.clear_completed_tasks()

    # checkbox_refs should be cleared (because task was "checked")
    assert len(gui.checkbox_refs) == 0

    # all_tasks should also be cleared
    assert len(gui.all_tasks) == 0
