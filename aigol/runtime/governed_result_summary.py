"""Standard governed result summary presentation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


SUMMARY_VERSION = "GOVERNED_RESULT_SUMMARY_V1"
ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"
AUTHORITY_BOUNDARY_REMINDER = "LLM proposes; AiGOL governs; worker executes after authorization; replay records."


def create_governed_result_summary(
    *,
    operator_flow_id: str,
    human_request: str,
    capability_used: str,
    replay_reference: str | Path,
    governed_result: dict[str, Any],
    replay_summary: dict[str, Any],
) -> dict[str, Any]:
    """Create replay-derived human-readable governed result summary."""

    if not isinstance(governed_result, dict):
        raise FailClosedRuntimeError("governed result is required")
    if not isinstance(replay_summary, dict):
        raise FailClosedRuntimeError("replay summary is required")
    final_status = _require_string(governed_result.get("final_status"), "final_status")
    accepted = final_status == "COMPLETED"
    if final_status not in {"COMPLETED", "FAILED"}:
        raise FailClosedRuntimeError("governed result final status is invalid")
    replay_verified = replay_summary.get("append_only_valid") is True
    summary = {
        "summary_version": SUMMARY_VERSION,
        "operator_flow_id": _require_string(operator_flow_id, "operator_flow_id"),
        "status": ACCEPTED if accepted else REJECTED,
        "reason": _result_reason(governed_result, accepted),
        "capability_used": _require_string(capability_used, "capability_used"),
        "human_request": _normalize_text(human_request, "human_request"),
        "replay_reference": str(Path(replay_reference)),
        "replay_verification_status": "VERIFIED" if replay_verified else "UNVERIFIED",
        "authority_boundary_reminder": AUTHORITY_BOUNDARY_REMINDER,
        "evidence_summary": _evidence_summary(governed_result, replay_summary),
        "recommended_next_action": _recommended_next_action(governed_result, replay_verified, accepted),
        "source": {
            "replay_artifact_count": replay_summary.get("replay_artifact_count"),
            "bridge_final_status": _bridge_final_status(replay_summary),
            "governed_result_hash": governed_result.get("artifact_hash"),
            "replay_hash": replay_summary.get("replay_hash"),
        },
        "non_authority": {
            "llm_execution": False,
            "worker_self_authorization": False,
            "new_capability_created": False,
            "replay_bypassed": False,
        },
    }
    summary["summary_hash"] = replay_hash(summary)
    return summary


def create_governed_failure_summary(
    *,
    operator_flow_id: str,
    human_request: str,
    capability_used: str,
    replay_reference: str | Path,
    failure_reason: str,
) -> dict[str, Any]:
    """Create deterministic rejection summary when replay evidence is unavailable."""

    summary = {
        "summary_version": SUMMARY_VERSION,
        "operator_flow_id": _require_string(operator_flow_id, "operator_flow_id"),
        "status": REJECTED,
        "reason": _require_string(failure_reason, "failure_reason"),
        "capability_used": _require_string(capability_used, "capability_used"),
        "human_request": _normalize_text(human_request, "human_request"),
        "replay_reference": str(Path(replay_reference)),
        "replay_verification_status": "UNVERIFIED",
        "authority_boundary_reminder": AUTHORITY_BOUNDARY_REMINDER,
        "evidence_summary": "Request rejected before verified governed replay evidence was available.",
        "recommended_next_action": "Review the rejection reason, correct the request, and retry as a new bounded invocation.",
        "source": {
            "replay_artifact_count": 0,
            "bridge_final_status": None,
            "governed_result_hash": None,
            "replay_hash": None,
        },
        "non_authority": {
            "llm_execution": False,
            "worker_self_authorization": False,
            "new_capability_created": False,
            "replay_bypassed": False,
        },
    }
    summary["summary_hash"] = replay_hash(summary)
    return summary


def render_governed_result_summary(summary: dict[str, Any]) -> str:
    """Render the standard summary as a stable human-readable block."""

    _verify_summary(summary)
    lines = [
        f"Status: {summary['status']}",
        f"Reason: {summary['reason']}",
        f"Capability Used: {summary['capability_used']}",
        f"Replay Reference: {summary['replay_reference']}",
        f"Replay Verification Status: {summary['replay_verification_status']}",
        f"Authority Boundary Reminder: {summary['authority_boundary_reminder']}",
        f"Evidence Summary: {summary['evidence_summary']}",
        f"Recommended Next Action: {summary['recommended_next_action']}",
    ]
    return "\n".join(lines)


def _verify_summary(summary: dict[str, Any]) -> None:
    if not isinstance(summary, dict):
        raise FailClosedRuntimeError("governed result summary must be a JSON object")
    required = {
        "summary_version",
        "operator_flow_id",
        "status",
        "reason",
        "capability_used",
        "human_request",
        "replay_reference",
        "replay_verification_status",
        "authority_boundary_reminder",
        "evidence_summary",
        "recommended_next_action",
        "source",
        "non_authority",
        "summary_hash",
    }
    if set(summary) != required:
        raise FailClosedRuntimeError("governed result summary has malformed structure")
    expected_input = deepcopy(summary)
    actual = expected_input.pop("summary_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed result summary hash mismatch")


def _result_reason(governed_result: dict[str, Any], accepted: bool) -> str:
    if accepted:
        return _require_string(governed_result.get("governed_return"), "governed_return")
    return _require_string(
        governed_result.get("failure_reason") or governed_result.get("governed_return"),
        "failure_reason",
    )


def _evidence_summary(governed_result: dict[str, Any], replay_summary: dict[str, Any]) -> str:
    final_status = _require_string(governed_result.get("final_status"), "final_status")
    capability = _require_string(governed_result.get("target_capability", "UNAVAILABLE"), "target_capability")
    artifact_count = replay_summary.get("replay_artifact_count")
    bridge_status = _bridge_final_status(replay_summary) or "UNAVAILABLE"
    return (
        f"Governed result {final_status} for {capability}; "
        f"operator replay artifacts={artifact_count}; bridge status={bridge_status}."
    )


def _recommended_next_action(governed_result: dict[str, Any], replay_verified: bool, accepted: bool) -> str:
    if not replay_verified:
        return "Do not rely on the result; inspect replay evidence before continuing."
    if accepted:
        return "Use the governed result and retain the replay reference for audit."
    reason = _result_reason(governed_result, accepted)
    if "unsupported" in reason.lower():
        return "Choose one supported read-only capability and submit a new bounded request."
    if "authorization" in reason.lower() or "unauthorized" in reason.lower():
        return "Request explicit authorization and retry as a new bounded invocation."
    if "hidden continuation" in reason.lower():
        return "Remove continuation language and retry as a single bounded request."
    return "Review the rejection reason and retry as a new bounded invocation only if still needed."


def _bridge_final_status(replay_summary: dict[str, Any]) -> str | None:
    bridge = replay_summary.get("bridge_replay")
    if isinstance(bridge, dict):
        value = bridge.get("final_status")
        if isinstance(value, str):
            return value
    return None


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
