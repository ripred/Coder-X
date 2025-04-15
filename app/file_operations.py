"""
File operations for Claude Code Python Assistant
- Open, read, write, edit files
- Explain code in a file
- Run tests (pytest/unittest)
- Lint code (flake8/pylint)
- Track file changes/edits in session history
"""
import os
from typing import Optional

class FileOps:
    def __init__(self):
        pass

    def read_file(self, filepath: str) -> Optional[str]:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def write_file(self, filepath: str, content: str) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False

    def append_file(self, filepath: str, content: str) -> bool:
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False

    def file_exists(self, filepath: str) -> bool:
        return os.path.exists(filepath)

    def explain_code(self, filepath: str) -> Optional[str]:
        """
        Explain code in a file using an integrated model, if available. Fallback to summary if model unavailable.
        """
        content = self.read_file(filepath)
        if not content:
            return None
        # Try to use remote model API for explanation
        try:
            import requests
            endpoint = os.environ.get("CLAUDE_CODE_MODEL_API", "http://localhost:8000/remote-model/generate")
            resp = requests.post(endpoint, json={"prompt": f"Explain the following code in detail:\n{content[:4000]}"})
            if resp.status_code == 200:
                data = resp.json()
                return data.get("output", "[No explanation returned]")
        except Exception:
            pass
        # Fallback: return a simple summary
        return f"[EXPLAIN] {filepath}:\n{content[:200]}..."

    def run_tests(self, test_path: str) -> str:
        import subprocess
        try:
            result = subprocess.run(["pytest", test_path], capture_output=True, text=True)
            return result.stdout + '\n' + result.stderr
        except Exception as e:
            return str(e)

    def lint_code(self, filepath: str) -> str:
        import subprocess
        try:
            result = subprocess.run(["flake8", filepath], capture_output=True, text=True)
            return result.stdout + '\n' + result.stderr
        except Exception as e:
            return str(e)
