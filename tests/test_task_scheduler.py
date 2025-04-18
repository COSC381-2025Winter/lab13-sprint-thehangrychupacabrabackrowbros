import pytest
import sys
import os
import json
from datetime import datetime

# Set up path and environment for testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DATA_FILE"] = "tests/test_data_temp.json"

from task_scheduler_gui import parse_date, format_time, save_tasks, load_tasks, all_tasks, checkbox_refs

DATA_FILE = os.environ["DATA_FILE"]

@pytest.fixture(scope="function")
def setup_data_file():
    # Ensure the test file is clean before and after
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
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
    test_tasks = [
        {"date": datetime(2025, 1, 1), "time": datetime(2000, 1, 1, 9, 0), "duration": "1 hour", "task_name": "Test Task 1"},
        {"date": datetime(2025, 1, 2), "time": datetime(2000, 1, 1, 10, 0), "duration": "2 hours", "task_name": "Test Task 2"}
    ]

    all_tasks.clear()
    checkbox_refs.clear()
    all_tasks.extend(test_tasks)
    save_tasks()

    assert os.path.exists(DATA_FILE)

    all_tasks.clear()
    checkbox_refs.clear()
    load_tasks()

    assert len(all_tasks) == 2
    assert all_tasks[0]['task_name'] == "Test Task 1"
    assert all_tasks[1]['duration'] == "2 hours"

def test_load_tasks_empty_file(setup_data_file):
    all_tasks.clear()
    load_tasks()
    assert len(all_tasks) == 0

def test_save_tasks_file_structure(setup_data_file):
    all_tasks.clear()
    all_tasks.append({"date": datetime(2025, 1, 1), "time": None, "duration": None, "task_name": "Task without time and duration"})
    save_tasks()

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    assert "2025-01-01" in data
    assert data["2025-01-01"][0]["task"] == "Task without time and duration"
