import os
import tempfile
from app.file_operations import FileOps

def test_read_write_append_file():
    fo = FileOps()
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        assert fo.write_file(path, "hello")
        assert fo.read_file(path) == "hello"
        assert fo.append_file(path, " world")
        assert fo.read_file(path) == "hello world"
    finally:
        os.remove(path)

def test_file_exists():
    fo = FileOps()
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        assert fo.file_exists(path)
    finally:
        os.remove(path)

def test_read_nonexistent_file():
    fo = FileOps()
    assert fo.read_file("/tmp/does_not_exist_coderx.txt") is None

def test_write_unwritable_location(monkeypatch):
    fo = FileOps()
    def fail_write(*a, **kw):
        raise PermissionError("denied")
    monkeypatch.setattr("builtins.open", lambda *a, **kw: (_ for _ in ()).throw(PermissionError("denied")))
    assert not fo.write_file("/root/forbidden.txt", "data")

def test_append_to_nonexistent_file():
    fo = FileOps()
    path = tempfile.mktemp()
    try:
        assert fo.append_file(path, "data")
        assert fo.read_file(path) == "data"
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_directory_as_file(tmp_path):
    fo = FileOps()
    dir_path = tmp_path
    # Should fail gracefully
    assert not fo.write_file(str(dir_path), "data")
    assert fo.read_file(str(dir_path)) is None
    assert not fo.append_file(str(dir_path), "data")

def test_file_io_exception(monkeypatch):
    fo = FileOps()
    def fail_open(*a, **kw):
        raise OSError("fail")
    monkeypatch.setattr("builtins.open", fail_open)
    assert not fo.write_file("/tmp/fail.txt", "data")
    assert fo.read_file("/tmp/fail.txt") is None

def test_explain_code_nonexistent(tmp_path):
    fo = FileOps()
    file_path = tmp_path / "nofile.py"
    assert fo.explain_code(str(file_path)) is None

def test_explain_code_fallback_summary(tmp_path, monkeypatch):
    fo = FileOps()
    file_path = tmp_path / "foo.py"
    file_path.write_text("print('hi')\n# comment\n")
    # Patch requests to raise ImportError so fallback triggers
    monkeypatch.setitem(__import__('sys').modules, "requests", None)
    result = fo.explain_code(str(file_path))
    assert "Summary" in result or result is not None

def test_explain_code_remote_success(tmp_path, monkeypatch):
    fo = FileOps()
    file_path = tmp_path / "foo.py"
    file_path.write_text("print('hi')\n")
    class DummyResp:
        def json(self): return {"result": "Remote explanation"}
        @property
        def status_code(self): return 200
    dummy_requests = type("R", (), {"post": staticmethod(lambda url, json, timeout: DummyResp())})
    monkeypatch.setitem(__import__('sys').modules, "requests", dummy_requests)
    result = fo.explain_code(str(file_path))
    assert result is not None and "Remote explanation" in result

def test_explain_code_remote_error(tmp_path, monkeypatch):
    fo = FileOps()
    file_path = tmp_path / "foo.py"
    file_path.write_text("print('hi')\n")
    class DummyResp:
        def json(self): raise ValueError("bad json")
        @property
        def status_code(self): return 500
    dummy_requests = type("R", (), {"post": staticmethod(lambda url, json, timeout: DummyResp())})
    monkeypatch.setitem(__import__('sys').modules, "requests", dummy_requests)
    result = fo.explain_code(str(file_path))
    assert "Summary" in result or result is not None

def test_explain_code_env_override(tmp_path, monkeypatch):
    fo = FileOps()
    file_path = tmp_path / "foo.py"
    file_path.write_text("print('hi')\n")
    class DummyResp:
        def json(self): return {"result": "from custom endpoint"}
        @property
        def status_code(self): return 200
    dummy_requests = type("R", (), {"post": staticmethod(lambda url, json, timeout: DummyResp())})
    monkeypatch.setitem(__import__('sys').modules, "requests", dummy_requests)
    monkeypatch.setenv("CODER_X_MODEL_API", "http://custom-endpoint")
    result = fo.explain_code(str(file_path))
    assert "from custom endpoint" in result

def test_run_tests_success(monkeypatch):
    fo = FileOps()
    class DummyResult:
        stdout = "test passed"
        stderr = ""
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    out = fo.run_tests("foo.py")
    assert "test passed" in out

def test_run_tests_failure(monkeypatch):
    fo = FileOps()
    class DummyResult:
        stdout = ""
        stderr = "fail"
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    out = fo.run_tests("foo.py")
    assert "fail" in out

def test_run_tests_exception(monkeypatch):
    fo = FileOps()
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: (_ for _ in ()).throw(Exception("boom")))
    out = fo.run_tests("foo.py")
    assert "boom" in out

def test_lint_code_success(monkeypatch):
    fo = FileOps()
    class DummyResult:
        stdout = "no lint errors"
        stderr = ""
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    out = fo.lint_code("foo.py")
    assert "no lint errors" in out

def test_lint_code_failure(monkeypatch):
    fo = FileOps()
    class DummyResult:
        stdout = ""
        stderr = "lint fail"
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    out = fo.lint_code("foo.py")
    assert "lint fail" in out

def test_lint_code_exception(monkeypatch):
    fo = FileOps()
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: (_ for _ in ()).throw(Exception("bad linter")))
    out = fo.lint_code("foo.py")
    assert "bad linter" in out
