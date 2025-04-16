# Coder-X Python Assistant

## Architecture and Maintenance

### Configuration Management
- **2025-04-15: CLI config subsystem refactored for robustness and extensibility.**
- Now uses a Pydantic V2 schema (`CoderXConfig`) for all config validation and IO, ensuring type safety and future-proofing.
- CLI config commands (`show`, `set`, `unset`, `setup`) are implemented as a Typer group. All output is structured JSON for scripting and testability.
- Config loading is robust: empty or invalid files are handled gracefully, always returning a valid config object.
- All config commands and edge cases are covered by comprehensive tests in `tests/test_config_cli.py`.

#### Unified Configuration and Testing Philosophy
- **Goal:** Ensure that the configuration loader, saver, and schema work identically in both runtime and testing contexts, with no silent fallback to defaults or overwriting of user/test values.
- Coverage and correctness are prioritized over "passing" tests.

#### Maintenance/Tracking
- **Next Steps:**
  - Update/add tests to assert error handling and round-trip.
  - Ensure all features use the real config logic in both runtime and testing.

#### Environment Variables

| Variable                  | Default                             | Description                                      |
|---------------------------|-------------------------------------|--------------------------------------------------|
| `CLAUDE_CODE_CONFIG`      | `~/.coder_x_config.json`            | Path to the main JSON config file                |
| `CODER_X_YAML_CONFIG`     | `~/.coder_x_config.yaml`            | Path to YAML config file (if used)               |
| `HOME`                    | System user home                    | Used for default config/model/history locations   |
| `CLAUDE_CODE_HISTORY`     | `~/.coder_x_history.json`           | Path to session history file                     |
| `CLAUDE_CODE_KEY`         | `~/.coder_x_key`                    | Path to encryption key for CLI keys              |
| `OLLAMA_MODELS_CMD`       | `ollama list`                       | Command to list Ollama models (if used)          |

These environment variables allow advanced users and deployers to customize configuration, model management, and security. Most are optional and have safe defaults.

This document provides a detailed, step-by-step breakdown of the architecture, implementation, and maintenance practices for each subsystem and feature of the Coder-X Python Assistant. It is updated in lockstep with development and testing.

---

## Table of Contents
- [Model Management](#model-management)
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
