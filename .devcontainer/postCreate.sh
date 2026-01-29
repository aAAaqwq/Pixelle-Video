#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer] Running postCreate tasks..."

cd /workspaces/Pixelle-Video

# Install system dependencies
echo "[devcontainer] Installing system dependencies..."
sudo apt-get update || true
sudo apt-get install -y --fix-missing ffmpeg chromium fonts-noto-cjk 2>&1 | tail -5

# Install uv package manager first
echo "[devcontainer] Installing uv package manager..."
pip install uv --quiet

# Install Python dependencies with uv
echo "[devcontainer] Installing Python dependencies with uv..."
uv sync --frozen

if [ -f scripts/codespace_setup.sh ]; then
  echo "[devcontainer] Running codespace setup script..."
  bash scripts/codespace_setup.sh
fi

echo "[devcontainer] postCreate complete. Streamlit will start automatically via postStart.sh"
