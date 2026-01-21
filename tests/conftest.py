"""Pytest fixtures for application-wide test setup."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # in-memory instance

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,  # Bind to our in-memory SQLite instance
)


@pytest.fixture(scope="function")
def db_session():
    """Fixture to create a fresh, isolated database session for each test."""

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture to create a TestClient with an overridden database dependency."""

    def override_get_db():
        """Dependency override to use the test database session."""
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def authenticated_client(client: TestClient):
    """Fixture to create a client that is pre-authenticated with a test user."""

    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testing_password",
    }
    client.post("/signup", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/login", json=login_data)
    token = response.json()["access_token"]

    client.headers = {"Authorization": f"Bearer {token}"}
    return client
