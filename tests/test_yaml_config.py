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
