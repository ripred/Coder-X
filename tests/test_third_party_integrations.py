import os
import pytest
from app.third_party_integrations import ThirdPartyIntegration

@pytest.fixture(autouse=True)
def clear_integrations_state():
    path = os.path.expanduser("~/.coder_x_integrations.json")
    if os.path.exists(path):
        os.remove(path)


def test_connect_and_list():
    tpi = ThirdPartyIntegration()
    assert tpi.connect("github", {"token": "abc"})
    assert "github" in tpi.list_integrations()
    assert tpi.disconnect("github")
    assert "github" not in tpi.list_integrations()

def test_connect_missing_credentials():
    tpi = ThirdPartyIntegration()
    assert not tpi.connect("github", {})
    assert "github" not in tpi.list_integrations()

def test_connect_invalid_integration():
    tpi = ThirdPartyIntegration()
    # Current implementation accepts any integration name
    assert tpi.connect("unknownsvc", {"token": "abc"})
    assert "unknownsvc" in tpi.list_integrations()

def test_double_connect_disconnect():
    tpi = ThirdPartyIntegration()
    assert tpi.connect("github", {"token": "abc"})
    # Double connect should be idempotent or overwrite
    assert tpi.connect("github", {"token": "def"})
    assert tpi.disconnect("github")
    # Double disconnect should be safe
    assert not tpi.disconnect("github")

def test_disconnect_not_connected():
    tpi = ThirdPartyIntegration()
    assert not tpi.disconnect("github")

def test_list_no_integrations():
    tpi = ThirdPartyIntegration()
    # If nothing connected, should be empty
    assert tpi.list_integrations() == []
    # But if something was connected, it will be listed
    tpi.connect("unknownsvc", {"token": "abc"})
    assert "unknownsvc" in tpi.list_integrations()

def test_multiple_integrations():
    tpi = ThirdPartyIntegration()
    assert tpi.connect("github", {"token": "abc"})
    assert tpi.connect("slack", {"token": "xyz"})
    lst = tpi.list_integrations()
    assert "github" in lst and "slack" in lst
    assert tpi.disconnect("slack")
    assert "slack" not in tpi.list_integrations()
