import sys
import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add project root to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import task_scheduler_gui as gui

@pytest.fixture(autouse=True)
def reset_state():
    gui.all_tasks.clear()
    gui.checkbox_refs.clear()
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", gui.task_hint)
    gui.month_var.set("")
    gui.day_var.set("")
    gui.year_entry.delete(0, "end")
    gui.hour_var.set("")
    gui.minute_var.set("")
    gui.am_pm_var.set("AM")
    gui.duration_var.set("")
    yield

def test_vcmd_type():
    assert isinstance(gui.vcmd, str)

def test_numeric_only_accepts_digits():
    assert gui.numeric_only('5') is True
    assert gui.numeric_only('a') is False

def test_validate_year_input_invalid():
    gui.year_entry.delete(0, "end")
    gui.year_entry.insert(0, "2020")
    gui.validate_year_input(None)
    assert gui.year_entry.get() == ""

def test_validate_year_input_valid():
    gui.year_entry.delete(0, "end")
    gui.year_entry.insert(0, "2025")
    gui.validate_year_input(None)
    assert gui.year_entry.get() == "2025"

def test_check_submit_ready_all_states():
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", "")
    gui.check_submit_ready()
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", gui.task_hint)
    gui.check_submit_ready()
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", "Real task")
    gui.check_submit_ready()

def test_set_and_clear_hint_explicit():
    gui.task_entry.delete("1.0", "end")
    gui.set_task_hint()
    assert gui.task_entry.get("1.0", "end").strip() == gui.task_hint
    gui.clear_task_hint()
    assert gui.task_entry.get("1.0", "end").strip() == ""

def test_parse_date_variants():
    assert gui.parse_date("12", "25", "2025") == datetime(2025, 12, 25)
    assert gui.parse_date("1", "1", "") == datetime(2025, 1, 1)
    assert gui.parse_date("2", "30", "2025") is None

def test_format_time_variants():
    assert gui.format_time("12", "00", "AM") == datetime(2000, 1, 1, 0, 0)
    assert gui.format_time("1", "00", "PM") == datetime(2000, 1, 1, 13, 0)
    assert gui.format_time("xx", "00", "AM") is None

@patch("task_scheduler_gui.messagebox.showerror")
def test_submit_task_empty_task(mock_error):
    # Set up a valid date
    gui.month_var.set("4")
    gui.day_var.set("20")
    gui.year_entry.delete(0, "end")
    gui.year_entry.insert(0, "2025")

    # Valid time
    gui.hour_var.set("10")
    gui.minute_var.set("30")
    gui.am_pm_var.set("AM")

    # Valid duration
    gui.duration_var.set("1")

    # Clear task name (simulate user didn't type anything)
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", gui.task_hint)

    # Run submission
    gui.submit_task()

    # Expect it to complain about missing task name, not date
    mock_error.assert_called_with("Missing Task", "Task name cannot be empty.")


@patch("task_scheduler_gui.messagebox.showerror")
def test_submit_task_invalid_date(mock_error):
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", "Some task")
    gui.month_var.set("2")
    gui.day_var.set("30")
    gui.year_entry.delete(0, "end")
    gui.year_entry.insert(0, "2025")
    assert gui.task_entry.get("1.0", "end").strip() == "Some task"
    gui.submit_task()
    mock_error.assert_called_with("Invalid Date", "Please enter a valid date.")
    

@patch("task_scheduler_gui.messagebox.showerror")
def test_submit_task_invalid_duration_type(mock_error):
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", "Duration error")
    gui.month_var.set("4")
    gui.day_var.set("20")
    gui.year_entry.delete(0, "end")
    gui.year_entry.insert(0, "2025")
    gui.hour_var.set("10")
    gui.minute_var.set("00")
    gui.duration_var.set("abc")
    gui.submit_task()
    mock_error.assert_called_with("Invalid Duration", "Please enter a valid numeric duration.")

@patch("task_scheduler_gui.backup_calendar_to_json")
@patch("task_scheduler_gui.create_event")
@patch("task_scheduler_gui.get_calendar_service")
@patch("task_scheduler_gui.messagebox.showinfo")
def test_submit_task_success(mock_info, mock_service, mock_create, mock_backup):
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", "Test Task")
    gui.month_var.set("4")
    gui.day_var.set("20")
    gui.year_entry.delete(0, "end")
    gui.year_entry.insert(0, "2025")
    gui.hour_var.set("10")
    gui.minute_var.set("00")
    gui.am_pm_var.set("AM")
    gui.duration_var.set("1")
    gui.submit_task()
    mock_create.assert_called_once()
    mock_info.assert_called_once()
    mock_backup.assert_called_once()

@patch("task_scheduler_gui.messagebox.showerror")
@patch("task_scheduler_gui.create_event", side_effect=Exception("fail"))
@patch("task_scheduler_gui.get_calendar_service")
def test_submit_task_event_creation_failure(mock_service, mock_create, mock_error):
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", "Test Failure")
    gui.month_var.set("4")
    gui.day_var.set("20")
    gui.year_entry.delete(0, "end")
    gui.year_entry.insert(0, "2025")
    gui.hour_var.set("10")
    gui.minute_var.set("00")
    gui.duration_var.set("1")
    gui.submit_task()
    mock_error.assert_called()
    assert "fail" in mock_error.call_args[0][1]

@patch("task_scheduler_gui.get_calendar_service", side_effect=Exception("fetch fail"))
def test_fetch_calendar_tasks_fail(mock_service):
    assert gui.fetch_calendar_tasks() == []

def test_sort_tasks_duration():
    gui.all_tasks.clear()
    gui.all_tasks.append({
        "date": datetime(2025, 4, 20),
        "time": None,
        "duration": "1 hour",
        "task_name": "Test Task",
        "start_datetime": datetime(2025, 4, 20, 10, 0)
    })
    gui.sort_tasks()
    assert gui.task_list_container.winfo_children()

def test_main_guard(monkeypatch):
    import importlib
    monkeypatch.setattr("builtins.__name__", "__main__")
    importlib.reload(gui)
    assert gui.task_list_container is not None


def test_numeric_only_with_vcmd_call():
    assert gui.app.register(gui.numeric_only)  # matches line 24

@patch("task_scheduler_gui.messagebox.showinfo")
@patch("task_scheduler_gui.get_calendar_service")
@patch("task_scheduler_gui.delete_task")
def test_clear_completed_tasks_triggers_info(mock_delete, mock_service, mock_info):
    var = MagicMock()
    var.get.return_value = 1
    frame = MagicMock()
    gui.checkbox_refs.append(({
        "task_name": "Test Clear",
        "start_datetime": datetime(2025, 4, 20, 10, 0)
    }, var, frame))
    gui.clear_completed_tasks()
    mock_info.assert_called_once_with("Tasks Cleared", "Completed tasks have been removed and deleted from Google Calendar.")
