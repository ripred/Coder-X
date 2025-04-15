import tempfile, os
from tests.test_cli_config import run_cli_command

import pytest
@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_config_setup():
    # Simulate guided config setup: model, storage path, api_keys, mcp_server
    temp_dir = tempfile.mkdtemp()
    user_inputs = [
        "setup-model",  # model
        temp_dir,       # model_storage_path
        "openai-key",  # openai api key
        "anthropic-key", # anthropic api key
        "ollama-key",    # ollama api key
        "https://mcp.example.com" # mcp_server
    ]
    input_text = "\n".join(user_inputs)
    out, err, code = run_cli_command("config setup", input_text=input_text)
    assert "Config saved" in out
    import re, json as js
    matches = re.findall(r'\{.*?\}', out, re.DOTALL)
    assert matches, f"No JSON object in output: {out}"
    resp = js.loads(matches[-1])
    assert resp.get("success") is True
    # Verify config values were set
    out, err, code = run_cli_command("config show")
    assert "setup-model" in out
    assert temp_dir in out
    assert "openai-key" in out
    assert "anthropic-key" in out
    assert "ollama-key" in out
    assert "https://mcp.example.com" in out
