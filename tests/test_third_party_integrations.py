from app.third_party_integrations import ThirdPartyIntegration

def test_connect_and_list():
    tpi = ThirdPartyIntegration()
    assert tpi.connect("github", {"token": "abc"})
    assert "github" in tpi.list_integrations()
    assert tpi.disconnect("github")
    assert "github" not in tpi.list_integrations()
