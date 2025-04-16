# Coder-X Python Agentic Coding Assistant - Project Plan

---

## 🛑 Primary Project Rules & Workflow Discipline

**These rules MUST be followed for every feature, bugfix, and code change. They are non-negotiable and are critical for project health and AI-assist reliability.**

1. **Documentation & Tracking**
   - `plan.md`, `architecture_and_maintenance.md`, `requirements.txt`, and all other project, bug tracking, and feature tracking files MUST be kept up to date with every significant change or success.
   - When a feature or bug is completed, immediately update all relevant documentation and remove obsolete/completed issues from tracking files.
   - Never leave documentation or tracking out of sync with the actual codebase.

2. **Testing Discipline**
   - Every new feature, bugfix, or refactor MUST include at least one relevant unit test.
   - Unit tests must always exercise real, production code paths (not just mocks or stubs).
   - After any change, **run all unit tests** (not just the tests for the current feature) to ensure nothing is broken.
   - Do not proceed to the next step until all tests are passing at 100%.

3. **Commit & Push Policy**
   - Once all tests are passing after a change, immediately commit all changes locally and push to the remote repository.
   - Never leave uncommitted changes or failing tests in the working directory.

---

## Project Goal & Approach

**Goal:**  
Develop a Python-based, agentic coding assistant modeled after Anthropic's Claude Code. This tool will provide natural language coding assistance, codebase understanding, and workflow automation directly from the terminal. It will support both local and remote models (e.g., Ollama), allow user selection and configuration of models, support the Model Context Protocol (MCP), and enable flexible storage of models on any user-selected drive.

**Approach:**  
- Use Python with CLI for the backend.
- Implement a CLI and interactive shell for user interaction.
- Support model selection (local/remote) and configuration.
- Integrate with MCP for context/memory sharing.
- Allow secure key management.
- Enable model storage on any user-selected location (internal or external drives).
- Modular, extensible, and well-documented codebase.

---

### Claude Code Parity & Feature Comparison

**Current Status:**
- Coder-X implements the core features of Claude Code: interactive CLI, one-off queries, scriptable output, unified configuration, model selection, session/history management, and secure key management.
- Documentation, onboarding, and test coverage are strong.

**Notable Parity Achievements:**
- Interactive REPL and scripting
- Unified config management (Pydantic, Typer)
- Model selection/configuration (Ollama/local/remote)
- Session/history and secure key management
- Modular, extensible subsystems
- Project initialization and onboarding docs

**Partial or Missing Features (Compared to Claude Code):**
- Slash command system (e.g., /clear, /doctor, /help, etc.)
- Full Model Context Protocol (MCP) integration
- Usage/cost tracking and reporting
- Health check/doctor command
- Bug reporting from CLI
- Project initialization as a command (/init)
- Memory file editing via CLI
- PR/comments/code review integration
- Terminal/editor integration (key bindings, vim mode)
- Auto-update mechanism

---

### Roadmap to Full Parity

To match the full feature set and experience of Claude Code, prioritize:
1. Implementing a robust slash command system for in-session runtime actions.
2. Completing MCP integration for project/user/global memory sharing.
3. Adding usage/cost tracking and reporting.
4. Introducing a health check/doctor CLI command.
5. Enabling bug reporting from the CLI.
6. Creating a project initialization command (/init) for onboarding.
7. Supporting memory file editing through the CLI.
8. Integrating with PR/comments and code review tools.
9. Adding terminal/editor integration features.
10. Providing an update mechanism for Coder-X.

---

**Summary:**  
Coder-X is well on its way to achieving parity with Anthropic's Claude Code, with all core features implemented and a clear roadmap for closing remaining gaps. This plan ensures Coder-X remains robust, user-friendly, and competitive as an agentic coding assistant.

---

## Features

- **CLI and Interactive Shell**: Natural language and slash command interface.
- **Model Management**: List, select, load, and switch models (local/remote).
- **Model Storage Location**: User can specify any directory for local model storage.
- **Key Management**: Secure storage, update, and retrieval of keys.
- **MCP Protocol Support**: Integration with MCP servers for context and memory.
- **File Operations**: Edit, explain, test, and lint code files.
- **Shell Command Integration**: Securely run shell commands from within the tool.
- **Configuration Management**: Load/save config files, support all settings via CLI and shell.
- **Session/History Management**: Track, display, clear, and export conversations and actions.
- **User Management**: Show user info, manage authentication.
- **Feedback/Telemetry**: Collect/send feedback, optionally send telemetry.
- **Third-Party Integrations**: Connect to VCS, cloud, or other services.

---

## Subsystems

1. **CLI & Interactive Shell**
2. **Model Management**
3. **Model Storage Location Management**
4. **Key Management**
5. **MCP Integration**
6. **File Operations**
7. **Shell Integration**
8. **Configuration Management**
9. **Session/History Management**
10. **User Management**
11. **Feedback/Telemetry**
12. **Third-Party Integrations**

