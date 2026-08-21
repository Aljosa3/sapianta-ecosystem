"""Bounded fail-closed constitutional evidence-reduction gate.

The gate evaluates authenticated evidence projections and creates immutable,
hash-bound evidence artifacts.  It never removes, condenses, archives, or
otherwise mutates constitutional evidence.  Persistence is an explicit caller
action through the existing :class:`RuntimeLedger` lineage.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

from aigol.runtime.authority_provenance import (
    AUTHORIZATION_OWNER_IDENTITY,
    BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION,
    OWNER_ISSUED_AUTHORIZATION_ACT_CLASS,
    TrustedAuthorityProvenanceResolverV1,
)
from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    RECORDED,
    validate_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    AUTHORIZATION,
    HUMAN_AUTHORITY_OWNER,
    bind_canonical_human_authority_act_to_che_v1,
    validate_canonical_human_authority_act_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    canonical_che_request_source_act_digest_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.ledger import RuntimeLedger
from aigol.runtime.transport.serialization import replay_hash, verify_replay_hash, with_replay_hash


EVIDENCE_REDUCTION_GATE_VERSION = (
    "G77_BOUNDED_FAIL_CLOSED_EVIDENCE_REDUCTION_GATE_PROFILE_B_C1_V1"
)
ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT = "4c2398380cb973ca522ccc2eb6e2ff22a5404296"
EVIDENCE_REDUCTION_POLICY_AUTHORITY_SCOPE = "BOUNDED_EVIDENCE_REDUCTION_POLICY"
AUTHORIZE_BOUNDED_EVIDENCE_REDUCTION_POLICY = (
    "AUTHORIZE_BOUNDED_EVIDENCE_REDUCTION_POLICY"
)

DOMAIN_REDUCTION_POLICY_ARTIFACT_V1 = "DOMAIN_REDUCTION_POLICY_PROJECTION_V1"
EVIDENCE_OBLIGATION_PROJECTION_ARTIFACT_V1 = "EVIDENCE_OBLIGATION_PROJECTION_V1"
PERMANENT_TRAIL_ARTIFACT_V1 = "PERMANENT_EVIDENCE_TRAIL_PROJECTION_V1"
ARTICLE_10_COHORT_ARTIFACT_V1 = "ARTICLE_10_EVIDENCE_COHORT_PROJECTION_V1"
PLANNED_REDUCTION_MANIFEST_ARTIFACT_V1 = "PLANNED_EVIDENCE_REDUCTION_MANIFEST_V1"
REDUCTION_AUTHORIZATION_ARTIFACT_V1 = "BOUNDED_EVIDENCE_REDUCTION_AUTHORIZATION_V1"
GATE_DECISION_ARTIFACT_V1 = "EVIDENCE_REDUCTION_GATE_DECISION_V1"
ACTUAL_REDUCTION_MANIFEST_ARTIFACT_V1 = "ACTUAL_EVIDENCE_REDUCTION_DISPOSITION_MANIFEST_V1"

ALLOW_BOUNDED_EVIDENCE_REDUCTION = "ALLOW_BOUNDED_EVIDENCE_REDUCTION"
DO_NOT_REDUCE_EVIDENCE = "DO_NOT_REDUCE_EVIDENCE"

CURRENT = "CURRENT"
AUTHENTICATED = "AUTHENTICATED"
CLOSED = "CLOSED"
NO_STRICTER_RETENTION_REQUIRED = "NO_STRICTER_RETENTION_REQUIRED"

BEFORE_BOUNDARY = "BEFORE_BOUNDARY"
AT_BOUNDARY = "AT_BOUNDARY"
AFTER_BOUNDARY = "AFTER_BOUNDARY"
FULL_EVIDENCE_PRESENT = "FULL_EVIDENCE_PRESENT"
AUTHORIZED_OR_PLANNED_INCOMPLETE = "AUTHORIZED_OR_PLANNED_INCOMPLETE"
PARTIAL_OR_AMBIGUOUS = "PARTIAL_OR_AMBIGUOUS"
PRIOR_VALID_REDUCTION_COMPLETE = "PRIOR_VALID_REDUCTION_COMPLETE"

PRIOR_VALID_OUTCOME_PRESERVED = "PRIOR_VALID_OUTCOME_PRESERVED"
EFFECTIVE_GATE_REQUIRED = "EFFECTIVE_GATE_REQUIRED"
REVALIDATION_UNDER_EFFECTIVE_GATE_REQUIRED = "REVALIDATION_UNDER_EFFECTIVE_GATE_REQUIRED"
STOP_FURTHER_REDUCTION = "STOP_FURTHER_REDUCTION"

OBLIGATION_CLASSES = (
    "replay",
    "audit",
    "dispute",
    "correctness",
    "certification",
    "other",
)
PLANNED_DISPOSITIONS = frozenset({"REMOVE", "CONDENSE", "OTHER_REDUCTION", "RETAIN"})
REDUCING_DISPOSITIONS = frozenset({"REMOVE", "CONDENSE", "OTHER_REDUCTION"})

_KNOWN_ARTIFACT_TYPES = frozenset(
    {
        DOMAIN_REDUCTION_POLICY_ARTIFACT_V1,
        EVIDENCE_OBLIGATION_PROJECTION_ARTIFACT_V1,
        PERMANENT_TRAIL_ARTIFACT_V1,
        ARTICLE_10_COHORT_ARTIFACT_V1,
        PLANNED_REDUCTION_MANIFEST_ARTIFACT_V1,
        REDUCTION_AUTHORIZATION_ARTIFACT_V1,
        GATE_DECISION_ARTIFACT_V1,
        ACTUAL_REDUCTION_MANIFEST_ARTIFACT_V1,
    }
)

_ARTIFACT_FIELDS = {
    DOMAIN_REDUCTION_POLICY_ARTIFACT_V1: {
        "artifact_type",
        "gate_version",
        "domain_id",
        "policy_id",
        "policy_version",
        "authority_id",
        "authority_evidence_reference",
        "authority_evidence_hash",
        "authority_provenance_root_identity",
        "authority_provenance_root_hash",
        "currentness_evidence_reference",
        "currentness_evidence_hash",
        "applicable_at_commit",
        "allowed_evidence_classes",
        "allowed_reduction_types",
        "complete",
        "authenticated",
        "current",
        "ambiguous",
        "bounded_scope",
        "semantic_authority_created",
        "replay_hash",
    },
    EVIDENCE_OBLIGATION_PROJECTION_ARTIFACT_V1: {
        "artifact_type",
        "gate_version",
        "domain_id",
        "evidence_class",
        "obligation_statuses",
        "projection_authority_id",
        "projection_evidence_reference",
        "projection_evidence_hash",
        "external_authority_status",
        "external_authority_evidence_reference",
        "external_authority_evidence_hash",
        "stricter_requirement_status",
        "authenticated",
        "current",
        "read_only_projection",
        "external_semantics_inferred",
        "replay_hash",
    },
    PERMANENT_TRAIL_ARTIFACT_V1: {
        "artifact_type",
        "gate_version",
        "trail_id",
        "domain_id",
        "evidence_class",
        "attempted_action",
        "subject_reference",
        "result_or_reason",
        "replay_provenance",
        "lifecycle_disposition",
        "complete",
        "verified",
        "immutable",
        "full_replay_claimed",
        "replay_hash",
    },
    ARTICLE_10_COHORT_ARTIFACT_V1: {
        "artifact_type",
        "gate_version",
        "evidence_id",
        "article_10_boundary_commit",
        "observed_commit",
        "started_position",
        "boundary_state",
        "prior_contract_validated",
        "historical_evidence_invented",
        "replay_hash",
    },
    PLANNED_REDUCTION_MANIFEST_ARTIFACT_V1: {
        "artifact_type",
        "gate_version",
        "manifest_id",
        "domain_id",
        "evidence_class",
        "reduction_type",
        "evidence_items",
        "policy_hash",
        "permanent_trail_id",
        "permanent_trail_hash",
        "cohort_hash",
        "article_10_boundary_commit",
        "physical_reduction_performed",
        "replay_hash",
    },
    REDUCTION_AUTHORIZATION_ARTIFACT_V1: {
        "artifact_type",
        "gate_version",
        "authorization_id",
        "domain_id",
        "policy_id",
        "policy_version",
        "policy_hash",
        "authority_id",
        "authority_evidence_reference",
        "authority_evidence_hash",
        "authority_provenance_root_identity",
        "authority_provenance_root_hash",
        "evidence_class",
        "reduction_type",
        "authorized_evidence_ids",
        "gate_basis_hash",
        "permanent_trail_hash",
        "planned_manifest_hash",
        "article_10_boundary_commit",
        "applicable_at_commit",
        "authenticated",
        "current",
        "ambiguous",
        "bounded_scope",
        "execution_authority_created",
        "replay_hash",
    },
    GATE_DECISION_ARTIFACT_V1: {
        "artifact_type",
        "gate_version",
        "article_10_boundary_commit",
        "decision",
        "failure_codes",
        "cohort_result",
        "input_hashes",
        "side_effect_performed",
        "physical_reduction_performed",
        "semantic_authority_created",
        "authority_paths",
        "production_paths",
        "parallel_paths",
        "human_entry_paths",
        "decision_id",
        "replay_hash",
    },
    ACTUAL_REDUCTION_MANIFEST_ARTIFACT_V1: {
        "artifact_type",
        "gate_version",
        "manifest_id",
        "domain_id",
        "evidence_class",
        "reduction_type",
        "planned_manifest_hash",
        "authorization_hash",
        "gate_decision_hash",
        "policy_hash",
        "permanent_trail_id",
        "permanent_trail_hash",
        "cohort_hash",
        "execution_evidence_reference",
        "execution_evidence_hash",
        "evidence_items",
        "constitutional_replay_provenance_preserved",
        "remaining_evidence_integrity_verified",
        "disposition_record_complete",
        "physical_reduction_performed_by_gate",
        "full_replay_claimed",
        "replay_hash",
    },
}


def domain_reduction_policy_authority_payload(
    *,
    domain_id: str,
    policy_id: str,
    policy_version: str,
    authority_id: str,
    applicable_at_commit: str,
    allowed_evidence_classes: list[str],
    allowed_reduction_types: list[str],
    obligations_hash: str,
    permanent_trail_hash: str,
    cohort_hash: str,
) -> dict[str, Any]:
    """Return the exact Human Authority payload for one policy snapshot."""

    return {
        "command": AUTHORIZE_BOUNDED_EVIDENCE_REDUCTION_POLICY,
        "domain_id": _require_text(domain_id, "domain_id"),
        "policy_id": _require_text(policy_id, "policy_id"),
        "policy_version": _require_text(policy_version, "policy_version"),
        "authority_id": _require_text(authority_id, "authority_id"),
        "applicable_at_commit": _require_text(
            applicable_at_commit, "applicable_at_commit"
        ),
        "allowed_evidence_classes": _text_list(
            allowed_evidence_classes, "allowed_evidence_classes"
        ),
        "allowed_reduction_types": _text_list(
            allowed_reduction_types, "allowed_reduction_types"
        ),
        "obligations_hash": _require_hash(obligations_hash, "obligations_hash"),
        "permanent_trail_hash": _require_hash(
            permanent_trail_hash, "permanent_trail_hash"
        ),
        "cohort_hash": _require_hash(cohort_hash, "cohort_hash"),
    }


def create_domain_reduction_policy_projection(
    *,
    domain_id: str,
    policy_id: str,
    policy_version: str,
    authority_id: str,
    authority_evidence_reference: str,
    authority_evidence_hash: str,
    authority_provenance_root_identity: str,
    authority_provenance_root_hash: str,
    currentness_evidence_reference: str,
    currentness_evidence_hash: str,
    applicable_at_commit: str,
    allowed_evidence_classes: list[str],
    allowed_reduction_types: list[str],
    complete: bool = True,
    authenticated: bool = True,
    current: bool = True,
    ambiguous: bool = False,
    bounded_scope: bool = True,
) -> dict[str, Any]:
    """Materialize one exact authority projection without granting authority."""

    return _artifact(
        {
            "artifact_type": DOMAIN_REDUCTION_POLICY_ARTIFACT_V1,
            "gate_version": EVIDENCE_REDUCTION_GATE_VERSION,
            "domain_id": _require_text(domain_id, "domain_id"),
            "policy_id": _require_text(policy_id, "policy_id"),
            "policy_version": _require_text(policy_version, "policy_version"),
            "authority_id": _require_text(authority_id, "authority_id"),
            "authority_evidence_reference": _require_text(
                authority_evidence_reference, "authority_evidence_reference"
            ),
            "authority_evidence_hash": _require_hash(authority_evidence_hash, "authority_evidence_hash"),
            "authority_provenance_root_identity": _require_text(
                authority_provenance_root_identity,
                "authority_provenance_root_identity",
            ),
            "authority_provenance_root_hash": _require_hash(
                authority_provenance_root_hash,
                "authority_provenance_root_hash",
            ),
            "currentness_evidence_reference": _require_text(
                currentness_evidence_reference, "currentness_evidence_reference"
            ),
            "currentness_evidence_hash": _require_hash(
                currentness_evidence_hash, "currentness_evidence_hash"
            ),
            "applicable_at_commit": _require_text(applicable_at_commit, "applicable_at_commit"),
            "allowed_evidence_classes": _text_list(allowed_evidence_classes, "allowed_evidence_classes"),
            "allowed_reduction_types": _text_list(allowed_reduction_types, "allowed_reduction_types"),
            "complete": _require_bool(complete, "complete"),
            "authenticated": _require_bool(authenticated, "authenticated"),
            "current": _require_bool(current, "current"),
            "ambiguous": _require_bool(ambiguous, "ambiguous"),
            "bounded_scope": _require_bool(bounded_scope, "bounded_scope"),
            "semantic_authority_created": False,
        }
    )


def create_obligation_projection(
    *,
    domain_id: str,
    evidence_class: str,
    obligation_statuses: dict[str, str],
    projection_authority_id: str,
    projection_evidence_reference: str,
    projection_evidence_hash: str,
    external_authority_status: str,
    external_authority_evidence_reference: str,
    external_authority_evidence_hash: str,
    stricter_requirement_status: str,
    authenticated: bool = True,
    current: bool = True,
) -> dict[str, Any]:
    """Create a read-only projection; the gate does not decide external law."""

    if not isinstance(obligation_statuses, dict):
        raise FailClosedRuntimeError("obligation_statuses must be an object")
    return _artifact(
        {
            "artifact_type": EVIDENCE_OBLIGATION_PROJECTION_ARTIFACT_V1,
            "gate_version": EVIDENCE_REDUCTION_GATE_VERSION,
            "domain_id": _require_text(domain_id, "domain_id"),
            "evidence_class": _require_text(evidence_class, "evidence_class"),
            "obligation_statuses": deepcopy(obligation_statuses),
            "projection_authority_id": _require_text(projection_authority_id, "projection_authority_id"),
            "projection_evidence_reference": _require_text(
                projection_evidence_reference, "projection_evidence_reference"
            ),
            "projection_evidence_hash": _require_hash(
                projection_evidence_hash, "projection_evidence_hash"
            ),
            "external_authority_status": _require_text(
                external_authority_status, "external_authority_status"
            ),
            "external_authority_evidence_reference": _require_text(
                external_authority_evidence_reference,
                "external_authority_evidence_reference",
            ),
            "external_authority_evidence_hash": _require_hash(
                external_authority_evidence_hash,
                "external_authority_evidence_hash",
            ),
            "stricter_requirement_status": _require_text(
                stricter_requirement_status, "stricter_requirement_status"
            ),
            "authenticated": _require_bool(authenticated, "authenticated"),
            "current": _require_bool(current, "current"),
            "read_only_projection": True,
            "external_semantics_inferred": False,
        }
    )


def create_permanent_trail_projection(
    *,
    trail_id: str,
    domain_id: str,
    evidence_class: str,
    attempted_action: str,
    subject_reference: str,
    result_or_reason: str,
    replay_provenance: list[dict[str, str]],
    lifecycle_disposition: str,
    complete: bool = True,
    verified: bool = True,
    immutable: bool = True,
) -> dict[str, Any]:
    """Create the permanent minimum-trail projection required before reduction."""

    return _artifact(
        {
            "artifact_type": PERMANENT_TRAIL_ARTIFACT_V1,
            "gate_version": EVIDENCE_REDUCTION_GATE_VERSION,
            "trail_id": _require_text(trail_id, "trail_id"),
            "domain_id": _require_text(domain_id, "domain_id"),
            "evidence_class": _require_text(evidence_class, "evidence_class"),
            "attempted_action": _require_text(attempted_action, "attempted_action"),
            "subject_reference": _require_text(subject_reference, "subject_reference"),
            "result_or_reason": _require_text(result_or_reason, "result_or_reason"),
            "replay_provenance": _lineage(replay_provenance),
            "lifecycle_disposition": _require_text(
                lifecycle_disposition, "lifecycle_disposition"
            ),
            "complete": _require_bool(complete, "complete"),
            "verified": _require_bool(verified, "verified"),
            "immutable": _require_bool(immutable, "immutable"),
            "full_replay_claimed": False,
        }
    )


def create_article10_cohort_projection(
    *,
    evidence_id: str,
    observed_commit: str,
    started_position: str,
    boundary_state: str,
    prior_contract_validated: bool = False,
    historical_evidence_invented: bool = False,
) -> dict[str, Any]:
    """Bind one evidence lifecycle to the effective Article-10 boundary."""

    return _artifact(
        {
            "artifact_type": ARTICLE_10_COHORT_ARTIFACT_V1,
            "gate_version": EVIDENCE_REDUCTION_GATE_VERSION,
            "evidence_id": _require_text(evidence_id, "evidence_id"),
            "article_10_boundary_commit": ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT,
            "observed_commit": _require_text(observed_commit, "observed_commit"),
            "started_position": _require_text(started_position, "started_position"),
            "boundary_state": _require_text(boundary_state, "boundary_state"),
            "prior_contract_validated": _require_bool(
                prior_contract_validated, "prior_contract_validated"
            ),
            "historical_evidence_invented": _require_bool(
                historical_evidence_invented, "historical_evidence_invented"
            ),
        }
    )


def classify_article10_cohort(cohort: dict[str, Any]) -> str:
    """Return the deterministic prospective-boundary treatment."""

    _validate_artifact(cohort, ARTICLE_10_COHORT_ARTIFACT_V1)
    if cohort["article_10_boundary_commit"] != ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT:
        raise FailClosedRuntimeError("Article-10 boundary mismatch")
    if cohort["started_position"] not in {BEFORE_BOUNDARY, AT_BOUNDARY, AFTER_BOUNDARY}:
        raise FailClosedRuntimeError("Article-10 position is invalid")
    if cohort["historical_evidence_invented"] is not False:
        return STOP_FURTHER_REDUCTION
    state = cohort["boundary_state"]
    if state == PRIOR_VALID_REDUCTION_COMPLETE:
        return (
            PRIOR_VALID_OUTCOME_PRESERVED
            if cohort["started_position"] == BEFORE_BOUNDARY
            and cohort["prior_contract_validated"] is True
            else STOP_FURTHER_REDUCTION
        )
    if state == PARTIAL_OR_AMBIGUOUS:
        return STOP_FURTHER_REDUCTION
    if state == AUTHORIZED_OR_PLANNED_INCOMPLETE:
        return REVALIDATION_UNDER_EFFECTIVE_GATE_REQUIRED
    if state == FULL_EVIDENCE_PRESENT:
        return EFFECTIVE_GATE_REQUIRED
    raise FailClosedRuntimeError("Article-10 boundary state is invalid")


def create_planned_reduction_manifest(
    *,
    manifest_id: str,
    domain_id: str,
    evidence_class: str,
    reduction_type: str,
    evidence_items: list[dict[str, str]],
    policy_hash: str,
    permanent_trail_id: str,
    permanent_trail_hash: str,
    cohort_hash: str,
) -> dict[str, Any]:
    """Create the exact planned scope without performing any reduction."""

    normalized_items = _manifest_items(evidence_items, actual=False)
    if not any(item["planned_disposition"] in REDUCING_DISPOSITIONS for item in normalized_items):
        raise FailClosedRuntimeError("planned manifest contains no bounded reduction")
    return _artifact(
        {
            "artifact_type": PLANNED_REDUCTION_MANIFEST_ARTIFACT_V1,
            "gate_version": EVIDENCE_REDUCTION_GATE_VERSION,
            "manifest_id": _require_text(manifest_id, "manifest_id"),
            "domain_id": _require_text(domain_id, "domain_id"),
            "evidence_class": _require_text(evidence_class, "evidence_class"),
            "reduction_type": _require_text(reduction_type, "reduction_type"),
            "evidence_items": normalized_items,
            "policy_hash": _require_hash(policy_hash, "policy_hash"),
            "permanent_trail_id": _require_text(
                permanent_trail_id, "permanent_trail_id"
            ),
            "permanent_trail_hash": _require_hash(permanent_trail_hash, "permanent_trail_hash"),
            "cohort_hash": _require_hash(cohort_hash, "cohort_hash"),
            "article_10_boundary_commit": ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT,
            "physical_reduction_performed": False,
        }
    )


def calculate_gate_basis_hash(
    *,
    policy: dict[str, Any],
    obligations: dict[str, Any],
    permanent_trail: dict[str, Any],
    planned_manifest: dict[str, Any],
    cohort: dict[str, Any],
) -> str:
    """Hash the immutable pre-authorization gate basis."""

    return replay_hash(
        {
            "article_10_boundary_commit": ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT,
            "policy_hash": _artifact_hash(policy),
            "obligations_hash": _artifact_hash(obligations),
            "permanent_trail_hash": _artifact_hash(permanent_trail),
            "planned_manifest_hash": _artifact_hash(planned_manifest),
            "cohort_hash": _artifact_hash(cohort),
        }
    )


def create_reduction_authorization(
    *,
    authorization_id: str,
    domain_id: str,
    policy_id: str,
    policy_version: str,
    policy_hash: str,
    authority_id: str,
    authority_evidence_reference: str,
    authority_evidence_hash: str,
    authority_provenance_root_identity: str,
    authority_provenance_root_hash: str,
    evidence_class: str,
    reduction_type: str,
    authorized_evidence_ids: list[str],
    gate_basis_hash: str,
    permanent_trail_hash: str,
    planned_manifest_hash: str,
    applicable_at_commit: str,
    authenticated: bool = True,
    current: bool = True,
    ambiguous: bool = False,
    bounded_scope: bool = True,
) -> dict[str, Any]:
    """Materialize exact bounded authorization evidence without executing it."""

    return _artifact(
        {
            "artifact_type": REDUCTION_AUTHORIZATION_ARTIFACT_V1,
            "gate_version": EVIDENCE_REDUCTION_GATE_VERSION,
            "authorization_id": _require_text(authorization_id, "authorization_id"),
            "domain_id": _require_text(domain_id, "domain_id"),
            "policy_id": _require_text(policy_id, "policy_id"),
            "policy_version": _require_text(policy_version, "policy_version"),
            "policy_hash": _require_hash(policy_hash, "policy_hash"),
            "authority_id": _require_text(authority_id, "authority_id"),
            "authority_evidence_reference": _require_text(
                authority_evidence_reference, "authority_evidence_reference"
            ),
            "authority_evidence_hash": _require_hash(authority_evidence_hash, "authority_evidence_hash"),
            "authority_provenance_root_identity": _require_text(
                authority_provenance_root_identity,
                "authority_provenance_root_identity",
            ),
            "authority_provenance_root_hash": _require_hash(
                authority_provenance_root_hash,
                "authority_provenance_root_hash",
            ),
            "evidence_class": _require_text(evidence_class, "evidence_class"),
            "reduction_type": _require_text(reduction_type, "reduction_type"),
            "authorized_evidence_ids": _text_list(
                authorized_evidence_ids, "authorized_evidence_ids"
            ),
            "gate_basis_hash": _require_hash(gate_basis_hash, "gate_basis_hash"),
            "permanent_trail_hash": _require_hash(permanent_trail_hash, "permanent_trail_hash"),
            "planned_manifest_hash": _require_hash(planned_manifest_hash, "planned_manifest_hash"),
            "article_10_boundary_commit": ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT,
            "applicable_at_commit": _require_text(applicable_at_commit, "applicable_at_commit"),
            "authenticated": _require_bool(authenticated, "authenticated"),
            "current": _require_bool(current, "current"),
            "ambiguous": _require_bool(ambiguous, "ambiguous"),
            "bounded_scope": _require_bool(bounded_scope, "bounded_scope"),
            "execution_authority_created": False,
        }
    )


class BoundedEvidenceReductionGateV1:
    """One gate bound to a resolver fixed outside every evaluation call."""

    __slots__ = ("__authority_provenance_resolver", "__sealed")

    def __init__(
        self, authority_provenance_resolver: TrustedAuthorityProvenanceResolverV1
    ) -> None:
        if (
            type(authority_provenance_resolver)
            is not TrustedAuthorityProvenanceResolverV1
        ):
            raise FailClosedRuntimeError(
                "exact trusted authority provenance resolver is required"
            )
        object.__setattr__(
            self,
            "_BoundedEvidenceReductionGateV1__authority_provenance_resolver",
            authority_provenance_resolver,
        )
        object.__setattr__(self, "_BoundedEvidenceReductionGateV1__sealed", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_BoundedEvidenceReductionGateV1__sealed", False):
            raise AttributeError("evidence-reduction gate composition is immutable")
        object.__setattr__(self, name, value)

    def evaluate(
        self,
        *,
        policy: dict[str, Any] | None,
        obligations: dict[str, Any] | None,
        permanent_trail: dict[str, Any] | None,
        planned_manifest: dict[str, Any] | None,
        authorization: dict[str, Any] | None,
        cohort: dict[str, Any] | None,
        authority_provenance_reference: str | None,
        authority_evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Resolve provenance gate-side and evaluate without side effects."""

        return _evaluate_evidence_reduction_gate(
            policy=policy,
            obligations=obligations,
            permanent_trail=permanent_trail,
            planned_manifest=planned_manifest,
            authorization=authorization,
            cohort=cohort,
            authority_provenance_reference=authority_provenance_reference,
            authority_evidence=authority_evidence,
            authority_provenance_resolver=self.__authority_provenance_resolver,
        )

    def record_decision(
        self,
        *,
        ledger: RuntimeLedger,
        runtime_id: str,
        artifact: dict[str, Any],
        decision_inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Recompute and append one decision through this same fixed gate."""

        if not isinstance(ledger, RuntimeLedger):
            raise FailClosedRuntimeError("existing RuntimeLedger is required")
        _require_text(runtime_id, "runtime_id")
        _validate_artifact(artifact, GATE_DECISION_ARTIFACT_V1)
        required_inputs = {
            "policy",
            "obligations",
            "permanent_trail",
            "planned_manifest",
            "authorization",
            "cohort",
            "authority_provenance_reference",
            "authority_evidence",
        }
        if (
            not isinstance(decision_inputs, dict)
            or set(decision_inputs) != required_inputs
        ):
            raise FailClosedRuntimeError(
                "gate decision recording requires exact immutable decision inputs"
            )
        recomputed = self.evaluate(**decision_inputs)
        if recomputed != artifact:
            raise FailClosedRuntimeError(
                "gate decision does not match recomputed bound inputs"
            )
        return ledger.append(
            runtime_id,
            f"evidence_reduction:{GATE_DECISION_ARTIFACT_V1.lower()}",
            artifact,
        )


def _evaluate_evidence_reduction_gate(
    *,
    policy: dict[str, Any] | None,
    obligations: dict[str, Any] | None,
    permanent_trail: dict[str, Any] | None,
    planned_manifest: dict[str, Any] | None,
    authorization: dict[str, Any] | None,
    cohort: dict[str, Any] | None,
    authority_provenance_reference: str | None,
    authority_evidence: dict[str, Any] | None = None,
    authority_provenance_resolver: TrustedAuthorityProvenanceResolverV1,
) -> dict[str, Any]:
    """Evaluate without side effects; every invalid condition returns denial."""

    artifacts = {
        "policy": policy,
        "obligations": obligations,
        "permanent_trail": permanent_trail,
        "planned_manifest": planned_manifest,
        "authorization": authorization,
        "cohort": cohort,
    }
    failures: list[str] = []
    expected_types = {
        "policy": DOMAIN_REDUCTION_POLICY_ARTIFACT_V1,
        "obligations": EVIDENCE_OBLIGATION_PROJECTION_ARTIFACT_V1,
        "permanent_trail": PERMANENT_TRAIL_ARTIFACT_V1,
        "planned_manifest": PLANNED_REDUCTION_MANIFEST_ARTIFACT_V1,
        "authorization": REDUCTION_AUTHORIZATION_ARTIFACT_V1,
        "cohort": ARTICLE_10_COHORT_ARTIFACT_V1,
    }
    for name, artifact in artifacts.items():
        if artifact is None:
            failures.append(f"{name.upper()}_MISSING")
            continue
        try:
            _validate_artifact(artifact, expected_types[name])
        except FailClosedRuntimeError:
            failures.append(f"{name.upper()}_TAMPERED_OR_MALFORMED")

    cohort_result = STOP_FURTHER_REDUCTION
    if cohort is not None and "COHORT_TAMPERED_OR_MALFORMED" not in failures:
        try:
            cohort_result = classify_article10_cohort(cohort)
        except FailClosedRuntimeError:
            failures.append("COHORT_INVALID")
        if cohort_result in {STOP_FURTHER_REDUCTION, PRIOR_VALID_OUTCOME_PRESERVED}:
            failures.append(cohort_result)

    if policy is not None and "POLICY_TAMPERED_OR_MALFORMED" not in failures:
        if policy.get("complete") is not True:
            failures.append("POLICY_INCOMPLETE")
        if policy.get("authenticated") is not True:
            failures.append("POLICY_UNAUTHENTICATED")
        if policy.get("current") is not True:
            failures.append("POLICY_STALE")
        if policy.get("ambiguous") is not False:
            failures.append("POLICY_AMBIGUOUS")
        if policy.get("bounded_scope") is not True:
            failures.append("POLICY_OVERBROAD")

    if obligations is not None and "OBLIGATIONS_TAMPERED_OR_MALFORMED" not in failures:
        statuses = obligations.get("obligation_statuses")
        if not isinstance(statuses, dict) or set(statuses) != set(OBLIGATION_CLASSES):
            failures.append("OBLIGATION_PROJECTION_INCOMPLETE")
        elif any(statuses[name] != CLOSED for name in OBLIGATION_CLASSES):
            failures.append("EVIDENCE_OBLIGATION_OPEN")
        if obligations.get("authenticated") is not True:
            failures.append("OBLIGATION_PROJECTION_UNAUTHENTICATED")
        if obligations.get("current") is not True:
            failures.append("OBLIGATION_PROJECTION_STALE")
        if obligations.get("external_authority_status") != NO_STRICTER_RETENTION_REQUIRED:
            failures.append("EXTERNAL_RETENTION_AUTHORITY_UNRESOLVED")
        if obligations.get("stricter_requirement_status") != NO_STRICTER_RETENTION_REQUIRED:
            failures.append("STRICTER_REQUIREMENT_REQUIRES_PRESERVATION")

    if permanent_trail is not None and "PERMANENT_TRAIL_TAMPERED_OR_MALFORMED" not in failures:
        if not all(permanent_trail.get(field) is True for field in ("complete", "verified", "immutable")):
            failures.append("PERMANENT_TRAIL_INCOMPLETE")
        if not permanent_trail.get("replay_provenance"):
            failures.append("PERMANENT_TRAIL_PROVENANCE_MISSING")

    if authorization is not None and "AUTHORIZATION_TAMPERED_OR_MALFORMED" not in failures:
        if authorization.get("authenticated") is not True:
            failures.append("AUTHORIZATION_UNAUTHENTICATED")
        if authorization.get("current") is not True:
            failures.append("AUTHORIZATION_STALE")
        if authorization.get("ambiguous") is not False:
            failures.append("AUTHORIZATION_AMBIGUOUS")
        if authorization.get("bounded_scope") is not True:
            failures.append("AUTHORIZATION_OVERBROAD")

    authority_provenance_fingerprint = _fingerprint(
        authority_provenance_reference
    )
    if authority_evidence is not None:
        failures.append("CALLER_AUTHORITY_EVIDENCE_FORBIDDEN")
    if all(
        artifact is not None
        for artifact in (policy, obligations, permanent_trail, authorization, cohort)
    ) and not any(
        code.endswith("_TAMPERED_OR_MALFORMED") for code in failures
    ):
        try:
            authority_provenance_fingerprint = _validate_authority_provenance(
                resolver=authority_provenance_resolver,
                provenance_root_identity=authority_provenance_reference,
                policy=policy,
                obligations=obligations,
                permanent_trail=permanent_trail,
                authorization=authorization,
                cohort=cohort,
            )
        except FailClosedRuntimeError:
            failures.append("AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID")

    if not failures:
        failures.extend(
            _cross_binding_failures(
                policy=policy,
                obligations=obligations,
                permanent_trail=permanent_trail,
                planned_manifest=planned_manifest,
                authorization=authorization,
                cohort=cohort,
            )
        )

    decision = ALLOW_BOUNDED_EVIDENCE_REDUCTION if not failures else DO_NOT_REDUCE_EVIDENCE
    input_hashes = {name: _fingerprint(value) for name, value in artifacts.items()}
    input_hashes["authority_provenance"] = authority_provenance_fingerprint
    basis = {
        "artifact_type": GATE_DECISION_ARTIFACT_V1,
        "gate_version": EVIDENCE_REDUCTION_GATE_VERSION,
        "article_10_boundary_commit": ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT,
        "decision": decision,
        "failure_codes": failures,
        "cohort_result": cohort_result,
        "input_hashes": input_hashes,
        "side_effect_performed": False,
        "physical_reduction_performed": False,
        "semantic_authority_created": False,
        "authority_paths": 1,
        "production_paths": 1,
        "parallel_paths": 0,
        "human_entry_paths": 1,
    }
    decision_seed = replay_hash(basis).split(":", 1)[1]
    basis["decision_id"] = f"EVIDENCE-REDUCTION-GATE-{decision_seed[:24]}"
    return _artifact(basis)


def create_actual_reduction_manifest(
    *,
    manifest_id: str,
    planned_manifest: dict[str, Any],
    authorization: dict[str, Any],
    gate_decision: dict[str, Any],
    execution_evidence_reference: str,
    execution_evidence_hash: str,
    evidence_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Record disposition evidence; this function performs no reduction."""

    _validate_artifact(planned_manifest, PLANNED_REDUCTION_MANIFEST_ARTIFACT_V1)
    _validate_artifact(authorization, REDUCTION_AUTHORIZATION_ARTIFACT_V1)
    _validate_artifact(gate_decision, GATE_DECISION_ARTIFACT_V1)
    if gate_decision["decision"] != ALLOW_BOUNDED_EVIDENCE_REDUCTION:
        raise FailClosedRuntimeError("actual manifest requires a passing gate decision")
    if authorization["planned_manifest_hash"] != planned_manifest["replay_hash"]:
        raise FailClosedRuntimeError("actual manifest authorization binding mismatch")
    if gate_decision["input_hashes"].get("planned_manifest") != _fingerprint(planned_manifest):
        raise FailClosedRuntimeError("actual manifest gate-to-plan binding mismatch")
    if gate_decision["input_hashes"].get("authorization") != _fingerprint(authorization):
        raise FailClosedRuntimeError("actual manifest gate-to-authorization binding mismatch")

    actual_items = _manifest_items(evidence_items, actual=True)
    for item in actual_items:
        if item["actual_disposition"] in REDUCING_DISPOSITIONS and (
            item["evidence_id"] == planned_manifest["permanent_trail_id"]
            or item["prior_hash"] == planned_manifest["permanent_trail_hash"]
        ):
            raise FailClosedRuntimeError(
                "actual reduction manifest cannot reduce the permanent trail"
            )
    planned_by_id = {item["evidence_id"]: item for item in planned_manifest["evidence_items"]}
    actual_by_id = {item["evidence_id"]: item for item in actual_items}
    if set(actual_by_id) != set(planned_by_id):
        raise FailClosedRuntimeError("actual manifest evidence identity set mismatch")
    for evidence_id, planned in planned_by_id.items():
        actual = actual_by_id[evidence_id]
        if actual["prior_hash"] != planned["evidence_hash"]:
            raise FailClosedRuntimeError("actual manifest prior evidence hash mismatch")
        if actual["actual_disposition"] != planned["planned_disposition"]:
            raise FailClosedRuntimeError("actual manifest disposition diverges from plan")
        if actual["integrity_verified"] is not True:
            raise FailClosedRuntimeError("actual manifest remaining integrity is not verified")
        if planned["planned_disposition"] == "RETAIN" and actual["retained_hash"] != planned["evidence_hash"]:
            raise FailClosedRuntimeError("retained evidence integrity mismatch")

    artifact = _artifact(
        {
            "artifact_type": ACTUAL_REDUCTION_MANIFEST_ARTIFACT_V1,
            "gate_version": EVIDENCE_REDUCTION_GATE_VERSION,
            "manifest_id": _require_text(manifest_id, "manifest_id"),
            "domain_id": planned_manifest["domain_id"],
            "evidence_class": planned_manifest["evidence_class"],
            "reduction_type": planned_manifest["reduction_type"],
            "planned_manifest_hash": planned_manifest["replay_hash"],
            "authorization_hash": authorization["replay_hash"],
            "gate_decision_hash": gate_decision["replay_hash"],
            "policy_hash": planned_manifest["policy_hash"],
            "permanent_trail_id": planned_manifest["permanent_trail_id"],
            "permanent_trail_hash": planned_manifest["permanent_trail_hash"],
            "cohort_hash": planned_manifest["cohort_hash"],
            "execution_evidence_reference": _require_text(
                execution_evidence_reference, "execution_evidence_reference"
            ),
            "execution_evidence_hash": _require_hash(
                execution_evidence_hash, "execution_evidence_hash"
            ),
            "evidence_items": actual_items,
            "constitutional_replay_provenance_preserved": True,
            "remaining_evidence_integrity_verified": True,
            "disposition_record_complete": True,
            "physical_reduction_performed_by_gate": False,
            "full_replay_claimed": False,
        }
    )
    validate_actual_reduction_manifest(artifact)
    return artifact


def validate_actual_reduction_manifest(artifact: dict[str, Any]) -> None:
    """Verify the immutable disposition record without asserting data exists."""

    _validate_artifact(artifact, ACTUAL_REDUCTION_MANIFEST_ARTIFACT_V1)
    items = _manifest_items(artifact.get("evidence_items"), actual=True)
    if any(
        item["actual_disposition"] in REDUCING_DISPOSITIONS
        and (
            item["evidence_id"] == artifact["permanent_trail_id"]
            or item["prior_hash"] == artifact["permanent_trail_hash"]
        )
        for item in items
    ):
        raise FailClosedRuntimeError(
            "actual reduction manifest cannot reduce the permanent trail"
        )
    required_true = (
        "constitutional_replay_provenance_preserved",
        "remaining_evidence_integrity_verified",
        "disposition_record_complete",
    )
    if not all(artifact.get(field) is True for field in required_true):
        raise FailClosedRuntimeError("actual reduction manifest is incomplete")
    if artifact.get("physical_reduction_performed_by_gate") is not False:
        raise FailClosedRuntimeError("physical reduction is outside gate scope")
    if artifact.get("full_replay_claimed") is not False:
        raise FailClosedRuntimeError("manifest cannot claim full Replay")


def record_reduction_evidence(
    *,
    ledger: RuntimeLedger,
    runtime_id: str,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Append one validated artifact to an existing RuntimeLedger lineage."""

    if not isinstance(ledger, RuntimeLedger):
        raise FailClosedRuntimeError("existing RuntimeLedger is required")
    _require_text(runtime_id, "runtime_id")
    artifact_type = artifact.get("artifact_type") if isinstance(artifact, dict) else None
    if artifact_type not in _KNOWN_ARTIFACT_TYPES:
        raise FailClosedRuntimeError("evidence-reduction artifact type is not recognized")
    _validate_artifact(artifact, artifact_type)
    if artifact_type == GATE_DECISION_ARTIFACT_V1:
        raise FailClosedRuntimeError(
            "gate decisions must be recorded through their fixed trusted gate"
        )
    if artifact_type == ACTUAL_REDUCTION_MANIFEST_ARTIFACT_V1:
        validate_actual_reduction_manifest(artifact)
    return ledger.append(
        runtime_id,
        f"evidence_reduction:{artifact_type.lower()}",
        artifact,
    )


def _authority_provenance_scope(
    *,
    policy: dict[str, Any],
    obligations: dict[str, Any],
    permanent_trail: dict[str, Any],
    cohort: dict[str, Any],
) -> dict[str, Any]:
    return {
        "domain_id": policy["domain_id"],
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "applicable_at_commit": policy["applicable_at_commit"],
        "allowed_evidence_classes": policy["allowed_evidence_classes"],
        "allowed_reduction_types": policy["allowed_reduction_types"],
        "obligations_hash": obligations["replay_hash"],
        "permanent_trail_hash": permanent_trail["replay_hash"],
        "cohort_hash": cohort["replay_hash"],
    }


def _validate_authority_provenance(
    *,
    resolver: TrustedAuthorityProvenanceResolverV1,
    provenance_root_identity: str | None,
    policy: dict[str, Any],
    obligations: dict[str, Any],
    permanent_trail: dict[str, Any],
    authorization: dict[str, Any],
    cohort: dict[str, Any],
) -> str:
    """Resolve and bind one owner-produced root before CHE validation."""

    if type(resolver) is not TrustedAuthorityProvenanceResolverV1:
        raise FailClosedRuntimeError(
            "authority provenance resolver is not constitutionally fixed"
        )
    if not isinstance(provenance_root_identity, str):
        raise FailClosedRuntimeError("authority provenance reference is missing")
    root = resolver.resolve(provenance_root_identity)
    expected_scope = _authority_provenance_scope(
        policy=policy,
        obligations=obligations,
        permanent_trail=permanent_trail,
        cohort=cohort,
    )
    revision = _policy_revision(policy["policy_version"])
    correlation_identity = root["request_evidence_correlation_identity"]
    correlation_hash = root["request_evidence_correlation_hash"]
    if (
        root["authorization_owner_identity"] != AUTHORIZATION_OWNER_IDENTITY
        or root["authorization_act_class"]
        != OWNER_ISSUED_AUTHORIZATION_ACT_CLASS
        or root["action_kind"]
        != BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION
        or root["subject_identity"] != policy["policy_id"]
        or root["scope"] != expected_scope
        or root["act_revision"] != revision
        or policy["authority_provenance_root_identity"]
        != root["provenance_root_identity"]
        or authorization["authority_provenance_root_identity"]
        != root["provenance_root_identity"]
        or policy["authority_provenance_root_hash"]
        != root["immutable_content_hash"]
        or authorization["authority_provenance_root_hash"]
        != root["immutable_content_hash"]
        or policy["authority_evidence_reference"] != correlation_identity
        or policy["currentness_evidence_reference"] != correlation_identity
        or authorization["authority_evidence_reference"] != correlation_identity
        or policy["authority_evidence_hash"] != correlation_hash
        or policy["currentness_evidence_hash"] != correlation_hash
        or authorization["authority_evidence_hash"] != correlation_hash
    ):
        raise FailClosedRuntimeError(
            "authority provenance owner, act, action, subject, scope, "
            "revision, correlation, or root binding is invalid"
        )
    authority_evidence_fingerprint = _validate_authority_evidence(
        policy=policy,
        obligations=obligations,
        permanent_trail=permanent_trail,
        authorization=authorization,
        cohort=cohort,
        authority_evidence=root["owner_issued_authority_evidence"],
    )
    return replay_hash(
        {
            "provenance_root": root,
            "resolved_authority_evidence_fingerprint": (
                authority_evidence_fingerprint
            ),
            "resolver_boundary_commit": resolver.boundary_commit,
        }
    )


def _validate_authority_evidence(
    *,
    policy: dict[str, Any],
    obligations: dict[str, Any],
    permanent_trail: dict[str, Any],
    authorization: dict[str, Any],
    cohort: dict[str, Any],
    authority_evidence: dict[str, Any] | None,
) -> str:
    """Authenticate one policy through existing Human Authority and CHE facts."""

    if not isinstance(authority_evidence, dict) or set(authority_evidence) != {
        "human_authority_act",
        "che_request",
        "che_continuation",
        "che_evidence_correlation",
    }:
        raise FailClosedRuntimeError("authority evidence bundle is incomplete")
    act = validate_canonical_human_authority_act_v1(
        authority_evidence["human_authority_act"]
    )
    correlation = validate_canonical_che_evidence_correlation_v1(
        authority_evidence["che_evidence_correlation"]
    )
    expected_payload = domain_reduction_policy_authority_payload(
        domain_id=policy["domain_id"],
        policy_id=policy["policy_id"],
        policy_version=policy["policy_version"],
        authority_id=policy["authority_id"],
        applicable_at_commit=policy["applicable_at_commit"],
        allowed_evidence_classes=policy["allowed_evidence_classes"],
        allowed_reduction_types=policy["allowed_reduction_types"],
        obligations_hash=obligations["replay_hash"],
        permanent_trail_hash=permanent_trail["replay_hash"],
        cohort_hash=cohort["replay_hash"],
    )
    revision = _policy_revision(policy["policy_version"])
    act = bind_canonical_human_authority_act_to_che_v1(
        act,
        authority_evidence["che_request"],
        authority_evidence["che_continuation"],
        expected_authority_kind=AUTHORIZATION,
        expected_target_identity=policy["policy_id"],
        expected_target_revision=revision,
        expected_producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=policy["authority_id"],
        expected_authority_scope=EVIDENCE_REDUCTION_POLICY_AUTHORITY_SCOPE,
    )
    if (
        act.authority_kind != AUTHORIZATION
        or act.producing_owner != HUMAN_AUTHORITY_OWNER
        or act.expected_owner != policy["authority_id"]
        or act.authority_scope != EVIDENCE_REDUCTION_POLICY_AUTHORITY_SCOPE
        or act.target_identity != policy["policy_id"]
        or act.target_revision != revision
        or act.to_dict()["payload"] != expected_payload
    ):
        raise FailClosedRuntimeError("Human Authority policy binding is invalid")
    if (
        correlation.evidence_status != RECORDED
        or correlation.actor_identity != act.actor_identity
        or correlation.request_identity != act.request_identity
        or correlation.source_act_identity != act.authority_act_identity
        or correlation.source_act_digest
        != canonical_che_request_source_act_digest_v1(
            authority_evidence["che_request"]
        )
        or correlation.continuation_identity != act.continuation_identity
        or correlation.authority_act_identity != act.authority_act_identity
        or correlation.authority_kind != act.authority_kind
        or correlation.authority_requesting_owner_identity != act.expected_owner
        or correlation.authority_target_identity != act.target_identity
        or correlation.authority_target_revision != act.target_revision
        or correlation.authority_payload_digest != act.payload_digest
        or correlation.producing_owner_identity != policy["authority_id"]
        or correlation.owner_state_identity
        != authority_evidence["che_continuation"][
            "expected_owner_state_identity"
        ]
        or correlation.owner_revision_before != act.target_revision
        or correlation.owner_revision_after != act.target_revision + 1
        or correlation.owner_advancement != "ADVANCED"
        or correlation.owner_disposition != "RECORDED"
    ):
        raise FailClosedRuntimeError("CHE authority correlation is invalid")
    correlation_hash = replay_hash(correlation.to_dict())
    bindings = (
        policy["authority_evidence_reference"],
        policy["currentness_evidence_reference"],
        authorization["authority_evidence_reference"],
    )
    hashes = (
        policy["authority_evidence_hash"],
        policy["currentness_evidence_hash"],
        authorization["authority_evidence_hash"],
    )
    if any(value != correlation.correlation_identity for value in bindings) or any(
        value != correlation_hash for value in hashes
    ):
        raise FailClosedRuntimeError("authority evidence reference binding is invalid")
    return replay_hash(
        {
            "human_authority_act": act.to_dict(),
            "che_request": authority_evidence["che_request"],
            "che_continuation": authority_evidence["che_continuation"],
            "che_evidence_correlation": correlation.to_dict(),
        }
    )


def _cross_binding_failures(
    *,
    policy: dict[str, Any],
    obligations: dict[str, Any],
    permanent_trail: dict[str, Any],
    planned_manifest: dict[str, Any],
    authorization: dict[str, Any],
    cohort: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    domain = policy["domain_id"]
    evidence_class = planned_manifest["evidence_class"]
    reduction_type = planned_manifest["reduction_type"]
    if any(item.get("domain_id") != domain for item in (obligations, permanent_trail, planned_manifest, authorization)):
        failures.append("DOMAIN_BINDING_DIVERGENT")
    if any(item.get("evidence_class") != evidence_class for item in (obligations, permanent_trail, authorization)):
        failures.append("EVIDENCE_CLASS_BINDING_DIVERGENT")
    if policy["allowed_evidence_classes"] != [evidence_class]:
        failures.append("POLICY_EVIDENCE_SCOPE_NOT_EXACT")
    if policy["allowed_reduction_types"] != [reduction_type]:
        failures.append("POLICY_REDUCTION_SCOPE_NOT_EXACT")
    if authorization["reduction_type"] != reduction_type:
        failures.append("AUTHORIZATION_REDUCTION_TYPE_MISMATCH")
    if authorization["policy_id"] != policy["policy_id"] or authorization["policy_version"] != policy["policy_version"]:
        failures.append("AUTHORIZATION_POLICY_IDENTITY_MISMATCH")
    if authorization["policy_hash"] != policy["replay_hash"] or planned_manifest["policy_hash"] != policy["replay_hash"]:
        failures.append("POLICY_HASH_BINDING_MISMATCH")
    if authorization["authority_id"] != policy["authority_id"]:
        failures.append("AUTHORITY_DIVERGENT")
    if authorization["authority_evidence_hash"] != policy["authority_evidence_hash"]:
        failures.append("AUTHORITY_EVIDENCE_DIVERGENT")
    if authorization["permanent_trail_hash"] != permanent_trail["replay_hash"]:
        failures.append("AUTHORIZATION_TRAIL_MISMATCH")
    if planned_manifest["permanent_trail_hash"] != permanent_trail["replay_hash"]:
        failures.append("MANIFEST_TRAIL_MISMATCH")
    if planned_manifest["permanent_trail_id"] != permanent_trail["trail_id"]:
        failures.append("MANIFEST_TRAIL_IDENTITY_MISMATCH")
    if authorization["planned_manifest_hash"] != planned_manifest["replay_hash"]:
        failures.append("AUTHORIZATION_MANIFEST_MISMATCH")
    if planned_manifest["cohort_hash"] != cohort["replay_hash"]:
        failures.append("MANIFEST_COHORT_MISMATCH")
    if authorization["article_10_boundary_commit"] != ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT:
        failures.append("AUTHORIZATION_BOUNDARY_MISMATCH")
    if planned_manifest["article_10_boundary_commit"] != ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT:
        failures.append("MANIFEST_BOUNDARY_MISMATCH")
    observed_commit = cohort["observed_commit"]
    if policy["applicable_at_commit"] != observed_commit or authorization["applicable_at_commit"] != observed_commit:
        failures.append("CURRENTNESS_COMMIT_MISMATCH")

    try:
        expected_basis = calculate_gate_basis_hash(
            policy=policy,
            obligations=obligations,
            permanent_trail=permanent_trail,
            planned_manifest=planned_manifest,
            cohort=cohort,
        )
    except FailClosedRuntimeError:
        failures.append("GATE_BASIS_INVALID")
    else:
        if authorization["gate_basis_hash"] != expected_basis:
            failures.append("AUTHORIZATION_GATE_BASIS_MISMATCH")

    reduced_ids = sorted(
        item["evidence_id"]
        for item in planned_manifest["evidence_items"]
        if item["planned_disposition"] in REDUCING_DISPOSITIONS
    )
    if authorization["authorized_evidence_ids"] != reduced_ids:
        failures.append("AUTHORIZATION_SCOPE_MISMATCH")
    if any(
        item["planned_disposition"] in REDUCING_DISPOSITIONS
        and (
            item["evidence_id"] == permanent_trail["trail_id"]
            or item["evidence_hash"] == permanent_trail["replay_hash"]
        )
        for item in planned_manifest["evidence_items"]
    ):
        failures.append("PERMANENT_TRAIL_IN_REDUCTION_SCOPE")
    return failures


def _artifact(value: dict[str, Any]) -> dict[str, Any]:
    return with_replay_hash(value)


def _validate_artifact(value: Any, artifact_type: str) -> None:
    if not isinstance(value, dict) or value.get("artifact_type") != artifact_type:
        raise FailClosedRuntimeError("evidence-reduction artifact identity mismatch")
    if value.get("gate_version") != EVIDENCE_REDUCTION_GATE_VERSION:
        raise FailClosedRuntimeError("evidence-reduction gate version mismatch")
    expected_fields = _ARTIFACT_FIELDS.get(artifact_type)
    if expected_fields is None or set(value) != expected_fields:
        raise FailClosedRuntimeError("evidence-reduction artifact field closure mismatch")
    verify_replay_hash(value)


def _artifact_hash(value: Any) -> str:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("evidence-reduction artifact is required")
    _validate_artifact(value, value.get("artifact_type"))
    return value["replay_hash"]


def _fingerprint(value: Any) -> str:
    if value is None:
        return "MISSING"
    try:
        return replay_hash(value)
    except FailClosedRuntimeError:
        return "UNSERIALIZABLE"


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required and must be exact text")
    return value


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(f"{field_name} must be a SHA-256 reference")
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(f"{field_name} must be a SHA-256 reference") from exc
    return text


def _require_bool(value: Any, field_name: str) -> bool:
    if type(value) is not bool:
        raise FailClosedRuntimeError(f"{field_name} must be boolean")
    return value


def _policy_revision(value: Any) -> int:
    text = _require_text(value, "policy_version")
    if len(text) < 2 or text[0] != "V" or not text[1:].isdigit():
        raise FailClosedRuntimeError("policy_version cannot bind a CHE revision")
    return int(text[1:])


def _text_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"{field_name} must be a non-empty list")
    normalized = [_require_text(item, field_name) for item in value]
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError(f"{field_name} contains duplicates")
    return sorted(normalized)


def _lineage(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("replay_provenance must be a non-empty list")
    lineage: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {"reference", "hash"}:
            raise FailClosedRuntimeError("replay provenance item is malformed")
        lineage.append(
            {
                "reference": _require_text(item["reference"], "replay reference"),
                "hash": _require_hash(item["hash"], "replay hash"),
            }
        )
    return lineage


def _manifest_items(value: Any, *, actual: bool) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("manifest evidence_items must be a non-empty list")
    expected = (
        {"evidence_id", "prior_hash", "actual_disposition", "retained_reference", "retained_hash", "integrity_verified"}
        if actual
        else {"evidence_id", "evidence_hash", "planned_disposition"}
    )
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != expected:
            raise FailClosedRuntimeError("manifest evidence item is malformed")
        evidence_id = _require_text(item["evidence_id"], "evidence_id")
        if evidence_id in seen:
            raise FailClosedRuntimeError("manifest evidence identity is duplicated")
        seen.add(evidence_id)
        if actual:
            disposition = _require_text(item["actual_disposition"], "actual_disposition")
            if disposition not in PLANNED_DISPOSITIONS:
                raise FailClosedRuntimeError("actual disposition is invalid")
            normalized.append(
                {
                    "evidence_id": evidence_id,
                    "prior_hash": _require_hash(item["prior_hash"], "prior_hash"),
                    "actual_disposition": disposition,
                    "retained_reference": _require_text(item["retained_reference"], "retained_reference"),
                    "retained_hash": _require_hash(item["retained_hash"], "retained_hash"),
                    "integrity_verified": _require_bool(item["integrity_verified"], "integrity_verified"),
                }
            )
        else:
            disposition = _require_text(item["planned_disposition"], "planned_disposition")
            if disposition not in PLANNED_DISPOSITIONS:
                raise FailClosedRuntimeError("planned disposition is invalid")
            normalized.append(
                {
                    "evidence_id": evidence_id,
                    "evidence_hash": _require_hash(item["evidence_hash"], "evidence_hash"),
                    "planned_disposition": disposition,
                }
            )
    return sorted(normalized, key=lambda item: item["evidence_id"])


__all__ = [name for name in globals() if name.isupper()] + [
    "BoundedEvidenceReductionGateV1",
    "calculate_gate_basis_hash",
    "classify_article10_cohort",
    "create_actual_reduction_manifest",
    "create_article10_cohort_projection",
    "create_domain_reduction_policy_projection",
    "create_obligation_projection",
    "create_permanent_trail_projection",
    "create_planned_reduction_manifest",
    "create_reduction_authorization",
    "domain_reduction_policy_authority_payload",
    "record_reduction_evidence",
    "validate_actual_reduction_manifest",
]
