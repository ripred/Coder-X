"""
API Key management for Claude Code Python Assistant
- Securely prompt for/store API keys
- Encrypt API keys at rest (simple XOR for demo, replace with real encryption in prod)
- Retrieve and use API keys for model requests
- Allow updating/removing API keys
"""
import os
import json
from typing import Optional
from .config import load_config, save_config
from .config_schema import CoderXConfig
from cryptography.fernet import Fernet

FERNET_KEY_FILE = os.path.expanduser("~/.coder_x_key")

# Generate or load Fernet key for encryption
if not os.path.exists(FERNET_KEY_FILE):
    key = Fernet.generate_key()
    with open(FERNET_KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(FERNET_KEY_FILE, "rb") as f:
        key = f.read()
fernet = Fernet(key)

def set_api_key(service: str, api_key: str):
    config = load_config()
    encrypted = fernet.encrypt(api_key.encode()).decode()
    if hasattr(config, "api_keys") and hasattr(config.api_keys, service):
        setattr(config.api_keys, service, encrypted)
    else:
        # fallback for dynamic keys
        d = config.model_dump()
        if "api_keys" not in d:
            d["api_keys"] = {}
        d["api_keys"][service] = encrypted
        config = CoderXConfig.model_validate(d)
    save_config(config)

def get_api_key(service: str) -> Optional[str]:
    config = load_config()
    enc = getattr(config.api_keys, service, None)
    if enc:
        try:
            return fernet.decrypt(enc.encode()).decode()
        except Exception:
            return None
    return None

def remove_api_key(service: str):
    config = load_config()
    if hasattr(config.api_keys, service):
        setattr(config.api_keys, service, None)
        save_config(config)
    else:
        d = config.model_dump()
        if "api_keys" in d and service in d["api_keys"]:
            del d["api_keys"][service]
            config = CoderXConfig.model_validate(d)
            save_config(config)
