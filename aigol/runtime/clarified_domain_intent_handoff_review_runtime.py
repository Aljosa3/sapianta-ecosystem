"""Governed review of clarified domain intent after clarification resume."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.clarification_continuity_runtime import (
    CLARIFICATION_WORKFLOW_RESUME_ARTIFACT_V1,
    WORKFLOW_RESUME_READY,
    reconstruct_clarification_continuity_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unknown_domain_clarification_runtime import CREATE_DOMAIN
from aigol.workers.domain_artifact_worker import (
    AUTHORIZED_SCOPE as DOMAIN_ARTIFACT_AUTHORIZED_SCOPE,
    DOMAIN_ARTIFACT_WORKER_ID,
    DOMAIN_DEFINITION_ARTIFACT_V1,
    DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1,
    DOMAIN_METADATA_ARTIFACT_V1,
    DOMAIN_REGISTRATION_ARTIFACT_V1,
    OPERATION_AUTHOR_DOMAIN_ARTIFACTS,
)


AIGOL_CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW_RUNTIME_VERSION = (
    "AIGOL_CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW_RUNTIME_V1"
)
HANDOFF_REVIEW_DECISION_ARTIFACT_V1 = "HANDOFF_REVIEW_DECISION_ARTIFACT_V1"
HANDOFF_REVIEW_RETURNED_ARTIFACT_V1 = "HANDOFF_REVIEW_RETURNED_ARTIFACT_V1"

OCS_HANDOFF_APPROVED = "OCS_HANDOFF_APPROVED"
WORKER_BINDING_APPROVED = "WORKER_BINDING_APPROVED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
FAIL_CLOSED = "FAIL_CLOSED"

ALLOWED_REVIEW_DECISIONS = frozenset(
    {
        OCS_HANDOFF_APPROVED,
        WORKER_BINDING_APPROVED,
        CLARIFICATION_REQUIRED,
    }
)
REPLAY_STEPS = ("handoff_review_decision_recorded", "handoff_review_returned")

AUTHORITY_FLAGS = {
    "provider_invoked": False,
    "ocs_authority": False,
    "approval_created": False,
    "authorization_created": False,
    "worker_request_created": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "execution_started": False,
    "domain_created": False,
    "domain_approved": False,
    "domain_activated": False,
    "live_registry_mutated": False,
    "repair_started": False,
    "retry_started": False,
    "replay_mutated": False,
}


def review_clarified_domain_intent(
    *,
    review_id: str,
    clarification_continuity_replay_reference: str,
    review_decision: str,
    reviewed_by: str,
    created_at: str,
    replay_dir: str | Path,
    clarification_questions: list[str] | None = None,
) -> dict[str, Any]:
    """Review clarified domain intent and emit a non-authoritative next-path decision."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        resume = _load_resume_artifact(Path(_require_string(
            clarification_continuity_replay_reference,
            "clarification_continuity_replay_reference",
        )))
        decision_status = _normalize_decision(review_decision)
        questions = _validate_decision_requirements(
            decision_status=decision_status,
            clarification_questions=clarification_questions or [],
            resume=resume,
        )
        decision = _decision_artifact(
            review_id=review_id,
            resume=resume,
            clarification_continuity_replay_reference=clarification_continuity_replay_reference,
            review_decision=decision_status,
            reviewed_by=reviewed_by,
            created_at=created_at,
            clarification_questions=questions,
            failure_reason=None,
        )
        returned = _returned_artifact(decision, created_at=created_at)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], decision)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(decision, returned, replay_path)
    except Exception as exc:
        decision = _failed_decision_artifact(
            review_id=review_id,
            clarification_continuity_replay_reference=clarification_continuity_replay_reference,
            review_decision=review_decision,
            reviewed_by=reviewed_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(decision, created_at=created_at)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], decision)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(decision, returned, replay_path)


