from copy import deepcopy

from sapianta_system.runtime.recovery import (
    close_governed_recovery_chain,
    create_recovery_chain,
    recover_governed_operation,
)
from sapianta_system.runtime.recovery.governed_recovery_replay import validate_recovery_replay
from sapianta_system.runtime.recovery.governed_recovery_validator import validate_recovery_chain
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


def _recovery_lineage(session, synchronization_chain):
    return {
        "governed_execution_session_id": session["governed_execution_session_id"],
        "governed_synchronization_chain_id": synchronization_chain["governed_synchronization_chain_id"],
        "governed_session_id": "GOV-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _connector(index=1):
    return {
        "connector_status": "COMPLETED",
        "registration": {"connector_id": "CONNECTOR-1"},
        "result": {"connector_result_id": f"RESULT-{index}", "replay_identity": f"REPLAY-{index}"},
        "evidence": {"replay_safe": True, "lineage_preserved": True},
    }


def _session_and_sync(index=1):
    session = create_governed_execution_session(session_seed={"conversation_id": "C-1"}, lineage=_session_lineage())
    session = append_governed_exchange(session=session, connector_output=_connector(index))["session"]
    exchange = session["exchanges"][-1]
    payload = {
        "last_exchange_id": exchange["governed_session_exchange_id"],
        "last_exchange_hash": exchange["exchange_hash"],
        "last_connector_result_id": exchange["connector_result_id"],
        "last_result_status": "RETURNED",
    }
    synchronization_chain = create_synchronization_chain(session=session, lineage=_sync_lineage(session))
    synchronization_chain = synchronize_governed_state(
        chain=synchronization_chain,
        session=session,
        synchronized_payload=payload,
    )["chain"]
    return session, synchronization_chain


def _authorization():
    return {
        "recovery_authorization_id": "REC-AUTH-1",
        "authorization_source": "human_governance_review",
        "approved_by": "human",
        "recovery_authorized": True,
    }


def _payload():
    return {
        "interruption_code": "BOUNDED_OPERATION_INTERRUPTED",
        "continuation_intent": "continue from explicit governed interruption",
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
        "autonomous_continuation_present": False,
        "hidden_continuation_present": False,
    }


def test_recovery_identity_is_deterministic():
    session, sync_chain = _session_and_sync()
    assert create_recovery_chain(
        session=session,
        synchronization_chain=sync_chain,
        lineage=_recovery_lineage(session, sync_chain),
    ) == create_recovery_chain(
        session=session,
        synchronization_chain=sync_chain,
        lineage=_recovery_lineage(session, sync_chain),
    )


def test_explicit_authorized_recovery_is_replay_linked():
    session, sync_chain = _session_and_sync()
    chain = create_recovery_chain(session=session, synchronization_chain=sync_chain, lineage=_recovery_lineage(session, sync_chain))
    first = recover_governed_operation(
        chain=chain,
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=_payload(),
        authorization=_authorization(),
    )["chain"]
    second = recover_governed_operation(
        chain=first,
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=_payload(),
        authorization={**_authorization(), "recovery_authorization_id": "REC-AUTH-2"},
    )["chain"]
    assert second["recovery_count"] == 2
    assert second["recoveries"][1]["previous_recovery_hash"] == second["recoveries"][0]["recovery_hash"]
    assert validate_recovery_chain(second)["valid"] is True


def test_unauthorized_recovery_fails_closed():
    session, sync_chain = _session_and_sync()
    chain = create_recovery_chain(session=session, synchronization_chain=sync_chain, lineage=_recovery_lineage(session, sync_chain))
    authorization = {**_authorization(), "approved_by": "runtime"}
    assert recover_governed_operation(
        chain=chain,
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=_payload(),
        authorization=authorization,
    )["states"] == ["BLOCKED"]


def test_hidden_continuation_and_retry_semantics_fail_closed():
    session, sync_chain = _session_and_sync()
    chain = create_recovery_chain(session=session, synchronization_chain=sync_chain, lineage=_recovery_lineage(session, sync_chain))
    payload = {**_payload(), "retry_present": True, "hidden_continuation_present": True}
    assert recover_governed_operation(
        chain=chain,
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=payload,
        authorization=_authorization(),
    )["states"] == ["BLOCKED"]


def test_replay_mismatch_fails_closed():
    session, sync_chain = _session_and_sync()
    chain = recover_governed_operation(
        chain=create_recovery_chain(session=session, synchronization_chain=sync_chain, lineage=_recovery_lineage(session, sync_chain)),
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=_payload(),
        authorization=_authorization(),
    )["chain"]
    chain["recoveries"][0]["recovery_hash"] = "MISMATCH"
    assert validate_recovery_replay(chain)["valid"] is False


def test_operational_interruption_isolation_preserves_prior_chain():
    session, sync_chain = _session_and_sync()
    original = create_recovery_chain(session=session, synchronization_chain=sync_chain, lineage=_recovery_lineage(session, sync_chain))
    before = deepcopy(original)
    appended = recover_governed_operation(
        chain=original,
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=_payload(),
        authorization=_authorization(),
    )
    assert original == before
    assert appended["chain"]["recovery_count"] == 1


def test_invalid_recovery_lineage_fails_closed():
    session, sync_chain = _session_and_sync()
    lineage = _recovery_lineage(session, sync_chain)
    lineage["runtime_execution_surface_id"] = ""
    chain = create_recovery_chain(session=session, synchronization_chain=sync_chain, lineage=lineage)
    assert recover_governed_operation(
        chain=chain,
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=_payload(),
        authorization=_authorization(),
    )["states"] == ["BLOCKED"]


def test_recovery_closure_is_deterministic_and_closed_chain_cannot_continue():
    session, sync_chain = _session_and_sync()
    chain = recover_governed_operation(
        chain=create_recovery_chain(session=session, synchronization_chain=sync_chain, lineage=_recovery_lineage(session, sync_chain)),
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=_payload(),
        authorization=_authorization(),
    )["chain"]
    first = close_governed_recovery_chain(chain=chain)
    second = close_governed_recovery_chain(chain=chain)
    assert first["validation"]["valid"] is True
    assert first["closure"]["governed_recovery_closure_id"] == second["closure"]["governed_recovery_closure_id"]
    assert recover_governed_operation(
        chain=first["chain"],
        session=session,
        synchronization_chain=sync_chain,
        recovery_payload=_payload(),
        authorization=_authorization(),
    )["states"] == ["BLOCKED"]
