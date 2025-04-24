import sys
import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from task_scheduler_gui import (
    submit_task,
    clear_completed_tasks,
    all_tasks,
    checkbox_refs,
    task_entry,
    task_hint,
    month_var,
    day_var,
    year_entry,
    hour_var,
    minute_var,
    am_pm_var,
    duration_var,
)

# 🔁 Fixture: resets GUI + state between test runs
@pytest.fixture(autouse=True)
def reset_gui_state():
    # Clear form input
    task_entry.delete("1.0", "end")
    month_var.set("")
    day_var.set("")
    year_entry.delete(0, "end")
    hour_var.set("")
    minute_var.set("")
    am_pm_var.set("AM")
    duration_var.set("")
    all_tasks.clear()
    checkbox_refs.clear()
    yield
    all_tasks.clear()
    checkbox_refs.clear()

# 🧪 Integration: Submitting a task pushes to calendar
@patch("calendar_utils.get_calendar_service")
@patch("task_scheduler_gui.create_event")
def test_submit_task_triggers_calendar_upload(mock_create_event, mock_get_service):
    # Simulate form inputs
    month_var.set("4")
    day_var.set("20")
    year_entry.insert(0, "2025")
    hour_var.set("10")
    minute_var.set("30")
    am_pm_var.set("AM")
    duration_var.set("1")
    task_entry.insert("1.0", "Calendar Integration Test")

    # Stub external dependencies
    mock_get_service.return_value = MagicMock()
    mock_create_event.return_value = {"status": "confirmed"}

    # Submit task
    submit_task()

    # Confirm internal state
    assert len(all_tasks) == 1
    assert all_tasks[0]["task_name"] == "Calendar Integration Test"

    # Confirm calendar call
    mock_create_event.assert_called_once()
    event_body = mock_create_event.call_args[0][1]
    assert event_body["summary"] == "Calendar Integration Test"
    assert "2025-04-20T10:30" in event_body["start"]["dateTime"]

# 🧪 Integration: Completed task is deleted from calendar
@patch("calendar_utils.get_calendar_service")
@patch("task_scheduler_gui.delete_task")
def test_clear_checked_tasks_removes_calendar_entry(mock_delete_task, mock_get_service):
    # Add a test task that simulates being 'checked'
    test_task = {
        "task_name": "Old Task",
        "date": datetime(2025, 4, 20),
        "time": datetime(2000, 1, 1, 10, 0),
        "duration": "1 hour",
        "start_datetime": datetime(2025, 4, 20, 10, 0)
    }

    class MockCheckbox:
        def get(self): return 1  # Marked as complete

    class MockFrame:
        def destroy(self): pass

    all_tasks.append(test_task)
    checkbox_refs.append((test_task, MockCheckbox(), MockFrame()))

    # Simulate calendar service
    mock_get_service.return_value = MagicMock()

    # Run deletion
    clear_completed_tasks()

    # Assertions
    mock_delete_task.assert_called_once()
    args = mock_delete_task.call_args[0]
    assert args[1] == "Old Task"
    assert args[2].startswith("2025-04-20T10:00")

    # Local list cleanup
    assert not all_tasks
    assert not checkbox_refs