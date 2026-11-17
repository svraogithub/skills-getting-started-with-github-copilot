from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_catalog_without_cache():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities
    assert response.headers["cache-control"] == "no-store"


def test_signup_adds_participant():
    activity_name = "Soccer Team"
    email = "test-student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities[activity_name]["participants"]


def test_signup_returns_not_found_for_unknown_activity():
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "test-student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant():
    activity_name = "Soccer Team"
    email = "test-student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"
    client.post(signup_url, params={"email": email})

    response = client.post(signup_url, params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"
    assert activities[activity_name]["participants"].count(email) == 1
