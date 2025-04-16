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
    import json, os
    from app.model_management import ModelManager
    mgr = ModelManager()
    if action == "list":
        models = set(mgr.list_local_models())
        try:
            models.update(mgr.list_ollama_models())
        except Exception:
            pass
        typer.echo(json.dumps(sorted(models), indent=2))
    elif action == "set" and name:
        mgr.set_active_model(name)
        typer.echo({"active_model": name})
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
            try:
                mgr.set_model_storage_path(path)
                typer.echo(f"Model storage path set to: {path}")
            except Exception as e:
                typer.echo(f"[ERROR] Failed to set model storage path: {e}")
        else:
            typer.echo(f"Current model storage path: {mgr.storage_path}")
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
    from app.file_operations import read_file, write_file, append_file
    if action == "read":
        try:
            content = read_file(path)
            typer.echo(content)
        except Exception as e:
            typer.echo(f"[ERROR] {e}")
    elif action == "write" and text:
        try:
            write_file(path, text)
            typer.echo("[OK] File written.")
        except Exception as e:
            typer.echo(f"[ERROR] {e}")
    elif action == "append" and text:
        try:
            append_file(path, text)
            typer.echo("[OK] Text appended.")
        except Exception as e:
            typer.echo(f"[ERROR] {e}")
    else:
        typer.echo("Usage: coder-x file [read|write|append] <path> [text]")

@app.command()
def history():
    """Show session history."""
    from app.session_history import SessionHistory
    sh = SessionHistory()
    typer.echo(sh.get_history())

@app.command()
def user():
    """Show current user info."""
    from app.user_management import UserManager
    um = UserManager()
    typer.echo(um.get_current_user())

@app.command()
def feedback(text: str = typer.Argument(..., help="Feedback text")):
    """Submit feedback."""
    # Placeholder: implement feedback logic directly
    print(f"[Feedback submitted] {text}")

@app.command()
def integration(action: str = typer.Argument(..., help="Action: list, connect, disconnect"), svc: str = typer.Argument(None, help="Service name")):
    """Manage integrations."""
    from app.third_party_integrations import IntegrationManager
    mgr = IntegrationManager()
    if action == "list":
        integrations = mgr.list_integrations()
        typer.echo("Available integrations:")
        for i in integrations:
            typer.echo(f"  {i}")
    elif action == "connect" and svc:
        ok = mgr.connect(svc)
        if ok:
            typer.echo(f"[OK] Connected to {svc}")
        else:
            typer.echo(f"[ERROR] Failed to connect to {svc}")
    elif action == "disconnect" and svc:
        ok = mgr.disconnect(svc)
        if ok:
            typer.echo(f"[OK] Disconnected from {svc}")
        else:
            typer.echo(f"[ERROR] Failed to disconnect from {svc}")
    else:
        typer.echo("Usage: coder-x integration [list|connect|disconnect] <service>")

@app.command()
def mcp(action: str = typer.Argument(..., help="Action: get-server, set-server, get-context, save-context"), arg1: str = typer.Argument(None, help="Server URL or context ID"), arg2: str = typer.Argument(None, help="Context data as JSON (for save-context)")):
    """MCP protocol integration commands."""
    from app.mcp_integration import MCPClient
    mcp = MCPClient()
    import json
    if action == "get-server":
        typer.echo(mcp.server_url)
    elif action == "set-server" and arg1:
        mcp.set_server_url(arg1)
        typer.echo(f"[OK] MCP server set to {arg1}")
    elif action == "get-context" and arg1:
        ctx = mcp.get_context(arg1)
        typer.echo(json.dumps(ctx, indent=2))
    elif action == "save-context" and arg1 and arg2:
        try:
            data = json.loads(arg2)
        except Exception as e:
            typer.echo(f"[ERROR] Invalid JSON for context data: {e}")
            return
        ok = mcp.save_context(arg1, data)
        if ok:
            typer.echo(f"[OK] Context {arg1} saved.")
        else:
            typer.echo(f"[ERROR] Failed to save context {arg1}.")
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
    from app.shell_integration import ShellIntegration
    shell = ShellIntegration()
    import subprocess
    if cmd:
        result = shell.run_command(cmd, override=True)
        typer.echo(result.get("stdout", "") + result.get("stderr", ""))
    else:
        from app.interactive_shell import InteractiveShell
        InteractiveShell().run()


if __name__ == "__main__":
    app()
