from __future__ import annotations

from pathlib import Path

import yaml

from verifbio.audit import audit_claim
from verifbio.models import ClaimSpec


def _load_spec(path: Path) -> ClaimSpec:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    # Pydantic v2: model_validate, v1: parse_obj
    if hasattr(ClaimSpec, "model_validate"):
        return ClaimSpec.model_validate(data)  # type: ignore[attr-defined]
    return ClaimSpec.parse_obj(data)  # type: ignore[attr-defined]


def test_audit_smoke() -> None:
    claim_path = Path("examples/brca1_parp.yaml")
    assert claim_path.exists(), "Example claim missing: examples/brca1_parp.yaml"

    spec = _load_spec(claim_path)
    report = audit_claim(spec)

    assert report["tool"] == "verifbio"
    assert report["overall"]["status"] in {"pass", "fail"}
    assert set(report["levels"].keys()) >= {"B1", "B2", "B3", "B4", "B5"}
