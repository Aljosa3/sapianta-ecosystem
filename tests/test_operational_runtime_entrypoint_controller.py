from sapianta_bridge.governed_operational_runtime_entrypoint import create_operational_runtime_entrypoint


def _channel_output():
    return {
        "runtime_persistent_channel_binding": {
            "runtime_persistent_channel_id": "CHANNEL-1",
            "runtime_surface_session_id": "SURFACE-1",
            "direct_runtime_interaction_session_id": "INTERACTION-1",
            "execution_exchange_session_id": "EXCHANGE-1",
            "execution_relay_session_id": "RELAY-1",
            "runtime_execution_commit_id": "COMMIT-1",
            "runtime_delivery_finalization_id": "FINALIZATION-1",
            "response_return_id": "RESPONSE-1",
        },
        "validation": {"valid": True},
    }


def test_controller_creates_operational_ready_entrypoint():
    result = create_operational_runtime_entrypoint(
        channel_output=_channel_output(),
        operational_intent="bounded_runtime_entry",
        admitted=True,
        approved_by="human",
    )
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "ENTRYPOINT_OPERATIONAL_READY"
    assert result["evidence"]["operational_activation_authorized"] is True


def test_controller_blocks_incomplete_channel_linkage():
    result = create_operational_runtime_entrypoint(
        channel_output={},
        operational_intent="bounded_runtime_entry",
        admitted=True,
        approved_by="human",
    )
    assert result["states"] == ["BLOCKED"]


def test_closed_entrypoint_cannot_reopen_implicitly():
    closed = create_operational_runtime_entrypoint(
        channel_output=_channel_output(),
        operational_intent="bounded_runtime_entry",
        admitted=True,
        approved_by="human",
        close_requested=True,
    )
    reopened = create_operational_runtime_entrypoint(
        channel_output=_channel_output(),
        operational_intent="bounded_runtime_entry",
        admitted=True,
        approved_by="human",
        prior_output=closed,
    )
    assert closed["states"][-1] == "ENTRYPOINT_CLOSED"
    assert reopened["states"] == ["BLOCKED"]
