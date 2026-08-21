from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import aigol.runtime.human_interface_runtime_entry_service as che_service
from aigol.runtime.authority_provenance import (
    AUTHORIZATION_OWNER_IDENTITY,
    BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION,
    OWNER_ISSUED_AUTHORIZATION_ACT_CLASS,
    PROFILE_A_OWNER_STATE_REVOKED,
    TrustedAuthorityProvenanceBindingV1,
    TrustedAuthorityProvenanceResolverV1,
    _persist_profile_a_owner_state_authorization_v1,
    _profile_a_event_hash,
    _profile_a_event_identity,
    _profile_a_root_identity_v1,
    authority_provenance_content_hash_v1,
    create_authority_provenance_root_v1,
)
from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
    NOT_APPLICABLE,
    RECORDED,
    create_canonical_che_evidence_correlation_v1,
    persist_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    AUTHORIZATION,
    CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION,
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    HUMAN_ACTOR,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    canonical_che_request_source_act_digest_v1,
)
from aigol.runtime.evidence_reduction_gate import (
    AFTER_BOUNDARY,
    ALLOW_BOUNDED_EVIDENCE_REDUCTION,
    ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT,
    AT_BOUNDARY,
    AUTHORIZED_OR_PLANNED_INCOMPLETE,
    BEFORE_BOUNDARY,
    CLOSED,
    DO_NOT_REDUCE_EVIDENCE,
    EVIDENCE_REDUCTION_POLICY_AUTHORITY_SCOPE,
    EFFECTIVE_GATE_REQUIRED,
    FULL_EVIDENCE_PRESENT,
    NO_STRICTER_RETENTION_REQUIRED,
    PARTIAL_OR_AMBIGUOUS,
    PRIOR_VALID_OUTCOME_PRESERVED,
    PRIOR_VALID_REDUCTION_COMPLETE,
    REVALIDATION_UNDER_EFFECTIVE_GATE_REQUIRED,
    STOP_FURTHER_REDUCTION,
    BoundedEvidenceReductionGateV1,
    _compose_profile_a_bounded_evidence_reduction_gate_v1,
    calculate_gate_basis_hash,
    create_actual_reduction_manifest,
    create_article10_cohort_projection,
    create_domain_reduction_policy_projection,
    create_obligation_projection,
    create_permanent_trail_projection,
    create_planned_reduction_manifest,
    create_reduction_authorization,
    domain_reduction_policy_authority_payload,
    record_reduction_evidence,
    validate_actual_reduction_manifest,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.ledger import RuntimeLedger
from aigol.runtime.transport.serialization import replay_hash, with_replay_hash


DOMAIN = "regulated-domain-alpha"
EVIDENCE_CLASS = "REJECTION_EVIDENCE"
REDUCTION_TYPE = "CONDENSE"
POLICY_ID = "DOMAIN-ALPHA-REDUCTION-POLICY"
POLICY_VERSION = "V1"
AUTHORITY_ID = "DOMAIN-ALPHA-HUMAN-AUTHORITY"
OBSERVED_COMMIT = "8" * 40
TRUSTED_BOUNDARY_COMMIT = "f" * 40
PROVENANCE_ROOT_IDENTITY = "G77-PROFILE-B-ROOT-1"


def _hash(label: str) -> str:
    return replay_hash({"fixture": label})


def _case(
    *,
    started_position: str = AT_BOUNDARY,
    boundary_state: str = FULL_EVIDENCE_PRESENT,
    prior_contract_validated: bool = False,
    policy_overrides: dict | None = None,
    obligation_statuses: dict[str, str] | None = None,
    obligation_overrides: dict | None = None,
    trail_overrides: dict | None = None,
    authorization_overrides: dict | None = None,
    authority_evidence_override: dict | None = None,
    provenance_root_overrides: dict | None = None,
    trusted_binding_overrides: dict | None = None,
    authority_provenance_reference: str | None = None,
    caller_authority_evidence: dict | None = None,
    permanent_trail_reduction_match: str | None = None,
    authority_created_at: str = "2026-08-21T00:00:00Z",
    profile_a_expires_at: str | None = None,
) -> dict:
    temporary_directory = TemporaryDirectory(prefix="g77-profile-a-")
    runtime_scope_identity = temporary_directory.name
    cohort = create_article10_cohort_projection(
        evidence_id="EVIDENCE-SET-1",
        observed_commit=OBSERVED_COMMIT,
        started_position=started_position,
        boundary_state=boundary_state,
        prior_contract_validated=prior_contract_validated,
    )
    statuses = {name: CLOSED for name in ("replay", "audit", "dispute", "correctness", "certification", "other")}
    statuses.update(obligation_statuses or {})
    obligation_arguments = {
        "domain_id": DOMAIN,
        "evidence_class": EVIDENCE_CLASS,
        "obligation_statuses": statuses,
        "projection_authority_id": "GOVERNANCE-EVIDENCE-OWNERS",
        "projection_evidence_reference": "replay:obligation-projection",
        "projection_evidence_hash": _hash("obligation-projection"),
        "external_authority_status": NO_STRICTER_RETENTION_REQUIRED,
        "external_authority_evidence_reference": "governance:external-authority-determination",
        "external_authority_evidence_hash": _hash("external-authority-determination"),
        "stricter_requirement_status": NO_STRICTER_RETENTION_REQUIRED,
    }
    obligation_arguments.update(obligation_overrides or {})
    obligations = create_obligation_projection(**obligation_arguments)

    trail_arguments = {
        "trail_id": "PERMANENT-TRAIL-1",
        "domain_id": DOMAIN,
        "evidence_class": EVIDENCE_CLASS,
        "attempted_action": "REJECTED_PROPOSAL",
        "subject_reference": "evidence:EVIDENCE-SET-1",
        "result_or_reason": "REJECTED_BY_CONSTITUTIONAL_VALIDATION",
        "replay_provenance": [{"reference": "replay:source-chain", "hash": _hash("source-chain")}],
        "lifecycle_disposition": "FULL_EVIDENCE_HELD_PENDING_GATE",
    }
    trail_arguments.update(trail_overrides or {})
    trail = create_permanent_trail_projection(**trail_arguments)

    authority_payload = domain_reduction_policy_authority_payload(
        domain_id=DOMAIN,
        policy_id=POLICY_ID,
        policy_version=POLICY_VERSION,
        authority_id=AUTHORITY_ID,
        applicable_at_commit=OBSERVED_COMMIT,
        allowed_evidence_classes=[EVIDENCE_CLASS],
        allowed_reduction_types=[REDUCTION_TYPE],
        obligations_hash=obligations["replay_hash"],
        permanent_trail_hash=trail["replay_hash"],
        cohort_hash=cohort["replay_hash"],
    )
    authority_act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity="G77-REDUCTION-POLICY-AUTHORITY-ACT-1",
        authority_kind=AUTHORIZATION,
        interaction_identity="G77-REDUCTION-INTERACTION-1",
        conversation_identity="G77-REDUCTION-CONVERSATION-1",
        session_identity="G77-REDUCTION-SESSION-1",
        actor_identity="G77-HUMAN-AUTHORITY-ACTOR",
        request_identity="G77-REDUCTION-REQUEST-1",
        continuation_identity="G77-REDUCTION-CONTINUATION-1",
        target_identity=POLICY_ID,
        target_revision=1,
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=AUTHORITY_ID,
        authority_scope=EVIDENCE_REDUCTION_POLICY_AUTHORITY_SCOPE,
        payload=authority_payload,
        payload_digest=canonical_human_authority_payload_digest_v1(authority_payload),
        metadata={
            "transport_fixture": "focused-g77-remediation",
            **(
                {"profile_a_expires_at": profile_a_expires_at}
                if profile_a_expires_at is not None
                else {}
            ),
        },
    )
    che_request = CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity="G77-FOCUSED-TEST-CHANNEL",
        adapter_identity="G77-FOCUSED-TEST-ADAPTER",
        actor_identity=authority_act.actor_identity,
        actor_class=HUMAN_ACTOR,
        session_identity=authority_act.session_identity,
        workspace_identity="G77-WORKSPACE",
        runtime_scope_identity=runtime_scope_identity,
        request_identity=authority_act.request_identity,
        source_act_identity=authority_act.authority_act_identity,
        order_identity="G77-ORDER-1",
        idempotency_identity="G77-IDEMPOTENCY-1",
        source_payload=authority_act.to_dict(),
        source_encoding="UTF-8",
        source_modality="STRUCTURED",
        declared_capabilities=(CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,),
        metadata={"transport_trace_identity": "G77-TRACE-1"},
        created_at=authority_created_at,
    )
    che_continuation = CanonicalContinuationEnvelopeV1(
        contract_version=CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION,
        continuation_identity=authority_act.continuation_identity,
        interaction_identity=authority_act.interaction_identity,
        conversation_identity=authority_act.conversation_identity,
        session_identity=authority_act.session_identity,
        actor_identity=authority_act.actor_identity,
        workspace_identity=che_request.workspace_identity,
        runtime_scope_identity=che_request.runtime_scope_identity,
        request_identity="G77-PRIOR-REQUEST-1",
        previous_response_identity="G77-PRIOR-RESPONSE-1",
        previous_order_identity="G77-PRIOR-ORDER-1",
        previous_idempotency_identity="G77-PRIOR-IDEMPOTENCY-1",
        continuation_sequence=1,
        expected_next_act_identity=POLICY_ID,
        expected_owner_state_identity="G77-REDUCTION-POLICY-OWNER-STATE",
        expected_owner_revision=1,
        continuation_state=ACTIVE_CONTINUATION,
        correlation_identity="G77-PRIOR-CORRELATION-1",
        metadata={"transport_trace_identity": "G77-TRACE-1"},
    )
    correlation = create_canonical_che_evidence_correlation_v1(
        contract_version=CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        interaction_identity=authority_act.interaction_identity,
        conversation_identity=authority_act.conversation_identity,
        session_identity=authority_act.session_identity,
        workspace_identity="G77-WORKSPACE",
        runtime_scope_identity=runtime_scope_identity,
        actor_identity=authority_act.actor_identity,
        source_channel_identity="G77-FOCUSED-TEST-CHANNEL",
        adapter_identity="G77-FOCUSED-TEST-ADAPTER",
        request_identity=authority_act.request_identity,
        che_entry_identity="G77-CHE-ENTRY-1",
        source_act_identity=authority_act.authority_act_identity,
        source_act_digest=canonical_che_request_source_act_digest_v1(che_request),
        order_identity="G77-ORDER-1",
        idempotency_identity="G77-IDEMPOTENCY-1",
        continuation_identity=authority_act.continuation_identity,
        continuation_sequence=1,
        authority_act_identity=authority_act.authority_act_identity,
        authority_kind=authority_act.authority_kind,
        authority_requesting_owner_identity=authority_act.expected_owner,
        authority_target_identity=authority_act.target_identity,
        authority_target_revision=authority_act.target_revision,
        authority_payload_digest=authority_act.payload_digest,
        authority_result_identity="G77-AUTHORITY-RESULT-1",
        opaque_reference_set_identity=NOT_APPLICABLE,
        ordered_reference_set_digest=NOT_APPLICABLE,
        opaque_reference_correlations=(),
        producing_owner_identity=AUTHORITY_ID,
        owner_state_identity="G77-REDUCTION-POLICY-OWNER-STATE",
        owner_revision_before=1,
        owner_revision_after=2,
        owner_advancement="ADVANCED",
        owner_disposition="RECORDED",
        next_act_identity=NOT_APPLICABLE,
        refusal_identity=NOT_APPLICABLE,
        terminal_identity=NOT_APPLICABLE,
        owner_projection_identity="G77-OWNER-PROJECTION-1",
        failure_identity=NOT_APPLICABLE,
        presentation_identity="G77-PRESENTATION-1",
        response_identity="G77-RESPONSE-1",
        response_digest=_hash("authority-response"),
        delivery_record_identity="G77-DELIVERY-1",
        delivery_status=NOT_APPLICABLE,
        duplicate_resolution=NOT_APPLICABLE,
        acknowledgement_state=NOT_APPLICABLE,
        replay_references=(),
        replay_status=NOT_APPLICABLE,
        certification_references=(),
        certification_status=NOT_APPLICABLE,
        evidence_status=RECORDED,
        metadata={"transport_fixture": "focused-g77-remediation"},
    )
    authority_evidence = {
        "human_authority_act": authority_act.to_dict(),
        "che_request": che_request.to_dict(),
        "che_continuation": che_continuation.to_dict(),
        "che_evidence_correlation": correlation.to_dict(),
    }
    authority_evidence.update(authority_evidence_override or {})
    correlation_reference = correlation.correlation_identity
    correlation_hash = replay_hash(correlation.to_dict())

    persist_canonical_che_evidence_correlation_v1(correlation)
    event_path = _persist_profile_a_owner_state_authorization_v1(
        request=che_request,
        continuation=che_continuation,
        authority_act=authority_act,
        correlation=correlation,
    )
    event = json.loads(event_path.read_text(encoding="utf-8"))
    provenance_root = event["provenance_root"]
    if provenance_root_overrides:
        provenance_root.update(deepcopy(provenance_root_overrides))
        provenance_root["immutable_content_hash"] = (
            authority_provenance_content_hash_v1(provenance_root)
        )
        event["provenance_root"] = provenance_root
    if (
        trusted_binding_overrides
        and trusted_binding_overrides.get("current") is False
    ):
        event["event_kind"] = PROFILE_A_OWNER_STATE_REVOKED
    if provenance_root_overrides or trusted_binding_overrides:
        event["event_identity"] = _profile_a_event_identity(event)
        event["event_hash"] = _profile_a_event_hash(event)
        event_path.write_text(
            json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
    gate = _compose_profile_a_bounded_evidence_reduction_gate_v1(
        runtime_scope_identity=runtime_scope_identity,
        owner_state_identity=correlation.owner_state_identity,
    )
    if authority_provenance_reference is None:
        authority_provenance_reference = provenance_root[
            "provenance_root_identity"
        ]

    policy_arguments = {
        "domain_id": DOMAIN,
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "authority_id": AUTHORITY_ID,
        "authority_evidence_reference": correlation_reference,
        "authority_evidence_hash": correlation_hash,
        "authority_provenance_root_identity": provenance_root[
            "provenance_root_identity"
        ],
        "authority_provenance_root_hash": provenance_root[
            "immutable_content_hash"
        ],
        "currentness_evidence_reference": correlation_reference,
        "currentness_evidence_hash": correlation_hash,
        "applicable_at_commit": OBSERVED_COMMIT,
        "allowed_evidence_classes": [EVIDENCE_CLASS],
        "allowed_reduction_types": [REDUCTION_TYPE],
    }
    policy_arguments.update(policy_overrides or {})
    policy = create_domain_reduction_policy_projection(**policy_arguments)

    planned_items = [
        {
            "evidence_id": "EVIDENCE-A",
            "evidence_hash": _hash("evidence-a"),
            "planned_disposition": "CONDENSE",
        },
        {
            "evidence_id": "EVIDENCE-B",
            "evidence_hash": _hash("evidence-b"),
            "planned_disposition": "RETAIN",
        },
    ]
    if permanent_trail_reduction_match == "identity":
        planned_items[0]["evidence_id"] = trail["trail_id"]
    elif permanent_trail_reduction_match == "hash":
        planned_items[0]["evidence_hash"] = trail["replay_hash"]

    planned = create_planned_reduction_manifest(
        manifest_id="PLANNED-MANIFEST-1",
        domain_id=DOMAIN,
        evidence_class=EVIDENCE_CLASS,
        reduction_type=REDUCTION_TYPE,
        evidence_items=planned_items,
        policy_hash=policy["replay_hash"],
        permanent_trail_id=trail["trail_id"],
        permanent_trail_hash=trail["replay_hash"],
        cohort_hash=cohort["replay_hash"],
    )
    gate_basis_hash = calculate_gate_basis_hash(
        policy=policy,
        obligations=obligations,
        permanent_trail=trail,
        planned_manifest=planned,
        cohort=cohort,
    )
    authorization_arguments = {
        "authorization_id": "REDUCTION-AUTHORIZATION-1",
        "domain_id": DOMAIN,
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "policy_hash": policy["replay_hash"],
        "authority_id": AUTHORITY_ID,
        "authority_evidence_reference": correlation_reference,
        "authority_evidence_hash": correlation_hash,
        "authority_provenance_root_identity": provenance_root[
            "provenance_root_identity"
        ],
        "authority_provenance_root_hash": provenance_root[
            "immutable_content_hash"
        ],
        "evidence_class": EVIDENCE_CLASS,
        "reduction_type": REDUCTION_TYPE,
        "authorized_evidence_ids": sorted(
            item["evidence_id"]
            for item in planned_items
            if item["planned_disposition"] in {"REMOVE", "CONDENSE", "OTHER_REDUCTION"}
        ),
        "gate_basis_hash": gate_basis_hash,
        "permanent_trail_hash": trail["replay_hash"],
        "planned_manifest_hash": planned["replay_hash"],
        "applicable_at_commit": OBSERVED_COMMIT,
    }
    authorization_arguments.update(authorization_overrides or {})
    authorization = create_reduction_authorization(**authorization_arguments)
    return {
        "policy": policy,
        "obligations": obligations,
        "permanent_trail": trail,
        "planned_manifest": planned,
        "authorization": authorization,
        "cohort": cohort,
        "authority_provenance_reference": authority_provenance_reference,
        "authority_evidence": caller_authority_evidence,
        "_gate": gate,
        "_provenance_root": provenance_root,
        "_profile_a_event_path": event_path,
        "_profile_a_runtime_scope": runtime_scope_identity,
        "_profile_a_owner_state_identity": correlation.owner_state_identity,
        "_temporary_directory": temporary_directory,
    }


def _append_profile_a_successor(case: dict) -> tuple[Path, dict]:
    evidence = case["_provenance_root"]["owner_issued_authority_evidence"]
    first_act = CanonicalHumanAuthorityActV1.from_dict(
        evidence["human_authority_act"]
    )
    first_request = CanonicalHumanEntryRequestEnvelopeV1.from_dict(
        evidence["che_request"]
    )
    first_continuation = CanonicalContinuationEnvelopeV1.from_dict(
        evidence["che_continuation"]
    )
    payload = first_act.to_dict()["payload"]
    payload["policy_version"] = "V2"
    second_act = replace(
        first_act,
        authority_act_identity="G77-REDUCTION-POLICY-AUTHORITY-ACT-2",
        request_identity="G77-REDUCTION-REQUEST-2",
        continuation_identity="G77-REDUCTION-CONTINUATION-2",
        target_revision=2,
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
    )
    second_request = replace(
        first_request,
        request_identity=second_act.request_identity,
        source_act_identity=second_act.authority_act_identity,
        order_identity="G77-ORDER-2",
        idempotency_identity="G77-IDEMPOTENCY-2",
        source_payload=second_act.to_dict(),
    )
    second_continuation = replace(
        first_continuation,
        continuation_identity=second_act.continuation_identity,
        request_identity=first_request.request_identity,
        previous_response_identity="G77-PRIOR-RESPONSE-2",
        previous_order_identity=first_request.order_identity,
        previous_idempotency_identity=first_request.idempotency_identity,
        continuation_sequence=2,
        expected_next_act_identity=POLICY_ID,
        expected_owner_revision=2,
        correlation_identity=evidence["che_evidence_correlation"][
            "correlation_identity"
        ],
    )
    second_correlation = create_canonical_che_evidence_correlation_v1(
        contract_version=CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        interaction_identity=second_act.interaction_identity,
        conversation_identity=second_act.conversation_identity,
        session_identity=second_act.session_identity,
        workspace_identity=second_request.workspace_identity,
        runtime_scope_identity=second_request.runtime_scope_identity,
        actor_identity=second_act.actor_identity,
        source_channel_identity=second_request.interface_identity,
        adapter_identity=second_request.adapter_identity,
        request_identity=second_act.request_identity,
        che_entry_identity="G77-CHE-ENTRY-2",
        source_act_identity=second_act.authority_act_identity,
        source_act_digest=canonical_che_request_source_act_digest_v1(
            second_request
        ),
        order_identity=second_request.order_identity,
        idempotency_identity=second_request.idempotency_identity,
        continuation_identity=second_act.continuation_identity,
        continuation_sequence=2,
        authority_act_identity=second_act.authority_act_identity,
        authority_kind=second_act.authority_kind,
        authority_requesting_owner_identity=second_act.expected_owner,
        authority_target_identity=second_act.target_identity,
        authority_target_revision=second_act.target_revision,
        authority_payload_digest=second_act.payload_digest,
        authority_result_identity="G77-AUTHORITY-RESULT-2",
        opaque_reference_set_identity=NOT_APPLICABLE,
        ordered_reference_set_digest=NOT_APPLICABLE,
        opaque_reference_correlations=(),
        producing_owner_identity=AUTHORITY_ID,
        owner_state_identity=case["_profile_a_owner_state_identity"],
        owner_revision_before=2,
        owner_revision_after=3,
        owner_advancement="ADVANCED",
        owner_disposition="RECORDED",
        next_act_identity=NOT_APPLICABLE,
        refusal_identity=NOT_APPLICABLE,
        terminal_identity=NOT_APPLICABLE,
        owner_projection_identity="G77-OWNER-PROJECTION-2",
        failure_identity=NOT_APPLICABLE,
        presentation_identity="G77-PRESENTATION-2",
        response_identity="G77-RESPONSE-2",
        response_digest=_hash("authority-response-2"),
        delivery_record_identity="G77-DELIVERY-2",
        delivery_status=NOT_APPLICABLE,
        duplicate_resolution=NOT_APPLICABLE,
        acknowledgement_state=NOT_APPLICABLE,
        replay_references=(),
        replay_status=NOT_APPLICABLE,
        certification_references=(),
        certification_status=NOT_APPLICABLE,
        evidence_status=RECORDED,
        metadata={"transport_fixture": "focused-g77-successor"},
    )
    persist_canonical_che_evidence_correlation_v1(second_correlation)
    path = _persist_profile_a_owner_state_authorization_v1(
        request=second_request,
        continuation=second_continuation,
        authority_act=second_act,
        correlation=second_correlation,
    )
    event = json.loads(path.read_text(encoding="utf-8"))
    return path, event


def _write_profile_a_event(path: Path, event: dict) -> None:
    event["event_identity"] = _profile_a_event_identity(event)
    event["event_hash"] = _profile_a_event_hash(event)
    path.write_text(
        json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _evaluate(case: dict) -> dict:
    return case["_gate"].evaluate(**_decision_inputs(case))


def _decision_inputs(case: dict) -> dict:
    return {key: value for key, value in case.items() if not key.startswith("_")}


def _clone_case_inputs(case: dict) -> dict:
    cloned = deepcopy(_decision_inputs(case))
    cloned["_gate"] = case["_gate"]
    cloned["_provenance_root"] = deepcopy(case["_provenance_root"])
    return cloned


def _actual(case: dict, decision: dict) -> dict:
    return create_actual_reduction_manifest(
        manifest_id="ACTUAL-MANIFEST-1",
        planned_manifest=case["planned_manifest"],
        authorization=case["authorization"],
        gate_decision=decision,
        execution_evidence_reference="replay:separately-authorized-executor-evidence",
        execution_evidence_hash=_hash("separately-authorized-executor-evidence"),
        evidence_items=[
            {
                "evidence_id": "EVIDENCE-A",
                "prior_hash": _hash("evidence-a"),
                "actual_disposition": "CONDENSE",
                "retained_reference": "trail:PERMANENT-TRAIL-1",
                "retained_hash": case["permanent_trail"]["replay_hash"],
                "integrity_verified": True,
            },
            {
                "evidence_id": "EVIDENCE-B",
                "prior_hash": _hash("evidence-b"),
                "actual_disposition": "RETAIN",
                "retained_reference": "evidence:EVIDENCE-B",
                "retained_hash": _hash("evidence-b"),
                "integrity_verified": True,
            },
        ],
    )


def test_exact_allow_case_is_bounded_and_zero_side_effect() -> None:
    decision = _evaluate(_case())
    assert decision["decision"] == ALLOW_BOUNDED_EVIDENCE_REDUCTION
    assert decision["failure_codes"] == []
    assert decision["side_effect_performed"] is False
    assert decision["physical_reduction_performed"] is False
    assert decision["semantic_authority_created"] is False


@pytest.mark.parametrize(
    ("policy_overrides", "failure_code"),
    [
        ({"complete": False}, "POLICY_INCOMPLETE"),
        ({"ambiguous": True}, "POLICY_AMBIGUOUS"),
        ({"current": False}, "POLICY_STALE"),
        ({"authenticated": False}, "POLICY_UNAUTHENTICATED"),
        ({"bounded_scope": False}, "POLICY_OVERBROAD"),
    ],
)
def test_invalid_authority_conditions_deny(policy_overrides: dict, failure_code: str) -> None:
    decision = _evaluate(_case(policy_overrides=policy_overrides))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert failure_code in decision["failure_codes"]


def test_missing_authority_denies() -> None:
    case = _case()
    case["policy"] = None
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "POLICY_MISSING" in decision["failure_codes"]


def test_tampered_authority_denies_without_exception() -> None:
    case = _case()
    case["policy"] = deepcopy(case["policy"])
    case["policy"]["authority_id"] = "TAMPERED"
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "POLICY_TAMPERED_OR_MALFORMED" in decision["failure_codes"]


def test_divergent_authority_denies() -> None:
    case = _case(authorization_overrides={"authority_id": "OTHER-AUTHORITY"})
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "AUTHORITY_DIVERGENT" in decision["failure_codes"]


def test_stricter_requirement_precedence_denies() -> None:
    case = _case(obligation_overrides={"stricter_requirement_status": "FULL_PRESERVATION_REQUIRED"})
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "STRICTER_REQUIREMENT_REQUIRES_PRESERVATION" in decision["failure_codes"]


def test_unresolved_external_authority_remains_fail_closed() -> None:
    case = _case(obligation_overrides={"external_authority_status": "UNRESOLVED"})
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "EXTERNAL_RETENTION_AUTHORITY_UNRESOLVED" in decision["failure_codes"]


def test_incomplete_permanent_trail_denies() -> None:
    decision = _evaluate(_case(trail_overrides={"complete": False}))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "PERMANENT_TRAIL_INCOMPLETE" in decision["failure_codes"]


def test_open_evidence_obligation_denies() -> None:
    decision = _evaluate(_case(obligation_statuses={"audit": "OPEN"}))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "EVIDENCE_OBLIGATION_OPEN" in decision["failure_codes"]


def test_authorization_manifest_mismatch_denies() -> None:
    case = _case()
    case["authorization"] = with_replay_hash(
        {**case["authorization"], "planned_manifest_hash": _hash("other-manifest")}
    )
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "AUTHORIZATION_MANIFEST_MISMATCH" in decision["failure_codes"]


def test_planned_manifest_tamper_denies_and_actual_manifest_tamper_fails_closed() -> None:
    case = _case()
    tampered_case = _clone_case_inputs(case)
    tampered_case["planned_manifest"]["evidence_items"][0]["planned_disposition"] = "REMOVE"
    assert _evaluate(tampered_case)["decision"] == DO_NOT_REDUCE_EVIDENCE

    decision = _evaluate(case)
    actual = _actual(case, decision)
    validate_actual_reduction_manifest(actual)
    tampered_actual = deepcopy(actual)
    tampered_actual["evidence_items"][0]["actual_disposition"] = "REMOVE"
    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        validate_actual_reduction_manifest(tampered_actual)


@pytest.mark.parametrize(
    ("position", "state", "prior_valid", "expected_decision", "expected_cohort"),
    [
        (BEFORE_BOUNDARY, FULL_EVIDENCE_PRESENT, False, ALLOW_BOUNDED_EVIDENCE_REDUCTION, EFFECTIVE_GATE_REQUIRED),
        (
            BEFORE_BOUNDARY,
            AUTHORIZED_OR_PLANNED_INCOMPLETE,
            False,
            ALLOW_BOUNDED_EVIDENCE_REDUCTION,
            REVALIDATION_UNDER_EFFECTIVE_GATE_REQUIRED,
        ),
        (AT_BOUNDARY, FULL_EVIDENCE_PRESENT, False, ALLOW_BOUNDED_EVIDENCE_REDUCTION, EFFECTIVE_GATE_REQUIRED),
        (AFTER_BOUNDARY, FULL_EVIDENCE_PRESENT, False, ALLOW_BOUNDED_EVIDENCE_REDUCTION, EFFECTIVE_GATE_REQUIRED),
        (
            BEFORE_BOUNDARY,
            PRIOR_VALID_REDUCTION_COMPLETE,
            True,
            DO_NOT_REDUCE_EVIDENCE,
            PRIOR_VALID_OUTCOME_PRESERVED,
        ),
        (
            BEFORE_BOUNDARY,
            PARTIAL_OR_AMBIGUOUS,
            False,
            DO_NOT_REDUCE_EVIDENCE,
            STOP_FURTHER_REDUCTION,
        ),
    ],
)
def test_article10_before_at_after_behavior(
    position: str,
    state: str,
    prior_valid: bool,
    expected_decision: str,
    expected_cohort: str,
) -> None:
    decision = _evaluate(
        _case(
            started_position=position,
            boundary_state=state,
            prior_contract_validated=prior_valid,
        )
    )
    assert decision["decision"] == expected_decision
    assert decision["cohort_result"] == expected_cohort
    assert decision["article_10_boundary_commit"] == ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT


def test_gate_failure_has_no_filesystem_side_effect(tmp_path) -> None:
    decision = _evaluate(_case(policy_overrides={"complete": False}))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert list(tmp_path.iterdir()) == []


def test_repeated_evaluation_is_deterministic() -> None:
    case = _case()
    assert _evaluate(case) == _evaluate(_clone_case_inputs(case))


def test_existing_runtime_ledger_preserves_ordered_replay_lineage(tmp_path) -> None:
    ledger = RuntimeLedger(tmp_path)
    runtime_id = "EXISTING-G77-REPLAY"
    seed = ledger.append(runtime_id, "existing_replay_lineage", {"hash": _hash("existing")})
    case = _case()
    decision = _evaluate(case)
    actual = _actual(case, decision)

    recorded = [
        record_reduction_evidence(ledger=ledger, runtime_id=runtime_id, artifact=case["planned_manifest"]),
        record_reduction_evidence(ledger=ledger, runtime_id=runtime_id, artifact=case["authorization"]),
        case["_gate"].record_decision(
            ledger=ledger,
            runtime_id=runtime_id,
            artifact=decision,
            decision_inputs=_decision_inputs(case),
        ),
        record_reduction_evidence(ledger=ledger, runtime_id=runtime_id, artifact=actual),
    ]
    reconstructed = ledger.read(runtime_id)
    assert reconstructed[0] == seed
    assert [entry["sequence"] for entry in reconstructed] == list(range(5))
    assert reconstructed[1:] == recorded
    assert all(entry["entry_hash"].startswith("sha256:") for entry in reconstructed)
    assert len({entry["entry_hash"] for entry in reconstructed}) == len(reconstructed)


def test_topology_isolation_and_no_executor_authority() -> None:
    decision = _evaluate(_case())
    assert decision["authority_paths"] == 1
    assert decision["production_paths"] == 1
    assert decision["parallel_paths"] == 0
    assert decision["human_entry_paths"] == 1
    assert decision["physical_reduction_performed"] is False
    assert decision["semantic_authority_created"] is False


def test_previous_public_caller_composition_bypass_is_closed() -> None:
    case = _case()
    synthetic_root = deepcopy(case["_provenance_root"])
    synthetic_root["provenance_root_identity"] = "CALLER-SYNTHETIC-ROOT"
    synthetic_root["boundary_commit"] = "f" * 40
    synthetic_root["immutable_content_hash"] = (
        authority_provenance_content_hash_v1(synthetic_root)
    )
    binding = TrustedAuthorityProvenanceBindingV1(
        provenance_root_identity=synthetic_root["provenance_root_identity"],
        immutable_content_hash=synthetic_root["immutable_content_hash"],
        boundary_commit="f" * 40,
        current_revision=1,
        current=True,
    )
    caller_resolver = TrustedAuthorityProvenanceResolverV1(
        boundary_commit="f" * 40,
        roots=(synthetic_root,),
        bindings=(binding,),
    )
    with pytest.raises(
        FailClosedRuntimeError, match="rejects caller-selected trust sources"
    ):
        BoundedEvidenceReductionGateV1(caller_resolver)

    caller_gate = BoundedEvidenceReductionGateV1()
    decision = caller_gate.evaluate(**_decision_inputs(case))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )
    assert decision["physical_reduction_performed"] is False
    assert decision["semantic_authority_created"] is False


def test_che_owner_path_projects_and_persists_only_exact_profile_a_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert (
        che_service._canonical_che_authority_kind_for_owner_reply_v1(
            BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION
        )
        == AUTHORIZATION
    )
    case = _case()
    evidence = case["_provenance_root"]["owner_issued_authority_evidence"]
    request = CanonicalHumanEntryRequestEnvelopeV1.from_dict(
        evidence["che_request"]
    )
    continuation = CanonicalContinuationEnvelopeV1.from_dict(
        evidence["che_continuation"]
    )
    authority_act = CanonicalHumanAuthorityActV1.from_dict(
        evidence["human_authority_act"]
    )
    correlation = evidence["che_evidence_correlation"]
    observed: list[dict] = []
    monkeypatch.setattr(
        che_service,
        "_persist_profile_a_owner_state_authorization_v1",
        lambda **kwargs: observed.append(kwargs),
    )
    che_service._persist_profile_a_owner_state_authorization_if_applicable_v1(
        request=request,
        continuation=continuation,
        authority_act=authority_act,
        correlation=correlation,
    )
    assert len(observed) == 1

    unrelated_payload = dict(authority_act.to_dict()["payload"])
    unrelated_payload["command"] = "AUTHORIZE_DIFFERENT_ACTION"
    unrelated_act = replace(
        authority_act,
        payload=unrelated_payload,
        payload_digest=canonical_human_authority_payload_digest_v1(
            unrelated_payload
        ),
    )
    che_service._persist_profile_a_owner_state_authorization_if_applicable_v1(
        request=request,
        continuation=continuation,
        authority_act=unrelated_act,
        correlation=correlation,
    )
    assert len(observed) == 1


@pytest.mark.parametrize(
    "injection",
    [
        {"authority_provenance_resolver": object()},
        {"runtime_scope_identity": "/caller/store"},
        {"owner_state_source": object()},
        {"service": object()},
        {"registry": object()},
    ],
)
def test_constructor_and_owner_state_source_injection_denies(
    injection: dict,
) -> None:
    with pytest.raises(
        FailClosedRuntimeError, match="rejects caller-selected trust sources"
    ):
        BoundedEvidenceReductionGateV1(**injection)


def test_future_owner_state_authority_denies() -> None:
    decision = _evaluate(_case(authority_created_at="2999-01-01T00:00:00Z"))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_expired_owner_state_authority_denies() -> None:
    decision = _evaluate(
        _case(
            authority_created_at="1999-01-01T00:00:00Z",
            profile_a_expires_at="2000-01-01T00:00:00Z",
        )
    )
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_superseded_owner_state_authority_denies() -> None:
    case = _case()
    _append_profile_a_successor(case)
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_revoked_owner_state_authority_denies() -> None:
    case = _case()
    path, event = _append_profile_a_successor(case)
    event["event_kind"] = PROFILE_A_OWNER_STATE_REVOKED
    _write_profile_a_event(path, event)
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_owner_state_rollback_and_unresolved_latest_state_deny() -> None:
    case = _case()
    latest_path, _ = _append_profile_a_successor(case)
    latest_path.unlink()
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


@pytest.mark.parametrize("attack", ["fork", "alias", "reorder"])
def test_owner_state_fork_alias_and_reorder_deny(attack: str) -> None:
    case = _case()
    event_path = case["_profile_a_event_path"]
    event_bytes = event_path.read_bytes()
    if attack == "fork":
        target = event_path.parent / "fork-event-0001.json"
    elif attack == "alias":
        target = event_path.parent / "event-alias.json"
    else:
        target = event_path.parent / "event-99999999999999999999.json"
    target.write_bytes(event_bytes)
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


@pytest.mark.parametrize(
    "attack", ["payload_challenge", "immutable_content", "reconstruction"]
)
def test_rehash_and_reconstruction_of_owner_state_provenance_deny(
    attack: str,
) -> None:
    case = _case()
    path = case["_profile_a_event_path"]
    event = json.loads(path.read_text(encoding="utf-8"))
    if attack == "payload_challenge":
        event["payload_challenge"] = _hash("caller-challenge")
    elif attack == "immutable_content":
        event["provenance_root"]["immutable_content_hash"] = _hash(
            "caller-content"
        )
    else:
        event["provenance_root"]["subject_identity"] = "CALLER-SUBJECT"
        root = event["provenance_root"]
        act = root["owner_issued_authority_evidence"]["human_authority_act"]
        root["provenance_root_identity"] = _profile_a_root_identity_v1(
            authorization_owner_identity=root["authorization_owner_identity"],
            authorization_act_class=root["authorization_act_class"],
            action_kind=root["action_kind"],
            subject_identity=root["subject_identity"],
            scope=root["scope"],
            act_revision=root["act_revision"],
            payload_challenge=act["payload_digest"],
            request_evidence_correlation_identity=(
                root["request_evidence_correlation_identity"]
            ),
            request_evidence_correlation_hash=(
                root["request_evidence_correlation_hash"]
            ),
            owner_issued_authority_evidence=(
                root["owner_issued_authority_evidence"]
            ),
        )
        event["provenance_root"]["immutable_content_hash"] = (
            authority_provenance_content_hash_v1(event["provenance_root"])
        )
    _write_profile_a_event(path, event)
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_caller_minted_self_asserted_authority_cannot_allow() -> None:
    case = _case()
    case["authority_evidence"] = deepcopy(
        case["_provenance_root"]["owner_issued_authority_evidence"]
    )
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "CALLER_AUTHORITY_EVIDENCE_FORBIDDEN" in decision["failure_codes"]


def test_caller_human_actor_class_assertion_has_no_authorization_effect() -> None:
    case = _case()
    caller_bundle = deepcopy(
        case["_provenance_root"]["owner_issued_authority_evidence"]
    )
    assert caller_bundle["che_request"]["actor_class"] == HUMAN_ACTOR
    case["authority_evidence"] = caller_bundle
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "CALLER_AUTHORITY_EVIDENCE_FORBIDDEN" in decision["failure_codes"]


def test_internally_coherent_caller_minted_bundle_cannot_allow() -> None:
    case = _case()
    case["authority_evidence"] = deepcopy(
        case["_provenance_root"]["owner_issued_authority_evidence"]
    )
    case["authority_provenance_reference"] = "CALLER-MINTED-ROOT"
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert {
        "CALLER_AUTHORITY_EVIDENCE_FORBIDDEN",
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID",
    }.issubset(decision["failure_codes"])


def test_copied_valid_payload_without_resolvable_root_denies() -> None:
    case = _case(authority_provenance_reference="UNRESOLVED-COPIED-ROOT")
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_provenance_root_identity_substitution_denies() -> None:
    decision = _evaluate(
        _case(authority_provenance_reference="SUBSTITUTED-PROVENANCE-ROOT")
    )
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_caller_modified_authority_content_and_recomputed_hash_denies() -> None:
    case = _case()
    caller_bundle = deepcopy(
        case["_provenance_root"]["owner_issued_authority_evidence"]
    )
    caller_bundle["human_authority_act"]["actor_identity"] = "CALLER-ACTOR"
    caller_bundle["human_authority_act"]["payload_digest"] = replay_hash(
        {"payload": caller_bundle["human_authority_act"]["payload"]}
    )
    case["authority_evidence"] = caller_bundle
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "CALLER_AUTHORITY_EVIDENCE_FORBIDDEN" in decision["failure_codes"]


@pytest.mark.parametrize(
    ("root_overrides", "label"),
    [
        (
            {"authorization_owner_identity": "CALLER-ASSERTED-HUMAN"},
            "owner",
        ),
        ({"authorization_act_class": "CALLER-ACT-CLASS"}, "act class"),
        ({"action_kind": "UNAUTHORIZED-HIGH-IMPACT-ACTION"}, "action kind"),
        ({"subject_identity": "OTHER-POLICY"}, "subject"),
    ],
)
def test_profile_b_root_semantic_mismatch_denies(
    root_overrides: dict, label: str
) -> None:
    decision = _evaluate(_case(provenance_root_overrides=root_overrides))
    assert label
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_profile_b_scope_mismatch_denies() -> None:
    mismatched_scope = {
        "domain_id": "OTHER-DOMAIN",
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "applicable_at_commit": OBSERVED_COMMIT,
        "allowed_evidence_classes": [EVIDENCE_CLASS],
        "allowed_reduction_types": [REDUCTION_TYPE],
        "obligations_hash": _hash("untrusted-obligations"),
        "permanent_trail_hash": _hash("untrusted-trail"),
        "cohort_hash": _hash("untrusted-cohort"),
    }
    decision = _evaluate(
        _case(provenance_root_overrides={"scope": mismatched_scope})
    )
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_policy_revision_mismatch_denies() -> None:
    decision = _evaluate(_case(policy_overrides={"policy_version": "V2"}))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
        or "POLICY_REPLAY_HASH_INVALID" in decision["failure_codes"]
    )