def reconstruct_clarified_domain_intent_handoff_review_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct clarified domain handoff review replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("clarified domain handoff review replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("clarified domain handoff review replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "clarified domain handoff review artifact")
        wrappers.append(wrapper)
    decision = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("review_decision_reference") != decision["review_id"]:
        raise FailClosedRuntimeError("clarified domain handoff review returned reference mismatch")
    if returned.get("review_decision_hash") != decision["artifact_hash"]:
        raise FailClosedRuntimeError("clarified domain handoff review returned hash mismatch")
    if decision["review_decision"] != FAIL_CLOSED:
        resume = _load_resume_artifact(
            _resolve_replay_reference(
                decision["clarification_continuity_replay_reference"],
                anchor=replay_path,
            )
        )
        if resume["artifact_hash"] != decision["clarification_workflow_resume_hash"]:
            raise FailClosedRuntimeError("clarified domain handoff review resume hash mismatch")
    _validate_authority_flags(decision)
    _validate_authority_flags(returned)
    return {
        "review_id": decision["review_id"],
        "review_decision": decision["review_decision"],
        "proposed_domain": decision["proposed_domain"],
        "originating_intent": decision["originating_intent"],
        "canonical_chain_id": decision["canonical_chain_id"],
        "next_certified_stage": decision["next_certified_stage"],
        "target_worker_id": decision["worker_binding"].get("target_worker_id"),
        "target_authorized_scope": decision["worker_binding"].get("authorized_scope"),
        "clarification_questions": deepcopy(decision["clarification_questions"]),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": decision["failure_reason"],
        "replay_hash": replay_hash(wrappers),
    }


def render_clarified_domain_intent_handoff_review_summary(capture: dict[str, Any]) -> str:
    """Render a compact operator-facing review summary."""

    if capture.get("fail_closed") is True:
        return f"FAILED_CLOSED: {capture.get('failure_reason')}"
    return "\n".join(
        [
            "Handoff Review",
            "",
            f"Review Decision: {capture.get('review_decision')}",
            f"Proposed Domain: {capture.get('proposed_domain')}",
            f"Next Certified Stage: {capture.get('next_certified_stage')}",
            "",
            "No approval, authorization, worker request, dispatch, invocation, execution, repair, or retry was created.",
        ]
    )


def _resolve_replay_reference(reference: Any, *, anchor: Path) -> Path:
    replay_path = Path(_require_string(reference, "replay_reference"))
    if replay_path.is_absolute() or replay_path.exists():
        return replay_path
    for parent in (anchor, *anchor.parents):
        candidate = parent / replay_path
        if candidate.exists():
            return candidate
    return replay_path


def _load_resume_artifact(replay_path: Path) -> dict[str, Any]:
    reconstructed = reconstruct_clarification_continuity_replay(replay_path)
    if reconstructed.get("workflow_resumed") is not True:
        raise FailClosedRuntimeError("clarified domain handoff review failed closed: workflow not resumed")
    wrapper = load_json(replay_path / "003_clarification_workflow_resume_recorded.json")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("clarified domain handoff review failed closed: resume artifact missing")
    _verify_artifact_hash(artifact, "clarification workflow resume artifact")
    if artifact.get("artifact_type") != CLARIFICATION_WORKFLOW_RESUME_ARTIFACT_V1:
        raise FailClosedRuntimeError("clarified domain handoff review failed closed: invalid resume artifact")
    if artifact.get("workflow_resume_status") != WORKFLOW_RESUME_READY:
        raise FailClosedRuntimeError("clarified domain handoff review failed closed: workflow not resumed")
    if artifact.get("originating_intent") != CREATE_DOMAIN:
        raise FailClosedRuntimeError("clarified domain handoff review failed closed: unsupported intent")
    if artifact.get("next_required_boundary") != "OCS_OR_EXECUTION_HANDOFF_REVIEW":
        raise FailClosedRuntimeError("clarified domain handoff review failed closed: boundary mismatch")
    _require_string(artifact.get("proposed_domain"), "proposed_domain")
    return artifact


