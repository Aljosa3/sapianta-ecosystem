"""MOC V1 worker dispatch request artifact generation.

This module records an explicit human/governance request to consider future
dispatch authorization for an eligible dispatch preview. It does not dispatch
workers, execute tasks, activate providers, orchestrate work, or create actual
dispatch authorization.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_WORKER_DISPATCH_REQUEST"
SCHEMA_VERSION = "1.0"
REQUESTED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

PREVIEW_ARTIFACT_TYPE = "MOC_V1_WORKER_DISPATCH_AUTHORIZATION_PREVIEW"
DISPATCH_PREVIEW_ELIGIBLE = "DISPATCH_PREVIEW_ELIGIBLE"

DISPATCH_REQUEST_CREATED = "DISPATCH_REQUEST_CREATED"
DISPATCH_REQUEST_REJECTED = "DISPATCH_REQUEST_REJECTED"
INVALID_PREVIEW_EVIDENCE = "INVALID_PREVIEW_EVIDENCE"
FAIL_CLOSED = "FAIL_CLOSED"

AUTHORITY_FIELDS = (
    "dispatch_authority",
    "execution_authority",
    "provider_activation",
    "worker_dispatch",
    "ready_for_actual_dispatch",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(request: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(request)
    safe.pop("dispatch_request_hash", None)
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


def _requester_type(request_evidence: dict[str, Any] | None) -> str:
    if not isinstance(request_evidence, dict):
        return UNKNOWN
    return _string_value(request_evidence.get("requester_type"))


def _request_scope(request_evidence: dict[str, Any] | None) -> str:
    if not isinstance(request_evidence, dict):
        return UNKNOWN
    value = request_evidence.get("request_scope")
    if isinstance(value, str) and value.strip():
        return value
    return "dispatch may be considered by a future authorization layer"


def _request_id(preview: dict[str, Any] | None, request_evidence: dict[str, Any] | None) -> str:
    return "moc-dispatch-request-" + canonical_hash(
        {
            "dispatch_preview_hash": _string_value(preview.get("dispatch_preview_hash")) if isinstance(preview, dict) else UNKNOWN,
            "worker_package_id": _string_value(preview.get("worker_package_id")) if isinstance(preview, dict) else UNKNOWN,
            "request_evidence_hash": canonical_hash(request_evidence or {}),
        }
    )


def _check(name: str, passed: bool, detail: str) -> dict[str, Any]:
    return {
        "check": name,
        "status": "PASS" if passed else "FAIL",
        "detail": detail,
    }


def _request_checks(
    dispatch_preview: dict[str, Any] | None,
    request_evidence: dict[str, Any] | None,
    load_errors: list[str],
) -> list[dict[str, Any]]:
    if not isinstance(dispatch_preview, dict):
        return [_check("dispatch_preview_present", False, "; ".join(load_errors or ["dispatch preview evidence missing"]))]
    if not isinstance(request_evidence, dict):
        return [_check("request_evidence_present", False, "; ".join(load_errors or ["request evidence missing"]))]
    return [
        _check(
            "artifact_type",
            dispatch_preview.get("artifact_type") == PREVIEW_ARTIFACT_TYPE,
            f"artifact_type={dispatch_preview.get('artifact_type', UNKNOWN)}",
        ),
        _check(
            "dispatch_preview_status",
            dispatch_preview.get("dispatch_preview_status") == DISPATCH_PREVIEW_ELIGIBLE,
            f"dispatch_preview_status={dispatch_preview.get('dispatch_preview_status', UNKNOWN)}",
        ),
        _check("dispatch_preview_hash", bool(_string_value(dispatch_preview.get("dispatch_preview_hash")) != UNKNOWN), "dispatch_preview_hash must exist"),
        _check("worker_package_id", bool(_string_value(dispatch_preview.get("worker_package_id")) != UNKNOWN), "worker_package_id must exist"),
        *[
            _check(
                field,
                dispatch_preview.get(field) is False,
                f"{field}={dispatch_preview.get(field, UNKNOWN)}",
            )
            for field in AUTHORITY_FIELDS
        ],
        _check("lineage_refs", bool(_list_value(dispatch_preview.get("lineage_refs"))), "lineage refs must exist"),
        _check("approval_refs", bool(_list_value(dispatch_preview.get("approval_refs"))), "approval refs must exist"),
        _check("replay_refs", bool(_list_value(dispatch_preview.get("replay_refs"))), "replay refs must exist"),
        _check("request_evidence", bool(request_evidence), "request evidence must be explicit"),
        _check("requester_type", _requester_type(request_evidence) != UNKNOWN, "requester_type must be explicit"),
    ]


def _violations(
    dispatch_preview: dict[str, Any] | None,
    request_evidence: dict[str, Any] | None,
    load_errors: list[str],
) -> list[str]:
    violations = list(load_errors)
    if not isinstance(dispatch_preview, dict):
        violations.append("dispatch preview evidence missing")
        return sorted(set(violations))
    if dispatch_preview.get("artifact_type") != PREVIEW_ARTIFACT_TYPE:
        violations.append("dispatch preview artifact_type invalid")
    if dispatch_preview.get("dispatch_preview_status") != DISPATCH_PREVIEW_ELIGIBLE:
        violations.append("dispatch preview is not DISPATCH_PREVIEW_ELIGIBLE")
    if _string_value(dispatch_preview.get("dispatch_preview_hash")) == UNKNOWN:
        violations.append("dispatch_preview_hash missing")
    if _string_value(dispatch_preview.get("worker_package_id")) == UNKNOWN:
        violations.append("worker_package_id missing")
    for field in AUTHORITY_FIELDS:
        if dispatch_preview.get(field) is not False:
            violations.append(f"{field} must remain false")
    if not _list_value(dispatch_preview.get("lineage_refs")):
        violations.append("lineage refs must exist")
    if not _list_value(dispatch_preview.get("approval_refs")):
        violations.append("approval refs must exist")
    if not _list_value(dispatch_preview.get("replay_refs")):
        violations.append("replay refs must exist")
    if not isinstance(request_evidence, dict) or not request_evidence:
        violations.append("request evidence missing")
    elif _requester_type(request_evidence) == UNKNOWN:
        violations.append("requester_type must be explicit")
    return sorted(set(violations))


def _status(dispatch_preview: dict[str, Any] | None, violations: list[str]) -> str:
    fail_closed_fragments = (
        "path missing",
        "malformed",
        "must be a JSON object",
        "missing",
        "refs must exist",
        "must remain false",
        "requester_type must be explicit",
    )
    if any(any(fragment in violation for fragment in fail_closed_fragments) for violation in violations):
        return FAIL_CLOSED
    if not isinstance(dispatch_preview, dict) or dispatch_preview.get("artifact_type") != PREVIEW_ARTIFACT_TYPE:
        return INVALID_PREVIEW_EVIDENCE
    if _string_value(dispatch_preview.get("dispatch_preview_hash")) == UNKNOWN:
        return INVALID_PREVIEW_EVIDENCE
    if dispatch_preview.get("dispatch_preview_status") != DISPATCH_PREVIEW_ELIGIBLE:
        return DISPATCH_REQUEST_REJECTED
    if violations:
        return FAIL_CLOSED
    return DISPATCH_REQUEST_CREATED


def build_worker_dispatch_request(
    dispatch_preview: dict[str, Any] | None,
    request_evidence: dict[str, Any] | None,
    *,
    requested_at: str = REQUESTED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(load_errors or [])
    violations = _violations(dispatch_preview, request_evidence, errors)
    status = _status(dispatch_preview, violations)
    safe_preview = dispatch_preview if isinstance(dispatch_preview, dict) else {}
    request = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "requested_at": str(requested_at),
        "dispatch_request_status": status,
        "dispatch_request_id": _request_id(dispatch_preview, request_evidence),
        "worker_package_id": _string_value(safe_preview.get("worker_package_id")),
        "worker_preparation_hash": _string_value(safe_preview.get("worker_preparation_hash")),
        "dispatch_preview_hash": _string_value(safe_preview.get("dispatch_preview_hash")),
        "proposal_id": _string_value(safe_preview.get("proposal_id")),
        "proposal_hash": _string_value(safe_preview.get("proposal_hash")),
        "linked_contract_id": _string_value(safe_preview.get("linked_contract_id")),
        "linked_contract_hash": _string_value(safe_preview.get("linked_contract_hash")),
        "request_evidence": _canonical_copy(request_evidence) if isinstance(request_evidence, dict) else {},
        "requester_type": _requester_type(request_evidence),
        "request_scope": _request_scope(request_evidence),
        "lineage_refs": _list_value(safe_preview.get("lineage_refs")),
        "approval_refs": _list_value(safe_preview.get("approval_refs")),
        "replay_refs": _list_value(safe_preview.get("replay_refs")),
        "request_checks": _request_checks(dispatch_preview, request_evidence, errors),
        "request_violations": violations,
        "warnings": [
            "dispatch request is not dispatch authorization",
            "dispatch request is not execution",
            "future dispatch authorization requires a separate milestone",
        ],
        "unknowns": [violation for violation in violations if "missing" in violation or "UNKNOWN" in violation],
        "dispatch_authority": False,
        "execution_authority": False,
        "provider_activation": False,
        "worker_dispatch": False,
        "ready_for_actual_dispatch": False,
        "governance_guarantees": {
            "request_only": True,
            "execution_authority": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "dispatch_authority": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
            "automatic_execution": False,
        },
    }
    request["dispatch_request_hash"] = canonical_hash(_hash_input(request))
    return request


def write_worker_dispatch_request(request: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(request, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_worker_dispatch_request(
    *,
    dispatch_preview_path: str | Path | None = None,
    request_evidence_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    dispatch_preview, preview_load_errors = _load_json_object(dispatch_preview_path, "dispatch preview")
    request_evidence, request_load_errors = _load_json_object(request_evidence_path, "request evidence")
    request = build_worker_dispatch_request(
        dispatch_preview,
        request_evidence,
        load_errors=preview_load_errors + request_load_errors,
    )
    result = {
        "command": "aigol moc dispatch-request",
        "dispatch_preview_path": str(dispatch_preview_path or ""),
        "request_evidence_path": str(request_evidence_path or ""),
        "worker_dispatch_request": request,
        "request_only": True,
        "execution_authority_added": False,
        "worker_dispatch_added": False,
        "provider_activation_added": False,
        "dispatch_authority_added": False,
        "orchestration_added": False,
        "autonomous_cognition_added": False,
        "governance_mutation_added": False,
        "actual_dispatch_authorization_added": False,
        "automatic_execution_added": False,
        "hidden_continuation_added": False,
    }
    if output_path:
        result["output"] = write_worker_dispatch_request(request, output_path)
    return result


def render_worker_dispatch_request_summary(request: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Worker Dispatch Request",
            f"  dispatch_request_status: {request.get('dispatch_request_status')}",
            f"  dispatch_request_id: {request.get('dispatch_request_id')}",
            f"  worker_package_id: {request.get('worker_package_id')}",
            f"  dispatch_preview_hash: {request.get('dispatch_preview_hash')}",
            "Boundary",
            "  dispatch_authority: false",
            "  execution_authority: false",
            "  provider_activation: false",
            "  worker_dispatch: false",
            "  ready_for_actual_dispatch: false",
            "Replay",
            f"  lineage_refs: {len(request.get('lineage_refs', []))}",
            f"  approval_refs: {len(request.get('approval_refs', []))}",
            f"  replay_refs: {len(request.get('replay_refs', []))}",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "DISPATCH_REQUEST_CREATED",
    "DISPATCH_REQUEST_REJECTED",
    "FAIL_CLOSED",
    "INVALID_PREVIEW_EVIDENCE",
    "build_worker_dispatch_request",
    "inspect_worker_dispatch_request",
    "render_worker_dispatch_request_summary",
    "write_worker_dispatch_request",
]
