#!/usr/bin/env bash
set -euo pipefail

# Rename EchoBio -> VerifBio with minimal assumptions.
# Run from repo root:
#   bash scripts/rename_to_verifbio.sh
#
# This script:
# 1) Moves src/echobio -> src/verifbio if present
# 2) Rewrites textual references (CLI, docs, workflow, pyproject, Makefile)
# 3) Adjusts tool label in audit report ("tool": "verifbio") if found

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

if [ -d "src/echobio" ] && [ ! -d "src/verifbio" ]; then
  mkdir -p "src"
  git mv "src/echobio" "src/verifbio" 2>/dev/null || mv "src/echobio" "src/verifbio"
fi

# If there's a top-level package without src-layout (rare), handle it too.
if [ -d "echobio" ] && [ ! -d "verifbio" ]; then
  git mv "echobio" "verifbio" 2>/dev/null || mv "echobio" "verifbio"
fi

python3 "scripts/rename_to_verifbio.py" --root .

# Also replace the tool id inside JSON-ish strings in code if present.
# (safe no-op if not found)
python3 - <<'PY'
from pathlib import Path
import re

paths = []
for p in Path(".").rglob("*.py"):
    if any(part in {".git","venv",".venv","__pycache__","_ci_out","build","dist"} for part in p.parts):
        continue
    paths.append(p)

pat = re.compile(r'"tool"\s*:\s*"echobio"')
changed = 0
for p in paths:
    try:
        s = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    ns = pat.sub('"tool": "verifbio"', s)
    if ns != s:
        p.write_text(ns, encoding="utf-8")
        changed += 1
print(f"Updated tool id in {changed} python files.")
PY

echo "Done. Review changes with: git diff"
