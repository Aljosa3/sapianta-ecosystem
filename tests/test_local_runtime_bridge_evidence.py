from sapianta_bridge.governed_local_runtime_bridge.local_runtime_bridge_evidence import local_runtime_bridge_evidence


def test_local_runtime_bridge_evidence_records_transport_link():
    evidence = local_runtime_bridge_evidence(binding={"runtime_transport_bridge_id": "RTB-1"}, valid=True, states=("LOCAL_RUNTIME_BRIDGE_CREATED",))
    assert evidence["runtime_transport_linked"] is True
    assert evidence["continuity_fabricated"] is False
