"""Certify Generation 2 compatibility-layer retirement dispositions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


COMPATIBILITY_RETIREMENT_CERTIFICATION_RUNTIME_VERSION = (
    "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_14_COMPATIBILITY_RETIREMENT_CERTIFICATION_RUNTIME_V1"
)
COMPATIBILITY_RETIREMENT_CERTIFICATION_ARTIFACT_V1 = (
    "COMPATIBILITY_RETIREMENT_CERTIFICATION_ARTIFACT_V1"
)
COMPATIBILITY_RETIREMENT_CERTIFIED = "COMPATIBILITY_RETIREMENT_CERTIFIED"
FAILED_CLOSED = "FAILED_CLOSED"

RETIRED_PERMANENTLY = "RETIRED_PERMANENTLY"
RETAINED_OBSERVATIONAL_REPLAY_EVIDENCE = "RETAINED_OBSERVATIONAL_REPLAY_EVIDENCE"
RETAINED_ACTIVE_PARITY_NOT_PROVEN = "RETAINED_ACTIVE_PARITY_NOT_PROVEN"
RETAINED_PERMANENT_STRUCTURED_AUTHORITY = "RETAINED_PERMANENT_STRUCTURED_AUTHORITY"

PARITY_CERTIFIED_STATUSES = {
    "PARITY_CERTIFIED",
    "CSA_PARITY_CERTIFIED",
    "DETERMINISTIC_PARITY_CERTIFIED",
}

REPLAY_STEPS = (
    "compatibility_retirement_certification_recorded",
    "compatibility_retirement_certification_returned",
)

AUTHORITY_FLAGS = (
    "governance_authority_preserved",
    "ocs_authority_preserved",
    "ppp_authority_preserved",
    "provider_authority_preserved",
    "worker_authority_preserved",
    "approval_authority_preserved",
)


def certify_compatibility_retirement(
    *,
    certification_id: str,
    compatibility_layers: list[dict[str, Any]],
    certified_by: str,
    certified_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Classify compatibility paths without granting runtime authority."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        dispositions = [_classify_layer(deepcopy(layer)) for layer in compatibility_layers]
        certification = _certification_artifact(
            certification_id=certification_id,
            dispositions=dispositions,
            certified_by=certified_by,
            certified_at=certified_at,
            status=COMPATIBILITY_RETIREMENT_CERTIFIED,
            failure_reason=None,
        )
        returned = _returned_artifact(certification)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], certification)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(certification, returned, replay_path)
    except Exception as exc:
        certification = _failed_certification_artifact(
            certification_id=certification_id,
            compatibility_layers=compatibility_layers,
            certified_by=certified_by,
            certified_at=certified_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(certification)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], certification)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(certification, returned, replay_path)


def reconstruct_compatibility_retirement_certification_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate compatibility retirement certification replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("compatibility retirement replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("compatibility retirement replay artifact must be object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    certification = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("compatibility_retirement_certification_reference") != certification["certification_id"]:
        raise FailClosedRuntimeError("compatibility retirement returned reference mismatch")
    if returned.get("compatibility_retirement_certification_hash") != certification["artifact_hash"]:
        raise FailClosedRuntimeError("compatibility retirement returned hash mismatch")
    return {
        "certification_id": certification["certification_id"],
        "certification_status": certification["certification_status"],
        "retired_layers": deepcopy(certification["retired_layers"]),
        "observational_replay_layers": deepcopy(certification["observational_replay_layers"]),
        "active_compatibility_layers": deepcopy(certification["active_compatibility_layers"]),
        "permanent_structured_authority_layers": deepcopy(
            certification["permanent_structured_authority_layers"]
        ),
        "generation2_completion_assessment": certification["generation2_completion_assessment"],
        "replay_integrity_preserved": certification["replay_integrity_preserved"],
        "rollback_capability_preserved": certification["rollback_capability_preserved"],
        "authority_boundaries_preserved": certification["authority_boundaries_preserved"],
        "runtime_behavior_changed": False,
        "governance_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _classify_layer(layer: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(layer, dict):
        raise FailClosedRuntimeError("compatibility retirement failed closed: layer must be object")
    layer_id = _require_string(layer.get("layer_id"), "layer_id")
    compatibility_layer = _require_string(layer.get("compatibility_layer"), "compatibility_layer")
    _require_string(layer.get("semantic_source"), "semantic_source")
    parity_status = _require_string(layer.get("parity_status"), "parity_status")
    replay_hash_value = _require_hash(layer.get("parity_evidence_hash"), "parity_evidence_hash")
    if layer.get("replay_integrity_verified") is not True:
        raise FailClosedRuntimeError("compatibility retirement failed closed: replay integrity not verified")
    if layer.get("rollback_capability_verified") is not True:
        raise FailClosedRuntimeError("compatibility retirement failed closed: rollback capability not verified")
    for flag in AUTHORITY_FLAGS:
        if layer.get(flag) is not True:
            raise FailClosedRuntimeError(f"compatibility retirement failed closed: {flag} missing")

    parity_certified = parity_status in PARITY_CERTIFIED_STATUSES
    permanent_authority = layer.get("permanent_structured_authority") is True
    observational_required = layer.get("observational_replay_required") is True
    retirement_candidate = layer.get("retirement_candidate") is True

    if permanent_authority:
        disposition = RETAINED_PERMANENT_STRUCTURED_AUTHORITY
        retirement_certified = False
    elif not parity_certified:
        disposition = RETAINED_ACTIVE_PARITY_NOT_PROVEN
        retirement_certified = False
    elif retirement_candidate and not observational_required:
        disposition = RETIRED_PERMANENTLY
        retirement_certified = True
    else:
        disposition = RETAINED_OBSERVATIONAL_REPLAY_EVIDENCE
        retirement_certified = False

    evidence = {
        "layer_id": layer_id,
        "compatibility_layer": compatibility_layer,
        "semantic_source": layer["semantic_source"],
        "parity_status": parity_status,
        "parity_evidence_hash": replay_hash_value,
        "rollback_capability_verified": True,
        "replay_integrity_verified": True,
        "authority_boundaries_verified": True,
        "disposition": disposition,
        "retirement_certified": retirement_certified,
        "fallback_status": layer.get("fallback_status", "FALLBACK_STATUS_NOT_REQUIRED"),
        "migration_batches": _string_list(layer.get("migration_batches")),
        "retirement_rationale": _require_string(layer.get("retirement_rationale"), "retirement_rationale"),
    }
    evidence["evidence_hash"] = replay_hash(evidence)
    return evidence


def _certification_artifact(
    *,
    certification_id: str,
    dispositions: list[dict[str, Any]],
    certified_by: str,
    certified_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    if not dispositions:
        raise FailClosedRuntimeError("compatibility retirement failed closed: at least one layer required")
    retired = _layers_by_disposition(dispositions, RETIRED_PERMANENTLY)
    observational = _layers_by_disposition(dispositions, RETAINED_OBSERVATIONAL_REPLAY_EVIDENCE)
    active = _layers_by_disposition(dispositions, RETAINED_ACTIVE_PARITY_NOT_PROVEN)
    structured = _layers_by_disposition(dispositions, RETAINED_PERMANENT_STRUCTURED_AUTHORITY)
    completion = (
        "GENERATION_2_COMPATIBILITY_RETIREMENT_CERTIFIED_WITH_ACTIVE_EXCEPTIONS"
        if active
        else "GENERATION_2_COMPATIBILITY_RETIREMENT_CERTIFIED"
    )
    artifact = {
        "artifact_type": COMPATIBILITY_RETIREMENT_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": COMPATIBILITY_RETIREMENT_CERTIFICATION_RUNTIME_VERSION,
        "certification_id": _require_string(certification_id, "certification_id"),
        "certification_status": status,
        "migration_batch_id": "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_14_COMPATIBILITY_RETIREMENT_CERTIFICATION_V1",
        "retirement_dispositions": deepcopy(dispositions),
        "retired_layers": retired,
        "observational_replay_layers": observational,
        "active_compatibility_layers": active,
        "permanent_structured_authority_layers": structured,
        "generation2_completion_assessment": completion,
        "replay_integrity_preserved": True,
        "rollback_capability_preserved": True,
        "authority_boundaries_preserved": True,
        "semantic_parity_verified": True,
        "runtime_behavior_changed": False,
        "compatibility_code_deleted": False,
        "historical_replay_reinterpreted": False,
        "governance_modified": False,
        "ocs_authority_modified": False,
        "ppp_authority_modified": False,
        "provider_authority_modified": False,
        "worker_authority_modified": False,
        "approval_authority_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "certified_by": _require_string(certified_by, "certified_by"),
        "certified_at": _require_string(certified_at, "certified_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_certification_artifact(
    *,
    certification_id: str,
    compatibility_layers: Any,
    certified_by: Any,
    certified_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": COMPATIBILITY_RETIREMENT_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": COMPATIBILITY_RETIREMENT_CERTIFICATION_RUNTIME_VERSION,
        "certification_id": certification_id if isinstance(certification_id, str) else "INVALID",
        "certification_status": FAILED_CLOSED,
        "migration_batch_id": "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_14_COMPATIBILITY_RETIREMENT_CERTIFICATION_V1",
        "retirement_dispositions": [],
        "retired_layers": [],
        "observational_replay_layers": [],
        "active_compatibility_layers": [],
        "permanent_structured_authority_layers": [],
        "submitted_layer_count": len(compatibility_layers) if isinstance(compatibility_layers, list) else 0,
        "generation2_completion_assessment": "GENERATION_2_COMPATIBILITY_RETIREMENT_FAILED_CLOSED",
        "replay_integrity_preserved": False,
        "rollback_capability_preserved": False,
        "authority_boundaries_preserved": False,
        "semantic_parity_verified": False,
        "runtime_behavior_changed": False,
        "compatibility_code_deleted": False,
        "historical_replay_reinterpreted": False,
        "governance_modified": False,
        "ocs_authority_modified": False,
        "ppp_authority_modified": False,
        "provider_authority_modified": False,
        "worker_authority_modified": False,
        "approval_authority_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "certified_by": certified_by if isinstance(certified_by, str) else None,
        "certified_at": certified_at if isinstance(certified_at, str) else None,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(certification: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(certification)
    artifact = {
        "event_type": "COMPATIBILITY_RETIREMENT_CERTIFICATION_RETURNED",
        "compatibility_retirement_certification_reference": certification["certification_id"],
        "compatibility_retirement_certification_hash": certification["artifact_hash"],
        "certification_status": certification["certification_status"],
        "generation2_completion_assessment": certification["generation2_completion_assessment"],
        "retired_layer_count": len(certification["retired_layers"]),
        "observational_replay_layer_count": len(certification["observational_replay_layers"]),
        "active_compatibility_layer_count": len(certification["active_compatibility_layers"]),
        "permanent_structured_authority_layer_count": len(
            certification["permanent_structured_authority_layers"]
        ),
        "replay_integrity_preserved": certification["replay_integrity_preserved"],
        "rollback_capability_preserved": certification["rollback_capability_preserved"],
        "authority_boundaries_preserved": certification["authority_boundaries_preserved"],
        "runtime_behavior_changed": False,
        "governance_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": certification["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(certification: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": COMPATIBILITY_RETIREMENT_CERTIFICATION_RUNTIME_VERSION,
        "certification_status": certification["certification_status"],
        "compatibility_retirement_certification_artifact": deepcopy(certification),
        "compatibility_retirement_certification_returned_artifact": deepcopy(returned),
        "compatibility_retirement_replay_reference": str(replay_path),
        "compatibility_retirement_certified": certification["certification_status"]
        == COMPATIBILITY_RETIREMENT_CERTIFIED,
        "generation2_completion_assessment": certification["generation2_completion_assessment"],
        "retired_layers": deepcopy(certification["retired_layers"]),
        "observational_replay_layers": deepcopy(certification["observational_replay_layers"]),
        "active_compatibility_layers": deepcopy(certification["active_compatibility_layers"]),
        "permanent_structured_authority_layers": deepcopy(
            certification["permanent_structured_authority_layers"]
        ),
        "replay_integrity_preserved": certification["replay_integrity_preserved"],
        "rollback_capability_preserved": certification["rollback_capability_preserved"],
        "authority_boundaries_preserved": certification["authority_boundaries_preserved"],
        "failure_reason": certification["failure_reason"],
    }
    capture["compatibility_retirement_capture_hash"] = replay_hash(capture)
    return capture


def _layers_by_disposition(dispositions: list[dict[str, Any]], disposition: str) -> list[dict[str, Any]]:
    return [deepcopy(layer) for layer in dispositions if layer["disposition"] == disposition]


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("compatibility retirement failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("compatibility retirement artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("compatibility retirement artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("compatibility retirement replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("compatibility retirement replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"compatibility retirement failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"compatibility retirement failed closed: {field_name} must be a replay hash")
    return text


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "compatibility retirement failed closed"
