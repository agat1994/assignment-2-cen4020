import pytest


@pytest.fixture
def full_client(sample_activities, client):
    sample_activities["Tiny Club"] = {
        "description": "Small club",
        "schedule": "Mondays",
        "max_participants": 1,
        "participants": ["only@mergington.edu"],
    }
    return client


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_participants = ["existing@mergington.edu"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == expected_participants


def test_signup_adds_participant(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_full_activity(full_client):
    # Arrange
    email = "late@mergington.edu"

    # Act
    response = full_client.post(
        "/activities/Tiny Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    participants = full_client.get("/activities").json()["Tiny Club"]["participants"]
    assert participants == ["only@mergington.edu"]


def test_signup_allowed_again_after_unregister_frees_spot(full_client):
    # Arrange
    full_client.delete(
        "/activities/Tiny Club/participants",
        params={"email": "only@mergington.edu"},
    )

    # Act
    response = full_client.post(
        "/activities/Tiny Club/signup",
        params={"email": "late@mergington.edu"},
    )

    # Assert
    assert response.status_code == 200


def test_signup_fills_last_spot(client, sample_activities):
    # Arrange
    activity = sample_activities["Chess Club"]
    activity["max_participants"] = len(activity["participants"]) + 1

    # Act
    first = client.post("/activities/Chess Club/signup", params={"email": "a@mergington.edu"})
    second = client.post("/activities/Chess Club/signup", params={"email": "b@mergington.edu"})

    # Assert
    assert first.status_code == 200
    assert second.status_code == 400


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
