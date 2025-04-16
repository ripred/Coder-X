import json
import pytest

def test_json_decode_error():
    path = 'malformed.json'
    with open(path, 'w') as f:
        f.write('not a json')
    with pytest.raises(json.JSONDecodeError):
        with open(path) as f:
            json.load(f)
