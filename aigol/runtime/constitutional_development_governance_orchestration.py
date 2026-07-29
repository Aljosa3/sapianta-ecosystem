"""Constitutional Development Governance runtime through G47-01C-R02.

This module realizes the immutable runtime structure, canonical stage order,
and deterministic constitutional semantics frozen by the G47-00B
implementation contract.  It validates evidence, evaluates Need Assessment
predicates without priority, reduces Governance disposition, and validates
planning eligibility.  It canonically serializes, hashes, validates, and
reconstructs the reference-only Governance bundle.  It does not integrate a
planner, persist Replay, or reconstruct a Replay protocol.

G47-01D completes the mechanical bundle-state and governance-eligible
durable-work projections without changing the certified decision reductions.
The deferred exception type remains public for API compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
import hashlib
from pathlib import Path
import re
from typing import Any, TypeAlias

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    lookup_platform_capability_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION = (
    "G47_01C_DEVELOPMENT_GOVERNANCE_CANONICAL_BUNDLE_RUNTIME_V1"
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

PRIMARY_WORK_CLASSES = frozenset(
    {
        "CONSTITUTIONAL",
        "PROTOCOL",
        "REALIZATION",
        "CAPABILITY",
        "IMPLEMENTATION_CATEGORY",
        "IMPLEMENTATION_ONLY",
    }
)
MUTATION_LAYERS = frozenset(
    {
        "L0",
        "L1",
        "L2",
        "L3",
        "L4",
        "MULTIPLE",
        "NOT_APPLICABLE",
        "UNRESOLVED",
    }
)
CONSTITUTIONAL_IMPACTS = frozenset(
    {
        "NONE",
        "CONSTITUTIONAL_PRINCIPLE_CHANGE",
        "STABLE_SUBSTRATE_CHANGE",
        "UNRESOLVED",
    }
)
PROTOCOL_IMPACTS = frozenset(
    {
        "NONE",
        "NEW_PROTOCOL",
        "EXISTING_PROTOCOL_CHANGE",
        "PROTOCOL_REALIZATION_ONLY",
        "UNRESOLVED",
    }
)
REALIZATION_CATEGORIES = frozenset(
    {
        "REFERENCE_REALIZATION_REFINEMENT",
        "PROTOCOL_REALIZATION",
        "CAPABILITY_RUNTIME",
        "DOMAIN_RUNTIME",
        "WORKER",
        "PROVIDER",
        "ADAPTER",
        "INTERFACE",
        "TOOLING",
        "OTHER",
        "NOT_APPLICABLE",
        "UNRESOLVED",
    }
)
REALIZATION_IMPACTS = frozenset(
    {"NONE", "COMPLETE", "REFINE", "NEW", "REPLACE", "UNRESOLVED"}
)
CAPABILITY_IMPACTS = frozenset(
    {"NONE", "REUSE", "COMPOSE", "EXTEND", "NEW", "UNRESOLVED"}
)
AUTHORITY_IMPACTS = frozenset(
    {
        "NONE",
        "HUMAN_AUTHORITY",
        "GOVERNANCE_AUTHORITY",
        "MUTATION_AUTHORIZATION",
        "EXECUTION_AUTHORITY",
        "MULTIPLE",
        "UNRESOLVED",
    }
)
CDD_TERMINATION_STATES = frozenset(
    {
        "CLASSIFIED",
        "CLARIFICATION_REQUIRED",
        "GOVERNANCE_REVIEW_REQUIRED",
        "BLOCKED",
        "FAILED_CLOSED",
    }
)

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

SUBSTANTIVE_NEED_OUTCOMES = frozenset(
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

SUPPORTED_EVIDENCE_VERSION = "V1"
_SUPPORTED_EVIDENCE_TYPE_CONTRACTS = {
    "DEVELOPMENT_GOVERNANCE_EVIDENCE_V1": {
        "artifact_version": SUPPORTED_EVIDENCE_VERSION,
        "authority_registry_version": (
            PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION
        ),
        "source_reference_binding": "CERTIFICATION_EVIDENCE",
        "content_hash_binding": "AUTHORITATIVE_SOURCE_BYTES",
        "compatibility_scope_binding": "CDD_BASELINE",
        "supersession_binding": "CERTIFICATION_RECORD",
    },
}
SUPPORTED_CERTIFICATION_STATES = frozenset(
    {
        "CERTIFIED",
        "VERIFIED",
        "NOT_REQUIRED",
        "UNCERTIFIED",
        "REJECTED",
        "INCOMPLETE",
        "SUPERSEDED",
    }
)
CERTIFICATION_SATISFIED_STATES = frozenset({"CERTIFIED", "VERIFIED"})
SUPPORTED_COMPATIBILITY_STATES = frozenset(
    {"COMPATIBLE", "INCOMPATIBLE", "NOT_APPLICABLE", "UNKNOWN"}
)
SUPPORTED_SUPERSESSION_STATES = frozenset(
    {"CURRENT", "SUPERSEDED", "HISTORICAL"}
)
SUPPORTED_EVIDENCE_SUBJECT_TYPES = frozenset(
    {
        "CONSTITUTION",
        "STABLE_SUBSTRATE",
        "PROTOCOL",
        "REALIZATION",
        "CAPABILITY",
        "COMPOSITION",
        "DOMAIN",
        "ADAPTER",
        "WORKER",
        "PROVIDER",
        "INTERFACE",
        "GOVERNANCE",
        "REPLAY",
        "CERTIFICATION",
        "IMPLEMENTATION",
        "BINDING",
    }
)

SUPPORTED_EVIDENCE_CLAIMS = {
    "OBJECTIVE_FACET_COVERAGE": frozenset({"COVERED", "UNCOVERED"}),
    "IMPLEMENTATION_REQUIREMENT": frozenset({"NONE", "REQUIRED"}),
    "REQUESTED_RESULT_STATE": frozenset(
        {"ALREADY_PRODUCED_ACCEPTED", "NOT_PRODUCED", "UNKNOWN"}
    ),
    "REQUESTER_AMBIGUITY": frozenset({"ABSENT", "PRESENT"}),
    "CONSTITUTIONAL_AMBIGUITY": frozenset({"ABSENT", "PRESENT"}),
    "REQUESTED_STRUCTURE_RELATION": frozenset(
        {
            "NEUTRAL",
            "REUSE_ACCEPTED",
            "DUPLICATES_EXISTING",
            "EXPANDS_SCOPE",
        }
    ),
    "CANONICALIZATION_SCOPE": frozenset(
        {"EXCLUSIVE", "NOT_EXCLUSIVE", "NOT_APPLICABLE"}
    ),
    "REALIZATION_COMPLETENESS": frozenset(
        {"INCOMPLETE", "COMPLETE", "UNKNOWN", "NOT_APPLICABLE"}
    ),
    "BINDING_STATE": frozenset(
        {
            "MISSING_EXISTING_CONTRACT",
            "PRESENT",
            "UNKNOWN",
            "NOT_APPLICABLE",
        }
    ),
    "OWNER_EXTENSION_FIT": frozenset(
        {"WITHIN_OWNER", "OUTSIDE_OWNER", "UNKNOWN", "NOT_APPLICABLE"}
    ),
    "COMPOSITION_COVERAGE": frozenset(
        {"COMPLETE", "INCOMPLETE", "UNKNOWN", "NOT_APPLICABLE"}
    ),
    "EXISTING_CONTRACT": frozenset({"EXISTS", "ABSENT", "UNKNOWN"}),
    "REALIZATION_AVAILABILITY": frozenset(
        {
            "NO_CURRENT_REALIZATION",
            "CURRENT_REALIZATION_AVAILABLE",
            "UNKNOWN",
        }
    ),
    "CONSTITUTIONAL_DISTINCTION": frozenset(
        {"DISTINCT", "NOT_DISTINCT", "UNKNOWN"}
    ),
    "SMALLER_CHANGE_OPTIONS": frozenset(
        {"DISPROVEN", "AVAILABLE", "UNKNOWN"}
    ),
    "ARCHITECTURAL_DUPLICATION": frozenset(
        {"PROVEN", "SUSPECTED", "DISPROVEN"}
    ),
    "EXPANSION_JUSTIFICATION": frozenset(
        {"JUSTIFIED", "UNRESOLVED", "UNJUSTIFIED", "NOT_APPLICABLE"}
    ),
}

SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

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

STAGE_ARTIFACT_TYPES = {
    TASK_INTAKE_STAGE: DEVELOPMENT_GOVERNANCE_TASK_INTAKE_ARTIFACT_V1,
    CDD_CLASSIFICATION_STAGE: (
        DEVELOPMENT_GOVERNANCE_CDD_CLASSIFICATION_ARTIFACT_V1
    ),
    EVIDENCE_SNAPSHOT_STAGE: (
        DEVELOPMENT_GOVERNANCE_EVIDENCE_SNAPSHOT_ARTIFACT_V1
    ),
    NEED_ASSESSMENT_STAGE: (
        DEVELOPMENT_GOVERNANCE_NEED_ASSESSMENT_ARTIFACT_V1
    ),
    GOVERNANCE_DISPOSITION_STAGE: (
        DEVELOPMENT_GOVERNANCE_DISPOSITION_ARTIFACT_V1
    ),
    PLANNING_ELIGIBILITY_STAGE: (
        DEVELOPMENT_GOVERNANCE_PLANNING_ELIGIBILITY_ARTIFACT_V1
    ),
}

DEFERRED_RESPONSIBILITIES: tuple[str, ...] = ()


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
    claim_value: str
    source_reference: str
    content_hash: str
    canonical_owner: str
    architectural_owner: str
    baseline_id: str
    certification_status: str
    certification_scope: str
    certification_required: bool
    supersession_state: str
    compatibility_scope: str
    compatibility_status: str
    reconstruction_required: bool
    covered_facets: tuple[str, ...]
    known_limitations: tuple[str, ...]
    residual_responsibilities: tuple[str, ...]
    declared_responsibilities: tuple[str, ...]
    implemented_responsibilities: tuple[str, ...]
    source_endpoint: str | None
    target_endpoint: str | None
    interface_identity: str | None
    interface_version: str | None


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
    objective_facets: tuple[str, ...]
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
    """Immutable hash-bound reference to one canonical stage output."""

    stage: str
    artifact_type: str
    artifact_id: str
    artifact_hash: str


@dataclass(frozen=True, slots=True)
class ConstitutionalDevelopmentGovernanceBundle:
    """Immutable canonical bundle containing ordered references and hashes."""

    artifact_type: str
    runtime_version: str
    bundle_id: str
    bundle_identity: str
    baseline_reference: str
    stage_order: tuple[str, ...]
    stage_references: tuple[DevelopmentGovernanceStageReference, ...]
    bundle_hash: str


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

    Every stage output is supplied by its owning stage, validated through its
    public validator, and then referenced by the immutable bundle.  Need,
    disposition, and eligibility semantics are mechanically checked against
    their complete upstream context.  Any exception terminates composition
    immediately.
    """

    intake = validate_development_governance_task_intake(task_intake)
    cdd = validate_cdd_classification(cdd_classification)
    evidence = validate_development_governance_evidence_snapshot(
        evidence_snapshot,
        expected_cdd_id=cdd.cdd_id,
        expected_baseline=cdd.baseline_reference,
    )
    need = validate_need_assessment(
        need_assessment,
        task_intake=intake,
        cdd_classification=cdd,
        evidence_snapshot=evidence,
    )
    disposition = validate_development_governance_disposition(
        governance_disposition,
        task_intake=intake,
        cdd_classification=cdd,
        evidence_snapshot=evidence,
        need_assessment=need,
    )
    eligibility = validate_planning_eligibility(
        planning_eligibility,
        need_assessment=need,
        governance_disposition=disposition,
    )

    _validate_stage_bindings(
        intake=intake,
        cdd=cdd,
        evidence=evidence,
        need=need,
        disposition=disposition,
        eligibility=eligibility,
    )

    stage_references = (
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
    )
    identity = _generate_bundle_identity(
        baseline_reference=intake.active_baseline_reference,
        stage_references=stage_references,
    )
    bundle = ConstitutionalDevelopmentGovernanceBundle(
        artifact_type=(
            CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1
        ),
        runtime_version=DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        bundle_id=_require_string(bundle_id, "bundle_id"),
        bundle_identity=identity,
        baseline_reference=intake.active_baseline_reference,
        stage_order=CANONICAL_STAGE_ORDER,
        stage_references=stage_references,
        bundle_hash="",
    )
    bundle = replace(bundle, bundle_hash=_canonical_artifact_hash(bundle))
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
    for value, name in (
        (artifact.declared_work_products, "declared_work_products"),
        (artifact.bounded_scope, "bounded_scope"),
        (artifact.constraints, "constraints"),
        (artifact.non_goals, "non_goals"),
        (
            artifact.clarification_requirements,
            "clarification_requirements",
        ),
    ):
        _require_string_tuple(value, name)
        _require_canonical_tuple(value, name)
    _require_string(
        artifact.active_baseline_reference,
        "active_baseline_reference",
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
        (artifact.owner, "owner"),
    ):
        _require_string(value, name)
    _require_member(artifact.action_mode, ACTION_MODES, "action_mode")
    for value, allowed, name in (
        (
            artifact.primary_work_class,
            PRIMARY_WORK_CLASSES,
            "primary_work_class",
        ),
        (artifact.mutation_layer, MUTATION_LAYERS, "mutation_layer"),
        (
            artifact.constitutional_impact,
            CONSTITUTIONAL_IMPACTS,
            "constitutional_impact",
        ),
        (artifact.protocol_impact, PROTOCOL_IMPACTS, "protocol_impact"),
        (
            artifact.realization_category,
            REALIZATION_CATEGORIES,
            "realization_category",
        ),
        (
            artifact.realization_impact,
            REALIZATION_IMPACTS,
            "realization_impact",
        ),
        (
            artifact.capability_impact,
            CAPABILITY_IMPACTS,
            "capability_impact",
        ),
        (
            artifact.authority_impact,
            AUTHORITY_IMPACTS,
            "authority_impact",
        ),
        (
            artifact.termination_state,
            CDD_TERMINATION_STATES,
            "termination_state",
        ),
    ):
        _require_member(value, allowed, name)
    for value, name in (
        (artifact.secondary_impacts, "secondary_impacts"),
        (artifact.affected_scope, "affected_scope"),
        (artifact.required_reviews, "required_reviews"),
        (artifact.explicit_prohibitions, "explicit_prohibitions"),
        (artifact.unresolved_fields, "unresolved_fields"),
    ):
        _require_string_tuple(value, name)
        _require_canonical_tuple(value, name)
    return artifact


