#!/usr/bin/env bash
# Run the pipeline. Passes any extra args through to pipeline.py.
# Example: ./run.sh --channels config/channels.txt --proxy socks5://127.0.0.1:9050
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

if [ ! -d ".venv" ]; then
  echo "ERROR: .venv not found. Run ./setup.sh first." >&2
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

python3 src/pipeline.py "$@"
