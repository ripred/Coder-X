from fastapi.testclient import TestClient
from app.main import app
import tempfile
import os

client = TestClient(app)

def test_file_read_write_append_exists():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        # Write
        resp = client.post("/file/write", json={"filepath": path, "content": "abc"})
        assert resp.status_code == 200
        # Exists
        resp = client.get(f"/file/exists?filepath={path}")
        assert resp.status_code == 200
        assert resp.json()["exists"]
        # Read
        resp = client.get(f"/file/read?filepath={path}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "abc"
        # Append
        resp = client.post("/file/append", json={"filepath": path, "content": "def"})
        assert resp.status_code == 200
        resp = client.get(f"/file/read?filepath={path}")
        assert resp.json()["content"] == "abcdef"
    finally:
        os.remove(path)

def test_file_explain_not_found():
    resp = client.get("/file/explain?filepath=/tmp/does_not_exist.txt")
    assert resp.status_code == 404
