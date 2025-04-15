"""
User management for Coder-X Python Assistant
- Display current user info
- Support login/logout for remote APIs (if needed)
"""
import getpass
import os
from typing import Optional

_TOKENS = {}

class UserManager:
    def __init__(self):
        self.username = getpass.getuser()
        self.home = os.path.expanduser(f"~{self.username}")

    def get_current_user(self) -> dict:
        return {
            "username": self.username,
            "home": self.home
        }

    def login(self, service: str, token: Optional[str] = None) -> bool:
        global _TOKENS
        if service.lower() == 'coder-x':
            if not token:
                raise ValueError("Coder-X login requires an API token.")
            _TOKENS['coder-x'] = token
            return True
        elif service.lower() == 'ollama':
            if token:
                _TOKENS['ollama'] = token
            return True
        else:
            raise ValueError(f"Unknown or unsupported service: {service}")

    def logout(self, service: str) -> bool:
        global _TOKENS
        service = service.lower()
        if service in _TOKENS:
            del _TOKENS[service]
            return True
        return False
