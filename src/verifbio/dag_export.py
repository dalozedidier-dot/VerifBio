from __future__ import annotations

import re
from typing import Any, Literal

from .models import ClaimSpec

DagFormat = Literal["mermaid", "dot"]

_ARROW_PATTERNS = [
    re.compile(r"(?P<a>[A-Za-z0-9_\-]+)\s*->\s*(?P<b>[A-Za-z0-9_\-]+)"),
    re.compile(r"(?P<a>[A-Za-z0-9_\-]+)\s*→\s*(?P<b>[A-Za-z0-9_\-]+)"),
]


def export_dag(spec: ClaimSpec, fmt: DagFormat) -> str:
    edges = _get_edges(spec)
    if fmt == "mermaid":
        return _to_mermaid(edges)
    if fmt == "dot":
        return _to_dot(edges)
    raise ValueError(f"Unsupported DAG format: {fmt}")


def _get_edges(spec: ClaimSpec) -> list[tuple[str, str]]:
    if spec.b3 and spec.b3.dag and spec.b3.dag.edges:
        return [(a, b) for (a, b) in spec.b3.dag.edges]

    edges: list[tuple[str, str]] = []
    if spec.b3 and spec.b3.causal_model and spec.b3.causal_model.statements:
        for s in spec.b3.causal_model.statements:
            edges.extend(_extract_edges_from_text(s))
    return edges


def _extract_edges_from_text(s: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for pat in _ARROW_PATTERNS:
        for m in pat.finditer(s):
            a = m.group("a").strip()
            b = m.group("b").strip()
            if a and b:
                out.append((a, b))
    return out


def _to_mermaid(edges: list[tuple[str, str]]) -> str:
    lines = ["flowchart TD"]
    for a, b in edges:
        lines.append(f"  {a} --> {b}")
    return "\n".join(lines).rstrip() + "\n"


def _to_dot(edges: list[tuple[str, str]]) -> str:
    lines = ["digraph G {"]
    for a, b in edges:
        lines.append(f'  "{a}" -> "{b}";')
    lines.append("}")
    return "\n".join(lines).rstrip() + "\n"
