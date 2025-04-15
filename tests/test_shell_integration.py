from app.shell_integration import ShellIntegration

def test_run_safe_command():
    shell = ShellIntegration()
    result = shell.run_command(["echo", "hi"])
    assert result["stdout"].strip() == "hi"
    assert result["returncode"] == 0

def test_run_disallowed_command():
    shell = ShellIntegration()
    result = shell.run_command(["rm", "-rf", "/"])
    assert "error" in result

# Test that dangerous commands are allowed if and only if override=True is set
import sys
import os
from unittest import mock

def test_run_dangerous_command_with_override():
    shell = ShellIntegration()
    # Mock subprocess.run to avoid actually running rm
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0
        result = shell.run_command(["rm", "-rf", "/"], override=True)
        assert "error" not in result
        assert result["returncode"] == 0
        mock_run.assert_called()
