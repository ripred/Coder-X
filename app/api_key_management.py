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
    config['api_keys'][service] = encrypted
    save_config(config)

def get_api_key(service: str) -> Optional[str]:
    config = load_config()
    enc = config['api_keys'].get(service)
    if enc:
        try:
            return fernet.decrypt(enc.encode()).decode()
        except Exception:
            return None
    return None

def remove_api_key(service: str):
    config = load_config()
    if service in config['api_keys']:
        del config['api_keys'][service]
        save_config(config)
