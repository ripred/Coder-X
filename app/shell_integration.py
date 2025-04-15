"""
Shell integration for Coder-X
- Run shell commands securely
- Capture and display output/errors
- Restrict dangerous commands (configurable)
"""
import subprocess
from typing import List, Optional

SAFE_COMMANDS = [
    'ls', 'cat', 'echo', 'pwd', 'whoami', 'date', 'head', 'tail', 'grep', 'find', 'df', 'du', 'ps', 'top', 'htop',
    # Add more safe commands as needed
]

class ShellIntegration:
    def __init__(self, allowed_commands: Optional[List[str]] = None):
        self.allowed_commands = allowed_commands or SAFE_COMMANDS

    def run_command(self, command: List[str], override: bool = False) -> dict:
        """
        Run a shell command. If override is True, allow any command (user has explicitly approved).
        Otherwise, only allow commands in allowed_commands.
        """
        if not override and command[0] not in self.allowed_commands:
            return {"error": f"Command '{command[0]}' is not allowed."}
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}
