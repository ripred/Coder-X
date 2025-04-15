import subprocess
import sys
import os
import tempfile
import json

def run_cli_command(cmd, input_text=None):
    """Run the CLI with the given command and optional input, return output as string."""
    env = os.environ.copy()
    # Use a temp config file so we don't affect user config
    with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
        config_path = tf.name
        tf.write(json.dumps({}))
    env["CLAUDE_CODE_CONFIG"] = config_path
    cli_path = os.path.join(os.path.dirname(__file__), "../app/cli.py")
    args = [sys.executable, cli_path]
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    try:
        out, err = proc.communicate(input=(cmd+"\n").encode() if input_text is None else (cmd+"\n"+input_text+"\n").encode(), timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise
    finally:
        os.remove(config_path)
    return out.decode(), err.decode(), proc.returncode

import pytest
@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_config_show_and_set():
    # Show config
    out, err, code = run_cli_command("config show")
    assert "model" in out
    # Set a config value
    out, err, code = run_cli_command("config set model test-model")
    # Parse last JSON object in output
    import re, json as js
    matches = re.findall(r'\{.*?\}', out, re.DOTALL)
    assert matches, f"No JSON object in output: {out}"
    resp = js.loads(matches[-1])
    assert resp.get("success") is True
    # Show config again
    out, err, code = run_cli_command("config show")
    assert "test-model" in out

@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_config_set_prompt():
    # Test interactive prompt for config set
    out, err, code = run_cli_command("config set model", input_text="interactive-model")
    import re, json as js
    matches = re.findall(r'\{.*?\}', out, re.DOTALL)
    assert matches, f"No JSON object in output: {out}"
    resp = js.loads(matches[-1])
    assert resp.get("success") is True
    out, err, code = run_cli_command("config show")
    assert "interactive-model" in out
