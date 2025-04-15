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
    class MockResp:
        def __init__(self, data):
            self._data = data
        def json(self):
            return self._data
    import requests
    monkeypatch.setattr(requests, "get", lambda url, **kwargs: MockResp({"models": ["foo", "bar"]}) if "/models" in url else MockResp({}, 404))
    result = runner.invoke(cli_entry.app, ["model", "list"])
    assert result.exit_code == 0
    assert "foo" in result.output
    assert "bar" in result.output

def test_config_show_and_set_direct(monkeypatch, tmp_path):
    # Patch requests to simulate config API
    config = {"model": "mock-model"}
    class MockResp:
        def __init__(self, data):
            self._data = data
            self.text = "{}"
        def json(self):
            return self._data
    import requests
    monkeypatch.setattr(requests, "get", lambda url, **kwargs: MockResp(config))
    monkeypatch.setattr(requests, "post", lambda url, json, **kwargs: MockResp({"success": True}))
    result = runner.invoke(cli_entry.app, ["config", "show"])
    assert result.exit_code == 0
    assert "mock-model" in result.output
    # Set config
    result = runner.invoke(cli_entry.app, ["config", "set", "model", "new-model"])
    assert result.exit_code == 0
    assert "success" in result.output

def test_config_persistence_file(tmp_path):
    # Simulate config persistence by writing to a file
    config_path = tmp_path / "coderx_config.json"
    config_data = {"model": "persisted-model"}
    import json
    with open(config_path, "w") as f:
        json.dump(config_data, f)
    os.environ["CLAUDE_CODE_CONFIG"] = str(config_path)
    result = runner.invoke(cli_entry.app, ["config", "show"])
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
