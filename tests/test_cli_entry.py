import pytest
from typer.testing import CliRunner
from app.cli_entry import app

runner = CliRunner()

def test_model_list(monkeypatch):
    class DummyMgr:
        def list_local_models(self): return ["foo"]
        def list_ollama_models(self): return ["bar"]
    monkeypatch.setattr("app.model_management.ModelManager", DummyMgr)
    result = runner.invoke(app, ["model", "list"])
    assert result.exit_code == 0
    assert "foo" in result.output and "bar" in result.output

def test_model_set(monkeypatch):
    called = {}
    class DummyMgr:
        def __init__(self): pass
        def set_active_model(self, name): called["model"] = name
    monkeypatch.setattr("app.model_management.ModelManager", DummyMgr)
    result = runner.invoke(app, ["model", "set", "baz"])
    assert result.exit_code == 0
    assert "baz" in result.output
    assert called["model"] == "baz"

def test_file_read(monkeypatch):
    def fake_read_file(path):
        assert path == "foo.txt"
        return "file contents"
    monkeypatch.setattr("app.file_operations.read_file", fake_read_file)
    result = runner.invoke(app, ["file", "read", "foo.txt"])
    assert result.exit_code == 0
    assert "file contents" in result.output

def test_file_read_error(monkeypatch):
    def fake_read_file(path):
        raise IOError("fail")
    monkeypatch.setattr("app.file_operations.read_file", fake_read_file)
    result = runner.invoke(app, ["file", "read", "bad.txt"])
    assert result.exit_code == 0
    assert "[ERROR] fail" in result.output

def test_file_write(monkeypatch):
    called = {}
    def fake_write_file(path, text):
        called["path"] = path
        called["text"] = text
    monkeypatch.setattr("app.file_operations.write_file", fake_write_file)
    result = runner.invoke(app, ["file", "write", "foo.txt", "hello"])
    assert result.exit_code == 0
    assert "[OK] File written." in result.output
    assert called["path"] == "foo.txt"
    assert called["text"] == "hello"

def test_file_write_error(monkeypatch):
    def fake_write_file(path, text):
        raise IOError("failwrite")
    monkeypatch.setattr("app.file_operations.write_file", fake_write_file)
    result = runner.invoke(app, ["file", "write", "foo.txt", "hello"])
    assert result.exit_code == 0
    assert "[ERROR] failwrite" in result.output

def test_file_append(monkeypatch):
    called = {}
    def fake_append_file(path, text):
        called["path"] = path
        called["text"] = text
    monkeypatch.setattr("app.file_operations.append_file", fake_append_file)
    result = runner.invoke(app, ["file", "append", "foo.txt", "add"])
    assert result.exit_code == 0
    assert "[OK] Text appended." in result.output
    assert called["path"] == "foo.txt"
    assert called["text"] == "add"

def test_file_append_error(monkeypatch):
    def fake_append_file(path, text):
        raise IOError("failappend")
    monkeypatch.setattr("app.file_operations.append_file", fake_append_file)
    result = runner.invoke(app, ["file", "append", "foo.txt", "add"])
    assert result.exit_code == 0
    assert "[ERROR] failappend" in result.output

# --- Additional tests for cli_entry.py ---
def test_model_storage_path(monkeypatch, tmp_path):
    called = {}
    class DummyMgr:
        storage_path = str(tmp_path)
        def set_model_storage_path(self, path):
            called['path'] = path
        def list_local_models(self): return []
        def list_ollama_models(self): return []
        def load_model_ollama(self, name): called['load'] = name; return True
        def unload_model_ollama(self, name): called['unload'] = name; return True
        def list_ollama_volumes(self): return ['vol1', 'vol2']
        def set_ollama_volume(self, name): called['volume'] = name; return True
    monkeypatch.setattr("app.model_management.ModelManager", DummyMgr)
    # storage-path set (writable)
    result = runner.invoke(app, ["model", "storage-path", str(tmp_path)])
    assert result.exit_code == 0
    assert "Model storage path set to" in result.output
    # storage-path get
    result = runner.invoke(app, ["model", "storage-path"])
    assert result.exit_code == 0
    assert str(tmp_path) in result.output
    # load
    result = runner.invoke(app, ["model", "load", "foo"])
    assert result.exit_code == 0
    assert "loaded successfully" in result.output
    assert called['load'] == "foo"
    # unload
    result = runner.invoke(app, ["model", "unload", "foo"])
    assert result.exit_code == 0
    assert "unloaded successfully" in result.output
    assert called['unload'] == "foo"
    # volumes
    result = runner.invoke(app, ["model", "volumes"])
    assert result.exit_code == 0
    assert "vol1" in result.output and "vol2" in result.output
    # set-volume
    result = runner.invoke(app, ["model", "set-volume", "myvol"])
    assert result.exit_code == 0
    assert "Ollama volume set to" in result.output
    assert called['volume'] == "myvol"
    # usage error
    result = runner.invoke(app, ["model", "badaction"])
    assert result.exit_code == 0
    assert "Usage: coder-x model" in result.output

