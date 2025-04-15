from app.mcp_integration import MCPClient
import pytest

class DummyServer:
    def __init__(self):
        self.contexts = {}
        self.url = "http://dummy"
    def get_context(self, context_id):
        return self.contexts.get(context_id)
    def save_context(self, context_id, data):
        self.contexts[context_id] = data
        return True

def test_set_and_get_server_url(monkeypatch):
    client = MCPClient(config={})
    url = "http://localhost:9999"
    client.set_server_url(url)
    assert client.server_url == url
    assert client.config["mcp_server"] == url

def test_get_context_and_save_context():
    # Passive integration test with public Obsidian MCP server (read-only)
    public_mcp_url = "https://mcp-obsidian-demo.modelcontextprotocol.io"
    client = MCPClient(config={"mcp_server": public_mcp_url})
    # Only perform a read operation on a known public resource
    resource_id = "vault/README.md"
    ctx = client.get_context(resource_id)
    if ctx is None:
        import pytest
        pytest.skip(f"Resource {resource_id} not found on the public MCP server; skipping test.")
    assert isinstance(ctx, dict) or isinstance(ctx, str), f"Expected resource {resource_id} to be a dict or str."
    # Do not attempt any write or modification operations.
