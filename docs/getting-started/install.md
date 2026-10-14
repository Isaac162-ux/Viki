# ViKi Installation Guide

> **Based on Viki** — ViKi inherits the same installation process with rebranded commands and paths.

---

## Quick Install

Pick your platform and run one command. Each installer handles [uv](https://docs.astral.sh/uv/), the Python venv, Ollama, and a starter model — about 3 minutes on broadband.

| Platform | One-liner |
|---|---|
| **macOS · Linux · WSL2** | `curl -fsSL https://open-viki.github.io/Viki/install.sh \| bash` |
| **Native Windows** | `irm https://open-viki.github.io/Viki/install.ps1 \| iex` |
| **Desktop GUI** | Download `.exe` / `.dmg` / `.deb` / `.rpm` / `.AppImage` from the [latest release](https://github.com/open-viki/Viki/releases) |

Then `viki` to start. The Rust extension and larger models continue downloading in the background; `viki doctor` shows status.

> **Note**: The installers still use the Viki URLs and branding. ViKi-specific installers will be available in a future release.

Platform-specific notes (WSL2 setup, native-Windows scheduled-task service, desktop prerequisites, manual / contributor install): see the [installation docs](https://open-viki.github.io/Viki/getting-started/install/).

---

## Quick Start

```bash
viki                          # start chatting (default: chat-simple)
viki gui                      # start the holographic browser interface
viki init --preset <name> --force  # replace config with a starter preset
```

`viki gui` starts the local API server and frontend, then opens the holographic chat interface in your default browser. It requires Node.js 22+ and is available from a source checkout; packaged desktop installers are available from the [latest release](https://github.com/open-viki/Viki/releases).

> Prefix `viki ...` with `uv run`, or `source .venv/bin/activate` first.

| Preset | What it does |
|---|---|
| `morning-digest-mac` / `morning-digest-linux` / `morning-digest-minimal` | Spoken daily briefing from email, calendar, health, news |
| `deep-research` | Multi-hop research across indexed docs with citations |
| `code-assistant` | Agent with code execution, file I/O, and shell access |
| `scheduled-monitor` | Stateful agent on a schedule with memory |
| `chat-simple` | Lightweight conversation, no tools |

Example:

```bash
viki init --preset morning-digest-mac --force
viki connect gdrive          # one OAuth covers Gmail / Calendar / Tasks
viki digest --fresh          # generate and play your first briefing
```

Per-preset deep dives: [morning digest](https://open-viki.github.io/Viki/user-guide/morning-digest/) · [deep research](https://open-viki.github.io/Viki/user-guide/deep-research/) · [code assistant](https://open-viki.github.io/Viki/user-guide/code-assistant/) · [scheduled monitor](https://open-viki.github.io/Viki/user-guide/scheduled-monitor/) · [chat simple](https://open-viki.github.io/Viki/user-guide/chat-simple/) · or the full [quickstart guide](https://open-viki.github.io/Viki/getting-started/quickstart/).

---

## System Requirements

- **Python**: 3.10 – 3.14 (3.14+ supported)
- **Ollama**: For local model inference (installed automatically)
- **Node.js**: 22+ (for `viki gui` / desktop app)
- **uv**: Fast Python package manager (installed automatically)
- **Rust**: 1.89+ (for desktop app compilation, installed automatically)
- **Disk Space**: ~5 GB for models and dependencies
- **RAM**: 8 GB minimum (16 GB+ recommended for larger models)

### Platform Support

| Platform | Status | Notes |
|---|---|---|
| macOS (Apple Silicon) | ✅ Full support | Best performance with MLX/Metal |
| macOS (Intel) | ✅ Full support | Requires Rosetta for some binaries |
| Linux (x86_64) | ✅ Full support | CUDA/ROCm for GPU acceleration |
| Linux (ARM64) | ✅ Full support | Raspberry Pi 4+, Jetson |
| Windows (x64) | ✅ Full support | Native, no WSL required |
| WSL2 | ✅ Full support | Use Linux installer inside WSL2 |

---

## Manual Installation (Contributor / Advanced)

If you prefer not to use the one-liner, or want to contribute:

```bash
git clone https://github.com/open-viki/Viki.git
cd Viki
uv sync --extra dev
uv run pre-commit install
uv run pytest tests/ -v
```

### Desktop App Development

```bash
cd frontend
npm install
npm run tauri dev
```

### Running Tests

```bash
# Core tests (fast)
uv run pytest tests/core/ -v

# Integration tests (require Ollama + models)
uv run pytest tests/integration/ -v

# All tests
uv run pytest tests/ -v
```

---

## Configuration

ViKi stores all runtime state (config, databases, caches, logs, credentials, skills, recipes) under a single directory:

- **Default**: `~/.viki` (was `~/.viki`)
- **Override**: Set `VIKI_HOME` environment variable
- **XDG**: Uses `$XDG_DATA_HOME/viki` if set

The main configuration file is `~/.viki/config.toml`. Run `viki init --preset <name>` to generate a starter config.

### Key Configuration Sections

```toml
# Model settings
[intelligence]
default_model = ""           # Auto-detect based on hardware
preferred_engine = "ollama"  # ollama, vllm, mlx, etc.
provider = "local"

# Agent settings
[agent]
default_agent = "simple"
max_turns = 10
tools = "calculator,web_search,file_read,think"

# Engine endpoints
[engine]
default = "ollama"
[engine.ollama]
host = "http://localhost:11434"

# Memory
[tools.storage]
default_backend = "sqlite"
db_path = "~/.viki/memory.db"

# Server
[server]
host = "127.0.0.1"
port = 8000
```

---

## First Run

After installation:

```bash
# 1. Verify installation
viki doctor

# 2. Initialize with a preset (optional)
viki init --preset chat-simple --force

# 3. Start chatting
viki

# Or launch the holographic UI
viki gui
```

### Pulling a Model

If you didn't use a preset, pull a model manually:

```bash
ollama pull qwen3.5:4b  # Fast, lightweight (~2.7 GB)
# ollama pull qwen3.5:9b   # Better quality (~5 GB)
```

Then start chatting:

```bash
viki ask "Hello, ViKi!"
```

---

## Desktop App

The ViKi desktop app provides a native experience with:

- Holographic orb interface
- System tray integration
- Auto-start on login
- Native notifications
- Offline-first operation

### Installation

Download from [releases](https://github.com/open-viki/Viki/releases):

| Platform | File |
|---|---|
| macOS (Apple Silicon) | `ViKi_aarch64.dmg` |
| macOS (Intel) | `ViKi_x64.dmg` |
| Windows (64-bit) | `ViKi_x64-setup.msi` |
| Linux (DEB) | `ViKi_amd64.deb` |
| Linux (RPM) | `ViKi_x86_64.rpm` |
| Linux (AppImage) | `ViKi_x86_64.AppImage` |

### Building from Source

```bash
cd frontend
npm install
npm run tauri dev        # Development with hot reload
npm run tauri build      # Production build
```

---

## Docker Deployment

For server deployment:

```bash
cd deploy/docker
cp .env.example .env
# Edit .env and set VIKI_API_KEY (generate: `viki auth generate-key`)
docker compose up -d
```

This starts both the API server and Ollama. The web UI is bundled and served automatically at port 8000.

---

## Troubleshooting

### `viki` command not found

```bash
# Add to PATH or use uv run
export PATH="$HOME/.local/bin:$PATH"
# Or
uv run viki
```

### Model not found / Ollama not running

```bash
ollama serve &
ollama pull qwen3.5:4b
viki doctor
```

### Permission denied on `~/.viki`

```bash
chown -R $USER:$USER ~/.viki
chmod -R u+rw ~/.viki
```

### Port 8000 already in use

```bash
viki serve --port 8001
# Or configure in ~/.viki/config.toml:
# [server]
# port = 8001
```

### Rust extension build failed

```bash
# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default 1.88
# Rebuild
uv sync --group desktop-native
```

### Python version issues

ViKi requires Python 3.10–3.14. Python 3.14+ is supported as of ViKi 1.0.

```bash
# Check version
python --version

# Install correct version (example with uv)
uv python install 3.12
uv python pin 3.12
```

---

## Uninstall

```bash
# Remove service (if installed)
# Linux: sudo systemctl disable --now viki
# macOS: launchctl unload ~/Library/LaunchAgents/com.viki.plist
# Windows: powershell -File viki-service.ps1 uninstall

# Remove data
rm -rf ~/.viki
# Windows: Remove-Item -Recurse -Force "$env:LOCALAPPDATA\ViKi"

# Uninstalling does NOT remove uv (separate tool)
```

---

## Next Steps

- Read the [Quickstart Guide](quickstart.md)
- Explore [Presets](../user-guide/)
- Learn about [Agents](../user-guide/agents.md)
- Configure [Memory](../user-guide/memory.md)
- Set up [Channels](../user-guide/channels.md)

---

*ViKi is built on [Viki](https://github.com/open-viki/Viki) (Apache-2.0). See [NOTICE](../NOTICE) for attribution.*