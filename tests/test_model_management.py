import os
import tempfile
from app.model_management import ModelManager
from app.config import save_config, load_config

def test_list_local_models(tmp_path):
    # Create fake model files
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "llama.bin").write_text("fake model")
    (model_dir / "mistral.gguf").write_text("fake model")
    config = load_config()
    config["model_storage_path"] = str(model_dir)
    save_config(config)
    mm = ModelManager(config)
    models = mm.list_local_models()
    assert "llama.bin" in models
    assert "mistral.gguf" in models

def test_set_and_get_active_model(tmp_path):
    config = load_config()
    mm = ModelManager(config)
    mm.set_active_model("llama3")
    assert mm.get_active_model() == "llama3"
    mm.set_active_model("mistral")
    assert mm.get_active_model() == "mistral"

def test_set_model_storage_path(tmp_path):
    mm = ModelManager()
    new_path = str(tmp_path / "new_models")
    mm.set_model_storage_path(new_path)
    assert os.path.exists(new_path)
    assert mm.storage_path == new_path

from unittest import mock
import errno

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
