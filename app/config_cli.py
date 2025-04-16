import typer
import json
from typing import Optional
from app.config import (
    load_config, save_config, set_config_key, unset_config_key, CONFIG_PATH
)
from app.config_schema import CoderXConfig

config_app = typer.Typer(help="Manage Coder-X configuration.")

def print_json(data):
    typer.echo(json.dumps(data, indent=2))

@config_app.command()
def show(config_path: Optional[str] = typer.Option(None, help="Path to config file.")):
    """Show current configuration."""
    try:
        config = load_config(config_path)
        print_json({"success": True, "config": config.model_dump()})
    except Exception as e:
        print_json({"success": False, "error": str(e)})
        raise typer.Exit(1)

@config_app.command()
def set(
    key: str = typer.Argument(..., help="Config key (dot notation for nested keys)."),
    value: str = typer.Argument(..., help="Value to set."),
    config_path: Optional[str] = typer.Option(None, help="Path to config file.")
):
    """Set a configuration value."""
    try:
        config = load_config(config_path)
        # Try to convert value to int, float, or bool
        def convert(val):
            if val.lower() in ("true", "false"): return val.lower() == "true"
            try: return int(val)
            except: pass
            try: return float(val)
            except: pass
            return val
        config = set_config_key(config, key, convert(value))
        save_config(config, config_path)
        print_json({"success": True, "config": config.model_dump()})
    except Exception as e:
        print_json({"success": False, "error": str(e)})
        raise typer.Exit(1)

@config_app.command()
def unset(
    key: str = typer.Argument(..., help="Config key (dot notation for nested keys)."),
    config_path: Optional[str] = typer.Option(None, help="Path to config file.")
):
    """Unset (remove) a configuration value."""
    try:
        config = load_config(config_path)
        config = unset_config_key(config, key)
        save_config(config, config_path)
        print_json({"success": True, "config": config.model_dump()})
    except Exception as e:
        print_json({"success": False, "error": str(e)})
        raise typer.Exit(1)

@config_app.command()
def setup(config_path: Optional[str] = typer.Option(None, help="Path to config file.")):
    """Guided configuration setup (interactive)."""
    try:
        config = load_config(config_path)
        # Guided prompts
        model = typer.prompt(f"Model (current: {config.model})", default=config.model or "")
        if model:
            config = set_config_key(config, "model", model)
        storage_path = typer.prompt(f"Model storage path (current: {config.model_storage_path})", default=config.model_storage_path)
        if storage_path:
            config = set_config_key(config, "model_storage_path", storage_path)
        for provider in ["openai", "anthropic", "ollama"]:
            current = getattr(config.api_keys, provider, None)
            key_val = typer.prompt(f"API key for {provider} (current: {current})", default=current or "")
            if key_val:
                config = set_config_key(config, f"api_keys.{provider}", key_val)
        mcp_server = typer.prompt(f"MCP server endpoint (current: {config.mcp_server})", default=config.mcp_server or "")
        if mcp_server:
            config = set_config_key(config, "mcp_server", mcp_server)
        save_config(config, config_path)
        print_json({"success": True, "message": "Config saved", "config": config.model_dump()})
    except Exception as e:
        print_json({"success": False, "error": str(e)})
        raise typer.Exit(1)
