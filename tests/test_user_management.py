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

def test_coderx_login_logout():
    um = UserManager()
    # coder-x login requires token
    try:
        um.login("coder-x")
        assert False, "Should raise ValueError if token missing"
    except ValueError:
        pass
    # Valid login/logout
    assert um.login("coder-x", token="tok123")
    assert um.logout("coder-x")

def test_double_login_logout():
    um = UserManager()
    assert um.login("ollama", token="tok1")
    # Second login should overwrite
    assert um.login("ollama", token="tok2")
    assert um.logout("ollama")
    # Logout when not logged in returns False
    assert not um.logout("ollama")

def test_multiple_services():
    um = UserManager()
    assert um.login("ollama", token="tok1")
    assert um.login("coder-x", token="tok2")
    assert um.logout("ollama")
    assert um.logout("coder-x")
    # After logout, can't logout again
    assert not um.logout("coder-x")
