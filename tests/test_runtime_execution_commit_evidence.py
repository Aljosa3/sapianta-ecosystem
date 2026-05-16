from sapianta_bridge.governed_runtime_execution_commit.runtime_execution_commit_evidence import runtime_execution_commit_evidence


def test_runtime_execution_commit_evidence_records_lifecycle_claims():
    evidence = runtime_execution_commit_evidence(
        binding={
            "activation_authorized": True,
            "approved_by": "human",
            "bounded_runtime_id": "RT-1",
            "result_capture_id": "CAP-1",
            "response_return_id": "RETURN-1",
        },
        valid=True,
        states=("RUNTIME_EXECUTION_COMMIT_CREATED",),
    )
    assert evidence["activation_authorized"] is True
    assert evidence["bounded_runtime_committed"] is True
    assert evidence["result_captured"] is True
    assert evidence["response_returned"] is True
