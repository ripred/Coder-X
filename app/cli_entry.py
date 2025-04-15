"""
CLI entrypoint for Coder-X using Typer
"""
import typer
from app import cli
from app.config_cli import config_app

app = typer.Typer(help="Coder-X: Python Agentic Coding Assistant")
app.add_typer(config_app, name="config")

@app.command()
def model(action: str = typer.Argument(..., help="Action: list, set, storage-path, load, unload, volumes, set-volume"), name: str = typer.Argument(None, help="Model name or path")):
    """List, set, load/unload models, or manage storage/volume."""
    import requests, json, os, sys
    API_BASE = "http://localhost:8000"
    from app.model_management import ModelManager
    mgr = ModelManager()
    if action == "list":
        r = requests.get(f"{API_BASE}/models")
        typer.echo(json.dumps(r.json(), indent=2))
    elif action == "set" and name:
        r = requests.post(f"{API_BASE}/models/active", json={"model": name})
        typer.echo(r.json())
    elif action == "storage-path":
        if name:
            path = os.path.expanduser(name)
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception as e:
                    typer.echo(f"[ERROR] Could not create path: {e}")
                    raise typer.Exit(1)
            if not os.access(path, os.W_OK):
                typer.echo("[ERROR] Path is not writable.")
                raise typer.Exit(1)
            st = os.statvfs(path)
            free = st.f_bavail * st.f_frsize // (1024*1024)
            if free < 100:
                typer.echo(f"[ERROR] Not enough free space at {path} ({free} MB available).")
                raise typer.Exit(1)
            r = requests.post(f"{API_BASE}/models/storage-path", params={"path": path})
            if r.status_code == 200:
                typer.echo(f"Model storage path set to: {path}")
            else:
                typer.echo(f"[ERROR] Failed to set model storage path: {r.text}")
        else:
            r = requests.get(f"{API_BASE}/models/storage-path")
            if r.status_code == 200:
                typer.echo(f"Current model storage path: {r.json().get('storage_path')}")
            else:
                typer.echo(f"[ERROR] Failed to get model storage path: {r.text}")
    elif action == "load" and name:
        typer.echo(f"[INFO] Loading model '{name}' via Ollama...")
        ok = mgr.load_model_ollama(name)
        if ok:
            typer.echo(f"Model '{name}' loaded successfully.")
        else:
            typer.echo(f"[ERROR] Failed to load model '{name}'.")
    elif action == "unload" and name:
        typer.echo(f"[INFO] Unloading model '{name}' via Ollama...")
        ok = mgr.unload_model_ollama(name)
        if ok:
            typer.echo(f"Model '{name}' unloaded successfully.")
        else:
            typer.echo(f"[ERROR] Failed to unload model '{name}'.")
    elif action == "volumes":
        volumes = mgr.list_ollama_volumes()
        typer.echo("Available model storage volumes:")
        for v in volumes:
            typer.echo(f"  {v}")
    elif action == "set-volume" and name:
        typer.echo(f"[INFO] Setting Ollama model storage volume to '{name}'...")
        ok = mgr.set_ollama_volume(os.path.expanduser(name))
        if ok:
            typer.echo(f"Ollama volume set to: {name}")
        else:
            typer.echo(f"[ERROR] Failed to set Ollama volume.")
    else:
        typer.echo("Usage: coder-x model [list|set|storage-path|load|unload|volumes|set-volume] [name/path]")

@app.command()
def file(action: str = typer.Argument(..., help="Action: read, write, append"), path: str = typer.Argument(..., help="File path"), text: str = typer.Argument(None, help="Text for write/append")):
    """Read, write, or append to files."""
    import requests
    API_BASE = "http://localhost:8000"
    if action == "read":
        r = requests.get(f"{API_BASE}/file/read", params={"path": path})
        typer.echo(r.text)
    elif action == "write" and text:
        r = requests.post(f"{API_BASE}/file/write", json={"path": path, "text": text})
        typer.echo(r.text)
    elif action == "append" and text:
        r = requests.post(f"{API_BASE}/file/append", json={"path": path, "text": text})
        typer.echo(r.text)
    else:
        typer.echo("Usage: coder-x file [read|write|append] <path> [text]")

@app.command()
def history():
    """Show session history."""
    import requests, json
    API_BASE = "http://localhost:8000"
    r = requests.get(f"{API_BASE}/history")
    typer.echo(json.dumps(r.json(), indent=2))

