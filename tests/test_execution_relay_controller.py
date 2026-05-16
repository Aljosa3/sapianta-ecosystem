from sapianta_bridge.governed_execution_exchange import create_execution_exchange
from sapianta_bridge.governed_execution_relay import create_execution_relay
from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.governed_live_request_ingestion import ingest_live_request
from sapianta_bridge.governed_terminal_runtime_attachment import attach_governed_terminal_runtime
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime
from sapianta_bridge.live_governed_interaction_serving_gateway import run_serving_gateway
from sapianta_bridge.live_governed_runtime_serving import attach_runtime_serving_turn, create_runtime_serving_session
from sapianta_bridge.live_governed_session_runtime import attach_session_runtime_turn, create_session_runtime_session
from sapianta_bridge.live_runtime_interaction_attachment import attach_live_runtime_interaction


def _exchange_and_terminal():
    loop = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    turn = run_interaction_loop_turn("Inspect governance evidence", session=loop, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    live = run_live_governed_interaction_runtime(loop_session=loop, loop_output=turn)
    attachment = attach_live_runtime_interaction(live_runtime_output=live)
    session_runtime = create_session_runtime_session(interaction_loop_session_id=loop["interaction_session_id"]).to_dict()
    session_output = attach_session_runtime_turn(session_runtime=session_runtime, attachment_output=attachment)
    serving = create_runtime_serving_session(session_runtime=session_runtime).to_dict()
    serving_output = attach_runtime_serving_turn(serving_session=serving, session_runtime_output=session_output)
    terminal = attach_governed_terminal_runtime(runtime_serving_output=serving_output, stdin_binding_id="STDIN-1", stdout_binding_id="STDOUT-1")
    gateway = run_serving_gateway(terminal_output=terminal, ingress_id="IN-1", egress_id="OUT-1")
    ingestion = ingest_live_request(gateway_output=gateway, request_activation_id="ACT-1")
    return create_execution_exchange(ingestion_output=ingestion), terminal


def test_execution_relay_emits_response():
    exchange, terminal = _exchange_and_terminal()
    result = create_execution_relay(exchange_output=exchange, terminal_output=terminal)
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "EXECUTION_RELAY_RESPONSE_EMITTED"


def test_execution_relay_blocks_incomplete_linkage():
    result = create_execution_relay(exchange_output={}, terminal_output={})
    assert result["states"] == ["BLOCKED"]


def test_execution_relay_blocks_identity_change():
    exchange, terminal = _exchange_and_terminal()
    first = create_execution_relay(exchange_output=exchange, terminal_output=terminal)
    changed_terminal = dict(terminal)
    changed_terminal["terminal_attachment_binding"] = dict(terminal["terminal_attachment_binding"])
    changed_terminal["terminal_attachment_binding"]["stdin_binding_id"] = "STDIN-CHANGED"
    second = create_execution_relay(exchange_output=exchange, terminal_output=changed_terminal, prior_output=first)
    assert second["validation"]["valid"] is False
    assert second["states"] == ["BLOCKED"]
