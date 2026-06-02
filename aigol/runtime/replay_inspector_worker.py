"""Read-only Replay Inspector Worker for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


REPLAY_INSPECTOR_WORKER_VERSION = "REPLAY_INSPECTOR_WORKER_V1"
REPLAY_INSPECTION_REPORT_V1 = "REPLAY_INSPECTION_REPORT_V1"
REPLAY_INSPECTION_RECORDED = "REPLAY_INSPECTION_RECORDED"
REPLAY_INSPECTION_RETURNED = "REPLAY_INSPECTION_RETURNED"

INSPECTION_COMPLETED = "INSPECTION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"
CONTINUOUS = "CONTINUOUS"
BROKEN = "BROKEN"
NOT_EVALUATED = "NOT_EVALUATED"

REPLAY_STEPS = ("replay_inspection_recorded", "replay_inspection_returned")
SUPPORTED_INSPECTION_SCOPES = frozenset(
    {
        "CHAIN_SUMMARY",
        "ARTIFACT_VALIDATION",
        "REFERENCE_CONTINUITY",
        "RECENT_ACTIVITY_SUMMARY",
    }
)
FORBIDDEN_INPUT_FIELDS = frozenset(
    {
        "write_authority",
        "filesystem_write_authority",
        "mutation_authority",
        "governance_authority",
        "provider_authority",
        "worker_authority",
        "modify_replay",
        "repair_replay",
        "execution_history_mutation",
        "result_certification",
        "self_improvement",
    }
)


def inspect_replay_worker(
    *,
    inspection_id: str,
    worker_id: str,
    canonical_chain_id: str,
    replay_references: list[str | Path],
    inspection_scope: str,
    created_at: str,
    replay_dir: str | Path,
    max_artifact_count: int = 100,
) -> dict[str, Any]:
    """Inspect explicit replay references and persist a read-only worker report."""

    replay_path = Path(replay_dir)
    _ensure_worker_replay_available(replay_path)
    refs = _normalize_replay_references(replay_references)
    _ensure_output_not_inside_references(replay_path, refs)
    try:
        chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
        scope = _normalize_token(inspection_scope, "inspection_scope")
        if scope not in SUPPORTED_INSPECTION_SCOPES:
            raise FailClosedRuntimeError("replay inspector failed closed: invalid inspection scope")
        if max_artifact_count <= 0:
            raise FailClosedRuntimeError("replay inspector failed closed: max_artifact_count must be positive")
        inspected = _load_replay_references(refs, max_artifact_count=max_artifact_count)
        report = _inspection_report(
            inspection_id=inspection_id,
            worker_id=worker_id,
            canonical_chain_id=chain_id,
            inspection_scope=scope,
            replay_references=refs,
            inspected_artifacts=inspected,
            created_at=created_at,
        )
    except Exception as exc:
        report = _failed_report(
            inspection_id=inspection_id,
            worker_id=worker_id,
            canonical_chain_id=canonical_chain_id,
            inspection_scope=inspection_scope,
            replay_references=replay_references,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], report)
    returned = _inspection_returned(report)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(report, returned)


def reconstruct_replay_inspector_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Replay Inspector Worker replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("replay inspector replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("replay inspector replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "replay inspection report")
        wrappers.append(wrapper)

    report = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("inspection_reference") != report["inspection_id"]:
        raise FailClosedRuntimeError("replay inspector replay reference mismatch")
    if returned.get("inspection_hash") != report["artifact_hash"]:
        raise FailClosedRuntimeError("replay inspector replay hash mismatch")
    if returned.get("canonical_chain_id") != report["canonical_chain_id"]:
        raise FailClosedRuntimeError("replay inspector replay chain mismatch")
    _validate_report(report)
    return {
        "inspection_id": report["inspection_id"],
        "worker_id": report["worker_id"],
        "worker_type": report["worker_type"],
        "canonical_chain_id": report["canonical_chain_id"],
        "inspection_scope": report["inspection_scope"],
        "inspection_status": report["inspection_status"],
        "inspected_replay_references": deepcopy(report["inspected_replay_references"]),
        "artifact_count": report["artifact_count"],
        "artifact_types": deepcopy(report["artifact_types"]),
        "chain_continuity_status": report["chain_continuity_status"],
        "missing_references": deepcopy(report["missing_references"]),
        "corrupt_references": deepcopy(report["corrupt_references"]),
        "authority_leak_detected": report["authority_leak_detected"],
        "mutation_detected": report["mutation_detected"],
        "failure_reason": report["failure_reason"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _inspection_report(
    *,
    inspection_id: str,
    worker_id: str,
    canonical_chain_id: str,
    inspection_scope: str,
    replay_references: list[Path],
    inspected_artifacts: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    chain_status = _chain_continuity_status(inspected_artifacts, canonical_chain_id)
    if chain_status == BROKEN:
        raise FailClosedRuntimeError("replay inspector failed closed: chain mismatch")
    artifact_types = sorted({artifact.get("artifact_type", "UNKNOWN") for artifact in inspected_artifacts})
    authority_leak = _authority_leak_detected(inspected_artifacts)
    if authority_leak:
        raise FailClosedRuntimeError("replay inspector failed closed: authority-bearing replay artifact")
    report = {
        "artifact_type": REPLAY_INSPECTION_REPORT_V1,
        "replay_inspector_worker_version": REPLAY_INSPECTOR_WORKER_VERSION,
        "worker_type": REPLAY_INSPECTOR_WORKER_VERSION,
        "worker_id": _require_string(worker_id, "worker_id"),
        "inspection_id": _require_string(inspection_id, "inspection_id"),
        "canonical_chain_id": canonical_chain_id,
        "inspection_scope": inspection_scope,
        "inspection_status": INSPECTION_COMPLETED,
        "inspected_replay_references": [str(ref) for ref in replay_references],
        "artifact_count": len(inspected_artifacts),
        "artifact_types": artifact_types,
        "chain_continuity_status": chain_status,
        "missing_references": [],
        "corrupt_references": [],
        "authority_leak_detected": False,
        "mutation_detected": False,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "mutation_performed": False,
        "filesystem_modified": False,
        "runtime_state_modified": False,
        "execution_history_modified": False,
        "failure_reason": None,
        "created_at": _require_string(created_at, "created_at"),
        "read_only": True,
        "replay_visible": True,
    }
    report["artifact_hash"] = replay_hash(report)
    _validate_report(report)
    return report


def _failed_report(
    *,
    inspection_id: str,
    worker_id: str,
    canonical_chain_id: Any,
    inspection_scope: Any,
    replay_references: list[str | Path],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    report = {
        "artifact_type": REPLAY_INSPECTION_REPORT_V1,
        "replay_inspector_worker_version": REPLAY_INSPECTOR_WORKER_VERSION,
        "worker_type": REPLAY_INSPECTOR_WORKER_VERSION,
        "worker_id": _safe_string(worker_id, "INVALID_WORKER_ID"),
        "inspection_id": _safe_string(inspection_id, "INVALID_INSPECTION_ID"),
        "canonical_chain_id": _safe_string(canonical_chain_id, "INVALID_CANONICAL_CHAIN_ID"),
        "inspection_scope": _safe_string(inspection_scope, "INVALID_INSPECTION_SCOPE"),
        "inspection_status": FAILED_CLOSED,
        "inspected_replay_references": [str(ref) for ref in replay_references] if isinstance(replay_references, list) else [],
        "artifact_count": 0,
        "artifact_types": [],
        "chain_continuity_status": BROKEN,
        "missing_references": [],
        "corrupt_references": [],
        "authority_leak_detected": False,
        "mutation_detected": False,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "mutation_performed": False,
        "filesystem_modified": False,
        "runtime_state_modified": False,
        "execution_history_modified": False,
        "failure_reason": failure_reason,
        "created_at": _safe_string(created_at, "INVALID_CREATED_AT"),
        "read_only": True,
        "replay_visible": True,
    }
    report["artifact_hash"] = replay_hash(report)
    _validate_report(report)
    return report


def _inspection_returned(report: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(report, "replay inspection report")
    returned = {
        "event_type": REPLAY_INSPECTION_RETURNED,
        "inspection_reference": report["inspection_id"],
        "inspection_hash": report["artifact_hash"],
        "worker_id": report["worker_id"],
        "worker_type": report["worker_type"],
        "canonical_chain_id": report["canonical_chain_id"],
        "inspection_status": report["inspection_status"],
        "artifact_count": report["artifact_count"],
        "chain_continuity_status": report["chain_continuity_status"],
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "mutation_performed": False,
        "reconstruction_metadata": {
            "inspection_reconstructable": True,
            "read_only": True,
            "replay_modified": False,
            "governance_modified": False,
            "runtime_state_modified": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(report: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "replay_inspection_report": deepcopy(report),
        "replay_inspection_replay": deepcopy(returned),
    }
    capture["replay_inspection_capture_hash"] = replay_hash(capture)
    return capture


def _normalize_replay_references(replay_references: list[str | Path]) -> list[Path]:
    if not isinstance(replay_references, list) or not replay_references:
        raise FailClosedRuntimeError("replay inspector failed closed: replay references are required")
    refs = [Path(ref) for ref in replay_references]
    for ref in refs:
        if not ref.exists():
            raise FailClosedRuntimeError("replay inspector failed closed: missing replay reference")
        if not ref.is_file() and not ref.is_dir():
            raise FailClosedRuntimeError("replay inspector failed closed: invalid replay reference")
    if len({str(ref) for ref in refs}) != len(refs):
        raise FailClosedRuntimeError("replay inspector failed closed: duplicate replay reference")
    return refs


def _ensure_output_not_inside_references(replay_dir: Path, refs: list[Path]) -> None:
    output = replay_dir.resolve()
    for ref in refs:
        boundary = ref.resolve() if ref.is_dir() else ref.resolve().parent
        if output == boundary or _is_relative_to(output, boundary):
            raise FailClosedRuntimeError("replay inspector failed closed: output path would modify inspected replay")


def _load_replay_references(refs: list[Path], *, max_artifact_count: int) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for ref in refs:
        paths = sorted(ref.glob("*.json")) if ref.is_dir() else [ref]
        if not paths:
            raise FailClosedRuntimeError("replay inspector failed closed: missing artifacts")
        for path in paths:
            wrapper = load_json(path)
            _verify_wrapper_hash(wrapper)
            artifact = wrapper.get("artifact")
            if not isinstance(artifact, dict):
                raise FailClosedRuntimeError("replay inspector failed closed: corrupt replay")
            _verify_artifact_hash(artifact, "replay artifact")
            artifacts.append(deepcopy(artifact))
            if len(artifacts) > max_artifact_count:
                raise FailClosedRuntimeError("replay inspector failed closed: max artifact count exceeded")
    if not artifacts:
        raise FailClosedRuntimeError("replay inspector failed closed: missing artifacts")
    return artifacts


def _chain_continuity_status(artifacts: list[dict[str, Any]], canonical_chain_id: str) -> str:
    chain_values = [artifact.get("canonical_chain_id") for artifact in artifacts if "canonical_chain_id" in artifact]
    if not chain_values:
        return NOT_EVALUATED
    if all(value == canonical_chain_id for value in chain_values):
        return CONTINUOUS
    return BROKEN


def _authority_leak_detected(artifacts: list[dict[str, Any]]) -> bool:
    for artifact in artifacts:
        if any(field in artifact and artifact.get(field) is not False for field in FORBIDDEN_INPUT_FIELDS):
            return True
    return False


def _validate_report(report: dict[str, Any]) -> None:
    if report.get("artifact_type") != REPLAY_INSPECTION_REPORT_V1:
        raise FailClosedRuntimeError("replay inspector failed closed: invalid report artifact")
    if report.get("worker_type") != REPLAY_INSPECTOR_WORKER_VERSION:
        raise FailClosedRuntimeError("replay inspector failed closed: invalid worker type")
    if report.get("inspection_status") not in {INSPECTION_COMPLETED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("replay inspector failed closed: invalid inspection status")
    if report.get("inspection_status") == INSPECTION_COMPLETED and report.get("artifact_count", 0) <= 0:
        raise FailClosedRuntimeError("replay inspector failed closed: missing artifacts")
    if report.get("chain_continuity_status") not in {CONTINUOUS, BROKEN, NOT_EVALUATED}:
        raise FailClosedRuntimeError("replay inspector failed closed: invalid chain continuity")
    for field in (
        "authority_leak_detected",
        "mutation_detected",
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "mutation_performed",
        "filesystem_modified",
        "runtime_state_modified",
        "execution_history_modified",
    ):
        if report.get(field) is not False:
            raise FailClosedRuntimeError("replay inspector failed closed: read-only boundary violation")
    if report.get("read_only") is not True or report.get("replay_visible") is not True:
        raise FailClosedRuntimeError("replay inspector failed closed: read-only replay visibility missing")
    _require_string(report.get("worker_id"), "worker_id")
    _require_string(report.get("inspection_id"), "inspection_id")
    _require_string(report.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(report.get("inspection_scope"), "inspection_scope")
    _require_string(report.get("created_at"), "created_at")


def _ensure_worker_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("replay inspector replay step ordering mismatch")
    _verify_artifact_hash(artifact, "replay inspection report")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": REPLAY_INSPECTION_RECORDED if index == 0 else REPLAY_INSPECTION_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("replay inspector replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("replay inspector replay hash mismatch")


def _is_relative_to(path: Path, boundary: Path) -> bool:
    try:
        path.relative_to(boundary)
    except ValueError:
        return False
    return True


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _safe_string(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return fallback


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "replay inspector failed closed"
