from __future__ import annotations

import json
from pathlib import Path

from echobio.audit import audit_claim
from echobio.dag_export import export_dag
from echobio.io import load_claim
from echobio.scoring import weighted_score


def test_audit_smoke() -> None:
    spec = load_claim(Path("examples") / "brca1_parp.yaml")
    report = audit_claim(spec, mode="strict")
    assert report["tool"] == "verifbio"
    assert report["overall"]["spec_score_0_100"] >= 0
    assert report["overall"]["weighted_score_0_100"] >= 0
    json.dumps(report)


def test_weighted_score_basic() -> None:
    s = weighted_score(b1="pass", b2="pass", b3="pass", b4="pass", b5="pass")
    assert s == 100


def test_dag_export_mermaid() -> None:
    spec = load_claim(Path("examples") / "brca1_parp.yaml")
    mmd = export_dag(spec, "mermaid")
    assert "flowchart" in mmd
