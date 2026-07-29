"""Constitutional Development Governance orchestration skeleton for G47-01A.

This module realizes only the immutable runtime structure and canonical stage
order frozen by the G47-00B implementation contract.  It performs structural
validation and in-memory composition.  It does not evaluate evidence, reduce
Need Assessment outcomes, decide Governance disposition, determine planning
eligibility, integrate a planner, serialize artifacts, write Replay, or
reconstruct persisted evidence.

The explicitly deferred public functions raise
``DevelopmentGovernanceDeferredImplementationError`` deterministically until
their owning implementation generations complete them.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from aigol.runtime.models import FailClosedRuntimeError


DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION = (
    "G47_01A_DEVELOPMENT_GOVERNANCE_RUNTIME_SKELETON_V1"
)

DEVELOPMENT_GOVERNANCE_TASK_INTAKE_ARTIFACT_V1 = (
    "DEVELOPMENT_GOVERNANCE_TASK_INTAKE_ARTIFACT_V1"
)
DEVELOPMENT_GOVERNANCE_CDD_CLASSIFICATION_ARTIFACT_V1 = (
    "DEVELOPMENT_GOVERNANCE_CDD_CLASSIFICATION_ARTIFACT_V1"
)
DEVELOPMENT_GOVERNANCE_EVIDENCE_SNAPSHOT_ARTIFACT_V1 = (
    "DEVELOPMENT_GOVERNANCE_EVIDENCE_SNAPSHOT_ARTIFACT_V1"
)
DEVELOPMENT_GOVERNANCE_NEED_ASSESSMENT_ARTIFACT_V1 = (
    "DEVELOPMENT_GOVERNANCE_NEED_ASSESSMENT_ARTIFACT_V1"
)
DEVELOPMENT_GOVERNANCE_DISPOSITION_ARTIFACT_V1 = (
    "DEVELOPMENT_GOVERNANCE_DISPOSITION_ARTIFACT_V1"
)
DEVELOPMENT_GOVERNANCE_PLANNING_ELIGIBILITY_ARTIFACT_V1 = (
    "DEVELOPMENT_GOVERNANCE_PLANNING_ELIGIBILITY_ARTIFACT_V1"
)
CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1 = (
    "CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1"
)

READ_ONLY = "READ_ONLY"
REPOSITORY_MUTATION_REQUESTED = "REPOSITORY_MUTATION_REQUESTED"
ACTION_MODES = frozenset({READ_ONLY, REPOSITORY_MUTATION_REQUESTED})

NEED_ASSESSMENT_OUTCOMES = frozenset(
    {
        "NO_IMPLEMENTATION_REQUIRED",
        "REUSE_EXISTING_UNCHANGED",
        "CANONICALIZATION_ONLY",
        "COMPLETE_EXISTING_REALIZATION",
        "IMPLEMENT_EXISTING_BINDING",
        "EXTEND_EXISTING_OWNER",
        "COMPOSE_EXISTING_CAPABILITIES",
        "NEW_REALIZATION_JUSTIFIED",
        "NEW_DISTINCT_CAPABILITY_JUSTIFIED",
        "ARCHITECTURAL_DUPLICATION",
        "UNJUSTIFIED_EXPANSION",
        "GOVERNANCE_REVIEW_REQUIRED",
        "FAILED_CLOSED",
    }
)

GOVERNANCE_DISPOSITIONS = frozenset(
    {
        "READ_ONLY_WORK_MAY_CONTINUE",
        "NO_IMPLEMENTATION_REQUIRED",
        "REUSE_REQUIRED",
        "CLARIFICATION_REQUIRED",
        "GOVERNANCE_REVIEW_REQUIRED",
        "BOUNDED_PLANNING_PERMITTED",
        "WORK_BLOCKED",
        "FAILED_CLOSED",
    }
)

TASK_INTAKE_STAGE = "TASK_INTAKE"
CDD_CLASSIFICATION_STAGE = "CDD_CLASSIFICATION"
EVIDENCE_SNAPSHOT_STAGE = "EVIDENCE_SNAPSHOT"
NEED_ASSESSMENT_STAGE = "NEED_ASSESSMENT"
GOVERNANCE_DISPOSITION_STAGE = "GOVERNANCE_DISPOSITION"
PLANNING_ELIGIBILITY_STAGE = "PLANNING_ELIGIBILITY"
CANONICAL_BUNDLE_STAGE = "CANONICAL_BUNDLE"

CANONICAL_STAGE_ORDER = (
    TASK_INTAKE_STAGE,
    CDD_CLASSIFICATION_STAGE,
    EVIDENCE_SNAPSHOT_STAGE,
    NEED_ASSESSMENT_STAGE,
    GOVERNANCE_DISPOSITION_STAGE,
    PLANNING_ELIGIBILITY_STAGE,
    CANONICAL_BUNDLE_STAGE,
)

DEFERRED_RESPONSIBILITIES = (
    "NEED_ASSESSMENT_PREDICATES",
    "EVIDENCE_EVALUATION",
    "GOVERNANCE_DISPOSITION_REDUCTION",
    "PLANNING_ELIGIBILITY_REDUCTION",
    "PLANNER_ADMISSIBILITY",
    "BUNDLE_HASHING",
    "SERIALIZATION",
    "RECONSTRUCTION",
    "DURABLE_WORK_BINDING",
    "REPLAY_INTEGRATION",
    "AICLI_INTEGRATION",
)


class DevelopmentGovernanceRuntimeError(FailClosedRuntimeError):
    """Raised when a G47 Development Governance structure is invalid."""


class DevelopmentGovernanceDeferredImplementationError(NotImplementedError):
    """Raised when a later G47 generation owns the requested behavior."""


@dataclass(frozen=True, slots=True)
class DevelopmentGovernanceTaskIntake:
    """Immutable, structurally validated Development Governance intake."""

    artifact_type: str
    runtime_version: str
    intake_id: str
    request_identity: str
    objective: str
    action_mode: str
    declared_work_products: tuple[str, ...]
    bounded_scope: tuple[str, ...]
    constraints: tuple[str, ...]
    non_goals: tuple[str, ...]
    active_baseline_reference: str
    clarification_requirements: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DevelopmentGovernanceCDDClassification:
    """Immutable structural representation of one completed CDD result."""

    artifact_type: str
    runtime_version: str
    cdd_id: str
    intake_id: str
    baseline_reference: str
    action_mode: str
    primary_work_class: str
    secondary_impacts: tuple[str, ...]
    mutation_layer: str
    constitutional_impact: str
    protocol_impact: str
    realization_category: str
    realization_impact: str
    capability_impact: str
    authority_impact: str
    owner: str
    affected_scope: tuple[str, ...]
    required_reviews: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    unresolved_fields: tuple[str, ...]
    termination_state: str


@dataclass(frozen=True, slots=True)
class DevelopmentGovernanceEvidenceReference:
    """Immutable structural reference to owner-supplied governance evidence."""

    evidence_id: str
    artifact_type: str
    artifact_version: str
    subject_id: str
    subject_type: str
    claim_type: str
    source_reference: str
    content_hash: str
    canonical_owner: str
    architectural_owner: str
    baseline_id: str
    certification_status: str
    certification_scope: str
    supersession_state: str
    compatibility_scope: str
    covered_facets: tuple[str, ...]
    known_limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DevelopmentGovernanceEvidenceSnapshot:
    """Immutable collection of structurally valid evidence references."""

    artifact_type: str
    runtime_version: str
    snapshot_id: str
    cdd_id: str
    baseline_reference: str
    evidence_items: tuple[DevelopmentGovernanceEvidenceReference, ...]


@dataclass(frozen=True, slots=True)
class DevelopmentGovernanceNeedAssessment:
    """Immutable structural representation of a Need Assessment result."""

    artifact_type: str
    runtime_version: str
    need_assessment_id: str
    cdd_id: str
    evidence_snapshot_id: str
    outcome: str
    covered_facets: tuple[str, ...]
    reusable_owners: tuple[str, ...]
    residual_gaps: tuple[str, ...]
    duplication_risks: tuple[str, ...]
    ownership_risks: tuple[str, ...]
    smallest_justified_change_class: str
    governance_impact: str
    replay_impact: str
    evidence_references: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DevelopmentGovernanceDisposition:
    """Immutable structural representation of Governance disposition."""

    artifact_type: str
    runtime_version: str
    disposition_id: str
    cdd_id: str
    need_assessment_id: str
    baseline_reference: str
    exact_scope: tuple[str, ...]
    governance_disposition: str
    review_references: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DevelopmentGovernancePlanningEligibility:
    """Immutable structural planning-eligibility boundary."""

    artifact_type: str
    runtime_version: str
    planning_eligibility_id: str
    disposition_id: str
    baseline_reference: str
    planning_eligible: bool
    residual_gap: tuple[str, ...]
    canonical_owners: tuple[str, ...]
    dependencies: tuple[str, ...]
    compatibility_requirements: tuple[str, ...]
    validation_requirements: tuple[str, ...]
    evidence_expectations: tuple[str, ...]
    replay_expectations: tuple[str, ...]
    certification_expectations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DevelopmentGovernanceStageReference:
    """Immutable in-memory reference to one canonical stage output."""

    stage: str
    artifact_type: str
    artifact_id: str


@dataclass(frozen=True, slots=True)
class ConstitutionalDevelopmentGovernanceBundle:
    """Immutable bundle skeleton containing ordered stage references only."""

    artifact_type: str
    runtime_version: str
    bundle_id: str
    baseline_reference: str
    stage_order: tuple[str, ...]
    stage_references: tuple[DevelopmentGovernanceStageReference, ...]


DevelopmentGovernanceStageArtifact: TypeAlias = (
    DevelopmentGovernanceTaskIntake
    | DevelopmentGovernanceCDDClassification
    | DevelopmentGovernanceEvidenceSnapshot
    | DevelopmentGovernanceNeedAssessment
    | DevelopmentGovernanceDisposition
    | DevelopmentGovernancePlanningEligibility
)


def orchestrate_constitutional_development_governance(
    *,
    bundle_id: str,
    task_intake: DevelopmentGovernanceTaskIntake,
    cdd_classification: DevelopmentGovernanceCDDClassification,
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
    need_assessment: DevelopmentGovernanceNeedAssessment,
    governance_disposition: DevelopmentGovernanceDisposition,
    planning_eligibility: DevelopmentGovernancePlanningEligibility,
) -> ConstitutionalDevelopmentGovernanceBundle:
    """Validate and compose all G47 stages in the frozen canonical order.

    The function deliberately performs no semantic reduction.  Every stage
    output is supplied by its owning stage, structurally validated through its
    public validator, and then referenced by the immutable bundle skeleton.
    Any exception terminates composition immediately.
    """

    intake = validate_development_governance_task_intake(task_intake)
    cdd = validate_cdd_classification(cdd_classification)
    evidence = validate_development_governance_evidence_snapshot(
        evidence_snapshot
    )
    need = validate_need_assessment(need_assessment)
    disposition = validate_development_governance_disposition(
        governance_disposition
    )
    eligibility = validate_planning_eligibility(planning_eligibility)

    _validate_stage_bindings(
        intake=intake,
        cdd=cdd,
        evidence=evidence,
        need=need,
        disposition=disposition,
        eligibility=eligibility,
    )

    bundle = ConstitutionalDevelopmentGovernanceBundle(
        artifact_type=(
            CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1
        ),
        runtime_version=DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        bundle_id=_require_string(bundle_id, "bundle_id"),
        baseline_reference=intake.active_baseline_reference,
        stage_order=CANONICAL_STAGE_ORDER,
        stage_references=(
            _stage_reference(TASK_INTAKE_STAGE, intake, intake.intake_id),
            _stage_reference(CDD_CLASSIFICATION_STAGE, cdd, cdd.cdd_id),
            _stage_reference(
                EVIDENCE_SNAPSHOT_STAGE,
                evidence,
                evidence.snapshot_id,
            ),
            _stage_reference(
                NEED_ASSESSMENT_STAGE,
                need,
                need.need_assessment_id,
            ),
            _stage_reference(
                GOVERNANCE_DISPOSITION_STAGE,
                disposition,
                disposition.disposition_id,
            ),
            _stage_reference(
                PLANNING_ELIGIBILITY_STAGE,
                eligibility,
                eligibility.planning_eligibility_id,
            ),
        ),
    )
    return validate_constitutional_development_governance_bundle(bundle)


def validate_development_governance_task_intake(
    artifact: DevelopmentGovernanceTaskIntake,
) -> DevelopmentGovernanceTaskIntake:
    """Validate Task Intake structure without interpreting its objective."""

    _require_instance(
        artifact,
        DevelopmentGovernanceTaskIntake,
        "task intake",
    )
    _require_envelope(
        artifact.artifact_type,
        DEVELOPMENT_GOVERNANCE_TASK_INTAKE_ARTIFACT_V1,
        artifact.runtime_version,
        "task intake",
    )
    _require_string(artifact.intake_id, "intake_id")
    _require_string(artifact.request_identity, "request_identity")
    _require_string(artifact.objective, "objective")
    _require_member(artifact.action_mode, ACTION_MODES, "action_mode")
    _require_string_tuple(
        artifact.declared_work_products,
        "declared_work_products",
    )
    _require_string_tuple(artifact.bounded_scope, "bounded_scope")
    _require_string_tuple(artifact.constraints, "constraints")
    _require_string_tuple(artifact.non_goals, "non_goals")
    _require_string(
        artifact.active_baseline_reference,
        "active_baseline_reference",
    )
    _require_string_tuple(
        artifact.clarification_requirements,
        "clarification_requirements",
    )
    return artifact


def validate_cdd_classification(
    artifact: DevelopmentGovernanceCDDClassification,
) -> DevelopmentGovernanceCDDClassification:
    """Validate CDD result structure without classifying constitutional work."""

    _require_instance(
        artifact,
        DevelopmentGovernanceCDDClassification,
        "CDD classification",
    )
    _require_envelope(
        artifact.artifact_type,
        DEVELOPMENT_GOVERNANCE_CDD_CLASSIFICATION_ARTIFACT_V1,
        artifact.runtime_version,
        "CDD classification",
    )
    for value, name in (
        (artifact.cdd_id, "cdd_id"),
        (artifact.intake_id, "intake_id"),
        (artifact.baseline_reference, "baseline_reference"),
        (artifact.primary_work_class, "primary_work_class"),
        (artifact.mutation_layer, "mutation_layer"),
        (artifact.constitutional_impact, "constitutional_impact"),
        (artifact.protocol_impact, "protocol_impact"),
        (artifact.realization_category, "realization_category"),
        (artifact.realization_impact, "realization_impact"),
        (artifact.capability_impact, "capability_impact"),
        (artifact.authority_impact, "authority_impact"),
        (artifact.owner, "owner"),
        (artifact.termination_state, "termination_state"),
    ):
        _require_string(value, name)
    _require_member(artifact.action_mode, ACTION_MODES, "action_mode")
    for value, name in (
        (artifact.secondary_impacts, "secondary_impacts"),
        (artifact.affected_scope, "affected_scope"),
        (artifact.required_reviews, "required_reviews"),
        (artifact.explicit_prohibitions, "explicit_prohibitions"),
        (artifact.unresolved_fields, "unresolved_fields"),
    ):
        _require_string_tuple(value, name)
    return artifact


def validate_development_governance_evidence_snapshot(
    artifact: DevelopmentGovernanceEvidenceSnapshot,
) -> DevelopmentGovernanceEvidenceSnapshot:
    """Validate evidence container structure without evaluating evidence."""

    _require_instance(
        artifact,
        DevelopmentGovernanceEvidenceSnapshot,
        "evidence snapshot",
    )
    _require_envelope(
        artifact.artifact_type,
        DEVELOPMENT_GOVERNANCE_EVIDENCE_SNAPSHOT_ARTIFACT_V1,
        artifact.runtime_version,
        "evidence snapshot",
    )
    _require_string(artifact.snapshot_id, "snapshot_id")
    _require_string(artifact.cdd_id, "cdd_id")
    _require_string(artifact.baseline_reference, "baseline_reference")
    if not isinstance(artifact.evidence_items, tuple):
        raise DevelopmentGovernanceRuntimeError(
            "evidence_items must be an immutable tuple"
        )
    for item in artifact.evidence_items:
        _validate_evidence_reference(item)
    return artifact


def validate_need_assessment(
    artifact: DevelopmentGovernanceNeedAssessment,
) -> DevelopmentGovernanceNeedAssessment:
    """Validate Need Assessment structure without evaluating predicates."""

    _require_instance(
        artifact,
        DevelopmentGovernanceNeedAssessment,
        "Need Assessment",
    )
    _require_envelope(
        artifact.artifact_type,
        DEVELOPMENT_GOVERNANCE_NEED_ASSESSMENT_ARTIFACT_V1,
        artifact.runtime_version,
        "Need Assessment",
    )
    for value, name in (
        (artifact.need_assessment_id, "need_assessment_id"),
        (artifact.cdd_id, "cdd_id"),
        (artifact.evidence_snapshot_id, "evidence_snapshot_id"),
        (
            artifact.smallest_justified_change_class,
            "smallest_justified_change_class",
        ),
        (artifact.governance_impact, "governance_impact"),
        (artifact.replay_impact, "replay_impact"),
    ):
        _require_string(value, name)
    _require_member(
        artifact.outcome,
        NEED_ASSESSMENT_OUTCOMES,
        "Need Assessment outcome",
    )
    for value, name in (
        (artifact.covered_facets, "covered_facets"),
        (artifact.reusable_owners, "reusable_owners"),
        (artifact.residual_gaps, "residual_gaps"),
        (artifact.duplication_risks, "duplication_risks"),
        (artifact.ownership_risks, "ownership_risks"),
        (artifact.evidence_references, "evidence_references"),
    ):
        _require_string_tuple(value, name)
    return artifact


def validate_development_governance_disposition(
    artifact: DevelopmentGovernanceDisposition,
) -> DevelopmentGovernanceDisposition:
    """Validate disposition structure without reducing upstream results."""

    _require_instance(
        artifact,
        DevelopmentGovernanceDisposition,
        "Governance disposition",
    )
    _require_envelope(
        artifact.artifact_type,
        DEVELOPMENT_GOVERNANCE_DISPOSITION_ARTIFACT_V1,
        artifact.runtime_version,
        "Governance disposition",
    )
    for value, name in (
        (artifact.disposition_id, "disposition_id"),
        (artifact.cdd_id, "cdd_id"),
        (artifact.need_assessment_id, "need_assessment_id"),
        (artifact.baseline_reference, "baseline_reference"),
    ):
        _require_string(value, name)
    _require_member(
        artifact.governance_disposition,
        GOVERNANCE_DISPOSITIONS,
        "governance_disposition",
    )
    _require_string_tuple(artifact.exact_scope, "exact_scope")
    _require_string_tuple(
        artifact.review_references,
        "review_references",
    )
    _require_string_tuple(
        artifact.explicit_prohibitions,
        "explicit_prohibitions",
    )
    return artifact


def validate_planning_eligibility(
    artifact: DevelopmentGovernancePlanningEligibility,
) -> DevelopmentGovernancePlanningEligibility:
    """Validate planning-eligibility structure without deciding eligibility."""

    _require_instance(
        artifact,
        DevelopmentGovernancePlanningEligibility,
        "planning eligibility",
    )
    _require_envelope(
        artifact.artifact_type,
        DEVELOPMENT_GOVERNANCE_PLANNING_ELIGIBILITY_ARTIFACT_V1,
        artifact.runtime_version,
        "planning eligibility",
    )
    for value, name in (
        (artifact.planning_eligibility_id, "planning_eligibility_id"),
        (artifact.disposition_id, "disposition_id"),
        (artifact.baseline_reference, "baseline_reference"),
    ):
        _require_string(value, name)
    if not isinstance(artifact.planning_eligible, bool):
        raise DevelopmentGovernanceRuntimeError(
            "planning_eligible must be boolean"
        )
    for value, name in (
        (artifact.residual_gap, "residual_gap"),
        (artifact.canonical_owners, "canonical_owners"),
        (artifact.dependencies, "dependencies"),
        (
            artifact.compatibility_requirements,
            "compatibility_requirements",
        ),
        (artifact.validation_requirements, "validation_requirements"),
        (artifact.evidence_expectations, "evidence_expectations"),
        (artifact.replay_expectations, "replay_expectations"),
        (
            artifact.certification_expectations,
            "certification_expectations",
        ),
        (artifact.explicit_prohibitions, "explicit_prohibitions"),
    ):
        _require_string_tuple(value, name)
    return artifact


def validate_constitutional_development_governance_bundle(
    artifact: ConstitutionalDevelopmentGovernanceBundle,
) -> ConstitutionalDevelopmentGovernanceBundle:
    """Validate canonical bundle structure and frozen stage ordering."""

    _require_instance(
        artifact,
        ConstitutionalDevelopmentGovernanceBundle,
        "Development Governance bundle",
    )
    _require_envelope(
        artifact.artifact_type,
        CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1,
        artifact.runtime_version,
        "Development Governance bundle",
    )
    _require_string(artifact.bundle_id, "bundle_id")
    _require_string(artifact.baseline_reference, "baseline_reference")
    if artifact.stage_order != CANONICAL_STAGE_ORDER:
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance stage order is invalid"
        )
    if not isinstance(artifact.stage_references, tuple):
        raise DevelopmentGovernanceRuntimeError(
            "stage_references must be an immutable tuple"
        )
    expected = CANONICAL_STAGE_ORDER[:-1]
    if len(artifact.stage_references) != len(expected):
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance stage references are incomplete"
        )
    for expected_stage, reference in zip(
        expected,
        artifact.stage_references,
    ):
        _require_instance(
            reference,
            DevelopmentGovernanceStageReference,
            "stage reference",
        )
        if reference.stage != expected_stage:
            raise DevelopmentGovernanceRuntimeError(
                "Development Governance stage reference order is invalid"
            )
        _require_string(reference.artifact_type, "stage artifact_type")
        _require_string(reference.artifact_id, "stage artifact_id")
    return artifact


def reconstruct_constitutional_development_governance_bundle(
    *,
    bundle: ConstitutionalDevelopmentGovernanceBundle,
    stage_outputs: tuple[DevelopmentGovernanceStageArtifact, ...],
) -> ConstitutionalDevelopmentGovernanceBundle:
    """Reconstruct a bundle after reconstruction logic is implemented."""

    del bundle, stage_outputs
    raise DevelopmentGovernanceDeferredImplementationError(
        "Development Governance reconstruction is deferred beyond G47-01A"
    )


def derive_bundle_state(
    governance_disposition: DevelopmentGovernanceDisposition,
) -> str:
    """Derive bundle state after disposition projection is implemented."""

    del governance_disposition
    raise DevelopmentGovernanceDeferredImplementationError(
        "Development Governance bundle-state derivation is deferred beyond "
        "G47-01A"
    )


def compose_governance_eligible_implementation_turn_durable_work_binding(
    *,
    planning_eligibility: DevelopmentGovernancePlanningEligibility,
    request: str,
    project_objective_artifact: dict[str, Any],
    knowledge_reuse_artifact: dict[str, Any],
    workspace_state: dict[str, Any] | None,
    workspace: str | Path,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Bind planning-eligible work after the dedicated integration generation."""

    del (
        planning_eligibility,
        request,
        project_objective_artifact,
        knowledge_reuse_artifact,
        workspace_state,
        workspace,
        created_at,
        replay_dir,
    )
    raise DevelopmentGovernanceDeferredImplementationError(
        "Development Governance durable-work binding is deferred beyond "
        "G47-01A"
    )