@app.command()
def user():
    """Show current user info."""
    import requests, json
    API_BASE = "http://localhost:8000"
    r = requests.get(f"{API_BASE}/user/info")
    typer.echo(json.dumps(r.json(), indent=2))

@app.command()
def feedback(text: str = typer.Argument(..., help="Feedback text")):
    """Submit feedback."""
    import requests
    API_BASE = "http://localhost:8000"
    r = requests.post(f"{API_BASE}/feedback/submit", json={"feedback": text})
    typer.echo(r.text)

@app.command()
def integration(action: str = typer.Argument(..., help="Action: list, connect, disconnect"), svc: str = typer.Argument(None, help="Service name")):
    """Manage integrations."""
    import requests, json
    API_BASE = "http://localhost:8000"
    if action == "list":
        r = requests.get(f"{API_BASE}/integration/list")
        typer.echo(json.dumps(r.json(), indent=2))
    elif action == "connect" and svc:
        r = requests.post(f"{API_BASE}/integration/connect", json={"service": svc})
        typer.echo(r.text)
    elif action == "disconnect" and svc:
        r = requests.post(f"{API_BASE}/integration/disconnect", json={"service": svc})
        typer.echo(r.text)
    else:
        typer.echo("Usage: coder-x integration [list|connect|disconnect] [service]")

@app.command()
def mcp(action: str = typer.Argument(..., help="Action: get-server, set-server, get-context, save-context"), arg1: str = typer.Argument(None, help="Server URL or context ID"), arg2: str = typer.Argument(None, help="Context data as JSON (for save-context)")):
    """MCP protocol integration commands."""
    import requests, json
    API_BASE = "http://localhost:8000"
    if action == "get-server":
        r = requests.get(f"{API_BASE}/mcp/server")
        if r.status_code == 200:
            typer.echo(f"MCP server URL: {r.json().get('server_url')}")
        else:
            typer.echo(f"[ERROR] Failed to get MCP server URL: {r.text}")
    elif action == "set-server" and arg1:
        r = requests.post(f"{API_BASE}/mcp/server", params={"url": arg1})
        if r.status_code == 200:
            typer.echo(f"MCP server URL set to: {arg1}")
        else:
            typer.echo(f"[ERROR] Failed to set MCP server URL: {r.text}")
    elif action == "get-context" and arg1:
        r = requests.get(f"{API_BASE}/mcp/context/{arg1}")
        if r.status_code == 200:
            typer.echo(json.dumps(r.json(), indent=2))
        else:
            typer.echo(f"[ERROR] Failed to get context: {r.text}")
    elif action == "save-context" and arg1 and arg2:
        try:
            data = json.loads(arg2)
        except Exception as e:
            typer.echo(f"[ERROR] Invalid JSON for context data: {e}")
            raise typer.Exit(1)
        r = requests.post(f"{API_BASE}/mcp/context/{arg1}", json={"context_id": arg1, "data": data})
        if r.status_code == 200:
            typer.echo(f"Context {arg1} saved.")
        else:
            typer.echo(f"[ERROR] Failed to save context: {r.text}")
    else:
        typer.echo("Usage: coder-x mcp [get-server|set-server|get-context|save-context] <arg1> [arg2]")

@app.command()
def version():
    """Show the version of Coder-X."""
    typer.echo("Coder-X version 1.0.0")

from typing import List

@app.command()
def shell(cmd: List[str] = typer.Argument(None, help="Shell command to run (optional, pass as separate args)")):
    """Run a shell command or start the interactive shell (with slash command support)."""
    import subprocess, shlex, os, sys
    if cmd:
        command_str = " ".join(cmd)
        dangerous = any(x in command_str for x in ["rm", "shutdown", "reboot"])
        if dangerous:
            typer.echo("[WARNING] Dangerous command detected.")
            try:
                approve = input("Are you sure you want to run this command? (yes/no): ").strip().lower()
            except Exception:
                approve = ""
            if approve != "yes":
                typer.echo("Command aborted.")
                print("Command aborted.")
                sys.exit(0)
        try:
            result = subprocess.run(command_str, shell=True, capture_output=True, text=True)
            typer.echo(result.stdout)
            if result.stderr:
                typer.echo(result.stderr)
        except Exception as e:
            typer.echo(f"[ERROR] {e}")
    else:
        from app.interactive_shell import InteractiveShell
        InteractiveShell().run()


if __name__ == "__main__":
    app()
