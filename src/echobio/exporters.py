from __future__ import annotations

from typing import Any, Literal

ExportFormat = Literal["markdown", "latex"]


def export_report(report: dict[str, Any], fmt: ExportFormat) -> str:
    if fmt == "markdown":
        return _export_markdown(report)
    if fmt == "latex":
        return _export_latex(report)
    raise ValueError(f"Unsupported export format: {fmt}")


def _export_markdown(report: dict[str, Any]) -> str:
    overall = report.get("overall", {})
    levels = report.get("levels", {})

    lines: list[str] = []
    lines.append(f"# EchoBio report: {report.get('claim_id', '')}".strip())
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append(f"- status: {overall.get('status')}")
    lines.append(f"- spec_score_0_100: {overall.get('spec_score_0_100')}")
    if "weighted_score_0_100" in overall:
        lines.append(f"- weighted_score_0_100: {overall.get('weighted_score_0_100')}")
    if overall.get("blocking_levels"):
        lines.append(f"- blocking_levels: {', '.join(overall.get('blocking_levels'))}")
    lines.append("")

    lines.append("## Levels")
    lines.append("")
    lines.append("| Level | Status |")
    lines.append("|---|---|")
    for lvl in ["B1", "B2", "B3", "B4", "B5"]:
        status = levels.get(lvl, {}).get("status", "n/a")
        lines.append(f"| {lvl} | {status} |")
    lines.append("")

    for lvl in ["B1", "B2", "B3", "B4", "B5"]:
        data = levels.get(lvl, {})
        lines.append(f"## {lvl}")
        lines.append("")
        lines.append(f"Status: {data.get('status')}")
        lines.append("")
        checks = data.get("checks", [])
        if checks:
            lines.append("Checks:")
            lines.append("")
            for c in checks:
                msg = c.get("message")
                suffix = f" ({msg})" if msg else ""
                lines.append(f"- {c.get('id')}: {c.get('status')}{suffix}")
            lines.append("")
        reasons = data.get("reasons", [])
        if reasons:
            lines.append("Reasons:")
            lines.append("")
            for r in reasons:
                lines.append(f"- {r}")
            lines.append("")
        suggestions = data.get("suggestions", [])
        if suggestions:
            lines.append("Suggestions:")
            lines.append("")
            for s in suggestions:
                lines.append(f"- {s}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _export_latex(report: dict[str, Any]) -> str:
    overall = report.get("overall", {})
    levels = report.get("levels", {})

    def esc(s: str) -> str:
        return (
            s.replace("\\", "\\textbackslash{}")
            .replace("&", "\\&")
            .replace("%", "\\%")
            .replace("$", "\\$")
            .replace("#", "\\#")
            .replace("_", "\\_")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace("~", "\\textasciitilde{}")
            .replace("^", "\\textasciicircum{}")
        )

    lines: list[str] = []
    lines.append("% EchoBio checklist export")
    lines.append("\\section*{EchoBio report}")
    lines.append(f"Claim: {esc(str(report.get('claim_id', '')))}\\\\")
    lines.append(f"Status: {esc(str(overall.get('status', '')))}\\\\")
    lines.append(f"Spec score: {esc(str(overall.get('spec_score_0_100', '')))}\\\\")
    if "weighted_score_0_100" in overall:
        lines.append(
            f"Weighted score: {esc(str(overall.get('weighted_score_0_100')))}\\\\"
        )
    lines.append("")
    lines.append("\\begin{tabular}{ll}")
    lines.append("\\textbf{Level} & \\textbf{Status} \\\\")
    lines.append("\\hline")
    for lvl in ["B1", "B2", "B3", "B4", "B5"]:
        status = levels.get(lvl, {}).get("status", "n/a")
        lines.append(f"{lvl} & {esc(str(status))} \\\\")
    lines.append("\\end{tabular}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