def _validate_evidence_reference(
    artifact: DevelopmentGovernanceEvidenceReference,
) -> None:
    _require_instance(
        artifact,
        DevelopmentGovernanceEvidenceReference,
        "evidence reference",
    )
    for value, name in (
        (artifact.evidence_id, "evidence_id"),
        (artifact.artifact_type, "evidence artifact_type"),
        (artifact.artifact_version, "evidence artifact_version"),
        (artifact.subject_id, "evidence subject_id"),
        (artifact.subject_type, "evidence subject_type"),
        (artifact.claim_type, "evidence claim_type"),
        (artifact.source_reference, "evidence source_reference"),
        (artifact.content_hash, "evidence content_hash"),
        (artifact.canonical_owner, "evidence canonical_owner"),
        (artifact.architectural_owner, "evidence architectural_owner"),
        (artifact.baseline_id, "evidence baseline_id"),
        (artifact.certification_status, "evidence certification_status"),
        (artifact.certification_scope, "evidence certification_scope"),
        (artifact.supersession_state, "evidence supersession_state"),
        (artifact.compatibility_scope, "evidence compatibility_scope"),
    ):
        _require_string(value, name)
    _require_string_tuple(artifact.covered_facets, "evidence covered_facets")
    _require_string_tuple(
        artifact.known_limitations,
        "evidence known_limitations",
    )


