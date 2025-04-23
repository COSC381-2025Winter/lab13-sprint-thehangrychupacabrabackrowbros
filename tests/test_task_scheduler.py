import os
os.environ["DATA_FILE"] = "tests/test_data_temp.json"

import pytest
import sys
import json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from task_scheduler_gui import parse_date, format_time, save_tasks, load_tasks, all_tasks, checkbox_refs

DATA_FILE = os.environ["DATA_FILE"]

from unittest.mock import patch
@pytest.fixture(autouse=True)
def no_gui(monkeypatch):
    # Prevent CTk from trying to open a window
    monkeypatch.setattr("customtkinter.CTk", lambda *a, **kw: None)


@pytest.fixture(scope="function")
def setup_data_file():
    open(DATA_FILE, "w").close()
    yield
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def test_parse_date_valid():
    assert parse_date("12", "25", "2025") == datetime(2025, 12, 25)

def test_parse_date_default_year():
    assert parse_date("1", "1", "") == datetime(2025, 1, 1)

def test_parse_date_invalid():
    assert parse_date("2", "30", "2025") is None

def test_format_time_pm():
    assert format_time("2", "30", "PM") == datetime(2000, 1, 1, 14, 30)

def test_format_time_am():
    assert format_time("12", "00", "AM") == datetime(2000, 1, 1, 0, 0)

def test_format_time_invalid():
    assert format_time("13", "60", "AM") is None

def test_save_and_load_tasks(setup_data_file):
    all_tasks.clear()
    checkbox_refs.clear()
    all_tasks.extend([
        {"date": datetime(2025, 2, 2), "time": datetime(2000, 1, 1, 2, 0), "duration": "0.5 hours\t", "task_name": "Test"},
        {"date": datetime(2025, 3, 1), "time": datetime(2000, 1, 1, 1, 5), "duration": "0.5 hours\t", "task_name": "Test2"}
    ])
    save_tasks()
    assert os.path.exists(DATA_FILE)
    all_tasks.clear()
    checkbox_refs.clear()
    load_tasks()
    assert len(all_tasks) == 2
    assert all_tasks[0]['task_name'] == "Test"
    assert all_tasks[1]['task_name'] == "Test2"

def test_load_tasks_empty_file(setup_data_file):
    all_tasks.clear()
    checkbox_refs.clear()
    load_tasks()
    assert len(all_tasks) == 0

def test_save_tasks_file_structure(setup_data_file):
    all_tasks.clear()
    all_tasks.append({
        "date": datetime(2025, 2, 2),
        "time": datetime(2000, 1, 1, 2, 0),
        "duration": "0.5 hours\t",
        "task_name": "Test"
    })
    save_tasks()
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    assert "2025-02-02" in data
    assert data["2025-02-02"][0]["task"] == "Test"
    assert data["2025-02-02"][0]["duration"] == "0.5 hours\t"
    assert data["2025-02-02"][0]["time"] == "02:00"


# --- Additional Tests for Full Coverage ---

from unittest.mock import patch, MagicMock
import task_scheduler_gui as gui

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


@patch("task_scheduler_gui.messagebox.showerror")
@patch.object(gui.task_entry, "get", return_value="Valid Task")
@patch.object(gui.month_var, "get", return_value="2")
@patch.object(gui.day_var, "get", return_value="30")  # Invalid date
@patch.object(gui.year_entry, "get", return_value="2025")
def test_submit_task_invalid_date(mock_year, mock_day, mock_month, mock_get, mock_error):
    gui.submit_task()
    mock_error.assert_called_with("Invalid Date", "Please enter a valid date.")

@patch("task_scheduler_gui.messagebox.showerror")
@patch.object(gui.task_entry, "get", return_value="Write your task or describe it here.")
@patch.object(gui.month_var, "get", return_value="1")
@patch.object(gui.day_var, "get", return_value="1")
@patch.object(gui.year_entry, "get", return_value="2025")
def test_submit_task_empty_name(mock_year, mock_day, mock_month, mock_get, mock_error):
    gui.submit_task()
    mock_error.assert_called_with("Missing Task", "Task name cannot be empty.")

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

def test_platform_strftime_unix_then_windows():
    date = datetime(2025, 2, 2)
    result = gui.platform_strftime(date, "%-m/%-d/%y", "%#m/%#d/%y")
    # One of these two will succeed depending on the platform
    assert result in ["2/2/25", "02/02/25", "2/2/25", "2/2/2025"]