@pytest.mark.parametrize(
    "root_overrides",
    [
        {"request_evidence_correlation_identity": "OTHER-CORRELATION"},
        {"request_evidence_correlation_hash": _hash("other-correlation")},
    ],
)
def test_request_evidence_correlation_mismatch_denies(
    root_overrides: dict,
) -> None:
    decision = _evaluate(_case(provenance_root_overrides=root_overrides))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_missing_provenance_reference_denies() -> None:
    case = _case()
    case["authority_provenance_reference"] = None
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_gate_caller_cannot_select_or_replace_resolver() -> None:
    case = _case()
    gate = case["_gate"]
    assert "resolver" not in inspect.signature(gate.evaluate).parameters
    with pytest.raises(
        AttributeError, match="gate composition is immutable"
    ):
        setattr(
            gate,
            "_BoundedEvidenceReductionGateV1__authority_provenance_resolver",
            object(),
        )


def test_trusted_resolver_exposes_no_write_or_registration_surface() -> None:
    case = _case()
    resolver = object.__getattribute__(
        case["_gate"],
        "_BoundedEvidenceReductionGateV1__authority_provenance_resolver",
    )
    assert not any(
        hasattr(resolver, name)
        for name in ("write", "register", "append", "replace", "overwrite")
    )
    with pytest.raises(AttributeError, match="resolver is immutable"):
        setattr(resolver, "owner_state_identity", "CALLER-OWNER-STATE")


