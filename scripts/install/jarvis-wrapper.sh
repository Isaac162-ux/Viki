#!/usr/bin/env bash
# viki-wrapper.sh — symlinked to ~/.local/bin/viki.
# Activates the managed venv and execs the real viki CLI.

viki_HOME="${viki_HOME:-$HOME/.viki}"
VENV="$viki_HOME/.venv"

if [[ ! -d "$VENV" ]]; then
    echo "viki: venv not found at $VENV" >&2
    echo "Re-run the installer: curl -fsSL https://open-viki.github.io/viki/install.sh | bash" >&2
    exit 1
fi

exec "$VENV/bin/viki" "$@"
