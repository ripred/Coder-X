from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_connect_list_disconnect():
    # Connect
    resp = client.post("/integration/connect", json={"service": "github", "config": {"token": "abc"}})
    assert resp.status_code == 200
    assert resp.json()["success"]
    # List
    resp = client.get("/integration/list")
    assert resp.status_code == 200
    assert "github" in resp.json()["integrations"]
    # Disconnect
    resp = client.post("/integration/disconnect", json={"service": "github"})
    assert resp.status_code == 200
    assert resp.json()["success"]
    # List again
    resp = client.get("/integration/list")
    assert resp.status_code == 200
    assert "github" not in resp.json()["integrations"]
