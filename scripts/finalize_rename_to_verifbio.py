#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
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


def _run(cmd: list[str]) -> int:
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        return 127


def _git_mv(src: Path, dst: Path) -> None:
    if _run(["git", "mv", str(src), str(dst)]) == 0:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)


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


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def write_text(path: Path, data: str) -> None:
    path.write_text(data, encoding="utf-8", newline="\n")


def replace_in_file(path: Path, repls: list[tuple[re.Pattern[str], str]]) -> bool:
    data = read_text(path)
    if data is None:
        return False

    new = data
    for pat, rep in repls:
        new = pat.sub(rep, new)

    if new != data:
        write_text(path, new)
        return True
    return False


def patch_pyproject(pyproject: Path) -> bool:
    data = read_text(pyproject)
    if data is None:
        return False

    new = data

    # Common patterns: PEP 621
    new = re.sub(r'(?m)^\s*name\s*=\s*"echobio"\s*$', 'name = "verifbio"', new)

    # Poetry style
    new = re.sub(r'(?m)^\s*name\s*=\s*"echobio"\s*$', 'name = "verifbio"', new)

    # Console scripts (best effort)
    new = re.sub(
        r'(?m)^\s*echobio\s*=\s*"echobio\.',
        'verifbio = "verifbio.',
        new,
    )

    # If packages are pinned explicitly
    new = re.sub(
        r'(?m)^\s*packages\s*=\s*\[\s*"echobio"\s*\]\s*$',
        'packages = ["verifbio"]',
        new,
    )

    if new != data:
        write_text(pyproject, new)
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Finalize rename echobio -> verifbio.")
    ap.add_argument("--root", default=".", help="Repo root (default: current dir)")
    args = ap.parse_args()

    repo = Path(args.root).resolve()

    moved = False
    if (repo / "src" / "echobio").is_dir() and not (repo / "src" / "verifbio").is_dir():
        _git_mv(repo / "src" / "echobio", repo / "src" / "verifbio")
        moved = True

    if (repo / "echobio").is_dir() and not (repo / "verifbio").is_dir():
        _git_mv(repo / "echobio", repo / "verifbio")
        moved = True

    repls: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"\bechobio\b"), "verifbio"),
        (re.compile(r"\bEchobio\b"), "Verifbio"),
        (re.compile(r"\bEchoBio\b"), "VerifBio"),
    ]

    changed = 0
    for f in iter_text_files(repo):
        if f.name == "pyproject.toml":
            if patch_pyproject(f):
                changed += 1
            continue
        if replace_in_file(f, repls):
            changed += 1

    print("Finalize rename summary")
    print(f"- moved package dirs: {moved}")
    print(f"- edited text files: {changed}")
    print("")
    print("Next")
    print("1) Review changes: git diff")
    print('2) Run: python -c "import verifbio; print(verifbio.__file__)"')
    print("3) Commit and push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
