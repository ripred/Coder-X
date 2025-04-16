"""
Interactive shell for Coder-X using prompt_toolkit.
Supports command history, tab completion, and slash commands.
"""
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
import os
import sys
import json
from app.model_management import ModelManager
from app.file_operations import read_file, write_file, append_file
from app.config import load_config, save_config, set_config_key
from app.session_history import SessionHistory
from app.user_management import UserManager

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
            mm = ModelManager()
            local = mm.list_local_models()
            ollama = mm.list_ollama_models()
            print(json.dumps({"local": local, "ollama": ollama}, indent=2))
        elif cmd == "/model-set" and len(args) > 1:
            mm = ModelManager()
            mm.set_active_model(args[1])
            print(f"Active model set to: {args[1]}")
        elif cmd == "/model-storage-path":
            mm = ModelManager()
            if len(args) > 1:
                path = os.path.expanduser(args[1])
                try:
                    mm.set_model_storage_path(path)
                    print(f"Model storage path set to: {path}")
                except Exception as e:
                    print(f"[ERROR] {e}")
            else:
                print(f"Current model storage path: {mm.storage_path}")
        elif cmd == "/config-show":
            conf = load_config()
            print(json.dumps(conf.model_dump(), indent=2))
        elif cmd == "/config-set" and len(args) > 2:
            key, value = args[1], args[2]
            conf = load_config()
            conf = set_config_key(conf, key, value)
            save_config(conf)
            print(f"Set {key} = {value}")
        elif cmd == "/file-read" and len(args) > 1:
            content = read_file(args[1])
            if content is not None:
                print(content)
            else:
                print(f"[ERROR] Could not read file: {args[1]}")
        elif cmd == "/file-write" and len(args) > 2:
            ok = write_file(args[1], ' '.join(args[2:]))
            if ok:
                print("[OK] File written.")
            else:
                print(f"[ERROR] Could not write file: {args[1]}")
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
