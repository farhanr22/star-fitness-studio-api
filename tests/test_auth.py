"""Integration tests for the authentication module."""

from fastapi.testclient import TestClient
from jose import jwt
import time

from app.core.config import settings


def test_signup_success(client: TestClient):
    """Test successful user registration."""
    
    response = client.post(
        "/signup",
        json={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User created successfully. Please log in."


def test_signup_duplicate_email(client: TestClient):
    """Test that signing up with a duplicate email fails."""
    
    user_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "password123",
    }
    
    # First signup should succeed
    response1 = client.post("/signup", json=user_data)
    assert response1.status_code == 201

    # Second signup with the same email should fail
    response2 = client.post("/signup", json=user_data)
    assert response2.status_code == 400
    error_data = response2.json()
    assert error_data["errors"][0]["msg"] == "User with this email already exists"


def test_login_success(client: TestClient):
    """Test successful user login and token generation."""
    
    user_data = {
        "name": "Test Login",
        "email": "login@example.com",
        "password": "password123",
    }
    client.post("/signup", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Verify the access token payload
    payload = jwt.decode(
        token_data["access_token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["email"] == user_data["email"]
    assert payload["type"] == "access"


def test_login_incorrect_password(client: TestClient):
    """Test that login fails with an incorrect password."""
    
    user_data = {
        "name": "Test Name",
        "email": "test@example.com",
        "password": "password123",
    }
    client.post("/signup", json=user_data)

    login_data = {"email": user_data["email"], "password": "wrong_password"}
    response = client.post("/login", json=login_data)

    assert response.status_code == 401
    error_data = response.json()
    assert error_data["errors"][0]["msg"] == "Invalid email or password"


def test_refresh_token_success(client: TestClient):
    """Test successful token refresh."""
    
    user_data = {
        "name": "Refresher",
        "email": "refresh@example.com",
        "password": "password123",
    }
    client.post("/signup", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_response = client.post("/login", json=login_data)
    old_tokens = login_response.json()

    # Allow a second to pass so that iat in the new access token is different
    time.sleep(1)

    refresh_response = client.post(
        "/refresh", json={"refresh_token": old_tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 200

    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    # The new tokens should be different from the old ones (token rotation)
    assert new_tokens["access_token"] != old_tokens["access_token"]
    assert new_tokens["refresh_token"] != old_tokens["refresh_token"]


def test_refresh_with_invalid_token(client: TestClient):
    """Test that token refresh fails with a bogus token."""
    
    response = client.post("/refresh", json={"refresh_token": "invalid.wrong.token"})
    assert response.status_code == 401
    error_data = response.json()
    assert error_data["errors"][0]["msg"] == "Invalid token"
