from sapianta_bridge.governed_execution_exchange import create_execution_exchange
from sapianta_bridge.governed_execution_relay import create_execution_relay
from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.governed_live_request_ingestion import ingest_live_request
from sapianta_bridge.governed_local_runtime_bridge import create_local_runtime_bridge
from sapianta_bridge.governed_runtime_activation_gate import create_runtime_activation_gate
from sapianta_bridge.governed_runtime_delivery_finalization import create_runtime_delivery_finalization
from sapianta_bridge.governed_runtime_execution_commit import create_runtime_execution_commit
from sapianta_bridge.governed_runtime_surface import create_runtime_surface
from sapianta_bridge.governed_direct_runtime_interaction import create_direct_runtime_interaction
from sapianta_bridge.governed_terminal_runtime_attachment import attach_governed_terminal_runtime
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime
from sapianta_bridge.live_governed_interaction_serving_gateway import run_serving_gateway
from sapianta_bridge.live_governed_runtime_serving import attach_runtime_serving_turn, create_runtime_serving_session
from sapianta_bridge.live_governed_session_runtime import attach_session_runtime_turn, create_session_runtime_session
from sapianta_bridge.live_runtime_interaction_attachment import attach_live_runtime_interaction
def _final():
    loop=create_loop_session(conversation_id="C-1",replay_identity="R-1").to_dict()
    turn=run_interaction_loop_turn("Inspect",session=loop,turn_index=1,execution_gate_id="G-1",bounded_runtime_id="RT-1",result_capture_id="CAP-1")
    live=run_live_governed_interaction_runtime(loop_session=loop,loop_output=turn)
    attach=attach_live_runtime_interaction(live_runtime_output=live)
    sr=create_session_runtime_session(interaction_loop_session_id=loop["interaction_session_id"]).to_dict()
    so=attach_session_runtime_turn(session_runtime=sr,attachment_output=attach)
    serving=create_runtime_serving_session(session_runtime=sr).to_dict()
    sv=attach_runtime_serving_turn(serving_session=serving,session_runtime_output=so)
    term=attach_governed_terminal_runtime(runtime_serving_output=sv,stdin_binding_id="STDIN-1",stdout_binding_id="STDOUT-1")
    gw=run_serving_gateway(terminal_output=term,ingress_id="IN-1",egress_id="OUT-1")
    ing=ingest_live_request(gateway_output=gw,request_activation_id="ACT-1")
    ex=create_execution_exchange(ingestion_output=ing); relay=create_execution_relay(exchange_output=ex,terminal_output=term)
    bridge=create_local_runtime_bridge(relay_output=relay,runtime_transport_bridge_id="RTB-1")
    activation=create_runtime_activation_gate(bridge_output=bridge,activation_authorized=True,approved_by="human")
    commit=create_runtime_execution_commit(activation_output=activation)
    return create_runtime_delivery_finalization(commit_output=commit)
def _surface():
    return create_runtime_surface(finalization_output=_final(),surface_ingress_id="IN",surface_egress_id="OUT")
def test_controller_returns():
    r=create_direct_runtime_interaction(surface_output=_surface(),interaction_admission_id="ADM")
    assert r["validation"]["valid"]; assert r["states"][-1]=="DIRECT_RUNTIME_INTERACTION_RETURNED"
def test_controller_blocks_incomplete_surface():
    assert create_direct_runtime_interaction(surface_output={},interaction_admission_id="ADM")["states"]==["BLOCKED"]
def test_controller_blocks_identity_change():
    s=_surface(); first=create_direct_runtime_interaction(surface_output=s,interaction_admission_id="A1"); second=create_direct_runtime_interaction(surface_output=s,interaction_admission_id="A2",prior_output=first)
    assert second["states"]==["BLOCKED"]
