"""
Interactive shell for Coder-X using prompt_toolkit.
Supports command history, tab completion, and slash commands.
"""
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
import os
import sys
import requests
import json

API_BASE = "http://localhost:8000"
HISTORY_FILE = os.path.expanduser("~/.coder_x_shell_history")

COMMANDS = [
    "/model-storage-path", "/model-list", "/model-set", "/config-show", "/config-set", "/file-read", "/file-write", "/shell", "/exit", "/help"
]

completer = WordCompleter(COMMANDS, ignore_case=True)

class InteractiveShell:
    def __init__(self):
        self.session = PromptSession(history=FileHistory(HISTORY_FILE), completer=completer)

    def run(self):
        print("Coder-X Interactive Shell (type /help for commands, /exit to quit)")
        while True:
            try:
                line = self.session.prompt("coder-x> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            if line.startswith("/"):
                self.handle_slash_command(line)
            else:
                print("[INFO] Use slash commands (e.g. /model-list, /file-read <path>)")

    def handle_slash_command(self, line):
        args = line.split()
        cmd = args[0].lower()
        if cmd == "/exit":
            print("Exiting shell.")
            sys.exit(0)
        elif cmd == "/help":
            print("Available commands:")
            for c in COMMANDS:
                print(f"  {c}")
        elif cmd == "/model-list":
            r = requests.get(f"{API_BASE}/models")
            print(json.dumps(r.json(), indent=2))
        elif cmd == "/model-set" and len(args) > 1:
            r = requests.post(f"{API_BASE}/models/active", json={"model": args[1]})
            print(r.json())
        elif cmd == "/model-storage-path":
            if len(args) > 1:
                path = os.path.expanduser(args[1])
                r = requests.post(f"{API_BASE}/models/storage-path", params={"path": path})
                print(r.text)
            else:
                r = requests.get(f"{API_BASE}/models/storage-path")
                print(r.text)
        elif cmd == "/config-show":
            r = requests.get(f"{API_BASE}/config")
            print(json.dumps(r.json(), indent=2))
        elif cmd == "/config-set" and len(args) > 2:
            key, value = args[1], args[2]
            r = requests.get(f"{API_BASE}/config")
            conf = r.json()
            conf[key] = value
            print(f"Set {key} = {value}")
        elif cmd == "/file-read" and len(args) > 1:
            r = requests.get(f"{API_BASE}/file/read", params={"path": args[1]})
            print(r.text)
        elif cmd == "/file-write" and len(args) > 2:
            r = requests.post(f"{API_BASE}/file/write", json={"path": args[1], "text": ' '.join(args[2:])})
            print(r.text)
        elif cmd == "/shell" and len(args) > 1:
            import subprocess
            command_str = ' '.join(args[1:])
            dangerous = any(x in command_str for x in ["rm", "shutdown", "reboot"])
            if dangerous:
                approve = input("[WARNING] Dangerous command detected. Run? (yes/no): ").strip().lower()
                if approve != "yes":
                    print("Command aborted.")
                    return
            result = subprocess.run(command_str, shell=True, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        else:
            print(f"Unknown or incomplete command: {line}")

if __name__ == "__main__":
    InteractiveShell().run()