def test_unverifiable_or_stale_correlated_authority_cannot_allow() -> None:
    case = _case(
        trusted_binding_overrides={
            "current": False,
            "superseded_by": "G77-PROFILE-B-ROOT-2",
        }
    )
    decision = _evaluate(case)
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert (
        "AUTHORITY_PROVENANCE_UNRESOLVED_OR_INVALID"
        in decision["failure_codes"]
    )


def test_rehashed_denial_changed_to_allow_cannot_be_recorded(tmp_path) -> None:
    case = _case()
    case["policy"] = None
    denied = _evaluate(case)
    assert denied["decision"] == DO_NOT_REDUCE_EVIDENCE
    forged_basis = deepcopy(denied)
    forged_basis.pop("replay_hash")
    forged_basis["decision"] = ALLOW_BOUNDED_EVIDENCE_REDUCTION
    forged_basis["failure_codes"] = []
    forged = with_replay_hash(forged_basis)
    with pytest.raises(FailClosedRuntimeError, match="does not match recomputed"):
        case["_gate"].record_decision(
            ledger=RuntimeLedger(tmp_path),
            runtime_id="FORGED-GATE-DECISION",
            artifact=forged,
            decision_inputs=_decision_inputs(case),
        )


def test_gate_decision_cannot_be_recorded_through_unbound_ledger_helper(
    tmp_path,
) -> None:
    decision = _evaluate(_case())
    with pytest.raises(FailClosedRuntimeError, match="fixed trusted gate"):
        record_reduction_evidence(
            ledger=RuntimeLedger(tmp_path),
            runtime_id="UNBOUND-GATE-DECISION",
            artifact=decision,
        )


