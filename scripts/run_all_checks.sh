#!/usr/bin/env bash
set -euo pipefail

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

mkdir -p _ci_out

python -m black --check .
pytest -q
echobio audit examples/brca1_parp.yaml --out _ci_out/echobio_report.json
echobio export _ci_out/echobio_report.json --format markdown --out _ci_out/echobio_report.md

echo "OK: wrote _ci_out/echobio_report.json"
