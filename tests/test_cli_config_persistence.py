import tempfile, os
from tests.test_cli_config import run_cli_command

import pytest
@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_config_persistence_across_cli_runs():
    temp_dir = tempfile.mkdtemp()
    # Set preferences via CLI
    run_cli_command(f"config set model persisted-model")
    run_cli_command(f"config set model_storage_path {temp_dir}")
    run_cli_command(f"config set api_keys.openai persisted-openai-key")
    run_cli_command(f"config set mcp_server https://persisted-mcp.example.com")
    # Now, simulate a new CLI session and check if preferences persist
    out, err, code = run_cli_command("config show")
    assert "persisted-model" in out
    assert temp_dir in out
    assert "persisted-openai-key" in out
    assert "https://persisted-mcp.example.com" in out