def validate_development_governance_evidence_snapshot(
    artifact: DevelopmentGovernanceEvidenceSnapshot,
    *,
    expected_cdd_id: str | None = None,
    expected_baseline: str | None = None,
) -> DevelopmentGovernanceEvidenceSnapshot:
    """Validate the canonical Evidence Validity Predicate and conflicts."""

    if expected_cdd_id is None or expected_baseline is None:
        raise DevelopmentGovernanceRuntimeError(
            "evidence validation requires authoritative CDD and baseline context"
        )
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
    if artifact.cdd_id != expected_cdd_id:
        raise DevelopmentGovernanceRuntimeError(
            "evidence snapshot does not bind the expected CDD classification"
        )
    if artifact.baseline_reference != expected_baseline:
        raise DevelopmentGovernanceRuntimeError(
            "evidence snapshot baseline differs from CDD"
        )
    if not isinstance(artifact.evidence_items, tuple):
        raise DevelopmentGovernanceRuntimeError(
            "evidence_items must be an immutable tuple"
        )
    seen_ids: set[str] = set()
    hashes_by_source: dict[str, str] = {}
    claims_by_authority: dict[
        tuple[str, str, str],
        list[DevelopmentGovernanceEvidenceReference],
    ] = {}
    for item in artifact.evidence_items:
        _validate_evidence_reference(
            item,
            expected_baseline=artifact.baseline_reference,
        )
        if item.evidence_id in seen_ids:
            raise DevelopmentGovernanceRuntimeError(
                "evidence snapshot contains duplicate evidence identity"
            )
        seen_ids.add(item.evidence_id)
        prior_hash = hashes_by_source.setdefault(
            item.source_reference,
            item.content_hash,
        )
        if prior_hash != item.content_hash:
            raise DevelopmentGovernanceRuntimeError(
                "evidence source resolves to conflicting content hashes"
            )
        _register_authoritative_claim(
            claims_by_authority,
            item,
        )
    return artifact


