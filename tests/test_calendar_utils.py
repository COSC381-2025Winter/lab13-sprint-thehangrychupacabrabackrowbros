import os
import pickle

import pytest

import calendar_utils
from calendar_utils import get_calendar_service

class DummyCreds:
    def __init__(self):
        self.valid = True
        self.expired = False
        self.refresh_token = None

@pytest.fixture(autouse=True)
def mock_oauth_flow_and_build(monkeypatch, tmp_path):
    # 1) Pretend there is no existing token.pickle
    monkeypatch.setattr(calendar_utils.os.path, "exists", lambda path: False)
    # 2) Fake the OAuth flow so run_local_server() returns DummyCreds()
    class FakeFlow:
        def run_local_server(self, port=0):
            return DummyCreds()
    monkeypatch.setattr(
        calendar_utils.InstalledAppFlow,
        "from_client_secrets_file",
        lambda creds_path, scopes: FakeFlow()
    )
    # 3) Stub out build() to return a sentinel
    monkeypatch.setattr(calendar_utils, "build", lambda service, version, credentials: "FAKE_SERVICE")
    # 4) Prevent actually writing a pickle
    monkeypatch.setattr(pickle, "dump", lambda obj, f: None)

def test_get_calendar_service_returns_fake_service():
    service = get_calendar_service()
    assert service == "FAKE_SERVICE"
