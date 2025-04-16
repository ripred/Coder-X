from app import yaml_config
import os
import tempfile

def test_yaml_config_load_and_save():
    config = {
        "model": "test-model",
        "model_storage_path": "/tmp/models",
        "api_keys": {"svc": "xxx"},
        "mcp_server": "http://localhost:1234",
        "history_path": "/tmp/history.json",
    }
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tf:
        path = tf.name
    try:
        yaml_config.save_yaml_config(config, path)
        loaded = yaml_config.load_yaml_config(path)
        assert loaded == config
    finally:
        os.remove(path)

def test_yaml_config_missing_file():
    path = "/tmp/does_not_exist_coderx.yaml"
    loaded = yaml_config.load_yaml_config(path)
    assert isinstance(loaded, dict)
    assert loaded["model_storage_path"]

def test_yaml_config_malformed():
    import pytest
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tf:
        path = tf.name
    with open(path, "w") as f:
        f.write(": not valid yaml ::::\n")
    try:
        with pytest.raises(Exception):
            yaml_config.load_yaml_config(path)
    finally:
        os.remove(path)

def test_yaml_config_permission_error(monkeypatch):
    import pytest
    def fail_open(*a, **kw):
        raise PermissionError("denied")
    monkeypatch.setattr("builtins.open", fail_open)
    with pytest.raises(PermissionError):
        yaml_config.save_yaml_config({}, "/root/forbidden.yaml")
