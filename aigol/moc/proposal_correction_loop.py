"""MOC V1 governed proposal correction feedback.

This module creates deterministic correction feedback from explicit proposal
validation evidence. AiGOL emits rejection evidence only; it does not repair
proposals, call an LLM, execute, dispatch, activate providers, infer hidden
meaning, mutate governance, or create hidden continuation.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_PROPOSAL_CORRECTION_FEEDBACK"
SCHEMA_VERSION = "1.0"
CREATED_AT = "1970-01-01T00:00:00Z"
CORRECTION_REQUIRED = "CORRECTION_REQUIRED"
CORRECTION_LIMIT_REACHED = "CORRECTION_LIMIT_REACHED"
PROPOSAL_VALID = "PROPOSAL_VALID"
FAIL_CLOSED = "FAIL_CLOSED"
UNKNOWN = "UNKNOWN"

VALIDATION_ARTIFACT_TYPE = "MOC_V1_ADVISORY_PROPOSAL_VALIDATION_RESULT"

FORBIDDEN_NEXT_STEPS = (
    "execute_proposal",
    "dispatch_worker",
    "activate_provider",
    "self_authorize",
    "bypass_human_approval",
    "mutate_governance",
    "create_hidden_continuation",
    "recursive_orchestration",
    "infer_hidden_meaning",
    "repair_inside_aigol",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(feedback: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(feedback)
    safe.pop("correction_feedback_hash", None)
    return safe


def _load_validation_result(input_path: str | Path | None) -> tuple[dict[str, Any] | None, list[str]]:
    if input_path is None or not str(input_path).strip():
        return None, ["validation result path missing"]
    path = Path(input_path)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"malformed validation result JSON: {type(exc).__name__}"]
    if not isinstance(loaded, dict):
        return None, ["validation result must be a JSON object"]
    if isinstance(loaded.get("advisory_proposal_validation_result"), dict):
        return _canonical_copy(loaded["advisory_proposal_validation_result"]), []
    return loaded, []


def _safe_attempt(value: Any, label: str) -> tuple[int | None, list[str]]:
    try:
        parsed = int(value)
    except Exception:
        return None, [f"{label} must be an integer"]
    if parsed < 1:
        return None, [f"{label} must be >= 1"]
    return parsed, []


def _validation_hash(validation_result: dict[str, Any] | None) -> str:
    if not isinstance(validation_result, dict):
        return UNKNOWN
    value = validation_result.get("validation_result_hash")
    if isinstance(value, str) and value.strip():
        return value
    return canonical_hash(validation_result)


def _status(validation_result: dict[str, Any] | None, attempt: int | None, max_attempts: int | None, errors: list[str]) -> str:
    if errors or not isinstance(validation_result, dict) or attempt is None or max_attempts is None:
        return FAIL_CLOSED
    if validation_result.get("proposal_validation_status") == "VALID":
        return PROPOSAL_VALID
    if attempt >= max_attempts:
        return CORRECTION_LIMIT_REACHED
    return CORRECTION_REQUIRED


def _required_corrections(validation_result: dict[str, Any] | None, errors: list[str]) -> list[str]:
    if errors:
        return ["provide valid proposal validation evidence"]
    if not isinstance(validation_result, dict):
        return ["provide explicit proposal validation result"]
    violations = validation_result.get("violations", [])
    if isinstance(violations, list) and violations:
        return [f"correct explicit violation: {violation}" for violation in violations]
    if validation_result.get("proposal_validation_status") == "VALID":
        return []
    return ["produce a revised advisory proposal that satisfies the proposal validation result"]


def _rejection_reason(status: str, validation_result: dict[str, Any] | None, errors: list[str]) -> str:
    if status == PROPOSAL_VALID:
        return "proposal validation status is VALID"
    if status == CORRECTION_LIMIT_REACHED:
        return "correction attempt limit reached"
    if errors:
        return "; ".join(errors)
    if isinstance(validation_result, dict):
        return f"proposal validation status is {validation_result.get('proposal_validation_status', UNKNOWN)}"
    return "proposal validation evidence unavailable"


def _llm_instruction_payload(
    *,
    rejection_reason: str,
    violations: list[str],
    required_corrections: list[str],
) -> dict[str, Any]:
    return {
        "rejection_summary": rejection_reason,
        "explicit_violations": violations,
        "required_corrections": required_corrections,
        "forbidden_actions": list(FORBIDDEN_NEXT_STEPS),
        "required_reminders": [
            "output must remain advisory_only=true",
            "output must remain replay_safe=true",
            "proposal does not equal execution",
            "do not request execution, dispatch, provider activation, governance mutation, or hidden continuation",
        ],
        "safe_for_llm_correction": True,
        "aigol_repaired_proposal": False,
        "llm_called_by_aigol": False,
    }


def build_proposal_correction_feedback(
    validation_result: dict[str, Any] | None,
    *,
    attempt_number: int | str,
    max_attempts: int | str,
    created_at: str = CREATED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    attempt, attempt_errors = _safe_attempt(attempt_number, "attempt_number")
    maximum, max_errors = _safe_attempt(max_attempts, "max_attempts")
    errors = list(load_errors or []) + attempt_errors + max_errors
    if isinstance(validation_result, dict) and validation_result.get("artifact_type") != VALIDATION_ARTIFACT_TYPE:
        errors.append("validation result artifact_type is not MOC_V1_ADVISORY_PROPOSAL_VALIDATION_RESULT")
    status = _status(validation_result, attempt, maximum, errors)
    violations = list(validation_result.get("violations", [])) if isinstance(validation_result, dict) and isinstance(validation_result.get("violations"), list) else []
    required_corrections = _required_corrections(validation_result, errors)
    rejection_reason = _rejection_reason(status, validation_result, errors)
    validation_hash = _validation_hash(validation_result)
    proposal_id = str(validation_result.get("proposal_id", UNKNOWN)) if isinstance(validation_result, dict) else UNKNOWN
    feedback = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "created_at": str(created_at),
        "correction_status": status,
        "attempt_number": attempt if attempt is not None else UNKNOWN,
        "max_attempts": maximum if maximum is not None else UNKNOWN,
        "linked_proposal_id": proposal_id,
        "linked_validation_result_hash": validation_hash,
        "rejection_reason": rejection_reason,
        "violations": violations,
        "required_corrections": required_corrections,
        "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS),
        "llm_instruction_payload": _llm_instruction_payload(
            rejection_reason=rejection_reason,
            violations=violations,
            required_corrections=required_corrections,
        ),
        "replay_refs": {
            "proposal_hash": validation_result.get("proposal_hash", UNKNOWN) if isinstance(validation_result, dict) else UNKNOWN,
            "proposal_validation_result_hash": validation_hash,
        },
        "lineage_refs": {
            "proposal_id": proposal_id,
            "linked_contract_id": validation_result.get("linked_contract_id", UNKNOWN) if isinstance(validation_result, dict) else UNKNOWN,
            "linked_contract_hash": validation_result.get("linked_contract_hash", UNKNOWN) if isinstance(validation_result, dict) else UNKNOWN,
        },
        "unknowns": sorted(set(errors)),
        "governance_guarantees": {
            "proposal_execution": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "self_authorization": False,
            "human_approval_bypass": False,
            "governance_mutation": False,
            "autonomous_execution": False,
            "hidden_continuation": False,
            "llm_called": False,
            "aigol_repaired_proposal": False,
            "hidden_inference": False,
        },
    }
    feedback["correction_feedback_hash"] = canonical_hash(_hash_input(feedback))
    return feedback


def write_correction_feedback(feedback: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(feedback, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_proposal_correction_feedback(
    *,
    validation_result_path: str | Path | None = None,
    attempt_number: int | str = 1,
    max_attempts: int | str = 3,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    validation_result, load_errors = _load_validation_result(validation_result_path)
    feedback = build_proposal_correction_feedback(
        validation_result,
        attempt_number=attempt_number,
        max_attempts=max_attempts,
        load_errors=load_errors,
    )
    result = {
        "command": "aigol moc correction-feedback",
        "validation_result_path": str(validation_result_path or ""),
        "proposal_correction_feedback": feedback,
        "read_only": True,
        "execution_authority_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "llm_call_added": False,
        "proposal_mutation_added": False,
        "proposal_repair_added": False,
        "hidden_inference_added": False,
        "hidden_continuation_added": False,
    }
    if output_path:
        result["output"] = write_correction_feedback(feedback, output_path)
    return result


def render_proposal_correction_feedback_summary(feedback: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Correction Status",
            f"  {feedback.get('correction_status')}",
            "Attempt",
            f"  {feedback.get('attempt_number')} / {feedback.get('max_attempts')}",
            "Proposal",
            f"  linked_proposal_id: {feedback.get('linked_proposal_id')}",
            f"  linked_validation_result_hash: {feedback.get('linked_validation_result_hash')}",
            "Rejection",
            f"  {feedback.get('rejection_reason')}",
            "Required Corrections",
            f"  {json.dumps(feedback.get('required_corrections', []), sort_keys=True)}",
            "Forbidden Next Steps",
            f"  {json.dumps(feedback.get('forbidden_next_steps', []), sort_keys=True)}",
            "Governance Guarantees",
            "  proposal_execution: false",
            "  worker_dispatch: false",
            "  provider_activation: false",
            "  llm_called: false",
            "  aigol_repaired_proposal: false",
            "  hidden_continuation: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "CORRECTION_LIMIT_REACHED",
    "CORRECTION_REQUIRED",
    "FAIL_CLOSED",
    "FORBIDDEN_NEXT_STEPS",
    "PROPOSAL_VALID",
    "build_proposal_correction_feedback",
    "inspect_proposal_correction_feedback",
    "render_proposal_correction_feedback_summary",
    "write_correction_feedback",
]