def _validate_stage_bindings(
    *,
    intake: DevelopmentGovernanceTaskIntake,
    cdd: DevelopmentGovernanceCDDClassification,
    evidence: DevelopmentGovernanceEvidenceSnapshot,
    need: DevelopmentGovernanceNeedAssessment,
    disposition: DevelopmentGovernanceDisposition,
    eligibility: DevelopmentGovernancePlanningEligibility,
) -> None:
    if cdd.intake_id != intake.intake_id:
        raise DevelopmentGovernanceRuntimeError(
            "CDD classification does not bind the validated Task Intake"
        )
    if evidence.cdd_id != cdd.cdd_id or need.cdd_id != cdd.cdd_id:
        raise DevelopmentGovernanceRuntimeError(
            "downstream stages do not bind the validated CDD classification"
        )
    if need.evidence_snapshot_id != evidence.snapshot_id:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment does not bind the validated evidence snapshot"
        )
    if (
        disposition.cdd_id != cdd.cdd_id
        or disposition.need_assessment_id != need.need_assessment_id
    ):
        raise DevelopmentGovernanceRuntimeError(
            "Governance disposition does not bind its upstream stages"
        )
    if eligibility.disposition_id != disposition.disposition_id:
        raise DevelopmentGovernanceRuntimeError(
            "planning eligibility does not bind Governance disposition"
        )
    baselines = {
        intake.active_baseline_reference,
        cdd.baseline_reference,
        evidence.baseline_reference,
        disposition.baseline_reference,
        eligibility.baseline_reference,
    }
    if len(baselines) != 1:
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance stages do not share one baseline"
        )
    if cdd.action_mode != intake.action_mode:
        raise DevelopmentGovernanceRuntimeError(
            "CDD action mode does not bind Task Intake action mode"
        )


