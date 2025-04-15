"""
CLI/Interactive shell for Coder-X
"""
import sys
import requests
import readline
import json

import os
IS_TEST_MODE = os.environ.get("CODER_X_TEST_MODE", "0") == "1"

API_BASE = "http://localhost:8000"

HELP = """
Coder-X CLI
Commands:
  model list                 List available models
  model set <name>           Set active model
  config show                Show current config
  config set <key> <value>   Set config value (supports nested keys via dot notation)
  config set <key>           Set config value interactively
  config unset <key>         Remove config key (supports nested keys)
  config setup                Guided config setup for all key options
  file read <path>           Read file contents
  file write <path> <text>   Write text to file
  file append <path> <text>  Append text to file
  shell <cmd>                Run shell command (safe commands only)
  history show               Show session history
  user info                  Show current user info
  feedback <text>            Submit feedback
  integration list           List integrations
  integration connect <svc>  Connect integration
  integration disconnect <svc> Disconnect integration
  help                       Show this help
  exit                       Exit CLI
"""

def trust_prompt():
    # No graphical prompt; just a plain text trust confirmation
    if IS_TEST_MODE:
        return
    folder = os.getcwd()
    print(f"Do you trust the files in this folder?\n{folder}\nType 'yes' to proceed, anything else to exit.")
    resp = input("> ").strip().lower()
    if resp != "yes":
        print("Exiting for safety.")
        sys.exit(0)

    folder = os.getcwd()
    panel = Panel(
        Align.center(
            f"[bold yellow]Do you trust the files in this folder?[/bold yellow]\n[white]{folder}[/white]\n\n[bold green]> Yes, proceed[/bold green]\n[bold]  No, exit[/bold]",
            vertical="middle"
        ),
        title="[cyan]Trust Prompt",
        subtitle="Enter to confirm · Esc to exit",
        border_style="bright_magenta",
        padding=(1, 4),
        width=80
    )
    console.print(panel)
    try:
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == '\r' or ch == '\n':
                console.print()
                break
            elif ord(ch) == 27:  # ESC
                console.print("[red]Exiting for safety.[/red]")
                sys.exit(0)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def run_command_line(line):
    args = line.split()
    output = ""
    if not args:
        return None
    if args[0] == "exit":
        return None
    elif args[0] == "help":
        return HELP
    elif args[0] == "model" and len(args) > 1:
        if args[1] == "list":
            r = requests.get(f"{API_BASE}/models")
            return json.dumps(r.json(), indent=2)
        elif args[1] == "set" and len(args) > 2:
            r = requests.post(f"{API_BASE}/models/active", json={"model": args[2]})
            return str(r.json())
    elif args[0] == "config" and len(args) > 1:
        import sys
        def safe_input(prompt):
            if sys.stdin.isatty():
                return input(prompt)
            else:
                # Read a single line from stdin (for test harness)
                print(prompt, end="", flush=True)
                return sys.stdin.readline().rstrip("\n")
        if args[1] == "setup":
            try:
                r = requests.get(f"{API_BASE}/config")
                conf = r.json()
            except Exception as e:
                return f"[ERROR] Could not connect to backend: {e}"
            model = safe_input(f"Model (current: {conf.get('model', None)}): ").strip()
            if model:
                conf['model'] = model
            storage_path = safe_input(f"Model storage path (current: {conf.get('model_storage_path', None)}): ").strip()
            if storage_path:
                import os
                if not os.path.exists(storage_path):
                    try:
                        os.makedirs(storage_path, exist_ok=True)
                        setup_msg = f"Created directory: {storage_path}\n"
                    except Exception as e:
                        setup_msg = f"[ERROR] Could not create directory: {e}\n"
                else:
                    setup_msg = ""
                conf['model_storage_path'] = storage_path
            else:
                setup_msg = ""
            api_keys_msg = "\nAPI Keys setup (leave blank to skip)\n"
            if 'api_keys' not in conf:
                conf['api_keys'] = {}
            for provider in ['openai', 'anthropic', 'ollama']:
                key = safe_input(f"API key for {provider} (current: {conf['api_keys'].get(provider, None)}): ").strip()
                if key:
                    conf['api_keys'][provider] = key
            mcp_server = safe_input(f"MCP server endpoint (current: {conf.get('mcp_server', None)}): ").strip()
            if mcp_server:
                conf['mcp_server'] = mcp_server
            try:
                r = requests.post(f"{API_BASE}/config", json=conf)
                result = "Config saved\n"
                result += json.dumps(r.json() if r.text else {}, indent=2) + "\n"
                r2 = requests.get(f"{API_BASE}/config")
                result += json.dumps(r2.json() if r2.text else {}, indent=2)
                return setup_msg + api_keys_msg + result
            except Exception as e:
                return f"[ERROR] Could not connect to backend: {e}"
        if args[1] == "show":
            try:
                r = requests.get(f"{API_BASE}/config")
                return json.dumps(r.json() if r.text else {}, indent=2)
            except Exception as e:
                return f"[ERROR] Could not connect to backend: {e}"
        elif args[1] == "set" and len(args) > 2:
            try:
                r = requests.get(f"{API_BASE}/config")
                conf = r.json()
            except Exception as e:
                return f"[ERROR] Could not connect to backend: {e}"
            key = args[2]
            if len(args) > 3:
                value = args[3]
            else:
                value = safe_input(f"Enter value for {key}: ")
            def convert(val):
                if isinstance(val, str) and val.lower() in ("true", "false"): return val.lower() == "true"
                try: return int(val)
                except: pass
                try: return float(val)
                except: pass
                return val
            value = convert(value)
            def set_nested(d, dotted_key, val):
                keys = dotted_key.split('.')
                for k in keys[:-1]:
                    if k not in d or not isinstance(d[k], dict):
                        d[k] = {}
                    d = d[k]
                d[keys[-1]] = val
            set_nested(conf, key, value)
            try:
                r = requests.post(f"{API_BASE}/config", json=conf)
                result = json.dumps(r.json() if r.text else {}, indent=2) + "\n"
                r2 = requests.get(f"{API_BASE}/config")
                result += json.dumps(r2.json() if r2.text else {}, indent=2)
                return result
            except Exception as e:
                return f"[ERROR] Could not connect to backend: {e}"
        elif args[1] == "unset" and len(args) > 2:
            try:
                r = requests.get(f"{API_BASE}/config")
                conf = r.json()
            except Exception as e:
                return f"[ERROR] Could not connect to backend: {e}"
            key = args[2]
            def unset_nested(d, dotted_key):
                keys = dotted_key.split('.')
                for k in keys[:-1]:
                    if k not in d or not isinstance(d[k], dict):
                        return False
                    d = d[k]
                return d.pop(keys[-1], None) is not None
            unset_nested(conf, key)
            try:
                r = requests.post(f"{API_BASE}/config", json=conf)
                return json.dumps(r.json() if r.text else {}, indent=2)
            except Exception as e:
                return f"[ERROR] Could not connect to backend: {e}"
    # Fallback to original main loop for other commands or unknowns
    return "Unknown command. Type 'help' for available commands."

def main():
    import sys
    # If any arguments are passed (other than script name), treat as a command
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        output = run_command_line(command)
        if output:
            print(output, flush=True)
        return
    # Single-command mode for test harness or automation
    single_command = os.environ.get("CODER_X_CLI_COMMAND")
    if IS_TEST_MODE and single_command:
        output = run_command_line(single_command)
        if output:
            print(output, flush=True)
        return
    # If stdin is not a TTY (e.g., piped input), read one line and execute as command
    if not sys.stdin.isatty():
        line = sys.stdin.readline().strip()
        if line:
            output = run_command_line(line)
            if output:
                print(output, flush=True)
        return
    trust_prompt()
    history = []
    while True:
        try:
            line = input("coder-x> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        output = run_command_line(line)
        if output:
            print(output, flush=True)

if __name__ == "__main__":
    main()
