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
python3 - <<'PY'
import argostranslate.package as pkg

WANT = ["ru", "zh", "vi", "es", "pt", "tr", "uk", "de", "fr", "id"]
pkg.update_package_index()
available = pkg.get_available_packages()
installed, missing = [], []
for code in WANT:
    match = next((p for p in available if p.from_code == code and p.to_code == "en"), None)
    if match is None:
        missing.append(code)
        continue
    pkg.install_from_path(match.download())
    installed.append(code)

print(f"  installed: {', '.join(installed) or 'none'}")
if missing:
    print(f"  NOT in Argos index: {', '.join(missing)}")
    print("  (Vietnamese 'vi' often needs an OPUS-MT model converted to .argosmodel;")
    print("   see README 'Vietnamese' section. Detection still works; those posts")
    print("   pass through untranslated and are keyword-matched in their own language.)")
PY

echo "Done. Authenticate tgspyder once, then run ./run.sh"
