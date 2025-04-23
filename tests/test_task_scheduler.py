import os
os.environ["DATA_FILE"] = "tests/test_data_temp.json"

import pytest
import sys
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import task_scheduler_gui as gui

DATA_FILE = os.environ["DATA_FILE"]

@pytest.fixture(scope="function")
def setup_data_file():
    open(DATA_FILE, "w").close()
    yield
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def test_parse_date_valid():
    assert gui.parse_date("12", "25", "2025") == datetime(2025, 12, 25)

def test_parse_date_default_year():
    assert gui.parse_date("1", "1", "") == datetime(2025, 1, 1)

def test_parse_date_invalid():
    assert gui.parse_date("2", "30", "2025") is None

def test_format_time_pm():
    assert gui.format_time("2", "30", "PM") == datetime(2000, 1, 1, 14, 30)

def test_format_time_am():
    assert gui.format_time("12", "00", "AM") == datetime(2000, 1, 1, 0, 0)

def test_format_time_invalid():
    assert gui.format_time("13", "60", "AM") is None

@patch("task_scheduler_gui.messagebox.showinfo")
@patch("task_scheduler_gui.get_calendar_service")
@patch("task_scheduler_gui.create_event")
@patch.object(gui.task_entry, "get", return_value="A test task")
@patch.object(gui.month_var, "get", return_value="3")
@patch.object(gui.day_var, "get", return_value="15")
@patch.object(gui.year_entry, "get", return_value="2025")
@patch.object(gui.hour_var, "get", return_value="1")
@patch.object(gui.minute_var, "get", return_value="30")
@patch.object(gui.am_pm_var, "get", return_value="PM")
@patch.object(gui.duration_var, "get", return_value="1")
def test_submit_task_valid(mock_dur, mock_am, mock_min, mock_hr, mock_yr, mock_day, mock_month, mock_get, mock_create, mock_service, mock_info):
    gui.submit_task()
    mock_info.assert_called_once()
    assert len(gui.all_tasks) >= 1

@patch("task_scheduler_gui.messagebox.showerror")
@patch.object(gui.task_entry, "get", return_value="Write your task or describe it here.")
@patch.object(gui.month_var, "get", return_value="1")
@patch.object(gui.day_var, "get", return_value="1")
@patch.object(gui.year_entry, "get", return_value="2025")
def test_submit_task_empty_name(mock_yr, mock_day, mock_month, mock_get, mock_error):
    gui.submit_task()
    mock_error.assert_called_with("Missing Task", "Task name cannot be empty.")

@patch("task_scheduler_gui.messagebox.showerror")
@patch.object(gui.task_entry, "get", return_value="A test task")
@patch.object(gui.month_var, "get", return_value="2")
@patch.object(gui.day_var, "get", return_value="30")  # Invalid date
@patch.object(gui.year_entry, "get", return_value="2025")
def test_submit_task_invalid_date(mock_yr, mock_day, mock_month, mock_get, mock_error):
    gui.submit_task()
    mock_error.assert_called_with("Invalid Date", "Please enter a valid date.")

@patch.object(gui.submit_btn, 'configure')
@patch.object(gui.task_entry, 'get', return_value="A task")
def test_check_submit_ready_enables_button(mock_get, mock_config):
    gui.task_hint = "Write your task or describe it here."
    gui.check_submit_ready()
    mock_config.assert_called_with(state="normal", fg_color="#1B64C0")

@patch.object(gui.submit_btn, 'configure')
@patch.object(gui.task_entry, 'get', return_value="Write your task or describe it here.")
def test_check_submit_ready_disables_button_if_hint(mock_get, mock_config):
    gui.task_hint = "Write your task or describe it here."
    gui.check_submit_ready()
    mock_config.assert_called_with(state="disabled", fg_color="gray")

@patch.object(gui.submit_btn, 'configure')
@patch.object(gui.task_entry, 'get', return_value="")
def test_check_submit_ready_disables_button_if_empty(mock_get, mock_config):
    gui.task_hint = "Write your task or describe it here."
    gui.check_submit_ready()
    mock_config.assert_called_with(state="disabled", fg_color="gray")

def test_validate_year_input_invalid(monkeypatch):
    gui.year_entry.delete(0, "end")
    gui.year_entry.insert(0, "1999")
    gui.validate_year_input(MagicMock())
    assert gui.year_entry.get() == ""

def test_clear_task_hint_removes_hint():
    gui.task_entry.delete("1.0", "end")
    gui.task_entry.insert("1.0", gui.task_hint)
    gui.clear_task_hint()
    assert gui.task_entry.get("1.0", "end").strip() == ""

def test_set_task_hint_inserts_hint():
    gui.task_entry.delete("1.0", "end")
    gui.set_task_hint()
    assert gui.task_entry.get("1.0", "end").strip() == gui.task_hint

@patch("task_scheduler_gui.messagebox.showinfo")
@patch("task_scheduler_gui.get_calendar_service")
@patch("task_scheduler_gui.delete_task")
def test_clear_completed_tasks_shows_confirmation(mock_delete, mock_service, mock_info):
    var = MagicMock()
    var.get.return_value = 1
    fake_frame = MagicMock()
    gui.checkbox_refs.clear()
    gui.checkbox_refs.append((
        {"task_name": "Task 1", "start_datetime": datetime.now()}, var, fake_frame
    ))
    gui.clear_completed_tasks()
    mock_info.assert_called_once_with("Tasks Cleared", "Completed tasks have been removed and deleted from Google Calendar.")
