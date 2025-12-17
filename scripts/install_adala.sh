#!/usr/bin/env bash
set -euo pipefail

# Install latest Adala from GitHub or do a developer install
# Usage:
#   ./scripts/install_adala.sh         # pip install from GitHub
#   ./scripts/install_adala.sh dev     # clone and poetry install

if [[ "${1:-}" == "dev" ]]; then
  echo "[Adala] Developer install..."
  if [ ! -d Adala ]; then
    git clone https://github.com/HumanSignal/Adala.git
  else
    echo "[Adala] Repository already cloned. Pulling latest..."
    (cd Adala && git pull --ff-only)
  fi
  cd Adala
  if command -v poetry >/dev/null 2>&1; then
    poetry install
  else
    echo "Poetry not found. Please install poetry: https://python-poetry.org/docs/"
    exit 1
  fi
else
  echo "[Adala] Installing latest from GitHub via pip..."
  pip install --upgrade "git+https://github.com/HumanSignal/Adala.git"
fi
