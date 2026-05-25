"""MOC V1 append-only advisory proposal ledger.

This module appends valid proposal persistence records to a deterministic JSONL
ledger. It does not execute proposals, dispatch workers, activate providers,
infer hidden state, mutate prior ledger entries, mutate governance, repair
proposals, trigger approval, or create autonomous cognition flows.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_PROPOSAL_LEDGER_ENTRY"
SCHEMA_VERSION = "1.0"
LEDGER_RECORDED_AT = "1970-01-01T00:00:00Z"
DEFAULT_LEDGER_PATH = ".runtime/aigol/moc/proposal_ledger.jsonl"
UNKNOWN = "UNKNOWN"
APPENDED = "APPENDED"
FAIL_CLOSED = "FAIL_CLOSED"

PERSISTENCE_ARTIFACT_TYPE = "MOC_V1_PROPOSAL_PERSISTENCE_RECORD"


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(entry: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(entry)
    safe.pop("ledger_entry_hash", None)
    return safe


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _load_persistence_record(input_path: str | Path | None) -> tuple[dict[str, Any] | None, list[str]]:
    if input_path is None or not str(input_path).strip():
        return None, ["persistence record path missing"]
    path = Path(input_path)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"malformed persistence record JSON: {type(exc).__name__}"]
    if not isinstance(loaded, dict):
        return None, ["persistence record must be a JSON object"]
    return loaded, []


def _read_ledger_entries(ledger_path: str | Path) -> tuple[list[dict[str, Any]], list[str]]:
    path = Path(ledger_path)
    if not path.exists():
        return [], []
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            loaded = json.loads(line)
        except Exception as exc:
            errors.append(f"malformed ledger line {index}: {type(exc).__name__}")
            continue
        if not isinstance(loaded, dict):
            errors.append(f"ledger line {index} is not an object")
            continue
        entries.append(loaded)
    return entries, errors


def _previous_ledger_hash(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return UNKNOWN
    value = entries[-1].get("ledger_entry_hash")
    return value if isinstance(value, str) and value.strip() else canonical_hash(entries[-1])


def _validation_errors(record: dict[str, Any] | None) -> list[str]:
    if not isinstance(record, dict):
        return ["persistence record missing"]
    errors: list[str] = []
    if record.get("artifact_type") != PERSISTENCE_ARTIFACT_TYPE:
        errors.append("invalid persistence record artifact_type")
    if not isinstance(record.get("persistence_hash"), str) or not record.get("persistence_hash"):
        errors.append("persistence_hash missing")
    if record.get("state_transition_valid") is not True:
        errors.append("persistence record state transition is not valid")
    if record.get("proposal_state") == "FAIL_CLOSED":
        errors.append("FAIL_CLOSED persistence record cannot be appended")
    if not isinstance(record.get("lineage_refs"), list) or not record.get("lineage_refs"):
        errors.append("lineage_refs missing")
    return sorted(set(errors))


def _entry_from_record(
    record: dict[str, Any] | None,
    *,
    previous_hash: str,
    append_status: str,
    errors: list[str],
    ledger_recorded_at: str,
) -> dict[str, Any]:
    safe_record = record if isinstance(record, dict) else {}
    entry = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "ledger_recorded_at": str(ledger_recorded_at),
        "ledger_append_status": append_status,
        "append_performed": append_status == APPENDED,
        "ledger_entry_id": canonical_hash(
            {
                "linked_persistence_hash": safe_record.get("persistence_hash", UNKNOWN),
                "previous_ledger_hash": previous_hash,
                "proposal_id": safe_record.get("proposal_id", UNKNOWN),
                "proposal_state": safe_record.get("proposal_state", UNKNOWN),
            }
        ),
        "proposal_id": str(safe_record.get("proposal_id", UNKNOWN)),
        "proposal_hash": str(safe_record.get("proposal_hash", UNKNOWN)),
        "proposal_state": str(safe_record.get("proposal_state", FAIL_CLOSED if append_status == FAIL_CLOSED else UNKNOWN)),
        "linked_persistence_hash": str(safe_record.get("persistence_hash", UNKNOWN)),
        "linked_contract_id": str(safe_record.get("linked_contract_id", UNKNOWN)),
        "linked_contract_hash": str(safe_record.get("linked_contract_hash", UNKNOWN)),
        "correction_attempt": int(safe_record.get("correction_attempt", 0)) if str(safe_record.get("correction_attempt", "0")).isdigit() else 0,
        "lineage_refs": _canonical_copy(safe_record.get("lineage_refs", [])) if isinstance(safe_record.get("lineage_refs"), list) else [],
        "validation_refs": _canonical_copy(safe_record.get("validation_refs", [])) if isinstance(safe_record.get("validation_refs"), list) else [],
        "correction_refs": _canonical_copy(safe_record.get("correction_refs", [])) if isinstance(safe_record.get("correction_refs"), list) else [],
        "approval_refs": _canonical_copy(safe_record.get("approval_refs", [])) if isinstance(safe_record.get("approval_refs"), list) else [],
        "previous_ledger_hash": previous_hash,
        "append_only": True,
        "replay_safe": True,
        "advisory_only": True,
        "violations": sorted(set(errors)),
        "governance_guarantees": {
            "execution_authority": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
            "hidden_continuation": False,
            "proposal_execution": False,
            "automatic_approval": False,
        },
    }
    entry["ledger_entry_hash"] = canonical_hash(_hash_input(entry))
    return entry


def build_proposal_ledger_entry(
    persistence_record: dict[str, Any] | None,
    *,
    previous_ledger_hash: str = UNKNOWN,
    ledger_recorded_at: str = LEDGER_RECORDED_AT,
    load_errors: list[str] | None = None,
    ledger_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(load_errors or []) + list(ledger_errors or []) + _validation_errors(persistence_record)
    append_status = FAIL_CLOSED if errors else APPENDED
    return _entry_from_record(
        persistence_record,
        previous_hash=previous_ledger_hash,
        append_status=append_status,
        errors=errors,
        ledger_recorded_at=ledger_recorded_at,
    )


def append_proposal_ledger_entry(
    persistence_record: dict[str, Any] | None,
    *,
    ledger_path: str | Path = DEFAULT_LEDGER_PATH,
) -> dict[str, Any]:
    path = Path(ledger_path)
    entries, ledger_errors = _read_ledger_entries(path)
    entry = build_proposal_ledger_entry(
        persistence_record,
        previous_ledger_hash=_previous_ledger_hash(entries),
        ledger_errors=ledger_errors,
    )
    if entry["ledger_append_status"] == APPENDED:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical_json(entry) + "\n")
    return entry


def write_ledger_entry(entry: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_proposal_ledger_append(
    *,
    persistence_record_path: str | Path | None = None,
    ledger_path: str | Path = DEFAULT_LEDGER_PATH,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    record, load_errors = _load_persistence_record(persistence_record_path)
    if load_errors:
        entry = build_proposal_ledger_entry(record, load_errors=load_errors)
    else:
        entry = append_proposal_ledger_entry(record, ledger_path=ledger_path)
    result = {
        "command": "aigol moc append-ledger",
        "persistence_record_path": str(persistence_record_path or ""),
        "ledger_path": str(ledger_path),
        "proposal_ledger_entry": entry,
        "read_only_except_append": True,
        "append_only": True,
        "execution_authority_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "proposal_repair_added": False,
        "hidden_continuation_added": False,
        "automatic_approval_added": False,
    }
    if output_path:
        result["output"] = write_ledger_entry(entry, output_path)
    return result


def render_proposal_ledger_summary(entry: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Proposal Ledger",
            f"  ledger_append_status: {entry.get('ledger_append_status')}",
            f"  ledger_entry_id: {entry.get('ledger_entry_id')}",
            f"  proposal_id: {entry.get('proposal_id')}",
            f"  proposal_state: {entry.get('proposal_state')}",
            "Chronology",
            f"  previous_ledger_hash: {entry.get('previous_ledger_hash')}",
            f"  ledger_entry_hash: {entry.get('ledger_entry_hash')}",
            "Lineage",
            f"  lineage_refs: {len(entry.get('lineage_refs', []))}",
            f"  validation_refs: {len(entry.get('validation_refs', []))}",
            f"  correction_refs: {len(entry.get('correction_refs', []))}",
            f"  approval_refs: {len(entry.get('approval_refs', []))}",
            "Governance Guarantees",
            "  append_only: true",
            "  advisory_only: true",
            "  replay_safe: true",
            "  execution_authority: false",
            "  worker_dispatch: false",
            "  provider_activation: false",
            "  automatic_approval: false",
        ]
    )


__all__ = [
    "APPENDED",
    "ARTIFACT_TYPE",
    "DEFAULT_LEDGER_PATH",
    "FAIL_CLOSED",
    "append_proposal_ledger_entry",
    "build_proposal_ledger_entry",
    "inspect_proposal_ledger_append",
    "render_proposal_ledger_summary",
    "write_ledger_entry",
]
