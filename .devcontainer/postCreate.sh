#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer] Running postCreate tasks..."

cd /workspaces/Pixelle-Video

if [ -f scripts/codespace_setup.sh ]; then
  bash scripts/codespace_setup.sh
fi

echo "[devcontainer] Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -e . || true

echo "[devcontainer] postCreate complete. You can start the app with .devcontainer/postStart.sh or let postStart run it automatically."
