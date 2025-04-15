import subprocess
import sys

import pytest
@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_cli_version():
    import os
    import subprocess
    result = subprocess.run([sys.executable, "-m", "app.cli_entry", "version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env={**os.environ, "PYTHONPATH": ".."})
    assert "Coder-X version" in result.stdout

@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_cli_model_list(monkeypatch):
    # Patch requests.get to simulate API
    import app.cli_entry as cli_entry
    import requests
    class MockResp:
        def __init__(self, data, status_code=200, text=""):
            self._data = data
            self.status_code = status_code
            self.text = text
        def json(self):
            return self._data
    monkeypatch.setattr(requests, "get", lambda url, **kwargs: MockResp({"models": ["foo", "bar"]}) if "/models" in url else MockResp({}, 404, "not found"))
    # Call the CLI command directly
    cli_entry.model("list")
