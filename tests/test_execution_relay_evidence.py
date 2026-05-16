from sapianta_bridge.governed_execution_relay.execution_relay_evidence import execution_relay_evidence


def test_execution_relay_evidence_records_stdio_pair():
    evidence = execution_relay_evidence(
        binding={"stdin_relay_id": "STDIN-1", "stdout_relay_id": "STDOUT-1"},
        valid=True,
        states=("EXECUTION_RELAY_CREATED",),
    )
    assert evidence["stdin_stdout_relay_paired"] is True
    assert evidence["continuity_fabricated"] is False
