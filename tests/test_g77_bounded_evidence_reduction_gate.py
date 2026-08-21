from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.authority_provenance import (
    AUTHORIZATION_OWNER_IDENTITY,
    BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION,
    OWNER_ISSUED_AUTHORIZATION_ACT_CLASS,
    TrustedAuthorityProvenanceBindingV1,
    TrustedAuthorityProvenanceResolverV1,
    create_authority_provenance_root_v1,
)
from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
    NOT_APPLICABLE,
    RECORDED,
    create_canonical_che_evidence_correlation_v1,
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
    authority_provenance_reference: str = PROVENANCE_ROOT_IDENTITY,
    caller_authority_evidence: dict | None = None,
    permanent_trail_reduction_match: str | None = None,
) -> dict:
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
        metadata={"transport_fixture": "focused-g77-remediation"},
    )
    che_request = CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity="G77-FOCUSED-TEST-CHANNEL",
        adapter_identity="G77-FOCUSED-TEST-ADAPTER",
        actor_identity=authority_act.actor_identity,
        actor_class=HUMAN_ACTOR,
        session_identity=authority_act.session_identity,
        workspace_identity="G77-WORKSPACE",
        runtime_scope_identity="G77-RUNTIME-SCOPE",
        request_identity=authority_act.request_identity,
        source_act_identity=authority_act.authority_act_identity,
        order_identity="G77-ORDER-1",
        idempotency_identity="G77-IDEMPOTENCY-1",
        source_payload=authority_act.to_dict(),
        source_encoding="UTF-8",
        source_modality="STRUCTURED",
        declared_capabilities=(CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,),
        metadata={"transport_trace_identity": "G77-TRACE-1"},
        created_at="2026-08-21T00:00:00Z",
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
        runtime_scope_identity="G77-RUNTIME-SCOPE",
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

    provenance_scope = {
        "domain_id": DOMAIN,
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "applicable_at_commit": OBSERVED_COMMIT,
        "allowed_evidence_classes": [EVIDENCE_CLASS],
        "allowed_reduction_types": [REDUCTION_TYPE],
        "obligations_hash": obligations["replay_hash"],
        "permanent_trail_hash": trail["replay_hash"],
        "cohort_hash": cohort["replay_hash"],
    }
    provenance_root_arguments = {
        "provenance_root_identity": PROVENANCE_ROOT_IDENTITY,
        "boundary_commit": TRUSTED_BOUNDARY_COMMIT,
        "authorization_owner_identity": AUTHORIZATION_OWNER_IDENTITY,
        "authorization_act_class": OWNER_ISSUED_AUTHORIZATION_ACT_CLASS,
        "action_kind": BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION,
        "subject_identity": POLICY_ID,
        "scope": provenance_scope,
        "act_revision": 1,
        "request_evidence_correlation_identity": correlation_reference,
        "request_evidence_correlation_hash": correlation_hash,
        "owner_issued_authority_evidence": authority_evidence,
    }
    provenance_root_arguments.update(provenance_root_overrides or {})
    provenance_root = create_authority_provenance_root_v1(
        **provenance_root_arguments
    )
    trusted_binding_arguments = {
        "provenance_root_identity": provenance_root[
            "provenance_root_identity"
        ],
        "immutable_content_hash": provenance_root["immutable_content_hash"],
        "boundary_commit": TRUSTED_BOUNDARY_COMMIT,
        "current_revision": provenance_root["act_revision"],
        "current": True,
        "superseded_by": None,
    }
    trusted_binding_arguments.update(trusted_binding_overrides or {})
    resolver = TrustedAuthorityProvenanceResolverV1(
        boundary_commit=TRUSTED_BOUNDARY_COMMIT,
        roots=(provenance_root,),
        bindings=(
            TrustedAuthorityProvenanceBindingV1(
                **trusted_binding_arguments
            ),
        ),
    )
    gate = BoundedEvidenceReductionGateV1(resolver)

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
    }


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
    assert not any(
        hasattr(TrustedAuthorityProvenanceResolverV1, name)
        for name in ("write", "register", "append", "replace", "overwrite")
    )


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
