from __future__ import annotations

from typing import Any

from .models import ClaimSpec


def suggest_predictions(spec: ClaimSpec) -> dict[str, Any]:
    suggestions: list[dict[str, Any]] = []

    if not spec.b3 or not spec.b3.causal_model.statements:
        return {
            "suggestions": suggestions,
            "notes": [
                "No causal statements found; add B3.causal_model.statements first.",
            ],
        }

    # Heuristic: for each statement "A -> B", propose perturbation of A and B.
    for idx, stmt in enumerate(spec.b3.causal_model.statements, start=1):
        if "->" not in stmt and "→" not in stmt:
            continue

        parts = stmt.replace("→", "->").split("->")
        if len(parts) < 2:
            continue

        a = parts[0].strip().split()[0]
        b = parts[1].strip().split()[0]

        suggestions.append(_mk_pred(f"S{idx}A", a, b))
        suggestions.append(_mk_pred(f"S{idx}B", b, "outcome"))

    return {
        "suggestions": suggestions,
        "notes": [
                "Heuristic suggestions; refine to be quantitative.",
        ],
    }


def _mk_pred(pred_id: str, target: str, downstream: str) -> dict[str, Any]:
    statement = (
        f"Perturbation of {target} will change {downstream} in the predicted direction "
        "under an independent test setup."
    )
    return {
        "prediction_id": pred_id,
        "is_independent": True,
        "statement": statement,
        "test_protocol": {
            "measurement": "Define a primary endpoint and measurement method.",
            "decision_rule": "Define a quantitative threshold and analysis plan.",
        },
        "data_reference": {"dataset_id": "independent_dataset_TBD"},
        "falsifiers": [
            "No change or opposite direction under blinded measurement.",
        ],
    }
