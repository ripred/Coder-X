import os
import tempfile
import pytest
from app import key_encryption
from cryptography.fernet import InvalidToken

def test_encrypt_decrypt_roundtrip():
    secret = "super_secret_api_key"
    password = "correct horse battery staple"
    salt, token = key_encryption.encrypt_secret(secret, password)
    # Decrypt with correct password
    decrypted = key_encryption.decrypt_secret(token, password, salt)
    assert decrypted == secret


def test_wrong_password_raises():
    secret = "another_secret"
    password = "rightpass"
    wrong = "wrongpass"
    salt, token = key_encryption.encrypt_secret(secret, password)
    # Decrypt with wrong password should fail
    with pytest.raises(InvalidToken):
        key_encryption.decrypt_secret(token, wrong, salt)


def test_save_and_load_encrypted_secret(tmp_path):
    secret = "persisted_secret"
    password = "persistpass"
    salt, token = key_encryption.encrypt_secret(secret, password)
    file_path = tmp_path / "enc_secret.bin"
    key_encryption.save_encrypted_secret(str(file_path), salt, token)
    loaded_salt, loaded_token = key_encryption.load_encrypted_secret(str(file_path))
    assert loaded_salt == salt
    assert loaded_token == token
    decrypted = key_encryption.decrypt_secret(loaded_token, password, loaded_salt)
    assert decrypted == secret


def test_encrypts_differently_each_time():
    secret = "same_secret"
    password = "samepass"
    # Encrypt twice, should get different salt/token
    salt1, token1 = key_encryption.encrypt_secret(secret, password)
    salt2, token2 = key_encryption.encrypt_secret(secret, password)
    assert salt1 != salt2 or token1 != token2  # At least one must differ


def test_invalid_file_load(tmp_path):
    # File too short
    file_path = tmp_path / "shortfile.bin"
    with open(file_path, "wb") as f:
        f.write(b"123")
    # Should raise ValueError due to file being too short for a valid salt
    with pytest.raises(ValueError):
        key_encryption.load_encrypted_secret(str(file_path))
