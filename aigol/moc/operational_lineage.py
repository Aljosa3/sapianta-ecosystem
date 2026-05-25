"""MOC V1 operational lineage closure.

This module links explicit MOC V1 operational artifacts into a deterministic,
replay-visible lineage chain. It is lineage-only: no execution, provider
activation, retry, orchestration, hidden reconstruction, semantic repair, or
automatic task generation is performed.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_OPERATIONAL_LINEAGE"
SCHEMA_VERSION = "1.0"
GENERATED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

LINEAGE_COMPLETE = "LINEAGE_COMPLETE"
LINEAGE_COMPLETE_WITH_WARNINGS = "LINEAGE_COMPLETE_WITH_WARNINGS"
LINEAGE_INCOMPLETE = "LINEAGE_INCOMPLETE"
INVALID_LINEAGE = "INVALID_LINEAGE"
FAIL_CLOSED = "FAIL_CLOSED"

CRITICAL_REFS = (
    "contract_ref",
    "proposal_ref",
    "approval_ref",
    "runtime_dispatch_ref",
    "governed_return_ref",
)

CHAIN_REFS = (
    "contract_ref",
    "proposal_ref",
    "validation_ref",
    "correction_ref",
    "persistence_ref",
    "ledger_ref",
    "approval_ref",
    "worker_preparation_ref",
    "dispatch_preview_ref",
    "dispatch_request_ref",
    "dispatch_authorization_ref",
    "runtime_dispatch_ref",
    "provider_gate_ref",
    "governed_return_ref",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(lineage: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(lineage)
    safe.pop("lineage_hash", None)
    return safe


def _load_json_object(path_value: str | Path | None, label: str, *, required: bool) -> tuple[dict[str, Any] | None, list[str]]:
    if path_value is None or not str(path_value).strip():
        return None, [f"{label} path missing"] if required else []
    path = Path(path_value)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"malformed {label} JSON: {type(exc).__name__}"]
    if not isinstance(loaded, dict):
        return None, [f"{label} must be a JSON object"]
    return loaded, []


def _string_value(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return UNKNOWN


def _hash_or_existing(value: dict[str, Any] | None, field: str) -> str:
    if not isinstance(value, dict):
        return UNKNOWN
    existing = value.get(field)
    if isinstance(existing, str) and existing.strip():
        return existing
    return canonical_hash(value)


def _artifact_ref(value: dict[str, Any] | None, *fields: str) -> str:
    if not isinstance(value, dict):
        return UNKNOWN
    for field in fields:
        ref = value.get(field)
        if isinstance(ref, str) and ref.strip():
            return ref
    return UNKNOWN


def _lineage_refs(value: dict[str, Any] | None) -> list[Any]:
    return _canonical_copy(value.get("lineage_refs")) if isinstance(value, dict) and isinstance(value.get("lineage_refs"), list) else []


def _approval_refs(value: dict[str, Any] | None) -> list[Any]:
    return _canonical_copy(value.get("approval_refs")) if isinstance(value, dict) and isinstance(value.get("approval_refs"), list) else []


def _replay_refs(value: dict[str, Any] | None) -> list[Any]:
    return _canonical_copy(value.get("replay_refs")) if isinstance(value, dict) and isinstance(value.get("replay_refs"), list) else []


def _chain(
    contract: dict[str, Any] | None,
    proposal: dict[str, Any] | None,
    approval: dict[str, Any] | None,
    runtime_dispatch: dict[str, Any] | None,
    governed_return: dict[str, Any] | None,
    provider_gate: dict[str, Any] | None,
) -> dict[str, str]:
    approval_lineage = _lineage_refs(approval)
    return {
        "contract_ref": _artifact_ref(contract, "contract_hash", "intent_id"),
        "proposal_ref": _artifact_ref(proposal, "proposal_hash", "proposal_id"),
        "validation_ref": _artifact_ref(approval, "linked_validation_hash", "validation_result_hash"),
        "correction_ref": _artifact_ref(approval, "linked_correction_hash", "correction_feedback_hash"),
        "persistence_ref": _artifact_ref(approval, "linked_persistence_hash", "persistence_record_hash"),
        "ledger_ref": _artifact_ref(approval, "linked_ledger_entry_hash"),
        "approval_ref": _artifact_ref(approval, "approval_gate_hash"),
        "worker_preparation_ref": _artifact_ref(runtime_dispatch, "worker_preparation_hash"),
        "dispatch_preview_ref": _artifact_ref(runtime_dispatch, "dispatch_preview_hash"),
        "dispatch_request_ref": _artifact_ref(runtime_dispatch, "dispatch_request_hash"),
        "dispatch_authorization_ref": _artifact_ref(runtime_dispatch, "dispatch_authorization_hash"),
        "runtime_dispatch_ref": _artifact_ref(runtime_dispatch, "runtime_dispatch_hash"),
        "provider_gate_ref": _artifact_ref(provider_gate, "provider_gate_hash"),
        "governed_return_ref": _artifact_ref(governed_return, "interpretation_hash"),
    } | {
        key: value
        for key, value in {
            "validation_ref": _lineage_value(approval_lineage, "validation", _artifact_ref(approval, "linked_validation_hash", "validation_result_hash")),
            "correction_ref": _lineage_value(approval_lineage, "correction", _artifact_ref(approval, "linked_correction_hash", "correction_feedback_hash")),
            "persistence_ref": _lineage_value(approval_lineage, "persistence", _artifact_ref(approval, "linked_persistence_hash", "persistence_record_hash")),
        }.items()
    }


def _lineage_value(refs: list[Any], token: str, fallback: str) -> str:
    if fallback != UNKNOWN:
        return fallback
    for item in refs:
        if not isinstance(item, dict):
            continue
        text = json.dumps(item, sort_keys=True)
        if token in text:
            for key in ("hash", "ref", "artifact_hash"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    return value
    return UNKNOWN


def _missing_refs(chain: dict[str, str]) -> list[str]:
    return [name for name in CHAIN_REFS if chain.get(name) == UNKNOWN]


def _critical_missing_refs(chain: dict[str, str]) -> list[str]:
    return [name for name in CRITICAL_REFS if chain.get(name) == UNKNOWN]


def _violations(
    contract: dict[str, Any] | None,
    proposal: dict[str, Any] | None,
    approval: dict[str, Any] | None,
    runtime_dispatch: dict[str, Any] | None,
    governed_return: dict[str, Any] | None,
    provider_gate: dict[str, Any] | None,
    chain: dict[str, str],
    load_errors: list[str],
) -> list[str]:
    violations = list(load_errors)
    if not isinstance(contract, dict):
        violations.append("contract evidence missing")
    if not isinstance(proposal, dict):
        violations.append("proposal evidence missing")
    if not isinstance(approval, dict):
        violations.append("approval evidence missing")
    if not isinstance(runtime_dispatch, dict):
        violations.append("runtime dispatch evidence missing")
    if not isinstance(governed_return, dict):
        violations.append("governed return evidence missing")
    if isinstance(contract, dict) and contract.get("advisory_only") is not True:
        violations.append("contract advisory_only must be true")
    if isinstance(proposal, dict) and proposal.get("proposal_id") != _string_value(approval.get("proposal_id") if isinstance(approval, dict) else UNKNOWN):
        violations.append("proposal_id does not match approval")
    if isinstance(runtime_dispatch, dict) and isinstance(governed_return, dict):
        if runtime_dispatch.get("runtime_dispatch_hash") != governed_return.get("runtime_dispatch_hash"):
            violations.append("runtime dispatch hash does not match governed return")
    if isinstance(provider_gate, dict) and isinstance(governed_return, dict):
        if provider_gate.get("provider_gate_hash") != governed_return.get("provider_gate_hash"):
            violations.append("provider gate hash does not match governed return")
    if _critical_missing_refs(chain):
        violations.append("critical lineage refs missing")
    return sorted(set(violations))


def _continuity(
    contract: dict[str, Any] | None,
    proposal: dict[str, Any] | None,
    approval: dict[str, Any] | None,
    runtime_dispatch: dict[str, Any] | None,
    governed_return: dict[str, Any] | None,
) -> dict[str, bool]:
    proposal_contract_hash = _string_value(proposal.get("linked_contract_hash")) if isinstance(proposal, dict) else UNKNOWN
    contract_hash = _hash_or_existing(contract, "contract_hash")
    proposal_hash = _hash_or_existing(proposal, "proposal_hash")
    return {
        "contract_to_proposal": bool(contract_hash != UNKNOWN and proposal_contract_hash == contract_hash),
        "proposal_to_validation": bool(proposal_hash != UNKNOWN and isinstance(approval, dict) and approval.get("proposal_hash") == proposal_hash),
        "validation_to_approval": bool(isinstance(approval, dict) and approval.get("approval_gate_hash")),
        "approval_to_dispatch": bool(
            isinstance(approval, dict)
            and isinstance(runtime_dispatch, dict)
            and approval.get("approval_gate_hash") in json.dumps(runtime_dispatch, sort_keys=True)
        ),
        "dispatch_to_runtime": bool(isinstance(runtime_dispatch, dict) and runtime_dispatch.get("runtime_dispatch_hash")),
        "runtime_to_return": bool(
            isinstance(runtime_dispatch, dict)
            and isinstance(governed_return, dict)
            and runtime_dispatch.get("runtime_dispatch_hash") == governed_return.get("runtime_dispatch_hash")
        ),
    }


def _status(violations: list[str], missing_refs: list[str], continuity: dict[str, bool]) -> str:
    if any("path missing" in item or "malformed" in item or "must be a JSON object" in item for item in violations):
        return FAIL_CLOSED
    if any(item.endswith("evidence missing") or item == "critical lineage refs missing" for item in violations):
        return FAIL_CLOSED
    if any("does not match" in item for item in violations):
        return FAIL_CLOSED
    if any("must be true" in item for item in violations):
        return INVALID_LINEAGE
    if missing_refs:
        return LINEAGE_INCOMPLETE
    if not all(continuity.values()):
        return LINEAGE_COMPLETE_WITH_WARNINGS
    return LINEAGE_COMPLETE


def build_operational_lineage(
    *,
    contract: dict[str, Any] | None,
    proposal: dict[str, Any] | None,
    approval: dict[str, Any] | None,
    runtime_dispatch: dict[str, Any] | None,
    governed_return: dict[str, Any] | None,
    provider_gate: dict[str, Any] | None = None,
    generated_at: str = GENERATED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    chain = _chain(contract, proposal, approval, runtime_dispatch, governed_return, provider_gate)
    missing_refs = _missing_refs(chain)
    continuity = _continuity(contract, proposal, approval, runtime_dispatch, governed_return)
    violations = _violations(contract, proposal, approval, runtime_dispatch, governed_return, provider_gate, chain, list(load_errors or []))
    status = _status(violations, missing_refs, continuity)
    complete = status == LINEAGE_COMPLETE
    reconstructable = complete and not missing_refs
    lineage = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "lineage_status": status,
        "operational_lineage_id": "moc-operational-lineage-" + canonical_hash(chain),
        "proposal_id": _string_value((proposal or {}).get("proposal_id")),
        "proposal_hash": _hash_or_existing(proposal, "proposal_hash"),
        "linked_contract_id": _string_value((proposal or {}).get("linked_contract_id") or (approval or {}).get("linked_contract_id")),
        "linked_contract_hash": _string_value((proposal or {}).get("linked_contract_hash") or (approval or {}).get("linked_contract_hash")),
        "lineage_chain": chain,
        "lineage_continuity": continuity,
        "replay_reconstructable": reconstructable,
        "lineage_complete": complete,
        "missing_refs": missing_refs,
        "lineage_violations": violations,
        "warnings": ["lineage closure does not infer missing lineage"] if missing_refs else [],
        "unknowns": [item for item in missing_refs + violations if "missing" in item or "UNKNOWN" in item],
        "governance_guarantees": {
            "lineage_only": True,
            "execution_authority": False,
            "provider_activation": False,
            "runtime_execution": False,
            "automatic_retry": False,
            "automatic_next_task": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
        },
    }
    lineage["lineage_hash"] = canonical_hash(_hash_input(lineage))
    return lineage


def write_operational_lineage(lineage: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lineage, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_operational_lineage(
    *,
    contract_path: str | Path | None = None,
    proposal_path: str | Path | None = None,
    approval_path: str | Path | None = None,
    runtime_dispatch_path: str | Path | None = None,
    governed_return_path: str | Path | None = None,
    provider_gate_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    contract, contract_errors = _load_json_object(contract_path, "contract", required=True)
    proposal, proposal_errors = _load_json_object(proposal_path, "proposal", required=True)
    approval, approval_errors = _load_json_object(approval_path, "approval", required=True)
    runtime_dispatch, runtime_errors = _load_json_object(runtime_dispatch_path, "runtime dispatch", required=True)
    governed_return, return_errors = _load_json_object(governed_return_path, "governed return", required=True)
    provider_gate, provider_errors = _load_json_object(provider_gate_path, "provider gate", required=False)
    lineage = build_operational_lineage(
        contract=contract,
        proposal=proposal,
        approval=approval,
        runtime_dispatch=runtime_dispatch,
        governed_return=governed_return,
        provider_gate=provider_gate,
        load_errors=contract_errors + proposal_errors + approval_errors + runtime_errors + return_errors + provider_errors,
    )
    result = {
        "command": "aigol moc operational-lineage",
        "operational_lineage": lineage,
        "lineage_only": True,
        "execution_authority_added": False,
        "provider_activation_added": False,
        "runtime_execution_added": False,
        "automatic_retry_added": False,
        "automatic_next_task_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "hidden_continuation_added": False,
        "lineage_repair_added": False,
    }
    if output_path:
        result["output"] = write_operational_lineage(lineage, output_path)
    return result


def render_operational_lineage_summary(lineage: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Operational Lineage",
            f"  lineage_status: {lineage.get('lineage_status')}",
            f"  operational_lineage_id: {lineage.get('operational_lineage_id')}",
            f"  replay_reconstructable: {lineage.get('replay_reconstructable')}",
            f"  lineage_complete: {lineage.get('lineage_complete')}",
            f"  missing_refs: {len(lineage.get('missing_refs', []))}",
            "Boundary",
            "  lineage_only: true",
            "  execution_authority: false",
            "  provider_activation: false",
            "  automatic_retry: false",
            "  automatic_next_task: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "FAIL_CLOSED",
    "INVALID_LINEAGE",
    "LINEAGE_COMPLETE",
    "LINEAGE_COMPLETE_WITH_WARNINGS",
    "LINEAGE_INCOMPLETE",
    "build_operational_lineage",
    "inspect_operational_lineage",
    "render_operational_lineage_summary",
    "write_operational_lineage",
]
