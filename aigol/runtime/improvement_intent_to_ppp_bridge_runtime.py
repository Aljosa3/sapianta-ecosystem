"""Governed bridge from certified improvement intent to PPP candidate intake."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_to_improvement_intent_runtime import (
    IMPROVEMENT_INTENT_ARTIFACT_V1,
    IMPROVEMENT_INTENT_CREATED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_IMPROVEMENT_INTENT_TO_PPP_BRIDGE_VERSION = "AIGOL_IMPROVEMENT_INTENT_TO_PPP_BRIDGE_V1"
PPP_CANDIDATE_ARTIFACT_V1 = "PPP_CANDIDATE_ARTIFACT_V1"
PPP_CANDIDATE_CREATED = "PPP_CANDIDATE_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ppp_candidate_recorded",
    "ppp_candidate_returned",
)


def bridge_improvement_intent_to_ppp_candidate(
    *,
    bridge_id: str,
    improvement_intent_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    affected_lifecycle_stage: str = "IMPROVEMENT_INTENT",
) -> dict[str, Any]:
    """Create a PPP intake candidate without invoking PPP or authorizing implementation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        intent = deepcopy(improvement_intent_artifact)
        _validate_improvement_intent(intent)
        candidate = _ppp_candidate_artifact(
            bridge_id=bridge_id,
            intent=intent,
            created_at=created_at,
            affected_lifecycle_stage=affected_lifecycle_stage,
            candidate_status=PPP_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(candidate)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(candidate, returned, replay_path)
    except Exception as exc:
        candidate = _failed_ppp_candidate_artifact(
            bridge_id=bridge_id,
            improvement_intent_artifact=improvement_intent_artifact,
            created_at=created_at,
            affected_lifecycle_stage=affected_lifecycle_stage,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(candidate)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], candidate)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(candidate, returned, replay_path)


