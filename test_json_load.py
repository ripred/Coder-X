import json
import os
import pytest

def test_load_malformed_json(tmp_path):
    path = tmp_path / "malformed.json"
    with open(path, "w") as f:
        f.write("not a json")
    with open(path) as f:
        contents = f.read()
    assert contents == "not a json"
    with open(path) as f:
        with pytest.raises(json.JSONDecodeError):
            json.load(f)
