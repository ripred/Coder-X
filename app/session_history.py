"""
Session/history management for Claude Code Python Assistant
- Store conversation/command history
- Allow user to view, clear, export history
"""
import os
import json
from typing import List, Optional
from .config import load_config, save_config

class SessionHistory:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.history_path = getattr(self.config, "history_path", os.environ.get("CODER_X_HISTORY") or os.path.expanduser("~/.coder_x_history.json"))
        if os.path.isdir(self.history_path):
            raise IsADirectoryError(f"History path {self.history_path} is a directory.")
        if not os.path.exists(self.history_path):
            with open(self.history_path, "w") as f:
                json.dump([], f)

    def append(self, entry: dict):
        if os.path.isdir(self.history_path):
            raise IsADirectoryError(f"History path {self.history_path} is a directory.")
        history = self.load()
        history.append(entry)
        with open(self.history_path, "w") as f:
            json.dump(history, f, indent=2)

    def load(self) -> List[dict]:
        if os.path.isdir(self.history_path):
            raise IsADirectoryError(f"History path {self.history_path} is a directory.")
        with open(self.history_path, "r") as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)

    def clear(self):
        if os.path.isdir(self.history_path):
            raise IsADirectoryError(f"History path {self.history_path} is a directory.")
        with open(self.history_path, "w") as f:
            json.dump([], f)

    def export(self, export_path: str) -> bool:
        try:
            if os.path.isdir(self.history_path):
                raise IsADirectoryError(f"History path {self.history_path} is a directory.")
            with open(self.history_path, "r") as src, open(export_path, "w") as dst:
                dst.write(src.read())
            return True
        except Exception:
            return False
