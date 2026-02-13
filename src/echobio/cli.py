from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import audit_claim
from .dag_export import export_dag
from .draft import draft_from_text, dump_yaml
from .exporters import export_report
from .io import load_claim
from .suggest import suggest_predictions


def _cmd_audit(args: argparse.Namespace) -> int:
    spec = load_claim(args.input)
    report = audit_claim(spec, mode=args.mode)
    out_text = json.dumps(report, indent=2, ensure_ascii=False)

    if args.out:
        Path(args.out).write_text(out_text + "\n", encoding="utf-8")
    else:
        print(out_text)
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    text = export_report(report, args.format)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


def _cmd_dag(args: argparse.Namespace) -> int:
    spec = load_claim(args.input)
    text = export_dag(spec, args.format)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


def _cmd_suggest(args: argparse.Namespace) -> int:
    spec = load_claim(args.input)
    payload = suggest_predictions(spec)
    out_text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(out_text + "\n", encoding="utf-8")
    else:
        print(out_text)
    return 0


def _cmd_draft(args: argparse.Namespace) -> int:
    text = Path(args.text).read_text(encoding="utf-8") if args.text else args.inline
    data = draft_from_text(text, language=args.language)
    y = dump_yaml(data)
    if args.out:
        Path(args.out).write_text(y, encoding="utf-8")
    else:
        print(y)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="echobio",
        description="Audit biological claim specification quality (not truth).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_audit = sub.add_parser("audit", help="Audit a claim YAML spec and output a JSON report.")
    p_audit.add_argument("input", help="Path to claim YAML (recommended).")
    p_audit.add_argument(
        "--mode",
        choices=["lite", "strict"],
        default="strict",
        help="Audit mode. 'lite' is more permissive for teaching; 'strict' is reviewer-grade.",
    )
    p_audit.add_argument("--out", help="Write report JSON to this path.")
    p_audit.set_defaults(func=_cmd_audit)

    p_export = sub.add_parser("export", help="Export an audit JSON report as markdown or latex.")
    p_export.add_argument("report", help="Path to report JSON (output of 'echobio audit').")
    p_export.add_argument("--format", choices=["markdown", "latex"], default="markdown")
    p_export.add_argument("--out", help="Write export to this path.")
    p_export.set_defaults(func=_cmd_export)

    p_dag = sub.add_parser("dag", help="Export DAG from claim (mermaid or graphviz dot).")
    p_dag.add_argument("input", help="Path to claim YAML.")
    p_dag.add_argument("--format", choices=["mermaid", "dot"], default="mermaid")
    p_dag.add_argument("--out", help="Write DAG to this path.")
    p_dag.set_defaults(func=_cmd_dag)

    p_suggest = sub.add_parser("suggest", help="Suggest independent predictions (heuristic).")
    p_suggest.add_argument("input", help="Path to claim YAML.")
    p_suggest.add_argument("--out", help="Write suggestions JSON to this path.")
    p_suggest.set_defaults(func=_cmd_suggest)

    p_draft = sub.add_parser("draft", help="Draft a claim YAML from raw text (heuristic).")
    group = p_draft.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Path to a text file (abstract, intro, notes).")
    group.add_argument("--inline", help="Inline text string.")
    p_draft.add_argument("--language", default="en", help="Language tag for the draft.")
    p_draft.add_argument("--out", help="Write draft YAML to this path.")
    p_draft.set_defaults(func=_cmd_draft)

    args = parser.parse_args()
    raise SystemExit(args.func(args))
