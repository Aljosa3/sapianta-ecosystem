from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_evidence import runtime_operational_entrypoint_evidence


def test_evidence_records_replay_visible_convergence():
    evidence = runtime_operational_entrypoint_evidence(
        session={"runtime_operational_entrypoint_id": "ENTRY-1"},
        request={"runtime_operational_entrypoint_request_id": "REQ-1"},
        response={"runtime_operational_entrypoint_response_id": "RESP-1"},
        binding={**{field: field for field in LINEAGE_FIELDS}, "runtime_operational_entrypoint_binding_id": "BIND-1"},
        valid=True,
        states=("RUNTIME_OPERATIONAL_ENTRY_FINALIZED",),
    )
    assert evidence["operational_entry_finalized"] is True
    assert evidence["stdin_relay_id"] == "stdin_relay_id"
