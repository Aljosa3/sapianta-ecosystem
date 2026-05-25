"""MOC V1 advisory proposal lifecycle persistence.

This module creates deterministic replay-visible persistence records for
explicit advisory proposal lifecycle transitions. It does not execute proposals,
dispatch workers, activate providers, infer hidden state, mutate governance,
auto-correct proposals, or create autonomous cognition flows.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_PROPOSAL_PERSISTENCE_RECORD"
SCHEMA_VERSION = "1.0"
RECORDED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

PROPOSED = "PROPOSED"
REJECTED = "REJECTED"
CORRECTION_REQUIRED = "CORRECTION_REQUIRED"
CORRECTED = "CORRECTED"
VALIDATED = "VALIDATED"
APPROVAL_PENDING = "APPROVAL_PENDING"
APPROVED = "APPROVED"
PREPARED_FOR_WORKER = "PREPARED_FOR_WORKER"
FAIL_CLOSED = "FAIL_CLOSED"

PROPOSAL_STATES = (
    PROPOSED,
    REJECTED,
    CORRECTION_REQUIRED,
    CORRECTED,
    VALIDATED,
    APPROVAL_PENDING,
    APPROVED,
    PREPARED_FOR_WORKER,
    FAIL_CLOSED,
)

VALID_TRANSITIONS = {
    (PROPOSED, VALIDATED),
    (PROPOSED, REJECTED),
    (REJECTED, CORRECTION_REQUIRED),
    (CORRECTION_REQUIRED, CORRECTED),
    (CORRECTED, VALIDATED),
    (VALIDATED, APPROVAL_PENDING),
    (APPROVAL_PENDING, APPROVED),
    (APPROVED, PREPARED_FOR_WORKER),
}


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(record: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(record)
    safe.pop("persistence_hash", None)
    return safe


def _load_proposal(input_path: str | Path | None) -> tuple[dict[str, Any] | None, list[str]]:
    if input_path is None or not str(input_path).strip():
        return None, ["proposal path missing"]
    path = Path(input_path)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"malformed proposal JSON: {type(exc).__name__}"]
    if not isinstance(loaded, dict):
        return None, ["proposal must be a JSON object"]
    return loaded, []


def _list_ref(proposal: dict[str, Any] | None, field: str) -> list[Any]:
    if not isinstance(proposal, dict):
        return []
    value = proposal.get(field)
    if isinstance(value, list):
        return _canonical_copy(value)
    if isinstance(value, dict):
        return [_canonical_copy(value)]
    return []


def _transition_valid(previous_state: str, proposal_state: str) -> bool:
    return (previous_state, proposal_state) in VALID_TRANSITIONS


def _proposal_hash(proposal: dict[str, Any] | None) -> str:
    if not isinstance(proposal, dict):
        return UNKNOWN
    value = proposal.get("proposal_hash")
    if isinstance(value, str) and value.strip():
        return value
    return canonical_hash(proposal)


def _correction_attempt(proposal: dict[str, Any] | None) -> int:
    if not isinstance(proposal, dict):
        return 0
    value = proposal.get("correction_attempt", 0)
    try:
        parsed = int(value)
    except Exception:
        return 0
    return max(parsed, 0)


def create_proposal_persistence_record(
    proposal: dict[str, Any] | None,
    *,
    proposal_state: str,
    previous_state: str,
    recorded_at: str = RECORDED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(load_errors or [])
    requested_state = str(proposal_state)
    requested_previous = str(previous_state)
    if requested_state not in PROPOSAL_STATES:
        errors.append(f"unknown proposal_state: {requested_state}")
    if requested_previous not in PROPOSAL_STATES:
        errors.append(f"unknown previous_state: {requested_previous}")
    if not isinstance(proposal, dict):
        errors.append("proposal evidence missing")
    transition_valid = not errors and _transition_valid(requested_previous, requested_state)
    effective_state = requested_state if transition_valid else FAIL_CLOSED
    proposal_hash = _proposal_hash(proposal)
    record = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "recorded_at": str(recorded_at),
        "proposal_id": str(proposal.get("proposal_id", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "proposal_hash": proposal_hash,
        "linked_contract_id": str(proposal.get("linked_contract_id", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "linked_contract_hash": str(proposal.get("linked_contract_hash", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "proposal_state": effective_state,
        "previous_state": requested_previous,
        "requested_proposal_state": requested_state,
        "correction_attempt": _correction_attempt(proposal),
        "lineage_refs": _list_ref(proposal, "lineage_refs"),
        "validation_refs": _list_ref(proposal, "validation_refs"),
        "correction_refs": _list_ref(proposal, "correction_refs"),
        "approval_refs": _list_ref(proposal, "approval_refs"),
        "state_transition_valid": transition_valid,
        "transition_violations": [] if transition_valid else sorted(set(errors + [f"invalid transition: {requested_previous} -> {requested_state}"])),
        "replay_safe": True,
        "advisory_only": True,
        "governance_guarantees": {
            "execution_authority": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
            "hidden_continuation": False,
            "proposal_execution": False,
        },
    }
    record["persistence_hash"] = canonical_hash(_hash_input(record))
    return record


def write_proposal_persistence_record(record: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_proposal_persistence(
    *,
    proposal_path: str | Path | None = None,
    proposal_state: str,
    previous_state: str,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    proposal, load_errors = _load_proposal(proposal_path)
    record = create_proposal_persistence_record(
        proposal,
        proposal_state=proposal_state,
        previous_state=previous_state,
        load_errors=load_errors,
    )
    result = {
        "command": "aigol moc persist-proposal",
        "proposal_path": str(proposal_path or ""),
        "proposal_persistence_record": record,
        "read_only": True,
        "execution_authority_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "proposal_repair_added": False,
        "hidden_continuation_added": False,
    }
    if output_path:
        result["output"] = write_proposal_persistence_record(record, output_path)
    return result


def render_proposal_persistence_summary(record: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Proposal Persistence",
            f"  proposal_id: {record.get('proposal_id')}",
            f"  proposal_state: {record.get('proposal_state')}",
            f"  previous_state: {record.get('previous_state')}",
            f"  requested_proposal_state: {record.get('requested_proposal_state')}",
            "Transition",
            f"  state_transition_valid: {record.get('state_transition_valid')}",
            f"  correction_attempt: {record.get('correction_attempt')}",
            "Lineage",
            f"  lineage_refs: {len(record.get('lineage_refs', []))}",
            f"  validation_refs: {len(record.get('validation_refs', []))}",
            f"  correction_refs: {len(record.get('correction_refs', []))}",
            f"  approval_refs: {len(record.get('approval_refs', []))}",
            "Governance Guarantees",
            "  advisory_only: true",
            "  replay_safe: true",
            "  execution_authority: false",
            "  worker_dispatch: false",
            "  provider_activation: false",
            "  hidden_continuation: false",
        ]
    )


__all__ = [
    "APPROVAL_PENDING",
    "APPROVED",
    "ARTIFACT_TYPE",
    "CORRECTED",
    "CORRECTION_REQUIRED",
    "FAIL_CLOSED",
    "PREPARED_FOR_WORKER",
    "PROPOSED",
    "PROPOSAL_STATES",
    "REJECTED",
    "VALIDATED",
    "VALID_TRANSITIONS",
    "create_proposal_persistence_record",
    "inspect_proposal_persistence",
    "render_proposal_persistence_summary",
    "write_proposal_persistence_record",
]
