"""Human-friendly replay-visible operator summary runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OPERATOR_SUMMARY_RUNTIME_VERSION = "AIGOL_OPERATOR_SUMMARY_RUNTIME_V1"
OPERATOR_SUMMARY_ARTIFACT_V1 = "OPERATOR_SUMMARY_ARTIFACT_V1"
OPERATOR_SUMMARY_CREATED = "OPERATOR_SUMMARY_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "operator_summary_recorded",
    "operator_summary_returned",
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_lifecycle_modification": False,
    "authorizes_automatic_implementation": False,
    "creates_approval": False,
}


def create_operator_summary(
    *,
    operator_summary_id: str,
    lifecycle_input: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    source_replay_reference: str | None = None,
) -> dict[str, Any]:
    """Create a concise operator summary without modifying lifecycle evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lifecycle = _validate_lifecycle_input(lifecycle_input)
        translation = _translate_lifecycle(lifecycle)
        artifact = _summary_artifact(
            operator_summary_id=operator_summary_id,
            lifecycle_input=lifecycle,
            translation=translation,
            created_at=created_at,
            source_replay_reference=source_replay_reference,
            summary_status=OPERATOR_SUMMARY_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_summary_artifact(
            operator_summary_id=operator_summary_id,
            lifecycle_input=lifecycle_input if isinstance(lifecycle_input, dict) else {},
            created_at=created_at,
            source_replay_reference=source_replay_reference,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_operator_summary_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct operator summary replay evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("operator summary replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("operator summary replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    summary = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("operator_summary_reference") != summary["operator_summary_id"]:
        raise FailClosedRuntimeError("operator summary returned reference mismatch")
    if returned.get("operator_summary_artifact_hash") != summary["artifact_hash"]:
        raise FailClosedRuntimeError("operator summary returned artifact hash mismatch")
    if returned.get("operator_summary_hash") != summary["operator_summary_hash"]:
        raise FailClosedRuntimeError("operator summary returned summary hash mismatch")
    if summary.get("operator_summary_hash") != _compute_operator_summary_hash(summary):
        raise FailClosedRuntimeError("operator summary hash mismatch")
    return {
        "operator_summary_id": summary["operator_summary_id"],
        "summary_status": summary["summary_status"],
        "operator_summary_hash": summary["operator_summary_hash"],
        "headline": summary["headline"],
        "details": deepcopy(summary["details"]),
        "operator_next_steps": deepcopy(summary["operator_next_steps"]),
        "technical_stage_groups": deepcopy(summary["technical_stage_groups"]),
        "source_lifecycle_hash": summary["source_lifecycle_hash"],
        "source_replay_reference": summary["source_replay_reference"],
        "read_only": True,
        "replay_visible": True,
        "authority_flags": deepcopy(summary["authority_flags"]),
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "failure_reason": summary["failure_reason"],
    }


def render_operator_summary(capture: dict[str, Any]) -> str:
    """Render the compact operator summary."""

    lines = ["", "Operator Summary", "", str(capture.get("headline") or "Summary unavailable.")]
    for detail in capture.get("details") or []:
        lines.append(f"- {detail}")
    next_steps = capture.get("operator_next_steps") or []
    if next_steps:
        lines.extend(["", "Next Steps"])
        lines.extend(f"- {step}" for step in next_steps)
    if capture.get("failure_reason"):
        lines.extend(["", f"failure_reason: {capture['failure_reason']}"])
    return "\n".join(lines)


def _validate_lifecycle_input(lifecycle_input: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(lifecycle_input, dict):
        raise FailClosedRuntimeError("operator summary failed closed: lifecycle input must be a JSON object")
    lifecycle = deepcopy(lifecycle_input)
    replay_hash(lifecycle)
    return lifecycle


def _translate_lifecycle(lifecycle: dict[str, Any]) -> dict[str, Any]:
    statuses = _collect_statuses(lifecycle)
    technical_groups = _technical_stage_groups(statuses)
    target = _target_label(lifecycle)

    if _has_status(statuses, "FAILED_CLOSED") or lifecycle.get("fail_closed") is True:
        reason = str(lifecycle.get("failure_reason") or "The operation failed closed.")
        return {
            "headline": "Operation failed closed.",
            "details": [_normalize_sentence(reason), "No lifecycle authority was changed by this summary."],
            "operator_next_steps": ["Inspect the replay evidence before retrying."],
            "technical_stage_groups": technical_groups,
        }

    if _has_status(statuses, "HUMAN_APPROVAL_REQUIRED"):
        return {
            "headline": "Human decision required.",
            "details": [
                _with_target("AiGOL prepared a governed proposal that requires operator approval", target),
                "No implementation or execution has been authorized by this summary.",
            ],
            "operator_next_steps": ["Choose APPROVE, REJECT, or REQUEST_MODIFICATION."],
            "technical_stage_groups": technical_groups,
        }

    if _has_status(statuses, "GOVERNED_REJECTION_RECORDED") or _has_status(statuses, "GOVERNED_REJECTION_TERMINATED"):
        return {
            "headline": "Request rejected and closed.",
            "details": ["The human rejection was recorded as replay-visible evidence."],
            "operator_next_steps": ["Start a new request if different work is needed."],
            "technical_stage_groups": technical_groups,
        }

    if _has_status(statuses, "MODIFICATION_REQUEST_RECORDED") or _has_status(statuses, "CLARIFICATION_REQUIRED"):
        return {
            "headline": "Modification requested; clarification is required.",
            "details": ["The modification request was recorded and no implementation was performed."],
            "operator_next_steps": ["Describe the requested modification in the next message."],
            "technical_stage_groups": technical_groups,
        }

    if _has_status(statuses, "HUMAN_CLARIFICATION_REQUIRED"):
        return {
            "headline": "Clarification required.",
            "details": ["AiGOL needs a more specific operator choice before continuing."],
            "operator_next_steps": ["Answer the clarification prompt with one intended interpretation."],
            "technical_stage_groups": technical_groups,
        }

    if _has_status(statuses, "EXECUTABLE_BUNDLE_VERIFIED"):
        return {
            "headline": "Domain bundle created and verified.",
            "details": [
                _with_target("AiGOL created the authorized create-only domain bundle", target),
                "Replay review completed and the operation was terminated.",
            ],
            "operator_next_steps": ["Use replay inspection for detailed lineage."],
            "technical_stage_groups": technical_groups,
        }

    if _has_status(statuses, "TERMINATED") and (
        _has_status(statuses, "REVIEW_COMPLETED") or _has_status(statuses, "RESULT_VALIDATED")
    ):
        return {
            "headline": "Operation completed and verified.",
            "details": [
                _with_target("The governed lifecycle completed successfully", target),
                "No new authority is created by this operator summary.",
            ],
            "operator_next_steps": ["Use replay inspection for detailed lineage."],
            "technical_stage_groups": technical_groups,
        }

    if _has_any(
        statuses,
        {
            "WORKER_ASSIGNED",
            "WORKER_DISPATCHED",
            "WORKER_INVOKED",
            "WORKER_RESULT_CAPTURED",
            "PROVIDER_PROPOSAL_PRODUCED",
            "DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED",
        },
    ):
        return {
            "headline": "Provider selected and proposal processed successfully.",
            "details": [
                _with_target("AiGOL processed the governed provider/proposal lifecycle", target),
                "This summary does not authorize real implementation.",
            ],
            "operator_next_steps": ["Continue only through the governed approval or replay path."],
            "technical_stage_groups": technical_groups,
        }

    return {
        "headline": "Lifecycle summary recorded.",
        "details": ["AiGOL recorded a read-only operator summary for the supplied lifecycle evidence."],
        "operator_next_steps": ["Inspect replay evidence for detailed lifecycle state."],
        "technical_stage_groups": technical_groups,
    }


def _collect_statuses(value: Any) -> list[str]:
    statuses: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if "status" in str(key).lower() and isinstance(item, str):
                statuses.append(item)
            else:
                statuses.extend(_collect_statuses(item))
    elif isinstance(value, list):
        for item in value:
            statuses.extend(_collect_statuses(item))
    return sorted(set(statuses))


def _technical_stage_groups(statuses: list[str]) -> dict[str, list[str]]:
    groups = {
        "handoff_and_proposal": [],
        "human_decision": [],
        "execution_preparation": [],
        "worker_lifecycle": [],
        "validation_review_termination": [],
        "artifact_creation": [],
        "failure": [],
    }
    for status in statuses:
        lowered = status.lower()
        if "proposal" in lowered or "handoff" in lowered or "ppp" in lowered:
            groups["handoff_and_proposal"].append(status)
        elif "approval" in lowered or "decision" in lowered or "reject" in lowered or "modification" in lowered:
            groups["human_decision"].append(status)
        elif "execution" in lowered or "authorization" in lowered or "ready" in lowered:
            groups["execution_preparation"].append(status)
        elif "worker" in lowered or "dispatch" in lowered or "invoked" in lowered:
            groups["worker_lifecycle"].append(status)
        elif "validated" in lowered or "review" in lowered or "terminated" in lowered:
            groups["validation_review_termination"].append(status)
        elif "bundle" in lowered or "artifact" in lowered or "created" in lowered:
            groups["artifact_creation"].append(status)
        elif "failed" in lowered:
            groups["failure"].append(status)
    return {key: sorted(set(values)) for key, values in groups.items() if values}


def _target_label(lifecycle: dict[str, Any]) -> str | None:
    for key in ("target_domain", "domain_id", "domain", "target_resource", "target_worker", "bundle_id"):
        value = lifecycle.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for value in lifecycle.values():
        if isinstance(value, dict):
            target = _target_label(value)
            if target:
                return target
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    target = _target_label(item)
                    if target:
                        return target
    return None


def _summary_artifact(
    *,
    operator_summary_id: str,
    lifecycle_input: dict[str, Any],
    translation: dict[str, Any],
    created_at: str,
    source_replay_reference: str | None,
    summary_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OPERATOR_SUMMARY_ARTIFACT_V1,
        "runtime_version": AIGOL_OPERATOR_SUMMARY_RUNTIME_VERSION,
        "operator_summary_id": _require_string(operator_summary_id, "operator_summary_id"),
        "created_at": _require_string(created_at, "created_at"),
        "summary_status": summary_status,
        "headline": translation["headline"],
        "details": list(translation["details"]),
        "operator_next_steps": list(translation["operator_next_steps"]),
        "technical_stage_groups": deepcopy(translation["technical_stage_groups"]),
        "source_lifecycle_hash": replay_hash(lifecycle_input),
        "source_replay_reference": source_replay_reference,
        "read_only": True,
        "replay_visible": True,
        "source_replay_mutated": False,
        "lifecycle_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["operator_summary_hash"] = _compute_operator_summary_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_summary_artifact(
    *,
    operator_summary_id: str,
    lifecycle_input: dict[str, Any],
    created_at: str,
    source_replay_reference: str | None,
    failure_reason: str,
) -> dict[str, Any]:
    return _summary_artifact(
        operator_summary_id=operator_summary_id,
        lifecycle_input=lifecycle_input,
        translation={
            "headline": "Operator summary failed closed.",
            "details": [_normalize_sentence(failure_reason)],
            "operator_next_steps": ["Inspect the source lifecycle evidence."],
            "technical_stage_groups": {"failure": [FAILED_CLOSED]},
        },
        created_at=created_at,
        source_replay_reference=source_replay_reference,
        summary_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(summary: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(summary)
    returned = {
        "artifact_type": "OPERATOR_SUMMARY_RETURNED_V1",
        "runtime_version": AIGOL_OPERATOR_SUMMARY_RUNTIME_VERSION,
        "event_type": "OPERATOR_SUMMARY_RETURNED",
        "operator_summary_reference": summary["operator_summary_id"],
        "operator_summary_artifact_hash": summary["artifact_hash"],
        "operator_summary_hash": summary["operator_summary_hash"],
        "summary_status": summary["summary_status"],
        "headline": summary["headline"],
        "read_only": True,
        "replay_visible": True,
        "source_replay_mutated": False,
        "lifecycle_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(summary: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "operator_summary_artifact": deepcopy(summary),
        "operator_summary_returned": deepcopy(returned),
        "operator_summary_replay_reference": str(replay_path),
        "operator_summary_id": summary["operator_summary_id"],
        "summary_status": summary["summary_status"],
        "operator_summary_hash": summary["operator_summary_hash"],
        "headline": summary["headline"],
        "details": deepcopy(summary["details"]),
        "operator_next_steps": deepcopy(summary["operator_next_steps"]),
        "technical_stage_groups": deepcopy(summary["technical_stage_groups"]),
        "source_lifecycle_hash": summary["source_lifecycle_hash"],
        "source_replay_reference": summary["source_replay_reference"],
        "read_only": True,
        "replay_visible": True,
        "source_replay_mutated": False,
        "lifecycle_modified": False,
        "authority_flags": deepcopy(summary["authority_flags"]),
        "failure_reason": summary["failure_reason"],
        "fail_closed": summary["summary_status"] == FAILED_CLOSED,
    }
    capture["operator_summary_capture_hash"] = replay_hash(capture)
    return capture


def _compute_operator_summary_hash(summary: dict[str, Any]) -> str:
    return replay_hash(
        {
            "operator_summary_id": summary["operator_summary_id"],
            "summary_status": summary["summary_status"],
            "headline": summary["headline"],
            "details": summary["details"],
            "operator_next_steps": summary["operator_next_steps"],
            "technical_stage_groups": summary["technical_stage_groups"],
            "source_lifecycle_hash": summary["source_lifecycle_hash"],
            "source_replay_reference": summary["source_replay_reference"],
            "read_only": summary["read_only"],
            "source_replay_mutated": summary["source_replay_mutated"],
            "lifecycle_modified": summary["lifecycle_modified"],
            "authority_flags": summary["authority_flags"],
            "failure_reason": summary["failure_reason"],
        }
    )


def _has_status(statuses: list[str], status: str) -> bool:
    return status in statuses


def _has_any(statuses: list[str], values: set[str]) -> bool:
    return any(status in values for status in statuses)


def _with_target(message: str, target: str | None) -> str:
    if target:
        return f"{message} for {target}."
    return f"{message}."


def _normalize_sentence(value: str) -> str:
    text = value.strip()
    if not text:
        return "The operation failed closed."
    if text.endswith((".", "!", "?")):
        return text
    return text + "."


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("operator summary failed closed: replay artifact already exists")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        return


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual:
        raise FailClosedRuntimeError("operator summary artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("operator summary artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("operator summary replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("operator summary replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"operator summary failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "operator summary failed closed"


__all__ = [
    "AIGOL_OPERATOR_SUMMARY_RUNTIME_VERSION",
    "OPERATOR_SUMMARY_ARTIFACT_V1",
    "OPERATOR_SUMMARY_CREATED",
    "create_operator_summary",
    "reconstruct_operator_summary_replay",
    "render_operator_summary",
]

