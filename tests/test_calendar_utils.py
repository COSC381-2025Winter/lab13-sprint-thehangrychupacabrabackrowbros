import sys
import os
import pickle
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, mock_open

# ✅ Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import calendar_utils as utils

@patch("calendar_utils.pickle.dump")
@patch("calendar_utils.pickle.load")
@patch("calendar_utils.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open)
@patch("calendar_utils.build")
def test_get_calendar_service_existing_creds(mock_build, mock_open_file, mock_exists, mock_load, mock_dump):
    mock_creds = MagicMock(valid=True)
    mock_load.return_value = mock_creds

    service = utils.get_calendar_service()
    assert service == mock_build.return_value
    mock_build.assert_called_once()
    
from unittest.mock import patch, mock_open, MagicMock
import os

@patch("calendar_utils.pickle.load", return_value=None)
@patch("calendar_utils.os.path.exists", return_value=False)
@patch("calendar_utils.InstalledAppFlow.from_client_secrets_file")
@patch("calendar_utils.pickle.dump")
def test_get_calendar_service_auth_flow(mock_dump, mock_flow, mock_exists, mock_load):
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_flow.return_value.run_local_server.return_value = mock_creds

    from calendar_utils import get_calendar_service
    service = get_calendar_service()

    assert service is not None
    mock_flow.assert_called_once()
    mock_dump.assert_called_once()



@patch("calendar_utils.pickle.dump")
@patch("calendar_utils.os.path.exists", return_value=False)
@patch("calendar_utils.InstalledAppFlow.from_client_secrets_file")
@patch("builtins.open", new_callable=mock_open)
@patch("calendar_utils.build")
def test_get_calendar_service_new_creds(mock_build, mock_open_file, mock_flow, mock_exists, mock_dump):
    mock_creds = MagicMock(valid=True)
    mock_flow.return_value.run_local_server.return_value = mock_creds

    service = utils.get_calendar_service()
    assert service == mock_build.return_value


def test_list_all_events():
    mock_service = MagicMock()
    mock_service.events.return_value.list.return_value.execute.return_value = {"items": [{"summary": "Test Event"}]}
    events = utils.list_all_events(mock_service)
    assert isinstance(events, list)
    assert events[0]["summary"] == "Test Event"


def test_create_event():
    mock_service = MagicMock()
    mock_service.events.return_value.insert.return_value.execute.return_value = {"id": "123"}
    result = utils.create_event(mock_service, {"summary": "Test"})
    assert result["id"] == "123"


@patch("calendar_utils.list_all_events")
def test_delete_task_found(mock_list):
    mock_service = MagicMock()
    event = {
        "id": "abc123",
        "summary": "Task",
        "start": {"dateTime": "2025-04-20T10:00:00Z"}
    }
    mock_list.return_value = [event]
    utils.delete_task(mock_service, "Task", "2025-04-20T10:00")
    mock_service.events.return_value.delete.assert_called_once()


@patch("calendar_utils.list_all_events", return_value=[])
def test_delete_task_not_found(mock_list):
    mock_service = MagicMock()
    utils.delete_task(mock_service, "Nonexistent", "2025-04-20T10:00")
    mock_service.events.return_value.delete.assert_not_called()


@patch("builtins.open", new_callable=mock_open)
@patch("calendar_utils.json.dump")
@patch("calendar_utils.list_all_events")
@patch("calendar_utils.print")
def test_backup_calendar_to_json(mock_print, mock_list_all_events, mock_json_dump, mock_open_file):
    mock_service = MagicMock()

    now = datetime.now(timezone.utc)
    start = now.isoformat()
    end = (now + timedelta(hours=1)).isoformat()

    # Add events that should be skipped (to trigger the `continue`)
    mock_list_all_events.return_value = [
        {"start": {"dateTime": start}, "end": {"dateTime": end}},  # Missing summary
        {"summary": "No start"},  # Missing start
        {
            "summary": "Valid Task",
            "start": {"dateTime": start},
            "end": {"dateTime": end}
        }
    ]

    utils.backup_calendar_to_json(mock_service, out_path="temp.json")

    # Valid output should contain only one task
    dumped_data = mock_json_dump.call_args[0][0]
    assert len(dumped_data) == 1
    assert dumped_data[start[:10]][0]["task"] == "Valid Task"

    mock_open_file.assert_called_once_with("temp.json", "w")
    mock_json_dump.assert_called_once()
    mock_print.assert_called_with("📝 Backup saved to temp.json")



from unittest.mock import patch, mock_open, MagicMock
from calendar_utils import get_calendar_service

@patch("calendar_utils.build")
@patch("calendar_utils.pickle.load")
@patch("calendar_utils.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open)
def test_get_calendar_service_with_valid_token(mock_open_file, mock_exists, mock_pickle, mock_build):
    mock_creds = MagicMock()
    mock_creds.valid = True  # ✅ This skips the auth flow (line 30)
    mock_pickle.return_value = mock_creds

    get_calendar_service()
    mock_build.assert_called_once()


from unittest.mock import patch, MagicMock
from calendar_utils import delete_task, CALENDAR_ID

@patch("calendar_utils.list_all_events")
@patch("calendar_utils.print")
def test_delete_task_prints_deleted(mock_print, mock_list_events):
    # Arrange a mock service with a matching event
    mock_service = MagicMock()
    mock_events = mock_service.events.return_value
    mock_delete = mock_events.delete.return_value
    mock_delete.execute.return_value = None

    mock_list_events.return_value = [{
        "summary": "Test Task",
        "start": {"dateTime": "2025-04-20T10:00:00"},
        "id": "abc123"
    }]

    # Act
    delete_task(mock_service, "Test Task", "2025-04-20T10:00")

    # Assert
    mock_print.assert_called_with("🗑️ Deleted: Test Task at 2025-04-20T10:00")
    mock_events.delete.assert_called_once_with(
        calendarId=CALENDAR_ID,
        eventId="abc123"
    )

@patch("calendar_utils.pickle.dump")
@patch("calendar_utils.pickle.load")
@patch("calendar_utils.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open)
@patch("calendar_utils.build")
@patch("calendar_utils.Request")
def test_get_calendar_service_refresh_token(mock_request, mock_build, mock_open_file, mock_exists, mock_load, mock_dump):
    mock_creds = MagicMock()
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = True

    mock_load.return_value = mock_creds
    mock_creds.refresh.return_value = None

    service = utils.get_calendar_service()
    assert service == mock_build.return_value
    mock_creds.refresh.assert_called_once_with(mock_request.return_value)
