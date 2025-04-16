# Coder-X Python Assistant  
**Architecture & Maintenance Guide**

Welcome to the Coder-X codebase! This guide is designed for developers new to the project, providing a clear overview of core architecture, configuration, testing philosophy, and best practices for maintenance. Use this document as your primary reference for understanding how Coder-X works and how to contribute effectively.

---

## 1. Configuration Management

**Overview:**  
Coder-X uses a robust, type-safe configuration system based on [Pydantic V2](https://docs.pydantic.dev/2.0/) schemas. All configuration is validated and loaded through a single schema (`CoderXConfig`), ensuring consistency and reliability across the CLI, runtime, and tests.

**Key Features:**
- **Unified Config:** All config logic (loading, saving, validation) is centralized, so runtime and tests behave identically.
- **CLI Integration:** Configuration commands (`show`, `set`, `unset`, `setup`) are available via the CLI, implemented with [Typer](https://typer.tiangolo.com/). All CLI output is structured JSON, making scripting and automation easy.
- **Error Handling:** Empty or invalid config files are handled gracefully, always producing a valid config object or clear error.

**Best Practices for Developers:**
- Always use the real config loader in both code and tests—never bypass with mocks or stubs.
- When adding features, ensure config changes are reflected in both the schema and CLI.
- Add or update tests to cover new config edge cases and error handling.

**Environment Variables:**  
Coder-X supports advanced customization via environment variables. Defaults are safe, but you can override for custom deployments or testing:

| Variable                  | Default                             | Description                                      |
|---------------------------|-------------------------------------|--------------------------------------------------|
| `CODER_X_CONFIG`          | `~/.coder_x_config.json`            | Path to the main JSON config file                |
| `CODER_X_YAML_CONFIG`     | `~/.coder_x_config.yaml`            | Path to YAML config file (if used)               |
| `HOME`                    | System user home                    | Used for default config/model/history locations   |
| `CODER_X_HISTORY`         | `~/.coder_x_history.json`           | Path to session history file                     |
| `CODER_X_KEY`             | `~/.coder_x_key.enc`                | Encrypted CLI/API key file (see below).         |
| `OLLAMA_MODELS_CMD`       | `ollama list`                       | Command to list Ollama models (if used)          |


---

## Encrypted CLI/API Key Storage

- Coder-X uses `app/key_encryption.py` for secure storage of CLI key encryption system: CLI/API keys are encrypted using PBKDF2HMAC (SHA256, 390,000 iterations) for key derivation and Fernet (AES) for authenticated encryption. The implementation includes robust error handling for corrupted or invalid files, and comprehensive unit tests for all critical paths. Blank passphrases are allowed for onboarding, but future enforcement of non-empty passphrases is planned. salt are stored in a binary file (default: `~/.coder_x_key.enc`).
- Users must supply a passphrase to encrypt/decrypt secrets; if lost, the key cannot be recovered.
- All error cases (corrupted/short files, wrong passphrase) are handled with clear exceptions.

See the module and README for usage and security notes.

## 2. Testing Philosophy

**Core Principles:**
- All tests must exercise real, production code paths—not just mocks or stubs.
- Features must behave the same way at runtime and in tests; never bypass or patch out core logic in tests.
- Unified configuration: The same config file and loader logic are used everywhere.
- Prioritize thorough coverage and test quality over simply “passing” tests.

**Current Status:**
- All core features are covered by automated tests.
- As of 2025-04-16, all tests pass and code coverage is 81%.
- SessionHistory, configuration, and file operations are robustly tested.
- No known failing or skipped tests remain.
- Documentation is kept current with all code and test changes.

**Developer Checklist:**
- When adding or changing features, write at least one new unit test.
- After every change, update both this guide and plan.md to reflect the true state of the codebase.
- Integration tests should be robust to external server state and never modify external data.

---

## 3. Project Structure & Subsystems

Coder-X is organized into modular subsystems, each with clear responsibilities. Here’s a quick map:

- **CLI & Interactive Shell:**  
  - Entry point for all user commands (Typer-based CLI, prompt_toolkit shell).
  - Command parsing, help/version/config display.

- **Model Management:**  
  - List, select, load, and unload models (local and remote).
  - Ollama and Anthropic integration.
  - User-supplied key support.

- **Model Storage Location Management:**  
  - Configurable model storage path, validated for existence and permissions.

- **Key Management:**  
  - Secure storage and retrieval of API/CLI keys.

- **Session/History Management:**  
  - Tracks user sessions and command history.
  - Robust error handling for malformed or missing files.

- **File Operations:**  
  - Safe read/write/append operations, always using production code paths.

- **Shell Integration:**  
  - Secure execution of shell commands within the assistant.

- **Configuration Management:**  
  - Unified loader/saver, schema-based validation, CLI integration.

- **User Management:**  
  - User info display and authentication.

- **Feedback/Telemetry:**  
  - Collects user feedback (telemetry opt-in, to be implemented).

- **Third-Party Integrations:**  
  - Hooks for VCS, cloud, and other external services.

---

## 4. Maintenance Practices

- **Documentation:**  
  - All major code or test changes must be reflected in this guide and plan.md immediately.
  - Keep architecture_and_maintenance.md up to date for onboarding and design reference.

- **Testing Discipline:**  
  - Run the full test suite after every change.
  - Never leave failing or skipped tests in the codebase.

- **Committing & Pushing:**  
  - Always commit after reaching a passing, documented state.
  - Push changes upstream promptly to keep the team in sync.

---

## 5. Getting Started as a Developer

1. **Read this guide and plan.md** to understand the project’s architecture and workflow.
2. **Clone the repo and set up a Python virtual environment.**
3. **Install dependencies:**  
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the test suite:**  
   ```sh
   pytest --cov=app --cov-report=term-missing
   ```
5. **Explore the CLI:**  
   ```sh
   python -m app.cli --help
   ```
6. **Ready to develop!**  
   - When making changes, follow the testing and documentation practices outlined above.
   - For questions, refer to this guide or ask the team.

---

## Table of Contents

- [Configuration Management](#configuration-management)
- [Testing Philosophy](#testing-philosophy)
- [Project Structure & Subsystems](#project-structure--subsystems)
- [Maintenance Practices](#maintenance-practices)
- [Getting Started as a Developer](#getting-started-as-a-developer)

---

This guide is your roadmap to maintaining, extending, and confidently contributing to Coder-X. Welcome aboard!

- [CLI Key Management](#cli-key-management)
- [MCP Integration](#mcp-integration)
- [File Operations](#file-operations)
- [Shell Integration](#shell-integration)
- [Session/History Management](#sessionhistory-management)
- [User Management](#user-management)
- [Third-Party Integrations](#third-party-integrations)
- [CLI Endpoints](#cli-endpoints)
- [CLI/Interactive Shell](#cliinteractive-shell)
- [Testing](#testing)
- [Maintenance](#maintenance)

---

## Model Management
### Overview
Handles listing, selecting, loading, and unloading models from a user-defined storage location. Supports both local (Ollama) and remote models.

#### Dynamic Model Loading/Unloading and Volume Selection
- **Dynamic loading/unloading**: Models can be loaded (downloaded) and unloaded (removed) at runtime using the real Ollama backend. Use the CLI commands:
  - `coder-x model load <model_name>` to pull/download a model
  - `coder-x model unload <model_name>` to remove a model
- **Volume selection**: Model storage location can be listed and changed at runtime:
  - `coder-x model volumes` lists all candidate storage volumes (including external drives)
  - `coder-x model set-volume <path>` sets the Ollama model storage directory, updating config and symlinking as needed
- All storage changes are validated for existence, writability, and available space. Errors for unavailable/disconnected drives are handled gracefully.
- All features are covered by unit tests in `tests/test_model_management.py` (subprocess and filesystem operations are mocked for safety).

> **Note:** Further improvements to output and user experience for model storage will be addressed after all basic features are complete.

#### Implementation Steps
- **ModelManager class**: Implements listing, selecting, loading, unloading, and volume logic.
- **Unit Tests**: `tests/test_model_management.py` verifies all model management and volume operations.

---

## CLI Key Management
### Overview
Securely stores, retrieves, and removes CLI keys, with placeholder encryption.

#### Implementation Steps
- **API Key Functions**: `set_api_key`, `get_api_key`, `remove_api_key` in `app/api_key_management.py`.
- **Unit Tests**: `tests/test_api_key_management.py` covers all key operations.

---

## MCP Integration
### Overview
Integrates with Model Context Protocol (MCP) for context and memory management.

#### Implementation Steps
- **MCPClient class**: Handles server URL, context fetch/save in `app/mcp_integration.py`.
- **Integration Test**: Now uses a real public MCP server endpoint in a passive, read-only way. The test skips if the resource/server is unavailable, ensuring CI robustness and no side effects on remote data.

---

## File Operations
### Overview
Provides read, write, append, explain, test, and lint operations for files.

#### Implementation Steps
- **FileOps class**: Implements all file operations in `app/file_operations.py`.
- **Unit Tests**: `tests/test_file_operations.py` and CLI tests cover all endpoints and logic.

---

## Shell Integration
### Overview
Executes shell commands securely with an allowlist. Dangerous commands are blocked unless user permission is granted. User approval is prompted for dangerous commands, and this logic is covered by unit tests.

#### Implementation Steps
- **ShellIntegration class**: In `app/shell_integration.py`.

> **Note:** Further improvements to output and user experience for shell integration will be addressed after all basic features are complete.
- **Unit Tests**: `tests/test_shell_integration.py` and CLI tests.
- **User Permission**: System designed to prompt for explicit user approval for dangerous commands (e.g., `rm`).
- **CLI Workflow**: If the backend responds with a 'not allowed' error, the CLI:
  - Displays a strong security warning and highlights the irreversible nature of dangerous commands.
  - Requires the user to type the full word 'yes' to approve execution. Any other input aborts the command.
  - Logs all dangerous command approvals to `~/.claude_code_dangerous_shell.log` with a timestamp and command for auditability.

---

## Session/History Management
### Overview
Stores, views, clears, and exports command and conversation history.

#### Implementation Steps
- **SessionHistory class**: In `app/session_history.py`.
- **Unit Tests**: `tests/test_session_history.py` and CLI tests.

---

## User Management
### Overview
Displays user info and provides login/logout stubs.

#### Implementation Steps
- **UserManager class**: In `app/user_management.py`.
- **Unit Tests**: `tests/test_user_management.py` and CLI tests.

---

## Third-Party Integrations
### Overview
Manages connections to external services.

#### Implementation Steps
- **ThirdPartyIntegration class**: In `app/third_party_integrations.py`.
- **Unit Tests**: `tests/test_third_party_integrations.py`.

---

## CLI Endpoints
### Overview
All subsystems are exposed via CLI endpoints, with a router per subsystem.

#### Implementation Steps
- Each subsystem has a dedicated CLI router file (e.g., `*_api.py`).
- Unit tests for each endpoint.

---

## CLI/Interactive Shell
### Overview
The CLI provides an interactive terminal interface to all backend features, including model management, file operations, shell commands, history, user management, and integrations.

#### Implementation Steps
- **Command Parsing**: The CLI parses user input and maps commands to CLI calls.
- **Dangerous Shell Command Prompt**: When a shell command is disallowed by the backend, the CLI prompts the user for permission to proceed. If the user agrees, the command is resent with an override flag.
- **Unit Tests**: CLI tested via subprocess and integration tests in `tests/test_cli.py`.

---

## Testing

All core features are covered by automated tests. As of 2025-04-16, all tests pass and code coverage is 81%. SessionHistory, configuration, and file operations are robustly tested. No known failing or skipped tests remain. Documentation is current and reflects the state of the codebase.

- All new or updated features must have at least one unit test.
- After every code or test change, both plan.md and architecture_and_maintenance.md are updated immediately to reflect the true project state and design decisions.
- Integration tests that touch external services are always passive/read-only and robust to remote server state.
### Overview
Every step includes at least one unit test. All tests are run after each step.

#### Implementation Steps
- Tests are located in the `tests/` directory.
- All tests must pass before proceeding.
- Special care for disk-using tests (user selects volume).

---

## Maintenance
### Overview
This document and the plan are updated with every step. All architectural, implementation, and testing details are documented here.

#### Implementation Steps
- Each subsystem and test is described in its own section.
- This document is updated in lockstep with implementation and testing.
