"""MOC V1 advisory semantic contract generation.

This module creates advisory-only semantic contract drafts from explicit input
fields and immediately validates them. It does not execute, dispatch, activate
providers, infer hidden meaning, repair contracts, mutate governance, or start
runtime cognition loops.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.moc.contract_validation import VALID, validate_semantic_contract

ARTIFACT_TYPE = "MOC_V1_ADVISORY_CONTRACT_GENERATION_RESULT"
SCHEMA_VERSION = "1.0"
GENERATED_AT = "1970-01-01T00:00:00Z"
GENERATED_VALID = "GENERATED_VALID"
GENERATED_INVALID = "GENERATED_INVALID"
INVALID_INPUT = "INVALID_INPUT"
FAIL_CLOSED = "FAIL_CLOSED"
UNKNOWN = "UNKNOWN"

REQUIRED_INPUT_FIELDS = (
    "intent_summary",
    "scope",
    "risk_level",
    "mutation_classification",
    "governance_anchors",
    "allowed_actions",
    "forbidden_actions",
    "required_approvals",
    "expected_outputs",
    "deterministic_constraints",
)

DEFAULT_FORBIDDEN_ACTIONS = (
    "execute_task",
    "dispatch_worker",
    "activate_provider",
    "mutate_governance",
    "hidden_continuation",
    "recursive_orchestration",
    "self_authorize",
)

DEFAULT_REQUIRED_APPROVALS = ("human_review",)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _load_generation_input(input_path: str | Path | None) -> tuple[dict[str, Any] | None, list[str], str]:
    if input_path is None or not str(input_path).strip():
        return None, ["generation input path missing"], FAIL_CLOSED
    path = Path(input_path)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"malformed JSON: {type(exc).__name__}"], FAIL_CLOSED
    if not isinstance(loaded, dict):
        return None, ["generation input must be a JSON object"], FAIL_CLOSED
    return loaded, [], UNKNOWN


def _normalize_list(value: Any, defaults: tuple[str, ...] = ()) -> list[Any]:
    if not isinstance(value, list):
        return list(defaults)
    combined = list(value)
    for item in defaults:
        if item not in combined:
            combined.append(item)
    return combined


def _missing_input_fields(generation_input: dict[str, Any] | None) -> list[str]:
    if not isinstance(generation_input, dict):
        return list(REQUIRED_INPUT_FIELDS)
    return [field for field in REQUIRED_INPUT_FIELDS if field not in generation_input]


def _build_contract(generation_input: dict[str, Any]) -> dict[str, Any]:
    explicit = _canonical_copy(generation_input)
    intent_id = "moc-intent-" + canonical_hash(
        {field: explicit.get(field) for field in REQUIRED_INPUT_FIELDS}
    ).removeprefix("sha256:")[:24]
    return {
        "intent_id": intent_id,
        "intent_summary": explicit.get("intent_summary"),
        "scope": explicit.get("scope"),
        "risk_level": explicit.get("risk_level"),
        "mutation_classification": explicit.get("mutation_classification"),
        "governance_anchors": _canonical_copy(explicit.get("governance_anchors")),
        "allowed_actions": _normalize_list(explicit.get("allowed_actions")),
        "forbidden_actions": _normalize_list(explicit.get("forbidden_actions"), DEFAULT_FORBIDDEN_ACTIONS),
        "required_approvals": _normalize_list(explicit.get("required_approvals"), DEFAULT_REQUIRED_APPROVALS),
        "expected_outputs": _normalize_list(explicit.get("expected_outputs")),
        "advisory_only": True,
        "replay_safe": True,
        "deterministic_constraints": _canonical_copy(explicit.get("deterministic_constraints")),
    }


def _result_hash_input(result: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(result)
    safe.pop("generation_result_hash", None)
    return safe


def _generation_status(contract: dict[str, Any] | None, validation_result: dict[str, Any], input_errors: list[str]) -> str:
    if input_errors:
        return FAIL_CLOSED
    if contract is None:
        return INVALID_INPUT
    if validation_result.get("validation_status") == VALID:
        return GENERATED_VALID
    return GENERATED_INVALID


def generate_advisory_contract(
    generation_input: dict[str, Any] | None,
    *,
    generated_at: str = GENERATED_AT,
    input_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(input_errors or [])
    missing = _missing_input_fields(generation_input)
    if missing:
        errors.extend(f"missing required generation input: {field}" for field in missing)
    contract = None if errors or not isinstance(generation_input, dict) else _build_contract(generation_input)
    validation_result = validate_semantic_contract(
        contract,
        load_errors=errors,
        load_status=FAIL_CLOSED if errors else UNKNOWN,
    )
    status = _generation_status(contract, validation_result, errors)
    result = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "generation_status": status,
        "intent_id": contract.get("intent_id", UNKNOWN) if isinstance(contract, dict) else UNKNOWN,
        "contract": contract if isinstance(contract, dict) else {},
        "contract_hash": canonical_hash(contract) if isinstance(contract, dict) else UNKNOWN,
        "validation_result": validation_result,
        "violations": sorted(set(errors + list(validation_result.get("violations", [])))),
        "warnings": [],
        "unknowns": sorted(set(errors)),
        "governance_guarantees": {
            "advisory_only": True,
            "replay_safe": True,
            "execution_authority": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "semantic_reasoning": False,
            "governance_mutation": False,
        },
        "generation_constraints": {
            "explicit_input_only": True,
            "hidden_inference": False,
            "contract_repair": False,
            "proposal_generation": False,
            "worker_task_created": False,
            "execution_triggered": False,
        },
    }
    result["generation_result_hash"] = canonical_hash(_result_hash_input(result))
    return result


def write_generation_result(result: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_advisory_contract_generation(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    generation_input, load_errors, load_status = _load_generation_input(input_path)
    result_artifact = generate_advisory_contract(
        generation_input,
        input_errors=load_errors if load_status == FAIL_CLOSED else [],
    )
    result = {
        "command": "aigol moc generate-contract",
        "input_path": str(input_path or ""),
        "advisory_contract_generation_result": result_artifact,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "contract_repair_added": False,
        "worker_task_created": False,
    }
    if output_path:
        result["output"] = write_generation_result(result_artifact, output_path)
    return result


def render_advisory_contract_generation_summary(result: dict[str, Any]) -> str:
    validation = result.get("validation_result", {}) if isinstance(result.get("validation_result"), dict) else {}
    return "\n".join(
        [
            "Generation Status",
            f"  {result.get('generation_status')}",
            "Contract",
            f"  intent_id: {result.get('intent_id')}",
            f"  contract_hash: {result.get('contract_hash')}",
            "Validation",
            f"  validation_status: {validation.get('validation_status')}",
            f"  schema_valid: {validation.get('schema_valid')}",
            f"  boundary_valid: {validation.get('boundary_valid')}",
            "Violations",
            f"  {json.dumps(result.get('violations', []), sort_keys=True)}",
            "Governance Guarantees",
            "  advisory_only: true",
            "  replay_safe: true",
            "  execution_authority: false",
            "  worker_dispatch: false",
            "  provider_activation: false",
            "  semantic_reasoning: false",
            "  governance_mutation: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "DEFAULT_FORBIDDEN_ACTIONS",
    "FAIL_CLOSED",
    "GENERATED_INVALID",
    "GENERATED_VALID",
    "INVALID_INPUT",
    "generate_advisory_contract",
    "inspect_advisory_contract_generation",
    "render_advisory_contract_generation_summary",
    "write_generation_result",
]
