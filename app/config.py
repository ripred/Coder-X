"""
Configuration management for Coder-X
"""
import os
import json
from typing import Optional, Any
from app.config_schema import CoderXConfig
from pydantic import ValidationError

# Deprecated: for backward compatibility only. Use get_config_path() everywhere else.
CONFIG_PATH = os.environ.get("CLAUDE_CODE_CONFIG", os.path.expanduser("~/.coder_x_config.json"))
def get_config_path() -> str:
    return os.environ.get("CLAUDE_CODE_CONFIG", os.path.expanduser("~/.coder_x_config.json"))

def load_config(path: Optional[str] = None) -> CoderXConfig:
    """
    Loads config from file, merges with defaults, and validates.
    Raises ValueError if config is invalid or cannot be loaded.
    Logs file path and loaded/merged data for debugging.
    """
    import logging
    path = path or CONFIG_PATH
    from app.config_schema import CoderXConfig
    default = CoderXConfig().model_dump()
    logging.debug(f"[load_config] Loading config from: {path}")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                content = f.read().strip()
                logging.debug(f"[load_config] Raw file content: {content}")
                if not content:
                    logging.debug("[load_config] Empty config file, using defaults.")
                    return CoderXConfig()
                data = json.loads(content)
            merged = {**default, **data}
            if "api_keys" in data:
                merged_api_keys = {**default.get("api_keys", {}), **data["api_keys"]}
                # If api_keys is a dict, coerce to APIKeys object
                from app.config_schema import APIKeys
                if isinstance(merged_api_keys, dict):
                    merged["api_keys"] = APIKeys(**merged_api_keys)
                else:
                    merged["api_keys"] = merged_api_keys
            logging.debug(f"[load_config] Merged config dict: {merged}")
            config = CoderXConfig.model_validate(merged)
            logging.debug(f"[load_config] Loaded config: {config}")
            return config
        except Exception as e:
            logging.error(f"[load_config] Failed to load or validate config at {path}: {e}")
            raise ValueError(f"Failed to load or validate config at {path}: {e}")
    else:
        logging.debug(f"[load_config] Config file not found at {path}, using defaults.")
        return CoderXConfig()

def save_config(config: CoderXConfig, path: Optional[str] = None):
    """
    Saves a complete config (all fields, no missing keys) to file.
    """
    path = path or get_config_path()
    with open(path, "w") as f:
        json.dump(config.model_dump(exclude_unset=False), f, indent=2)

def set_config_key(config: CoderXConfig, dotted_key: str, value: Any) -> CoderXConfig:
    """Set a (possibly nested) config key. Raises ValueError if key is invalid."""
    import copy
    config_dict = copy.deepcopy(config.model_dump())
    keys = dotted_key.split('.')
    d = config_dict
    # Validate top-level key
    top_keys = set(CoderXConfig.model_fields.keys())
    if keys[0] not in top_keys:
        raise ValueError(f"Invalid config key: {keys[0]}")
    # Validate nested keys for api_keys
    if keys[0] == "api_keys" and len(keys) > 1:
        from app.config_schema import APIKeys
        api_keys_fields = set(APIKeys.model_fields.keys())
        if keys[1] not in api_keys_fields:
            raise ValueError(f"Invalid api_keys subkey: {keys[1]}")
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
