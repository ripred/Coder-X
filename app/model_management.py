"""
Model management for Claude Code Python Assistant
- List, select, load, and switch models (local/remote)
- Support model storage location selection
- Integrate with Ollama and Anthropic API
"""
import os
from typing import List, Optional
import subprocess
from .config import get_model_storage_path, load_config, set_config_key

OLLAMA_MODELS_CMD = ["ollama", "list"]

class ModelManager:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.storage_path = get_model_storage_path(self.config)

    def list_local_models(self) -> List[str]:
        """List all models in the configured storage path (Ollama or other)."""
        models = []
        if os.path.exists(self.storage_path):
            for entry in os.listdir(self.storage_path):
                if os.path.isdir(os.path.join(self.storage_path, entry)) or entry.endswith(('.bin', '.gguf', '.ggml', '.pth')):
                    models.append(entry)
        return models

    def list_ollama_models(self) -> List[str]:
        """List models available via Ollama CLI (if installed)."""
        try:
            result = subprocess.run(OLLAMA_MODELS_CMD, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            return [line.split()[0] for line in lines[1:] if line]
        except Exception:
            return []

    def set_model_storage_path(self, path: str):
        """Update the config with a new storage path. Validates existence, writability, and free space."""
        import shutil
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                raise RuntimeError(f"Model storage path unavailable or could not be created: {e}")
        # Check if writable
        if not os.access(path, os.W_OK):
            raise PermissionError(f"Model storage path '{path}' is not writable. Please choose a different location or adjust permissions.")
        # Check for sufficient free space (require at least 1GB)
        try:
            total, used, free = shutil.disk_usage(path)
            if free < 1 * 1024 * 1024 * 1024:  # 1GB
                raise OSError(f"Insufficient disk space at '{path}'. At least 1GB free is required.")
        except Exception as e:
            raise OSError(f"Could not determine disk usage for '{path}': {e}")
        self.config = set_config_key(self.config, "model_storage_path", path)
        from .config import save_config
        save_config(self.config)
        self.storage_path = path

    def get_active_model(self) -> Optional[str]:
        return getattr(self.config, "model", None)

    def set_active_model(self, model_name: str):
        self.config = set_config_key(self.config, "model", model_name)
        from .config import save_config
        save_config(self.config)

    def load_model_ollama(self, model_name: str) -> bool:
        """Pull (download) a model from Ollama registry and make it available locally."""
        try:
            result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True, check=True)
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] Failed to load model '{model_name}' via Ollama: {e}")
            return False

    def unload_model_ollama(self, model_name: str) -> bool:
        """Remove a model from Ollama's local storage."""
        try:
            result = subprocess.run(["ollama", "rm", model_name], capture_output=True, text=True, check=True)
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] Failed to unload model '{model_name}' via Ollama: {e}")
            return False

    def list_ollama_volumes(self) -> list:
        """List candidate parent directories for Ollama model storage."""
        # Ollama stores models in ~/.ollama/models by default, but user may want to use a different volume
        default_path = os.path.expanduser("~/.ollama/models")
        candidates = [default_path]
        # Add any user-configured path
        if self.storage_path not in candidates:
            candidates.append(self.storage_path)
        # Optionally scan for mounted volumes (macOS/Linux)
        mounts = ["/Volumes", "/mnt", "/media"]
        for m in mounts:
            if os.path.exists(m):
                for entry in os.listdir(m):
                    p = os.path.join(m, entry)
                    if os.path.isdir(p):
                        candidates.append(p)
        return candidates

    def set_ollama_volume(self, path: str) -> bool:
        """Set the volume (directory) for Ollama model storage and update config."""
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            # Optionally, symlink ~/.ollama/models to the new location
            default_path = os.path.expanduser("~/.ollama/models")
            if os.path.islink(default_path) or os.path.exists(default_path):
                try:
                    if os.path.islink(default_path):
                        os.unlink(default_path)
                    else:
                        import shutil
                        shutil.move(default_path, path)
                except Exception as e:
                    print(f"[WARN] Could not move/symlink Ollama models: {e}")
            try:
                os.symlink(path, default_path)
            except Exception as e:
                print(f"[WARN] Could not create symlink for Ollama models: {e}")
            self.set_model_storage_path(path)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to set Ollama volume: {e}")
            return False
