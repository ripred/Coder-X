"""
key_encryption.py
----------------
Secure encryption and decryption for CLI/API keys using best-practice cryptography.
Uses PBKDF2HMAC for key derivation and Fernet (AES) for authenticated encryption.

Usage:
    from app.key_encryption import encrypt_secret, decrypt_secret

    # To encrypt and save a secret:
    salt, token = encrypt_secret(secret, passphrase)
    # Save both salt and token (bytes) to disk

    # To load and decrypt a secret:
    secret = decrypt_secret(token, passphrase, salt)

Environment:
    - Requires 'cryptography' package.
    - Never store passphrase or derived key on disk.
"""
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

# Constants
KDF_ITERATIONS = 390_000  # NIST recommendation for PBKDF2
SALT_SIZE = 16  # 128 bits


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet key from password and salt using PBKDF2HMAC."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Fernet key is 32 bytes
        salt=salt,
        iterations=KDF_ITERATIONS,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_secret(secret: str, password: str) -> tuple[bytes, bytes]:
    """
    Encrypt a secret string with a password.
    Returns (salt, token) as bytes. Store both for decryption.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(secret.encode())
    return salt, token


def decrypt_secret(token: bytes, password: str, salt: bytes) -> str:
    """
    Decrypt a token (bytes) using password and salt.
    Returns the original secret string.
    Raises InvalidToken if password is wrong.
    """
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(token).decode()


# Example utility functions for file storage

def save_encrypted_secret(filepath: str, salt: bytes, token: bytes) -> None:
    """Save salt and token to a file (simple binary format)."""
    with open(filepath, "wb") as f:
        f.write(salt + token)


def load_encrypted_secret(filepath: str) -> tuple[bytes, bytes]:
    """
    Load salt and token from a file. Assumes salt is first 16 bytes.
    Raises ValueError if file is too short to contain a valid salt.
    """
    with open(filepath, "rb") as f:
        data = f.read()
    if len(data) < SALT_SIZE:
        raise ValueError(f"Encrypted secret file '{filepath}' is too short to contain a valid salt.")
    salt = data[:SALT_SIZE]
    token = data[SALT_SIZE:]
    return salt, token