@pytest.mark.parametrize("match_kind", ["identity", "hash"])
def test_permanent_trail_in_planned_reduction_scope_cannot_allow(
    match_kind: str,
) -> None:
    decision = _evaluate(_case(permanent_trail_reduction_match=match_kind))
    assert decision["decision"] == DO_NOT_REDUCE_EVIDENCE
    assert "PERMANENT_TRAIL_IN_REDUCTION_SCOPE" in decision["failure_codes"]


@pytest.mark.parametrize("match_kind", ["identity", "hash"])
def test_permanent_trail_in_actual_reduction_scope_fails_closed(
    match_kind: str,
) -> None:
    case = _case()
    decision = _evaluate(case)
    items = [
        {
            "evidence_id": "EVIDENCE-A",
            "prior_hash": _hash("evidence-a"),
            "actual_disposition": "CONDENSE",
            "retained_reference": "trail:PERMANENT-TRAIL-1",
            "retained_hash": case["permanent_trail"]["replay_hash"],
            "integrity_verified": True,
        },
        {
            "evidence_id": "EVIDENCE-B",
            "prior_hash": _hash("evidence-b"),
            "actual_disposition": "RETAIN",
            "retained_reference": "evidence:EVIDENCE-B",
            "retained_hash": _hash("evidence-b"),
            "integrity_verified": True,
        },
    ]
    if match_kind == "identity":
        items[0]["evidence_id"] = case["permanent_trail"]["trail_id"]
    else:
        items[0]["prior_hash"] = case["permanent_trail"]["replay_hash"]
    with pytest.raises(FailClosedRuntimeError, match="cannot reduce the permanent trail"):
        create_actual_reduction_manifest(
            manifest_id="ACTUAL-MANIFEST-TRAIL-ATTACK",
            planned_manifest=case["planned_manifest"],
            authorization=case["authorization"],
            gate_decision=decision,
            execution_evidence_reference="replay:executor",
            execution_evidence_hash=_hash("executor"),
            evidence_items=items,
        )


@pytest.mark.parametrize("match_kind", ["identity", "hash"])
def test_rehashed_actual_manifest_cannot_bypass_permanent_trail_exclusion(
    match_kind: str,
) -> None:
    case = _case()
    actual = _actual(case, _evaluate(case))
    forged_basis = deepcopy(actual)
    forged_basis.pop("replay_hash")
    if match_kind == "identity":
        forged_basis["evidence_items"][0]["evidence_id"] = actual[
            "permanent_trail_id"
        ]
    else:
        forged_basis["evidence_items"][0]["prior_hash"] = actual[
            "permanent_trail_hash"
        ]
    forged = with_replay_hash(forged_basis)
    with pytest.raises(FailClosedRuntimeError, match="cannot reduce the permanent trail"):
        validate_actual_reduction_manifest(forged)
