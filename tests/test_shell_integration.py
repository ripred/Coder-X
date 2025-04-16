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

def test_run_command_failure(monkeypatch):
    shell = ShellIntegration()
    # 'false' is not in allowed commands, so should return error only
    result = shell.run_command(["false"])
    assert "error" in result
    assert "not allowed" in result["error"]

def test_run_command_missing_binary(monkeypatch):
    shell = ShellIntegration()
    # notarealcommand is not allowed, so error comes from command filter, not subprocess
    result = shell.run_command(["notarealcommand"])
    assert "error" in result
    assert "notarealcommand" in result["error"]

def test_run_command_long_output(monkeypatch):
    shell = ShellIntegration()
    class FakeResult:
        stdout = "a" * 10000
        stderr = ""
        returncode = 0
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: FakeResult())
    result = shell.run_command(["echo", "big"])
    assert result["stdout"].startswith("a")
    assert result["returncode"] == 0

def test_run_command_mixed_output(monkeypatch):
    shell = ShellIntegration()
    class FakeResult:
        stdout = "out"
        stderr = "err"
        returncode = 0
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: FakeResult())
    result = shell.run_command(["echo", "mix"])
    assert result["stdout"] == "out"
    assert result["stderr"] == "err"

def test_run_command_exception(monkeypatch):
    shell = ShellIntegration()
    def fake_run(*a, **kw):
        raise OSError("fail")
    monkeypatch.setattr("subprocess.run", fake_run)
    result = shell.run_command(["ls"])
    assert "error" in result
    assert "fail" in result["error"]

def test_shell_injection_attempt(monkeypatch):
    shell = ShellIntegration()
    # Should be treated as a normal command, but let's mock for safety
    class FakeResult:
        stdout = ""
        stderr = ""
        returncode = 0
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: FakeResult())
    result = shell.run_command(["echo", "; rm -rf /"])
    assert result["returncode"] == 0

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
