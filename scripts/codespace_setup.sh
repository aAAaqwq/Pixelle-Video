#!/usr/bin/env bash
set -euo pipefail

echo "[codespace-setup] Starting Codespace system setup..."

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -y

# Install system packages needed by the project (idempotent)
sudo apt-get install -y --no-install-recommends \
  ffmpeg \
  fontconfig \
  fonts-liberation \
  fonts-noto-cjk \
  wget \
  xdg-utils \
  ca-certificates || true

# Try installing chromium via common package names (some images use different package names)
sudo apt-get install -y --no-install-recommends chromium chromium-driver || true
sudo apt-get install -y --no-install-recommends chromium-browser chromium-driver || true

echo "[codespace-setup] System packages installation complete. Verifying fonts and chromium..."

echo "[codespace-setup] Chinese fonts (sample):"
fc-list :lang=zh | head -n 10 || true

if command -v chromium >/dev/null 2>&1; then
  echo "[codespace-setup] chromium -> $(command -v chromium)"
elif command -v chromium-browser >/dev/null 2>&1; then
  echo "[codespace-setup] chromium-browser -> $(command -v chromium-browser)"
else
  echo "[codespace-setup] Warning: chromium not found in PATH"
fi

echo "[codespace-setup] Done. Next: install Python deps in postCreate step."
