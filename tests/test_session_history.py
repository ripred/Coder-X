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
