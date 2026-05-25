"""MOC V1 worker dispatch authorization boundary.

This module creates explicit authorization evidence for future runtime dispatch
eligibility only. Dispatch authorization is not execution: it does not execute
workers, activate providers, perform runtime execution, orchestrate work, or
create autonomous continuation.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_WORKER_DISPATCH_AUTHORIZATION"
SCHEMA_VERSION = "1.0"
AUTHORIZED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

REQUEST_ARTIFACT_TYPE = "MOC_V1_WORKER_DISPATCH_REQUEST"
DISPATCH_REQUEST_CREATED = "DISPATCH_REQUEST_CREATED"

DISPATCH_AUTHORIZED = "DISPATCH_AUTHORIZED"
DISPATCH_AUTHORIZATION_REJECTED = "DISPATCH_AUTHORIZATION_REJECTED"
INVALID_DISPATCH_REQUEST = "INVALID_DISPATCH_REQUEST"
FAIL_CLOSED = "FAIL_CLOSED"

AUTHORITY_FIELDS = (
    "dispatch_authority",
    "execution_authority",
    "provider_activation",
    "worker_dispatch",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(authorization: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(authorization)
    safe.pop("dispatch_authorization_hash", None)
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


def _dict_value(value: Any) -> dict[str, Any]:
    return _canonical_copy(value) if isinstance(value, dict) else {}


def _string_value(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return UNKNOWN


def _authorization_id(dispatch_request: dict[str, Any] | None) -> str:
    return "moc-dispatch-authorization-" + canonical_hash(
        {
            "dispatch_request_hash": (
                _string_value(dispatch_request.get("dispatch_request_hash"))
                if isinstance(dispatch_request, dict)
                else UNKNOWN
            ),
            "worker_package_id": (
                _string_value(dispatch_request.get("worker_package_id"))
                if isinstance(dispatch_request, dict)
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


def _authorization_checks(dispatch_request: dict[str, Any] | None, load_errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(dispatch_request, dict):
        return [_check("dispatch_request_present", False, "; ".join(load_errors or ["dispatch request evidence missing"]))]
    request_evidence = _dict_value(dispatch_request.get("request_evidence"))
    return [
        _check(
            "artifact_type",
            dispatch_request.get("artifact_type") == REQUEST_ARTIFACT_TYPE,
            f"artifact_type={dispatch_request.get('artifact_type', UNKNOWN)}",
        ),
        _check(
            "dispatch_request_status",
            dispatch_request.get("dispatch_request_status") == DISPATCH_REQUEST_CREATED,
            f"dispatch_request_status={dispatch_request.get('dispatch_request_status', UNKNOWN)}",
        ),
        _check(
            "dispatch_request_hash",
            _string_value(dispatch_request.get("dispatch_request_hash")) != UNKNOWN,
            "dispatch_request_hash must exist",
        ),
        *[
            _check(
                field,
                dispatch_request.get(field) is False,
                f"{field}={dispatch_request.get(field, UNKNOWN)}",
            )
            for field in AUTHORITY_FIELDS
        ],
        _check("lineage_refs", bool(_list_value(dispatch_request.get("lineage_refs"))), "lineage refs must exist"),
        _check("approval_refs", bool(_list_value(dispatch_request.get("approval_refs"))), "approval refs must exist"),
        _check("replay_refs", bool(_list_value(dispatch_request.get("replay_refs"))), "replay refs must exist"),
        _check("request_evidence", bool(request_evidence), "request evidence must exist"),
        _check("request_evidence_replay_safe", request_evidence.get("replay_safe") is True, "request evidence must remain replay_safe"),
        _check(
            "request_evidence_advisory_only",
            request_evidence.get("advisory_only", True) is True,
            "request evidence must remain advisory_only where applicable",
        ),
    ]


def _violations(dispatch_request: dict[str, Any] | None, load_errors: list[str]) -> list[str]:
    violations = list(load_errors)
    if not isinstance(dispatch_request, dict):
        violations.append("dispatch request evidence missing")
        return sorted(set(violations))
    if dispatch_request.get("artifact_type") != REQUEST_ARTIFACT_TYPE:
        violations.append("dispatch request artifact_type invalid")
    if dispatch_request.get("dispatch_request_status") != DISPATCH_REQUEST_CREATED:
        violations.append("dispatch request status is not DISPATCH_REQUEST_CREATED")
    if _string_value(dispatch_request.get("dispatch_request_hash")) == UNKNOWN:
        violations.append("dispatch_request_hash missing")
    for field in AUTHORITY_FIELDS:
        if dispatch_request.get(field) is not False:
            violations.append(f"{field} must remain false")
    if not _list_value(dispatch_request.get("lineage_refs")):
        violations.append("lineage refs must exist")
    if not _list_value(dispatch_request.get("approval_refs")):
        violations.append("approval refs must exist")
    if not _list_value(dispatch_request.get("replay_refs")):
        violations.append("replay refs must exist")
    request_evidence = _dict_value(dispatch_request.get("request_evidence"))
    if not request_evidence:
        violations.append("request evidence missing")
    else:
        if request_evidence.get("replay_safe") is not True:
            violations.append("request evidence must remain replay_safe")
        if request_evidence.get("advisory_only", True) is not True:
            violations.append("request evidence must remain advisory_only where applicable")
    return sorted(set(violations))


def _status(dispatch_request: dict[str, Any] | None, violations: list[str]) -> str:
    fail_closed_fragments = (
        "path missing",
        "malformed",
        "must be a JSON object",
        "missing",
        "refs must exist",
        "must remain false",
        "must remain replay_safe",
        "must remain advisory_only",
    )
    if any(any(fragment in violation for fragment in fail_closed_fragments) for violation in violations):
        return FAIL_CLOSED
    if not isinstance(dispatch_request, dict) or dispatch_request.get("artifact_type") != REQUEST_ARTIFACT_TYPE:
        return INVALID_DISPATCH_REQUEST
    if dispatch_request.get("dispatch_request_status") != DISPATCH_REQUEST_CREATED:
        return DISPATCH_AUTHORIZATION_REJECTED
    if violations:
        return FAIL_CLOSED
    return DISPATCH_AUTHORIZED


def authorize_worker_dispatch(
    dispatch_request: dict[str, Any] | None,
    *,
    authorized_at: str = AUTHORIZED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(load_errors or [])
    violations = _violations(dispatch_request, errors)
    status = _status(dispatch_request, violations)
    safe_request = dispatch_request if isinstance(dispatch_request, dict) else {}
    authorized = status == DISPATCH_AUTHORIZED
    authorization = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "authorized_at": str(authorized_at),
        "dispatch_authorization_status": status,
        "dispatch_authorization_id": _authorization_id(dispatch_request),
        "dispatch_request_hash": _string_value(safe_request.get("dispatch_request_hash")),
        "worker_package_id": _string_value(safe_request.get("worker_package_id")),
        "worker_preparation_hash": _string_value(safe_request.get("worker_preparation_hash")),
        "proposal_id": _string_value(safe_request.get("proposal_id")),
        "proposal_hash": _string_value(safe_request.get("proposal_hash")),
        "linked_contract_id": _string_value(safe_request.get("linked_contract_id")),
        "linked_contract_hash": _string_value(safe_request.get("linked_contract_hash")),
        "authorization_scope": "future_runtime_dispatch_only",
        "dispatch_authorized": authorized,
        "execution_authority": False,
        "provider_activation": False,
        "runtime_execution": False,
        "worker_dispatch_performed": False,
        "authorization_checks": _authorization_checks(dispatch_request, errors),
        "authorization_violations": violations,
        "warnings": [
            "dispatch authorization is not execution",
            "dispatch authorization is not runtime execution",
            "future runtime dispatch requires a separate milestone",
        ],
        "unknowns": [violation for violation in violations if "missing" in violation or "UNKNOWN" in violation],
        "lineage_refs": _list_value(safe_request.get("lineage_refs")),
        "approval_refs": _list_value(safe_request.get("approval_refs")),
        "replay_refs": _list_value(safe_request.get("replay_refs")),
        "governance_guarantees": {
            "authorization_only": True,
            "execution_authority": False,
            "provider_activation": False,
            "runtime_execution": False,
            "worker_dispatch_performed": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
            "automatic_execution": False,
        },
    }
    authorization["dispatch_authorization_hash"] = canonical_hash(_hash_input(authorization))
    return authorization


def write_worker_dispatch_authorization(authorization: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(authorization, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_worker_dispatch_authorization(
    *,
    dispatch_request_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    dispatch_request, load_errors = _load_json_object(dispatch_request_path, "dispatch request")
    authorization = authorize_worker_dispatch(dispatch_request, load_errors=load_errors)
    result = {
        "command": "aigol moc dispatch-authorize",
        "dispatch_request_path": str(dispatch_request_path or ""),
        "worker_dispatch_authorization": authorization,
        "authorization_only": True,
        "execution_authority_added": False,
        "worker_dispatch_performed": False,
        "provider_activation_added": False,
        "runtime_execution_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "automatic_execution_added": False,
        "hidden_continuation_added": False,
    }
    if output_path:
        result["output"] = write_worker_dispatch_authorization(authorization, output_path)
    return result


def render_worker_dispatch_authorization_summary(authorization: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Worker Dispatch Authorization",
            f"  dispatch_authorization_status: {authorization.get('dispatch_authorization_status')}",
            f"  dispatch_authorization_id: {authorization.get('dispatch_authorization_id')}",
            f"  dispatch_request_hash: {authorization.get('dispatch_request_hash')}",
            f"  dispatch_authorized: {authorization.get('dispatch_authorized')}",
            "Boundary",
            "  execution_authority: false",
            "  provider_activation: false",
            "  runtime_execution: false",
            "  worker_dispatch_performed: false",
            "Replay",
            f"  lineage_refs: {len(authorization.get('lineage_refs', []))}",
            f"  approval_refs: {len(authorization.get('approval_refs', []))}",
            f"  replay_refs: {len(authorization.get('replay_refs', []))}",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "DISPATCH_AUTHORIZED",
    "DISPATCH_AUTHORIZATION_REJECTED",
    "FAIL_CLOSED",
    "INVALID_DISPATCH_REQUEST",
    "authorize_worker_dispatch",
    "inspect_worker_dispatch_authorization",
    "render_worker_dispatch_authorization_summary",
    "write_worker_dispatch_authorization",
]
