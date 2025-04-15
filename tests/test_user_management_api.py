from fastapi.testclient import TestClient
from app.main import app
from app.user_management import UserManager
from app.user_management_api import get_user_manager

# Create a single UserManager instance for all test requests
_test_user_manager = UserManager()
app.dependency_overrides[get_user_manager] = lambda: _test_user_manager

client = TestClient(app)

def test_get_current_user():
    resp = client.get("/user/me")
    assert resp.status_code == 200
    data = resp.json()
    assert "username" in data
    assert "home" in data

def test_login_logout():
    resp = client.post("/user/login", json={"service": "ollama", "token": "abc123"})
    assert resp.status_code == 200
    assert resp.json()["success"]
    resp = client.post("/user/logout", json={"service": "ollama"})
    if resp.status_code != 200:
        print(f"Logout failed: status={resp.status_code}, response={resp.json()}")
    assert resp.status_code == 200
    assert resp.json()["success"]
