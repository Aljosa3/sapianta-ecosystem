from sapianta_bridge.governed_execution_exchange.execution_exchange_evidence import execution_exchange_evidence


def test_execution_exchange_evidence_records_pairing():
    evidence = execution_exchange_evidence(
        binding={"result_capture_id": "CAP-1", "response_return_id": "RETURN-1"},
        valid=True,
        states=("EXECUTION_EXCHANGE_CREATED",),
    )
    assert evidence["governed_execution_result_paired"] is True
    assert evidence["continuity_fabricated"] is False
