"""MOC V1 worker preparation package generation.

This module prepares a governed worker package only from explicit approved
proposal evidence. Worker preparation is not execution, dispatch, provider
activation, orchestration, or hidden continuation.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

APPROVED_FOR_WORKER_PREPARATION = "APPROVED_FOR_WORKER_PREPARATION"
ARTIFACT_TYPE = "MOC_V1_WORKER_PREPARATION_PACKAGE"
SCHEMA_VERSION = "1.0"
PREPARED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

PREPARED_FOR_WORKER = "PREPARED_FOR_WORKER"
NOT_APPROVED = "NOT_APPROVED"
INVALID_APPROVAL_EVIDENCE = "INVALID_APPROVAL_EVIDENCE"
INVALID_PROPOSAL_EVIDENCE = "INVALID_PROPOSAL_EVIDENCE"
FAIL_CLOSED = "FAIL_CLOSED"

APPROVAL_ARTIFACT_TYPE = "MOC_V1_APPROVAL_GATE_RESULT"

FORBIDDEN_AUTHORITY_FIELDS = {
    "execution_authority",
    "dispatch_authority",
    "ready_for_dispatch",
    "worker_dispatch",
    "provider_activation",
    "orchestration_authority",
    "autonomous_continuation",
    "governance_mutation",
    "automatic_execution",
    "hidden_continuation",
}


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(package: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(package)
    safe.pop("worker_preparation_hash", None)
    return safe


def _load_json_object(path_value: str | Path | None, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    if path_value is None or not str(path_value).strip():
        return None, [f"{label} path missing"]
    path = Path(path_value)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"malformed {label} JSON: {type(exc).__name__}"]
    if not isinstance(loaded, dict):
        return None, [f"{label} must be a JSON object"]
    return loaded, []


def _scan_forbidden_fields(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = f"{path}.{key}"
            if key in FORBIDDEN_AUTHORITY_FIELDS and item is not False:
                findings.append(f"forbidden worker preparation authority field present: {item_path}")
            findings.extend(_scan_forbidden_fields(item, item_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_scan_forbidden_fields(item, f"{path}[{index}]"))
    return findings


def _list_value(value: Any) -> list[Any]:
    return _canonical_copy(value) if isinstance(value, list) else []


def _proposal_hash(proposal: dict[str, Any] | None) -> str:
    if not isinstance(proposal, dict):
        return UNKNOWN
    value = proposal.get("proposal_hash")
    if isinstance(value, str) and value.strip():
        return value
    return canonical_hash(proposal)


def _approval_hash(approval_gate: dict[str, Any] | None) -> str:
    if not isinstance(approval_gate, dict):
        return UNKNOWN
    value = approval_gate.get("approval_gate_hash")
    if isinstance(value, str) and value.strip():
        return value
    return canonical_hash(approval_gate)


def _violations(proposal: dict[str, Any] | None, approval_gate: dict[str, Any] | None, load_errors: list[str]) -> list[str]:
    violations = list(load_errors)
    if not isinstance(proposal, dict):
        violations.append("proposal evidence missing")
    if not isinstance(approval_gate, dict):
        violations.append("approval gate evidence missing")
    if violations:
        return sorted(set(violations))
    if approval_gate.get("artifact_type") != APPROVAL_ARTIFACT_TYPE:
        violations.append("approval gate artifact_type invalid")
    if approval_gate.get("approval_status") != APPROVED_FOR_WORKER_PREPARATION:
        violations.append("approval gate is not APPROVED_FOR_WORKER_PREPARATION")
    if proposal.get("proposal_id") != approval_gate.get("proposal_id"):
        violations.append("proposal_id does not match approval gate")
    if _proposal_hash(proposal) != approval_gate.get("proposal_hash"):
        violations.append("proposal_hash does not match approval gate")
    if proposal.get("advisory_only") is not True:
        violations.append("advisory_only must be true")
    if proposal.get("replay_safe") is not True:
        violations.append("replay_safe must be true")
    actions = _list_value(proposal.get("suggested_actions"))
    if not actions:
        violations.append("suggested_actions must be explicit")
    allowed = set(_list_value(proposal.get("allowed_actions")) or actions)
    forbidden = set(_list_value(proposal.get("forbidden_actions")))
    for action in actions:
        if action not in allowed:
            violations.append(f"worker action outside explicit allowed actions: {action}")
        if action in forbidden:
            violations.append(f"worker action appears in explicit forbidden actions: {action}")
    if not _list_value(proposal.get("lineage_refs")):
        violations.append("lineage refs must be explicit")
    approval_refs = _list_value(proposal.get("approval_refs"))
    if not approval_refs:
        approval_refs = [{"approval_gate_hash": _approval_hash(approval_gate)}]
    if not approval_refs:
        violations.append("approval refs must be explicit")
    violations.extend(_scan_forbidden_fields(proposal, "$.proposal"))
    violations.extend(_scan_forbidden_fields(approval_gate, "$.approval_gate"))
    return sorted(set(violations))


def _status(proposal: dict[str, Any] | None, approval_gate: dict[str, Any] | None, violations: list[str]) -> str:
    if any("missing" in violation or "malformed" in violation for violation in violations):
        return FAIL_CLOSED
    if not isinstance(proposal, dict):
        return INVALID_PROPOSAL_EVIDENCE
    if not isinstance(approval_gate, dict) or approval_gate.get("artifact_type") != APPROVAL_ARTIFACT_TYPE:
        return INVALID_APPROVAL_EVIDENCE
    if approval_gate.get("approval_status") != APPROVED_FOR_WORKER_PREPARATION:
        return NOT_APPROVED
    if violations:
        if any("approval gate" in violation for violation in violations):
            return INVALID_APPROVAL_EVIDENCE
        return INVALID_PROPOSAL_EVIDENCE
    return PREPARED_FOR_WORKER


def prepare_worker_package(
    proposal: dict[str, Any] | None,
    approval_gate: dict[str, Any] | None,
    *,
    prepared_at: str = PREPARED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    violations = _violations(proposal, approval_gate, list(load_errors or []))
    status = _status(proposal, approval_gate, violations)
    suggested_actions = _list_value(proposal.get("suggested_actions")) if isinstance(proposal, dict) else []
    forbidden_actions = _list_value(proposal.get("forbidden_actions")) if isinstance(proposal, dict) else []
    package = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "prepared_at": str(prepared_at),
        "preparation_status": status,
        "worker_package_id": canonical_hash(
            {
                "approval_gate_hash": _approval_hash(approval_gate),
                "proposal_hash": _proposal_hash(proposal),
                "suggested_actions": suggested_actions,
            }
        ),
        "proposal_id": str(proposal.get("proposal_id", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "proposal_hash": _proposal_hash(proposal),
        "linked_contract_id": str(proposal.get("linked_contract_id", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "linked_contract_hash": str(proposal.get("linked_contract_hash", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "linked_approval_gate_hash": _approval_hash(approval_gate),
        "allowed_worker_actions": suggested_actions if status == PREPARED_FOR_WORKER else [],
        "forbidden_worker_actions": forbidden_actions,
        "expected_outputs": _list_value(proposal.get("expected_outputs")) if isinstance(proposal, dict) else [],
        "lineage_refs": _list_value(proposal.get("lineage_refs")) if isinstance(proposal, dict) else [],
        "approval_refs": _list_value(proposal.get("approval_refs")) if isinstance(proposal, dict) else [],
        "replay_refs": [
            {"ref_type": "proposal_hash", "hash": _proposal_hash(proposal)},
            {"ref_type": "approval_gate_hash", "hash": _approval_hash(approval_gate)},
        ],
        "preparation_violations": violations,
        "warnings": [] if forbidden_actions else ["forbidden worker actions are limited to explicit proposal evidence"],
        "unknowns": [violation for violation in violations if "missing" in violation or "UNKNOWN" in violation],
        "ready_for_dispatch": False,
        "dispatch_authority": False,
        "execution_authority": False,
        "provider_activation": False,
        "worker_dispatch": False,
        "governance_guarantees": {
            "execution_authority": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
            "automatic_execution": False,
            "hidden_continuation": False,
        },
    }
    if not package["approval_refs"] and isinstance(approval_gate, dict):
        package["approval_refs"] = [{"approval_gate_hash": _approval_hash(approval_gate)}]
    package["worker_preparation_hash"] = canonical_hash(_hash_input(package))
    return package


def write_worker_preparation_package(package: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(package, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_worker_preparation(
    *,
    proposal_path: str | Path | None = None,
    approval_gate_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    proposal, proposal_errors = _load_json_object(proposal_path, "proposal")
    approval_gate, approval_errors = _load_json_object(approval_gate_path, "approval gate")
    package = prepare_worker_package(proposal, approval_gate, load_errors=proposal_errors + approval_errors)
    result = {
        "command": "aigol moc prepare-worker",
        "proposal_path": str(proposal_path or ""),
        "approval_gate_path": str(approval_gate_path or ""),
        "worker_preparation_package": package,
        "read_only": True,
        "execution_authority_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "proposal_repair_added": False,
        "hidden_continuation_added": False,
        "automatic_execution_added": False,
    }
    if output_path:
        result["output"] = write_worker_preparation_package(package, output_path)
    return result


def render_worker_preparation_summary(package: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Worker Preparation",
            f"  preparation_status: {package.get('preparation_status')}",
            f"  worker_package_id: {package.get('worker_package_id')}",
            f"  proposal_id: {package.get('proposal_id')}",
            "Actions",
            f"  allowed_worker_actions: {json.dumps(package.get('allowed_worker_actions', []), sort_keys=True)}",
            f"  forbidden_worker_actions: {json.dumps(package.get('forbidden_worker_actions', []), sort_keys=True)}",
            "Boundary",
            "  ready_for_dispatch: false",
            "  dispatch_authority: false",
            "  execution_authority: false",
            "  provider_activation: false",
            "  worker_dispatch: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "FAIL_CLOSED",
    "INVALID_APPROVAL_EVIDENCE",
    "INVALID_PROPOSAL_EVIDENCE",
    "NOT_APPROVED",
    "PREPARED_FOR_WORKER",
    "inspect_worker_preparation",
    "prepare_worker_package",
    "render_worker_preparation_summary",
    "write_worker_preparation_package",
]
