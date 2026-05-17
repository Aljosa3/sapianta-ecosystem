from copy import deepcopy

from sapianta_system.runtime.session import (
    append_governed_exchange,
    close_governed_execution_session,
    create_governed_execution_session,
)
from sapianta_system.runtime.session.governed_session_replay import validate_session_replay
from sapianta_system.runtime.session.governed_session_validator import validate_governed_execution_session


def _lineage():
    return {
        "governed_session_id": "GOV-1",
        "runtime_operational_entrypoint_id": "ENTRY-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_operation_envelope_id": "ENV-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _session():
    return create_governed_execution_session(session_seed={"conversation_id": "C-1"}, lineage=_lineage())


def _connector(index):
    return {
        "connector_status": "COMPLETED",
        "registration": {"connector_id": "CONNECTOR-1"},
        "result": {
            "connector_result_id": f"RESULT-{index}",
            "replay_identity": f"REPLAY-{index}",
        },
        "evidence": {"replay_safe": True, "lineage_preserved": True},
    }


def _multi_exchange_session():
    first = append_governed_exchange(session=_session(), connector_output=_connector(1))["session"]
    second = append_governed_exchange(session=first, connector_output=_connector(2))["session"]
    return append_governed_exchange(session=second, connector_output=_connector(3))["session"]


def test_session_identity_is_deterministic():
    assert _session()["governed_execution_session_id"] == _session()["governed_execution_session_id"]


def test_multi_exchange_chain_is_deterministic_and_replay_linked():
    session = _multi_exchange_session()
    assert session["exchange_count"] == 3
    assert validate_governed_execution_session(session)["valid"] is True
    assert session["exchanges"][1]["previous_exchange_hash"] == session["exchanges"][0]["exchange_hash"]
    assert session["exchanges"][2]["previous_exchange_hash"] == session["exchanges"][1]["exchange_hash"]


def test_session_closure_is_deterministic():
    first = close_governed_execution_session(session=_multi_exchange_session())
    second = close_governed_execution_session(session=_multi_exchange_session())
    assert first["validation"]["valid"] is True
    assert first["closure"]["governed_session_closure_id"] == second["closure"]["governed_session_closure_id"]
    assert first["session"]["closed"] is True


def test_continuity_break_fails_closed():
    session = _multi_exchange_session()
    session["exchanges"][1]["previous_exchange_hash"] = "MISMATCH"
    assert validate_governed_execution_session(session)["valid"] is False


def test_replay_mismatch_fails_closed():
    session = _multi_exchange_session()
    session["exchanges"][2]["exchange_hash"] = "MISMATCH"
    assert validate_session_replay(session)["valid"] is False


def test_invalid_ordering_fails_closed():
    session = _multi_exchange_session()
    session["exchanges"][1]["exchange_index"] = 9
    assert validate_governed_execution_session(session)["valid"] is False


def test_closed_session_cannot_continue():
    closed = close_governed_execution_session(session=_multi_exchange_session())["session"]
    assert append_governed_exchange(session=closed, connector_output=_connector(4))["states"] == ["BLOCKED"]


def test_append_does_not_mutate_prior_session():
    original = _session()
    before = deepcopy(original)
    appended = append_governed_exchange(session=original, connector_output=_connector(1))
    assert original == before
    assert appended["session"]["exchange_count"] == 1
