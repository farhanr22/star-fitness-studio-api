"""Integration tests for the classes module."""

from fastapi.testclient import TestClient


def test_create_class_success(authenticated_client: TestClient):
    """Test successful class creation as an authenticated user."""

    class_data = {
        "name": "Stretching Class",
        "instructor": "Example Name",
        "dateTime": "2029-01-01T07:00:00Z",
        "availableSlots": 20,
    }
    response = authenticated_client.post("/classes", json=class_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == class_data["name"]
    assert data["instructor"] == class_data["instructor"]
    assert data["availableSlots"] == class_data["availableSlots"]
    assert "id" in data
    # Check if the response dateTime matches the input, formatted as UTC Z
    assert data["dateTime"] == "2029-01-01T07:00:00Z"


def test_create_class_unauthenticated(client: TestClient):
    """Test that creating a class fails without authentication."""
    
    class_data = {
        "name": "Exercise Class",
        "instructor": "First Name",
        "dateTime": "2029-01-01T18:00:00Z",
        "availableSlots": 15,
    }
    response = client.post("/classes", json=class_data)
    assert response.status_code == 401
    assert response.json()["errors"][0]["msg"] == "Not authenticated"


def test_create_class_in_the_past(authenticated_client: TestClient):
    """Test that creating a class with a past datetime fails."""
    
    class_data = {
        "name": "Past Class",
        "instructor": "Example Name",
        "dateTime": "2020-01-01T10:00:00Z",  # A date in the past
        "availableSlots": 10,
    }
    response = authenticated_client.post("/classes", json=class_data)
    assert response.status_code == 400
    assert response.json()["errors"][0]["msg"] == "Cannot create a class in the past"


def test_create_class_instructor_conflict(authenticated_client: TestClient):
    """Test that an instructor cannot be booked for two classes at the same time."""
    
    time_slot = "2029-02-15T12:00:00Z"
    instructor_name = "Neutral Name"

    class_data_1 = {
        "name": "Morning Class",
        "instructor": instructor_name,
        "dateTime": time_slot,
        "availableSlots": 10,
    }
    response1 = authenticated_client.post("/classes", json=class_data_1)
    assert response1.status_code == 201

    class_data_2 = {
        "name": "Afternoon Class",
        "instructor": instructor_name,  # Same instructor
        "dateTime": time_slot,  # Same time
        "availableSlots": 15,
    }
    response2 = authenticated_client.post("/classes", json=class_data_2)
    assert response2.status_code == 409
    assert (
        response2.json()["errors"][0]["msg"]
        == "This instructor is already booked for a class at this time"
    )


def test_get_upcoming_classes(authenticated_client: TestClient):
    """Test fetching all upcoming classes."""
    
    # Create a class in the past and two in the future
    past_class = {
        "name": "Old Class",
        "instructor": "Past Name",
        "dateTime": "2021-01-01T10:00:00Z",
        "availableSlots": 5,
    }
    future_class_1 = {
        "name": "Future Class 1",
        "instructor": "Future Name 1",
        "dateTime": "2030-01-01T10:00:00Z",
        "availableSlots": 10,
    }
    future_class_2 = {
        "name": "Future Class 2",
        "instructor": "Future Name 2",
        "dateTime": "2030-01-02T10:00:00Z",
        "availableSlots": 15,
    }

    authenticated_client.post("/classes", json=past_class)
    authenticated_client.post("/classes", json=future_class_1)
    authenticated_client.post("/classes", json=future_class_2)

    # Fetch the classes
    response = authenticated_client.get("/classes")
    assert response.status_code == 200

    # Test: Only the two future classes should be returned
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Future Class 1"
    assert data[1]["name"] == "Future Class 2"
