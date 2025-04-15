from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_run_shell_command_success():
    resp = client.post("/shell/run", json={"command": ["echo", "hello"]})
    assert resp.status_code == 200
    data = resp.json()
    assert data["stdout"].strip() == "hello"
    assert data["returncode"] == 0

def test_run_shell_command_disallowed():
    resp = client.post("/shell/run", json={"command": ["rm", "-rf", "/"]})
    assert resp.status_code == 400
    assert "not allowed" in resp.json()["detail"]

def test_run_shell_command_override():
    # Should be allowed with override=True (simulate, do not actually run dangerous command)
    # Use a harmless command for safety, but test override logic
    resp = client.post("/shell/run", json={"command": ["echo", "override works"], "override": True})
    assert resp.status_code == 200
    data = resp.json()
    assert "override works" in data["stdout"]