def reconstruct_improvement_intent_to_ppp_bridge_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify improvement intent to PPP candidate bridge replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("improvement intent to PPP bridge replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("improvement intent to PPP bridge replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    candidate = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("ppp_candidate_reference") != candidate["ppp_candidate_id"]:
        raise FailClosedRuntimeError("improvement intent to PPP bridge candidate reference mismatch")
    if returned.get("ppp_candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("improvement intent to PPP bridge candidate hash mismatch")
    return {
        "ppp_candidate_id": candidate["ppp_candidate_id"],
        "candidate_status": candidate["candidate_status"],
        "source_improvement_intent": candidate["source_improvement_intent"],
        "source_gap_reference": candidate["source_gap_reference"],
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "implementation_prevented": candidate["implementation_authorized"] is False
        and candidate["implementation_applied"] is False,
        "ready_for_governed_implementation_requests": candidate["candidate_status"] == PPP_CANDIDATE_CREATED
        and candidate["human_approval_required"] is True,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_improvement_intent(intent: dict[str, Any]) -> None:
    _validate_artifact(intent)
    if intent.get("artifact_type") != IMPROVEMENT_INTENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: invalid artifact type")
    if intent.get("intent_status") != IMPROVEMENT_INTENT_CREATED:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: certified intent required")
    if intent.get("ppp_eligible") is not True:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: intent is not PPP eligible")
    if intent.get("human_review_required") is not True:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: human review required")
    _require_string(intent.get("gap_reference"), "gap_reference")
    _require_hash(intent.get("gap_hash"), "gap_hash")
    if not _string_list(intent.get("source_replay_reference")):
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: source replay references required")
    if not _hash_list(intent.get("source_replay_hash")):
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: source replay hashes required")
    if intent.get("proposal_created") is not False:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: proposal already created")
    if intent.get("ppp_invoked") is not False:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: PPP already invoked")
    if intent.get("implementation_authorized") is not False:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: implementation already authorized")
    if intent.get("implementation_applied") is not False:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: implementation already applied")
    if intent.get("execution_requested") is not False:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: execution already requested")
    if intent.get("governance_mutated") is not False or intent.get("replay_mutated") is not False:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: mutation boundary violated")
    if intent.get("self_modification_authority") is not False:
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: self-modification authority present")


def _ppp_candidate_artifact(
    *,
    bridge_id: str,
    intent: dict[str, Any],
    created_at: str,
    affected_lifecycle_stage: str,
    candidate_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PPP_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_TO_PPP_BRIDGE_VERSION,
        "ppp_candidate_id": f"{_require_string(bridge_id, 'bridge_id')}:PPP-CANDIDATE",
        "bridge_id": bridge_id,
        "candidate_status": candidate_status,
        "source_improvement_intent": intent["improvement_intent_id"],
        "source_improvement_intent_hash": intent["artifact_hash"],
        "source_gap_reference": intent["gap_reference"],
        "source_gap_hash": intent["gap_hash"],
        "source_replay_references": deepcopy(intent["source_replay_reference"]),
        "source_replay_hashes": deepcopy(intent["source_replay_hash"]),
        "proposal_summary": intent["intent_summary"],
        "affected_runtime": intent["affected_layer"],
        "affected_domain": intent["affected_domain"],
        "affected_worker_family": intent["affected_worker_family"],
        "affected_lifecycle_stage": _require_string(affected_lifecycle_stage, "affected_lifecycle_stage"),
        "governance_classification": {
            "improvement_class": intent["improvement_class"],
            "confidence": intent["confidence"],
            "high_risk_domain": intent["high_risk_domain"],
            "human_review_required": intent["human_review_required"],
            "source": "CERTIFIED_IMPROVEMENT_INTENT",
        },
        "human_approval_requirement": "MANDATORY",
        "human_approval_required": True,
        "approval_granted": False,
        "replay_lineage_preserved": True,
        "certification_status": "CERTIFIED_IMPROVEMENT_INTENT_ACCEPTED",
        "ppp_intake_ready": True,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "implementation_authorized": False,
        "implementation_applied": False,
        "code_modified": False,
        "governance_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_ppp_candidate_artifact(
    *,
    bridge_id: str,
    improvement_intent_artifact: dict[str, Any],
    created_at: str,
    affected_lifecycle_stage: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PPP_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_TO_PPP_BRIDGE_VERSION,
        "ppp_candidate_id": f"{bridge_id}:PPP-CANDIDATE" if isinstance(bridge_id, str) else "INVALID:PPP-CANDIDATE",
        "bridge_id": bridge_id if isinstance(bridge_id, str) else "INVALID",
        "candidate_status": FAILED_CLOSED,
        "source_improvement_intent": improvement_intent_artifact.get("improvement_intent_id")
        if isinstance(improvement_intent_artifact, dict)
        else None,
        "source_improvement_intent_hash": improvement_intent_artifact.get("artifact_hash")
        if isinstance(improvement_intent_artifact, dict)
        else None,
        "source_gap_reference": improvement_intent_artifact.get("gap_reference")
        if isinstance(improvement_intent_artifact, dict)
        else None,
        "source_gap_hash": improvement_intent_artifact.get("gap_hash")
        if isinstance(improvement_intent_artifact, dict)
        else None,
        "source_replay_references": [],
        "source_replay_hashes": [],
        "proposal_summary": None,
        "affected_runtime": None,
        "affected_domain": None,
        "affected_worker_family": None,
        "affected_lifecycle_stage": affected_lifecycle_stage if isinstance(affected_lifecycle_stage, str) else None,
        "governance_classification": {},
        "human_approval_requirement": "MANDATORY",
        "human_approval_required": True,
        "approval_granted": False,
        "replay_lineage_preserved": False,
        "certification_status": FAILED_CLOSED,
        "ppp_intake_ready": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "implementation_authorized": False,
        "implementation_applied": False,
        "code_modified": False,
        "governance_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at if isinstance(created_at, str) else None,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(candidate: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(candidate)
    artifact = {
        "event_type": "PPP_CANDIDATE_RETURNED",
        "ppp_candidate_reference": candidate["ppp_candidate_id"],
        "ppp_candidate_hash": candidate["artifact_hash"],
        "candidate_status": candidate["candidate_status"],
        "source_improvement_intent": candidate["source_improvement_intent"],
        "human_approval_required": candidate["human_approval_required"],
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "implementation_authorized": False,
        "implementation_applied": False,
        "authorization_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": candidate["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(candidate: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_TO_PPP_BRIDGE_VERSION,
        "candidate_status": candidate["candidate_status"],
        "ppp_candidate_artifact": deepcopy(candidate),
        "ppp_candidate_returned_artifact": deepcopy(returned),
        "ppp_candidate_replay_reference": str(replay_path),
        "ppp_candidate_artifact_generated": candidate["candidate_status"] == PPP_CANDIDATE_CREATED,
        "replay_lineage_preserved": candidate["replay_lineage_preserved"],
        "human_approval_required": candidate["human_approval_required"],
        "implementation_prevented": candidate["implementation_authorized"] is False
        and candidate["implementation_applied"] is False,
        "ready_for_governed_implementation_requests": candidate["candidate_status"] == PPP_CANDIDATE_CREATED
        and candidate["human_approval_required"] is True,
        "failure_reason": candidate["failure_reason"],
    }
    capture["improvement_intent_to_ppp_bridge_capture_hash"] = replay_hash(capture)
    return capture


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
            raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("improvement intent to PPP bridge failed closed: artifact must be a JSON object")
    _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("improvement intent to PPP bridge artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("improvement intent to PPP bridge artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("improvement intent to PPP bridge replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("improvement intent to PPP bridge replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"improvement intent to PPP bridge failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"improvement intent to PPP bridge failed closed: {field_name} must be a replay hash")
    return text


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _hash_list(value: Any) -> list[str]:
    return [item for item in _string_list(value) if item.startswith("sha256:")]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "improvement intent to PPP bridge failed closed"
