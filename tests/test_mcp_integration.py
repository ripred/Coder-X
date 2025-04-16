import pytest
from app import mcp_integration

def test_mcpclient_set_server_url(tmp_path, monkeypatch):
    config = type('Config', (), {'mcp_server': None})()
    client = mcp_integration.MCPClient(config=config)
    called = {}
    def fake_save_config(cfg):
        called['url'] = cfg.mcp_server
    monkeypatch.setattr('app.config.save_config', fake_save_config)
    client.set_server_url('http://example.com')
    assert client.server_url == 'http://example.com'
    assert config.mcp_server == 'http://example.com'
    assert called['url'] == 'http://example.com'

def test_mcpclient_get_context_success(monkeypatch):
    client = mcp_integration.MCPClient(config=type('Config', (), {'mcp_server': 'http://test'})())
    class FakeResp:
        status_code = 200
        def json(self):
            return {'foo': 'bar'}
    def fake_get(url):
        assert url == 'http://test/context/abc'
        return FakeResp()
    monkeypatch.setattr(mcp_integration.requests, 'get', fake_get)
    result = client.get_context('abc')
    assert result == {'foo': 'bar'}

def test_mcpclient_get_context_no_server():
    client = mcp_integration.MCPClient(config=type('Config', (), {'mcp_server': None})())
    assert client.get_context('abc') is None

def test_mcpclient_get_context_error(monkeypatch):
    client = mcp_integration.MCPClient(config=type('Config', (), {'mcp_server': 'http://test'})())
    def fake_get(url):
        raise Exception('fail')
    monkeypatch.setattr(mcp_integration.requests, 'get', fake_get)
    assert client.get_context('abc') is None

def test_mcpclient_save_context_success(monkeypatch):
    client = mcp_integration.MCPClient(config=type('Config', (), {'mcp_server': 'http://test'})())
    class FakeResp:
        status_code = 200
    def fake_post(url, json):
        assert url == 'http://test/context/abc'
        assert json == {'foo': 'bar'}
        return FakeResp()
    monkeypatch.setattr(mcp_integration.requests, 'post', fake_post)
    assert client.save_context('abc', {'foo': 'bar'}) is True

def test_mcpclient_save_context_no_server():
    client = mcp_integration.MCPClient(config=type('Config', (), {'mcp_server': None})())
    assert client.save_context('abc', {'foo': 'bar'}) is False

def test_mcpclient_save_context_error(monkeypatch):
    client = mcp_integration.MCPClient(config=type('Config', (), {'mcp_server': 'http://test'})())
    def fake_post(url, json):
        raise Exception('fail')
    monkeypatch.setattr(mcp_integration.requests, 'post', fake_post)
    assert client.save_context('abc', {'foo': 'bar'}) is False
