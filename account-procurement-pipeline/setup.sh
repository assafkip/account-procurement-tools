#!/usr/bin/env bash
# One-time setup: venv, deps, vendored tgspyder, and offline translation models.
# Safe to re-run. Downloads translation models once (needs network for this step).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

echo "[1/4] Creating virtualenv (.venv)"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/4] Installing Python dependencies"
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "[3/4] Installing vendored tgspyder (editable)"
pip install -e ../tgspyder

echo "[4/4] Installing offline translation models (source -> English)"
python3 install_models.py

echo "Done. Authenticate tgspyder once, then run ./run.sh"
