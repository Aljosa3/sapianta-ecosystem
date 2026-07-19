"""Replay-visible human decision runtime for approval-required operations."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.conversation_to_ppp_handoff_execution import HUMAN_APPROVAL_REQUIRED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_HUMAN_DECISION_RUNTIME_VERSION = "AIGOL_HUMAN_DECISION_RUNTIME_V1"
HUMAN_DECISION_ARTIFACT_V1 = "HUMAN_DECISION_ARTIFACT_V1"
HUMAN_DECISION_RETURNED_V1 = "HUMAN_DECISION_RETURNED_V1"
HUMAN_DECISION_RECORDED = "HUMAN_DECISION_RECORDED"
APPROVE = "APPROVE"
REJECT = "REJECT"
REQUEST_MODIFICATION = "REQUEST_MODIFICATION"
GOVERNED_REJECTION_RECORDED = "GOVERNED_REJECTION_RECORDED"
MODIFICATION_REQUEST_RECORDED = "MODIFICATION_REQUEST_RECORDED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

VALID_DECISIONS = frozenset({APPROVE, REJECT, REQUEST_MODIFICATION})
REPLAY_STEPS = ("human_decision_recorded", "human_decision_returned")

AIGOL_HUMAN_DECISION_RUNTIME_VERSION_V2, HUMAN_DECISION_ARTIFACT_V2, HUMAN_DECISION_RETURNED_V2 = "AIGOL_HUMAN_DECISION_RUNTIME_V2", "HUMAN_DECISION_ARTIFACT_V2", "HUMAN_DECISION_RETURNED_V2"
CONTENT_ACCEPTANCE, CONTENT_ACCEPTANCE_ONLY = "CONTENT_ACCEPTANCE", "CONTENT_ACCEPTANCE_ONLY"
ACCEPTED, REJECTED = "ACCEPTED", "REJECTED"
CONTENT_DECISION_REPLAY_STEPS = ("content_acceptance_context_presented", "content_acceptance_request_recorded", "content_acceptance_decision_recorded", "content_acceptance_decision_returned")


def record_human_decision(
    *,
    human_decision_id: str,
    approval_required_artifact: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record a human decision for a HUMAN_APPROVAL_REQUIRED operation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        approval_required = _validate_approval_required(approval_required_artifact)
        artifact = _decision_artifact(
            human_decision_id=human_decision_id,
            approval_required=approval_required,
            decision=decision,
            decision_reason=decision_reason,
            decided_by=decided_by,
            decided_at=decided_at,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_decision_artifact(
            human_decision_id=human_decision_id,
            approval_required_artifact=approval_required_artifact,
            decision=decision,
            decision_reason=decision_reason,
            decided_by=decided_by,
            decided_at=decided_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_human_decision_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct human decision replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("human decision replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("human decision replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "human decision artifact")
        wrappers.append(wrapper)
    decision = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("human_decision_reference") != decision["human_decision_id"]:
        raise FailClosedRuntimeError("human decision replay reference mismatch")
    if returned.get("human_decision_hash") != decision["artifact_hash"]:
        raise FailClosedRuntimeError("human decision replay hash mismatch")
    if returned.get("chain_id") != decision["chain_id"]:
        raise FailClosedRuntimeError("human decision replay chain mismatch")
    return {
        "human_decision_id": decision["human_decision_id"],
        "decision_status": decision["decision_status"],
        "decision": decision["decision"],
        "chain_id": decision["chain_id"],
        "approval_scope": decision["approval_scope"],
        "terminal_status": decision["terminal_status"],
        "clarification_required": decision["clarification_required"],
        "implementation_authorized": decision["implementation_authorized"],
        "implementation_authorization_allowed": decision.get(
            "implementation_authorization_allowed", True
        ),
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "failure_reason": decision["failure_reason"],
    }


def render_human_decision_summary(capture: dict[str, Any]) -> str:
    lines = [
        "Human Decision",
        "",
        f"Decision Status: {capture.get('decision_status')}",
        f"Decision: {capture.get('decision')}",
        f"Terminal Status: {capture.get('terminal_status')}",
        f"Approval Scope: {capture.get('approval_scope')}",
        f"Human Decision Reference: {capture.get('human_decision_id')}",
        f"Replay Reference: {capture.get('human_decision_replay_reference')}",
    ]
    if capture.get("clarification_required"):
        lines.append("Clarification State: REQUIRED")
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def normalize_human_decision(value: str) -> str:
    token = value.strip().upper().replace(" ", "_").replace("-", "_").rstrip(".")
    aliases = {
        "APPROVED": APPROVE,
        "APPROVE": APPROVE,
        "YES": APPROVE,
        "REJECTED": REJECT,
        "REJECT": REJECT,
        "NO": REJECT,
        "REQUEST_CHANGES": REQUEST_MODIFICATION,
        "REQUEST_CHANGE": REQUEST_MODIFICATION,
        "REQUEST_MODIFICATION": REQUEST_MODIFICATION,
        "MODIFY": REQUEST_MODIFICATION,
        "MODIFICATION": REQUEST_MODIFICATION,
    }
    return aliases.get(token, token)


def prepare_content_acceptance_decision_context(
    *, context_id: str, binding_capture: dict[str, Any], human_actor_id: str,
    presented_at: str, session_root: str | Path, replay_dir: str | Path,
) -> dict[str, Any]:
    """Project one exact G31-23B result for a later explicit V2 decision."""
    root, path = Path(session_root).resolve(), Path(replay_dir).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("content-acceptance decision context is cross-session")
    _ensure_content_replay_available(path)
    subject = _content_acceptance_subject(binding_capture, root)
    context = {
        "artifact_type": "HUMAN_DECISION_CONTEXT_PRESENTED_V2", "runtime_version": AIGOL_HUMAN_DECISION_RUNTIME_VERSION_V2,
        "context_id": _require_string(context_id, "context_id"), "human_actor_id": _require_string(human_actor_id, "human_actor_id"),
        "decision_type": CONTENT_ACCEPTANCE, "decision_scope": CONTENT_ACCEPTANCE_ONLY,
        "valid_decision_outcomes": [ACCEPTED, REJECTED], "subject_binding": subject,
        "subject_binding_hash": subject["subject_binding_hash"], "presented_at": _require_string(presented_at, "presented_at"), **_content_authority_boundaries(),
    }
    context["artifact_hash"] = replay_hash(context)
    request = {
        "artifact_type": "HUMAN_DECISION_REQUESTED_V2", "runtime_version": AIGOL_HUMAN_DECISION_RUNTIME_VERSION_V2,
        "context_reference": context["context_id"], "context_hash": context["artifact_hash"],
        "decision_type": CONTENT_ACCEPTANCE, "decision_scope": CONTENT_ACCEPTANCE_ONLY,
        "valid_decision_outcomes": [ACCEPTED, REJECTED], "human_actor_id": context["human_actor_id"],
        "requested_at": context["presented_at"], **_content_authority_boundaries(),
    }
    request["artifact_hash"] = replay_hash(request)
    return {"context_artifact": context, "request_artifact": request, "human_decision_replay_reference": str(path), "decision_pending": True}


def record_content_acceptance_decision(
    *, context_capture: dict[str, Any], binding_capture: dict[str, Any],
    decision_outcome: str, decided_by: str, decided_at: str,
    session_root: str | Path,
) -> dict[str, Any]:
    """Persist one exact ACCEPTED or REJECTED V2 decision without acceptance."""
    root, path = Path(session_root).resolve(), Path(context_capture.get("human_decision_replay_reference", "")).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("content-acceptance decision Replay is cross-session")
    _ensure_content_replay_available(path)
    context, request = context_capture.get("context_artifact"), context_capture.get("request_artifact")
    _verify_artifact_hash(context, "content-acceptance context"); _verify_artifact_hash(request, "content-acceptance request")
    subject = _content_acceptance_subject(binding_capture, root)
    if context.get("subject_binding") != subject or request.get("context_hash") != context["artifact_hash"]:
        raise FailClosedRuntimeError("content-acceptance decision subject or request mismatch")
    actor = _require_string(decided_by, "decided_by")
    if actor != context.get("human_actor_id") or decision_outcome not in {ACCEPTED, REJECTED}:
        raise FailClosedRuntimeError("content-acceptance decision actor or outcome invalid")
    _reject_content_decision_reuse(root, subject["subject_binding_hash"])
    decision = {
        "artifact_type": HUMAN_DECISION_ARTIFACT_V2, "runtime_version": AIGOL_HUMAN_DECISION_RUNTIME_VERSION_V2,
        "human_decision_id": f"{context['context_id']}:DECISION", "decision_status": "CONTENT_ACCEPTANCE_DECISION_RECORDED",
        "decision_type": CONTENT_ACCEPTANCE, "decision_scope": CONTENT_ACCEPTANCE_ONLY,
        "decision_outcome": decision_outcome, "context_reference": context["context_id"],
        "context_hash": context["artifact_hash"], "request_hash": request["artifact_hash"], "subject_binding_hash": subject["subject_binding_hash"],
        "decided_by": actor, "decided_at": _require_string(decided_at, "decided_at"),
        **_content_authority_boundaries(),
    }
    decision["artifact_hash"] = replay_hash(decision)
    returned = {
        "artifact_type": HUMAN_DECISION_RETURNED_V2, "runtime_version": AIGOL_HUMAN_DECISION_RUNTIME_VERSION_V2,
        "human_decision_reference": decision["human_decision_id"], "human_decision_hash": decision["artifact_hash"],
        "decision_type": CONTENT_ACCEPTANCE, "decision_scope": CONTENT_ACCEPTANCE_ONLY,
        "decision_outcome": decision_outcome, "subject_binding_hash": subject["subject_binding_hash"], **_content_authority_boundaries(),
    }
    returned["artifact_hash"] = replay_hash(returned)
    for index, artifact in enumerate((context, request, decision, returned)):
        _persist_content_step(path, index, artifact)
    capture = deepcopy(decision)
    capture.update({"human_decision_artifact": deepcopy(decision), "human_decision_replay": deepcopy(returned),
                    "content_acceptance_context_artifact": deepcopy(context), "content_acceptance_request_artifact": deepcopy(request),
                    "human_decision_replay_reference": str(path)})
    capture["human_decision_capture_hash"] = replay_hash(capture)
    return capture


def reconstruct_content_acceptance_decision_replay(
    *, decision_capture: dict[str, Any], binding_capture: dict[str, Any],
    session_root: str | Path,
) -> dict[str, Any]:
    """Reconstruct and rebind one four-step V2 content decision Replay."""
    root, path = Path(session_root).resolve(), Path(decision_capture.get("human_decision_replay_reference", "")).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("content-acceptance decision Replay is cross-session")
    artifacts, wrappers = [], []
    for index, step in enumerate(CONTENT_DECISION_REPLAY_STEPS):
        wrapper = load_json(path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("content-acceptance decision Replay ordering mismatch")
        _verify_wrapper_hash(wrapper); _verify_artifact_hash(wrapper.get("artifact"), "content-acceptance Replay artifact")
        wrappers.append(wrapper); artifacts.append(wrapper["artifact"])
    context, request, decision, returned = artifacts
    subject = _content_acceptance_subject(binding_capture, root)
    checks = (context.get("subject_binding") == subject, request.get("context_hash") == context.get("artifact_hash"),
        decision_capture.get("human_decision_artifact") == decision, decision.get("context_hash") == context.get("artifact_hash"),
        decision.get("request_hash") == request.get("artifact_hash"), returned.get("human_decision_hash") == decision.get("artifact_hash"),
        returned.get("decision_outcome") == decision.get("decision_outcome"), returned.get("subject_binding_hash") == subject.get("subject_binding_hash"))
    if not all(checks):
        raise FailClosedRuntimeError("content-acceptance decision Replay identity mismatch")
    return {"human_decision_id": decision["human_decision_id"], "decision_type": decision["decision_type"],
            "decision_scope": decision["decision_scope"], "decision_outcome": decision["decision_outcome"],
            "result_accepted": False, "mutation_authorized": False, "main_repository_mutated": False,
            "replay_artifact_count": 4, "replay_hash": replay_hash(wrappers)}


def render_content_acceptance_decision_context(context_capture: dict[str, Any]) -> str:
    context = context_capture.get("context_artifact") or {}; _verify_artifact_hash(context, "content-acceptance context")
    subject, files = context["subject_binding"], context["subject_binding"]["replacement_files"]
    return "\n".join(("Human Content-Acceptance Decision Required",
        f"Decision Type: {CONTENT_ACCEPTANCE}", f"Decision Scope: {CONTENT_ACCEPTANCE_ONLY}",
        f"Validated Result: {subject['binding_reference']}",
        f"Manifest: {subject['manifest_reference']}",
        *(f"Replacement: {item['target_path']} {item['preimage_sha256']} -> {item['postimage_sha256']}" for item in files),
        "Use /accept to record ACCEPTED or /reject to record REJECTED.",
        "No content is accepted and no mutation is authorized by this decision."))


def render_content_acceptance_decision(capture: dict[str, Any]) -> str:
    artifact = capture.get("human_decision_artifact") or {}; _verify_artifact_hash(artifact, "content-acceptance decision")
    return "\n".join(("Human Content-Acceptance Decision",
        f"Decision Type: {artifact['decision_type']}", f"Decision Scope: {artifact['decision_scope']}",
        f"Decision Outcome: {artifact['decision_outcome']}",
        f"Subject Binding Hash: {artifact['subject_binding_hash']}",
        f"Replay Reference: {capture['human_decision_replay_reference']}",
        "Result Accepted: False", "Mutation Authorized: False", "Main Repository Mutated: False"))


def _validate_approval_required(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("human decision failed closed: approval-required artifact missing")
    _verify_artifact_hash(artifact, "approval-required artifact")
    if artifact.get("terminal_status") != HUMAN_APPROVAL_REQUIRED:
        raise FailClosedRuntimeError("human decision failed closed: approval is not pending")
    packet = artifact.get("approval_resume_packet")
    if not isinstance(packet, dict):
        raise FailClosedRuntimeError("human decision failed closed: approval packet missing")
    expected = deepcopy(packet)
    actual = expected.pop("packet_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("human decision failed closed: approval packet hash mismatch")
    request = packet.get("approval_request_artifact")
    if not isinstance(request, dict):
        raise FailClosedRuntimeError("human decision failed closed: approval request missing")
    _verify_artifact_hash(request, "approval request")
    if request.get("approval_status") != HUMAN_APPROVAL_REQUIRED:
        raise FailClosedRuntimeError("human decision failed closed: approval request is not pending")
    if (
        "implementation_authorization_allowed" in request
        and not isinstance(request["implementation_authorization_allowed"], bool)
    ):
        raise FailClosedRuntimeError(
            "human decision failed closed: implementation authority boundary is malformed"
        )
    if request.get("artifact_hash") != artifact.get("approval_hash"):
        raise FailClosedRuntimeError("human decision failed closed: approval lineage mismatch")
    return deepcopy(artifact)


def _decision_artifact(
    *,
    human_decision_id: str,
    approval_required: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
) -> dict[str, Any]:
    normalized_decision = normalize_human_decision(_require_string(decision, "decision"))
    if normalized_decision not in VALID_DECISIONS:
        raise FailClosedRuntimeError("human decision failed closed: invalid decision")
    return _base_decision_artifact(
        human_decision_id=human_decision_id,
        approval_required=approval_required,
        decision=normalized_decision,
        decision_reason=decision_reason,
        decided_by=decided_by,
        decided_at=decided_at,
        failure_reason=None,
    )


def _failed_decision_artifact(
    *,
    human_decision_id: str,
    approval_required_artifact: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_DECISION_RUNTIME_VERSION,
        "human_decision_id": human_decision_id,
        "decision_status": FAILED_CLOSED,
        "decision": normalize_human_decision(decision) if isinstance(decision, str) else None,
        "decision_reason": decision_reason if isinstance(decision_reason, str) else "",
        "decision_reason_hash": replay_hash(decision_reason) if isinstance(decision_reason, str) else None,
        "chain_id": approval_required_artifact.get("canonical_chain_id") if isinstance(approval_required_artifact, dict) else None,
        "approval_required_reference": approval_required_artifact.get("execution_id") if isinstance(approval_required_artifact, dict) else None,
        "approval_required_hash": approval_required_artifact.get("artifact_hash") if isinstance(approval_required_artifact, dict) else None,
        "approval_request_reference": None,
        "approval_request_hash": None,
        "approval_scope": approval_required_artifact.get("approval_scope") if isinstance(approval_required_artifact, dict) else None,
        "proposal_reference": None,
        "proposal_hash": None,
        "terminal_status": FAILED_CLOSED,
        "clarification_required": False,
        "implementation_authorized": False,
        "implementation_rejected": False,
        "modification_requested": False,
        "decided_by": decided_by if isinstance(decided_by, str) else "",
        "decided_at": decided_at if isinstance(decided_at, str) else "",
        **_authority_boundaries(),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _base_decision_artifact(
    *,
    human_decision_id: str,
    approval_required: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    packet = approval_required["approval_resume_packet"]
    request = packet["approval_request_artifact"]
    implementation_authorization_allowed = request.get(
        "implementation_authorization_allowed", True
    )
    status_by_decision = {
        APPROVE: HUMAN_DECISION_RECORDED,
        REJECT: GOVERNED_REJECTION_RECORDED,
        REQUEST_MODIFICATION: MODIFICATION_REQUEST_RECORDED,
    }
    terminal_by_decision = {
        APPROVE: "APPROVAL_DECISION_RECORDED",
        REJECT: "GOVERNED_REJECTION_TERMINATED",
        REQUEST_MODIFICATION: CLARIFICATION_REQUIRED,
    }
    artifact = {
        "artifact_type": HUMAN_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_DECISION_RUNTIME_VERSION,
        "human_decision_id": _require_string(human_decision_id, "human_decision_id"),
        "decision_status": status_by_decision[decision],
        "decision": decision,
        "decision_reason": _require_string(decision_reason, "decision_reason"),
        "decision_reason_hash": replay_hash(decision_reason),
        "chain_id": approval_required["canonical_chain_id"],
        "approval_required_reference": approval_required["execution_id"],
        "approval_required_hash": approval_required["artifact_hash"],
        "approval_request_reference": request["approval_id"],
        "approval_request_hash": request["artifact_hash"],
        "approval_scope": request["approval_scope"],
        "proposal_reference": request["proposal_reference"],
        "proposal_hash": request["proposal_hash"],
        "terminal_status": terminal_by_decision[decision],
        "clarification_required": decision == REQUEST_MODIFICATION,
        "implementation_authorized": (
            decision == APPROVE and implementation_authorization_allowed
        ),
        "implementation_rejected": (
            decision == REJECT and implementation_authorization_allowed
        ),
        "modification_requested": decision == REQUEST_MODIFICATION,
        "decided_by": _require_string(decided_by, "decided_by"),
        "decided_at": _require_string(decided_at, "decided_at"),
        **_authority_boundaries(),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    if "implementation_authorization_allowed" in request:
        artifact["implementation_authorization_allowed"] = (
            implementation_authorization_allowed
        )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(decision: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(decision, "human decision artifact")
    artifact = {
        "artifact_type": HUMAN_DECISION_RETURNED_V1,
        "event_type": "HUMAN_DECISION_RETURNED",
        "human_decision_reference": decision["human_decision_id"],
        "human_decision_hash": decision["artifact_hash"],
        "decision_status": decision["decision_status"],
        "decision": decision["decision"],
        "chain_id": decision["chain_id"],
        "approval_scope": decision["approval_scope"],
        "terminal_status": decision["terminal_status"],
        "clarification_required": decision["clarification_required"],
        "implementation_authorized": decision["implementation_authorized"],
        "implementation_rejected": decision["implementation_rejected"],
        "modification_requested": decision["modification_requested"],
        **_authority_boundaries(),
        "replay_visible": True,
        "failure_reason": decision["failure_reason"],
    }
    if "implementation_authorization_allowed" in decision:
        artifact["implementation_authorization_allowed"] = decision[
            "implementation_authorization_allowed"
        ]
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(decision: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = deepcopy(decision)
    capture.update(
        {
            "human_decision_artifact": deepcopy(decision),
            "human_decision_replay": deepcopy(returned),
            "human_decision_replay_reference": str(replay_path),
            "fail_closed": decision["decision_status"] == FAILED_CLOSED,
        }
    )
    capture["human_decision_capture_hash"] = replay_hash(capture)
    return capture


def _authority_boundaries() -> dict[str, bool]:
    return {
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "approval_modified": False,
        "automatic_approval": False,
        "provider_authority": False,
        "worker_authority": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("human decision replay ordering mismatch")
    _verify_artifact_hash(artifact, "human decision artifact")
    wrapper = {"replay_index": index, "replay_step": step, "event_type": step.upper(), "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("human decision replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("human decision replay hash mismatch")


def _content_acceptance_subject(binding_capture: dict[str, Any], root: Path) -> dict[str, Any]:
    from aigol.runtime.codex_replacement_acceptance_prerequisite_binding_runtime import reconstruct_codex_replacement_acceptance_prerequisite_binding
    from aigol.runtime.generated_content_acceptance_runtime import verify_generated_content_acceptance_prerequisite_artifact
    from aigol.runtime.implementation_manifest_runtime import IMPLEMENTATION_MANIFEST_ARTIFACT_V2, REPLACE_CONTENT
    reconstructed = reconstruct_codex_replacement_acceptance_prerequisite_binding(binding_capture=binding_capture, session_root=root)
    binding = binding_capture["binding_artifact"]
    manifest = binding_capture["implementation_manifest_capture"]["implementation_manifest_artifact"]
    content = binding_capture["generated_content_validation_capture"]["generated_content_validation_artifact"]
    tests = binding_capture["generated_test_validation_capture"]["generated_test_validation_artifact"]
    prerequisite = binding_capture["acceptance_prerequisite_capture"]["acceptance_prerequisite_artifact"]
    verify_generated_content_acceptance_prerequisite_artifact(prerequisite)
    if not all((binding_capture.get("acceptance_prerequisites_satisfied") is True, binding_capture.get("ready_for_acceptance") is True,
                binding_capture.get("result_accepted") is False, binding_capture.get("mutation_authorized") is False,
                binding_capture.get("main_repository_mutated") is False, manifest.get("artifact_type") == IMPLEMENTATION_MANIFEST_ARTIFACT_V2,
                manifest.get("operation_mode") == REPLACE_CONTENT, manifest.get("canonical_session_id") == root.name)):
        raise FailClosedRuntimeError("content-acceptance decision requires exact unaccepted G31-23B readiness")
    files = [{key: entry[key] for key in (
        "target_path", "artifact_type", "operation", "preimage_sha256", "postimage_sha256", "file_type",
        "postimage_file_type", "file_mode", "postimage_file_mode", "file_entry_hash",
    )} for entry in manifest["file_entries"]]
    subject = {
        "canonical_session_id": manifest["canonical_session_id"], "canonical_chain_id": manifest["canonical_chain_id"],
        "source_workspace": manifest["source_workspace"], "operation_mode": REPLACE_CONTENT,
        "binding_reference": binding["binding_id"], "binding_hash": binding["artifact_hash"],
        "binding_replay_reference": binding_capture["binding_replay_reference"], "binding_replay_hash": reconstructed["replay_hash"],
        "prerequisite_reference": prerequisite["prerequisite_id"], "prerequisite_hash": prerequisite["prerequisite_hash"],
        "manifest_reference": manifest["manifest_id"], "manifest_artifact_hash": manifest["artifact_hash"],
        "manifest_hash": manifest["implementation_manifest_hash"], "manifest_replay_hash": binding["implementation_manifest_replay_hash"],
        "content_validation_reference": content["validation_id"], "content_validation_hash": content["generated_content_validation_hash"],
        "test_validation_reference": tests["validation_id"], "test_validation_hash": tests["generated_test_validation_hash"],
        "disposable_validation_reference": binding["source_disposable_validation_reference"],
        "disposable_validation_hash": binding["source_disposable_validation_hash"],
        "replacement_files": files,
    }
    subject["subject_binding_hash"] = replay_hash(subject)
    return subject


def _content_authority_boundaries() -> dict[str, bool]:
    return {"result_accepted": False, "mutation_authorized": False, "main_repository_mutated": False,
            "execution_authorized": False, "provider_invoked": False, "worker_invoked": False,
            "command_executed": False, "patch_applied": False, "automatic_approval": False, "replay_visible": True}


def _ensure_content_replay_available(path: Path) -> None:
    if any((path / f"{index:03d}_{step}.json").exists() for index, step in enumerate(CONTENT_DECISION_REPLAY_STEPS)):
        raise FailClosedRuntimeError("content-acceptance decision destination already exists")


def _persist_content_step(path: Path, index: int, artifact: dict[str, Any]) -> None:
    step = CONTENT_DECISION_REPLAY_STEPS[index]; _verify_artifact_hash(artifact, "content-acceptance decision artifact")
    wrapper = {"replay_index": index, "replay_step": step, "event_type": step.upper(), "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"{index:03d}_{step}.json", wrapper)


def _reject_content_decision_reuse(root: Path, subject_hash: str) -> None:
    for path in root.rglob("002_content_acceptance_decision_recorded.json"):
        wrapper = load_json(path); _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact") or {}; _verify_artifact_hash(artifact, "content-acceptance decision")
        if artifact.get("subject_binding_hash") == subject_hash:
            raise FailClosedRuntimeError("content-acceptance decision subject already decided")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"human decision failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return str(exc) or "human decision failed closed"
