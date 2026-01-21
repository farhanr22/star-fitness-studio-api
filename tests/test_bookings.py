"""Integration tests for the bookings module."""

from typing import Dict, Any
from fastapi.testclient import TestClient


def create_class_for_booking(
    client: TestClient,
    slots: int,
    instructor: str = "Booking Tester",
    dt: str = "2030-05-20T10:00:00Z",
) -> Dict[str, Any]:
    """Helper function to create a class with customizable details."""
    
    class_data = {
        "name": "Test Booking Class",
        "instructor": instructor,
        "dateTime": dt,
        "availableSlots": slots,
    }
    response = client.post("/classes", json=class_data)
    assert response.status_code == 201, f"Failed to create class: {response.text}"
    return response.json()


def test_book_class_success(authenticated_client: TestClient):
    """Test successful class booking."""
    
    created_class = create_class_for_booking(authenticated_client, 5)

    booking_data = {
        "class_id": created_class["id"],
        "client_name": "Test Booker",
        "client_email": "booker@example.com",
    }
    response = authenticated_client.post("/book", json=booking_data)
    assert response.status_code == 201

    data = response.json()
    assert data["class_id"] == created_class["id"]

    class_details_response = authenticated_client.get("/classes")
    updated_class = next(
        c for c in class_details_response.json() if c["id"] == created_class["id"]
    )
    assert updated_class["availableSlots"] == 4


def test_book_full_class(client: TestClient, authenticated_client: TestClient):
    """Test that booking a class with no available slots fails."""
    
    # Create a class with 1 slot using the first authenticated user
    created_class = create_class_for_booking(authenticated_client, 1)

    # First user books the last slot successfully
    booking_data = {
        "class_id": created_class["id"],
        "client_name": "First Booker",
        "client_email": "first@example.com",
    }
    response1 = authenticated_client.post("/book", json=booking_data)
    assert response1.status_code == 201

    # Create and authenticate a second user
    user_2_data = {
        "name": "Second User",
        "email": "user2@example.com",
        "password": "pw",
    }
    signup_resp = client.post("/signup", json=user_2_data)
    assert signup_resp.status_code == 201

    login_resp = client.post(
        "/login",
        json={"email": user_2_data["email"], "password": user_2_data["password"]},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    client.headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/book", json=booking_data)

    # Test
    assert response.status_code == 409
    assert response.json()["errors"][0]["msg"] == "Class is full, no available slots"


def test_user_cannot_book_same_class_twice(authenticated_client: TestClient):
    """Test that a user is prevented from booking the same class more than once."""
    
    created_class = create_class_for_booking(authenticated_client, 2)
    booking_data = {
        "class_id": created_class["id"],
        "client_name": "Test Name",
        "client_email": "name@example.com",
    }

    response1 = authenticated_client.post("/book", json=booking_data)
    assert response1.status_code == 201

    response2 = authenticated_client.post("/book", json=booking_data)
    assert response2.status_code == 409
    assert response2.json()["errors"][0]["msg"] == "You have already booked this class"


def test_get_my_bookings(authenticated_client: TestClient):
    """Test fetching all bookings for the authenticated user."""
    
    class1 = create_class_for_booking(
        authenticated_client, 5, instructor="Instructor A", dt="2030-01-01T10:00:00Z"
    )
    class2 = create_class_for_booking(
        authenticated_client, 5, instructor="Instructor B", dt="2030-01-02T10:00:00Z"
    )

    authenticated_client.post(
        "/book",
        json={
            "class_id": class1["id"],
            "client_name": "Client 1",
            "client_email": "c1@example.com",
        },
    )
    authenticated_client.post(
        "/book",
        json={
            "class_id": class2["id"],
            "client_name": "Client 2",
            "client_email": "c2@example.com",
        },
    )

    response = authenticated_client.get("/bookings")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["classId"] == class1["id"]
    assert data[1]["classId"] == class2["id"]
