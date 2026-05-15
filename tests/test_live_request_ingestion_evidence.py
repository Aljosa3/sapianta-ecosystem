from sapianta_bridge.governed_live_request_ingestion.live_request_ingestion_evidence import live_request_ingestion_evidence


def test_live_request_ingestion_evidence_records_activation():
    evidence = live_request_ingestion_evidence(binding={"request_activation_id": "ACT-1"}, valid=True, states=("LIVE_REQUEST_INGESTION_CREATED",))
    assert evidence["request_activation_bound"] is True
    assert evidence["continuity_fabricated"] is False
