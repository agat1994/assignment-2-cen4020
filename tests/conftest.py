import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

SEED_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture
def sample_activities():
    """Small, predictable activity data for isolated tests."""
    return {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        }
    }


@pytest.fixture
def client(monkeypatch, sample_activities):
    """Client backed by fresh sample data; state never leaks between tests."""
    monkeypatch.setattr(app_module, "activities", sample_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


@pytest.fixture
def seeded_client(monkeypatch):
    """Client backed by a fresh copy of the app's shipped activity data."""
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(SEED_ACTIVITIES))

    with TestClient(app_module.app) as test_client:
        yield test_client
