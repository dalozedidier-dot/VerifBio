from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import audit_claim
from .io import load_claim


def _cmd_audit(args: argparse.Namespace) -> int:
    spec = load_claim(args.input)
    report = audit_claim(spec)
    out_text = json.dumps(report, indent=2, ensure_ascii=False)

    if args.out:
        Path(args.out).write_text(out_text + "\n", encoding="utf-8")
    else:
        print(out_text)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="echobio",
        description="Audit biological claim specification quality (not truth).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_audit = sub.add_parser("audit", help="Audit a claim YAML spec and output a JSON report.")
    p_audit.add_argument("input", help="Path to claim YAML (recommended).")
    p_audit.add_argument("--out", help="Write report JSON to this path.")
    p_audit.set_defaults(func=_cmd_audit)

    args = parser.parse_args()
    raise SystemExit(args.func(args))