def validate_need_assessment(
    artifact: DevelopmentGovernanceNeedAssessment,
    *,
    task_intake: DevelopmentGovernanceTaskIntake | None = None,
    cdd_classification: DevelopmentGovernanceCDDClassification | None = None,
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot | None = None,
) -> DevelopmentGovernanceNeedAssessment:
    """Validate structure and, with context, all frozen Need predicates."""

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
    _require_member(
        artifact.smallest_justified_change_class,
        NEED_ASSESSMENT_OUTCOMES,
        "smallest_justified_change_class",
    )
    for value, name in (
        (artifact.objective_facets, "objective_facets"),
        (artifact.covered_facets, "covered_facets"),
        (artifact.reusable_owners, "reusable_owners"),
        (artifact.residual_gaps, "residual_gaps"),
        (artifact.duplication_risks, "duplication_risks"),
        (artifact.ownership_risks, "ownership_risks"),
        (artifact.evidence_references, "evidence_references"),
    ):
        _require_string_tuple(value, name)
        _require_canonical_tuple(value, name)
    if (
        task_intake is None
        or cdd_classification is None
        or evidence_snapshot is None
    ):
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment semantic validation requires complete context"
        )
    validate_development_governance_task_intake(task_intake)
    validate_cdd_classification(cdd_classification)
    validate_development_governance_evidence_snapshot(
        evidence_snapshot,
        expected_cdd_id=cdd_classification.cdd_id,
        expected_baseline=cdd_classification.baseline_reference,
    )
    expected = _evaluate_need_assessment_outcome(
        artifact=artifact,
        task_intake=task_intake,
        cdd_classification=cdd_classification,
        evidence_snapshot=evidence_snapshot,
    )
    if artifact.outcome != expected:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment outcome does not match deterministic predicates"
        )
    if artifact.smallest_justified_change_class != expected:
        raise DevelopmentGovernanceRuntimeError(
            "smallest_justified_change_class must match the Need outcome"
        )
    return artifact


def validate_development_governance_disposition(
    artifact: DevelopmentGovernanceDisposition,
    *,
    task_intake: DevelopmentGovernanceTaskIntake | None = None,
    cdd_classification: DevelopmentGovernanceCDDClassification | None = None,
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot | None = None,
    need_assessment: DevelopmentGovernanceNeedAssessment | None = None,
) -> DevelopmentGovernanceDisposition:
    """Validate structure and the frozen Governance disposition reduction."""

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
    _require_canonical_tuple(artifact.exact_scope, "exact_scope")
    _require_canonical_tuple(
        artifact.review_references,
        "review_references",
    )
    _require_canonical_tuple(
        artifact.explicit_prohibitions,
        "explicit_prohibitions",
    )
    if (
        task_intake is None
        or cdd_classification is None
        or evidence_snapshot is None
        or need_assessment is None
    ):
        raise DevelopmentGovernanceRuntimeError(
            "Governance disposition validation requires complete context"
        )
    expected = _reduce_governance_disposition(
        task_intake=task_intake,
        cdd_classification=cdd_classification,
        evidence_snapshot=evidence_snapshot,
        need_assessment=need_assessment,
        review_references=artifact.review_references,
    )
    if artifact.governance_disposition != expected:
        raise DevelopmentGovernanceRuntimeError(
            "Governance disposition does not match deterministic reduction"
        )
    if artifact.exact_scope != cdd_classification.affected_scope:
        raise DevelopmentGovernanceRuntimeError(
            "Governance disposition scope differs from CDD scope"
        )
    return artifact


def validate_planning_eligibility(
    artifact: DevelopmentGovernancePlanningEligibility,
    *,
    need_assessment: DevelopmentGovernanceNeedAssessment | None = None,
    governance_disposition: DevelopmentGovernanceDisposition | None = None,
) -> DevelopmentGovernancePlanningEligibility:
    """Validate structure and the constitutional eligibility reduction."""

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
        _require_canonical_tuple(value, name)
    if need_assessment is None or governance_disposition is None:
        raise DevelopmentGovernanceRuntimeError(
            "planning eligibility validation requires complete context"
        )
    expected_eligible = (
        governance_disposition.governance_disposition
        == "BOUNDED_PLANNING_PERMITTED"
    )
    if artifact.planning_eligible is not expected_eligible:
        raise DevelopmentGovernanceRuntimeError(
            "planning eligibility does not match Governance disposition"
        )
    if expected_eligible:
        if artifact.residual_gap != need_assessment.residual_gaps:
            raise DevelopmentGovernanceRuntimeError(
                "planning eligibility does not bind the exact residual gap"
            )
        if artifact.canonical_owners != need_assessment.reusable_owners:
            raise DevelopmentGovernanceRuntimeError(
                "planning eligibility does not bind canonical owners"
            )
    elif artifact.residual_gap or artifact.canonical_owners:
        raise DevelopmentGovernanceRuntimeError(
            "ineligible planning artifact must not expose planning scope"
        )
    return artifact


