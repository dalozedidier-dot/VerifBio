#!/usr/bin/env bash
set -euo pipefail

# Run from repo root:
#   bash scripts/rename_to_verifbio.sh
#
# This script:
# - Moves src/echobio -> src/verifbio if present
# - Rewrites textual references echobio -> verifbio across repo text files

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -d "src/echobio" ] && [ ! -d "src/verifbio" ]; then
  mkdir -p "src"
  if command -v git >/dev/null 2>&1; then
    git mv "src/echobio" "src/verifbio" 2>/dev/null || mv "src/echobio" "src/verifbio"
  else
    mv "src/echobio" "src/verifbio"
  fi
fi

if [ -d "echobio" ] && [ ! -d "verifbio" ]; then
  if command -v git >/dev/null 2>&1; then
    git mv "echobio" "verifbio" 2>/dev/null || mv "echobio" "verifbio"
  else
    mv "echobio" "verifbio"
  fi
fi

python3 "scripts/rename_to_verifbio.py" --root .

echo "Done. Review with: git diff"
