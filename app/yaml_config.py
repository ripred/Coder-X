"""
YAML configuration management for Coder-X
"""
import os
import yaml
from typing import Optional

CONFIG_PATH = os.environ.get("CODER_X_YAML_CONFIG", os.path.expanduser("~/.coder_x_config.yaml"))

DEFAULT_CONFIG = {
    "model": None,
    "model_storage_path": os.path.expanduser("~/.coder_x_models"),
    "api_keys": {},
    "mcp_server": None,
    "history_path": os.path.expanduser("~/.coder_x_history.json"),
}

def load_yaml_config(path: Optional[str] = None):
    path = path or CONFIG_PATH
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f)
    else:
        return DEFAULT_CONFIG.copy()

def save_yaml_config(config: dict, path: Optional[str] = None):
    path = path or CONFIG_PATH
    with open(path, "w") as f:
        yaml.safe_dump(config, f)