def validate_constitutional_development_governance_bundle(
    artifact: ConstitutionalDevelopmentGovernanceBundle,
) -> ConstitutionalDevelopmentGovernanceBundle:
    """Validate bundle structure, ordering, identity, and canonical hash."""

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
    _require_string(artifact.bundle_identity, "bundle_identity")
    _require_string(artifact.baseline_reference, "baseline_reference")
    if not artifact.bundle_identity.startswith("DG-BUNDLE:sha256:"):
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance bundle identity is invalid"
        )
    _require_hash(artifact.bundle_hash, "bundle_hash")
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
    seen_artifact_ids: set[str] = set()
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
        if (
            reference.artifact_type
            != STAGE_ARTIFACT_TYPES[expected_stage]
        ):
            raise DevelopmentGovernanceRuntimeError(
                "Development Governance stage artifact type is invalid"
            )
        _require_string(reference.artifact_id, "stage artifact_id")
        _require_hash(reference.artifact_hash, "stage artifact_hash")
        if reference.artifact_id in seen_artifact_ids:
            raise DevelopmentGovernanceRuntimeError(
                "Development Governance stage artifact identity is duplicated"
            )
        seen_artifact_ids.add(reference.artifact_id)
    expected_identity = _generate_bundle_identity(
        baseline_reference=artifact.baseline_reference,
        stage_references=artifact.stage_references,
    )
    if artifact.bundle_identity != expected_identity:
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance bundle identity mismatch"
        )
    if artifact.bundle_hash != _canonical_artifact_hash(artifact):
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance bundle hash mismatch"
        )
    return artifact


def serialize_constitutional_development_governance_bundle(
    artifact: ConstitutionalDevelopmentGovernanceBundle,
) -> str:
    """Return the validated bundle in canonical JSON form."""

    bundle = validate_constitutional_development_governance_bundle(artifact)
    return canonical_serialize(_canonical_value(bundle))


def reconstruct_constitutional_development_governance_bundle(
    *,
    bundle: ConstitutionalDevelopmentGovernanceBundle,
    stage_outputs: tuple[DevelopmentGovernanceStageArtifact, ...],
) -> ConstitutionalDevelopmentGovernanceBundle:
    """Rebuild and verify a bundle from its ordered stage outputs."""

    source_bundle = validate_constitutional_development_governance_bundle(
        bundle
    )
    if not isinstance(stage_outputs, tuple):
        raise DevelopmentGovernanceRuntimeError(
            "reconstruction stage_outputs must be an immutable tuple"
        )
    expected_types = (
        DevelopmentGovernanceTaskIntake,
        DevelopmentGovernanceCDDClassification,
        DevelopmentGovernanceEvidenceSnapshot,
        DevelopmentGovernanceNeedAssessment,
        DevelopmentGovernanceDisposition,
        DevelopmentGovernancePlanningEligibility,
    )
    if len(stage_outputs) != len(expected_types):
        raise DevelopmentGovernanceRuntimeError(
            "reconstruction stage outputs are incomplete"
        )
    for artifact, expected_type in zip(stage_outputs, expected_types):
        _require_instance(
            artifact,
            expected_type,
            "reconstruction stage output",
        )

    intake = stage_outputs[0]
    cdd = stage_outputs[1]
    evidence = stage_outputs[2]
    need = stage_outputs[3]
    disposition = stage_outputs[4]
    eligibility = stage_outputs[5]
    if not isinstance(intake, DevelopmentGovernanceTaskIntake):
        raise DevelopmentGovernanceRuntimeError(
            "reconstruction Task Intake type is invalid"
        )
    if not isinstance(cdd, DevelopmentGovernanceCDDClassification):
        raise DevelopmentGovernanceRuntimeError(
            "reconstruction CDD type is invalid"
        )
    if not isinstance(evidence, DevelopmentGovernanceEvidenceSnapshot):
        raise DevelopmentGovernanceRuntimeError(
            "reconstruction evidence type is invalid"
        )
    if not isinstance(need, DevelopmentGovernanceNeedAssessment):
        raise DevelopmentGovernanceRuntimeError(
            "reconstruction Need Assessment type is invalid"
        )
    if not isinstance(disposition, DevelopmentGovernanceDisposition):
        raise DevelopmentGovernanceRuntimeError(
            "reconstruction disposition type is invalid"
        )
    if not isinstance(
        eligibility,
        DevelopmentGovernancePlanningEligibility,
    ):
        raise DevelopmentGovernanceRuntimeError(
            "reconstruction planning eligibility type is invalid"
        )

    reconstructed = orchestrate_constitutional_development_governance(
        bundle_id=source_bundle.bundle_id,
        task_intake=intake,
        cdd_classification=cdd,
        evidence_snapshot=evidence,
        need_assessment=need,
        governance_disposition=disposition,
        planning_eligibility=eligibility,
    )
    if reconstructed != source_bundle:
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance reconstruction differs from the bundle"
        )
    if (
        serialize_constitutional_development_governance_bundle(reconstructed)
        != serialize_constitutional_development_governance_bundle(
            source_bundle
        )
    ):
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance reconstruction serialization mismatch"
        )
    return reconstructed


def derive_bundle_state(
    governance_disposition: DevelopmentGovernanceDisposition,
) -> str:
    """Project bundle state mechanically from the certified disposition."""

    _require_instance(
        governance_disposition,
        DevelopmentGovernanceDisposition,
        "Governance disposition",
    )
    return _require_member(
        governance_disposition.governance_disposition,
        GOVERNANCE_DISPOSITIONS,
        "governance_disposition",
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
    governance_bundle: ConstitutionalDevelopmentGovernanceBundle | None = None,
    stage_outputs: tuple[DevelopmentGovernanceStageArtifact, ...] | None = None,
) -> dict[str, Any]:
    """Bind certified planning eligibility to existing planning and durable work."""

    if governance_bundle is None or stage_outputs is None:
        raise DevelopmentGovernanceRuntimeError(
            "governance-eligible durable-work binding requires the complete bundle"
        )
    reconstructed = reconstruct_constitutional_development_governance_bundle(
        bundle=governance_bundle,
        stage_outputs=stage_outputs,
    )
    eligibility = stage_outputs[5]
    disposition = stage_outputs[4]
    if not isinstance(eligibility, DevelopmentGovernancePlanningEligibility):
        raise DevelopmentGovernanceRuntimeError(
            "governance-eligible durable-work binding eligibility is invalid"
        )
    if not isinstance(disposition, DevelopmentGovernanceDisposition):
        raise DevelopmentGovernanceRuntimeError(
            "governance-eligible durable-work binding disposition is invalid"
        )
    if eligibility != planning_eligibility:
        raise DevelopmentGovernanceRuntimeError(
            "governance-eligible durable-work binding substituted eligibility"
        )
    if (
        eligibility.planning_eligible is not True
        or disposition.governance_disposition
        != "BOUNDED_PLANNING_PERMITTED"
        or derive_bundle_state(disposition) != "BOUNDED_PLANNING_PERMITTED"
    ):
        raise DevelopmentGovernanceRuntimeError(
            "Development Governance did not permit bounded planning"
        )

    from aigol.runtime.platform_implementation_turn_durable_work_binding import (
        compose_implementation_turn_durable_work_binding,
        implementation_turn_planning_scope_from_plan,
    )

    binding = compose_implementation_turn_durable_work_binding(
        request=request,
        project_objective_artifact=project_objective_artifact,
        knowledge_reuse_artifact=knowledge_reuse_artifact,
        workspace_state=workspace_state,
        workspace=workspace,
        created_at=created_at,
        replay_dir=Path(replay_dir) / "implementation_turn",
    )
    plan_scope = implementation_turn_planning_scope_from_plan(
        binding["development_composition_plan_artifact"]
    )
    if plan_scope != eligibility.residual_gap:
        raise DevelopmentGovernanceRuntimeError(
            "planner output scope differs from certified Governance scope"
        )
    return {
        "governance_bundle": reconstructed,
        "bundle_state": derive_bundle_state(disposition),
        "planning_eligibility": eligibility,
        "implementation_turn_binding": binding,
        "governance_bundle_hash": reconstructed.bundle_hash,
        "implementation_turn_binding_hash": binding["artifact_hash"],
    }


