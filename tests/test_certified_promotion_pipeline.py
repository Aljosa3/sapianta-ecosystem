from copy import deepcopy

from sapianta_system.runtime.promotion.certified_promotion_pipeline import (
    certify_governed_promotion,
    create_certified_promotion_pipeline,
)
from sapianta_system.runtime.promotion.governed_promotion_certification import create_promotion_certification
from sapianta_system.runtime.promotion.governed_promotion_closure import close_certified_promotion_pipeline
from sapianta_system.runtime.promotion.governed_promotion_replay import validate_promotion_replay
from sapianta_system.runtime.promotion.governed_promotion_validator import validate_promotion_pipeline
from sapianta_system.runtime.recovery import create_recovery_chain, recover_governed_operation
from sapianta_system.runtime.session import append_governed_exchange, create_governed_execution_session
from sapianta_system.runtime.synchronization import create_synchronization_chain, synchronize_governed_state


def _session_lineage():
    return {
        "governed_session_id": "GOV-1",
        "runtime_operational_entrypoint_id": "ENTRY-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_operation_envelope_id": "ENV-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _sync_lineage(session):
    return {
        "governed_execution_session_id": session["governed_execution_session_id"],
        "governed_session_id": "GOV-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _recovery_lineage(session, sync_chain):
    return {
        "governed_execution_session_id": session["governed_execution_session_id"],
        "governed_synchronization_chain_id": sync_chain["governed_synchronization_chain_id"],
        "governed_session_id": "GOV-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _promotion_lineage(session, sync_chain, recovery_chain):
    return {
        "governed_execution_session_id": session["governed_execution_session_id"],
        "governed_synchronization_chain_id": sync_chain["governed_synchronization_chain_id"],
        "governed_recovery_chain_id": recovery_chain["governed_recovery_chain_id"],
        "governed_session_id": "GOV-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _connector():
    return {
        "connector_status": "COMPLETED",
        "registration": {"connector_id": "CONNECTOR-1"},
        "result": {"connector_result_id": "RESULT-1", "replay_identity": "REPLAY-1"},
        "evidence": {"replay_safe": True, "lineage_preserved": True},
    }


def _operational_state():
    session = create_governed_execution_session(session_seed={"conversation_id": "C-1"}, lineage=_session_lineage())
    session = append_governed_exchange(session=session, connector_output=_connector())["session"]
    exchange = session["exchanges"][-1]
    sync_chain = create_synchronization_chain(session=session, lineage=_sync_lineage(session))
    sync_chain = synchronize_governed_state(
        chain=sync_chain,
        session=session,
        synchronized_payload={
            "last_exchange_id": exchange["governed_session_exchange_id"],
            "last_exchange_hash": exchange["exchange_hash"],
            "last_connector_result_id": exchange["connector_result_id"],
            "last_result_status": "RETURNED",
        },
    )["chain"]
    recovery_chain = create_recovery_chain(session=session, synchronization_chain=sync_chain, lineage=_recovery_lineage(session, sync_chain))
    recovery_chain = recover_governed_operation(
        chain=recovery_chain,
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload={
            "interruption_code": "BOUNDED_OPERATION_INTERRUPTED",
            "continuation_intent": "continue from explicit governed interruption",
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
            "autonomous_continuation_present": False,
            "hidden_continuation_present": False,
        },
        authorization={
            "recovery_authorization_id": "REC-AUTH-1",
            "authorization_source": "human_governance_review",
            "approved_by": "human",
            "recovery_authorized": True,
        },
    )["chain"]
    return session, sync_chain, recovery_chain


def _authorization():
    return {
        "promotion_authorization_id": "PROMO-AUTH-1",
        "authorization_source": "human_governance_review",
        "approved_by": "human",
        "promotion_authorized": True,
    }


def _payload():
    return {
        "certification_intent": "certify bounded operational state eligibility",
        "certification_basis": "validated continuity, synchronization, and recovery lineage",
        "deployment_present": False,
        "rollout_present": False,
        "orchestration_present": False,
        "autonomous_rollout_present": False,
        "hidden_approval_present": False,
    }


def test_promotion_identity_is_deterministic():
    session, sync_chain, recovery_chain = _operational_state()
    assert create_certified_promotion_pipeline(
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        lineage=_promotion_lineage(session, sync_chain, recovery_chain),
    ) == create_certified_promotion_pipeline(
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        lineage=_promotion_lineage(session, sync_chain, recovery_chain),
    )


def test_explicit_authorized_promotion_is_replay_linked():
    session, sync_chain, recovery_chain = _operational_state()
    pipeline = create_certified_promotion_pipeline(
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        lineage=_promotion_lineage(session, sync_chain, recovery_chain),
    )
    first = certify_governed_promotion(
        pipeline=pipeline,
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload=_payload(),
        authorization=_authorization(),
    )["pipeline"]
    second = certify_governed_promotion(
        pipeline=first,
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload=_payload(),
        authorization={**_authorization(), "promotion_authorization_id": "PROMO-AUTH-2"},
    )["pipeline"]
    assert second["promotion_count"] == 2
    assert second["promotions"][1]["previous_promotion_hash"] == second["promotions"][0]["promotion_hash"]
    assert validate_promotion_pipeline(second)["valid"] is True


def test_promotion_certification_identity_is_deterministic():
    session, sync_chain, recovery_chain = _operational_state()
    pipeline = certify_governed_promotion(
        pipeline=create_certified_promotion_pipeline(
            session=session,
            synchronization_chain=sync_chain,
            recovery_chain=recovery_chain,
            lineage=_promotion_lineage(session, sync_chain, recovery_chain),
        ),
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload=_payload(),
        authorization=_authorization(),
    )["pipeline"]
    assert create_promotion_certification(pipeline=pipeline) == create_promotion_certification(pipeline=pipeline)
    assert create_promotion_certification(pipeline=pipeline)["deployment_authorized"] is False


def test_unauthorized_promotion_fails_closed():
    session, sync_chain, recovery_chain = _operational_state()
    pipeline = create_certified_promotion_pipeline(
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        lineage=_promotion_lineage(session, sync_chain, recovery_chain),
    )
    assert certify_governed_promotion(
        pipeline=pipeline,
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload=_payload(),
        authorization={**_authorization(), "approved_by": "runtime"},
    )["states"] == ["BLOCKED"]


def test_deployment_semantics_disguised_as_certification_fail_closed():
    session, sync_chain, recovery_chain = _operational_state()
    pipeline = create_certified_promotion_pipeline(
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        lineage=_promotion_lineage(session, sync_chain, recovery_chain),
    )
    assert certify_governed_promotion(
        pipeline=pipeline,
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload={**_payload(), "rollout_present": True, "hidden_approval_present": True},
        authorization=_authorization(),
    )["states"] == ["BLOCKED"]


def test_replay_mismatch_fails_closed():
    session, sync_chain, recovery_chain = _operational_state()
    pipeline = certify_governed_promotion(
        pipeline=create_certified_promotion_pipeline(
            session=session,
            synchronization_chain=sync_chain,
            recovery_chain=recovery_chain,
            lineage=_promotion_lineage(session, sync_chain, recovery_chain),
        ),
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload=_payload(),
        authorization=_authorization(),
    )["pipeline"]
    pipeline["promotions"][0]["promotion_hash"] = "MISMATCH"
    assert validate_promotion_replay(pipeline)["valid"] is False


def test_certification_isolation_preserves_prior_pipeline():
    session, sync_chain, recovery_chain = _operational_state()
    original = create_certified_promotion_pipeline(
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        lineage=_promotion_lineage(session, sync_chain, recovery_chain),
    )
    before = deepcopy(original)
    certified = certify_governed_promotion(
        pipeline=original,
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload=_payload(),
        authorization=_authorization(),
    )
    assert original == before
    assert certified["pipeline"]["promotion_count"] == 1


def test_promotion_closure_is_deterministic_and_closed_pipeline_cannot_continue():
    session, sync_chain, recovery_chain = _operational_state()
    pipeline = certify_governed_promotion(
        pipeline=create_certified_promotion_pipeline(
            session=session,
            synchronization_chain=sync_chain,
            recovery_chain=recovery_chain,
            lineage=_promotion_lineage(session, sync_chain, recovery_chain),
        ),
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload=_payload(),
        authorization=_authorization(),
    )["pipeline"]
    first = close_certified_promotion_pipeline(pipeline=pipeline)
    second = close_certified_promotion_pipeline(pipeline=pipeline)
    assert first["validation"]["valid"] is True
    assert first["closure"]["certified_promotion_closure_id"] == second["closure"]["certified_promotion_closure_id"]
    assert certify_governed_promotion(
        pipeline=first["pipeline"],
        session=session,
        synchronization_chain=sync_chain,
        recovery_chain=recovery_chain,
        promotion_payload=_payload(),
        authorization=_authorization(),
    )["states"] == ["BLOCKED"]
