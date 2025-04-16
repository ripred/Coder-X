import os
import tempfile
from app import model_management
ModelManager = model_management.ModelManager
from app.config import save_config, load_config

def test_list_local_models(monkeypatch, tmp_path):
    from app.config_schema import CoderXConfig
    # Create fake model files
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "llama.bin").write_text("fake model")
    (model_dir / "mistral.gguf").write_text("fake model")
    config_path = tmp_path / "coderx_config.json"
    monkeypatch.setenv("CODER_X_CONFIG", str(config_path))
    config = CoderXConfig(model_storage_path=str(model_dir))
    save_config(config, str(config_path))
    mm = ModelManager(config)
    models = mm.list_local_models()
    assert "llama.bin" in models
    assert "mistral.gguf" in models

def test_set_and_get_active_model(monkeypatch, tmp_path):
    from app.config_schema import CoderXConfig
    config_path = tmp_path / "coderx_config.json"
    monkeypatch.setenv("CODER_X_CONFIG", str(config_path))
    config = CoderXConfig()
    save_config(config, str(config_path))
    mm = ModelManager(config)
    mm.set_active_model("llama3")
    assert mm.get_active_model() == "llama3"
    mm.set_active_model("mistral")
    assert mm.get_active_model() == "mistral"

def test_set_model_storage_path(monkeypatch, tmp_path):
    from app.config_schema import CoderXConfig
    config_path = tmp_path / "coderx_config.json"
    monkeypatch.setenv("CODER_X_CONFIG", str(config_path))
    config = CoderXConfig()
    save_config(config, str(config_path))
    mm = ModelManager(config)
    new_path = str(tmp_path / "new_models")
    mm.set_model_storage_path(new_path)
    assert os.path.exists(new_path)
    assert mm.storage_path == new_path

from unittest import mock
import errno

# --- Additional edge/error case tests ---
def test_list_ollama_models_error(monkeypatch):
    mm = ModelManager()
    # Simulate subprocess.run raising
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")))
    assert mm.list_ollama_models() == []
    # Simulate subprocess.run returning bad output
    class DummyResult:
        stdout = "bad\noutput"
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    assert mm.list_ollama_models() == ["output"]

def test_load_model_ollama_nonzero(monkeypatch):
    mm = ModelManager()
    class DummyResult:
        returncode = 1
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    assert not mm.load_model_ollama("foo")

def test_unload_model_ollama_nonzero(monkeypatch):
    mm = ModelManager()
    class DummyResult:
        returncode = 1
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    assert not mm.unload_model_ollama("foo")

def test_list_ollama_volumes_edge(monkeypatch, tmp_path):
    mm = ModelManager()
    # Simulate no extra volumes
    monkeypatch.setattr("os.path.exists", lambda p: False)
    vols = mm.list_ollama_volumes()
    assert isinstance(vols, list)
    # Simulate all mount directories exist but are empty
    monkeypatch.setattr("os.path.exists", lambda p: True)
    monkeypatch.setattr("os.listdir", lambda p: [])
    vols = mm.list_ollama_volumes()
    assert isinstance(vols, list)

def test_set_active_model_minimal_config(monkeypatch):
    class DummyConf:
        model_storage_path = "/tmp"
    mm = ModelManager(DummyConf())
    monkeypatch.setattr("app.model_management.set_config_key", lambda c, k, v: c)
    monkeypatch.setattr("app.config.save_config", lambda c: None)
    mm.set_active_model("foo")
    assert hasattr(mm, "config")

def test_set_model_storage_path_minimal(monkeypatch, tmp_path):
    mm = ModelManager()
    p = str(tmp_path / "new")
    monkeypatch.setattr("os.path.exists", lambda path: False)
    monkeypatch.setattr("os.makedirs", lambda path, exist_ok: None)
    monkeypatch.setattr("os.access", lambda path, mode: True)
    class DummyDU: total=10**12; used=0; free=10**12
    import shutil
    monkeypatch.setattr(shutil, "disk_usage", lambda path: (DummyDU.total, DummyDU.used, DummyDU.free))
    monkeypatch.setattr("app.model_management.set_config_key", lambda c, k, v: c)
    monkeypatch.setattr("app.config.save_config", lambda c: None)
    mm.set_model_storage_path(p)

# --- Additional tests for storage path validation ---
def test_set_model_storage_path_non_writable(tmp_path):
    mm = ModelManager()
    new_path = str(tmp_path / "non_writable")
    os.makedirs(new_path)
    with mock.patch("os.access", return_value=False):
        try:
            mm.set_model_storage_path(new_path)
        except Exception as e:
            assert "writable" in str(e) or "permission" in str(e).lower()
        else:
            assert False, "Should raise error for non-writable path"

