"""MOC V1 operational approval gate.

This module evaluates explicit proposal, ledger, and approval evidence for
worker-preparation eligibility. Approval does not execute, dispatch workers,
activate providers, mutate governance, auto-approve, or create hidden
continuation.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_APPROVAL_GATE_RESULT"
SCHEMA_VERSION = "1.0"
APPROVED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

APPROVED_FOR_WORKER_PREPARATION = "APPROVED_FOR_WORKER_PREPARATION"
APPROVAL_REJECTED = "APPROVAL_REJECTED"
APPROVAL_PENDING = "APPROVAL_PENDING"
INVALID_APPROVAL_EVIDENCE = "INVALID_APPROVAL_EVIDENCE"
FAIL_CLOSED = "FAIL_CLOSED"

LEDGER_ARTIFACT_TYPE = "MOC_V1_PROPOSAL_LEDGER_ENTRY"

FORBIDDEN_AUTHORITY_FIELDS = {
    "execution_authority",
    "dispatch_authority",
    "worker_dispatch",
    "provider_activation",
    "orchestration_authority",
    "autonomous_continuation",
    "governance_mutation",
    "automatic_execution",
    "hidden_continuation",
    "recursive_worker_spawn",
    "self_authorization",
}


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(result: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(result)
    safe.pop("approval_gate_hash", None)
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
                findings.append(f"forbidden approval authority field present: {item_path}")
            findings.extend(_scan_forbidden_fields(item, item_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_scan_forbidden_fields(item, f"{path}[{index}]"))
    return findings


def _hash_or_existing(value: dict[str, Any] | None, field: str) -> str:
    if not isinstance(value, dict):
        return UNKNOWN
    existing = value.get(field)
    if isinstance(existing, str) and existing.strip():
        return existing
    return canonical_hash(value)


def _approval_violations(
    proposal: dict[str, Any] | None,
    ledger_entry: dict[str, Any] | None,
    approval_evidence: dict[str, Any] | None,
    load_errors: list[str],
) -> list[str]:
    violations = list(load_errors)
    if not isinstance(proposal, dict):
        violations.append("proposal evidence missing")
    if not isinstance(ledger_entry, dict):
        violations.append("ledger evidence missing")
    if not isinstance(approval_evidence, dict):
        violations.append("approval evidence missing")
    if violations:
        return sorted(set(violations))

    if ledger_entry.get("artifact_type") != LEDGER_ARTIFACT_TYPE:
        violations.append("ledger artifact_type invalid")
    if ledger_entry.get("ledger_append_status") != "APPENDED":
        violations.append("proposal must exist in appended proposal ledger")
    if ledger_entry.get("proposal_state") != "VALIDATED":
        violations.append("proposal must already be VALIDATED")
    if not ledger_entry.get("lineage_refs"):
        violations.append("proposal lineage must exist")
    if ledger_entry.get("proposal_id") != proposal.get("proposal_id"):
        violations.append("proposal_id does not match ledger entry")
    if ledger_entry.get("proposal_hash") != _hash_or_existing(proposal, "proposal_hash"):
        violations.append("proposal_hash does not match ledger entry")
    if proposal.get("replay_safe") is not True or ledger_entry.get("replay_safe") is not True:
        violations.append("replay_safe must be true")
    if proposal.get("advisory_only") is not True or ledger_entry.get("advisory_only") is not True:
        violations.append("advisory_only must be true")
    if approval_evidence.get("human_review") is not True:
        violations.append("human_review approval must exist")
    if approval_evidence.get("approval_decision") not in {"APPROVED", "APPROVED_FOR_WORKER_PREPARATION"}:
        violations.append("approval_decision must approve worker preparation eligibility")
    if proposal.get("correction_status") in {"CORRECTION_REQUIRED", "CORRECTION_LIMIT_REACHED"}:
        violations.append("correction loop unresolved")
    if ledger_entry.get("correction_status") in {"CORRECTION_REQUIRED", "CORRECTION_LIMIT_REACHED"}:
        violations.append("ledger correction loop unresolved")
    if approval_evidence.get("correction_status") in {"CORRECTION_REQUIRED", "CORRECTION_LIMIT_REACHED"}:
        violations.append("approval evidence correction loop unresolved")
    violations.extend(_scan_forbidden_fields(proposal, "$.proposal"))
    violations.extend(_scan_forbidden_fields(ledger_entry, "$.ledger_entry"))
    violations.extend(_scan_forbidden_fields(approval_evidence, "$.approval_evidence"))
    return sorted(set(violations))


def _status(violations: list[str], approval_evidence: dict[str, Any] | None) -> str:
    if any("missing" in violation or "malformed" in violation for violation in violations):
        return FAIL_CLOSED
    if not isinstance(approval_evidence, dict):
        return FAIL_CLOSED
    if approval_evidence.get("human_review") is not True:
        return APPROVAL_PENDING
    if violations:
        return APPROVAL_REJECTED
    return APPROVED_FOR_WORKER_PREPARATION


def _evidence(violations: list[str], proposal: dict[str, Any] | None, ledger_entry: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [
        {
            "check": "proposal_validated",
            "status": "PASS" if isinstance(ledger_entry, dict) and ledger_entry.get("proposal_state") == "VALIDATED" else "FAIL",
            "details": [],
        },
        {
            "check": "proposal_lineage",
            "status": "PASS" if isinstance(ledger_entry, dict) and bool(ledger_entry.get("lineage_refs")) else "FAIL",
            "details": [],
        },
        {
            "check": "proposal_ledger_presence",
            "status": "PASS" if isinstance(ledger_entry, dict) and ledger_entry.get("ledger_append_status") == "APPENDED" else "FAIL",
            "details": [],
        },
        {
            "check": "approval_boundary",
            "status": "PASS" if not violations else "FAIL",
            "details": violations,
        },
        {
            "check": "proposal_non_execution",
            "status": "PASS",
            "details": ["approval grants worker preparation eligibility only"],
        },
    ]


def evaluate_approval_gate(
    proposal: dict[str, Any] | None,
    ledger_entry: dict[str, Any] | None,
    approval_evidence: dict[str, Any] | None,
    *,
    approved_at: str = APPROVED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    violations = _approval_violations(proposal, ledger_entry, approval_evidence, list(load_errors or []))
    status = _status(violations, approval_evidence)
    result = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "approved_at": str(approved_at),
        "approval_status": status,
        "proposal_id": str(proposal.get("proposal_id", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "proposal_hash": _hash_or_existing(proposal, "proposal_hash"),
        "linked_contract_id": str(ledger_entry.get("linked_contract_id", UNKNOWN)) if isinstance(ledger_entry, dict) else UNKNOWN,
        "linked_contract_hash": str(ledger_entry.get("linked_contract_hash", UNKNOWN)) if isinstance(ledger_entry, dict) else UNKNOWN,
        "linked_ledger_entry_hash": str(ledger_entry.get("ledger_entry_hash", UNKNOWN)) if isinstance(ledger_entry, dict) else UNKNOWN,
        "approval_eligible": status == APPROVED_FOR_WORKER_PREPARATION,
        "approval_requirements_satisfied": status == APPROVED_FOR_WORKER_PREPARATION,
        "approval_violations": violations,
        "warnings": [],
        "unknowns": [violation for violation in violations if "missing" in violation or "UNKNOWN" in violation],
        "evidence": _evidence(violations, proposal, ledger_entry),
        "governance_guarantees": {
            "execution_authority": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
            "automatic_execution": False,
            "automatic_approval": False,
            "proposal_execution": False,
        },
    }
    result["approval_gate_hash"] = canonical_hash(_hash_input(result))
    return result


def write_approval_gate_result(result: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_approval_gate(
    *,
    proposal_path: str | Path | None = None,
    ledger_entry_path: str | Path | None = None,
    approval_evidence_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    proposal, proposal_errors = _load_json_object(proposal_path, "proposal")
    ledger_entry, ledger_errors = _load_json_object(ledger_entry_path, "ledger entry")
    approval_evidence, approval_errors = _load_json_object(approval_evidence_path, "approval evidence")
    result_artifact = evaluate_approval_gate(
        proposal,
        ledger_entry,
        approval_evidence,
        load_errors=proposal_errors + ledger_errors + approval_errors,
    )
    result = {
        "command": "aigol moc approval-gate",
        "proposal_path": str(proposal_path or ""),
        "ledger_entry_path": str(ledger_entry_path or ""),
        "approval_evidence_path": str(approval_evidence_path or ""),
        "approval_gate_result": result_artifact,
        "read_only": True,
        "execution_authority_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "automatic_execution_added": False,
        "automatic_approval_added": False,
        "hidden_continuation_added": False,
    }
    if output_path:
        result["output"] = write_approval_gate_result(result_artifact, output_path)
    return result


def render_approval_gate_summary(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Approval Gate",
            f"  approval_status: {result.get('approval_status')}",
            f"  approval_eligible: {result.get('approval_eligible')}",
            "Proposal",
            f"  proposal_id: {result.get('proposal_id')}",
            f"  proposal_hash: {result.get('proposal_hash')}",
            "Ledger",
            f"  linked_ledger_entry_hash: {result.get('linked_ledger_entry_hash')}",
            "Violations",
            f"  {json.dumps(result.get('approval_violations', []), sort_keys=True)}",
            "Governance Guarantees",
            "  worker_preparation_eligibility_only: true",
            "  execution_authority: false",
            "  worker_dispatch: false",
            "  provider_activation: false",
            "  automatic_execution: false",
            "  automatic_approval: false",
        ]
    )


__all__ = [
    "APPROVAL_PENDING",
    "APPROVAL_REJECTED",
    "APPROVED_FOR_WORKER_PREPARATION",
    "ARTIFACT_TYPE",
    "FAIL_CLOSED",
    "INVALID_APPROVAL_EVIDENCE",
    "evaluate_approval_gate",
    "inspect_approval_gate",
    "render_approval_gate_summary",
    "write_approval_gate_result",
]
