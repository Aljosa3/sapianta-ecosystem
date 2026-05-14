from sapianta_bridge.real_e2e_codex_loop.e2e_loop_binding import (
    RealE2ELoopBinding,
    validate_e2e_loop_binding,
)


def test_real_e2e_loop_binding_is_replay_safe():
    binding = RealE2ELoopBinding(
        loop_id="LOOP-1",
        ingress_request_id="INGRESS-1",
        semantic_request_id="SEM-1",
        envelope_id="ENV-1",
        connector_id="CONN-1",
        execution_gate_id="GATE-1",
        invocation_id="INV-1",
        result_return_id="RESULT-1",
        provider_id="codex_cli",
        replay_identity="REPLAY-1",
    ).to_dict()

    assert binding["immutable"] is True
    assert validate_e2e_loop_binding(binding)["valid"] is True


def test_real_e2e_loop_binding_rejects_result_identity_mutation():
    binding = RealE2ELoopBinding(
        loop_id="LOOP-1",
        ingress_request_id="INGRESS-1",
        semantic_request_id="SEM-1",
        envelope_id="ENV-1",
        connector_id="CONN-1",
        execution_gate_id="GATE-1",
        invocation_id="INV-1",
        result_return_id="RESULT-1",
        provider_id="codex_cli",
        replay_identity="REPLAY-1",
    ).to_dict()
    binding["result_return_id"] = "RESULT-2"

    validation = validate_e2e_loop_binding(binding)

    assert validation["valid"] is False
    assert any(error["field"] == "binding_sha256" for error in validation["errors"])
