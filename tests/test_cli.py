import pytest
from app import cli

# Test the HELP constant is present and contains expected commands
def test_help_text():
    assert "Coder-X CLI" in cli.HELP
    assert "model list" in cli.HELP
    assert "exit" in cli.HELP

# Test trust_prompt in test mode (should not prompt or exit)
def test_trust_prompt_test_mode(monkeypatch):
    monkeypatch.setenv("CODER_X_TEST_MODE", "1")
    cli.trust_prompt()  # Should not exit or prompt

# Test run_command_line handles empty input and 'exit'
def test_run_command_line_empty_and_exit():
    assert cli.run_command_line("") is None
    assert cli.run_command_line("exit") is None

# Test run_command_line help command
def test_run_command_line_help():
    result = cli.run_command_line("help")
    assert "Coder-X CLI" in result

# Test run_command_line unknown command
def test_run_command_line_unknown():
    result = cli.run_command_line("foobar")
    assert "Unknown command" in result or result is None

# Test 'model list' command with backend mock
def test_run_command_line_model_list(monkeypatch):
    class DummyMM:
        def list_local_models(self): return ["foo"]
        def list_ollama_models(self): return ["bar"]
    monkeypatch.setattr("app.model_management.ModelManager", DummyMM)
    result = cli.run_command_line("model list")
    assert "foo" in result and "bar" in result

# Test 'model set' command with backend mock
def test_run_command_line_model_set(monkeypatch):
    called = {}
    class DummyMM:
        def __init__(self): pass
        def list_local_models(self): return []
        def list_ollama_models(self): return []
        def set_active_model(self, model):
            called["model"] = model
    monkeypatch.setattr("app.model_management.ModelManager", DummyMM)
    result = cli.run_command_line("model set baz")
    assert "baz" in result
    assert called["model"] == "baz"

# Test 'config show' command with backend mock
def test_run_command_line_config_show(monkeypatch):
    from app.config_schema import CoderXConfig
    dummy_conf = CoderXConfig(model="mock")
    monkeypatch.setattr("app.config.load_config", lambda path=None: dummy_conf)
    result = cli.run_command_line("config show")
    assert "mock" in result

# Test 'config set' command with backend mock and edge case
def test_run_command_line_config_set(monkeypatch):
    from app.config_schema import CoderXConfig
    state = {"conf": CoderXConfig(model="old")}
    def fake_load_config(path=None):
        return state["conf"]
    def fake_save_config(conf, path=None):
        state["conf"] = conf
    monkeypatch.setattr("app.config.load_config", fake_load_config)
    monkeypatch.setattr("app.config.save_config", fake_save_config)
    # Patch model_validate to always return a config with model="new"
    monkeypatch.setattr(CoderXConfig, "model_validate", staticmethod(lambda data: CoderXConfig(model="new")))
    result = cli.run_command_line("config set model new")
    assert "new" in result

# Test 'config unset' command with backend mock
def test_run_command_line_config_unset(monkeypatch):
    from app.config_schema import CoderXConfig
    dummy_conf = CoderXConfig(model="something", api_keys={})
    monkeypatch.setattr("app.config.load_config", lambda path=None: dummy_conf)
    monkeypatch.setattr("app.config.save_config", lambda conf, path=None: None)
    result = cli.run_command_line("config unset model")
    assert result is not None

# Test error handling for missing arguments
def test_run_command_line_model_missing_args():
    result = cli.run_command_line("model")
    assert result is None or "Unknown command" in str(result)

def test_run_command_line_config_missing_args():
    result = cli.run_command_line("config")
    assert result is None or "Unknown command" in str(result)