def _validate_evidence_reference(
    artifact: DevelopmentGovernanceEvidenceReference,
    *,
    expected_baseline: str,
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
        (artifact.claim_value, "evidence claim_value"),
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
    evidence_contract = _SUPPORTED_EVIDENCE_TYPE_CONTRACTS.get(
        artifact.artifact_type
    )
    if evidence_contract is None:
        raise DevelopmentGovernanceRuntimeError(
            "evidence artifact_type is unsupported"
        )
    if artifact.artifact_version != evidence_contract["artifact_version"]:
        raise DevelopmentGovernanceRuntimeError(
            "evidence artifact_version is unsupported"
        )
    if not artifact.artifact_type.endswith(
        f"_{artifact.artifact_version}"
    ):
        raise DevelopmentGovernanceRuntimeError(
            "evidence artifact type and version are inconsistent"
        )
    allowed_values = SUPPORTED_EVIDENCE_CLAIMS.get(artifact.claim_type)
    if allowed_values is None:
        raise DevelopmentGovernanceRuntimeError(
            "evidence claim_type is unsupported"
        )
    _require_member(
        artifact.claim_value,
        allowed_values,
        "evidence claim_value",
    )
    _require_member(
        artifact.subject_type,
        SUPPORTED_EVIDENCE_SUBJECT_TYPES,
        "evidence subject_type",
    )
    if not SHA256_PATTERN.fullmatch(artifact.content_hash):
        raise DevelopmentGovernanceRuntimeError(
            "evidence content_hash must be canonical sha256"
        )
    if artifact.baseline_id != expected_baseline:
        raise DevelopmentGovernanceRuntimeError(
            "evidence item baseline differs from the snapshot baseline"
        )
    _validate_authoritative_evidence_context(
        artifact,
        expected_baseline=expected_baseline,
    )
    _require_member(
        artifact.certification_status,
        SUPPORTED_CERTIFICATION_STATES,
        "evidence certification_status",
    )
    if not isinstance(artifact.certification_required, bool):
        raise DevelopmentGovernanceRuntimeError(
            "evidence certification_required must be boolean"
        )
    if (
        artifact.certification_required
        and artifact.certification_status
        not in CERTIFICATION_SATISFIED_STATES
    ):
        raise DevelopmentGovernanceRuntimeError(
            "required evidence certification is not satisfied"
        )
    _require_member(
        artifact.compatibility_status,
        SUPPORTED_COMPATIBILITY_STATES,
        "evidence compatibility_status",
    )
    _require_member(
        artifact.supersession_state,
        SUPPORTED_SUPERSESSION_STATES,
        "evidence supersession_state",
    )
    if (
        artifact.certification_status == "SUPERSEDED"
        and artifact.supersession_state == "CURRENT"
    ):
        raise DevelopmentGovernanceRuntimeError(
            "superseded certification cannot be current evidence"
        )
    if not isinstance(artifact.reconstruction_required, bool):
        raise DevelopmentGovernanceRuntimeError(
            "evidence reconstruction_required must be boolean"
        )
    _require_string_tuple(artifact.covered_facets, "evidence covered_facets")
    _require_canonical_tuple(
        artifact.covered_facets,
        "evidence covered_facets",
    )
    _require_string_tuple(
        artifact.known_limitations,
        "evidence known_limitations",
    )
    _require_canonical_tuple(
        artifact.known_limitations,
        "evidence known_limitations",
    )
    for value, name in (
        (
            artifact.residual_responsibilities,
            "evidence residual_responsibilities",
        ),
        (
            artifact.declared_responsibilities,
            "evidence declared_responsibilities",
        ),
        (
            artifact.implemented_responsibilities,
            "evidence implemented_responsibilities",
        ),
    ):
        _require_string_tuple(value, name)
        _require_canonical_tuple(value, name)
    for value, name in (
        (artifact.source_endpoint, "evidence source_endpoint"),
        (artifact.target_endpoint, "evidence target_endpoint"),
        (artifact.interface_identity, "evidence interface_identity"),
        (artifact.interface_version, "evidence interface_version"),
    ):
        _require_optional_string(value, name)
    if (
        artifact.claim_type == "OBJECTIVE_FACET_COVERAGE"
        and not artifact.covered_facets
    ):
        raise DevelopmentGovernanceRuntimeError(
            "coverage evidence must identify at least one objective facet"
        )
    if (
        artifact.claim_type == "BINDING_STATE"
        and artifact.claim_value == "MISSING_EXISTING_CONTRACT"
        and not all(
            (
                artifact.source_endpoint,
                artifact.target_endpoint,
                artifact.interface_identity,
                artifact.interface_version,
            )
        )
    ):
        raise DevelopmentGovernanceRuntimeError(
            "missing-binding evidence requires exact compatible endpoints"
        )
    if (
        artifact.claim_type == "REALIZATION_COMPLETENESS"
        and artifact.claim_value in {"INCOMPLETE", "COMPLETE"}
        and not artifact.declared_responsibilities
    ):
        raise DevelopmentGovernanceRuntimeError(
            "realization evidence requires declared responsibility"
        )
    if artifact.claim_type == "REALIZATION_COMPLETENESS":
        declared = set(artifact.declared_responsibilities)
        implemented = set(artifact.implemented_responsibilities)
        residual = set(artifact.residual_responsibilities)
        if not implemented <= declared or not residual <= declared:
            raise DevelopmentGovernanceRuntimeError(
                "realization evidence exceeds declared responsibility"
            )
        if (
            artifact.claim_value == "INCOMPLETE"
            and not artifact.residual_responsibilities
        ):
            raise DevelopmentGovernanceRuntimeError(
                "incomplete realization evidence requires residual work"
            )
        if (
            artifact.claim_value == "COMPLETE"
            and (
                artifact.residual_responsibilities
                or implemented != declared
            )
        ):
            raise DevelopmentGovernanceRuntimeError(
                "complete realization evidence is internally inconsistent"
            )


def _validate_authoritative_evidence_context(
    artifact: DevelopmentGovernanceEvidenceReference,
    *,
    expected_baseline: str,
) -> None:
    try:
        authority = lookup_platform_capability_certification(
            artifact.subject_id
        )
    except FailClosedRuntimeError as exc:
        raise DevelopmentGovernanceRuntimeError(
            "evidence subject has no authoritative certified owner binding"
        ) from exc

    if artifact.subject_id != authority["capability_identifier"]:
        raise DevelopmentGovernanceRuntimeError(
            "evidence subject identity is not canonical"
        )
    expected_owner = authority["capability_owner"]
    expected_architectural_owner = authority["architectural_owner"]
    if artifact.canonical_owner != expected_owner:
        raise DevelopmentGovernanceRuntimeError(
            "evidence canonical_owner differs from authoritative ownership"
        )
    if artifact.architectural_owner != expected_architectural_owner:
        raise DevelopmentGovernanceRuntimeError(
            "evidence architectural_owner differs from authoritative ownership"
        )
    if artifact.certification_status != authority["certification_status"]:
        raise DevelopmentGovernanceRuntimeError(
            "evidence certification status differs from authoritative record"
        )
    if artifact.certification_scope != authority["certification_scope"]:
        raise DevelopmentGovernanceRuntimeError(
            "evidence certification scope differs from authoritative record"
        )
    if artifact.certification_required is not True:
        raise DevelopmentGovernanceRuntimeError(
            "authoritative evidence must preserve certification requirement"
        )

    expected_supersession = (
        "SUPERSEDED"
        if authority["certification_status"] == "SUPERSEDED"
        or authority["superseded_by"] is not None
        else "CURRENT"
    )
    if artifact.supersession_state != expected_supersession:
        raise DevelopmentGovernanceRuntimeError(
            "evidence supersession scope differs from authoritative record"
        )
    if artifact.compatibility_scope != expected_baseline:
        raise DevelopmentGovernanceRuntimeError(
            "evidence compatibility scope differs from the authoritative baseline"
        )

    authoritative_sources = tuple(authority["certification_evidence"])
    if artifact.source_reference not in authoritative_sources:
        raise DevelopmentGovernanceRuntimeError(
            "evidence source reference is not authoritative for its owner"
        )
    source_path = Path(__file__).resolve().parents[2] / artifact.source_reference
    if not source_path.is_file():
        raise DevelopmentGovernanceRuntimeError(
            "authoritative evidence source is unavailable"
        )
    source_hash = "sha256:" + hashlib.sha256(source_path.read_bytes()).hexdigest()
    if artifact.content_hash != source_hash:
        raise DevelopmentGovernanceRuntimeError(
            "evidence content hash differs from the authoritative source"
        )


def _register_authoritative_claim(
    claims_by_authority: dict[
        tuple[str, str, str],
        list[DevelopmentGovernanceEvidenceReference],
    ],
    artifact: DevelopmentGovernanceEvidenceReference,
) -> None:
    authority_key = (
        artifact.subject_id,
        artifact.claim_type,
        artifact.canonical_owner,
    )
    prior_claims = claims_by_authority.setdefault(authority_key, [])
    for prior in prior_claims:
        if (
            prior.claim_value != artifact.claim_value
            and _authoritative_claim_scopes_overlap(prior, artifact)
        ):
            raise DevelopmentGovernanceRuntimeError(
                "one authoritative owner supplied overlapping conflicting evidence"
            )
    prior_claims.append(artifact)


def _authoritative_claim_scopes_overlap(
    first: DevelopmentGovernanceEvidenceReference,
    second: DevelopmentGovernanceEvidenceReference,
) -> bool:
    if not first.covered_facets or not second.covered_facets:
        return True
    return bool(set(first.covered_facets).intersection(second.covered_facets))


def _evaluate_need_assessment_outcome(
    *,
    artifact: DevelopmentGovernanceNeedAssessment,
    task_intake: DevelopmentGovernanceTaskIntake,
    cdd_classification: DevelopmentGovernanceCDDClassification,
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
) -> str:
    if artifact.cdd_id != cdd_classification.cdd_id:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment does not bind the CDD classification"
        )
    if artifact.evidence_snapshot_id != evidence_snapshot.snapshot_id:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment does not bind the evidence snapshot"
        )
    if cdd_classification.action_mode != task_intake.action_mode:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment context has divergent action mode"
        )

    objective_facets = set(artifact.objective_facets)
    if not objective_facets <= set(cdd_classification.affected_scope):
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment facets exceed the classified CDD scope"
        )
    evidence_ids = tuple(
        sorted(item.evidence_id for item in evidence_snapshot.evidence_items)
    )
    if artifact.evidence_references != evidence_ids:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment must bind every evidence item exactly once"
        )
    if not objective_facets or not evidence_snapshot.evidence_items:
        return "FAILED_CLOSED"

    covered, uncovered, ambiguous_coverage = _coverage_sets(
        evidence_snapshot
    )
    missing_coverage = objective_facets.difference(covered | uncovered)
    expected_covered = tuple(sorted(objective_facets.intersection(covered)))
    expected_residual = tuple(sorted(objective_facets - covered))
    if artifact.covered_facets != expected_covered:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment covered facets differ from evidence"
        )
    if artifact.residual_gaps != expected_residual:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment residual gaps differ from evidence"
        )

    reusable_owners = _reusable_owners(
        evidence_snapshot,
        objective_facets,
    )
    if artifact.reusable_owners != reusable_owners:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment reusable owners differ from evidence"
        )

    duplication_risks = tuple(
        sorted(
            item.evidence_id
            for item in evidence_snapshot.evidence_items
            if item.claim_type == "ARCHITECTURAL_DUPLICATION"
            and item.claim_value in {"PROVEN", "SUSPECTED"}
        )
    )
    if artifact.duplication_risks != duplication_risks:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment duplication risks differ from evidence"
        )

    ownership_risks = _ownership_conflicts(evidence_snapshot)
    if artifact.ownership_risks != ownership_risks:
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment ownership risks differ from evidence"
        )

    if missing_coverage:
        return "FAILED_CLOSED"

    facts = _evidence_facts(evidence_snapshot)
    if (
        ambiguous_coverage
        or ownership_risks
        or _has_fact(facts, "REQUESTER_AMBIGUITY", "PRESENT")
        or _has_fact(facts, "CONSTITUTIONAL_AMBIGUITY", "PRESENT")
        or _has_fact(facts, "ARCHITECTURAL_DUPLICATION", "SUSPECTED")
        or _has_fact(facts, "EXPANSION_JUSTIFICATION", "UNRESOLVED")
        or _contains_unknown_evidence(evidence_snapshot)
    ):
        return "GOVERNANCE_REVIEW_REQUIRED"

    predicate_matches = _need_predicate_matches(
        action_mode=task_intake.action_mode,
        objective_facets=objective_facets,
        covered=covered,
        uncovered=uncovered,
        reusable_owners=reusable_owners,
        facts=facts,
    )
    if set(predicate_matches) != SUBSTANTIVE_NEED_OUTCOMES:
        raise DevelopmentGovernanceRuntimeError(
            "Need predicate catalogue is incomplete"
        )
    matched = tuple(
        sorted(
            outcome
            for outcome, satisfied in predicate_matches.items()
            if satisfied
        )
    )
    if len(matched) == 1:
        return matched[0]
    return "GOVERNANCE_REVIEW_REQUIRED"