---

## Task Breakdown

---

- Once tests pass, clean up the test code and update documentation as needed.

---

## Testing and Configuration Philosophy

- All tests must exercise real, production code paths (not just mocks or stubs).
- Features must work the same way at runtime and in tests—tests should not bypass or mock out core logic.
- Configuration loading and saving must be unified: the same config file must work identically in both runtime and test contexts.
- If the config loader or CLI/API code falls back to defaults or overwrites fields, this must be refactored so that valid files are always honored as-is.
- Coverage and test quality are prioritized over simply "passing" tests.

---

## Tracked Steps: In Progress


## Basic Features: Status Summary

All core features (model management, storage, shell integration, config, session/history, user management, MCP, key management, file operations) are now implemented, tested, and documented. Unit tests (see test_cli_new.py and other current tests) cover all validation and error-handling logic. Documentation is up to date in plan.md and architecture_and_maintenance.md. Legacy and redundant tests have been removed for clarity.

---

### 1. CLI & Interactive Shell
- [x] Implement CLI entrypoint (Typer-based)
- [x] Implement interactive shell (prompt_toolkit)
- [x] Add command parsing for CLI and slash commands  
  - [x] CLI command parsing (Typer)
  - [x] Slash command support (via interactive shell)
- [x] Implement help/version/config display

### 2. Model Management
- [x] List available models (local/remote)
- [x] Select model
- [x] Load/unload models dynamically (Ollama backend integration, real CLI commands: `model load/unload`, volume selection)
- [x] Integrate with Ollama for local models
- [x] Integrate with Anthropic API for Claude models (simulated/stubbed)
- [x] Support user-supplied keys for remote models

### 3. Model Storage Location Management
- [x] Add `model_storage_path` to config schema
- [x] Implement CLI flag (`--model-storage-path <path>`) and slash command (`/model-storage-path <path>`)
- [x] Validate user-supplied path (exists, writable, sufficient space)
- [x] Update model loading/saving logic to use storage path
- [x] Handle errors for unavailable/disconnected drives
- [x] Document feature in help/config

> **Note:** Validation for existence, writability, and free space is implemented and tested. Error handling for unavailable/disconnected drives is in place. Further improvements to output/UX are deferred until all basic features are complete.

### 4. Key Management
- [x] Securely prompt for/store keys (unit tests written)
- [x] Encrypt keys at rest (Fernet, unit tests written)
- [x] Retrieve and use keys for model requests (unit tests written)
- [x] Allow updating/removing keys (unit tests written)

### 5. MCP Integration
- [x] Integrate MCP protocol via official Python library (unit tests written)
- [x] Connect to MCP servers (configurable endpoint, unit tests written)
- [x] Fetch/send context and memory to MCP server (unit tests written)
- [x] Expose MCP settings in config and slash commands (unit tests written)
- [x] Integration test now uses a real public endpoint in a passive, read-only way and skips if unavailable, ensuring robust CI.

### 6. File Operations
- [x] Open, read, write, edit files
- [x] Explain code in a file
- [x] Run tests (pytest/unittest)
- [x] Lint code (flake8/pylint)
- [x] Track file changes/edits in session history

### 7. Shell Integration
- [x] Run shell commands securely
- [x] Capture/display output/errors
- [x] Block dangerous commands by default; prompt user for approval if such a command is requested (implemented and tested).

> **Note:** Output/UX improvements for shell integration deferred until all basic features are complete.
- [x] Restrict dangerous commands (configurable)

### 8. Configuration Management
- [x] Load/save config from file (JSON, YAML support planned, unit tests written)
- [x] Refactored config subsystem: now uses Pydantic V2 schema for robust validation and type safety.
- [x] CLI config commands (show, set, unset, setup) implemented as Typer group, all output is structured JSON for scripting and testability.
- [x] Robust config loading: handles empty/invalid files, always returns a valid config object.
- [x] All config commands and edge cases are covered by new tests in tests/test_config_cli.py.
- [x] Documentation and architecture updated to reflect new design.

### 9. Session/History Management
- [x] Store conversation/command history
- [x] Allow user to view, clear, export history

### 10. User Management
- [x] Display current user info
- [x] Support login/logout for remote APIs
- [x] UserManager is now a singleton for correct session state persistence (login/logout tests pass)

### 11. Feedback/Telemetry
- [x] All telemetry and feedback code and tests fully removed as required by user plan (no data is collected or sent)

### 12. Third-Party Integrations
- [x] Connect to external services (VCS, cloud, etc.)
- [x] Expose via `/connect` command

---

## Best Practices & Design Decisions

