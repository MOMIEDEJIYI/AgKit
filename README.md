# Agent
[English](README.md) | [Chinese](README.zh.md)

An intelligent agent framework with a **plugin system**, supporting both **CLI** and **GUI** modes.

## Features

| Module            | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| **Conversation**  | - Multi-turn dialogue context management   - CLI / GUI support   - Switchable LLM providers (OpenAI, Gemini, DeepSeek) |
| **Plugin System** | Pluggable architecture, supporting extensions like file operations |
| **GUI**           | - Chat window (bubble-style)   - Toolbar (method snapshot, navigation, title bar)   - Settings panel (model, conversation, voice) |
| **API Service**   | - FastAPI-based chat interface   - Support for conversation creation and management |

## Roadmap

| Module           | Planned Features                                             |
| ---------------- | ------------------------------------------------------------ |
| **Cluster Mode** | Multi-agent collaboration: each node focuses on specialized capabilities (distributed scheduling) |
| **Plugins**      | Database operations, automation tasks, external service integration |
| **Models**       | Support for more LLMs (Claude, Llama, Qwen, etc.)            |
| **Multimodal**   | Voice input/output, image & file parsing                     |

------

## Quick Start

### 1. Setup

Make sure you have **Python 3.10+** installed (recommended: use conda for environment management):

```
pip install -r requirements.txt
```

Configure your API key in `config.json`:

- `provider` supports: `deepseek`, `gemini`, `openai`

------

### 2. Run

- Start in **CLI mode**:

```
python main_cli.py
```

- Start in **GUI mode**:

```
python main_gui.py
```

------

### 3. Project Structure

```
├─agent/            # Core agent modules (dialogue, task scheduling, RPC)
├─api/              # FastAPI routes (chat / session APIs)
├─assets/           # UI styles (QSS)
├─common/           # Shared modules (error codes, etc.)
├─model/            # Data models (Pydantic schemas)
├─plugins/          # Plugin modules (command exec, reports, file ops, etc.)
├─ui/               # GUI (PyQt components & windows)
├─utils/            # Utility functions
│
├─config.json       # Default config
├─main_cli.py       # CLI entry
├─main_gui.py       # GUI entry
├─requirements.txt  # Dependencies
└─README.md
```

------

### 4. Plugins

To add a plugin:

1. Create a new folder under `plugins/` (acts as a module).
2. Add an `__init__.py` file to mark it as a package.
3. Implement your logic in a `.py` file and expose methods with `@register_method`.
4. Once loaded, confirm the registration in the runtime method snapshot.

`@register_method` supports:

| Field            | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| name             | Method name (required)                                       |
| param_desc       | Parameter description (required, use `param=None` if no params) |
| description      | Usage description (required, helps LLM understand intent)    |
| needs_nlg        | Whether this requires a secondary model reply (default: `false`) |
| tool_result_wrap | Whether to include RPC results in the return payload (default: `false`) |

------

### 5. Built-in Plugins

| Package | Description       | Verified | Notes                                                        |
| ------- | ----------------- | -------- | ------------------------------------------------------------ |
| exec    | Command execution | ❌        | Run local commands (e.g. pip install). Security risks apply. |
| network | HTTP requests     | ❌        | Supports HTTP/HTTPS. Proxy/timeout not fully tested.         |
| report  | Report example    | ✅        | Sample plugin, generates demo results.                       |
| system  | File operations   | ✅        | Read/write/create/delete local files. Use inside safe directories. |

------

### ⚠️ Notes

- Some plugins (`exec`, `system`) have **security risks**.
- `exec` requires existing system commands (`pip`, `ls`, etc.).
- `network` is not fully tested.
- Always ensure plugin prompts and parameters are correct before use.
