from fastapi.testclient import TestClient
from app.main import app
from app.config import load_config, save_config

client = TestClient(app)

def test_get_config():
    resp = client.get("/config")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "model_storage_path" in data

def test_update_config():
    config = load_config()
    config["model"] = "test_model"
    resp = client.post("/config", json=config)
    assert resp.status_code == 200
    assert resp.json()["success"]
    # Confirm persisted
    assert load_config()["model"] == "test_model"
