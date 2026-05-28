import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_data():
    with TestClient(app) as client:
        response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant_for_activity():
    email = "newstudent@mergington.edu"

    with TestClient(app) as client:
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_is_rejected():
    email = "michael@mergington.edu"

    with TestClient(app) as client:
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_from_activity():
    email = "daniel@mergington.edu"

    with TestClient(app) as client:
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": email},
        )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_delete_nonexistent_participant_returns_404():
    email = "unknown@mergington.edu"

    with TestClient(app) as client:
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": email},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
