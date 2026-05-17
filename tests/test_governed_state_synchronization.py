from copy import deepcopy

from sapianta_system.runtime.session import append_governed_exchange, create_governed_execution_session
from sapianta_system.runtime.synchronization import (
    close_governed_synchronization_chain,
    create_synchronization_chain,
    synchronize_governed_state,
)
from sapianta_system.runtime.synchronization.governed_synchronization_replay import validate_synchronization_replay
from sapianta_system.runtime.synchronization.governed_synchronization_validator import validate_synchronization_chain


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


def _connector(index):
    return {
        "connector_status": "COMPLETED",
        "registration": {"connector_id": "CONNECTOR-1"},
        "result": {"connector_result_id": f"RESULT-{index}", "replay_identity": f"REPLAY-{index}"},
        "evidence": {"replay_safe": True, "lineage_preserved": True},
    }


def _session_with_exchange(index=1):
    session = create_governed_execution_session(session_seed={"conversation_id": "C-1"}, lineage=_session_lineage())
    return append_governed_exchange(session=session, connector_output=_connector(index))["session"]


def _payload(session):
    exchange = session["exchanges"][-1]
    return {
        "last_exchange_id": exchange["governed_session_exchange_id"],
        "last_exchange_hash": exchange["exchange_hash"],
        "last_connector_result_id": exchange["connector_result_id"],
        "last_result_status": "RETURNED",
    }


def test_synchronization_identity_is_deterministic():
    session = _session_with_exchange()
    assert create_synchronization_chain(session=session, lineage=_sync_lineage(session)) == create_synchronization_chain(session=session, lineage=_sync_lineage(session))


def test_synchronization_chain_is_deterministic_and_replay_linked():
    session = _session_with_exchange(1)
    chain = create_synchronization_chain(session=session, lineage=_sync_lineage(session))
    first = synchronize_governed_state(chain=chain, session=session, synchronized_payload=_payload(session))["chain"]
    session2 = append_governed_exchange(session=session, connector_output=_connector(2))["session"]
    second = synchronize_governed_state(chain=first, session=session2, synchronized_payload=_payload(session2))["chain"]
    assert second["synchronization_count"] == 2
    assert second["synchronizations"][1]["previous_synchronization_hash"] == second["synchronizations"][0]["synchronization_hash"]
    assert validate_synchronization_chain(second)["valid"] is True


def test_explicit_boundary_rejects_unauthorized_fields():
    session = _session_with_exchange()
    chain = create_synchronization_chain(session=session, lineage=_sync_lineage(session))
    payload = {**_payload(session), "hidden_memory": "NOPE"}
    assert synchronize_governed_state(chain=chain, session=session, synchronized_payload=payload)["states"] == ["BLOCKED"]


def test_replay_mismatch_fails_closed():
    session = _session_with_exchange()
    chain = synchronize_governed_state(
        chain=create_synchronization_chain(session=session, lineage=_sync_lineage(session)),
        session=session,
        synchronized_payload=_payload(session),
    )["chain"]
    chain["synchronizations"][0]["synchronization_hash"] = "MISMATCH"
    assert validate_synchronization_replay(chain)["valid"] is False


def test_operational_isolation_preserves_prior_chain():
    session = _session_with_exchange()
    original = create_synchronization_chain(session=session, lineage=_sync_lineage(session))
    before = deepcopy(original)
    appended = synchronize_governed_state(chain=original, session=session, synchronized_payload=_payload(session))
    assert original == before
    assert appended["chain"]["synchronization_count"] == 1


def test_hidden_drift_payload_fails_closed():
    session = _session_with_exchange()
    chain = create_synchronization_chain(session=session, lineage=_sync_lineage(session))
    payload = {**_payload(session), "last_exchange_hash": "MISMATCH"}
    assert synchronize_governed_state(chain=chain, session=session, synchronized_payload=payload)["states"] == ["BLOCKED"]


def test_synchronization_closure_is_deterministic():
    session = _session_with_exchange()
    chain = synchronize_governed_state(
        chain=create_synchronization_chain(session=session, lineage=_sync_lineage(session)),
        session=session,
        synchronized_payload=_payload(session),
    )["chain"]
    first = close_governed_synchronization_chain(chain=chain)
    second = close_governed_synchronization_chain(chain=chain)
    assert first["validation"]["valid"] is True
    assert first["closure"]["governed_synchronization_closure_id"] == second["closure"]["governed_synchronization_closure_id"]


def test_closed_chain_cannot_continue():
    session = _session_with_exchange()
    chain = synchronize_governed_state(
        chain=create_synchronization_chain(session=session, lineage=_sync_lineage(session)),
        session=session,
        synchronized_payload=_payload(session),
    )["chain"]
    closed = close_governed_synchronization_chain(chain=chain)["chain"]
    assert synchronize_governed_state(chain=closed, session=session, synchronized_payload=_payload(session))["states"] == ["BLOCKED"]
