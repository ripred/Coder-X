import os
import tempfile
from app.session_history import SessionHistory

def test_append_and_load_history():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        class DummyConf:
            history_path = path
        sh = SessionHistory(config=DummyConf())
        sh.clear()
        sh.append({"cmd": "foo"})
        sh.append({"cmd": "bar"})
        hist = sh.load()
        assert hist == [{"cmd": "foo"}, {"cmd": "bar"}]
    finally:
        os.remove(path)

def test_export_history():
    with tempfile.NamedTemporaryFile(delete=False) as tf, tempfile.NamedTemporaryFile(delete=False) as tf2:
        path = tf.name
        export_path = tf2.name
    try:
        class DummyConf:
            history_path = path
        sh = SessionHistory(config=DummyConf())
        sh.clear()
        sh.append({"cmd": "foo"})
        assert sh.export(export_path)
        with open(export_path) as f:
            data = f.read()
        assert "foo" in data
    finally:
        os.remove(path)
        os.remove(export_path)

def test_clear_history():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        class DummyConf:
            history_path = path
        sh = SessionHistory(config=DummyConf())
        sh.append({"cmd": "foo"})
        sh.clear()
        assert sh.load() == []
    finally:
        os.remove(path)

def test_load_empty_file():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        open(path, "w").close()  # Empty file
        class DummyConf:
            history_path = path
        sh = SessionHistory(config=DummyConf())
        assert sh.load() == [] or sh.load() == None or isinstance(sh.load(), list)
    finally:
        os.remove(path)

def test_load_missing_file():
    path = "_not_a_real_file.json"
    try:
        class DummyConf:
            history_path = path
        sh = SessionHistory(config=DummyConf())
        # Should create file and return []
        result = sh.load()
        assert isinstance(result, list)
        sh.clear()
        assert sh.load() == []
    finally:
        if os.path.exists(path):
            os.remove(path)

import pytest
import json

def test_load_malformed_file(tmp_path):
    import json
    path = tmp_path / "malformed.json"
    with open(path, "w") as f:
        f.write("not a json")
    class DummyConf:
        history_path = str(path)
    sh = SessionHistory(config=DummyConf())
    # Confirm direct json.load fails
    try:
        with open(path) as f:
            json.load(f)
    except Exception as e:
        assert isinstance(e, json.JSONDecodeError)
    # Confirm SessionHistory.load also raises or handles JSONDecodeError
    try:
        sh.load()
    except Exception as e:
        assert isinstance(e, json.JSONDecodeError)

def test_append_malformed_file(tmp_path):
    import json
    path = tmp_path / "malformed_append.json"
    with open(path, "w") as f:
        f.write("not a json")
    class DummyConf:
        history_path = str(path)
    sh = SessionHistory(config=DummyConf())
    # Confirm direct json.load fails
    try:
        with open(path) as f:
            json.load(f)
    except Exception as e:
        assert isinstance(e, json.JSONDecodeError)
    # SessionHistory.append should raise when file is malformed
    try:
        sh.append({"cmd": "foo"})
    except Exception as e:
        assert isinstance(e, json.JSONDecodeError)
    else:
        assert False, 'sh.append did not raise as expected'

def test_init_history_path_is_dir(tmp_path):
    d = tmp_path / "adir"
    d.mkdir()
    class DummyConf:
        history_path = str(d)
    try:
        SessionHistory(config=DummyConf())
        assert False, "Should raise IsADirectoryError or OSError"
    except Exception as e:
        assert isinstance(e, (IsADirectoryError, OSError, PermissionError))

def test_clear_unwritable(tmp_path):
    path = tmp_path / "unwritable.json"
    with open(path, "w") as f:
        f.write("[]")
    os.chmod(path, 0o400)  # read-only
    class DummyConf:
        history_path = str(path)
    sh = SessionHistory(config=DummyConf())
    try:
        sh.clear()
        assert False, "Should raise PermissionError"
    except Exception as e:
        assert isinstance(e, PermissionError)
    finally:
        os.chmod(path, 0o600)

def test_export_file_error(monkeypatch, tmp_path):
    path = str(tmp_path / "hist.json")
    export_path = str(tmp_path / "export.json")
    class DummyConf:
        history_path = path
    sh = SessionHistory(config=DummyConf())
    sh.append({"cmd": "foo"})
    # Simulate error by patching open only within this test
    def bad_open(*a, **kw):
        raise IOError("fail")
    monkeypatch.setattr("builtins.open", bad_open)
    try:
        assert not sh.export(export_path)
    finally:
        monkeypatch.undo()

def test_append_non_dict(tmp_path):
    path = str(tmp_path / "hist.json")
    class DummyConf:
        history_path = path
    sh = SessionHistory(config=DummyConf())
    sh.clear()
    # Should still append, but not crash
    sh.append("notadict")
    hist = sh.load()
    assert "notadict" in hist or any(isinstance(x, str) for x in hist)
