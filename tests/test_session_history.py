import os
import tempfile
from app.session_history import SessionHistory

def test_append_and_load_history():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        sh = SessionHistory(config={"history_path": path})
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
        sh = SessionHistory(config={"history_path": path})
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
        sh = SessionHistory(config={"history_path": path})
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
        sh = SessionHistory(config={"history_path": path})
        assert sh.load() == [] or sh.load() == None or isinstance(sh.load(), list)
    finally:
        os.remove(path)

def test_load_missing_file():
    path = "_not_a_real_file.json"
    try:
        sh = SessionHistory(config={"history_path": path})
        # Should create file and return []
        result = sh.load()
        assert isinstance(result, list)
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_export_file_error(monkeypatch, tmp_path):
    path = str(tmp_path / "hist.json")
    export_path = str(tmp_path / "export.json")
    sh = SessionHistory(config={"history_path": path})
    sh.append({"cmd": "foo"})
    # Simulate error by patching open
    def bad_open(*a, **kw):
        raise IOError("fail")
    monkeypatch.setattr("builtins.open", bad_open)
    assert not sh.export(export_path)

def test_append_non_dict(tmp_path):
    path = str(tmp_path / "hist.json")
    sh = SessionHistory(config={"history_path": path})
    sh.clear()
    # Should still append, but not crash
    sh.append("notadict")
    hist = sh.load()
    assert "notadict" in hist or any(isinstance(x, str) for x in hist)
