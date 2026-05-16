from sapianta_bridge.governed_runtime_delivery_finalization.runtime_delivery_finalization_evidence import runtime_delivery_finalization_evidence


def test_runtime_delivery_finalization_evidence_records_closure():
    evidence = runtime_delivery_finalization_evidence(
        binding={
            "activation_authorized": True,
            "approved_by": "human",
            "result_capture_id": "CAP-1",
            "response_return_id": "RETURN-1",
        },
        valid=True,
        states=("RUNTIME_DELIVERY_FINALIZATION_CREATED",),
    )
    assert evidence["delivery_finalized"] is True
    assert evidence["operational_lifecycle_closed"] is True