def _stage_reference(
    stage: str,
    artifact: DevelopmentGovernanceStageArtifact,
    artifact_id: str,
) -> DevelopmentGovernanceStageReference:
    return DevelopmentGovernanceStageReference(
        stage=stage,
        artifact_type=_require_string(
            artifact.artifact_type,
            "stage artifact_type",
        ),
        artifact_id=_require_string(artifact_id, "stage artifact_id"),
    )


def _require_instance(value: Any, expected: type[Any], name: str) -> None:
    if not isinstance(value, expected):
        raise DevelopmentGovernanceRuntimeError(
            f"{name} must be {expected.__name__}"
        )


def _require_envelope(
    artifact_type: str,
    expected_artifact_type: str,
    runtime_version: str,
    name: str,
) -> None:
    if artifact_type != expected_artifact_type:
        raise DevelopmentGovernanceRuntimeError(
            f"{name} artifact type is invalid"
        )
    if runtime_version != DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION:
        raise DevelopmentGovernanceRuntimeError(
            f"{name} runtime version is invalid"
        )


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DevelopmentGovernanceRuntimeError(f"{name} is required")
    return value


def _require_member(value: Any, allowed: frozenset[str], name: str) -> str:
    candidate = _require_string(value, name)
    if candidate not in allowed:
        raise DevelopmentGovernanceRuntimeError(f"{name} is invalid")
    return candidate


