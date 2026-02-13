from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class I18nText(BaseModel):
    language: str = Field(description="BCP-47-ish language tag, e.g. en, fr, es, zh")
    text: str


class Provenance(BaseModel):
    source: Literal["user", "inferred", "unknown"] = "user"
    notes: str | None = None


class EntityIds(BaseModel):
    hgnc: str | None = None
    ensembl: str | None = None
    uniprot: str | None = None
    ncbi_gene: str | None = None


class Entity(BaseModel):
    kind: str
    name: str
    ids: EntityIds | None = None


class Species(BaseModel):
    name: str
    tax_id: int | None = None


class Variables(BaseModel):
    exposure_or_intervention: dict[str, Any]
    outcome: dict[str, Any]
    mediators: list[dict[str, Any]] = Field(default_factory=list)
    covariates_declared: list[str] = Field(default_factory=list)


class B1(BaseModel):
    entities: list[Entity]
    context: dict[str, Any]
    variables: Variables


class ModelSystem(BaseModel):
    description: str
    validity_notes: str | None = None


class Boundaries(BaseModel):
    time_window: str | None = None
    spatial_scope: str | None = None
    generalization_limits: list[str] = Field(default_factory=list)


class B2(BaseModel):
    biological_scale: str
    model_system: ModelSystem
    boundaries: Boundaries


class Dag(BaseModel):
    nodes: list[str] = Field(default_factory=list)
    edges: list[tuple[str, str]] = Field(default_factory=list)


class Confounder(BaseModel):
    name: str
    control_strategy: str | None = None


class Confounders(BaseModel):
    listed: list[Confounder] = Field(default_factory=list)


class CausalModel(BaseModel):
    type: Literal["pathway", "dag", "none"]
    statements: list[str] = Field(default_factory=list)


class B3(BaseModel):
    causal_model: CausalModel
    dag: Dag | None = None
    confounders: Confounders = Field(default_factory=Confounders)
    identification_notes: list[str] = Field(default_factory=list)


class PowerAnalysis(BaseModel):
    declared: bool
    endpoint: str | None = None
    effect_size_assumption: str | None = None
    alpha: float | None = None
    power: float | None = None
    planned_n_per_group: int | None = None


class AnalysisPlan(BaseModel):
    primary_endpoint: str | None = None
    secondary_endpoints: list[str] = Field(default_factory=list)
    multiple_testing: dict[str, Any] | None = None
    outlier_handling: str | None = None


class DesignControls(BaseModel):
    randomization: str | None = None
    blinding: str | None = None
    sabv: Literal["yes", "no", "partial"] | None = None
    power_analysis: PowerAnalysis | None = None
    exclusion_criteria: list[str] = Field(default_factory=list)
    analysis_plan: AnalysisPlan | None = None


class RRIDItem(BaseModel):
    kind: str
    rrid: str
    description: str | None = None


class Resources(BaseModel):
    rrids: list[RRIDItem] = Field(default_factory=list)
    cell_lines: list[dict[str, Any]] = Field(default_factory=list)


class CircularityGuards(BaseModel):
    discovery_data: list[str] = Field(default_factory=list)
    validation_data: list[str] = Field(default_factory=list)
    notes: str | None = None


class B4(BaseModel):
    design_controls: DesignControls
    resources: Resources = Field(default_factory=Resources)
    circularity_guards: CircularityGuards = Field(default_factory=CircularityGuards)


class IndependentPrediction(BaseModel):
    prediction_id: str
    is_independent: bool
    statement: str
    test_protocol: dict[str, Any] = Field(default_factory=dict)
    data_reference: dict[str, Any] = Field(default_factory=dict)
    falsifiers: list[str] = Field(default_factory=list)


class B5(BaseModel):
    independent_predictions: list[IndependentPrediction] = Field(default_factory=list)


class ClaimSpec(BaseModel):
    schema_version: str
    claim_id: str
    title: str
    claim_type: str
    domain_tags: list[str] = Field(default_factory=list)

    b1: B1
    b2: B2 | None = None
    b3: B3 | None = None
    b4: B4 | None = None
    b5: B5 | None = None
