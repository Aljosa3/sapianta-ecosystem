"""MOC V1 governed return interpretation.

This module interprets explicit runtime dispatch, provider gate, and optional
return evidence into bounded governance outcome classifications. It is
interpretation-only: no execution, provider activation, retry, repair, or
automatic next-task generation is performed.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_GOVERNED_RETURN_INTERPRETATION"
SCHEMA_VERSION = "1.0"
INTERPRETED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

RUNTIME_DISPATCH_ARTIFACT_TYPE = "MOC_V1_RUNTIME_DISPATCH_EVENT"
PROVIDER_GATE_ARTIFACT_TYPE = "MOC_V1_WORKER_PROVIDER_EXECUTION_GATE"

INTERPRETED = "INTERPRETED"
INTERPRETED_WITH_WARNINGS = "INTERPRETED_WITH_WARNINGS"
INVALID_RETURN_EVIDENCE = "INVALID_RETURN_EVIDENCE"
UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"
FAIL_CLOSED = "FAIL_CLOSED"

DISPATCH_RECORDED_ONLY = "DISPATCH_RECORDED_ONLY"
PROVIDER_GATE_ELIGIBLE_ONLY = "PROVIDER_GATE_ELIGIBLE_ONLY"
EXECUTION_NOT_PERFORMED = "EXECUTION_NOT_PERFORMED"
EXECUTION_RESULT_PRESENT = "EXECUTION_RESULT_PRESENT"
EXECUTION_FAILED = "EXECUTION_FAILED"
UNKNOWN_OUTCOME = "UNKNOWN_OUTCOME"


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(interpretation: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(interpretation)
    safe.pop("interpretation_hash", None)
    return safe


def _load_json_object(
    path_value: str | Path | None,
    label: str,
    *,
    required: bool,
) -> tuple[dict[str, Any] | None, list[str]]:
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


def _list_value(value: Any) -> list[Any]:
    return _canonical_copy(value) if isinstance(value, list) else []


def _string_value(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return UNKNOWN


def _bool_value(source: dict[str, Any] | None, key: str, default: bool = False) -> bool:
    if not isinstance(source, dict):
        return default
    return source.get(key) is True


def _return_interpretation_id(
    runtime_dispatch: dict[str, Any] | None,
    provider_gate: dict[str, Any] | None,
    return_evidence: dict[str, Any] | None,
) -> str:
    return "moc-return-interpretation-" + canonical_hash(
        {
            "runtime_dispatch_hash": (
                _string_value(runtime_dispatch.get("runtime_dispatch_hash"))
                if isinstance(runtime_dispatch, dict)
                else UNKNOWN
            ),
            "provider_gate_hash": (
                _string_value(provider_gate.get("provider_gate_hash")) if isinstance(provider_gate, dict) else UNKNOWN
            ),
            "return_evidence_hash": canonical_hash(return_evidence or {}),
        }
    )


def _return_execution_completed(return_evidence: dict[str, Any] | None) -> bool:
    return _bool_value(return_evidence, "execution_completed", default=False)


def _return_result_present(return_evidence: dict[str, Any] | None) -> bool:
    if not isinstance(return_evidence, dict):
        return False
    if return_evidence.get("result_present") is True:
        return True
    return return_evidence.get("execution_result_present") is True


def _provider_execution_performed(provider_gate: dict[str, Any] | None, return_evidence: dict[str, Any] | None) -> bool:
    if _bool_value(return_evidence, "provider_execution_performed", default=False):
        return True
    return _bool_value(provider_gate, "provider_execution_performed", default=False)


def _outcome_classification(
    runtime_dispatch: dict[str, Any] | None,
    provider_gate: dict[str, Any] | None,
    return_evidence: dict[str, Any] | None,
) -> str:
    if not isinstance(runtime_dispatch, dict):
        return UNKNOWN_OUTCOME
    if _return_result_present(return_evidence):
        return EXECUTION_RESULT_PRESENT
    if _return_execution_completed(return_evidence) and not _return_result_present(return_evidence):
        return EXECUTION_FAILED
    if isinstance(return_evidence, dict) and return_evidence.get("execution_completed") is False and not _return_result_present(return_evidence):
        return EXECUTION_NOT_PERFORMED
    if isinstance(provider_gate, dict):
        return PROVIDER_GATE_ELIGIBLE_ONLY
    return DISPATCH_RECORDED_ONLY


def _governance_consequence(outcome: str) -> str:
    if outcome == DISPATCH_RECORDED_ONLY:
        return "runtime dispatch recorded; provider execution not evidenced"
    if outcome == PROVIDER_GATE_ELIGIBLE_ONLY:
        return "provider execution eligibility recorded; provider execution not evidenced"
    if outcome == EXECUTION_NOT_PERFORMED:
        return "execution not performed; human review required before any next action"
    if outcome == EXECUTION_RESULT_PRESENT:
        return "execution result evidence present; human review required for interpretation"
    if outcome == EXECUTION_FAILED:
        return "execution failure evidence present; human review required"
    return "outcome unknown; evidence insufficient"


def _next_step_recommendation(outcome: str) -> str:
    if outcome in {DISPATCH_RECORDED_ONLY, PROVIDER_GATE_ELIGIBLE_ONLY, EXECUTION_NOT_PERFORMED}:
        return "human_review_required_before_provider_execution"
    if outcome == EXECUTION_RESULT_PRESENT:
        return "human_review_required_before_accepting_result"
    if outcome == EXECUTION_FAILED:
        return "human_review_required_before_remediation"
    return "human_review_required_due_to_unknown_outcome"


def _drift_indicators(
    runtime_dispatch: dict[str, Any] | None,
    provider_gate: dict[str, Any] | None,
    return_evidence: dict[str, Any] | None,
) -> list[str]:
    indicators: list[str] = []
    if _provider_execution_performed(provider_gate, return_evidence):
        indicators.append("provider execution evidence present")
    if _return_result_present(return_evidence):
        indicators.append("execution result evidence present")
    if _bool_value(return_evidence, "automatic_retry", default=False):
        indicators.append("automatic retry claim present")
    if _bool_value(return_evidence, "automatic_next_task", default=False):
        indicators.append("automatic next-task claim present")
    if isinstance(provider_gate, dict) and provider_gate.get("runtime_dispatch_hash") != _string_value(runtime_dispatch.get("runtime_dispatch_hash")):
        indicators.append("provider gate runtime dispatch hash mismatch")
    return indicators


def _violations(
    runtime_dispatch: dict[str, Any] | None,
    provider_gate: dict[str, Any] | None,
    return_evidence: dict[str, Any] | None,
    load_errors: list[str],
) -> list[str]:
    violations = list(load_errors)
    if not isinstance(runtime_dispatch, dict):
        violations.append("runtime dispatch evidence missing")
        return sorted(set(violations))
    if runtime_dispatch.get("artifact_type") != RUNTIME_DISPATCH_ARTIFACT_TYPE:
        violations.append("runtime dispatch artifact_type invalid")
    if not _list_value(runtime_dispatch.get("lineage_refs")):
        violations.append("lineage refs must exist")
    if not _list_value(runtime_dispatch.get("replay_refs")):
        violations.append("replay refs must exist")
    if isinstance(provider_gate, dict):
        if provider_gate.get("artifact_type") != PROVIDER_GATE_ARTIFACT_TYPE:
            violations.append("provider gate artifact_type invalid")
        if provider_gate.get("runtime_dispatch_hash") != _string_value(runtime_dispatch.get("runtime_dispatch_hash")):
            violations.append("provider gate runtime dispatch hash mismatch")
        if not _list_value(provider_gate.get("lineage_refs")):
            violations.append("provider gate lineage refs must exist")
        if not _list_value(provider_gate.get("replay_refs")):
            violations.append("provider gate replay refs must exist")
    if isinstance(return_evidence, dict):
        if return_evidence.get("automatic_retry") is True:
            violations.append("return evidence automatic_retry must remain false")
        if return_evidence.get("automatic_next_task") is True:
            violations.append("return evidence automatic_next_task must remain false")
        if return_evidence.get("result_repaired") is True:
            violations.append("return evidence result_repaired must remain false")
    return sorted(set(violations))


def _status(violations: list[str], outcome: str, provider_gate: dict[str, Any] | None, return_evidence: dict[str, Any] | None) -> str:
    fail_closed_fragments = (
        "path missing",
        "malformed",
        "must be a JSON object",
        "missing",
        "refs must exist",
        "must remain false",
        "hash mismatch",
    )
    if any(any(fragment in violation for fragment in fail_closed_fragments) for violation in violations):
        return FAIL_CLOSED
    if violations:
        return INVALID_RETURN_EVIDENCE
    if outcome == UNKNOWN_OUTCOME:
        return UNKNOWN_INSUFFICIENT_EVIDENCE
    if provider_gate is None and return_evidence is None:
        return INTERPRETED
    return INTERPRETED_WITH_WARNINGS if outcome in {PROVIDER_GATE_ELIGIBLE_ONLY, EXECUTION_NOT_PERFORMED} else INTERPRETED


def interpret_governed_return(
    runtime_dispatch: dict[str, Any] | None,
    provider_gate: dict[str, Any] | None = None,
    return_evidence: dict[str, Any] | None = None,
    *,
    interpreted_at: str = INTERPRETED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(load_errors or [])
    violations = _violations(runtime_dispatch, provider_gate, return_evidence, errors)
    outcome = _outcome_classification(runtime_dispatch, provider_gate, return_evidence)
    status = _status(violations, outcome, provider_gate, return_evidence)
    safe_runtime = runtime_dispatch if isinstance(runtime_dispatch, dict) else {}
    safe_gate = provider_gate if isinstance(provider_gate, dict) else {}
    execution_completed = _return_execution_completed(return_evidence)
    result_present = _return_result_present(return_evidence)
    provider_execution_performed = _provider_execution_performed(provider_gate, return_evidence)
    interpretation = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "interpreted_at": str(interpreted_at),
        "interpretation_status": status,
        "return_interpretation_id": _return_interpretation_id(runtime_dispatch, provider_gate, return_evidence),
        "runtime_dispatch_hash": _string_value(safe_runtime.get("runtime_dispatch_hash")),
        "provider_gate_hash": _string_value(safe_gate.get("provider_gate_hash")),
        "worker_package_id": _string_value(safe_runtime.get("worker_package_id") or safe_gate.get("worker_package_id")),
        "proposal_id": _string_value(safe_runtime.get("proposal_id") or safe_gate.get("proposal_id")),
        "proposal_hash": _string_value(safe_runtime.get("proposal_hash") or safe_gate.get("proposal_hash")),
        "linked_contract_id": _string_value(safe_runtime.get("linked_contract_id") or safe_gate.get("linked_contract_id")),
        "linked_contract_hash": _string_value(safe_runtime.get("linked_contract_hash") or safe_gate.get("linked_contract_hash")),
        "outcome_classification": outcome,
        "execution_completed": execution_completed,
        "provider_execution_performed": provider_execution_performed,
        "result_present": result_present,
        "governance_consequence": _governance_consequence(outcome),
        "drift_indicators": _drift_indicators(runtime_dispatch, provider_gate, return_evidence),
        "required_human_review": True,
        "next_step_recommendation": _next_step_recommendation(outcome),
        "interpretation_violations": violations,
        "warnings": [
            "return interpretation is interpretation-only",
            "return interpretation does not execute, retry, repair, or generate new tasks",
            "human review remains required",
        ],
        "unknowns": [violation for violation in violations if "missing" in violation or "UNKNOWN" in violation],
        "lineage_refs": _list_value(safe_runtime.get("lineage_refs") or safe_gate.get("lineage_refs")),
        "approval_refs": _list_value(safe_runtime.get("approval_refs") or safe_gate.get("approval_refs")),
        "replay_refs": _list_value(safe_runtime.get("replay_refs") or safe_gate.get("replay_refs")),
        "governance_guarantees": {
            "interpretation_only": True,
            "execution_authority": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "automatic_retry": False,
            "automatic_next_task": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
        },
    }
    interpretation["interpretation_hash"] = canonical_hash(_hash_input(interpretation))
    return interpretation


def write_governed_return_interpretation(interpretation: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(interpretation, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_governed_return_interpretation(
    *,
    runtime_dispatch_path: str | Path | None = None,
    provider_gate_path: str | Path | None = None,
    return_evidence_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    runtime_dispatch, runtime_errors = _load_json_object(runtime_dispatch_path, "runtime dispatch", required=True)
    provider_gate, provider_errors = _load_json_object(provider_gate_path, "provider gate", required=False)
    return_evidence, return_errors = _load_json_object(return_evidence_path, "return evidence", required=False)
    interpretation = interpret_governed_return(
        runtime_dispatch,
        provider_gate,
        return_evidence,
        load_errors=runtime_errors + provider_errors + return_errors,
    )
    result = {
        "command": "aigol moc interpret-return",
        "runtime_dispatch_path": str(runtime_dispatch_path or ""),
        "provider_gate_path": str(provider_gate_path or ""),
        "return_evidence_path": str(return_evidence_path or ""),
        "governed_return_interpretation": interpretation,
        "interpretation_only": True,
        "execution_authority_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "automatic_retry_added": False,
        "automatic_next_task_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "hidden_continuation_added": False,
        "result_repair_added": False,
    }
    if output_path:
        result["output"] = write_governed_return_interpretation(interpretation, output_path)
    return result


def render_governed_return_interpretation_summary(interpretation: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Governed Return Interpretation",
            f"  interpretation_status: {interpretation.get('interpretation_status')}",
            f"  outcome_classification: {interpretation.get('outcome_classification')}",
            f"  runtime_dispatch_hash: {interpretation.get('runtime_dispatch_hash')}",
            f"  provider_gate_hash: {interpretation.get('provider_gate_hash')}",
            "Boundary",
            "  required_human_review: true",
            "  automatic_retry: false",
            "  automatic_next_task: false",
            "  provider_activation: false",
            "  worker_dispatch: false",
            "Replay",
            f"  lineage_refs: {len(interpretation.get('lineage_refs', []))}",
            f"  approval_refs: {len(interpretation.get('approval_refs', []))}",
            f"  replay_refs: {len(interpretation.get('replay_refs', []))}",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "DISPATCH_RECORDED_ONLY",
    "EXECUTION_FAILED",
    "EXECUTION_NOT_PERFORMED",
    "EXECUTION_RESULT_PRESENT",
    "FAIL_CLOSED",
    "INTERPRETED",
    "INTERPRETED_WITH_WARNINGS",
    "PROVIDER_GATE_ELIGIBLE_ONLY",
    "UNKNOWN_INSUFFICIENT_EVIDENCE",
    "UNKNOWN_OUTCOME",
    "inspect_governed_return_interpretation",
    "interpret_governed_return",
    "render_governed_return_interpretation_summary",
    "write_governed_return_interpretation",
]
