"""
Configuration management for Coder-X
"""
import os
import json
from typing import Optional, Any
from app.config_schema import CoderXConfig
from pydantic import ValidationError

CONFIG_PATH = os.environ.get("CLAUDE_CODE_CONFIG", os.path.expanduser("~/.coder_x_config.json"))

def load_config(path: Optional[str] = None) -> CoderXConfig:
    path = path or CONFIG_PATH
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                content = f.read().strip()
                if not content:
                    return CoderXConfig()
                data = json.loads(content)
            return CoderXConfig.model_validate(data)
        except Exception:
            # fallback to defaults if corrupted or empty/invalid
            return CoderXConfig()
    else:
        return CoderXConfig()

def save_config(config: CoderXConfig, path: Optional[str] = None):
    path = path or CONFIG_PATH
    with open(path, "w") as f:
        json.dump(config.model_dump(), f, indent=2)

def set_config_key(config: CoderXConfig, dotted_key: str, value: Any) -> CoderXConfig:
    """Set a (possibly nested) config key."""
    import copy
    config_dict = copy.deepcopy(config.model_dump())
    keys = dotted_key.split('.')
    d = config_dict
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            d[k] = {}
        d = d[k]
    d[keys[-1]] = value
    return CoderXConfig.model_validate(config_dict)

def unset_config_key(config: CoderXConfig, dotted_key: str) -> CoderXConfig:
    import copy
    config_dict = copy.deepcopy(config.model_dump())
    keys = dotted_key.split('.')
    d = config_dict
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            return config
        d = d[k]
    d.pop(keys[-1], None)
    return CoderXConfig.model_validate(config_dict)

def get_model_storage_path(config: CoderXConfig):
    return config.model_storage_path
