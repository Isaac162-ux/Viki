<div align="center">
  <img alt="ViKi" src="assets/Viki_Horizontal_Logo.png" width="400">

  <p><i>Personal AI, On Personal Devices — Reimagined.</i></p>

  <p>
    <a href="https://arxiv.org/abs/2605.17172"><img src="https://img.shields.io/badge/arXiv-2605.17172-b31b1b.svg" alt="arXiv"></a>
    <a href="https://viki.stanford.edu/"><img src="https://img.shields.io/badge/project-ViKi%20(based%20on%20Viki)-blue" alt="Project"></a>
    <a href="https://open-viki.github.io/Viki/"><img src="https://img.shields.io/badge/docs-mkdocs-blue" alt="Docs"></a>
    <img src="https://img.shields.io/badge/python-%3E%3D3.10-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License">
    <a href="https://discord.gg/CMVBmDQ5Fj"><img src="https://img.shields.io/badge/discord-join-7289da?logo=discord&logoColor=white" alt="Discord"></a>
    <a href="https://x.com/VikiAI"><img src="https://img.shields.io/badge/X-@VikiAI-black?logo=x&logoColor=white" alt="X / Twitter"></a>
  </p>
</div>

---

<div align="center">
  <img alt="ViKi demo reel" src="assets/viki_demo_reel.webp" width="75%">
</div>

---

> **[Documentation](https://open-viki.github.io/Viki/)**
>
> **[Project Site](https://viki.stanford.edu/)**
>
> **[Paper](https://arxiv.org/abs/2605.17172)**
>
> **[Leaderboard](https://open-viki.github.io/Viki/leaderboard/)**
>
> **[Roadmap](https://open-viki.github.io/Viki/development/roadmap/)**

## What is ViKi?

ViKi is a personal AI platform built on the Viki framework — featuring a holographic interface, voice interaction, autonomous agents, and local-first execution.

**Built on Viki** — the research-grade local AI stack from Stanford Hazy Research. ViKi extends Viki with:
- **Holographic 3D interface** (Three.js/WebGL orb with real-time state visualization)
- **Voice I/O** (STT/TTS with local and cloud backends)
- **Multimodal chat** (images, documents, code)
- **Model gateway** (Ollama, vLLM, MLX, Gemini, Groq, OpenRouter + intelligent routing)
- **Plugin system** (extensible with versioned contracts)
- **Mobile apps** (Android/iOS companions)

## Installation

Pick your platform and run one command. Each installer handles [uv](https://docs.astral.sh/uv/), the Python venv, Ollama, and a starter model — about 3 minutes on broadband.

| Platform | One-liner |
|---|---|
| **macOS · Linux · WSL2** | `curl -fsSL https://open-viki.github.io/Viki/install.sh \| bash` |
| **Native Windows** | `irm https://open-viki.github.io/Viki/install.ps1 \| iex` |
| **Desktop GUI** | Download `.exe` / `.dmg` / `.deb` / `.rpm` / `.AppImage` from the [latest release](https://github.com/open-viki/Viki/releases) |

Then `viki` to start. The Rust extension and larger models continue downloading in the background; `viki doctor` shows status.

Platform-specific notes (WSL2 setup, native-Windows scheduled-task service, desktop prerequisites, manual / contributor install): see the [installation docs](https://open-viki.github.io/Viki/getting-started/install/).

## Quick Start

```bash
viki                          # start chatting (default: simple agent)
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

### Agents

ViKi inherits Viki's eight built-in agents across three execution modes (on-demand, scheduled, continuous):

| Agent | Type | What it does |
|-------|------|-------------|
| `morning_digest` | Scheduled | Daily briefing from email, calendar, health, news — with TTS audio |
| `deep_research` | On-demand | Multi-hop research with citations across web and local docs |
| `monitor_operative` | Continuous | Long-horizon monitoring with memory, compression, and retrieval |
| `orchestrator` | On-demand | Multi-turn reasoning with automatic tool selection |
| `native_react` | On-demand | ReAct (Thought-Action-Observation) loop agent |
| `operative` | Continuous | Persistent autonomous agent with state management |
| `native_openhands` | On-demand | CodeAct — generates and executes Python code |
| `simple` | On-demand | Single-turn chat, no tools |

See the [User Guide](https://open-viki.github.io/Viki/user-guide/morning-digest/) and [Tutorials](https://open-viki.github.io/Viki/tutorials/) for detailed setup instructions.

Full documentation — including Docker deployment, cloud engines, development setup, and tutorials — at **[open-viki.github.io/Viki](https://open-viki.github.io/Viki/)**.

## Community

- **GitHub:** [github.com/open-viki/Viki](https://github.com/open-viki/Viki)
- **Discord:** [discord.gg/CMVBmDQ5Fj](https://discord.gg/CMVBmDQ5Fj)
- **X / Twitter:** [@VikiAI](https://x.com/VikiAI)
- **Docs:** [open-viki.github.io/Viki](https://open-viki.github.io/Viki/)

## Contributing

We welcome contributions! See the [Contributing Guide](CONTRIBUTING.md) for incentives, contribution types, and the PR process.

Quick start for contributors:

```bash
git clone https://github.com/open-viki/Viki.git
cd Viki
uv sync --extra dev
uv run pre-commit install
uv run pytest tests/ -v
```

Browse the [Roadmap](https://open-viki.github.io/Viki/development/roadmap/) for areas where help is needed. Comment **"take"** on any issue to get auto-assigned.

## About

ViKi is built on **Viki**, which is part of [Intelligence Per Watt](https://www.intelligence-per-watt.ai/), a research initiative studying the intelligence efficiency of AI systems. The project is developed at [Hazy Research](https://hazyresearch.stanford.edu/) and the [Scaling Intelligence Lab](https://scalingintelligence.stanford.edu/) at [Stanford SAIL](https://ai.stanford.edu/).

## Sponsors

<p>
  <a href="https://www.laude.org/">Laude Institute</a> &bull;
  <a href="https://datascience.stanford.edu/marlowe">Stanford Marlowe</a> &bull;
  <a href="https://cloud.google.com/">Google Cloud Platform</a> &bull;
  <a href="https://lambda.ai/">Lambda Labs</a> &bull;
  <a href="https://ollama.com/">Ollama</a> &bull;
  <a href="https://research.ibm.com/">IBM Research</a> &bull;
  <a href="https://hai.stanford.edu/">Stanford HAI</a>
</p>

## Citation

```bibtex
@misc{saadfalcon2026vikipersonalaipersonal,
      title={Viki: Personal AI, On Personal Devices}, 
      author={Jon Saad-Falcon and Avanika Narayan and Robby Manihani and Tanvir Bhathal and Herumb Shandilya and Hakki Orhun Akengin and Gabriel Bo and Andrew Park and Matthew Hart and Caia Costello and Chuan Li and Christopher Ré and Azalia Mirhoseini},
      year={2026},
      eprint={2605.17172},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2605.17172}, 
}
```

## License

[Apache 2.0](LICENSE) — ViKi includes code from Viki (Copyright 2025 The Viki Authors, licensed under Apache-2.0). See [NOTICE](NOTICE) for attribution details.
