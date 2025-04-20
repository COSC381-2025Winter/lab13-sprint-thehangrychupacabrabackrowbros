import os
os.environ["DATA_FILE"] = "tests/test_data_temp.json"

import pytest
import sys
import json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from task_scheduler_gui import parse_date, format_time, save_tasks, load_tasks, all_tasks, checkbox_refs

DATA_FILE = os.environ["DATA_FILE"]  # <- This is the missing piece

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

    assert os.path.exists(os.environ["DATA_FILE"])

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

    with open(os.environ["DATA_FILE"], "r") as f:
        data = json.load(f)

    assert "2025-02-02" in data
    assert data["2025-02-02"][0]["task"] == "Test"
    assert data["2025-02-02"][0]["duration"] == "0.5 hours\t"
    assert data["2025-02-02"][0]["time"] == "02:00"


# --- Additional Tests to Reach 100% Coverage ---

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
