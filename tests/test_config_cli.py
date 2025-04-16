import os
import tempfile
import json
import pytest
from typer.testing import CliRunner
from app.cli_entry import app

def tmp_config_path():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path

runner = CliRunner()

def test_show_default_config():
    path = tmp_config_path()
    result = runner.invoke(app, ["config", "show", "--config-path", path])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["success"] is True
    assert "config" in data
    os.remove(path)

def test_set_and_show_config():
    path = tmp_config_path()
    result = runner.invoke(app, ["config", "set", "model", "test-model", "--config-path", path])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["success"] is True
    assert data["config"]["model"] == "test-model"
    # Show reflects set value
    result2 = runner.invoke(app, ["config", "show", "--config-path", path])
    data2 = json.loads(result2.output)
    assert data2["config"]["model"] == "test-model"
    os.remove(path)

def test_set_nested_key():
    path = tmp_config_path()
    result = runner.invoke(app, ["config", "set", "api_keys.openai", "sk-test", "--config-path", path])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["success"] is True
    assert data["config"]["api_keys"]["openai"] == "sk-test"
    os.remove(path)

def test_set_invalid_key():
    path = tmp_config_path()
    result = runner.invoke(app, ["config", "set", "notarealkey", "val", "--config-path", path])
    assert result.exit_code != 0
    assert "error" in result.output.lower() or "invalid" in result.output.lower()
    os.remove(path)

def test_set_invalid_value():
    path = tmp_config_path()
    # Set a value that should fail validation (e.g., model_storage_path as int)
    result = runner.invoke(app, ["config", "set", "model_storage_path", "123", "--config-path", path])
    # Accepts as string, but let's try a nested key with invalid type
    result2 = runner.invoke(app, ["config", "set", "api_keys", "123", "--config-path", path])
    assert result2.exit_code != 0 or "error" in result2.output.lower()
    os.remove(path)

def test_missing_config_file():
    path = "/tmp/does_not_exist_coderx_cli.json"
    result = runner.invoke(app, ["config", "show", "--config-path", path])
    # Should show default config, not error
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["success"] is True

def test_malformed_config_file():
    path = tmp_config_path()
    with open(path, "w") as f:
        f.write("not json!")
    result = runner.invoke(app, ["config", "show", "--config-path", path])
    assert result.exit_code != 0
    assert "error" in result.output.lower() or "fail" in result.output.lower()
    os.remove(path)

def test_permission_error_on_save(monkeypatch):
    path = tmp_config_path()
    def fail_open(*a, **kw):
        raise PermissionError("denied")
    monkeypatch.setattr("builtins.open", fail_open)
    result = runner.invoke(app, ["config", "set", "model", "foo", "--config-path", path])
    assert result.exit_code != 0
    assert "denied" in result.output.lower() or "permission" in result.output.lower()
    os.remove(path)

def test_unset_key():
    path = tmp_config_path()
    # Set first
    runner.invoke(app, ["config", "set", "model", "to-remove", "--config-path", path])
    # Unset
    result = runner.invoke(app, ["config", "unset", "model", "--config-path", path])
    data = json.loads(result.output)
    assert data["success"] is True
    assert data["config"]["model"] is None
    os.remove(path)

def test_guided_setup(monkeypatch):
    path = tmp_config_path()
    responses = iter([
        "guided-model",
        os.path.expanduser("~/.coder_x_models"),
        "openai-key",
        "anthropic-key",
        "ollama-key",
        "https://mcp.example.com"
    ])
    monkeypatch.setattr("typer.prompt", lambda text, default=None: next(responses))
    result = runner.invoke(app, ["config", "setup", "--config-path", path])
    data = json.loads(result.output)
    assert data["success"] is True
    assert data["config"]["model"] == "guided-model"
    assert data["config"]["api_keys"]["openai"] == "openai-key"
    assert data["config"]["api_keys"]["anthropic"] == "anthropic-key"
    assert data["config"]["api_keys"]["ollama"] == "ollama-key"
    assert data["config"]["mcp_server"] == "https://mcp.example.com"
    os.remove(path)
