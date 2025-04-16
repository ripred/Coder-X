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
    assert not fo.append_file("/tmp/fail.txt", "data")
