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

def test_update_config(monkeypatch, tmp_path):
    from app.config_schema import CoderXConfig
    import os
    config_path = tmp_path / "coderx_config.json"
    monkeypatch.setenv("CLAUDE_CODE_CONFIG", str(config_path))
    # Provide a full config schema for validation
    from app.config_schema import APIKeys
    orig = CoderXConfig(
        model="test_model",
        model_storage_path="/tmp/models",
        api_keys=APIKeys(openai="dummy", anthropic="dummy", ollama="dummy").model_dump(),
        mcp_server="http://localhost:1234",
        history_path="/tmp/history.json"
    )
    resp = client.post("/config", json=orig.model_dump(exclude_unset=False))
    assert resp.status_code == 200
    assert resp.json()["success"]
    # Confirm persisted
    loaded = load_config(str(config_path))
    assert loaded.model == "test_model"
