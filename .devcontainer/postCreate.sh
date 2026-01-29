#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer] Running postCreate tasks..."

cd /workspaces/Pixelle-Video

# Install system dependencies
echo "[devcontainer] Installing system dependencies..."
sudo apt-get update || true
sudo apt-get install -y --fix-missing ffmpeg chromium fonts-noto-cjk 2>&1 | tail -5

# Install uv package library
echo "[devcontainer] Installing uv package library..."
uv sync --frozen

if [ -f scripts/codespace_setup.sh ]; then
  echo "[devcontainer] Running codespace setup script..."
  bash scripts/codespace_setup.sh
fi

echo "[devcontainer] postCreate complete. Streamlit will start automatically via postStart.sh"
