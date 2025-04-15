from app.user_management import UserManager

def test_get_current_user():
    um = UserManager()
    user = um.get_current_user()
    assert "username" in user
    assert "home" in user

def test_login_logout():
    um = UserManager()
    # Ollama login/logout with token
    assert um.login("ollama", token="abc123")
    assert um.logout("ollama")
    # Unknown service raises
    try:
        um.login("unknownsvc")
        assert False, "Should raise ValueError for unknown service"
    except ValueError:
        pass
