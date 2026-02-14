from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import yaml


def _resolve_pkg() -> str:
    for name in ("verifbio", "echobio"):
        try:
            importlib.import_module(name)
            return name
        except ModuleNotFoundError:
            continue
    raise RuntimeError("Neither verifbio nor echobio could be imported")


PKG = _resolve_pkg()
audit_mod = importlib.import_module(f"{PKG}.audit")
models_mod = importlib.import_module(f"{PKG}.models")

audit_claim = getattr(audit_mod, "audit_claim")
ClaimSpec = getattr(models_mod, "ClaimSpec")


def _load_spec(path: Path) -> Any:
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

    assert report["tool"] in {"verifbio", "echobio"}
    assert report["overall"]["status"] in {"pass", "fail"}
    assert set(report["levels"].keys()) >= {"B1", "B2", "B3", "B4", "B5"}
