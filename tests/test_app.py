import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # RedirectResponse
    assert "/static/index.html" in str(response.headers.get("location"))


def test_signup_success():
    # Use an activity with empty participants initially, like Basketball Team
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Basketball Team" in data["message"]

    # Check if added to participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "test@example.com" in activities["Basketball Team"]["participants"]


def test_signup_duplicate():
    # First signup
    client.post("/activities/Art%20Club/signup?email=duplicate@example.com")
    # Second signup same email
    response = client.post("/activities/Art%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity():
    response = client.post("/activities/NonExistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_missing_email():
    response = client.post("/activities/Chess%20Club/signup")
    assert response.status_code == 422  # Validation error for missing email


def test_signup_invalid_email_format():
    # The app doesn't validate email format, but we can test if it accepts any string
    response = client.post("/activities/Drama%20Club/signup?email=invalid-email")
    assert response.status_code == 200  # Since no validation, it accepts