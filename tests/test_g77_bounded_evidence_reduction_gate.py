from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.evidence_reduction_gate import (
    AFTER_BOUNDARY,
    ALLOW_BOUNDED_EVIDENCE_REDUCTION,
    ARTICLE_10_EFFECTIVE_BOUNDARY_COMMIT,
    AT_BOUNDARY,
    AUTHORIZED_OR_PLANNED_INCOMPLETE,
    BEFORE_BOUNDARY,
    CLOSED,
    DO_NOT_REDUCE_EVIDENCE,
    EFFECTIVE_GATE_REQUIRED,
    FULL_EVIDENCE_PRESENT,
    NO_STRICTER_RETENTION_REQUIRED,
    PARTIAL_OR_AMBIGUOUS,
    PRIOR_VALID_OUTCOME_PRESERVED,
    PRIOR_VALID_REDUCTION_COMPLETE,
    REVALIDATION_UNDER_EFFECTIVE_GATE_REQUIRED,
    STOP_FURTHER_REDUCTION,
    calculate_gate_basis_hash,
    create_actual_reduction_manifest,
    create_article10_cohort_projection,
    create_domain_reduction_policy_projection,
    create_obligation_projection,
    create_permanent_trail_projection,
    create_planned_reduction_manifest,
    create_reduction_authorization,
    evaluate_evidence_reduction_gate,
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
) -> dict:
    cohort = create_article10_cohort_projection(
        evidence_id="EVIDENCE-SET-1",
        observed_commit=OBSERVED_COMMIT,
        started_position=started_position,
        boundary_state=boundary_state,
        prior_contract_validated=prior_contract_validated,
    )
    policy_arguments = {
        "domain_id": DOMAIN,
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "authority_id": AUTHORITY_ID,
        "authority_evidence_reference": "governance:authority-alpha",
        "authority_evidence_hash": _hash("authority-alpha"),
        "currentness_evidence_reference": "governance:policy-currentness",
        "currentness_evidence_hash": _hash("policy-currentness"),
        "applicable_at_commit": OBSERVED_COMMIT,
        "allowed_evidence_classes": [EVIDENCE_CLASS],
        "allowed_reduction_types": [REDUCTION_TYPE],
    }
    policy_arguments.update(policy_overrides or {})
    policy = create_domain_reduction_policy_projection(**policy_arguments)

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

    planned = create_planned_reduction_manifest(
        manifest_id="PLANNED-MANIFEST-1",
        domain_id=DOMAIN,
        evidence_class=EVIDENCE_CLASS,
        reduction_type=REDUCTION_TYPE,
        evidence_items=[
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
        ],
        policy_hash=policy["replay_hash"],
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
        "authority_evidence_reference": "governance:authority-alpha",
        "authority_evidence_hash": _hash("authority-alpha"),
        "evidence_class": EVIDENCE_CLASS,
        "reduction_type": REDUCTION_TYPE,
        "authorized_evidence_ids": ["EVIDENCE-A"],
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
    }


def _evaluate(case: dict) -> dict:
    return evaluate_evidence_reduction_gate(**case)


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
    tampered_case = deepcopy(case)
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
    assert _evaluate(case) == _evaluate(deepcopy(case))


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
        record_reduction_evidence(ledger=ledger, runtime_id=runtime_id, artifact=decision),
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
