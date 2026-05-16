"""Operational admission semantics."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_entry_admission(*, contract: dict, admitted: bool, approved_by: str) -> dict:
    value = {
        "operational_entry_contract_id": contract["operational_entry_contract_id"],
        "admitted": admitted,
        "approved_by": approved_by,
    }
    return {
        "operational_entry_admission_id": f"OPERATIONAL-ENTRY-ADMISSION-{stable_hash(value)[:24]}",
        **value,
    }
