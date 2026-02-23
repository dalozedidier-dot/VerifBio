# -*- coding: utf-8 -*-
# fmt: off
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


def _msg(status: LevelStatus, message: str) -> str | None:
    return None if status == "pass" else message


def audit_claim(spec: ClaimSpec, *, mode: Mode = "strict") -> dict[str, Any]:
    levels: dict[str, LevelReport] = {}

    # -----------------
    # B1
    # -----------------
    b1_checks: list[CheckResult] = []

    b1_entities_status: LevelStatus = "pass" if spec.b1.entities else "fail"
    b1_checks.append(
        CheckResult(
            "B1.entities.present",
            b1_entities_status,
            _msg(b1_entities_status, "No entities declared"),
        )
    )

    exp = spec.b1.variables.exposure_or_intervention
    out = spec.b1.variables.outcome

    b1_exp_status: LevelStatus = "pass" if exp.get("description") and exp.get("operationalization") else "fail"
    b1_checks.append(
        CheckResult(
            "B1.exposure.operationalized",
            b1_exp_status,
            _msg(
                b1_exp_status,
                "Exposure/intervention lacks description or operationalization",
            ),
        )
    )

    b1_out_status: LevelStatus = "pass" if out.get("description") and out.get("operationalization") else "fail"
    b1_checks.append(
        CheckResult(
            "B1.outcome.operationalized",
            b1_out_status,
            _msg(b1_out_status, "Outcome lacks description or operationalization"),
        )
    )

    b1_status = _status_from_checks(b1_checks)
    levels["B1"] = LevelReport(
        status=b1_status,
        checks=b1_checks,
        reasons=[c.message for c in b1_checks if c.status == "fail" and c.message],
        suggestions=(["Specify measurement operationalizations for exposure/outcome"] if b1_status != "pass" else []),
    )

    # -----------------
    # B2
    # -----------------
    if spec.b2 is None:
        levels["B2"] = LevelReport(
            status="fail",
            checks=[CheckResult("B2.present", "fail", "B2 section missing")],
            reasons=["B2 section missing"],
            suggestions=[
                "Declare biological scale, model validity, and boundaries (time/spatial/generalization limits)",
            ],
        )
    else:
        b2_checks: list[CheckResult] = []

        b2_scale_status: LevelStatus = "fail" if spec.b2.biological_scale.lower() in {"unspecified", "", "na"} else "pass"
        b2_checks.append(CheckResult("B2.scale.declared", b2_scale_status, _msg(b2_scale_status, "Biological scale unspecified")))

        b2_model_status: LevelStatus = "fail" if (not spec.b2.model_system.description or "not specified" in spec.b2.model_system.description.lower()) else "pass"
        b2_checks.append(CheckResult("B2.model_system.defined", b2_model_status, _msg(b2_model_status, "Model system not defined")))

        has_any_boundary = any(
            (
                bool(spec.b2.boundaries.time_window),
                bool(spec.b2.boundaries.spatial_scope),
                bool(spec.b2.boundaries.generalization_limits),
            )
        )
        b2_bound_status: LevelStatus = "pass" if has_any_boundary else "partial"
        b2_checks.append(CheckResult("B2.boundaries.present", b2_bound_status, _msg(b2_bound_status, "Boundaries are thin or missing")))

        b2_status = _status_from_checks(b2_checks)
        levels["B2"] = LevelReport(
            status=b2_status,
            checks=b2_checks,
            reasons=[c.message for c in b2_checks if c.status in {"fail", "partial"} and c.message],
            suggestions=(["Add explicit time window and generalization limits"] if b2_status != "pass" else []),
        )

    # -----------------
    # B3
    # -----------------
    if spec.b3 is None:
        levels["B3"] = LevelReport(
            status="fail",
            checks=[CheckResult("B3.present", "fail", "B3 section missing")],
            reasons=["B3 section missing"],
            suggestions=["Declare a causal mechanism or DAG and address plausible confounders"],
        )
    else:
        b3_checks: list[CheckResult] = []

        b3_mech_status: LevelStatus = "fail" if (spec.b3.causal_model.type == "none" or not spec.b3.causal_model.statements) else "pass"
        b3_checks.append(CheckResult("B3.mechanism.declared", b3_mech_status, _msg(b3_mech_status, "No causal mechanism/pathway statements")))

        confs = spec.b3.confounders.listed
        b3_conf_list_status: LevelStatus = "pass" if confs else "partial"
        b3_checks.append(CheckResult("B3.confounders.listed", b3_conf_list_status, _msg(b3_conf_list_status, "No confounders listed")))

        has_controls = any(bool(c.control_strategy) for c in confs)
        b3_conf_ctrl_status: LevelStatus = "pass" if has_controls else "partial"
        b3_checks.append(CheckResult("B3.confounders.controlled", b3_conf_ctrl_status, _msg(b3_conf_ctrl_status, "Confounders lack control strategies")))

        b3_status = _status_from_checks(b3_checks)
        levels["B3"] = LevelReport(
            status=b3_status,
            checks=b3_checks,
            reasons=[c.message for c in b3_checks if c.status in {"fail", "partial"} and c.message],
            suggestions=(["Provide minimal DAG nodes/edges and explicit control strategies"] if b3_status != "pass" else []),
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
            checks=[CheckResult("B4.present", "fail", "B4 section missing")],
            reasons=["B4 section missing"],
            suggestions=["Declare randomization/blinding/power, endpoints, exclusion criteria, and circularity guards"],
        )
    else:
        b4_checks: list[CheckResult] = []
        dc = spec.b4.design_controls

        b4_random_status = "pass" if dc.randomization else "partial"
        b4_blinding_status = "pass" if dc.blinding else "partial"

        b4_checks.append(CheckResult("B4.randomization.declared", b4_random_status, _msg(b4_random_status, "Randomization not declared")))
        b4_checks.append(CheckResult("B4.blinding.declared", b4_blinding_status, _msg(b4_blinding_status, "Blinding not declared")))

        if dc.sabv is None:
            b4_sabv_status = "partial"
            b4_checks.append(CheckResult("B4.sabv.declared", b4_sabv_status, "SABV (sex as a biological variable) not declared"))
        elif dc.sabv == "yes":
            b4_sabv_status = "pass"
            b4_checks.append(CheckResult("B4.sabv.declared", b4_sabv_status))
        elif dc.sabv == "partial":
            b4_sabv_status = "partial"
            b4_checks.append(CheckResult("B4.sabv.declared", b4_sabv_status, "SABV partial (single-sex or limited reporting)"))
        else:
            b4_sabv_status = "fail"
            b4_checks.append(CheckResult("B4.sabv.declared", b4_sabv_status, "SABV not addressed"))

        pa = dc.power_analysis
        b4_power_status: LevelStatus = "pass" if (pa is not None and pa.declared) else "partial"
        b4_checks.append(CheckResult("B4.power.declared", b4_power_status, _msg(b4_power_status, "Power analysis not declared")))

        ap = dc.analysis_plan
        b4_ep_status: LevelStatus = "pass" if (ap is not None and ap.primary_endpoint) else "partial"
        b4_checks.append(CheckResult("B4.primary_endpoint.locked", b4_ep_status, _msg(b4_ep_status, "Primary endpoint not locked")))

        rrids = spec.b4.resources.rrids
        if rrids:
            bad = [r.rrid for r in rrids if not _RRID_RE.match(r.rrid)]
            if bad:
                b4_checks.append(CheckResult("B4.rrids.valid", "fail", f"Invalid RRID format: {bad}"))
            else:
                b4_checks.append(CheckResult("B4.rrids.valid", "pass"))
        else:
            b4_checks.append(CheckResult("B4.rrids.present", "partial", "No RRIDs declared (may be ok depending on claim)"))

        disc = set(spec.b4.circularity_guards.discovery_data)
        val = set(spec.b4.circularity_guards.validation_data)
        overlap = sorted(disc.intersection(val))
        if overlap:
            b4_checks.append(CheckResult("B4.circularity.no_overlap", "fail", f"Discovery/validation overlap: {overlap}"))
        else:
            b4_checks.append(CheckResult("B4.circularity.no_overlap", "pass"))

        b4_status = _status_from_checks(b4_checks)
        if mode == "lite" and b4_status == "fail":
            has_hard_fail = any(c.id == "B4.circularity.no_overlap" and c.status == "fail" for c in b4_checks)
            if not has_hard_fail:
                b4_status = "partial"

        levels["B4"] = LevelReport(
            status=b4_status,
            checks=b4_checks,
            reasons=[c.message for c in b4_checks if c.status in {"fail", "partial"} and c.message],
            suggestions=(["Lock endpoints and analysis degrees of freedom; separate discovery vs validation explicitly"] if b4_status != "pass" else []),
        )

    # -----------------
    # B5
    # -----------------
    if spec.b5 is None:
        levels["B5"] = LevelReport(
            status="fail",
            checks=[CheckResult("B5.present", "fail", "B5 section missing")],
            reasons=["B5 section missing"],
            suggestions=["Add at least one independent prediction with protocol, decision rule, and independent data reference"],
        )
    else:
        b5_checks: list[CheckResult] = []
        preds = spec.b5.independent_predictions

        b5_pred_present_status: LevelStatus = "pass" if preds else "fail"
        b5_checks.append(CheckResult("B5.predictions.present", b5_pred_present_status, _msg(b5_pred_present_status, "No independent predictions provided")))

        any_ind = any(p.is_independent for p in preds)
        b5_ind_status: LevelStatus = "pass" if any_ind else "fail"
        b5_checks.append(CheckResult("B5.is_independent.true", b5_ind_status, _msg(b5_ind_status, "No prediction marked is_independent: true")))

        thin = [p.prediction_id for p in preds if not p.test_protocol or "decision_rule" not in p.test_protocol]
        b5_proto_status: LevelStatus = "partial" if thin else "pass"
        b5_checks.append(CheckResult("B5.protocol.declared", b5_proto_status, _msg(b5_proto_status, f"Thin protocols (missing decision_rule): {thin}")))

        b5_status = _status_from_checks(b5_checks)
        if mode == "lite" and b5_status == "fail":
            has_preds_present = any(c.id == "B5.predictions.present" and c.status == "pass" for c in b5_checks)
            if not has_preds_present:
                b5_status = "partial"

        levels["B5"] = LevelReport(
            status=b5_status,
            checks=b5_checks,
            reasons=[c.message for c in b5_checks if c.status in {"fail", "partial"} and c.message],
            suggestions=(["Make predictions quantitative and bind them to a pre-registered decision rule"] if b5_status != "pass" else []),
        )

    # -----------------
    # Overall
    # -----------------
    blocking = [lvl for lvl, rep in levels.items() if rep.status == "fail" and lvl in {"B1", "B3", "B5"}]

    score_map = {"pass": 1.0, "partial": 0.5, "fail": 0.0}
    raw = sum(score_map[levels[k].status] for k in ("B1", "B2", "B3", "B4", "B5"))
    spec_score = int(round((raw / 5.0) * 100))

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
        "tool": "verifbio",
        "tool_version": "0.2.0",
        "claim_id": spec.claim_id,
        "overall": {
            "status": "pass" if not blocking else "fail",
            "blocking_levels": blocking,
            "spec_score_0_100": spec_score,
            "weighted_score_0_100": w_score,
            "mode": mode,
        },
        "levels": {
            k: {
                "status": v.status,
                "checks": [{"id": c.id, "status": c.status, "message": c.message} for c in v.checks],
                "reasons": v.reasons,
                "suggestions": v.suggestions,
            }
            for k, v in levels.items()
        },
        "risk_flags": risk_flags,
        "metadata": {"schema_version": spec.schema_version, "language": spec.language},
    }
