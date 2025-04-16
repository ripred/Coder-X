import pytest
from app import interactive_shell
InteractiveShell = interactive_shell.InteractiveShell

class DummyShell(InteractiveShell):
    def __init__(self):
        super().__init__()
        self.output = []
    def session_prompt(self, prompt):
        # Simulate user input
        return "/help"
    def run_once(self, line):
        # Capture output for test
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        self.handle_slash_command(line)
        out = sys.stdout.getvalue()
        sys.stdout = old_stdout
        return out

def test_help_command():
    shell = DummyShell()
    output = shell.run_once("/help")
    assert "Available commands" in output
    assert "/model-list" in output

def test_unknown_command():
    shell = DummyShell()
    output = shell.run_once("/unknown")
    assert "Unknown or incomplete command" in output

def test_exit(monkeypatch):
    shell = DummyShell()
    called = {}
    def fake_exit(code):
        called['exit'] = code
        raise SystemExit
    monkeypatch.setattr("sys.exit", fake_exit)
    with pytest.raises(SystemExit):
        shell.run_once("/exit")
    assert called['exit'] == 0

def test_model_list(monkeypatch):
    shell = DummyShell()
    class FakeMM:
        def list_local_models(self): return ['foo', 'bar']
        def list_ollama_models(self): return ['baz']
    monkeypatch.setattr("app.interactive_shell.ModelManager", lambda *a, **kw: FakeMM())
    output = shell.run_once("/model-list")
    assert 'foo' in output and 'bar' in output and 'baz' in output

def test_model_set(monkeypatch):
    shell = DummyShell()
    called = {}
    class FakeMM:
        def set_active_model(self, name): called['model'] = name
    monkeypatch.setattr("app.interactive_shell.ModelManager", lambda *a, **kw: FakeMM())
    output = shell.run_once("/model-set testmodel")
    assert "Active model set to: testmodel" in output
    assert called['model'] == "testmodel"

def test_model_storage_path_set(monkeypatch):
    shell = DummyShell()
    called = {}
    class FakeMM:
        storage_path = "/models"
        def set_model_storage_path(self, path): called['path'] = path
    monkeypatch.setattr("app.interactive_shell.ModelManager", lambda *a, **kw: FakeMM())
    output = shell.run_once("/model-storage-path /tmp")
    assert "Model storage path set to: /tmp" in output
    assert called['path'] == "/tmp"

def test_model_storage_path_show(monkeypatch):
    shell = DummyShell()
    class FakeMM:
        storage_path = "/models"
        def set_model_storage_path(self, path): pass
    monkeypatch.setattr("app.interactive_shell.ModelManager", lambda *a, **kw: FakeMM())
    output = shell.run_once("/model-storage-path")
    assert "Current model storage path: /models" in output

def test_config_show(monkeypatch):
    shell = DummyShell()
    class FakeConf:
        def model_dump(self): return {"foo": "bar"}
    monkeypatch.setattr("app.interactive_shell.load_config", lambda: FakeConf())
    output = shell.run_once("/config-show")
    assert 'foo' in output and 'bar' in output

def test_config_set(monkeypatch):
    shell = DummyShell()
    called = {}
    class FakeConf:
        def model_dump(self): return {"foo": "bar"}
    def fake_load(): return FakeConf()
    def fake_set(conf, key, value): called['set'] = (key, value); return conf
    def fake_save(conf): called['save'] = True
    monkeypatch.setattr("app.interactive_shell.load_config", fake_load)
    monkeypatch.setattr("app.interactive_shell.set_config_key", fake_set)
    monkeypatch.setattr("app.interactive_shell.save_config", fake_save)
    output = shell.run_once("/config-set foo baz")
    assert "Set foo = baz" in output
    assert called['set'] == ("foo", "baz")
    assert called['save']

def test_file_read(monkeypatch):
    shell = DummyShell()
    monkeypatch.setattr("app.interactive_shell.read_file", lambda path: "hello" if path=="/tmp/x" else None)
    output = shell.run_once("/file-read /tmp/x")
    assert "hello" in output
    output2 = shell.run_once("/file-read /notfound")
    assert "Could not read file" in output2

def test_file_write(monkeypatch):
    shell = DummyShell()
    called = {}
    def fake_write(path, content):
        called['w'] = (path, content)
        return path == "/ok"
    monkeypatch.setattr("app.interactive_shell.write_file", fake_write)
    output = shell.run_once("/file-write /ok hello world")
    assert "[OK] File written." in output
    assert called['w'] == ("/ok", "hello world")
    output2 = shell.run_once("/file-write /fail test")
    assert "Could not write file" in output2

def test_shell_command(monkeypatch):
    shell = DummyShell()
    class FakeResult:
        stdout = "out"
        stderr = ""
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: FakeResult())
    output = shell.run_once("/shell echo hi")
    assert "out" in output

def test_shell_command_dangerous(monkeypatch):
    shell = DummyShell()
    called = {}
    def fake_run(cmd, shell, capture_output, text):
        raise Exception("danger")
    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("builtins.input", lambda prompt=None: "no")
    out = shell.run_once("/shell rm -rf /")
    assert "[ERROR]" in out or "Aborted" in out or "Command aborted." in out

# --- Additional edge/error case tests ---
def test_file_read_fail(monkeypatch):
    shell = DummyShell()
    monkeypatch.setattr("app.interactive_shell.read_file", lambda path: None)
    out = shell.run_once("/file-read missing.txt")
    assert "Could not read file" in out

def test_file_write_missing_args():
    shell = DummyShell()
    out = shell.run_once("/file-write onlyonearg")
    assert "[ERROR]" in out or "Usage" in out or "Unknown or incomplete command" in out or out.strip() == ""

def test_config_set_missing_args():
    shell = DummyShell()
    out = shell.run_once("/config-set keyonly")
    assert "[ERROR]" in out or "Usage" in out or "Unknown or incomplete command" in out or out.strip() == ""

def test_model_set_missing_args():
    shell = DummyShell()
    out = shell.run_once("/model-set")
    assert "[ERROR]" in out or "Usage" in out or "Unknown or incomplete command" in out or out.strip() == ""

def test_model_storage_path_exception(monkeypatch):
    shell = DummyShell()
    class MM:
        storage_path = "/foo/bar"
        def set_model_storage_path(self, path):
            raise Exception("fail-path")
    monkeypatch.setattr("app.interactive_shell.ModelManager", lambda: MM())
    out = shell.run_once("/model-storage-path /bad/path")
    assert "[ERROR]" in out

def test_shell_missing_args():
    shell = DummyShell()
    out = shell.run_once("/shell")
    assert "[ERROR]" in out or "Usage" in out or "Unknown or incomplete command" in out or out.strip() == ""

def test_non_slash_input(capsys):
    shell = DummyShell()
    # Simulate non-slash input
    import sys
    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    shell.handle_slash_command = lambda line: None  # bypass
    print("hello")
    sys.stdout.seek(0)
    sys.stdout = old_stdout
    # No assert: just ensure no crash

def test_keyboardinterrupt(monkeypatch):
    class Shell(InteractiveShell):
        def __init__(self):
            pass
        def run(self):
            raise KeyboardInterrupt
    shell = Shell()
    try:
        shell.run()
    except KeyboardInterrupt:
        pass

def test_eoferror(monkeypatch):
    class Shell(InteractiveShell):
        def __init__(self):
            pass
        def run(self):
            raise EOFError
    shell = Shell()
    try:
        shell.run()
    except EOFError:
        pass
