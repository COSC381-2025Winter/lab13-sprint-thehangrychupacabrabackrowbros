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

@pytest.fixture(autouse=True)
def clear_state():
    all_tasks.clear()
    checkbox_refs.clear()
    task_entry.delete("1.0", "end")
    yield
    all_tasks.clear()
    checkbox_refs.clear()

@patch("task_scheduler_gui.create_event")
@patch("calendar_utils.get_calendar_service")
def test_submit_task_creates_calendar_event(mock_service, mock_create):
    # Setup input fields
    month_var.set("4")
    day_var.set("20")
    year_entry.delete(0, "end")
    year_entry.insert(0, "2025")
    hour_var.set("10")
    minute_var.set("30")
    am_pm_var.set("AM")
    duration_var.set("1")
    task_entry.insert("1.0", "Calendar Test Task")

    mock_service.return_value = MagicMock()
    mock_create.return_value = {"status": "confirmed"}

    submit_task()

    assert len(all_tasks) == 1
    mock_create.assert_called_once()
    assert all_tasks[0]["task_name"] == "Calendar Test Task"

@patch("task_scheduler_gui.delete_task")
@patch("calendar_utils.get_calendar_service")
def test_clear_completed_tasks_deletes_calendar_event(mock_service, mock_delete):
    task = {
        "date": datetime(2025, 4, 20),
        "time": datetime(2000, 1, 1, 10, 0),
        "duration": "1 hour",
        "task_name": "To Be Deleted"
    }
    all_tasks.append(task)

    class DummyVar:
        def __init__(self): self.value = 1  # ✅ Task is checked
        def get(self): return self.value

    class DummyFrame:
        def destroy(self): pass

    checkbox_refs.append((task, DummyVar(), DummyFrame()))
    mock_service.return_value = MagicMock()

    clear_completed_tasks()

    # ✅ Assert the calendar deletion was triggered
    mock_delete.assert_called_once()
    called_args = mock_delete.call_args[0]
    assert called_args[1] == "To Be Deleted"
    assert called_args[2].startswith("2000-01-01T10:00")