def test_set_model_storage_path_insufficient_space(tmp_path):
    mm = ModelManager()
    new_path = str(tmp_path / "no_space")
    os.makedirs(new_path)
    # Simulate <1GB free
    with mock.patch("shutil.disk_usage", return_value=(10**12, 10**12-500, 500)), \
         mock.patch("os.access", return_value=True):
        try:
            mm.set_model_storage_path(new_path)
        except Exception as e:
            assert "Insufficient disk space" in str(e)
        else:
            assert False, "Should raise error for insufficient disk space"

def test_set_model_storage_path_usage_error(tmp_path):
    mm = ModelManager()
    new_path = str(tmp_path / "err_usage")
    os.makedirs(new_path)
    with mock.patch("shutil.disk_usage", side_effect=OSError("fail")), \
         mock.patch("os.access", return_value=True):
        try:
            mm.set_model_storage_path(new_path)
        except Exception as e:
            assert "Could not determine disk usage" in str(e)
        else:
            assert False, "Should raise error for disk usage failure"

def test_list_local_models_mixed(tmp_path):
    from app.config_schema import CoderXConfig
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "llama.bin").write_text("fake model")
    (model_dir / "README.md").write_text("not a model")
    (model_dir / "nested").mkdir()
    config = CoderXConfig(model_storage_path=str(model_dir))
    mm = ModelManager(config)
    models = mm.list_local_models()
    assert "llama.bin" in models
    assert "nested" in models
    assert "README.md" not in models

def test_load_model_ollama_error(monkeypatch):
    mm = ModelManager()
    def fake_run(*a, **kw):
        raise Exception("fail")
    monkeypatch.setattr("subprocess.run", fake_run)
    assert not mm.load_model_ollama("badmodel")

def test_unload_model_ollama_error(monkeypatch):
    mm = ModelManager()
    def fake_run(*a, **kw):
        raise Exception("fail")
    monkeypatch.setattr("subprocess.run", fake_run)
    assert not mm.unload_model_ollama("badmodel")

def test_set_active_model_invalid(monkeypatch, tmp_path):
    from app.config_schema import CoderXConfig
    config_path = tmp_path / "coderx_config.json"
    monkeypatch.setenv("CODER_X_CONFIG", str(config_path))
    config = CoderXConfig()
    save_config(config, str(config_path))
    mm = ModelManager(config)
    # Should not raise, just set an arbitrary name
    mm.set_active_model("")
    assert mm.get_active_model() == ""
    mm.set_active_model(None)
    assert mm.get_active_model() is None

def test_set_model_storage_path_insufficient_space(tmp_path):
    mm = ModelManager()
    new_path = str(tmp_path / "no_space")
    os.makedirs(new_path)
    # Simulate insufficient space by patching shutil.disk_usage
    with mock.patch("shutil.disk_usage", return_value=(100, 100, 0)):
        try:
            mm.set_model_storage_path(new_path)
        except Exception as e:
            assert "space" in str(e).lower()
        else:
            assert False, "Should raise error for insufficient disk space"

def test_set_model_storage_path_unavailable_drive():
    mm = ModelManager()
    # Simulate unavailable drive by patching os.path.exists to return False
    fake_path = "/mnt/disconnected_drive/models"
    with mock.patch("os.path.exists", return_value=False):
        with mock.patch("os.makedirs", side_effect=OSError(errno.ENOENT, "No such file or directory")):
            try:
                mm.set_model_storage_path(fake_path)
            except Exception as e:
                assert "unavailable" in str(e).lower() or "no such file" in str(e).lower()
            else:
                assert False, "Should raise error for unavailable/disconnected drive"

from unittest import mock

def test_load_model_ollama():
    mm = ModelManager()
    with mock.patch("subprocess.run") as m:
        m.return_value.returncode = 0
        assert mm.load_model_ollama("llama2")
        m.assert_called_with(["ollama", "pull", "llama2"], capture_output=True, text=True, check=True)

def test_unload_model_ollama():
    mm = ModelManager()
    with mock.patch("subprocess.run") as m:
        m.return_value.returncode = 0
        assert mm.unload_model_ollama("llama2")
        m.assert_called_with(["ollama", "rm", "llama2"], capture_output=True, text=True, check=True)

def test_list_ollama_volumes(tmp_path):
    mm = ModelManager()
    vols = mm.list_ollama_volumes()
    assert any(".ollama/models" in v for v in vols)

def test_set_ollama_volume(tmp_path):
    mm = ModelManager()
    path = str(tmp_path / "ollama_vol")
    with mock.patch("os.symlink") as symlink, \
         mock.patch("os.path.islink", return_value=False), \
         mock.patch("os.path.exists", return_value=False), \
         mock.patch("os.makedirs") as makedirs, \
         mock.patch("shutil.move") as move, \
         mock.patch("os.access", return_value=True), \
         mock.patch("shutil.disk_usage", return_value=(10**12, 10**11, 10**12)):
        assert mm.set_ollama_volume(path)
        symlink.assert_called()
        makedirs.assert_called()
