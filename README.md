# Coder-X Python Agentic Coding Assistant

**Project Status (as of 2025-04-16):**
- All core features implemented, tested, and documented
- All tests pass (pytest, 159 tests)
- Code coverage: 81% (see plan.md for details)
- SessionHistory, config, and file operations are robust and fully covered by tests
- Documentation is up to date in plan.md and architecture_and_maintenance.md
- No outstanding bugs or failing tests

A Python Agentic Coding Assistant with CLI, supporting configuration management, model management, and secure shell/file operations.

## Workflow Discipline

This project adheres to a strict workflow discipline to ensure maintainability, reliability, and quality:

* Always keep documentation up to date with the latest changes and features.
* Always require and run tests for every change, no matter how small.
* Always commit and push changes after all tests have passed.

## Features
- CLI and interactive shell (Typer-based)
- Powerful configuration management (CLI, prompts, and config files)
- Model management (local and remote, flexible storage path selection)
- Secure shell and file operations with full audit trail
- User and session management with export and clear history
- Secure CLI/API key encryption and storage
- Third-party integrations (e.g., GitHub, Ollama, etc.) with token management
- YAML and JSON config support
- MCP server integration for advanced workflows
- Automated testing and high code coverage discipline
- Extensible plugin and integration architecture

## Quickstart

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Run the Coder-X CLI:**
   ```sh
   python app/main.py
   ```

3. **Use the CLI:**
   ```sh
   python app/test_cli_new.py --help
   ```

## Testing

Run all tests:
```sh
pytest
```

## Project Structure
- `app/` — Main application code
- `tests/` — Tests for all modules
- `plan.md` — Project plan and progress
- `architecture_and_maintenance.md` — System architecture and maintenance docs

## Configuration
- Config is stored in JSON (default: `~/.coder_x_config.json`), validated and managed via a Pydantic V2 schema for safety and extensibility.
- Model storage path defaults to `~/.coder_x_models`
- All config options can be managed via robust CLI commands (`show`, `set`, `unset`, `setup`), with all output as structured JSON for scripting and testability.
- Comprehensive tests ensure config reliability and future extensibility.

## Model Management
- List, select, load, and unload models via CLI
- Dynamic loading/unloading of local LLMs using Ollama backend:
  - `coder-x model load <model_name>` to download/pull a model
  - `coder-x model unload <model_name>` to remove a model
- Model storage volume can be listed and set at runtime:
  - `coder-x model volumes` to list candidate storage locations
  - `coder-x model set-volume <path>` to set Ollama model storage directory
- See `architecture_and_maintenance.md` for backend and config details

## Environment Variables

| Variable                  | Default                             | Description                                      |
|---------------------------|-------------------------------------|--------------------------------------------------|
| `CODER_X_CONFIG`          | `~/.coder_x_config.json`            | Path to the main JSON config file                |
| `CODER_X_YAML_CONFIG`     | `~/.coder_x_config.yaml`            | Path to YAML config file (if used)               |
| `HOME`                    | System user home                    | Used for default config/model/history locations   |
| `PYTHONPATH`              | (set by tests)                      | Ensures correct module/package import            |
| `CODER_X_CONFIG`          | `~/.coder_x_config.json`            | Path to JSON config file                         |
| `CODER_X_HISTORY`         | `~/.coder_x_history.json`           | Path to session history file                     |
| `CODER_X_KEY`             | `~/.coder_x_key.enc`                | Encrypted CLI/API key file (see below).         |
| `OLLAMA_MODELS_CMD`       | `ollama list`                       | Command to list Ollama models (if used)          |

### Encrypted CLI/API Key Storage

Coder-X now supports secure encryption of CLI/API keys using industry-standard cryptography:
- **Encryption:** Uses PBKDF2HMAC key derivation and Fernet (AES) authenticated encryption.
- **Storage:** Encrypted secrets are stored in a binary file (default: `~/.coder_x_key.enc`).
- **Passphrase:** You must provide a passphrase (recommended: via environment variable or prompt) to encrypt/decrypt your secret.

**How to Use:**
- To save a new key: use the CLI or call `encrypt_secret()` from `app/key_encryption.py`, then store the resulting salt and token.
- To load a key: use `load_encrypted_secret()` and `decrypt_secret()` with your passphrase.

**Security Notes:**
- Your key is never stored in plain text.
- If you lose your passphrase, the encrypted key cannot be recovered—you must generate a new one.
- See `app/key_encryption.py` for code and usage examples.

*Most environment variables are optional; defaults are used if unset.*

---

For more, see `plan.md` and `architecture_and_maintenance.md`.
