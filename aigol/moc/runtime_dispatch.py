"""MOC V1 bounded runtime dispatch event recording.

This module records the first deterministic runtime dispatch boundary crossing
for MOC V1. It emits replay-visible dispatch evidence only: no provider
activation, external execution, orchestration runtime, autonomous retry, or
recursive dispatch is performed.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_RUNTIME_DISPATCH_EVENT"
SCHEMA_VERSION = "1.0"
DISPATCHED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

AUTHORIZATION_ARTIFACT_TYPE = "MOC_V1_WORKER_DISPATCH_AUTHORIZATION"
DISPATCH_AUTHORIZED = "DISPATCH_AUTHORIZED"

RUNTIME_DISPATCH_PERFORMED = "RUNTIME_DISPATCH_PERFORMED"
RUNTIME_DISPATCH_REJECTED = "RUNTIME_DISPATCH_REJECTED"
INVALID_DISPATCH_AUTHORIZATION = "INVALID_DISPATCH_AUTHORIZATION"
FAIL_CLOSED = "FAIL_CLOSED"

AUTHORITY_FIELDS = (
    "execution_authority",
    "provider_activation",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(dispatch_event: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(dispatch_event)
    safe.pop("runtime_dispatch_hash", None)
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


def _runtime_dispatch_id(dispatch_authorization: dict[str, Any] | None) -> str:
    return "moc-runtime-dispatch-" + canonical_hash(
        {
            "dispatch_authorization_hash": (
                _string_value(dispatch_authorization.get("dispatch_authorization_hash"))
                if isinstance(dispatch_authorization, dict)
                else UNKNOWN
            ),
            "worker_package_id": (
                _string_value(dispatch_authorization.get("worker_package_id"))
                if isinstance(dispatch_authorization, dict)
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


def _runtime_checks(
    dispatch_authorization: dict[str, Any] | None,
    load_errors: list[str],
) -> list[dict[str, Any]]:
    if not isinstance(dispatch_authorization, dict):
        return [
            _check(
                "dispatch_authorization_present",
                False,
                "; ".join(load_errors or ["dispatch authorization evidence missing"]),
            )
        ]
    return [
        _check(
            "artifact_type",
            dispatch_authorization.get("artifact_type") == AUTHORIZATION_ARTIFACT_TYPE,
            f"artifact_type={dispatch_authorization.get('artifact_type', UNKNOWN)}",
        ),
        _check(
            "dispatch_authorization_status",
            dispatch_authorization.get("dispatch_authorization_status") == DISPATCH_AUTHORIZED,
            f"dispatch_authorization_status={dispatch_authorization.get('dispatch_authorization_status', UNKNOWN)}",
        ),
        _check(
            "dispatch_authorization_hash",
            _string_value(dispatch_authorization.get("dispatch_authorization_hash")) != UNKNOWN,
            "dispatch_authorization_hash must exist",
        ),
        *[
            _check(
                field,
                dispatch_authorization.get(field) is False,
                f"{field}={dispatch_authorization.get(field, UNKNOWN)}",
            )
            for field in AUTHORITY_FIELDS
        ],
        _check(
            "dispatch_authorized",
            dispatch_authorization.get("dispatch_authorized") is True,
            f"dispatch_authorized={dispatch_authorization.get('dispatch_authorized', UNKNOWN)}",
        ),
        _check(
            "authorization_scope",
            dispatch_authorization.get("authorization_scope") == "future_runtime_dispatch_only",
            f"authorization_scope={dispatch_authorization.get('authorization_scope', UNKNOWN)}",
        ),
        _check("lineage_refs", bool(_list_value(dispatch_authorization.get("lineage_refs"))), "lineage refs must exist"),
        _check("approval_refs", bool(_list_value(dispatch_authorization.get("approval_refs"))), "approval refs must exist"),
        _check("replay_refs", bool(_list_value(dispatch_authorization.get("replay_refs"))), "replay refs must exist"),
    ]


def _violations(dispatch_authorization: dict[str, Any] | None, load_errors: list[str]) -> list[str]:
    violations = list(load_errors)
    if not isinstance(dispatch_authorization, dict):
        violations.append("dispatch authorization evidence missing")
        return sorted(set(violations))
    if dispatch_authorization.get("artifact_type") != AUTHORIZATION_ARTIFACT_TYPE:
        violations.append("dispatch authorization artifact_type invalid")
    if dispatch_authorization.get("dispatch_authorization_status") != DISPATCH_AUTHORIZED:
        violations.append("dispatch authorization status is not DISPATCH_AUTHORIZED")
    if _string_value(dispatch_authorization.get("dispatch_authorization_hash")) == UNKNOWN:
        violations.append("dispatch_authorization_hash missing")
    if dispatch_authorization.get("dispatch_authorized") is not True:
        violations.append("dispatch_authorized must be true")
    if dispatch_authorization.get("authorization_scope") != "future_runtime_dispatch_only":
        violations.append("authorization_scope must be future_runtime_dispatch_only")
    for field in AUTHORITY_FIELDS:
        if dispatch_authorization.get(field) is not False:
            violations.append(f"{field} must remain false")
    if dispatch_authorization.get("runtime_execution") is not False:
        violations.append("runtime_execution must remain false")
    if dispatch_authorization.get("worker_dispatch_performed") is not False:
        violations.append("worker_dispatch_performed must remain false before runtime dispatch")
    if not _list_value(dispatch_authorization.get("lineage_refs")):
        violations.append("lineage refs must exist")
    if not _list_value(dispatch_authorization.get("approval_refs")):
        violations.append("approval refs must exist")
    if not _list_value(dispatch_authorization.get("replay_refs")):
        violations.append("replay refs must exist")
    return sorted(set(violations))


def _status(dispatch_authorization: dict[str, Any] | None, violations: list[str]) -> str:
    fail_closed_fragments = (
        "path missing",
        "malformed",
        "must be a JSON object",
        "missing",
        "refs must exist",
        "must remain false",
        "must be true",
        "must be future_runtime_dispatch_only",
    )
    if any(any(fragment in violation for fragment in fail_closed_fragments) for violation in violations):
        return FAIL_CLOSED
    if not isinstance(dispatch_authorization, dict) or dispatch_authorization.get("artifact_type") != AUTHORIZATION_ARTIFACT_TYPE:
        return INVALID_DISPATCH_AUTHORIZATION
    if dispatch_authorization.get("dispatch_authorization_status") != DISPATCH_AUTHORIZED:
        return RUNTIME_DISPATCH_REJECTED
    if violations:
        return FAIL_CLOSED
    return RUNTIME_DISPATCH_PERFORMED


def create_runtime_dispatch_event(
    dispatch_authorization: dict[str, Any] | None,
    *,
    dispatched_at: str = DISPATCHED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(load_errors or [])
    violations = _violations(dispatch_authorization, errors)
    status = _status(dispatch_authorization, violations)
    safe_authorization = dispatch_authorization if isinstance(dispatch_authorization, dict) else {}
    performed = status == RUNTIME_DISPATCH_PERFORMED
    runtime_dispatch_id = _runtime_dispatch_id(dispatch_authorization)
    event = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "dispatched_at": str(dispatched_at),
        "runtime_dispatch_status": status,
        "runtime_dispatch_id": runtime_dispatch_id,
        "dispatch_authorization_hash": _string_value(safe_authorization.get("dispatch_authorization_hash")),
        "worker_package_id": _string_value(safe_authorization.get("worker_package_id")),
        "proposal_id": _string_value(safe_authorization.get("proposal_id")),
        "proposal_hash": _string_value(safe_authorization.get("proposal_hash")),
        "linked_contract_id": _string_value(safe_authorization.get("linked_contract_id")),
        "linked_contract_hash": _string_value(safe_authorization.get("linked_contract_hash")),
        "runtime_execution_scope": "bounded_single_dispatch",
        "runtime_dispatch_performed": performed,
        "provider_activation_performed": False,
        "execution_completed": False,
        "execution_result_present": False,
        "dispatch_events": [
            {
                "event_type": "BOUNDED_RUNTIME_DISPATCH_RECORDED",
                "event_status": "RECORDED" if performed else "NOT_RECORDED",
                "runtime_dispatch_id": runtime_dispatch_id,
                "single_dispatch_only": True,
                "provider_activation_performed": False,
                "execution_completed": False,
                "automatic_retry": False,
                "recursive_dispatch": False,
            }
        ],
        "runtime_checks": _runtime_checks(dispatch_authorization, errors),
        "runtime_violations": violations,
        "warnings": [
            "runtime dispatch is not provider execution",
            "runtime dispatch records bounded single dispatch only",
            "future provider execution requires a separate milestone",
        ],
        "unknowns": [violation for violation in violations if "missing" in violation or "UNKNOWN" in violation],
        "lineage_refs": _list_value(safe_authorization.get("lineage_refs")),
        "approval_refs": _list_value(safe_authorization.get("approval_refs")),
        "replay_refs": _list_value(safe_authorization.get("replay_refs")),
        "governance_guarantees": {
            "bounded_runtime_dispatch": True,
            "single_dispatch_only": True,
            "provider_activation_performed": False,
            "execution_completed": False,
            "autonomous_continuation": False,
            "orchestration_authority": False,
            "governance_mutation": False,
            "automatic_retry": False,
        },
    }
    event["runtime_dispatch_hash"] = canonical_hash(_hash_input(event))
    return event


def write_runtime_dispatch_event(dispatch_event: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dispatch_event, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_runtime_dispatch(
    *,
    dispatch_authorization_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    dispatch_authorization, load_errors = _load_json_object(dispatch_authorization_path, "dispatch authorization")
    dispatch_event = create_runtime_dispatch_event(dispatch_authorization, load_errors=load_errors)
    result = {
        "command": "aigol moc runtime-dispatch",
        "dispatch_authorization_path": str(dispatch_authorization_path or ""),
        "runtime_dispatch_event": dispatch_event,
        "bounded_runtime_dispatch": True,
        "single_dispatch_only": True,
        "provider_activation_performed": False,
        "external_provider_activation_added": False,
        "execution_completed": False,
        "execution_result_present": False,
        "automatic_retry_added": False,
        "recursive_dispatch_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "hidden_continuation_added": False,
    }
    if output_path:
        result["output"] = write_runtime_dispatch_event(dispatch_event, output_path)
    return result


def render_runtime_dispatch_summary(dispatch_event: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Runtime Dispatch Event",
            f"  runtime_dispatch_status: {dispatch_event.get('runtime_dispatch_status')}",
            f"  runtime_dispatch_id: {dispatch_event.get('runtime_dispatch_id')}",
            f"  dispatch_authorization_hash: {dispatch_event.get('dispatch_authorization_hash')}",
            f"  runtime_dispatch_performed: {dispatch_event.get('runtime_dispatch_performed')}",
            "Boundary",
            "  provider_activation_performed: false",
            "  execution_completed: false",
            "  execution_result_present: false",
            "  automatic_retry: false",
            "  recursive_dispatch: false",
            "Replay",
            f"  lineage_refs: {len(dispatch_event.get('lineage_refs', []))}",
            f"  approval_refs: {len(dispatch_event.get('approval_refs', []))}",
            f"  replay_refs: {len(dispatch_event.get('replay_refs', []))}",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "FAIL_CLOSED",
    "INVALID_DISPATCH_AUTHORIZATION",
    "RUNTIME_DISPATCH_PERFORMED",
    "RUNTIME_DISPATCH_REJECTED",
    "create_runtime_dispatch_event",
    "inspect_runtime_dispatch",
    "render_runtime_dispatch_summary",
    "write_runtime_dispatch_event",
]
