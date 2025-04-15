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
