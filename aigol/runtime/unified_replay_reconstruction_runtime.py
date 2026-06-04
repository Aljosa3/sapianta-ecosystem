"""Unified read-only replay reconstruction runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_VERSION = "UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_V1"
UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1 = "UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1"
UNIFIED_REPLAY_RECONSTRUCTION_RECORDED = "UNIFIED_REPLAY_RECONSTRUCTION_RECORDED"
UNIFIED_REPLAY_RECONSTRUCTION_RETURNED = "UNIFIED_REPLAY_RECONSTRUCTION_RETURNED"

RECONSTRUCTED = "RECONSTRUCTED"
FAILED_CLOSED = "FAILED_CLOSED"
CORRUPT = "CORRUPT"
AMBIGUOUS = "AMBIGUOUS"

REPLAY_STEPS = (
    "unified_replay_reconstruction_recorded",
    "unified_replay_reconstruction_returned",
)

SCOPES = frozenset(
    {
        "LATEST_CHAIN",
        "CHAIN_BY_ID",
        "EXECUTION_LIFECYCLE",
        "LEARNING_LIFECYCLE",
        "FULL_LINEAGE",
    }
)

EXECUTION_ARTIFACT_TYPES = frozenset(
    {
        "EXECUTION_REQUEST_ARTIFACT_V1",
        "READY_FOR_DISPATCH_ARTIFACT_V1",
        "WORKER_ASSIGNMENT_ARTIFACT_V1",
        "DISPATCH_ARTIFACT_V1",
        "WORKER_INVOCATION_ARTIFACT_V1",
        "EXECUTION_ARTIFACT_V1",
        "COMPLETION_ARTIFACT_V1",
        "RESULT_ARTIFACT_V1",
        "RESULT_EVALUATION_ARTIFACT_V1",
    }
)
LEARNING_ARTIFACT_TYPES = frozenset(
    {
        "RESULT_EVALUATION_ARTIFACT_V1",
        "IMPROVEMENT_PROPOSAL_ARTIFACT_V1",
        "IMPROVEMENT_REVIEW_ARTIFACT_V1",
        "IMPROVEMENT_APPROVAL_ARTIFACT_V1",
        "IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
    }
)
BRIDGE_ARTIFACT_TYPES = frozenset(
    {
        "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1",
    }
)
WORKER_ARTIFACT_TYPES = frozenset(
    {
        "WORKER_ARTIFACT_V1",
        "WORKER_ASSIGNMENT_ARTIFACT_V1",
        "WORKER_INVOCATION_ARTIFACT_V1",
        "REPLAY_INSPECTION_REPORT_V1",
    }
)

REFERENCE_FIELDS = {
    "execution_request_reference": "execution_request_hash",
    "implementation_plan_reference": "implementation_plan_hash",
    "improvement_approval_reference": "improvement_approval_hash",
    "improvement_review_reference": "improvement_review_hash",
    "improvement_proposal_reference": "improvement_proposal_hash",
    "evaluation_reference": "evaluation_hash",
    "result_reference": "result_hash",
    "worker_reference": "worker_hash",
    "worker_assignment_reference": "worker_assignment_hash",
    "worker_invocation_reference": "worker_invocation_hash",
    "dispatch_reference": "dispatch_hash",
    "readiness_reference": "readiness_hash",
}

ID_FIELDS = (
    "conversation_id",
    "router_id",
    "execution_request_id",
    "readiness_id",
    "worker_id",
    "worker_assignment_id",
    "dispatch_id",
    "worker_invocation_id",
    "execution_id",
    "completion_id",
    "result_id",
    "evaluation_id",
    "improvement_proposal_id",
    "improvement_review_id",
    "improvement_approval_id",
    "implementation_plan_id",
    "bridge_id",
    "inspection_id",
)

TIME_FIELDS = ("created_at", "started_at", "completed_at", "evaluated_at", "assigned_at", "dispatched_at", "invoked_at")


def reconstruct_latest_chain(
    *,
    replay_root: str | Path,
    report_dir: str | Path,
    created_at: str,
    persist_report: bool = True,
) -> dict[str, Any]:
    """Reconstruct the most recent canonical chain from replay evidence."""

    return _reconstruct(
        scope="LATEST_CHAIN",
        replay_root=Path(replay_root),
        report_dir=Path(report_dir),
        created_at=created_at,
        persist_report=persist_report,
    )


def reconstruct_chain_by_id(
    *,
    canonical_chain_id: str,
    replay_root: str | Path,
    report_dir: str | Path,
    created_at: str,
    persist_report: bool = True,
) -> dict[str, Any]:
    """Reconstruct one canonical chain by id."""

    return _reconstruct(
        scope="CHAIN_BY_ID",
        replay_root=Path(replay_root),
        report_dir=Path(report_dir),
        created_at=created_at,
        canonical_chain_id=canonical_chain_id,
        persist_report=persist_report,
    )


def reconstruct_execution_lifecycle(
    *,
    canonical_chain_id: str,
    replay_root: str | Path,
    report_dir: str | Path,
    created_at: str,
    persist_report: bool = True,
) -> dict[str, Any]:
    """Reconstruct execution lifecycle evidence for one chain."""

    return _reconstruct(
        scope="EXECUTION_LIFECYCLE",
        replay_root=Path(replay_root),
        report_dir=Path(report_dir),
        created_at=created_at,
        canonical_chain_id=canonical_chain_id,
        persist_report=persist_report,
    )


def reconstruct_learning_lifecycle(
    *,
    canonical_chain_id: str,
    replay_root: str | Path,
    report_dir: str | Path,
    created_at: str,
    persist_report: bool = True,
) -> dict[str, Any]:
    """Reconstruct governed learning lifecycle evidence for one chain."""

    return _reconstruct(
        scope="LEARNING_LIFECYCLE",
        replay_root=Path(replay_root),
        report_dir=Path(report_dir),
        created_at=created_at,
        canonical_chain_id=canonical_chain_id,
        persist_report=persist_report,
    )


def reconstruct_full_lineage(
    *,
    canonical_chain_id: str,
    replay_root: str | Path,
    report_dir: str | Path,
    created_at: str,
    persist_report: bool = True,
) -> dict[str, Any]:
    """Reconstruct full chain lineage across replay, runtime, bridge, and worker evidence."""

    return _reconstruct(
        scope="FULL_LINEAGE",
        replay_root=Path(replay_root),
        report_dir=Path(report_dir),
        created_at=created_at,
        canonical_chain_id=canonical_chain_id,
        persist_report=persist_report,
    )


def reconstruct_unified_replay_reconstruction_report(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct a persisted unified replay reconstruction report event."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("unified replay reconstruction ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("unified replay reconstruction artifact must be a JSON object")
        _verify_artifact_hash(artifact, "unified replay reconstruction report")
        wrappers.append(wrapper)

    report = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("report_reference") != report["report_id"]:
        raise FailClosedRuntimeError("unified replay reconstruction report reference mismatch")
    if returned.get("report_hash") != report["artifact_hash"]:
        raise FailClosedRuntimeError("unified replay reconstruction report hash mismatch")
    if returned.get("canonical_chain_id") != report["canonical_chain_id"]:
        raise FailClosedRuntimeError("unified replay reconstruction report chain mismatch")
    return {
        "report_id": report["report_id"],
        "canonical_chain_id": report["canonical_chain_id"],
        "reconstruction_scope": report["reconstruction_scope"],
        "reconstruction_status": report["reconstruction_status"],
        "failure_reason": report["failure_reason"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _reconstruct(
    *,
    scope: str,
    replay_root: Path,
    report_dir: Path,
    created_at: str,
    canonical_chain_id: str | None = None,
    persist_report: bool = True,
) -> dict[str, Any]:
    if scope not in SCOPES:
        raise FailClosedRuntimeError("unified replay reconstruction failed closed: invalid scope")
    if persist_report:
        _ensure_report_replay_available(report_dir)
    try:
        evidence = _scan_replay_root(replay_root, report_dir)
        chain_id = _select_chain_id(scope, canonical_chain_id, evidence)
        chain_evidence = _chain_evidence(evidence, chain_id)
        if not chain_evidence:
            raise FailClosedRuntimeError("unified replay reconstruction failed closed: missing evidence")
        _detect_multiple_chain_ownership(evidence)
        _validate_references(chain_evidence)
        report = _report(
            scope=scope,
            canonical_chain_id=chain_id,
            replay_root=replay_root,
            evidence=chain_evidence,
            created_at=created_at,
            status=RECONSTRUCTED,
            failure_reason=None,
            report_persisted=persist_report,
        )
    except Exception as exc:
        report = _failed_report(
            scope=scope,
            canonical_chain_id=canonical_chain_id,
            replay_root=replay_root,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
            report_persisted=persist_report,
        )
        if persist_report:
            _persist_report(report_dir, report)
        raise FailClosedRuntimeError(report["failure_reason"]) from exc
    if persist_report:
        _persist_report(report_dir, report)
    return _public_report(report)


def _scan_replay_root(replay_root: Path, report_dir: Path) -> list[dict[str, Any]]:
    if not replay_root.exists() or not replay_root.is_dir():
        raise FailClosedRuntimeError("unified replay reconstruction failed closed: replay root missing")
    evidence: list[dict[str, Any]] = []
    for path in sorted(replay_root.rglob("*.json")):
        if _is_report_path(path, report_dir):
            continue
        wrapper = load_json(path)
        if "replay_hash" not in wrapper or "artifact" not in wrapper:
            continue
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("unified replay reconstruction failed closed: replay artifact invalid")
        if "artifact_hash" in artifact:
            _verify_artifact_hash(artifact, "unified replay artifact")
        evidence.append(
            {
                "path": str(path),
                "replay_index": wrapper.get("replay_index"),
                "replay_step": wrapper.get("replay_step"),
                "event_type": wrapper.get("event_type") or artifact.get("event_type"),
                "wrapper_hash": wrapper["replay_hash"],
                "artifact": artifact,
            }
        )
    if not evidence:
        raise FailClosedRuntimeError("unified replay reconstruction failed closed: missing evidence")
    return evidence


def _select_chain_id(scope: str, canonical_chain_id: str | None, evidence: list[dict[str, Any]]) -> str:
    if scope == "LATEST_CHAIN":
        chains: dict[str, str] = {}
        for item in evidence:
            chain_id = item["artifact"].get("canonical_chain_id")
            if isinstance(chain_id, str) and chain_id.strip():
                chains[chain_id] = max(chains.get(chain_id, ""), _artifact_time(item["artifact"]))
        if not chains:
            raise FailClosedRuntimeError("unified replay reconstruction failed closed: missing canonical_chain_id")
        latest = sorted(chains.items(), key=lambda entry: (entry[1], entry[0]))[-1]
        return latest[0]
    if not isinstance(canonical_chain_id, str) or not canonical_chain_id.strip():
        raise FailClosedRuntimeError("unified replay reconstruction failed closed: canonical_chain_id is required")
    return canonical_chain_id


def _chain_evidence(evidence: list[dict[str, Any]], canonical_chain_id: str) -> list[dict[str, Any]]:
    selected = [
        item
        for item in evidence
        if item["artifact"].get("canonical_chain_id") == canonical_chain_id
    ]
    return sorted(selected, key=lambda item: (_artifact_time(item["artifact"]), item["path"]))


def _detect_multiple_chain_ownership(evidence: list[dict[str, Any]]) -> None:
    ownership: dict[str, set[str]] = {}
    for item in evidence:
        artifact = item["artifact"]
        chain_id = artifact.get("canonical_chain_id")
        if not isinstance(chain_id, str) or not chain_id.strip():
            continue
        identity = _artifact_identity(artifact)
        if identity is None:
            continue
        ownership.setdefault(identity, set()).add(chain_id)
    if any(len(chains) > 1 for chains in ownership.values()):
        raise FailClosedRuntimeError("unified replay reconstruction failed closed: multiple chain ownership")


def _validate_references(evidence: list[dict[str, Any]]) -> None:
    by_id: dict[str, dict[str, Any]] = {}
    for item in evidence:
        artifact = item["artifact"]
        identity = _artifact_identity(artifact)
        if identity is not None:
            by_id[identity] = artifact

    missing: list[str] = []
    invalid: list[str] = []
    for item in evidence:
        artifact = item["artifact"]
        for ref_field, hash_field in REFERENCE_FIELDS.items():
            reference = artifact.get(ref_field)
            if not isinstance(reference, str) or not reference.strip():
                continue
            if hash_field not in artifact:
                continue
            target = by_id.get(reference)
            if target is None:
                missing.append(f"{ref_field}:{reference}")
                continue
            if artifact[hash_field] != target.get("artifact_hash"):
                invalid.append(f"{ref_field}:{reference}")
    if missing:
        raise FailClosedRuntimeError("unified replay reconstruction failed closed: invalid references")
    if invalid:
        raise FailClosedRuntimeError("unified replay reconstruction failed closed: continuity failure")


def _report(
    *,
    scope: str,
    canonical_chain_id: str,
    replay_root: Path,
    evidence: list[dict[str, Any]],
    created_at: str,
    status: str,
    failure_reason: str | None,
    report_persisted: bool,
) -> dict[str, Any]:
    artifact_refs = [_artifact_ref(item) for item in evidence]
    report = {
        "artifact_type": UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1,
        "unified_replay_reconstruction_runtime_version": UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_VERSION,
        "report_id": f"{scope}:{canonical_chain_id}:{replay_hash(artifact_refs)}",
        "canonical_chain_id": canonical_chain_id,
        "reconstruction_scope": scope,
        "reconstruction_status": status,
        "replay_root": str(replay_root),
        "report_persisted": report_persisted,
        "operationally_read_only": not report_persisted,
        "conversation": _section(evidence, _is_conversation_evidence),
        "source_routing": _section(evidence, _is_source_routing_evidence),
        "execution_lifecycle": _section(evidence, lambda item: _artifact_type(item) in EXECUTION_ARTIFACT_TYPES),
        "learning_lifecycle": _section(evidence, lambda item: _artifact_type(item) in LEARNING_ARTIFACT_TYPES),
        "implementation_execution_bridge": _section(evidence, _is_bridge_evidence),
        "worker_evidence": _section(evidence, lambda item: _artifact_type(item) in WORKER_ARTIFACT_TYPES),
        "replay_evidence": {
            "artifact_count": len(evidence),
            "replay_hash": replay_hash(artifact_refs),
            "artifacts": artifact_refs,
        },
        "detected_failures": {
            "missing_evidence": False,
            "chain_corruption": False,
            "hash_mismatch": False,
            "continuity_failures": False,
            "invalid_references": False,
            "ambiguous_lineage": False,
            "multiple_chain_ownership": False,
        },
        "authority_boundary": {
            "llm_proposes": True,
            "aigol_governs": True,
            "human_authorizes": True,
            "worker_executes": True,
            "replay_records": True,
            "read_only_reconstruction": True,
            "execution_requests_created": False,
            "workers_dispatched": False,
            "workers_invoked": False,
            "inspection_report_persisted": report_persisted,
        },
        "failure_reason": failure_reason,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    report["artifact_hash"] = replay_hash(report)
    return report


def _failed_report(
    *,
    scope: str,
    canonical_chain_id: str | None,
    replay_root: Path,
    created_at: str,
    failure_reason: str,
    report_persisted: bool,
) -> dict[str, Any]:
    chain_id = canonical_chain_id if isinstance(canonical_chain_id, str) and canonical_chain_id.strip() else "UNRESOLVED"
    report = {
        "artifact_type": UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1,
        "unified_replay_reconstruction_runtime_version": UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_VERSION,
        "report_id": f"{scope}:{chain_id}:FAILED_CLOSED:{replay_hash(failure_reason)}",
        "canonical_chain_id": chain_id,
        "reconstruction_scope": scope,
        "reconstruction_status": FAILED_CLOSED,
        "replay_root": str(replay_root),
        "report_persisted": report_persisted,
        "operationally_read_only": not report_persisted,
        "conversation": _empty_section(),
        "source_routing": _empty_section(),
        "execution_lifecycle": _empty_section(),
        "learning_lifecycle": _empty_section(),
        "implementation_execution_bridge": _empty_section(),
        "worker_evidence": _empty_section(),
        "replay_evidence": {"artifact_count": 0, "replay_hash": replay_hash([]), "artifacts": []},
        "detected_failures": _failure_flags(failure_reason),
        "authority_boundary": {
            "llm_proposes": True,
            "aigol_governs": True,
            "human_authorizes": True,
            "worker_executes": True,
            "replay_records": True,
            "read_only_reconstruction": True,
            "execution_requests_created": False,
            "workers_dispatched": False,
            "workers_invoked": False,
            "inspection_report_persisted": report_persisted,
        },
        "failure_reason": failure_reason,
        "created_at": _safe_string(created_at, "INVALID_CREATED_AT"),
        "replay_visible": True,
    }
    report["artifact_hash"] = replay_hash(report)
    return report


def _persist_report(report_dir: Path, report: dict[str, Any]) -> None:
    _persist_step(report_dir, 0, REPLAY_STEPS[0], UNIFIED_REPLAY_RECONSTRUCTION_RECORDED, report)
    returned = {
        "event_type": UNIFIED_REPLAY_RECONSTRUCTION_RETURNED,
        "report_reference": report["report_id"],
        "report_hash": report["artifact_hash"],
        "canonical_chain_id": report["canonical_chain_id"],
        "reconstruction_scope": report["reconstruction_scope"],
        "reconstruction_status": report["reconstruction_status"],
        "failure_reason": report["failure_reason"],
        "read_only_reconstruction": True,
        "execution_requests_created": False,
        "workers_dispatched": False,
        "workers_invoked": False,
        "replay_visible": True,
    }
    returned["artifact_hash"] = replay_hash(returned)
    _persist_step(report_dir, 1, REPLAY_STEPS[1], UNIFIED_REPLAY_RECONSTRUCTION_RETURNED, returned)


def _persist_step(report_dir: Path, index: int, step: str, event_type: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "unified replay reconstruction report")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": event_type,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(report_dir / f"{index:03d}_{step}.json", wrapper)


def _ensure_report_replay_available(report_dir: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = report_dir / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _section(evidence: list[dict[str, Any]], predicate) -> dict[str, Any]:
    items = [_artifact_ref(item) for item in evidence if predicate(item)]
    return {
        "present": bool(items),
        "artifact_count": len(items),
        "artifacts": items,
        "replay_hash": replay_hash(items),
    }


def _empty_section() -> dict[str, Any]:
    return {"present": False, "artifact_count": 0, "artifacts": [], "replay_hash": replay_hash([])}


def _public_report(report: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(report)


def _artifact_ref(item: dict[str, Any]) -> dict[str, Any]:
    artifact = item["artifact"]
    return {
        "path": item["path"],
        "replay_step": item["replay_step"],
        "event_type": item["event_type"],
        "artifact_type": _artifact_type(item),
        "artifact_id": _artifact_identity(artifact),
        "artifact_hash": artifact.get("artifact_hash"),
        "wrapper_hash": item["wrapper_hash"],
        "created_at": _artifact_time(artifact),
    }


def _artifact_identity(artifact: dict[str, Any]) -> str | None:
    for field in ID_FIELDS:
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _artifact_type(item: dict[str, Any]) -> str:
    artifact = item["artifact"]
    value = artifact.get("artifact_type") or artifact.get("event_type") or item.get("event_type")
    return value if isinstance(value, str) and value.strip() else "UNKNOWN"


def _artifact_time(artifact: dict[str, Any]) -> str:
    for field in TIME_FIELDS:
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _is_conversation_evidence(item: dict[str, Any]) -> bool:
    artifact_type = _artifact_type(item)
    return artifact_type.startswith("CONVERSATION_") or artifact_type == "CONVERSATION_RESPONSE_ARTIFACT_V1"


def _is_source_routing_evidence(item: dict[str, Any]) -> bool:
    return _artifact_type(item) == "SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1"


def _is_bridge_evidence(item: dict[str, Any]) -> bool:
    artifact = item["artifact"]
    return (
        _artifact_type(item) in BRIDGE_ARTIFACT_TYPES
        or artifact.get("execution_request_source_type") == "IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1"
    )


def _is_report_path(path: Path, report_dir: Path) -> bool:
    try:
        path.relative_to(report_dir)
        return True
    except ValueError:
        return False


def _failure_flags(reason: str) -> dict[str, bool]:
    lowered = reason.lower()
    return {
        "missing_evidence": "missing evidence" in lowered,
        "chain_corruption": "corrupt" in lowered or "corruption" in lowered,
        "hash_mismatch": "hash mismatch" in lowered,
        "continuity_failures": "continuity" in lowered,
        "invalid_references": "invalid references" in lowered,
        "ambiguous_lineage": "ambiguous" in lowered,
        "multiple_chain_ownership": "multiple chain ownership" in lowered,
    }


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("unified replay reconstruction failed closed: replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"unified replay reconstruction failed closed: {field_name} is required")
    return value


def _safe_string(value: Any, fallback: str) -> str:
    return value if isinstance(value, str) and value.strip() else fallback
