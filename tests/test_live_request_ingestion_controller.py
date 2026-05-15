from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.governed_live_request_ingestion import ingest_live_request
from sapianta_bridge.governed_terminal_runtime_attachment import attach_governed_terminal_runtime
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime
from sapianta_bridge.live_governed_interaction_serving_gateway import run_serving_gateway
from sapianta_bridge.live_governed_runtime_serving import attach_runtime_serving_turn, create_runtime_serving_session
from sapianta_bridge.live_governed_session_runtime import attach_session_runtime_turn, create_session_runtime_session
from sapianta_bridge.live_runtime_interaction_attachment import attach_live_runtime_interaction


def _gateway_output():
    loop = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    turn = run_interaction_loop_turn("Inspect governance evidence", session=loop, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    live = run_live_governed_interaction_runtime(loop_session=loop, loop_output=turn)
    attachment = attach_live_runtime_interaction(live_runtime_output=live)
    session_runtime = create_session_runtime_session(interaction_loop_session_id=loop["interaction_session_id"]).to_dict()
    session_output = attach_session_runtime_turn(session_runtime=session_runtime, attachment_output=attachment)
    serving = create_runtime_serving_session(session_runtime=session_runtime).to_dict()
    serving_output = attach_runtime_serving_turn(serving_session=serving, session_runtime_output=session_output)
    terminal = attach_governed_terminal_runtime(runtime_serving_output=serving_output, stdin_binding_id="STDIN-1", stdout_binding_id="STDOUT-1")
    return run_serving_gateway(terminal_output=terminal, ingress_id="IN-1", egress_id="OUT-1")


def test_live_request_ingestion_accepts_valid_gateway():
    result = ingest_live_request(gateway_output=_gateway_output(), request_activation_id="ACT-1")
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "LIVE_RESPONSE_CONTINUITY_READY"


def test_live_request_ingestion_blocks_incomplete_gateway():
    result = ingest_live_request(gateway_output={}, request_activation_id="ACT-1")
    assert result["states"] == ["BLOCKED"]


def test_live_request_ingestion_blocks_identity_change():
    first = ingest_live_request(gateway_output=_gateway_output(), request_activation_id="ACT-1")
    second = ingest_live_request(gateway_output=_gateway_output(), request_activation_id="ACT-2", prior_output=first)
    assert second["validation"]["valid"] is False
    assert second["states"] == ["BLOCKED"]