- Use Ollama for local models; fallback to `llama-cpp-python` or `transformers` if needed.
- Secure, encrypted key storage.
- Model storage location is user-configurable and can be any attached drive.
- All config changes available via CLI, shell, and config file.
- Modular code for easy extension and maintenance.

---

## Project-wide Testing Requirement

- **Every implementation step must include at least one unit test.**
- After each step and its associated test(s) are implemented, all unit tests must be run to:
  - Verify the new functionality is correct.
  - Ensure no existing functionality is broken (non-regression).
- The project will not proceed to the next step until all tests pass.
- **Before running any test that downloads or uses a local model, always prompt the user to select which volume to use for model storage to avoid disk space issues or using the wrong drive.**
- **Defer the implementation and testing of local model downloading/storage until after remote/free/no-API-key model functionality is implemented and tested successfully.**
- **For each section and step (and its unit test(s)), an accurate section must be added to architecture_and_maintenance.md describing how the step is accomplished. This document must be updated at the same rate as steps are implemented and tested.**
- **All code stubs (placeholders, stub functions/classes, and TODOs) must be fully implemented and tested before the project is considered complete. Stub removal is a tracked deliverable.**

---

## References & Research Links

- [Anthropic Claude Code Docs](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- [Ollama Python GitHub](https://github.com/ollama/ollama-python)
- [MCP Protocol](https://github.com/modelcontextprotocol/servers)
- [Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/)
- [CLI](https://fastapi.tiangolo.com/)
- [CLI](https://www.uvicorn.org/)

---

## Progress Tracking

- [x] CLI entrypoint (Typer-based, Coder-X branding, unit tests written)
- [x] Telemetry/feedback code and tests fully removed per user requirement
- [x] MCP integration test made robust, passive, and read-only for public endpoint
- [x] User management tests fixed by enforcing singleton state for UserManager
- [ ] Interactive shell (migrating to new CLI structure, unit tests pending)
- [ ] Model management
- [ ] Model storage location selection
- [x] Key management  
  - Created `app/key_management.py` for secure key storage, retrieval, and removal (with placeholder encryption).
  - **Stub removal required:** All placeholder encryption and stubbed methods must be fully implemented and tested before completion.
- [x] MCP integration  
  - Created `app/mcp_integration.py` for connecting to MCP servers, fetching and saving context/memory.
  - **Stub removal required:** All stubbed methods must be fully implemented and tested before completion.
- [x] File operations  
  - Created `app/file_operations.py` for reading, writing, appending, explaining, testing, and linting files (with stubs for model integration).
  - **Stub removal required:** All stubs for model integration must be implemented and tested before completion.
- [x] Shell integration  
  - Created `app/shell_integration.py` for running shell commands securely, with a configurable allowlist of safe commands.
- [ ] Config management (CLI editing and persistence, YAML/JSON selection, unit tests pending)
- [x] History/session management  
  - Created `app/session_history.py` for storing, viewing, clearing, and exporting conversation and command history.
- [x] User management  
  - Created `app/user_management.py` for displaying user info and stubs for login/logout (for remote APIs or future expansion).
  - **Stub removal required:** Login/logout stubs must be fully implemented and tested before completion.
- [x] Feedback/telemetry  
  - Created `app/feedback_telemetry.py` for collecting user feedback and stubs for telemetry (opt-in, to be implemented).
  - **Stub removal required:** Telemetry stubs must be fully implemented and tested before completion.
- [x] Third-party integrations  
  - Created `app/third_party_integrations.py` for connecting to external services (VCS, cloud, etc.), with connect/disconnect/list stubs.
  - **Stub removal required:** All stubbed methods must be fully implemented and tested before completion.

---

## Integration Testing Policy

- All integration/system tests (including those that generate, write, or execute code) **must** run in a temporary, isolated directory. Never run such tests in the user's real project, codebase, or home folder.
- This prevents accidental file creation, overwriting, or clutter in real user directories and is required for safety and reproducibility.
- Integration tests should always clean up after themselves and verify no files are left behind.

## Console Framing Refactor (Claude-style)

- [ ] Add 'rich' as a dependency for console UI.
- [ ] Refactor CLI to render all input/output inside a persistent frame using rich.
- [ ] Refactor interactive shell to use rich framing for all prompts and outputs.
- [ ] Add integration/system tests to ensure all shell/CLI output and input is always inside a frame.
- [ ] Document the framing behavior and test requirements in architecture_and_maintenance.md.
- [ ] Mark as required for all future features and output improvements.

## Remaining Steps for Project Completion

- [ ] Implement and test telemetry (remove stubs in `app/feedback_telemetry.py`)
- [ ] Implement and test third-party integrations (remove stubs in `app/third_party_integrations.py`)
- [ ] **Final audit:** Remove all stubs, placeholders, and TODOs; ensure 100% implementation and test coverage
- [ ] Plan and begin next-phase improvements (output/UX, new features, etc.)


---
