"""Read-only G76 Revision 4 G70-04 to G70-05 evidence binding.

This module reconstructs the already-recorded G70-04 artifact from canonical
CHE evidence and passes that exact artifact to the existing G70-05
certification contract.  Reconstruction creates no Human authority, consumes
no Continuation, invokes no CHE owner, and performs no persistence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, TypeVar

from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CanonicalCHEEvidenceCorrelationV1,
    read_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CLIA_CONFORMANCE_PROFILE_V1,
    create_canonical_hic_human_authority_act_request_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    HUMAN_AUTHORITY_OWNER,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    TERMINAL_CONTINUATION,
    CanonicalContinuationEnvelopeV1,
    deserialize_canonical_che_response_envelope_v1,
)
from aigol.runtime.constitutional_amendment_certification_contract_v1 import (
    CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE,
    CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE,
    CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE,
    HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE,
    ConstitutionalAmendmentCertificationArtifactV1,
    ConstitutionalAmendmentCertificationEvidenceReferenceV1,
    certify_constitutional_amendment_v1,
    validate_constitutional_amendment_certification_artifact_v1,
)
from aigol.runtime.constitutional_gap_determination_evidence_contract_v1 import (
    CONSTITUTIONAL_CERTIFICATION_OWNER,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    RATIFY_CONSTITUTIONAL_AMENDMENT,
    ConstitutionalHumanRatificationArtifactV1,
    validate_constitutional_human_ratification_artifact_v1,
)
from aigol.runtime.g76_revision_4_ratification_operator_binding_v1 import (
    create_explicit_g76_revision_4_human_act_v1,
)
from aigol.runtime.g76_revision_4_ratification_owner_composition_v1 import (
    G76_REVISION_4_RATIFICATION_RECORDED_STATUS,
    compose_g76_revision_4_human_ratification_v1,
    materialize_g76_revision_4_ratification_package_v1,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    _read_canonical_che_continuation_binding_v1,
    _read_canonical_che_delivery_record_v1,
    _validate_canonical_che_delivery_request_binding_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


G76_REVISION_4_CERTIFICATION_BINDING_VERSION = (
    "G76_REVISION_4_G70_04_TO_G70_05_CERTIFICATION_BINDING_V1"
)

_T = TypeVar("_T")


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(
            f"G76 Revision 4 certification binding {field_name} is invalid"
        )
    return value


def _require_sha256(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(
            f"G76 Revision 4 certification binding {field_name} is invalid"
        )
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"G76 Revision 4 certification binding {field_name} is invalid"
        ) from exc
    return text


def _read_exact_store(
    store: Path,
    reader: Callable[[Path], _T],
    *,
    expected_count: int,
    record_kind: str,
) -> tuple[_T, ...]:
    paths = sorted(store.glob("*.json")) if store.is_dir() else []
    if len(paths) != expected_count:
        raise FailClosedRuntimeError(
            f"G76 Revision 4 {record_kind} evidence count is invalid"
        )
    return tuple(reader(path) for path in paths)


def _select_one(
    values: tuple[_T, ...],
    predicate: Callable[[_T], bool],
    record_kind: str,
) -> _T:
    matches = tuple(value for value in values if predicate(value))
    if len(matches) != 1:
        raise FailClosedRuntimeError(
            f"G76 Revision 4 {record_kind} evidence is absent or ambiguous"
        )
    return matches[0]


def recover_g76_revision_4_human_ratification_v1(
    *,
    repository_root: str | Path,
    runtime_root: str | Path,
    ratified_at: str,
    expected_human_authority_act_identity: str,
    expected_human_authority_act_digest: str,
    expected_ratification_identity: str,
    expected_ratification_digest: str,
    expected_terminal_response_identity: str,
    expected_terminal_continuation_identity: str,
) -> ConstitutionalHumanRatificationArtifactV1:
    """Recover and validate the exact prior artifact without authority effects."""

    repository = Path(repository_root).resolve()
    runtime = Path(runtime_root).resolve()
    bound_ratified_at = _require_text(ratified_at, "ratified_at")
    bound_act_identity = _require_text(
        expected_human_authority_act_identity,
        "expected_human_authority_act_identity",
    )
    bound_act_digest = _require_sha256(
        expected_human_authority_act_digest,
        "expected_human_authority_act_digest",
    )
    bound_ratification_identity = _require_text(
        expected_ratification_identity,
        "expected_ratification_identity",
    )
    bound_ratification_digest = _require_sha256(
        expected_ratification_digest,
        "expected_ratification_digest",
    )
    bound_response_identity = _require_text(
        expected_terminal_response_identity,
        "expected_terminal_response_identity",
    )
    bound_terminal_continuation_identity = _require_text(
        expected_terminal_continuation_identity,
        "expected_terminal_continuation_identity",
    )

    deliveries = _read_exact_store(
        runtime / "canonical_human_entry_delivery_resolution_v1",
        _read_canonical_che_delivery_record_v1,
        expected_count=2,
        record_kind="delivery",
    )
    continuation_records = _read_exact_store(
        runtime / "canonical_human_entry_continuations_v1",
        _read_canonical_che_continuation_binding_v1,
        expected_count=2,
        record_kind="Continuation",
    )
    correlations = _read_exact_store(
        runtime / "canonical_che_evidence_correlations_v1",
        read_canonical_che_evidence_correlation_v1,
        expected_count=2,
        record_kind="correlation",
    )

    terminal_delivery = _select_one(
        deliveries,
        lambda value: (
            value["authority_act_identity"] == bound_act_identity
            and value["response_identity"] == bound_response_identity
        ),
        "terminal delivery",
    )
    presentation_delivery = _select_one(
        deliveries,
        lambda value: value["authority_act_identity"] == "NOT_APPLICABLE",
        "presentation delivery",
    )
    terminal_correlation = _select_one(
        correlations,
        lambda value: (
            value.terminal_identity == bound_ratification_identity
            and value.authority_act_identity == bound_act_identity
            and value.response_identity == bound_response_identity
        ),
        "terminal correlation",
    )
    if terminal_delivery["evidence_correlation"] != terminal_correlation.to_dict():
        raise FailClosedRuntimeError(
            "G76 Revision 4 terminal delivery correlation is invalid"
        )
    if (
        terminal_correlation.certification_status != "NOT_CREATED"
        or terminal_correlation.replay_status != "NOT_CREATED"
        or terminal_correlation.duplicate_resolution != "ORIGINAL_DELIVERY"
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 terminal correlation state is invalid"
        )

    consumed_record = _select_one(
        continuation_records,
        lambda value: (
            value["consumption_state"] == "CONSUMED"
            and value["consumed_by_request_identity"]
            == terminal_correlation.request_identity
            and value["consumed_by_idempotency_identity"]
            == terminal_correlation.idempotency_identity
        ),
        "consumed Continuation",
    )
    terminal_record = _select_one(
        continuation_records,
        lambda value: (
            value["consumption_state"] == "AVAILABLE"
            and value["envelope"]["continuation_identity"]
            == bound_terminal_continuation_identity
        ),
        "terminal Continuation",
    )
    active_continuation = CanonicalContinuationEnvelopeV1.from_dict(
        consumed_record["envelope"]
    )
    terminal_continuation = CanonicalContinuationEnvelopeV1.from_dict(
        terminal_record["envelope"]
    )
    if (
        active_continuation.continuation_state != ACTIVE_CONTINUATION
        or terminal_continuation.continuation_state != TERMINAL_CONTINUATION
        or terminal_continuation.previous_response_identity
        != bound_response_identity
        or terminal_continuation.expected_next_act_identity
        != bound_ratification_identity
        or terminal_correlation.continuation_identity
        != active_continuation.continuation_identity
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 Continuation lineage is invalid"
        )

    terminal_response = deserialize_canonical_che_response_envelope_v1(
        terminal_delivery["serialized_response"]
    )
    if (
        terminal_response.response_identity != bound_response_identity
        or terminal_response.owner_status
        != G76_REVISION_4_RATIFICATION_RECORDED_STATUS
        or terminal_response.continuation_envelope != terminal_continuation
        or terminal_response.owner_transition.terminal_identity
        != bound_ratification_identity
        or terminal_response.certification_references
        or terminal_response.replay_references
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 terminal CHE Response is invalid"
        )

    presentation_response = deserialize_canonical_che_response_envelope_v1(
        presentation_delivery["serialized_response"]
    )
    if (
        presentation_response.continuation_envelope is None
        or presentation_response.continuation_envelope != active_continuation
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 presentation Continuation is invalid"
        )
    human_act = create_explicit_g76_revision_4_human_act_v1(
        exact_human_input=RATIFY_CONSTITUTIONAL_AMENDMENT,
        response=presentation_response,
    )
    if (
        human_act.authority_act_identity != bound_act_identity
        or replay_hash(human_act.to_dict()) != bound_act_digest
        or terminal_delivery["authority_act_digest"] != bound_act_digest
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 Human Authority Act evidence is invalid"
        )

    request = create_canonical_hic_human_authority_act_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        human_authority_act=human_act,
        continuation=active_continuation,
        request_identity=terminal_correlation.request_identity,
        order_identity=terminal_correlation.order_identity,
        idempotency_identity=terminal_correlation.idempotency_identity,
        created_at=bound_ratified_at,
    )
    _validate_canonical_che_delivery_request_binding_v1(
        terminal_delivery,
        request,
        active_continuation,
    )

    package = materialize_g76_revision_4_ratification_package_v1(repository)
    ratification = validate_constitutional_human_ratification_artifact_v1(
        compose_g76_revision_4_human_ratification_v1(
            package=package,
            human_authority_act=human_act,
            che_request=request,
            che_continuation=active_continuation,
        )
    )
    if (
        ratification.ratification_identity != bound_ratification_identity
        or ratification.artifact_digest != bound_ratification_digest
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 reconstructed ratification identity is invalid"
        )
    return ratification


def certify_g76_revision_4_ratification_v1(
    *,
    repository_root: str | Path,
    runtime_root: str | Path,
    ratified_at: str,
    certified_at: str,
    expected_human_authority_act_identity: str,
    expected_human_authority_act_digest: str,
    expected_ratification_identity: str,
    expected_ratification_digest: str,
    expected_terminal_response_identity: str,
    expected_terminal_continuation_identity: str,
) -> ConstitutionalAmendmentCertificationArtifactV1:
    """Execute existing G70-05 once over the exact recovered G70-04 input."""

    ratification = recover_g76_revision_4_human_ratification_v1(
        repository_root=repository_root,
        runtime_root=runtime_root,
        ratified_at=ratified_at,
        expected_human_authority_act_identity=(
            expected_human_authority_act_identity
        ),
        expected_human_authority_act_digest=expected_human_authority_act_digest,
        expected_ratification_identity=expected_ratification_identity,
        expected_ratification_digest=expected_ratification_digest,
        expected_terminal_response_identity=expected_terminal_response_identity,
        expected_terminal_continuation_identity=(
            expected_terminal_continuation_identity
        ),
    )
    assessment = ratification.impact_assessment
    proposal = assessment.amendment_proposal
    gap = proposal.constitutional_gap
    evidence = (
        ConstitutionalAmendmentCertificationEvidenceReferenceV1(
            evidence_role=CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE,
            producing_owner=gap.responsibility_owner,
            artifact_identity=gap.gap_identity,
            artifact_digest=gap.artifact_digest,
        ),
        ConstitutionalAmendmentCertificationEvidenceReferenceV1(
            evidence_role=CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE,
            producing_owner=proposal.proposing_owner,
            artifact_identity=proposal.proposal_identity,
            artifact_digest=proposal.artifact_digest,
        ),
        ConstitutionalAmendmentCertificationEvidenceReferenceV1(
            evidence_role=CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE,
            producing_owner=assessment.assessing_owner,
            artifact_identity=assessment.assessment_identity,
            artifact_digest=assessment.artifact_digest,
        ),
        ConstitutionalAmendmentCertificationEvidenceReferenceV1(
            evidence_role=HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE,
            producing_owner=HUMAN_AUTHORITY_OWNER,
            artifact_identity=ratification.ratification_identity,
            artifact_digest=ratification.artifact_digest,
        ),
    )
    return validate_constitutional_amendment_certification_artifact_v1(
        certify_constitutional_amendment_v1(
            human_ratification=ratification,
            certifying_owner=CONSTITUTIONAL_CERTIFICATION_OWNER,
            evidence_references=evidence,
            certified_at=_require_text(certified_at, "certified_at"),
        )
    )


__all__ = [
    "G76_REVISION_4_CERTIFICATION_BINDING_VERSION",
    "certify_g76_revision_4_ratification_v1",
    "recover_g76_revision_4_human_ratification_v1",
]
