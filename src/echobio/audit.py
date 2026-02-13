from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from .models import ClaimSpec
from .scoring import weighted_score

LevelStatus = Literal["pass", "partial", "fail"]
Mode = Literal["lite", "strict"]

_RRID_RE = re.compile(r"^RRID:([A-Za-z0-9_]+)$")


@dataclass(frozen=True)
class CheckResult:
    id: str
    status: LevelStatus
    message: str | None = None


@dataclass
class LevelReport:
    status: LevelStatus
    checks: list[CheckResult]
    reasons: list[str]
    suggestions: list[str]


def _status_from_checks(checks: list[CheckResult]) -> LevelStatus:
    if any(c.status == "fail" for c in checks):
        return "fail"
    if any(c.status == "partial" for c in checks):
        return "partial"
    return "pass"


def audit_claim(spec: ClaimSpec, *, mode: Mode = "strict") -> dict[str, Any]:
    levels: dict[str, LevelReport] = {}

    # -----------------
    # B1
    # -----------------
    b1_checks: list[CheckResult] = []

    if not spec.b1.entities:
        b1_checks.append(
            CheckResult(
                id="B1.entities.present",
                status="fail",
                message="No entities declared",
            )
        )
    else:
        b1_checks.append(CheckResult(id="B1.entities.present", status="pass"))

    exp = spec.b1.variables.exposure_or_intervention
    out = spec.b1.variables.outcome

    if not exp.get("description") or not exp.get("operationalization"):
        b1_checks.append(
            CheckResult(
                id="B1.exposure.operationalized",
                status="fail",
                message="Exposure/intervention lacks description or operationalization",
            )
        )
    else:
        b1_checks.append(CheckResult(id="B1.exposure.operationalized", status="pass"))

    if not out.get("description") or not out.get("operationalization"):
        b1_checks.append(
            CheckResult(
                id="B1.outcome.operationalized",
                status="fail",
                message="Outcome lacks description or operationalization",
            )
        )
    else:
        b1_checks.append(CheckResult(id="B1.outcome.operationalized", status="pass"))

    b1_status = _status_from_checks(b1_checks)
    b1_reasons = [c.message for c in b1_checks if c.message and c.status == "fail"]
    b1_suggestions = (
        ["Specify measurement operationalizations for exposure/outcome"]
        if b1_status != "pass"
        else []
    )
    levels["B1"] = LevelReport(
        status=b1_status,
        checks=b1_checks,
        reasons=b1_reasons,
        suggestions=b1_suggestions,
    )

    # -----------------
    # B2
    # -----------------
    if spec.b2 is None:
        levels["B2"] = LevelReport(
            status="fail",
            checks=[
                    CheckResult(
                        id="B2.present",
                        status="fail",
                        message="B2 section missing",
                    ),
            ],
            reasons=["B2 section missing"],
            suggestions=[
                "Declare biological scale, model validity, and boundaries "
                "(time/spatial/generalization limits).",
            ],
        )
    else:
        b2_checks: list[CheckResult] = []

        scale = spec.b2.biological_scale.strip().lower()
        if scale in {"unspecified", "", "na"}:
            b2_checks.append(
                CheckResult(
                    id="B2.scale.declared",
                    status="fail",
                    message="Biological scale unspecified",
                )
            )
        else:
            b2_checks.append(CheckResult(id="B2.scale.declared", status="pass"))

        ms_desc = (spec.b2.model_system.description or "").strip().lower()
        if not ms_desc or "not specified" in ms_desc:
            b2_checks.append(
                CheckResult(
                    id="B2.model_system.defined",
                    status="fail",
                    message="Model system not defined",
                )
            )
        else:
            b2_checks.append(CheckResult(id="B2.model_system.defined", status="pass"))

        has_any_boundary = any(
            (
                bool(spec.b2.boundaries.time_window),
                bool(spec.b2.boundaries.spatial_scope),
                bool(spec.b2.boundaries.generalization_limits),
            )
        )
        b2_checks.append(
            CheckResult(
                id="B2.boundaries.present",
                status="pass" if has_any_boundary else "partial",
                message=None if has_any_boundary else "Boundaries are thin or missing",
            )
        )

        b2_status = _status_from_checks(b2_checks)
        b2_reasons = [
            c.message
            for c in b2_checks
            if c.message and c.status in {"fail", "partial"}
        ]
        b2_suggestions = (
            ["Add explicit time window and generalization limits"]
            if b2_status != "pass"
            else []
        )
        levels["B2"] = LevelReport(
            status=b2_status,
            checks=b2_checks,
            reasons=b2_reasons,
            suggestions=b2_suggestions,
        )

    # -----------------
    # B3
    # -----------------
    if spec.b3 is None:
        levels["B3"] = LevelReport(
            status="fail",
            checks=[
                    CheckResult(
                        id="B3.present",
                        status="fail",
                        message="B3 section missing",
                    ),
            ],
            reasons=["B3 section missing"],
            suggestions=[
                "Declare a causal mechanism or DAG and address plausible confounders.",
            ],
        )
    else:
        b3_checks: list[CheckResult] = []

        if spec.b3.causal_model.type == "none" or not spec.b3.causal_model.statements:
            b3_checks.append(
                CheckResult(
                    id="B3.mechanism.declared",
                    status="fail",
                    message="No causal mechanism/pathway statements",
                )
            )
        else:
            b3_checks.append(CheckResult(id="B3.mechanism.declared", status="pass"))

        confs = spec.b3.confounders.listed
        b3_checks.append(
            CheckResult(
                id="B3.confounders.listed",
                status="pass" if confs else "partial",
                message=None if confs else "No confounders listed",
            )
        )

        has_controls = any(bool(c.control_strategy) for c in confs)
        b3_checks.append(
            CheckResult(
                id="B3.confounders.controlled",
                status="pass" if has_controls else "partial",
                message=None if has_controls else "Confounders lack control strategies",
            )
        )

        b3_status = _status_from_checks(b3_checks)
        b3_reasons = [
            c.message
            for c in b3_checks
            if c.message and c.status in {"fail", "partial"}
        ]
        b3_suggestions = (
            ["Provide minimal DAG nodes/edges and explicit control strategies"]
            if b3_status != "pass"
            else []
        )
        levels["B3"] = LevelReport(
            status=b3_status,
            checks=b3_checks,
            reasons=b3_reasons,
            suggestions=b3_suggestions,
        )

    # -----------------
    # B4
    # -----------------
    b4_sabv_status: LevelStatus | None = None
    b4_blinding_status: LevelStatus | None = None
    b4_random_status: LevelStatus | None = None

    if spec.b4 is None:
        levels["B4"] = LevelReport(
            status="fail",
            checks=[
                    CheckResult(
                        id="B4.present",
                        status="fail",
                        message="B4 section missing",
                    ),
            ],
            reasons=["B4 section missing"],
            suggestions=[
                "Declare randomization/blinding/power, endpoints, exclusion criteria, "
                "and circularity guards.",
            ],
        )
    else:
        b4_checks: list[CheckResult] = []
        dc = spec.b4.design_controls

        b4_random_status = "pass" if dc.randomization else "partial"
        b4_blinding_status = "pass" if dc.blinding else "partial"

        b4_checks.append(
            CheckResult(
                id="B4.randomization.declared",
                status=b4_random_status,
                message=None if dc.randomization else "Randomization not declared",
            )
        )
        b4_checks.append(
            CheckResult(
                id="B4.blinding.declared",
                status=b4_blinding_status,
                message=None if dc.blinding else "Blinding not declared",
            )
        )

        if dc.sabv is None:
            b4_sabv_status = "partial"
            b4_checks.append(
                CheckResult(
                    id="B4.sabv.declared",
                    status="partial",
                    message="SABV (sex as a biological variable) not declared",
                )
            )
        elif dc.sabv == "yes":
            b4_sabv_status = "pass"
            b4_checks.append(CheckResult(id="B4.sabv.declared", status="pass"))
        elif dc.sabv == "partial":
            b4_sabv_status = "partial"
            b4_checks.append(
                CheckResult(
                    id="B4.sabv.declared",
                    status="partial",
                    message="SABV partial (single-sex or limited reporting)",
                )
            )
        else:
            b4_sabv_status = "fail"
            b4_checks.append(
                CheckResult(
                    id="B4.sabv.declared",
                    status="fail",
                    message="SABV not addressed",
                )
            )

        pa = dc.power_analysis
        if pa is None or not pa.declared:
            b4_checks.append(
                CheckResult(
                    id="B4.power.declared",
                    status="partial",
                    message="Power analysis not declared",
                )
            )
        else:
            b4_checks.append(CheckResult(id="B4.power.declared", status="pass"))

        ap = dc.analysis_plan
        if ap is None or not ap.primary_endpoint:
            b4_checks.append(
                CheckResult(
                    id="B4.primary_endpoint.locked",
                    status="partial",
                    message="Primary endpoint not locked",
                )
            )
        else:
                b4_checks.append(
                    CheckResult(id="B4.primary_endpoint.locked", status="pass"),
                )

        rrids = spec.b4.resources.rrids
        if rrids:
            bad = [r.rrid for r in rrids if not _RRID_RE.match(r.rrid)]
            if bad:
                b4_checks.append(
                    CheckResult(
                        id="B4.rrids.valid",
                        status="fail",
                        message=f"Invalid RRID format: {bad}",
                    )
                )
            else:
                b4_checks.append(CheckResult(id="B4.rrids.valid", status="pass"))
        else:
            b4_checks.append(
                CheckResult(
                    id="B4.rrids.present",
                    status="partial",
                    message="No RRIDs declared (may be ok depending on claim)",
                )
            )

        disc = set(spec.b4.circularity_guards.discovery_data)
        val = set(spec.b4.circularity_guards.validation_data)
        overlap = sorted(disc.intersection(val))

        if overlap:
            b4_checks.append(
                CheckResult(
                    id="B4.circularity.no_overlap",
                    status="fail",
                    message=f"Discovery/validation overlap: {overlap}",
                )
            )
        else:
            b4_checks.append(CheckResult(id="B4.circularity.no_overlap", status="pass"))

        b4_status = _status_from_checks(b4_checks)

        if mode == "lite" and b4_status == "fail":
            hard_fail = any(
                c.id == "B4.circularity.no_overlap" and c.status == "fail"
                for c in b4_checks
            )
            if not hard_fail:
                b4_status = "partial"

        b4_reasons = [
            c.message
            for c in b4_checks
            if c.message and c.status in {"fail", "partial"}
        ]
        b4_suggestions = (
            [
                "Lock endpoints and analysis degrees of freedom; "
                "separate discovery vs validation explicitly",
            ]
            if b4_status != "pass"
            else []
        )
        levels["B4"] = LevelReport(
            status=b4_status,
            checks=b4_checks,
            reasons=b4_reasons,
            suggestions=b4_suggestions,
        )

    # -----------------
    # B5
    # -----------------
    if spec.b5 is None:
        levels["B5"] = LevelReport(
            status="fail",
            checks=[
                    CheckResult(
                        id="B5.present",
                        status="fail",
                        message="B5 section missing",
                    ),
            ],
            reasons=["B5 section missing"],
            suggestions=[
                "Add at least one independent prediction with protocol, "
                "decision rule, and independent data reference.",
            ],
        )
    else:
        b5_checks: list[CheckResult] = []
        preds = spec.b5.independent_predictions

        if not preds:
            b5_checks.append(
                CheckResult(
                    id="B5.predictions.present",
                    status="fail",
                    message="No independent predictions provided",
                )
            )
        else:
            b5_checks.append(CheckResult(id="B5.predictions.present", status="pass"))

        any_ind = any(p.is_independent for p in preds)
        b5_checks.append(
            CheckResult(
                id="B5.is_independent.true",
                status="pass" if any_ind else "fail",
                    message=(
                        None if any_ind else "No prediction marked is_independent: true"
                    ),
            )
        )

        thin = [
            p.prediction_id
            for p in preds
            if (not p.test_protocol) or ("decision_rule" not in p.test_protocol)
        ]
        b5_checks.append(
            CheckResult(
                id="B5.protocol.declared",
                status="partial" if thin else "pass",
                    message=(
                        f"Thin protocols (missing decision_rule): {thin}"
                        if thin
                        else None
                    ),
            )
        )

        b5_status = _status_from_checks(b5_checks)

        if mode == "lite" and b5_status == "fail":
            has_any_preds = any(
                    c.id == "B5.predictions.present"
                    and c.status == "pass"
                    for c in b5_checks
            )
            if not has_any_preds:
                b5_status = "partial"

        b5_reasons = [
            c.message
            for c in b5_checks
            if c.message and c.status in {"fail", "partial"}
        ]
        b5_suggestions = (
            [
                "Make predictions quantitative and bind them to a pre-registered "
                "decision rule",
            ]
            if b5_status != "pass"
            else []
        )
        levels["B5"] = LevelReport(
            status=b5_status,
            checks=b5_checks,
            reasons=b5_reasons,
            suggestions=b5_suggestions,
        )

    # -----------------
    # Overall
    # -----------------
    blocking_levels = [
        lvl
        for (lvl, rep) in levels.items()
        if rep.status == "fail" and lvl in {"B1", "B3", "B5"}
    ]

    base_map = {"pass": 1.0, "partial": 0.5, "fail": 0.0}
    base_raw = sum(
        base_map[levels[lvl].status]
        for lvl in ("B1", "B2", "B3", "B4", "B5")
    )
    spec_score = int(round((base_raw / 5.0) * 100))

    w_score = weighted_score(
        b1=levels["B1"].status,
        b2=levels["B2"].status,
        b3=levels["B3"].status,
        b4=levels["B4"].status,
        b5=levels["B5"].status,
        sabv=b4_sabv_status,
        blinding=b4_blinding_status,
        randomization=b4_random_status,
    )

    risk_flags: list[dict[str, str]] = []
    if levels["B4"].status != "pass":
        risk_flags.append({"id": "degrees_of_freedom", "level": "medium"})
    if levels["B3"].status != "pass":
        risk_flags.append({"id": "confounding_unaddressed", "level": "medium"})
    if levels["B4"].status == "fail":
        risk_flags.append({"id": "controls_or_circularity", "level": "high"})

    return {
        "tool": "echobio",
        "tool_version": "0.2.2",
        "claim_id": spec.claim_id,
        "overall": {
            "status": "pass" if not blocking_levels else "fail",
            "blocking_levels": blocking_levels,
            "spec_score_0_100": spec_score,
            "weighted_score_0_100": w_score,
            "mode": mode,
        },
        "levels": {
            lvl: {
                "status": rep.status,
                "checks": [
                    {"id": c.id, "status": c.status, "message": c.message}
                    for c in rep.checks
                ],
                "reasons": rep.reasons,
                "suggestions": rep.suggestions,
            }
            for (lvl, rep) in levels.items()
        },
        "risk_flags": risk_flags,
        "metadata": {"schema_version": spec.schema_version, "language": spec.language},
    }