def _require_string_tuple(value: Any, name: str) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise DevelopmentGovernanceRuntimeError(
            f"{name} must be an immutable tuple"
        )
    for item in value:
        _require_string(item, f"{name} item")
    return value


__all__ = [
    "ACTION_MODES",
    "CANONICAL_STAGE_ORDER",
    "CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1",
    "DEFERRED_RESPONSIBILITIES",
    "DEVELOPMENT_GOVERNANCE_CDD_CLASSIFICATION_ARTIFACT_V1",
    "DEVELOPMENT_GOVERNANCE_DISPOSITION_ARTIFACT_V1",
    "DEVELOPMENT_GOVERNANCE_EVIDENCE_SNAPSHOT_ARTIFACT_V1",
    "DEVELOPMENT_GOVERNANCE_NEED_ASSESSMENT_ARTIFACT_V1",
    "DEVELOPMENT_GOVERNANCE_PLANNING_ELIGIBILITY_ARTIFACT_V1",
    "DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION",
    "DEVELOPMENT_GOVERNANCE_TASK_INTAKE_ARTIFACT_V1",
    "GOVERNANCE_DISPOSITIONS",
    "NEED_ASSESSMENT_OUTCOMES",
    "READ_ONLY",
    "REPOSITORY_MUTATION_REQUESTED",
    "ConstitutionalDevelopmentGovernanceBundle",
    "DevelopmentGovernanceCDDClassification",
    "DevelopmentGovernanceDeferredImplementationError",
    "DevelopmentGovernanceDisposition",
    "DevelopmentGovernanceEvidenceReference",
    "DevelopmentGovernanceEvidenceSnapshot",
    "DevelopmentGovernanceNeedAssessment",
    "DevelopmentGovernancePlanningEligibility",
    "DevelopmentGovernanceRuntimeError",
    "DevelopmentGovernanceStageReference",
    "DevelopmentGovernanceTaskIntake",
    "compose_governance_eligible_implementation_turn_durable_work_binding",
    "derive_bundle_state",
    "orchestrate_constitutional_development_governance",
    "reconstruct_constitutional_development_governance_bundle",
    "validate_cdd_classification",
    "validate_constitutional_development_governance_bundle",
    "validate_development_governance_disposition",
    "validate_development_governance_evidence_snapshot",
    "validate_development_governance_task_intake",
    "validate_need_assessment",
    "validate_planning_eligibility",
]
