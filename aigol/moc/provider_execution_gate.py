"""MOC V1 provider execution eligibility gate.

This module evaluates whether a runtime-dispatched worker package is eligible
for future provider execution. It is gate-only: no provider is executed, no
external API is called, no shell command is run, and no external system is
activated.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_WORKER_PROVIDER_EXECUTION_GATE"
SCHEMA_VERSION = "1.0"
GATED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

RUNTIME_DISPATCH_ARTIFACT_TYPE = "MOC_V1_RUNTIME_DISPATCH_EVENT"
RUNTIME_DISPATCH_PERFORMED = "RUNTIME_DISPATCH_PERFORMED"

PROVIDER_EXECUTION_ELIGIBLE = "PROVIDER_EXECUTION_ELIGIBLE"
PROVIDER_EXECUTION_REJECTED = "PROVIDER_EXECUTION_REJECTED"
INVALID_RUNTIME_DISPATCH = "INVALID_RUNTIME_DISPATCH"
FAIL_CLOSED = "FAIL_CLOSED"


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(gate: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(gate)
    safe.pop("provider_gate_hash", None)
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


def _list_value(value: Any) -> list[Any]:
    return _canonical_copy(value) if isinstance(value, list) else []


def _string_value(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return UNKNOWN


def _dispatch_event_value(runtime_dispatch: dict[str, Any] | None, key: str) -> Any:
    if not isinstance(runtime_dispatch, dict):
        return UNKNOWN
    events = runtime_dispatch.get("dispatch_events")
    if not isinstance(events, list) or not events:
        return UNKNOWN
    first = events[0]
    if not isinstance(first, dict):
        return UNKNOWN
    return first.get(key, UNKNOWN)


def _provider_gate_id(runtime_dispatch: dict[str, Any] | None) -> str:
    return "moc-provider-execution-gate-" + canonical_hash(
        {
            "runtime_dispatch_hash": (
                _string_value(runtime_dispatch.get("runtime_dispatch_hash"))
                if isinstance(runtime_dispatch, dict)
                else UNKNOWN
            ),
            "worker_package_id": (
                _string_value(runtime_dispatch.get("worker_package_id"))
                if isinstance(runtime_dispatch, dict)
                else UNKNOWN
            ),
        }
    )


def _check(name: str, passed: bool, detail: str) -> dict[str, Any]:
    return {
        "check": name,
        "status": "PASS" if passed else "FAIL",
        "detail": detail,
    }


def _eligibility_checks(runtime_dispatch: dict[str, Any] | None, load_errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(runtime_dispatch, dict):
        return [_check("runtime_dispatch_present", False, "; ".join(load_errors or ["runtime dispatch evidence missing"]))]
    return [
        _check(
            "artifact_type",
            runtime_dispatch.get("artifact_type") == RUNTIME_DISPATCH_ARTIFACT_TYPE,
            f"artifact_type={runtime_dispatch.get('artifact_type', UNKNOWN)}",
        ),
        _check(
            "runtime_dispatch_status",
            runtime_dispatch.get("runtime_dispatch_status") == RUNTIME_DISPATCH_PERFORMED,
            f"runtime_dispatch_status={runtime_dispatch.get('runtime_dispatch_status', UNKNOWN)}",
        ),
        _check(
            "runtime_dispatch_hash",
            _string_value(runtime_dispatch.get("runtime_dispatch_hash")) != UNKNOWN,
            "runtime_dispatch_hash must exist",
        ),
        _check(
            "runtime_execution_scope",
            runtime_dispatch.get("runtime_execution_scope") == "bounded_single_dispatch",
            f"runtime_execution_scope={runtime_dispatch.get('runtime_execution_scope', UNKNOWN)}",
        ),
        _check(
            "provider_activation_performed",
            runtime_dispatch.get("provider_activation_performed") is False,
            f"provider_activation_performed={runtime_dispatch.get('provider_activation_performed', UNKNOWN)}",
        ),
        _check(
            "execution_completed",
            runtime_dispatch.get("execution_completed") is False,
            f"execution_completed={runtime_dispatch.get('execution_completed', UNKNOWN)}",
        ),
        _check(
            "execution_result_present",
            runtime_dispatch.get("execution_result_present") is False,
            f"execution_result_present={runtime_dispatch.get('execution_result_present', UNKNOWN)}",
        ),
        _check(
            "automatic_retry",
            _dispatch_event_value(runtime_dispatch, "automatic_retry") is False,
            f"automatic_retry={_dispatch_event_value(runtime_dispatch, 'automatic_retry')}",
        ),
        _check(
            "recursive_dispatch",
            _dispatch_event_value(runtime_dispatch, "recursive_dispatch") is False,
            f"recursive_dispatch={_dispatch_event_value(runtime_dispatch, 'recursive_dispatch')}",
        ),
        _check("lineage_refs", bool(_list_value(runtime_dispatch.get("lineage_refs"))), "lineage refs must exist"),
        _check("approval_refs", bool(_list_value(runtime_dispatch.get("approval_refs"))), "approval refs must exist"),
        _check("replay_refs", bool(_list_value(runtime_dispatch.get("replay_refs"))), "replay refs must exist"),
    ]


def _violations(runtime_dispatch: dict[str, Any] | None, load_errors: list[str]) -> list[str]:
    violations = list(load_errors)
    if not isinstance(runtime_dispatch, dict):
        violations.append("runtime dispatch evidence missing")
        return sorted(set(violations))
    if runtime_dispatch.get("artifact_type") != RUNTIME_DISPATCH_ARTIFACT_TYPE:
        violations.append("runtime dispatch artifact_type invalid")
    if runtime_dispatch.get("runtime_dispatch_status") != RUNTIME_DISPATCH_PERFORMED:
        violations.append("runtime dispatch status is not RUNTIME_DISPATCH_PERFORMED")
    if _string_value(runtime_dispatch.get("runtime_dispatch_hash")) == UNKNOWN:
        violations.append("runtime_dispatch_hash missing")
    if runtime_dispatch.get("runtime_execution_scope") != "bounded_single_dispatch":
        violations.append("runtime dispatch must be bounded_single_dispatch")
    if runtime_dispatch.get("provider_activation_performed") is not False:
        violations.append("provider_activation_performed must remain false")
    if runtime_dispatch.get("execution_completed") is not False:
        violations.append("execution_completed must remain false")
    if runtime_dispatch.get("execution_result_present") is not False:
        violations.append("execution_result_present must remain false")
    if _dispatch_event_value(runtime_dispatch, "automatic_retry") is not False:
        violations.append("automatic_retry must remain false")
    if _dispatch_event_value(runtime_dispatch, "recursive_dispatch") is not False:
        violations.append("recursive_dispatch must remain false")
    if not _list_value(runtime_dispatch.get("lineage_refs")):
        violations.append("lineage refs must exist")
    if not _list_value(runtime_dispatch.get("approval_refs")):
        violations.append("approval refs must exist")
    if not _list_value(runtime_dispatch.get("replay_refs")):
        violations.append("replay refs must exist")
    return sorted(set(violations))


def _status(runtime_dispatch: dict[str, Any] | None, violations: list[str]) -> str:
    fail_closed_fragments = (
        "path missing",
        "malformed",
        "must be a JSON object",
        "missing",
        "refs must exist",
        "must remain false",
        "must be bounded_single_dispatch",
    )
    if any(any(fragment in violation for fragment in fail_closed_fragments) for violation in violations):
        return FAIL_CLOSED
    if not isinstance(runtime_dispatch, dict) or runtime_dispatch.get("artifact_type") != RUNTIME_DISPATCH_ARTIFACT_TYPE:
        return INVALID_RUNTIME_DISPATCH
    if runtime_dispatch.get("runtime_dispatch_status") != RUNTIME_DISPATCH_PERFORMED:
        return PROVIDER_EXECUTION_REJECTED
    if violations:
        return FAIL_CLOSED
    return PROVIDER_EXECUTION_ELIGIBLE


def evaluate_provider_execution_gate(
    runtime_dispatch: dict[str, Any] | None,
    *,
    gated_at: str = GATED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(load_errors or [])
    violations = _violations(runtime_dispatch, errors)
    status = _status(runtime_dispatch, violations)
    safe_dispatch = runtime_dispatch if isinstance(runtime_dispatch, dict) else {}
    eligible = status == PROVIDER_EXECUTION_ELIGIBLE
    gate = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "gated_at": str(gated_at),
        "provider_gate_status": status,
        "provider_gate_id": _provider_gate_id(runtime_dispatch),
        "runtime_dispatch_hash": _string_value(safe_dispatch.get("runtime_dispatch_hash")),
        "worker_package_id": _string_value(safe_dispatch.get("worker_package_id")),
        "proposal_id": _string_value(safe_dispatch.get("proposal_id")),
        "proposal_hash": _string_value(safe_dispatch.get("proposal_hash")),
        "linked_contract_id": _string_value(safe_dispatch.get("linked_contract_id")),
        "linked_contract_hash": _string_value(safe_dispatch.get("linked_contract_hash")),
        "provider_execution_eligible": eligible,
        "provider_activation": False,
        "provider_execution_performed": False,
        "external_api_called": False,
        "shell_command_executed": False,
        "execution_result_present": False,
        "automatic_retry": False,
        "recursive_execution": False,
        "eligibility_checks": _eligibility_checks(runtime_dispatch, errors),
        "provider_gate_violations": violations,
        "warnings": [
            "provider execution gate is not provider execution",
            "provider execution gate does not activate providers",
            "future provider execution requires a separate milestone",
        ],
        "unknowns": [violation for violation in violations if "missing" in violation or "UNKNOWN" in violation],
        "lineage_refs": _list_value(safe_dispatch.get("lineage_refs")),
        "approval_refs": _list_value(safe_dispatch.get("approval_refs")),
        "replay_refs": _list_value(safe_dispatch.get("replay_refs")),
        "governance_guarantees": {
            "gate_only": True,
            "provider_activation": False,
            "provider_execution_performed": False,
            "external_api_called": False,
            "shell_command_executed": False,
            "execution_result_present": False,
            "automatic_retry": False,
            "recursive_execution": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
        },
    }
    gate["provider_gate_hash"] = canonical_hash(_hash_input(gate))
    return gate


def write_provider_execution_gate(gate: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(gate, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_provider_execution_gate(
    *,
    runtime_dispatch_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    runtime_dispatch, load_errors = _load_json_object(runtime_dispatch_path, "runtime dispatch")
    gate = evaluate_provider_execution_gate(runtime_dispatch, load_errors=load_errors)
    result = {
        "command": "aigol moc provider-execution-gate",
        "runtime_dispatch_path": str(runtime_dispatch_path or ""),
        "provider_execution_gate": gate,
        "gate_only": True,
        "provider_activation_added": False,
        "provider_execution_performed": False,
        "external_api_called": False,
        "shell_command_executed": False,
        "execution_result_present": False,
        "automatic_retry_added": False,
        "recursive_execution_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "hidden_continuation_added": False,
    }
    if output_path:
        result["output"] = write_provider_execution_gate(gate, output_path)
    return result


def render_provider_execution_gate_summary(gate: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Provider Execution Gate",
            f"  provider_gate_status: {gate.get('provider_gate_status')}",
            f"  provider_gate_id: {gate.get('provider_gate_id')}",
            f"  runtime_dispatch_hash: {gate.get('runtime_dispatch_hash')}",
            f"  provider_execution_eligible: {gate.get('provider_execution_eligible')}",
            "Boundary",
            "  provider_activation: false",
            "  provider_execution_performed: false",
            "  external_api_called: false",
            "  shell_command_executed: false",
            "  automatic_retry: false",
            "  recursive_execution: false",
            "Replay",
            f"  lineage_refs: {len(gate.get('lineage_refs', []))}",
            f"  approval_refs: {len(gate.get('approval_refs', []))}",
            f"  replay_refs: {len(gate.get('replay_refs', []))}",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "FAIL_CLOSED",
    "INVALID_RUNTIME_DISPATCH",
    "PROVIDER_EXECUTION_ELIGIBLE",
    "PROVIDER_EXECUTION_REJECTED",
    "evaluate_provider_execution_gate",
    "inspect_provider_execution_gate",
    "render_provider_execution_gate_summary",
    "write_provider_execution_gate",
]
