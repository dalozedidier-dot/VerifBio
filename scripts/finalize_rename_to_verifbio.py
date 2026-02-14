#!/usr/bin/env python3
from __future__ import annotations

import argparse
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

PAT_ECHOBIO = re.compile(r"\bechobio\b")
PAT_ECHOBIO_CAP = re.compile(r"\bEchobio\b")
PAT_ECHOBIO_TITLE = re.compile(r"\bEchoBio\b")


def _run(cmd: list[str]) -> int:
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        return 127


def _git_mv(src: Path, dst: Path) -> bool:
    if _run(["git", "mv", str(src), str(dst)]) == 0:
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    return True


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_EXTS or path.name == "Makefile":
            files.append(path)
    return files


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def write_text(path: Path, data: str) -> None:
    path.write_text(data, encoding="utf-8", newline="\n")


def replace_in_text(data: str) -> str:
    data = PAT_ECHOBIO.sub("verifbio", data)
    data = PAT_ECHOBIO_CAP.sub("Verifbio", data)
    data = PAT_ECHOBIO_TITLE.sub("VerifBio", data)
    return data


def patch_pyproject(pyproject: Path) -> bool:
    data = read_text(pyproject)
    if data is None:
        return False

    new = data

    # PEP 621 / Poetry: project name
    new = re.sub(
        r'(?m)^\s*name\s*=\s*"echobio"\s*$',
        'name = "verifbio"',
        new,
    )

    # Console scripts: echobio = "echobio...." -> verifbio = "verifbio...."
    new = re.sub(
        r'(?m)^\s*echobio\s*=\s*"echobio\.',
        'verifbio = "verifbio.',
        new,
    )

    # Explicit packages list: packages = ["echobio"]
    new = re.sub(
        r'(?m)^\s*packages\s*=\s*\[\s*"echobio"\s*\]\s*$',
        'packages = ["verifbio"]',
        new,
    )

    new = replace_in_text(new)

    if new != data:
        write_text(pyproject, new)
        return True
    return False


def replace_in_file(path: Path) -> bool:
    data = read_text(path)
    if data is None:
        return False

    if path.name == "pyproject.toml":
        return patch_pyproject(path)

    new = replace_in_text(data)
    if new != data:
        write_text(path, new)
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Finalize rename echobio -> verifbio (package dir + refs)."
    )
    parser.add_argument("--root", default=".", help="Repo root (default: .)")
    args = parser.parse_args()

    repo = Path(args.root).resolve()

    moved = False

    src_old = repo / "src" / "echobio"
    src_new = repo / "src" / "verifbio"
    if src_old.is_dir() and not src_new.is_dir():
        _git_mv(src_old, src_new)
        moved = True

    top_old = repo / "echobio"
    top_new = repo / "verifbio"
    if top_old.is_dir() and not top_new.is_dir():
        _git_mv(top_old, top_new)
        moved = True

    changed = 0
    for f in iter_text_files(repo):
        if replace_in_file(f):
            changed += 1

    print("Finalize rename summary")
    print(f"- moved package dirs: {moved}")
    print(f"- edited text files: {changed}")
    print("")
    print("Next")
    print("1) Review: git diff")
    print('2) Test:  python -c "import verifbio; print(verifbio.__file__)"')
    print("3) Commit + push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
