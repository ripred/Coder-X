"""
MCP (Model Context Protocol) integration for Coder-X Python Assistant
- Integrate with MCP servers for context/memory
"""
from typing import Optional
import requests
from .config import load_config

class MCPClient:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.server_url = self.config.get("mcp_server")

    def set_server_url(self, url: str):
        self.server_url = url
        self.config["mcp_server"] = url
        from .config import save_config
        save_config(self.config)

    def get_context(self, context_id: str) -> Optional[dict]:
        if not self.server_url:
            return None
        try:
            resp = requests.get(f"{self.server_url}/context/{context_id}")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def save_context(self, context_id: str, data: dict) -> bool:
        if not self.server_url:
            return False
        try:
            resp = requests.post(f"{self.server_url}/context/{context_id}", json=data)
            return resp.status_code == 200
        except Exception:
            return False
