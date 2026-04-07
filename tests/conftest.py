import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, todos_db


@pytest.fixture(autouse=True)
def clear_todos_db():
    """Clear the in-memory todos database before each test."""
    todos_db.clear()
    yield
    todos_db.clear()


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_todo_payload():
    """Return a valid todo creation payload."""
    return {
        "title": "Test Todo",
        "description": "A test todo item",
        "due_date": "2099-12-31",
        "priority": 1,
        "status": "New"
    }


@pytest.fixture
def created_todo(client, sample_todo_payload):
    """Create a todo and return the response JSON."""
    response = client.post("/todos", json=sample_todo_payload)
    assert response.status_code == 201
    return response.json()
