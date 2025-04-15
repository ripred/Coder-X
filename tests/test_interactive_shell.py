import pytest
from app.interactive_shell import InteractiveShell

class DummyShell(InteractiveShell):
    def __init__(self):
        super().__init__()
        self.output = []
    def session_prompt(self, prompt):
        # Simulate user input
        return "/help"
    def run_once(self, line):
        # Capture output for test
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        self.handle_slash_command(line)
        out = sys.stdout.getvalue()
        sys.stdout = old_stdout
        return out

def test_help_command():
    shell = DummyShell()
    output = shell.run_once("/help")
    assert "Available commands" in output
    assert "/model-list" in output

def test_unknown_command():
    shell = DummyShell()
    output = shell.run_once("/unknown")
    assert "Unknown or incomplete command" in output