def test_file_usage_error():
    result = runner.invoke(app, ["file", "badaction", "foo.txt"])
    assert result.exit_code == 0
    assert "Usage: coder-x file" in result.output

def test_history(monkeypatch):
    class DummySH:
        def get_history(self): return ["a", "b"]
    monkeypatch.setattr("app.session_history.SessionHistory", DummySH)
    result = runner.invoke(app, ["history"])
    assert result.exit_code == 0
    assert "a" in result.output and "b" in result.output

def test_user(monkeypatch):
    class DummyUM:
        def get_current_user(self): return "testuser"
    monkeypatch.setattr("app.user_management.UserManager", DummyUM)
    result = runner.invoke(app, ["user"])
    assert result.exit_code == 0
    assert "testuser" in result.output

def test_feedback():
    result = runner.invoke(app, ["feedback", "Great tool!"])
    assert result.exit_code == 0
    assert "Feedback submitted" in result.output

def test_integration(monkeypatch):
    class DummyMgr:
        def list_integrations(self): return ["svc1", "svc2"]
        def connect(self, svc): return svc == "svc1"
        def disconnect(self, svc): return svc == "svc2"
    monkeypatch.setattr("app.third_party_integrations.ThirdPartyIntegration", DummyMgr)
    # list
    result = runner.invoke(app, ["integration", "list"])
    assert result.exit_code == 0
    assert "svc1" in result.output and "svc2" in result.output
    # connect ok
    result = runner.invoke(app, ["integration", "connect", "svc1"])
    assert result.exit_code == 0
    assert "Connected to svc1" in result.output
    # connect fail
    result = runner.invoke(app, ["integration", "connect", "svc2"])
    assert result.exit_code == 0
    assert "Failed to connect to svc2" in result.output
    # disconnect ok
    result = runner.invoke(app, ["integration", "disconnect", "svc2"])
    assert result.exit_code == 0
    assert "Disconnected from svc2" in result.output
    # disconnect fail
    result = runner.invoke(app, ["integration", "disconnect", "svc1"])
    assert result.exit_code == 0
    assert "Failed to disconnect from svc1" in result.output
    # usage error
    result = runner.invoke(app, ["integration", "badaction"])
    assert result.exit_code == 0
    assert "Usage: coder-x integration" in result.output

def test_mcp(monkeypatch):
    class DummyMCP:
        server_url = "http://foo"
        def set_server_url(self, url): self.server_url = url
        def get_context(self, cid): return {"cid": cid}
        def save_context(self, cid, data): return data.get("ok", False)
    monkeypatch.setattr("app.mcp_integration.MCPClient", DummyMCP)
    # get-server
    result = runner.invoke(app, ["mcp", "get-server"])
    assert result.exit_code == 0
    assert "http://foo" in result.output
    # set-server
    result = runner.invoke(app, ["mcp", "set-server", "http://bar"])
    assert result.exit_code == 0
    assert "MCP server set to http://bar" in result.output
    # get-context
    result = runner.invoke(app, ["mcp", "get-context", "cid1"])
    assert result.exit_code == 0
    assert '"cid": "cid1"' in result.output
    # save-context ok
    import json
    result = runner.invoke(app, ["mcp", "save-context", "cid2", json.dumps({"ok": True})])
    assert result.exit_code == 0
    assert "Context cid2 saved" in result.output
    # save-context fail
    result = runner.invoke(app, ["mcp", "save-context", "cid2", json.dumps({"ok": False})])
    assert result.exit_code == 0
    assert "Failed to save context cid2" in result.output
    # save-context invalid JSON
    result = runner.invoke(app, ["mcp", "save-context", "cid2", "notjson"])
    assert result.exit_code == 0
    assert "Invalid JSON for context data" in result.output
    # usage error
    result = runner.invoke(app, ["mcp", "badaction"])
    assert result.exit_code == 0
    assert "Usage: coder-x mcp" in result.output

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Coder-X version" in result.output

def test_shell(monkeypatch):
    class DummyShell:
        def __init__(self): self._ran = True
        def run(self): print("[SHELL]")
    monkeypatch.setattr("app.interactive_shell.InteractiveShell", DummyShell)
    # shell with no args (should run interactive shell)
    result = runner.invoke(app, ["shell"])
    assert result.exit_code == 0
    assert "[SHELL]" in result.output
    # shell with command
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: type('R', (), {"stdout": "ok", "stderr": "", "returncode": 0})())
    result = runner.invoke(app, ["shell", "echo", "hi"])
    assert result.exit_code == 0
    assert "ok" in result.output
