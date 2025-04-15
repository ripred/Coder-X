import subprocess
import sys
import os
import time
import requests

# Start the FastAPI server in the background for CLI tests
def start_server():
    import uvicorn
    from multiprocessing import Process
    proc = Process(target=uvicorn.run, args=("app.main:app",), kwargs={"host": "127.0.0.1", "port": 8000, "log_level": "error"})
    proc.start()
    time.sleep(1.5)
    return proc

import pytest
@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_cli_help_and_exit():
    proc = start_server()
    try:
        # Run CLI with 'help' and 'exit' commands
        import os
        import subprocess
        cli_entry_path = os.path.join("app", "cli_entry.py")
        result = subprocess.run([
            sys.executable, cli_entry_path, "--help"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10, cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), env={**os.environ, "PYTHONPATH": "."}
        )
        assert "Coder-X" in result.stdout
        assert "Commands" in result.stdout
    finally:
        proc.terminate()
        proc.join()

@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_cli_model_list(monkeypatch):
    proc = start_server()
    try:
        import os
        import subprocess
        cli_entry_path = os.path.join("app", "cli_entry.py")
        result = subprocess.run([
            sys.executable, cli_entry_path, "model", "list"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10, cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), env={**os.environ, "PYTHONPATH": "."}
        )
        assert "models" in result.stdout
    finally:
        proc.terminate()
        proc.join()

# NOTE: test_cli_dangerous_shell_approve is commented out for safety.
# It should be re-enabled and run by a human to verify override logic for dangerous shell commands.
# def test_cli_dangerous_shell_approve(monkeypatch, tmp_path):
#     """
#     Test that approving a dangerous shell command runs it and logs the approval.
#     """
#     # This test is disabled for CI safety. Enable and run manually for full coverage.
#     pass

@pytest.mark.skip(reason="Replaced by new approaches in test_cli_new.py")
def test_cli_dangerous_shell_decline(monkeypatch, tmp_path):
    """
    Test that declining a dangerous shell command aborts execution and does not log.
    """
    import os
    # Patch input to always decline
    monkeypatch.setattr("builtins.input", lambda _: "no")
    # Patch HOME so log file goes to tmp_path
    monkeypatch.setenv("HOME", str(tmp_path))
    proc = start_server()
    try:
        import os
        import subprocess
        cli_entry_path = os.path.join("app", "cli_entry.py")
        result = subprocess.run([
            sys.executable, cli_entry_path, "shell", "rm", "testfile"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10, cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), env={**os.environ, "PYTHONPATH": "."}
        )
        # Should see 'Command aborted.' in result.stdout
        assert "Command aborted." in result.stdout
        # Log file should not exist
        log_path = tmp_path / ".coder_x_dangerous_shell.log"
        assert not log_path.exists()    
    finally:
        proc.terminate()
        proc.join()
