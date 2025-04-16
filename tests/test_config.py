import os
import tempfile
import json
from app import config

def test_config_load_and_save(monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    monkeypatch.setenv("CLAUDE_CODE_CONFIG", path)
    try:
        from app.config_schema import CoderXConfig
        original = CoderXConfig.model_validate({"model": "test-model", "model_storage_path": "/tmp/models", "api_keys": {"foo": "bar"}, "mcp_server": "http://localhost", "history_path": "/tmp/history.json"})
        config.save_config(original, path)
        loaded = config.load_config(path)
        assert loaded.model == original.model
        assert loaded.model_storage_path == original.model_storage_path
        assert loaded.api_keys.model_dump() == original.api_keys.model_dump()
        assert loaded.mcp_server == original.mcp_server
        assert loaded.history_path == original.history_path
    finally:
        os.remove(path)

def test_model_storage_path():
    from app.config_schema import CoderXConfig
    conf = CoderXConfig.model_validate({"model_storage_path": "/tmp/models"})
    assert config.get_model_storage_path(conf) == "/tmp/models"
    default_conf = CoderXConfig()
    assert config.get_model_storage_path(default_conf) == default_conf.model_storage_path
