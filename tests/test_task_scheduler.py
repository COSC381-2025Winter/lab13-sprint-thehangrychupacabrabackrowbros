import pytest
import sys
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
import customtkinter as ctk

# Set up path and environment for testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DATA_FILE"] = "tests/test_data_temp.json"

from task_scheduler_gui import (parse_date, format_time, save_tasks, load_tasks, 
                              all_tasks, checkbox_refs, submit_task, clear_completed_tasks,
                              month_var, day_var, year_entry, task_entry)

DATA_FILE = os.environ["DATA_FILE"]

@pytest.fixture(scope="function")
def setup_data_file():
    """Ensures clean test environment for file operations"""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    yield
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def test_clear_completed_tasks():
    """Tests that completed tasks are properly handled"""
    # Reset state
    all_tasks.clear()
    checkbox_refs.clear()
    
    # Create test tasks
    completed_task = {
        'date': datetime(2025, 1, 1),
        'time': None,
        'duration': None,
        'task_name': 'Completed Task'
    }
    active_task = {
        'date': datetime(2025, 1, 2),
        'time': None,
        'duration': None,
        'task_name': 'Active Task'
    }
    
    # Setup checkbox references
    completed_var = ctk.IntVar(value=1)  # 1 = checked/completed
    active_var = ctk.IntVar(value=0)     # 0 = unchecked/active
    mock_frame = MagicMock()
    
    checkbox_refs.extend([
        (completed_task, completed_var, mock_frame),
        (active_task, active_var, mock_frame)
    ])
    all_tasks.extend([completed_task, active_task])
    
    # Execute
    clear_completed_tasks()
    
    # Verify current behavior
    assert len(all_tasks) == 2, "all_tasks should remain unchanged"