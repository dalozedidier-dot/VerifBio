#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

TEXT_EXTS = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "_ci_out",
    "build",
    "dist",
    "venv",
}


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in TEXT_EXTS or p.name == "Makefile":
            files.append(p)
    return files


def replace_in_file(path: Path, repls: list[tuple[re.Pattern[str], str]]) -> bool:
    try:
        data = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    new = data
    for pat, rep in repls:
        new = pat.sub(rep, new)

    if new != data:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Rename EchoBio -> VerifBio across a repo."
    )
    ap.add_argument("--root", default=".", help="Repo root (default: .)")
    ap.add_argument(
        "--old",
        default="echobio",
        help="Old package/cli name (default: echobio)",
    )
    ap.add_argument(
        "--new",
        default="verifbio",
        help="New package/cli name (default: verifbio)",
    )
    args = ap.parse_args()

    repo = Path(args.root).resolve()
    old = args.old
    new = args.new

    repls: list[tuple[re.Pattern[str], str]] = [
        (re.compile(rf"\b{re.escape(old)}\b"), new),
        (re.compile(rf"\b{re.escape(old.capitalize())}\b"), new.capitalize()),
        (re.compile(r"\bEchoBio\b"), "VerifBio"),
    ]

    changed = 0
    for f in iter_text_files(repo):
        if replace_in_file(f, repls):
            changed += 1

    print(f"Updated {changed} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
