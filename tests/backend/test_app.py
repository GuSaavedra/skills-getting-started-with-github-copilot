import copy
import pytest

from fastapi.testclient import TestClient
from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert isinstance(activities["Chess Club"]["participants"], list)


def test_signup_adds_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "runner.signup@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    refreshed = client.get("/activities").json()
    assert email in refreshed[activity_name]["participants"]


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "runner.remove@example.com"
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    # Act
    delete_response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"

    refreshed = client.get("/activities").json()
    assert email not in refreshed[activity_name]["participants"]
