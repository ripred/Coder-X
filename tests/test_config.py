import os
import tempfile
import json
from app import config

def test_config_load_and_save():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        original = {"model": "test-model", "model_storage_path": "/tmp/models", "api_keys": {"foo": "bar"}, "mcp_server": "http://localhost", "history_path": "/tmp/history.json"}
        config.save_config(original, path)
        loaded = config.load_config(path)
        assert loaded == original
    finally:
        os.remove(path)

def test_model_storage_path():
    conf = {"model_storage_path": "/tmp/models"}
    assert config.get_model_storage_path(conf) == "/tmp/models"
    assert config.get_model_storage_path({}) == config.DEFAULT_CONFIG["model_storage_path"]
