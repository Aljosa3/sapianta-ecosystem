"""MOC V1 worker dispatch authorization preview.

This module evaluates dispatch eligibility semantics for worker preparation
packages without dispatching workers, executing tasks, activating providers, or
creating actual dispatch authorization.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "MOC_V1_WORKER_DISPATCH_AUTHORIZATION_PREVIEW"
SCHEMA_VERSION = "1.0"
PREVIEWED_AT = "1970-01-01T00:00:00Z"
UNKNOWN = "UNKNOWN"

WORKER_PACKAGE_ARTIFACT_TYPE = "MOC_V1_WORKER_PREPARATION_PACKAGE"
PREPARED_FOR_WORKER = "PREPARED_FOR_WORKER"

DISPATCH_PREVIEW_ELIGIBLE = "DISPATCH_PREVIEW_ELIGIBLE"
DISPATCH_PREVIEW_REJECTED = "DISPATCH_PREVIEW_REJECTED"
INVALID_WORKER_PREPARATION = "INVALID_WORKER_PREPARATION"
FAIL_CLOSED = "FAIL_CLOSED"

AUTHORITY_FIELDS = (
    "ready_for_dispatch",
    "dispatch_authority",
    "execution_authority",
    "provider_activation",
    "worker_dispatch",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(preview: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(preview)
    safe.pop("dispatch_preview_hash", None)
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


def _worker_preparation_hash(worker_package: dict[str, Any] | None) -> str:
    if not isinstance(worker_package, dict):
        return UNKNOWN
    value = worker_package.get("worker_preparation_hash")
    if isinstance(value, str) and value.strip():
        return value
    return canonical_hash(worker_package)


def _check(name: str, passed: bool, detail: str) -> dict[str, Any]:
    return {
        "check": name,
        "status": "PASS" if passed else "FAIL",
        "detail": detail,
    }


def _eligibility_checks(worker_package: dict[str, Any] | None, load_errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(worker_package, dict):
        return [_check("worker_package_present", False, "; ".join(load_errors or ["worker package evidence missing"]))]

    allowed = _list_value(worker_package.get("allowed_worker_actions"))
    forbidden = _list_value(worker_package.get("forbidden_worker_actions"))
    overlap = sorted(set(allowed).intersection(set(forbidden)))
    return [
        _check(
            "artifact_type",
            worker_package.get("artifact_type") == WORKER_PACKAGE_ARTIFACT_TYPE,
            f"artifact_type={worker_package.get('artifact_type', UNKNOWN)}",
        ),
        _check(
            "preparation_status",
            worker_package.get("preparation_status") == PREPARED_FOR_WORKER,
            f"preparation_status={worker_package.get('preparation_status', UNKNOWN)}",
        ),
        *[
            _check(
                field,
                worker_package.get(field) is False,
                f"{field}={worker_package.get(field, UNKNOWN)}",
            )
            for field in AUTHORITY_FIELDS
        ],
        _check("lineage_refs", bool(_list_value(worker_package.get("lineage_refs"))), "lineage refs must exist"),
        _check("approval_refs", bool(_list_value(worker_package.get("approval_refs"))), "approval refs must exist"),
        _check("replay_refs", bool(_list_value(worker_package.get("replay_refs"))), "replay refs must exist"),
        _check("allowed_worker_actions", bool(allowed), "allowed worker actions must be explicit and non-empty"),
        _check("forbidden_overlap", not overlap, f"overlap={json.dumps(overlap, sort_keys=True)}"),
    ]


def _violations(worker_package: dict[str, Any] | None, load_errors: list[str]) -> list[str]:
    violations = list(load_errors)
    if not isinstance(worker_package, dict):
        violations.append("worker package evidence missing")
        return sorted(set(violations))
    if worker_package.get("artifact_type") != WORKER_PACKAGE_ARTIFACT_TYPE:
        violations.append("worker preparation artifact_type invalid")
    if not isinstance(worker_package.get("worker_preparation_hash"), str) or not worker_package.get("worker_preparation_hash"):
        violations.append("worker_preparation_hash missing")
    if worker_package.get("preparation_status") != PREPARED_FOR_WORKER:
        violations.append("worker package is not PREPARED_FOR_WORKER")
    for field in AUTHORITY_FIELDS:
        if worker_package.get(field) is not False:
            violations.append(f"{field} must remain false")
    if not _list_value(worker_package.get("lineage_refs")):
        violations.append("lineage refs must exist")
    if not _list_value(worker_package.get("approval_refs")):
        violations.append("approval refs must exist")
    if not _list_value(worker_package.get("replay_refs")):
        violations.append("replay refs must exist")
    allowed = _list_value(worker_package.get("allowed_worker_actions"))
    forbidden = _list_value(worker_package.get("forbidden_worker_actions"))
    if not allowed:
        violations.append("allowed_worker_actions must be explicit and non-empty")
    overlap = sorted(set(allowed).intersection(set(forbidden)))
    if overlap:
        violations.append(f"allowed and forbidden worker actions overlap: {json.dumps(overlap, sort_keys=True)}")
    return sorted(set(violations))


def _status(worker_package: dict[str, Any] | None, violations: list[str]) -> str:
    if any("missing" in violation or "malformed" in violation for violation in violations):
        return FAIL_CLOSED
    if not isinstance(worker_package, dict) or worker_package.get("artifact_type") != WORKER_PACKAGE_ARTIFACT_TYPE:
        return INVALID_WORKER_PREPARATION
    if not isinstance(worker_package.get("worker_preparation_hash"), str) or not worker_package.get("worker_preparation_hash"):
        return INVALID_WORKER_PREPARATION
    if violations:
        return DISPATCH_PREVIEW_REJECTED
    return DISPATCH_PREVIEW_ELIGIBLE


def build_dispatch_authorization_preview(
    worker_package: dict[str, Any] | None,
    *,
    previewed_at: str = PREVIEWED_AT,
    load_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(load_errors or [])
    violations = _violations(worker_package, errors)
    status = _status(worker_package, violations)
    safe_package = worker_package if isinstance(worker_package, dict) else {}
    preview = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "previewed_at": str(previewed_at),
        "dispatch_preview_status": status,
        "worker_package_id": str(safe_package.get("worker_package_id", UNKNOWN)),
        "worker_preparation_hash": _worker_preparation_hash(worker_package),
        "proposal_id": str(safe_package.get("proposal_id", UNKNOWN)),
        "proposal_hash": str(safe_package.get("proposal_hash", UNKNOWN)),
        "linked_contract_id": str(safe_package.get("linked_contract_id", UNKNOWN)),
        "linked_contract_hash": str(safe_package.get("linked_contract_hash", UNKNOWN)),
        "linked_approval_gate_hash": str(safe_package.get("linked_approval_gate_hash", UNKNOWN)),
        "dispatch_eligible_preview": status == DISPATCH_PREVIEW_ELIGIBLE,
        "dispatch_authority": False,
        "execution_authority": False,
        "provider_activation": False,
        "worker_dispatch": False,
        "ready_for_actual_dispatch": False,
        "eligibility_checks": _eligibility_checks(worker_package, errors),
        "dispatch_preview_violations": violations,
        "warnings": ["dispatch preview is not actual dispatch authorization"],
        "unknowns": [violation for violation in violations if "missing" in violation or "UNKNOWN" in violation],
        "lineage_refs": _list_value(safe_package.get("lineage_refs")),
        "approval_refs": _list_value(safe_package.get("approval_refs")),
        "replay_refs": _list_value(safe_package.get("replay_refs")),
        "governance_guarantees": {
            "preview_only": True,
            "execution_authority": False,
            "worker_dispatch": False,
            "provider_activation": False,
            "dispatch_authority": False,
            "orchestration_authority": False,
            "autonomous_continuation": False,
            "governance_mutation": False,
            "automatic_execution": False,
            "actual_dispatch_authorization": False,
            "hidden_continuation": False,
        },
    }
    preview["dispatch_preview_hash"] = canonical_hash(_hash_input(preview))
    return preview


def write_dispatch_authorization_preview(preview: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(preview, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_dispatch_authorization_preview(
    *,
    worker_package_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    worker_package, load_errors = _load_json_object(worker_package_path, "worker package")
    preview = build_dispatch_authorization_preview(worker_package, load_errors=load_errors)
    result = {
        "command": "aigol moc dispatch-preview",
        "worker_package_path": str(worker_package_path or ""),
        "dispatch_authorization_preview": preview,
        "preview_only": True,
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
        result["output"] = write_dispatch_authorization_preview(preview, output_path)
    return result


def render_dispatch_authorization_preview_summary(preview: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Dispatch Authorization Preview",
            f"  dispatch_preview_status: {preview.get('dispatch_preview_status')}",
            f"  worker_package_id: {preview.get('worker_package_id')}",
            f"  worker_preparation_hash: {preview.get('worker_preparation_hash')}",
            f"  dispatch_eligible_preview: {preview.get('dispatch_eligible_preview')}",
            "Boundary",
            "  dispatch_authority: false",
            "  execution_authority: false",
            "  provider_activation: false",
            "  worker_dispatch: false",
            "  ready_for_actual_dispatch: false",
            "Replay",
            f"  lineage_refs: {len(preview.get('lineage_refs', []))}",
            f"  approval_refs: {len(preview.get('approval_refs', []))}",
            f"  replay_refs: {len(preview.get('replay_refs', []))}",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "DISPATCH_PREVIEW_ELIGIBLE",
    "DISPATCH_PREVIEW_REJECTED",
    "FAIL_CLOSED",
    "INVALID_WORKER_PREPARATION",
    "build_dispatch_authorization_preview",
    "inspect_dispatch_authorization_preview",
    "render_dispatch_authorization_preview_summary",
    "write_dispatch_authorization_preview",
]
