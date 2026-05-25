"""MOC V1 advisory proposal validation.

This module validates explicit advisory proposals against already-validated
semantic contracts. It does not execute, dispatch, activate providers, infer
hidden meaning, mutate governance, repair proposals, or create runtime cognition
loops.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_ADVISORY_PROPOSAL_VALIDATION_RESULT"
SCHEMA_VERSION = "1.0"
VALIDATED_AT = "1970-01-01T00:00:00Z"
VALID = "VALID"
INVALID_SCHEMA = "INVALID_SCHEMA"
INVALID_BOUNDARY = "INVALID_BOUNDARY"
INVALID_CONTRACT_REFERENCE = "INVALID_CONTRACT_REFERENCE"
UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"
FAIL_CLOSED = "FAIL_CLOSED"
UNKNOWN = "UNKNOWN"

REQUIRED_PROPOSAL_FIELDS = (
    "proposal_id",
    "proposal_summary",
    "linked_contract_id",
    "linked_contract_hash",
    "suggested_actions",
    "expected_outputs",
    "bounded_scope",
    "approvals_required",
    "replay_safe",
    "advisory_only",
)

FORBIDDEN_PROPOSAL_FIELDS = {
    "execution_authority",
    "dispatch_authority",
    "provider_activation",
    "orchestration_authority",
    "autonomous_continuation",
    "governance_mutation",
    "recursive_worker_spawn",
    "self_authorization",
}


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(result: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(result)
    safe.pop("validation_result_hash", None)
    return safe


def _load_json_object(path_value: str | Path | None, label: str) -> tuple[dict[str, Any] | None, list[str], str]:
    if path_value is None or not str(path_value).strip():
        return None, [f"{label} path missing"], FAIL_CLOSED
    path = Path(path_value)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"malformed {label} JSON: {type(exc).__name__}"], FAIL_CLOSED
    if not isinstance(loaded, dict):
        return None, [f"{label} must be a JSON object"], FAIL_CLOSED
    return loaded, [], UNKNOWN


def _extract_validated_contract(contract_artifact: dict[str, Any] | None) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    if not isinstance(contract_artifact, dict):
        return None, None, ["validated contract evidence missing"]
    if isinstance(contract_artifact.get("contract"), dict) and isinstance(contract_artifact.get("validation_result"), dict):
        return _canonical_copy(contract_artifact["contract"]), _canonical_copy(contract_artifact["validation_result"]), []
    if (
        isinstance(contract_artifact.get("advisory_contract_generation_result"), dict)
        and isinstance(contract_artifact["advisory_contract_generation_result"].get("contract"), dict)
        and isinstance(contract_artifact["advisory_contract_generation_result"].get("validation_result"), dict)
    ):
        generation = contract_artifact["advisory_contract_generation_result"]
        return _canonical_copy(generation["contract"]), _canonical_copy(generation["validation_result"]), []
    if contract_artifact.get("artifact_type") == "MOC_V1_CONTRACT_VALIDATION_RESULT":
        return None, _canonical_copy(contract_artifact), ["validated contract content missing"]
    return None, None, ["validated contract artifact structure unsupported"]


def _schema_violations(proposal: dict[str, Any] | None) -> list[str]:
    if not isinstance(proposal, dict):
        return ["proposal evidence missing"]
    violations = [f"missing required proposal field: {field}" for field in REQUIRED_PROPOSAL_FIELDS if field not in proposal]
    for field in ("suggested_actions", "expected_outputs", "approvals_required"):
        value = proposal.get(field)
        if not isinstance(value, list) or not value:
            violations.append(f"{field} must be a non-empty array")
    for field in ("proposal_id", "proposal_summary", "linked_contract_id", "linked_contract_hash", "bounded_scope"):
        value = proposal.get(field)
        if not isinstance(value, str) or not value.strip():
            violations.append(f"{field} must be a non-empty string")
    if proposal.get("advisory_only") is not True:
        violations.append("advisory_only must be true")
    if proposal.get("replay_safe") is not True:
        violations.append("replay_safe must be true")
    return sorted(set(violations))


def _scan_forbidden_fields(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = f"{path}.{key}"
            if key in FORBIDDEN_PROPOSAL_FIELDS:
                findings.append(f"forbidden proposal authority field present: {item_path}")
            findings.extend(_scan_forbidden_fields(item, item_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_scan_forbidden_fields(item, f"{path}[{index}]"))
    return findings


def _contract_reference_violations(
    proposal: dict[str, Any] | None,
    contract: dict[str, Any] | None,
    validation_result: dict[str, Any] | None,
) -> list[str]:
    violations: list[str] = []
    if not isinstance(proposal, dict):
        return ["proposal evidence missing"]
    if not isinstance(contract, dict):
        return ["validated contract content missing"]
    if not isinstance(validation_result, dict) or validation_result.get("validation_status") != VALID:
        violations.append("linked contract validation status must be VALID")
    contract_id = str(contract.get("intent_id", UNKNOWN))
    contract_hash = canonical_hash(contract)
    if proposal.get("linked_contract_id") != contract_id:
        violations.append("linked_contract_id mismatch")
    if proposal.get("linked_contract_hash") != contract_hash:
        violations.append("linked_contract_hash mismatch")
    if validation_result and validation_result.get("contract_hash") != contract_hash:
        violations.append("linked contract validation hash mismatch")
    return sorted(set(violations))


def _boundary_violations(proposal: dict[str, Any] | None, contract: dict[str, Any] | None) -> list[str]:
    if not isinstance(proposal, dict):
        return ["proposal evidence missing"]
    violations = _scan_forbidden_fields(proposal)
    if proposal.get("advisory_only") is not True:
        violations.append("advisory_only must be true")
    if proposal.get("replay_safe") is not True:
        violations.append("replay_safe must be true")
    approvals = proposal.get("approvals_required")
    if not isinstance(approvals, list) or "human_review" not in approvals:
        violations.append("approvals_required must include human_review")
    suggested = proposal.get("suggested_actions")
    if isinstance(contract, dict) and isinstance(suggested, list):
        allowed = set(contract.get("allowed_actions", []))
        forbidden = set(contract.get("forbidden_actions", []))
        for action in suggested:
            if action not in allowed:
                violations.append(f"suggested action outside contract allowed_actions: {action}")
            if action in forbidden:
                violations.append(f"suggested action appears in contract forbidden_actions: {action}")
    return sorted(set(violations))


def _status(
    load_errors: list[str],
    schema_violations: list[str],
    reference_violations: list[str],
    boundary_violations: list[str],
) -> str:
    if load_errors:
        return FAIL_CLOSED
    if reference_violations:
        return INVALID_CONTRACT_REFERENCE
    if boundary_violations:
        return INVALID_BOUNDARY
    if schema_violations:
        return INVALID_SCHEMA
    return VALID


def _evidence(
    schema_violations: list[str],
    reference_violations: list[str],
    boundary_violations: list[str],
) -> list[dict[str, Any]]:
    return [
        {
            "check": "proposal_schema",
            "status": "PASS" if not schema_violations else "FAIL",
            "details": schema_violations,
        },
        {
            "check": "contract_reference",
            "status": "PASS" if not reference_violations else "FAIL",
            "details": reference_violations,
        },
        {
            "check": "proposal_boundary",
            "status": "PASS" if not boundary_violations else "FAIL",
            "details": boundary_violations,
        },
    ]


def validate_advisory_proposal(
    proposal: dict[str, Any] | None,
    validated_contract_artifact: dict[str, Any] | None,
    *,
    validated_at: str = VALIDATED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    contract, validation_result, contract_unknowns = _extract_validated_contract(validated_contract_artifact)
    errors = list(load_errors or [])
    schema_violations = _schema_violations(proposal)
    reference_violations = _contract_reference_violations(proposal, contract, validation_result)
    boundary_violations = _boundary_violations(proposal, contract)
    if contract_unknowns:
        errors.extend(contract_unknowns)
    status = _status(errors, schema_violations, reference_violations, boundary_violations)
    if status == FAIL_CLOSED and not errors:
        errors.append("proposal validation failed closed")
    proposal_hash = canonical_hash(proposal) if isinstance(proposal, dict) else UNKNOWN
    linked_contract_hash = canonical_hash(contract) if isinstance(contract, dict) else UNKNOWN
    result = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "validated_at": str(validated_at),
        "proposal_validation_status": status,
        "proposal_id": str(proposal.get("proposal_id", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "proposal_hash": proposal_hash,
        "linked_contract_id": str(proposal.get("linked_contract_id", UNKNOWN)) if isinstance(proposal, dict) else UNKNOWN,
        "linked_contract_hash": linked_contract_hash,
        "proposal_scope_valid": bool(status == VALID),
        "proposal_boundary_valid": bool(status == VALID),
        "proposal_replay_safe": bool(isinstance(proposal, dict) and proposal.get("replay_safe") is True),
        "proposal_advisory_only": bool(isinstance(proposal, dict) and proposal.get("advisory_only") is True),
        "violations": sorted(set(errors + schema_violations + reference_violations + boundary_violations)),
        "warnings": [],
        "unknowns": sorted(set(errors)),
        "evidence": _evidence(schema_violations, reference_violations, boundary_violations),
        "governance_guarantees": {
            "execution_authority": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
            "semantic_reasoning": False,
        },
        "validation_constraints": {
            "explicit_fields_only": True,
            "hidden_inference": False,
            "proposal_repair": False,
            "proposal_execution": False,
            "worker_task_created": False,
        },
    }
    result["validation_result_hash"] = canonical_hash(_hash_input(result))
    return result


def write_proposal_validation_result(result: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_advisory_proposal_validation(
    *,
    proposal_path: str | Path | None = None,
    contract_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    proposal, proposal_errors, proposal_status = _load_json_object(proposal_path, "proposal")
    contract, contract_errors, contract_status = _load_json_object(contract_path, "contract")
    load_errors = []
    if proposal_status == FAIL_CLOSED:
        load_errors.extend(proposal_errors)
    if contract_status == FAIL_CLOSED:
        load_errors.extend(contract_errors)
    result_artifact = validate_advisory_proposal(proposal, contract, load_errors=load_errors)
    result = {
        "command": "aigol moc validate-proposal",
        "proposal_path": str(proposal_path or ""),
        "contract_path": str(contract_path or ""),
        "advisory_proposal_validation_result": result_artifact,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "proposal_repair_added": False,
        "proposal_execution_added": False,
    }
    if output_path:
        result["output"] = write_proposal_validation_result(result_artifact, output_path)
    return result


def render_advisory_proposal_validation_summary(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Proposal Validation Status",
            f"  {result.get('proposal_validation_status')}",
            "Proposal",
            f"  proposal_id: {result.get('proposal_id')}",
            f"  proposal_hash: {result.get('proposal_hash')}",
            "Contract Linkage",
            f"  linked_contract_id: {result.get('linked_contract_id')}",
            f"  linked_contract_hash: {result.get('linked_contract_hash')}",
            "Boundary",
            f"  proposal_boundary_valid: {result.get('proposal_boundary_valid')}",
            f"  advisory_only: {result.get('proposal_advisory_only')}",
            f"  replay_safe: {result.get('proposal_replay_safe')}",
            "Violations",
            f"  {json.dumps(result.get('violations', []), sort_keys=True)}",
            "Governance Guarantees",
            "  execution_authority: false",
            "  worker_dispatch: false",
            "  provider_activation: false",
            "  orchestration_authority: false",
            "  semantic_reasoning: false",
            "  governance_mutation: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "FAIL_CLOSED",
    "INVALID_BOUNDARY",
    "INVALID_CONTRACT_REFERENCE",
    "INVALID_SCHEMA",
    "UNKNOWN_INSUFFICIENT_EVIDENCE",
    "VALID",
    "inspect_advisory_proposal_validation",
    "render_advisory_proposal_validation_summary",
    "validate_advisory_proposal",
    "write_proposal_validation_result",
]