def _need_predicate_matches(
    *,
    action_mode: str,
    objective_facets: set[str],
    covered: set[str],
    uncovered: set[str],
    reusable_owners: tuple[str, ...],
    facts: dict[str, frozenset[str]],
) -> dict[str, bool]:
    coverage_complete = bool(objective_facets) and objective_facets <= covered
    residual_exists = bool(uncovered)
    implementation_none = _has_fact(
        facts,
        "IMPLEMENTATION_REQUIREMENT",
        "NONE",
    )
    implementation_required = _has_fact(
        facts,
        "IMPLEMENTATION_REQUIREMENT",
        "REQUIRED",
    )
    result_already_accepted = _has_fact(
        facts,
        "REQUESTED_RESULT_STATE",
        "ALREADY_PRODUCED_ACCEPTED",
    )
    duplication_proven = _has_fact(
        facts,
        "ARCHITECTURAL_DUPLICATION",
        "PROVEN",
    )
    expansion_unjustified = _has_fact(
        facts,
        "EXPANSION_JUSTIFICATION",
        "UNJUSTIFIED",
    )
    prohibited_positive = duplication_proven or expansion_unjustified
    neutral_structure = _has_any_fact(
        facts,
        "REQUESTED_STRUCTURE_RELATION",
        {"NEUTRAL", "REUSE_ACCEPTED"},
    )

    return {
        "NO_IMPLEMENTATION_REQUIRED": (
            (action_mode == READ_ONLY or result_already_accepted)
            and coverage_complete
            and implementation_none
            and not residual_exists
            and not prohibited_positive
        ),
        "REUSE_EXISTING_UNCHANGED": (
            action_mode == REPOSITORY_MUTATION_REQUESTED
            and coverage_complete
            and implementation_none
            and neutral_structure
            and not result_already_accepted
            and not residual_exists
            and not prohibited_positive
        ),
        "CANONICALIZATION_ONLY": (
            residual_exists
            and implementation_required
            and _has_fact(
                facts,
                "CANONICALIZATION_SCOPE",
                "EXCLUSIVE",
            )
            and not prohibited_positive
        ),
        "COMPLETE_EXISTING_REALIZATION": (
            residual_exists
            and implementation_required
            and _has_fact(
                facts,
                "REALIZATION_COMPLETENESS",
                "INCOMPLETE",
            )
            and _has_fact(facts, "OWNER_EXTENSION_FIT", "WITHIN_OWNER")
            and _has_fact(facts, "EXISTING_CONTRACT", "EXISTS")
            and not prohibited_positive
        ),
        "IMPLEMENT_EXISTING_BINDING": (
            residual_exists
            and implementation_required
            and _has_fact(
                facts,
                "BINDING_STATE",
                "MISSING_EXISTING_CONTRACT",
            )
            and not prohibited_positive
        ),
        "EXTEND_EXISTING_OWNER": (
            residual_exists
            and implementation_required
            and _has_fact(facts, "OWNER_EXTENSION_FIT", "WITHIN_OWNER")
            and _has_fact(
                facts,
                "REALIZATION_COMPLETENESS",
                "COMPLETE",
            )
            and not _has_fact(
                facts,
                "BINDING_STATE",
                "MISSING_EXISTING_CONTRACT",
            )
            and not _has_fact(
                facts,
                "COMPOSITION_COVERAGE",
                "COMPLETE",
            )
            and not prohibited_positive
        ),
        "COMPOSE_EXISTING_CAPABILITIES": (
            residual_exists
            and implementation_required
            and len(reusable_owners) >= 2
            and _has_fact(
                facts,
                "COMPOSITION_COVERAGE",
                "COMPLETE",
            )
            and not _has_fact(
                facts,
                "BINDING_STATE",
                "MISSING_EXISTING_CONTRACT",
            )
            and not prohibited_positive
        ),
        "NEW_REALIZATION_JUSTIFIED": (
            residual_exists
            and implementation_required
            and _has_fact(facts, "EXISTING_CONTRACT", "EXISTS")
            and _has_fact(
                facts,
                "REALIZATION_AVAILABILITY",
                "NO_CURRENT_REALIZATION",
            )
            and _has_fact(
                facts,
                "CONSTITUTIONAL_DISTINCTION",
                "NOT_DISTINCT",
            )
            and _has_fact(
                facts,
                "SMALLER_CHANGE_OPTIONS",
                "DISPROVEN",
            )
            and not prohibited_positive
        ),
        "NEW_DISTINCT_CAPABILITY_JUSTIFIED": (
            residual_exists
            and implementation_required
            and _has_fact(
                facts,
                "CONSTITUTIONAL_DISTINCTION",
                "DISTINCT",
            )
            and _has_fact(
                facts,
                "SMALLER_CHANGE_OPTIONS",
                "DISPROVEN",
            )
            and _has_fact(
                facts,
                "EXPANSION_JUSTIFICATION",
                "JUSTIFIED",
            )
            and not duplication_proven
            and not expansion_unjustified
        ),
        "ARCHITECTURAL_DUPLICATION": duplication_proven,
        "UNJUSTIFIED_EXPANSION": expansion_unjustified,
    }


