# ViKi Quickstart

> **5 minutes to your first conversation with ViKi**

---

## 1. Install ViKi

```bash
# macOS / Linux / WSL2
curl -fsSL https://open-viki.github.io/Viki/install.sh | bash

# Windows (PowerShell)
irm https://open-viki.github.io/Viki/install.ps1 | iex
```

> The installer handles uv, Python, Ollama, and a starter model (~3 min).

---

## 2. Verify Installation

```bash
viki doctor
```

You should see all checks pass ✅

---

## 3. Start Chatting

```bash
# Option A: Terminal chat
viki

# Option B: Holographic UI (requires Node.js 22+)
viki gui
```

---

## 4. Your First Conversation

```
You: Hello, ViKi!
ViKi: Hello! I'm ViKi, your personal AI assistant. How can I help you today?

You: What's the weather like?
ViKi: I don't have direct access to weather data, but I can help you find it! Would you like me to search for the weather in your area?
```

---

## 5. Try a Preset

```bash
# Daily briefing with email/calendar
viki init --preset morning-digest-mac --force
viki connect gdrive
viki digest --fresh

# Code assistant
viki init --preset code-assistant --force

# Deep research
viki init --preset deep-research --force
```

---

## 5-Minute Tour

| Command | What it does |
|---|---|
| `viki` | Start terminal chat |
| `viki gui` | Launch holographic UI |
| `viki ask "question"` | Single question |
| `viki ask --agent orchestrator "task"` | Multi-step task with tools |
| `viki memory index ~/docs` | Index documents for search |
| `viki memory search "topic"` | Search your knowledge base |
| `viki init --preset <name>` | Apply a preset config |
| `viki doctor` | System health check |
| `viki auth generate-key` | Generate API key for server mode |

---

## Next Steps

- **Holographic UI**: Run `viki gui` for the 3D orb interface
- **Presets**: Try `viki init --preset code-assistant` for coding help
- **Memory**: Index your docs with `viki memory index ~/Documents`
- **Channels**: Connect Telegram/Telegram with `viki connect telegram`
- **Desktop App**: Download from [releases](https://github.com/open-viki/Viki/releases)

---

## Need Help?

- `viki --help` — All commands
- `viki doctor` — Diagnose issues
- [Documentation](https://open-viki.github.io/Viki/)
- [Discord](https://discord.gg/CMVBmDQ5Fj)
- [GitHub Issues](https://github.com/open-viki/Viki/issues)

---

*ViKi is built on [Viki](https://github.com/open-viki/Viki). Welcome to your personal AI!*