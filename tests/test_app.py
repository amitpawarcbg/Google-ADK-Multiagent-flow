import pytest
from fastapi.testclient import TestClient
from app.main import app, db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    db.clear()
    yield
    db.clear()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "student-registration-app"

def test_register_student():
    payload = {
        "name": "Jane Doe",
        "email": "jane@cybage.com",
        "state": "Maharashtra",
        "course": "Multi-Agent Systems & GenAI"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@cybage.com"
    assert data["state"] == "Maharashtra"
    assert data["course"] == "Multi-Agent Systems & GenAI"

def test_list_and_get_students():
    # Register first
    reg = client.post("/register", json={"name": "Alice", "email": "alice@cybage.com", "state": "Washington", "course": "DevOps"})
    student_id = reg.json()["id"]

    # List
    list_res = client.get("/students")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Get by ID
    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Alice"
    assert get_res.json()["state"] == "Washington"

def test_delete_student():
    reg = client.post("/register", json={"name": "Bob", "email": "bob@cybage.com", "state": "Illinois", "course": "Cloud Native"})
    student_id = reg.json()["id"]

    del_res = client.delete(f"/students/{student_id}")
    assert del_res.status_code == 200

    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 404
