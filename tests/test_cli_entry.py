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
