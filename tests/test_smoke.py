from __future__ import annotations

import json
from pathlib import Path

from echobio.audit import audit_claim
from echobio.io import load_claim


def test_audit_smoke() -> None:
    spec = load_claim(Path("examples") / "brca1_parp.yaml")
    report = audit_claim(spec)
    assert report["tool"] == "echobio"
    assert report["overall"]["spec_score_0_100"] >= 0
    # ensure JSON serializable
    json.dumps(report)