def _reduce_governance_disposition(
    *,
    task_intake: DevelopmentGovernanceTaskIntake,
    cdd_classification: DevelopmentGovernanceCDDClassification,
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
    need_assessment: DevelopmentGovernanceNeedAssessment,
    review_references: tuple[str, ...],
) -> str:
    facts = _evidence_facts(evidence_snapshot)

    # Fixed routing order: invalid evidence has already failed validation.
    if (
        cdd_classification.termination_state == "FAILED_CLOSED"
        or need_assessment.outcome == "FAILED_CLOSED"
    ):
        return "FAILED_CLOSED"
    if (
        cdd_classification.termination_state == "CLARIFICATION_REQUIRED"
        or _has_fact(facts, "REQUESTER_AMBIGUITY", "PRESENT")
    ):
        return "CLARIFICATION_REQUIRED"

    unresolved_constitutional_evidence = (
        cdd_classification.termination_state
        == "GOVERNANCE_REVIEW_REQUIRED"
        or need_assessment.outcome == "GOVERNANCE_REVIEW_REQUIRED"
        or _has_fact(facts, "CONSTITUTIONAL_AMBIGUITY", "PRESENT")
        or bool(_ownership_conflicts(evidence_snapshot))
    )
    if unresolved_constitutional_evidence:
        return "GOVERNANCE_REVIEW_REQUIRED"
    if cdd_classification.required_reviews and not review_references:
        return "GOVERNANCE_REVIEW_REQUIRED"

    if cdd_classification.termination_state == "BLOCKED":
        return "WORK_BLOCKED"
    if need_assessment.outcome in {
        "ARCHITECTURAL_DUPLICATION",
        "UNJUSTIFIED_EXPANSION",
    }:
        return "WORK_BLOCKED"
    if task_intake.action_mode == READ_ONLY:
        return "READ_ONLY_WORK_MAY_CONTINUE"
    if need_assessment.outcome == "NO_IMPLEMENTATION_REQUIRED":
        return "NO_IMPLEMENTATION_REQUIRED"
    if need_assessment.outcome == "REUSE_EXISTING_UNCHANGED":
        return "REUSE_REQUIRED"
    if (
        need_assessment.outcome == "NEW_DISTINCT_CAPABILITY_JUSTIFIED"
        and not review_references
    ):
        return "GOVERNANCE_REVIEW_REQUIRED"
    if need_assessment.outcome in {
        "CANONICALIZATION_ONLY",
        "COMPLETE_EXISTING_REALIZATION",
        "IMPLEMENT_EXISTING_BINDING",
        "EXTEND_EXISTING_OWNER",
        "COMPOSE_EXISTING_CAPABILITIES",
        "NEW_REALIZATION_JUSTIFIED",
        "NEW_DISTINCT_CAPABILITY_JUSTIFIED",
    }:
        return "BOUNDED_PLANNING_PERMITTED"
    return "FAILED_CLOSED"


