from __future__ import annotations

import re
from typing import Any

import yaml

_MIR_RE = re.compile(r"(miR-\d+)", re.IGNORECASE)
_GENE_RE = re.compile(r"\b([A-Z0-9]{3,10})\b")


def draft_from_text(text: str, *, language: str = "en") -> dict[str, Any]:
    # Very lightweight heuristic draft.
    # Goal: produce a syntactically valid YAML structure that the user can refine.
    genes = sorted(set(_GENE_RE.findall(text)))[:5]
    mirs = sorted(set(m.group(1) for m in _MIR_RE.finditer(text)))[:3]

    entities = []
    for g in genes:
        entities.append({"kind": "gene_or_factor", "name": g})
    for m in mirs:
        entities.append({"kind": "mirna", "name": m})

    if not entities:
        entities.append({"kind": "entity", "name": "TBD"})

    claim_text = text.strip().replace("\n", " ").strip()
    claim_text = claim_text[:6000]

    return {
        "schema_version": "0.1",
        "claim_id": "ECHOBIO-DRAFT-0001",
        "title": "",
        "claim_type": "causal_mechanistic",
        "language": language,
        "claim_text": claim_text if claim_text else None,
        "domain_tags": [],
        "b1": {
            "entities": entities,
            "context": {
                "setting": "",
                "species": {"name": "", "tax_id": None},
                "tissue": "",
                "notes": "",
            },
            "variables": {
                "exposure_or_intervention": {
                    "description": "",
                    "operationalization": "",
                },
                "outcome": {"description": "", "operationalization": ""},
                "mediators": [],
                "covariates_declared": [],
            },
        },
        "b2": {
            "biological_scale": "",
            "model_system": {"description": "", "validity_notes": ""},
            "boundaries": {
                "time_window": "",
                "spatial_scope": "",
                "generalization_limits": [],
            },
        },
        "b3": {
            "causal_model": {"type": "none", "statements": []},
            "dag": {"nodes": [], "edges": []},
            "confounders": {"listed": []},
            "identification_notes": [],
        },
        "b4": {
            "design_controls": {
                "randomization": "",
                "blinding": "",
                "sabv": None,
                "power_analysis": {"declared": False},
                "exclusion_criteria": [],
                "analysis_plan": {
                    "primary_endpoint": "",
                    "secondary_endpoints": [],
                    "multiple_testing": {"correction": ""},
                    "outlier_handling": "",
                },
            },
            "resources": {"rrids": [], "cell_lines": []},
            "circularity_guards": {
                "discovery_data": [],
                "validation_data": [],
                "notes": "",
            },
        },
        "b5": {"independent_predictions": []},
    }


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
