"""
CLI/Interactive shell for Coder-X
"""
import sys

import readline
import json

import os
IS_TEST_MODE = os.environ.get("CODER_X_TEST_MODE", "0") == "1"


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
    if os.environ.get("CODER_X_TEST_MODE", "0") == "1":
        return  # In test mode, do nothing and never prompt
    folder = os.getcwd()
    print(f"Do you trust the files in this folder?\n{folder}\nType 'yes' to proceed, anything else to exit.")
    resp = input("> ").strip().lower()
    if resp != "yes":
        print("Exiting for safety.")
        sys.exit(0)
    # Optionally: graphical/panel prompt for interactive mode (if ever used)

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
        from app.model_management import ModelManager
        mm = ModelManager()
        if args[1] == "list":
            local_models = mm.list_local_models()
            ollama_models = mm.list_ollama_models()
            return json.dumps({"local": local_models, "ollama": ollama_models}, indent=2)
        elif args[1] == "set" and len(args) > 2:
            mm.set_active_model(args[2])
            return f"Active model set to {args[2]}"
    elif args[0] == "config" and len(args) > 1:
        import sys
        from app.config import load_config, save_config, get_config_path
        from app.config_schema import CoderXConfig
        def safe_input(prompt):
            if sys.stdin.isatty():
                return input(prompt)
            else:
                # Read a single line from stdin (for test harness)
                print(prompt, end="", flush=True)
                return sys.stdin.readline().rstrip("\n")
        config_path = get_config_path()
        if args[1] == "setup":
            try:
                conf = load_config(config_path)
            except Exception as e:
                return f"[ERROR] Could not load config: {e}"
            model = safe_input(f"Model (current: {conf.model}): ").strip()
            if model:
                conf.model = model
            storage_path = safe_input(f"Model storage path (current: {conf.model_storage_path}): ").strip()
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
                conf.model_storage_path = storage_path
            else:
                setup_msg = ""
            api_keys_msg = "\nAPI Keys setup (leave blank to skip)\n"
            if not conf.api_keys:
                conf.api_keys = {}
            for provider in ['openai', 'anthropic', 'ollama']:
                key = safe_input(f"API key for {provider} (current: {getattr(conf.api_keys, provider, None)}): ").strip()
                if key:
                    conf.api_keys[provider] = key
            mcp_server = safe_input(f"MCP server endpoint (current: {conf.mcp_server}): ").strip()
            if mcp_server:
                conf.mcp_server = mcp_server
            try:
                save_config(conf, config_path)
                result = "Config saved\n"
                result += json.dumps(conf.model_dump(), indent=2) + "\n"
                return setup_msg + api_keys_msg + result
            except Exception as e:
                return f"[ERROR] Could not save config: {e}"
        if args[1] == "show":
            try:
                conf = load_config(config_path)
                return json.dumps(conf.model_dump(), indent=2)
            except Exception as e:
                return f"[ERROR] Could not load config: {e}"
        elif args[1] == "set" and len(args) > 2:
            try:
                conf = load_config(config_path)
            except Exception as e:
                return f"[ERROR] Could not load config: {e}"
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
            def set_nested(obj, dotted_key, val):
                keys = dotted_key.split('.')
                d = obj.model_dump()
                for k in keys[:-1]:
                    if k not in d or not isinstance(d[k], dict):
                        d[k] = {}
                    d = d[k]
                d[keys[-1]] = val
                # Re-validate as CoderXConfig
                return CoderXConfig.model_validate(obj.model_dump(exclude_unset=False))
            conf = set_nested(conf, key, value)
            try:
                save_config(conf, config_path)
                return json.dumps(conf.model_dump(), indent=2)
            except Exception as e:
                return f"[ERROR] Could not save config: {e}"
        elif args[1] == "unset" and len(args) > 2:
            try:
                conf = load_config(config_path)
            except Exception as e:
                return f"[ERROR] Could not load config: {e}"
            key = args[2]
            def unset_nested(obj, dotted_key):
                keys = dotted_key.split('.')
                d = obj.model_dump()
                for k in keys[:-1]:
                    if k not in d or not isinstance(d[k], dict):
                        return False
                    d = d[k]
                d.pop(keys[-1], None)
                return CoderXConfig.model_validate(obj.model_dump(exclude_unset=False))
            conf = unset_nested(conf, key)
            try:
                save_config(conf, config_path)
                return json.dumps(conf.model_dump(), indent=2)
            except Exception as e:
                return f"[ERROR] Could not save config: {e}"
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
    history = []
    while True:
        try:
            line = input("coder-x> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.lower() == "exit":
            print("Exiting Coder-X CLI.")
            break
        output = run_command_line(line)
        if output:
            print(output, flush=True)

if __name__ == "__main__":
    main()
