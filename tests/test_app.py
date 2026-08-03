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
        "roll_no": "RN-2026-001",
        "name": "Jane Doe",
        "email": "jane@cybage.com",
        "city": "Pune",
        "course": "Multi-Agent Systems & GenAI"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["roll_no"] == "RN-2026-001"
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@cybage.com"
    assert data["city"] == "Pune"
    assert data["course"] == "Multi-Agent Systems & GenAI"

def test_list_and_get_students():
    # Register first
    reg = client.post("/register", json={"roll_no": "RN-101", "name": "Alice", "email": "alice@cybage.com", "city": "Seattle", "course": "DevOps"})
    student_id = reg.json()["id"]

    # List
    list_res = client.get("/students")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Get by ID
    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Alice"
    assert get_res.json()["roll_no"] == "RN-101"
    assert get_res.json()["city"] == "Seattle"

def test_delete_student():
    reg = client.post("/register", json={"roll_no": "RN-102", "name": "Bob", "email": "bob@cybage.com", "city": "Chicago", "course": "Cloud Native"})
    student_id = reg.json()["id"]

    del_res = client.delete(f"/students/{student_id}")
    assert del_res.status_code == 200

    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 404