def _decision_artifact(
    *,
    review_id: str,
    resume: dict[str, Any],
    clarification_continuity_replay_reference: str,
    review_decision: str,
    reviewed_by: str,
    created_at: str,
    clarification_questions: list[str],
    failure_reason: str | None,
) -> dict[str, Any]:
    next_stage = _next_certified_stage(review_decision)
    artifact = {
        "artifact_type": HANDOFF_REVIEW_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW_RUNTIME_VERSION,
        "review_id": _require_string(review_id, "review_id"),
        "review_decision": review_decision,
        "reviewed_by": _require_string(reviewed_by, "reviewed_by"),
        "created_at": _require_string(created_at, "created_at"),
        "clarification_continuity_replay_reference": _require_string(
            clarification_continuity_replay_reference,
            "clarification_continuity_replay_reference",
        ),
        "clarification_workflow_resume_reference": resume["clarification_workflow_resume_id"],
        "clarification_workflow_resume_hash": resume["artifact_hash"],
        "originating_workflow_id": resume["originating_workflow_id"],
        "originating_intent": resume["originating_intent"],
        "proposed_domain": resume["proposed_domain"],
        "canonical_chain_id": resume["canonical_chain_id"],
        "review_scope": "CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW",
        "next_certified_stage": next_stage,
        "ocs_handoff_decision": _ocs_handoff_decision(review_decision, resume),
        "worker_binding": _worker_binding_decision(review_decision, resume),
        "clarification_questions": clarification_questions,
        "allowed_review_outputs": [
            OCS_HANDOFF_APPROVED,
            WORKER_BINDING_APPROVED,
            CLARIFICATION_REQUIRED,
            FAIL_CLOSED,
        ],
        "approval_required_before_execution": True,
        "human_approval_created": False,
        "execution_authorization_created": False,
        "worker_selection_required_before_request": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["decision_hash"] = _decision_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_decision_artifact(
    *,
    review_id: Any,
    clarification_continuity_replay_reference: Any,
    review_decision: Any,
    reviewed_by: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HANDOFF_REVIEW_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW_RUNTIME_VERSION,
        "review_id": review_id if isinstance(review_id, str) and review_id.strip() else "INVALID_REVIEW_ID",
        "review_decision": FAIL_CLOSED,
        "requested_review_decision": review_decision if isinstance(review_decision, str) else "INVALID_REVIEW_DECISION",
        "reviewed_by": reviewed_by if isinstance(reviewed_by, str) and reviewed_by.strip() else "INVALID_REVIEWER",
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00Z",
        "clarification_continuity_replay_reference": (
            clarification_continuity_replay_reference
            if isinstance(clarification_continuity_replay_reference, str)
            else "INVALID_REPLAY_REFERENCE"
        ),
        "clarification_workflow_resume_reference": None,
        "clarification_workflow_resume_hash": None,
        "originating_workflow_id": None,
        "originating_intent": None,
        "proposed_domain": None,
        "canonical_chain_id": None,
        "review_scope": "CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW",
        "next_certified_stage": FAIL_CLOSED,
        "ocs_handoff_decision": {},
        "worker_binding": {},
        "clarification_questions": [],
        "allowed_review_outputs": [
            OCS_HANDOFF_APPROVED,
            WORKER_BINDING_APPROVED,
            CLARIFICATION_REQUIRED,
            FAIL_CLOSED,
        ],
        "approval_required_before_execution": True,
        "human_approval_created": False,
        "execution_authorization_created": False,
        "worker_selection_required_before_request": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["decision_hash"] = _decision_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(decision: dict[str, Any], *, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": HANDOFF_REVIEW_RETURNED_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW_RUNTIME_VERSION,
        "review_decision_reference": decision["review_id"],
        "review_decision": decision["review_decision"],
        "review_decision_hash": decision["artifact_hash"],
        "proposed_domain": decision["proposed_domain"],
        "next_certified_stage": decision["next_certified_stage"],
        "created_at": _require_string(created_at, "created_at"),
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": decision["failure_reason"],
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(decision: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "milestone_id": AIGOL_CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW_RUNTIME_VERSION,
        "final_classification": "CLARIFIED_DOMAIN_INTENT_HANDOFF_REVIEW_STATUS",
        "review_decision": decision["review_decision"],
        "review_reference": decision["review_id"],
        "review_hash": decision["artifact_hash"],
        "proposed_domain": decision["proposed_domain"],
        "originating_intent": decision["originating_intent"],
        "canonical_chain_id": decision["canonical_chain_id"],
        "next_certified_stage": decision["next_certified_stage"],
        "handoff_review_decision_artifact": deepcopy(decision),
        "handoff_review_returned_artifact": deepcopy(returned),
        "handoff_review_replay_reference": str(replay_path),
        "fail_closed": decision["review_decision"] == FAIL_CLOSED,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": decision["failure_reason"],
    }
    capture["handoff_review_capture_hash"] = replay_hash(capture)
    return capture


def _validate_decision_requirements(
    *,
    decision_status: str,
    clarification_questions: list[str],
    resume: dict[str, Any],
) -> list[str]:
    _require_string(resume.get("proposed_domain"), "proposed_domain")
    if decision_status == CLARIFICATION_REQUIRED:
        return _string_list_required(clarification_questions, "clarification_questions")
    if clarification_questions:
        raise FailClosedRuntimeError("clarified domain handoff review failed closed: unexpected clarification questions")
    return []


def _normalize_decision(value: Any) -> str:
    decision = _require_string(value, "review_decision").strip().upper()
    if decision not in ALLOWED_REVIEW_DECISIONS:
        raise FailClosedRuntimeError("clarified domain handoff review failed closed: invalid review decision")
    return decision


def _next_certified_stage(review_decision: str) -> str:
    if review_decision == OCS_HANDOFF_APPROVED:
        return "AIGOL_OCS_TO_EXECUTION_HANDOFF_RUNTIME_V1"
    if review_decision == WORKER_BINDING_APPROVED:
        return "AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW"
    if review_decision == CLARIFICATION_REQUIRED:
        return "UNKNOWN_DOMAIN_CLARIFICATION_WORKFLOW"
    return FAIL_CLOSED


def _ocs_handoff_decision(review_decision: str, resume: dict[str, Any]) -> dict[str, Any]:
    if review_decision != OCS_HANDOFF_APPROVED:
        return {}
    return {
        "handoff_preparation_allowed": True,
        "required_runtime": "AIGOL_OCS_TO_EXECUTION_HANDOFF_RUNTIME_V1",
        "execution_intent_summary": f"Prepare governed domain artifact execution intake for {resume['proposed_domain']}.",
        "human_review_required": True,
        "approval_created": False,
        "authorization_created": False,
    }


def _worker_binding_decision(review_decision: str, resume: dict[str, Any]) -> dict[str, Any]:
    if review_decision != WORKER_BINDING_APPROVED:
        return {}
    return {
        "worker_binding_review_allowed": True,
        "target_worker_id": DOMAIN_ARTIFACT_WORKER_ID,
        "target_worker_family": "GOVERNED_DOMAIN_ARTIFACT_AUTHORING",
        "authorized_scope": DOMAIN_ARTIFACT_AUTHORIZED_SCOPE,
        "operation": OPERATION_AUTHOR_DOMAIN_ARTIFACTS,
        "domain_name": resume["proposed_domain"],
        "allowed_outputs": [
            DOMAIN_DEFINITION_ARTIFACT_V1,
            DOMAIN_METADATA_ARTIFACT_V1,
            DOMAIN_REGISTRATION_ARTIFACT_V1,
            DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1,
        ],
        "forbidden_operations": [
            "DOMAIN_APPROVAL",
            "DOMAIN_ACTIVATION",
            "LIVE_DOMAIN_REGISTRY_MUTATION",
            "PROVIDER_INVOCATION",
            "WORKER_SELF_AUTHORIZATION",
            "REPLAY_MUTATION",
        ],
        "approval_created": False,
        "authorization_created": False,
        "worker_request_created": False,
    }


def _decision_hash(artifact: dict[str, Any]) -> str:
    payload = deepcopy(artifact)
    payload.pop("decision_hash", None)
    payload.pop("artifact_hash", None)
    return replay_hash(payload)


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("clarified domain handoff review replay step ordering mismatch")
    _verify_artifact_hash(artifact, "clarified domain handoff review artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{step}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, step, artifact)
        except FailClosedRuntimeError:
            return


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only handoff review artifact already exists: {path.name}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")
    if "decision_hash" in artifact and artifact["decision_hash"] != _decision_hash(artifact):
        raise FailClosedRuntimeError(f"{label} decision hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("clarified domain handoff review replay hash mismatch")


def _validate_authority_flags(artifact: dict[str, Any]) -> None:
    for key, expected in AUTHORITY_FLAGS.items():
        if artifact.get(key) is not expected:
            raise FailClosedRuntimeError("clarified domain handoff review authority violation")
    if artifact.get("human_approval_created", False) is not False:
        raise FailClosedRuntimeError("clarified domain handoff review authority violation")
    if artifact.get("execution_authorization_created", False) is not False:
        raise FailClosedRuntimeError("clarified domain handoff review authority violation")


def _string_list_required(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"clarified domain handoff review failed closed: {field_name} is required")
    items: list[str] = []
    for item in value:
        items.append(_require_string(item, field_name))
    return items


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"clarified domain handoff review failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "clarified domain handoff review failed closed"
