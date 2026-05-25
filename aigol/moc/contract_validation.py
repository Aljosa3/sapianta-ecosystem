"""MOC V1 semantic contract validation.

This module validates explicit MOC V1 semantic contracts against the canonical
schema and boundary guarantees. It is validation-only: no execution, dispatch,
provider activation, proposal generation, hidden inference, mutation, repair, or
runtime cognition loop is introduced.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

try:  # pragma: no cover - exercised implicitly when jsonschema is installed.
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover - deterministic fallback covers absence.
    Draft202012Validator = None  # type: ignore[assignment]

ARTIFACT_TYPE = "MOC_V1_CONTRACT_VALIDATION_RESULT"
SCHEMA_VERSION = "1.0"
VALID = "VALID"
INVALID_SCHEMA = "INVALID_SCHEMA"
INVALID_BOUNDARY = "INVALID_BOUNDARY"
UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"
FAIL_CLOSED = "FAIL_CLOSED"
UNKNOWN = "UNKNOWN"
VALIDATED_AT = "1970-01-01T00:00:00Z"

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "semantic_contract.schema.json"

FORBIDDEN_AUTHORITY_FIELDS = {
    "execution_authority",
    "dispatch_authority",
    "provider_activation",
    "autonomous_continuation",
    "orchestration_authority",
    "mutation_authority",
    "governance_mutation",
    "hidden_continuation",
    "recursive_worker_spawn",
    "self_authorization",
    "semantic_repair",
    "authority_issuance",
}

REQUIRED_DETERMINISTIC_CONSTRAINTS = {
    "no_hidden_inference",
    "no_self_dispatch",
    "no_runtime_mutation",
    "no_autonomous_continuation",
    "no_provider_activation",
}


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _result_hash_input(result: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(result)
    safe.pop("validation_result_hash", None)
    return safe


def _load_schema() -> dict[str, Any]:
    try:
        loaded = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _load_contract(input_path: str | Path | None) -> tuple[dict[str, Any] | None, list[str], str]:
    if input_path is None or not str(input_path).strip():
        return None, ["contract input path missing"], UNKNOWN_INSUFFICIENT_EVIDENCE
    path = Path(input_path)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"malformed JSON: {type(exc).__name__}"], FAIL_CLOSED
    if not isinstance(loaded, dict):
        return None, ["semantic contract must be a JSON object"], FAIL_CLOSED
    return loaded, [], UNKNOWN


def _schema_errors_with_jsonschema(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    if Draft202012Validator is None:
        return []
    validator = Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(contract), key=lambda item: (list(item.path), item.message)):
        path = ".".join(str(part) for part in error.path) or "$"
        errors.append(f"{path}: {error.message}")
    return errors


def _fallback_schema_errors(contract: dict[str, Any]) -> list[str]:
    required = [
        "intent_id",
        "intent_summary",
        "scope",
        "risk_level",
        "mutation_classification",
        "governance_anchors",
        "allowed_actions",
        "forbidden_actions",
        "required_approvals",
        "expected_outputs",
        "advisory_only",
        "replay_safe",
        "deterministic_constraints",
    ]
    errors: list[str] = []
    for field in required:
        if field not in contract:
            errors.append(f"$: '{field}' is a required property")
    allowed = set(required)
    for field in sorted(set(contract) - allowed):
        errors.append(f"$: Additional properties are not allowed ('{field}' was unexpected)")
    if contract.get("risk_level") not in {"low", "medium", "high", "critical"}:
        errors.append("risk_level: invalid enum")
    if contract.get("mutation_classification") not in {"cosmetic", "parametric", "structural"}:
        errors.append("mutation_classification: invalid enum")
    if contract.get("advisory_only") is not True:
        errors.append("advisory_only: True was expected")
    if contract.get("replay_safe") is not True:
        errors.append("replay_safe: True was expected")
    for field in ("governance_anchors", "forbidden_actions", "required_approvals", "expected_outputs"):
        value = contract.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{field}: non-empty array required")
    constraints = contract.get("deterministic_constraints")
    if not isinstance(constraints, dict):
        errors.append("deterministic_constraints: object required")
    else:
        for key in sorted(REQUIRED_DETERMINISTIC_CONSTRAINTS):
            if constraints.get(key) is not True:
                errors.append(f"deterministic_constraints.{key}: True was expected")
        for key in sorted(set(constraints) - REQUIRED_DETERMINISTIC_CONSTRAINTS):
            errors.append(f"deterministic_constraints: Additional properties are not allowed ('{key}' was unexpected)")
    return errors


def _schema_errors(contract: dict[str, Any]) -> list[str]:
    schema = _load_schema()
    if schema and Draft202012Validator is not None:
        return _schema_errors_with_jsonschema(contract, schema)
    return _fallback_schema_errors(contract)


def _scan_forbidden_fields(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = f"{path}.{key}"
            if key in FORBIDDEN_AUTHORITY_FIELDS:
                findings.append(f"forbidden authority field present: {item_path}")
            findings.extend(_scan_forbidden_fields(item, item_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_scan_forbidden_fields(item, f"{path}[{index}]"))
    return findings


def _boundary_violations(contract: dict[str, Any]) -> list[str]:
    violations = _scan_forbidden_fields(contract)
    if contract.get("advisory_only") is not True:
        violations.append("advisory_only must be true")
    if contract.get("replay_safe") is not True:
        violations.append("replay_safe must be true")
    required_approvals = contract.get("required_approvals")
    if not isinstance(required_approvals, list) or not required_approvals:
        violations.append("required_approvals must be explicit")
    forbidden_actions = contract.get("forbidden_actions")
    if not isinstance(forbidden_actions, list) or not forbidden_actions:
        violations.append("forbidden_actions must be explicit")
    constraints = contract.get("deterministic_constraints")
    if not isinstance(constraints, dict):
        violations.append("deterministic_constraints must be present")
    else:
        for key in sorted(REQUIRED_DETERMINISTIC_CONSTRAINTS):
            if constraints.get(key) is not True:
                violations.append(f"deterministic_constraints.{key} must be true")
    return sorted(set(violations))


def _status(
    *,
    contract: dict[str, Any] | None,
    load_status: str,
    schema_errors: list[str],
    boundary_violations: list[str],
) -> str:
    if load_status == FAIL_CLOSED:
        return FAIL_CLOSED
    if contract is None:
        return UNKNOWN_INSUFFICIENT_EVIDENCE
    if boundary_violations:
        return INVALID_BOUNDARY
    if schema_errors:
        return INVALID_SCHEMA
    return VALID


def _evidence(contract: dict[str, Any] | None, schema_errors: list[str], boundary_violations: list[str]) -> list[dict[str, Any]]:
    if contract is None:
        return [{"check": "contract_loaded", "status": "UNKNOWN", "details": ["no contract object available"]}]
    return [
        {
            "check": "schema_conformance",
            "status": "PASS" if not schema_errors else "FAIL",
            "details": schema_errors,
        },
        {
            "check": "boundary_guarantees",
            "status": "PASS" if not boundary_violations else "FAIL",
            "details": boundary_violations,
        },
        {
            "check": "advisory_only",
            "status": "PASS" if contract.get("advisory_only") is True else "FAIL",
            "details": [],
        },
        {
            "check": "replay_safe",
            "status": "PASS" if contract.get("replay_safe") is True else "FAIL",
            "details": [],
        },
    ]


def validate_semantic_contract(
    contract: dict[str, Any] | None,
    *,
    validated_at: str = VALIDATED_AT,
    load_errors: list[str] | None = None,
    load_status: str = UNKNOWN,
) -> dict[str, Any]:
    schema_errors = _schema_errors(contract) if isinstance(contract, dict) else []
    boundary_violations = _boundary_violations(contract) if isinstance(contract, dict) else []
    unknowns = list(load_errors or [])
    status = _status(
        contract=contract,
        load_status=load_status,
        schema_errors=schema_errors,
        boundary_violations=boundary_violations,
    )
    violations = sorted(set(schema_errors + boundary_violations + ([] if status != FAIL_CLOSED else unknowns)))
    result = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "validated_at": str(validated_at),
        "validation_status": status,
        "contract_id": str(contract.get("intent_id", UNKNOWN)) if isinstance(contract, dict) else UNKNOWN,
        "contract_hash": canonical_hash(contract) if isinstance(contract, dict) else UNKNOWN,
        "schema_valid": bool(isinstance(contract, dict) and not schema_errors),
        "boundary_valid": bool(isinstance(contract, dict) and not boundary_violations),
        "replay_safe": bool(isinstance(contract, dict) and contract.get("replay_safe") is True),
        "advisory_only": bool(isinstance(contract, dict) and contract.get("advisory_only") is True),
        "violations": violations,
        "warnings": [],
        "unknowns": sorted(set(unknowns)),
        "evidence": _evidence(contract, schema_errors, boundary_violations),
        "governance_guarantees": {
            "execution_authority": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "semantic_reasoning": False,
            "governance_mutation": False,
        },
    }
    result["validation_result_hash"] = canonical_hash(_result_hash_input(result))
    return result


def write_validation_result(result: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_contract_validation(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    contract, load_errors, load_status = _load_contract(input_path)
    result_artifact = validate_semantic_contract(contract, load_errors=load_errors, load_status=load_status)
    result = {
        "command": "aigol moc validate-contract",
        "input_path": str(input_path or ""),
        "contract_validation_result": result_artifact,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "contract_repair_added": False,
    }
    if output_path:
        result["output"] = write_validation_result(result_artifact, output_path)
    return result


def render_contract_validation_summary(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Validation Status",
            f"  {result.get('validation_status')}",
            "Contract",
            f"  contract_id: {result.get('contract_id')}",
            f"  contract_hash: {result.get('contract_hash')}",
            "Schema",
            f"  schema_valid: {result.get('schema_valid')}",
            "Boundary",
            f"  boundary_valid: {result.get('boundary_valid')}",
            f"  advisory_only: {result.get('advisory_only')}",
            f"  replay_safe: {result.get('replay_safe')}",
            "Violations",
            f"  {json.dumps(result.get('violations', []), sort_keys=True)}",
            "Governance Guarantees",
            "  execution_authority: false",
            "  orchestration_authority: false",
            "  worker_dispatch: false",
            "  provider_activation: false",
            "  semantic_reasoning: false",
            "  governance_mutation: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "FAIL_CLOSED",
    "INVALID_BOUNDARY",
    "INVALID_SCHEMA",
    "UNKNOWN_INSUFFICIENT_EVIDENCE",
    "VALID",
    "inspect_contract_validation",
    "render_contract_validation_summary",
    "validate_semantic_contract",
    "write_validation_result",
]
