#!/usr/bin/env bash
set -uo pipefail

echo "[devcontainer] Running postCreate tasks..."

cd /workspaces/Pixelle-Video

# ============================================================================
# System Dependencies Installation
# ============================================================================

export DEBIAN_FRONTEND=noninteractive

# Remove problematic Yarn repository if it exists
echo "[devcontainer] Removing problematic repositories..."
sudo rm -f /etc/apt/sources.list.d/yarn.sources 2>/dev/null || true
sudo rm -f /etc/apt/sources.list.d/yarn.list 2>/dev/null || true

# Update package lists
echo "[devcontainer] Updating package lists..."
sudo apt-get update -y || {
  echo "[devcontainer] Warning: apt-get update had issues, continuing anyway..."
  true
}

# Install system packages needed by the project
echo "[devcontainer] Installing system packages..."
sudo apt-get install -y --no-install-recommends \
  ffmpeg \
  fontconfig \
  fonts-liberation \
  fonts-noto-cjk \
  wget \
  xdg-utils \
  ca-certificates || true

# Install chromium
echo "[devcontainer] Installing chromium..."
sudo apt-get install -y --no-install-recommends chromium 2>/dev/null || true

# Verify installation
echo "[devcontainer] Verifying system packages..."
echo "[devcontainer] Chinese fonts (sample):"
fc-list :lang=zh | head -n 10 || true

if command -v chromium >/dev/null 2>&1; then
  echo "[devcontainer] chromium -> $(command -v chromium)"
elif command -v chromium-browser >/dev/null 2>&1; then
  echo "[devcontainer] chromium-browser -> $(command -v chromium-browser)"
else
  echo "[devcontainer] Warning: chromium not found in PATH"
fi

# ============================================================================
# Python Dependencies Installation
# ============================================================================

# Install uv package manager
echo "[devcontainer] Installing uv package manager..."
pip install uv --quiet

# Install Python dependencies with uv
echo "[devcontainer] Installing Python dependencies with uv..."
uv sync --frozen

echo "[devcontainer] postCreate complete. Streamlit will start automatically via postStart.sh"
