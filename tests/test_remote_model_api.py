from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_with_remote_model():
    resp = client.post("/remote-model/generate", json={"prompt": "Hello, world!", "model_name": "dummy-free-model"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["model"] == "dummy-free-model"
    assert "Hello, world!" in data["output"]
