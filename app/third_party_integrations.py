"""
Third-party integrations for Coder-X
- Connect to external services (VCS, cloud, etc.)
- Expose via `/connect` command or API
"""
from typing import Optional

class ThirdPartyIntegration:
    def __init__(self):
        self.integrations = {}

    def connect(self, service: str, config: Optional[dict] = None) -> bool:
        # Simulate connecting to a third-party service, e.g., check for required API key
        if not config:
            config = {}
        # Simulate API key check for demonstration
        api_key = config.get("token")
        if service.lower() in ("github", "gitlab") and not api_key:
            return False
        self.integrations[service] = config
        self._save_integrations()
        return True

    def disconnect(self, service: str) -> bool:
        if service in self.integrations:
            del self.integrations[service]
            self._save_integrations()
            return True
        return False

    def list_integrations(self):
        return list(self.integrations.keys())

    def _save_integrations(self):
        import json, os
        path = os.path.expanduser("~/.coder_x_integrations.json")
        with open(path, "w") as f:
            json.dump(self.integrations, f, indent=2)

    def _load_integrations(self):
        import json, os
        path = os.path.expanduser("~/.coder_x_integrations.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.integrations = json.load(f)
        else:
            self.integrations = {}

    # Load integrations at init
    def __init__(self):
        self._load_integrations()
