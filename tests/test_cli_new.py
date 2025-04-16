import os
import sys
import tempfile
import pytest
from typer.testing import CliRunner
import app.cli_entry as cli_entry

runner = CliRunner()

def test_help_command_typer():
    result = runner.invoke(cli_entry.app, ["--help"])
    assert result.exit_code == 0
    assert "Coder-X" in result.output
    assert "Commands" in result.output

def test_model_list_typer(monkeypatch):
    from app.model_management import ModelManager
    monkeypatch.setattr(ModelManager, "list_local_models", lambda self: ["foo"])
    monkeypatch.setattr(ModelManager, "list_ollama_models", lambda self: ["bar"])
    result = runner.invoke(cli_entry.app, ["model", "list"])
    assert result.exit_code == 0
    assert "foo" in result.output
    assert "bar" in result.output

def test_config_show_and_set_direct(monkeypatch, tmp_path):
    # Write mock config to a temp file and set env var
    import json, os
    config_path = tmp_path / "coderx_config.json"
    from app.config_schema import CoderXConfig
    from app.config_schema import APIKeys
    config = CoderXConfig(
        model="mock-model",
        model_storage_path="/tmp/models",
        api_keys=APIKeys(openai="dummy", anthropic="dummy", ollama="dummy"),
        mcp_server="http://localhost:1234",
        history_path="/tmp/history.json"
    )
    from app.config import save_config, load_config
    save_config(config, str(config_path))
    monkeypatch.setenv("CLAUDE_CODE_CONFIG", str(config_path))
    # Debug print
    print(f"[DEBUG] test_config_show_and_set_direct: config_path={config_path}")
    loaded = load_config(str(config_path))
    print(f"[DEBUG] Loaded config: {loaded}")
    result = runner.invoke(cli_entry.app, ["config", "show", "--config-path", str(config_path)])
    print(f"[DEBUG] CLI output: {result.output}")
    assert result.exit_code == 0
    assert "mock-model" in result.output
    # Set config
    result = runner.invoke(cli_entry.app, ["config", "set", "--config-path", str(config_path), "model", "new-model"])
    assert result.exit_code == 0
    assert "success" in result.output
    # Check new value
    result = runner.invoke(cli_entry.app, ["config", "show", "--config-path", str(config_path)])
    print(f"[DEBUG] CLI output: {result.output}")
    assert "new-model" in result.output

def test_config_persistence_file(tmp_path):
    # Simulate config persistence by writing to a file
    config_path = tmp_path / "coderx_config.json"
    from app.config_schema import CoderXConfig
    import json
    from app.config_schema import APIKeys
    config = CoderXConfig(
        model="persisted-model",
        model_storage_path="/tmp/models",
        api_keys=APIKeys(openai="dummy", anthropic="dummy", ollama="dummy"),
        mcp_server="http://localhost:1234",
        history_path="/tmp/history.json"
    )
    from app.config import save_config, load_config
    save_config(config, str(config_path))
    os.environ["CLAUDE_CODE_CONFIG"] = str(config_path)
    # Debug print
    print(f"[DEBUG] test_config_persistence_file: config_path={config_path}")
    loaded = load_config(str(config_path))
    print(f"[DEBUG] Loaded config: {loaded}")
    result = runner.invoke(cli_entry.app, ["config", "show", "--config-path", str(config_path)])
    print(f"[DEBUG] CLI output: {result.output}")
    assert "persisted-model" in result.output


def test_config_setup_programmatic(monkeypatch, tmp_path):
    # Patch input to simulate guided setup
    responses = iter([
        "setup-model",
        str(tmp_path),
        "openai-key",
        "anthropic-key",
        "ollama-key",
        "https://mcp.example.com"
    ])
    monkeypatch.setattr("builtins.input", lambda prompt=None: next(responses))
    class MockResp:
        def __init__(self, data):
            self._data = data
            self.text = "{}"
        def json(self):
            return self._data
    import requests
    monkeypatch.setattr(requests, "get", lambda url, **kwargs: MockResp({}))
    monkeypatch.setattr(requests, "post", lambda url, json, **kwargs: MockResp({"success": True}))
    result = runner.invoke(cli_entry.app, ["config", "setup"])
    assert result.exit_code == 0
    assert "Config saved" in result.output


def test_cli_version_typer():
    result = runner.invoke(cli_entry.app, ["version"])
    assert result.exit_code == 0
    assert "Coder-X version" in result.output
