import pytest
from fastapi.testclient import TestClient
from webhook.main import app

client = TestClient(app)

def test_webhook_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_github_webhook_github_pr_event():
    payload = {
        "action": "closed",
        "repository": {
            "full_name": "cybage-devops/student-app"
        },
        "pull_request": {
            "number": 88,
            "head": {
                "ref": "main",
                "sha": "f1e2d3c4b5a6"
            }
        }
    }
    res = client.post("/github/webhook", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "SUCCESS"
    assert "PR #88" in body["message"]
    assert body["data"]["final_service_url"].startswith("https://")

def test_github_webhook_direct_trigger():
    payload = {
        "repo": "cybage-devops/student-app",
        "pr_id": 99,
        "branch": "main",
        "commit": "1a2b3c4d",
        "date": "2026-08-03",
        "time": "13:20:00"
    }
    res = client.post("/github/webhook", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "SUCCESS"
    assert "PR #99" in body["message"]