def _coverage_sets(
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
) -> tuple[set[str], set[str], bool]:
    covered: set[str] = set()
    uncovered: set[str] = set()
    for item in evidence_snapshot.evidence_items:
        if item.claim_type != "OBJECTIVE_FACET_COVERAGE":
            continue
        if not _evidence_is_current_and_usable(item):
            continue
        target = covered if item.claim_value == "COVERED" else uncovered
        target.update(item.covered_facets)
    return covered, uncovered, bool(covered & uncovered)


def _reusable_owners(
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
    objective_facets: set[str],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                item.canonical_owner
                for item in evidence_snapshot.evidence_items
                if item.claim_type == "OBJECTIVE_FACET_COVERAGE"
                and item.claim_value == "COVERED"
                and objective_facets.intersection(item.covered_facets)
                and _evidence_is_current_and_usable(item)
            }
        )
    )


def _ownership_conflicts(
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
) -> tuple[str, ...]:
    owners_by_subject: dict[str, set[str]] = {}
    for item in evidence_snapshot.evidence_items:
        owners_by_subject.setdefault(item.subject_id, set()).add(
            item.canonical_owner
        )
    return tuple(
        sorted(
            subject_id
            for subject_id, owners in owners_by_subject.items()
            if len(owners) > 1
        )
    )


def _evidence_facts(
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
) -> dict[str, frozenset[str]]:
    facts: dict[str, set[str]] = {}
    for item in evidence_snapshot.evidence_items:
        if not _evidence_is_current_and_usable(item):
            continue
        facts.setdefault(item.claim_type, set()).add(item.claim_value)
    return {
        claim_type: frozenset(sorted(values))
        for claim_type, values in sorted(facts.items())
    }


def _evidence_is_current_and_usable(
    artifact: DevelopmentGovernanceEvidenceReference,
) -> bool:
    certification_satisfied = (
        not artifact.certification_required
        or artifact.certification_status in CERTIFICATION_SATISFIED_STATES
    )
    return (
        artifact.supersession_state == "CURRENT"
        and artifact.compatibility_status
        in {"COMPATIBLE", "NOT_APPLICABLE"}
        and certification_satisfied
    )


def _contains_unknown_evidence(
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
) -> bool:
    return any(
        item.compatibility_status == "UNKNOWN"
        or item.claim_value == "UNKNOWN"
        for item in evidence_snapshot.evidence_items
    )


def _has_fact(
    facts: dict[str, frozenset[str]],
    claim_type: str,
    claim_value: str,
) -> bool:
    return claim_value in facts.get(claim_type, frozenset())


def _has_any_fact(
    facts: dict[str, frozenset[str]],
    claim_type: str,
    claim_values: set[str],
) -> bool:
    return bool(facts.get(claim_type, frozenset()).intersection(claim_values))


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
    if cdd.affected_scope != intake.bounded_scope:
        raise DevelopmentGovernanceRuntimeError(
            "CDD affected scope does not bind Task Intake scope"
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
        artifact_hash=_canonical_artifact_hash(artifact),
    )


def _generate_bundle_identity(
    *,
    baseline_reference: str,
    stage_references: tuple[DevelopmentGovernanceStageReference, ...],
) -> str:
    identity_body = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1
        ),
        "runtime_version": DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        "baseline_reference": _require_string(
            baseline_reference,
            "baseline_reference",
        ),
        "stage_order": list(CANONICAL_STAGE_ORDER),
        "stage_references": _canonical_value(stage_references),
    }
    return "DG-BUNDLE:" + replay_hash(identity_body)


def _canonical_artifact_hash(artifact: Any) -> str:
    body = _canonical_value(artifact)
    if not isinstance(body, dict):
        raise DevelopmentGovernanceRuntimeError(
            "canonical artifact body must be an object"
        )
    body.pop("bundle_hash", None)
    return replay_hash(body)


def _canonical_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _canonical_value(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, tuple):
        return [_canonical_value(item) for item in value]
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise DevelopmentGovernanceRuntimeError(
                "canonical mapping keys must be strings"
            )
        return {
            key: _canonical_value(item)
            for key, item in sorted(value.items())
        }
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise DevelopmentGovernanceRuntimeError(
        "Development Governance value is not canonically serializable"
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


def _require_hash(value: Any, name: str) -> str:
    candidate = _require_string(value, name)
    if not SHA256_PATTERN.fullmatch(candidate):
        raise DevelopmentGovernanceRuntimeError(
            f"{name} must be canonical sha256"
        )
    return candidate


def _require_optional_string(value: Any, name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, name)


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


def _require_canonical_tuple(
    value: tuple[str, ...],
    name: str,
) -> tuple[str, ...]:
    if value != tuple(sorted(set(value))):
        raise DevelopmentGovernanceRuntimeError(
            f"{name} must be sorted and contain no duplicates"
        )
    return value


__all__ = [
    "ACTION_MODES",
    "AUTHORITY_IMPACTS",
    "CANONICAL_STAGE_ORDER",
    "CAPABILITY_IMPACTS",
    "CDD_TERMINATION_STATES",
    "CONSTITUTIONAL_IMPACTS",
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
    "MUTATION_LAYERS",
    "NEED_ASSESSMENT_OUTCOMES",
    "PRIMARY_WORK_CLASSES",
    "PROTOCOL_IMPACTS",
    "READ_ONLY",
    "REALIZATION_CATEGORIES",
    "REALIZATION_IMPACTS",
    "REPOSITORY_MUTATION_REQUESTED",
    "STAGE_ARTIFACT_TYPES",
    "SUBSTANTIVE_NEED_OUTCOMES",
    "SUPPORTED_CERTIFICATION_STATES",
    "SUPPORTED_COMPATIBILITY_STATES",
    "SUPPORTED_EVIDENCE_CLAIMS",
    "SUPPORTED_EVIDENCE_SUBJECT_TYPES",
    "SUPPORTED_EVIDENCE_VERSION",
    "SUPPORTED_SUPERSESSION_STATES",
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
    "serialize_constitutional_development_governance_bundle",
    "validate_cdd_classification",
    "validate_constitutional_development_governance_bundle",
    "validate_development_governance_disposition",
    "validate_development_governance_evidence_snapshot",
    "validate_development_governance_task_intake",
    "validate_need_assessment",
    "validate_planning_eligibility",
]
