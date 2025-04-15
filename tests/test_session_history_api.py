from fastapi.testclient import TestClient
from app.main import app
import tempfile
import os

client = TestClient(app)

def test_history_append_and_get():
    # Clear first
    client.post("/history/clear")
    # Append
    resp = client.post("/history/append", json={"entry": {"cmd": "foo"}})
    assert resp.status_code == 200
    # Get
    resp = client.get("/history")
    assert resp.status_code == 200
    hist = resp.json()["history"]
    assert any(e["cmd"] == "foo" for e in hist)

def test_history_export():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        export_path = tf.name
    try:
        resp = client.post("/history/export", params={"export_path": export_path})
        assert resp.status_code == 200
        assert resp.json()["success"]
        with open(export_path) as f:
            data = f.read()
        assert "cmd" in data
    finally:
        os.remove(export_path)
