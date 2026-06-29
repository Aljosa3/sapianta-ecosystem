"""Runtime certification for the G3 ACLI primary development interface."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_authorization_bridge import (
    ACLI_AUTHORIZATION_BRIDGE_ARTIFACT_V1,
    AUTHORIZATION_READY,
    PRECONDITIONS_SATISFIED,
)
from aigol.runtime.acli_conversational_development_session import (
    ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1,
)
from aigol.runtime.acli_development_session_lifecycle import (
    ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1,
)
from aigol.runtime.acli_operator_rendering_and_confirmation import (
    ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1,
    ACLI_OPERATOR_RENDERING_ARTIFACT_V1,
)
from aigol.runtime.acli_proposal_approval_bridge import (
    ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1,
    APPROVAL_RECORDED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_RUNTIME_VERSION = (
    "G3_02_IMPLEMENTATION_PHASE_6_RUNTIME_CERTIFICATION_RUNTIME_V1"
)
ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_ARTIFACT_V1 = (
    "ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_ARTIFACT_V1"
)

G3_02_RUNTIME_CERTIFIED = "G3_02_RUNTIME_CERTIFIED"
FAILED_CLOSED = "FAILED_CLOSED"

EVENT_CERTIFICATION_RECORDED = "acli_primary_development_interface_certification_recorded"

CERTIFICATION_SCOPE = (
    "session_lifecycle_integrity",
    "conversational_continuity",
    "csa_lineage",
    "replay_integrity",
    "proposal_lineage",
    "approval_lineage",
    "authorization_readiness",
    "rollback_capability",
    "non_authority_guarantees",
    "governance_preservation",
)

NON_AUTHORITY_FLAGS = (
    "provider_invoked",
    "worker_invoked",
    "authorization_created",
    "execution_requested",
    "repository_mutated",
    "deployment_requested",
    "product1_workflow_started",
)


def certify_acli_primary_development_interface(
    *,
    certification_id: str,
    session_artifact: dict[str, Any],
    conversation_artifact: dict[str, Any],
    operator_rendering_artifact: dict[str, Any],
    confirmation_classification_artifact: dict[str, Any],
    proposal_artifact: dict[str, Any],
    authorization_bridge_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Certify the complete G3-02 ACLI runtime chain without adding capability."""

    try:
        session = _validated_artifact(
            session_artifact,
            ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1,
            "session lifecycle",
        )
        conversation = _validated_artifact(
            conversation_artifact,
            ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1,
            "conversation",
        )
        rendering = _validated_artifact(
            operator_rendering_artifact,
            ACLI_OPERATOR_RENDERING_ARTIFACT_V1,
            "operator rendering",
        )
        confirmation = _validated_artifact(
            confirmation_classification_artifact,
            ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1,
            "confirmation classification",
        )
        proposal = _validated_artifact(
            proposal_artifact,
            ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1,
            "proposal approval bridge",
        )
        authorization = _validated_artifact(
            authorization_bridge_artifact,
            ACLI_AUTHORIZATION_BRIDGE_ARTIFACT_V1,
            "authorization bridge",
        )
        checks = _certification_checks(
            session=session,
            conversation=conversation,
            rendering=rendering,
            confirmation=confirmation,
            proposal=proposal,
            authorization=authorization,
        )
        failed = [check["check_name"] for check in checks if check["check_passed"] is not True]
        status = G3_02_RUNTIME_CERTIFIED if not failed else FAILED_CLOSED
        failure_reason = None if not failed else "G3-02 certification failed closed: " + ", ".join(failed)
        references = _references(session, conversation, rendering, confirmation, proposal, authorization)
        csa_reference = authorization["canonical_semantic_artifact_reference"]
        csa_hash = authorization["canonical_semantic_artifact_hash"]
        rollback_reference = authorization["rollback_reference"]
    except Exception as exc:
        checks = _failed_checks(_failure_reason(exc))
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)
        references = _fallback_references(
            session_artifact,
            conversation_artifact,
            operator_rendering_artifact,
            confirmation_classification_artifact,
            proposal_artifact,
            authorization_bridge_artifact,
        )
        csa_reference = _safe_string(authorization_bridge_artifact.get("canonical_semantic_artifact_reference"))
        csa_hash = _safe_string(authorization_bridge_artifact.get("canonical_semantic_artifact_hash"))
        rollback_reference = _safe_string(authorization_bridge_artifact.get("rollback_reference"))

    event = _event(
        event_index=0,
        event_type=EVENT_CERTIFICATION_RECORDED,
        occurred_at=created_at,
        event_payload={
            "certification_id": _safe_string(certification_id),
            "certification_status": status,
            "failed_check_count": sum(1 for check in checks if check["check_passed"] is not True),
        },
    )
    artifact = {
        "artifact_type": ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_6_RUNTIME_CERTIFICATION_V1",
        "certification_id": _safe_string(certification_id),
        "created_at": _safe_string(created_at),
        "certification_status": status,
        "certification_scope": list(CERTIFICATION_SCOPE),
        "certification_checks": deepcopy(checks),
        "certification_check_count": len(checks),
        "passed_check_count": sum(1 for check in checks if check["check_passed"] is True),
        "failed_check_count": sum(1 for check in checks if check["check_passed"] is not True),
        "session_id": references["session_id"],
        "conversation_id": references["conversation_id"],
        "turn_id": references["turn_id"],
        "proposal_id": references["proposal_id"],
        "authorization_bridge_id": references["authorization_bridge_id"],
        "canonical_semantic_artifact_reference": csa_reference,
        "canonical_semantic_artifact_hash": csa_hash,
        "rollback_reference": rollback_reference,
        "source_references": references,
        "replay_guarantees": _replay_guarantees(status),
        "remaining_limitations": _remaining_limitations(),
        "recommended_certification": status == G3_02_RUNTIME_CERTIFIED,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "event": event,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    replay_path = Path(replay_dir)
    _persist_step(replay_path, 0, EVENT_CERTIFICATION_RECORDED, artifact)
    return _capture(artifact, replay_path)


def reconstruct_acli_primary_development_interface_certification_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate G3-02 certification replay."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("ACLI primary development interface certification failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("ACLI primary development interface certification replay ordering mismatch")
    artifact = _validated_artifact(
        wrappers[-1]["artifact"],
        ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_ARTIFACT_V1,
        "certification",
    )
    event = artifact.get("event")
    if not isinstance(event, dict) or event.get("event_index") != 0:
        raise FailClosedRuntimeError("ACLI primary development interface certification event mismatch")
    _verify_hash_field(event, "event_hash", "ACLI primary development interface certification event hash mismatch")
    return {
        "certification_id": artifact["certification_id"],
        "certification_status": artifact["certification_status"],
        "certification_scope": deepcopy(artifact["certification_scope"]),
        "certification_check_count": artifact["certification_check_count"],
        "passed_check_count": artifact["passed_check_count"],
        "failed_check_count": artifact["failed_check_count"],
        "session_id": artifact["session_id"],
        "conversation_id": artifact["conversation_id"],
        "turn_id": artifact["turn_id"],
        "proposal_id": artifact["proposal_id"],
        "authorization_bridge_id": artifact["authorization_bridge_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "rollback_reference": artifact["rollback_reference"],
        "recommended_certification": artifact["recommended_certification"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
    }


def _certification_checks(
    *,
    session: dict[str, Any],
    conversation: dict[str, Any],
    rendering: dict[str, Any],
    confirmation: dict[str, Any],
    proposal: dict[str, Any],
    authorization: dict[str, Any],
) -> list[dict[str, Any]]:
    turn = _latest_turn(conversation)
    return [
        _check("session_lifecycle_integrity", conversation["session_artifact_hash"] == session["artifact_hash"]),
        _check(
            "conversational_continuity",
            turn is not None
            and turn["session_id"] == session["session_id"]
            and rendering["session_id"] == session["session_id"]
            and confirmation["session_id"] == session["session_id"]
            and rendering["conversation_hash"] == conversation["artifact_hash"]
            and confirmation["conversation_hash"] == conversation["artifact_hash"],
        ),
        _check(
            "csa_lineage",
            turn is not None
            and proposal["canonical_semantic_artifact_hash"] == turn["canonical_semantic_artifact_hash"]
            and authorization["canonical_semantic_artifact_hash"] == proposal["canonical_semantic_artifact_hash"],
        ),
        _check("replay_integrity", all(_artifact_replay_visible(item) for item in (session, conversation, rendering, confirmation, proposal, authorization))),
        _check(
            "proposal_lineage",
            proposal["originating_session_id"] == session["session_id"]
            and turn is not None
            and proposal["originating_turn_id"] == turn["turn_id"],
        ),
        _check(
            "approval_lineage",
            proposal["approval_status"] == APPROVAL_RECORDED
            and bool(proposal["approval_requests"])
            and bool(proposal["approval_decisions"])
            and proposal["approval_decisions"][-1]["approval_request_id"] == proposal["approval_requests"][-1]["approval_request_id"],
        ),
        _check(
            "authorization_readiness",
            authorization["authorization_readiness_status"] == AUTHORIZATION_READY
            and authorization["precondition_status"] == PRECONDITIONS_SATISFIED,
        ),
        _check(
            "rollback_capability",
            bool(proposal.get("rollback_reference"))
            and authorization["rollback_reference"] == proposal["rollback_reference"],
        ),
        _check(
            "non_authority_guarantees",
            all(_non_authority_preserved(item) for item in (session, conversation, rendering, confirmation, proposal, authorization)),
        ),
        _check(
            "governance_preservation",
            all(
                value is True
                for key, value in session["governance_checkpoints"].items()
                if key.endswith("_preserved")
            ),
        ),
    ]


def _check(name: str, passed: bool) -> dict[str, Any]:
    check = {"check_name": name, "check_passed": bool(passed)}
    check["check_hash"] = replay_hash(check)
    return check


def _failed_checks(reason: str) -> list[dict[str, Any]]:
    checks = [_check(name, False) for name in CERTIFICATION_SCOPE]
    for check in checks:
        check["failure_reason"] = reason
        check["check_hash"] = replay_hash({key: value for key, value in check.items() if key != "check_hash"})
    return checks


def _references(
    session: dict[str, Any],
    conversation: dict[str, Any],
    rendering: dict[str, Any],
    confirmation: dict[str, Any],
    proposal: dict[str, Any],
    authorization: dict[str, Any],
) -> dict[str, Any]:
    return {
        "session_id": session["session_id"],
        "session_hash": session["artifact_hash"],
        "conversation_id": conversation["conversation_id"],
        "conversation_hash": conversation["artifact_hash"],
        "turn_id": proposal["originating_turn_id"],
        "render_id": rendering["render_id"],
        "rendering_hash": rendering["artifact_hash"],
        "classification_id": confirmation["classification_id"],
        "confirmation_hash": confirmation["artifact_hash"],
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "approval_request_id": proposal["approval_requests"][-1]["approval_request_id"],
        "approval_decision_id": proposal["approval_decisions"][-1]["approval_decision_id"],
        "authorization_bridge_id": authorization["authorization_bridge_id"],
        "authorization_bridge_hash": authorization["artifact_hash"],
    }


def _fallback_references(*artifacts: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "session",
        "conversation",
        "rendering",
        "confirmation",
        "proposal",
        "authorization_bridge",
    )
    refs = {f"{key}_hash": _safe_string(artifact.get("artifact_hash")) for key, artifact in zip(keys, artifacts)}
    refs.update(
        {
            "session_id": _safe_string(artifacts[0].get("session_id")),
            "conversation_id": _safe_string(artifacts[1].get("conversation_id")),
            "turn_id": _safe_string(artifacts[4].get("originating_turn_id")),
            "proposal_id": _safe_string(artifacts[4].get("proposal_id")),
            "authorization_bridge_id": _safe_string(artifacts[5].get("authorization_bridge_id")),
        }
    )
    return refs


def _latest_turn(conversation: dict[str, Any]) -> dict[str, Any] | None:
    turns = conversation.get("turns")
    return deepcopy(turns[-1]) if isinstance(turns, list) and turns else None


def _artifact_replay_visible(artifact: dict[str, Any]) -> bool:
    return artifact.get("replay_visible") is True and isinstance(artifact.get("artifact_hash"), str)


def _non_authority_preserved(artifact: dict[str, Any]) -> bool:
    return all(artifact.get(flag) is False for flag in NON_AUTHORITY_FLAGS if flag in artifact)


def _replay_guarantees(status: str) -> dict[str, Any]:
    return {
        "hash_bound": True,
        "replay_visible": True,
        "lineage_checked": status == G3_02_RUNTIME_CERTIFIED,
        "non_authority_checked": status == G3_02_RUNTIME_CERTIFIED,
        "fail_closed_on_mismatch": True,
    }


def _remaining_limitations() -> list[str]:
    return [
        "G3-02 certification does not authorize worker execution.",
        "G3-02 certification does not invoke providers.",
        "G3-02 certification does not mutate repositories.",
        "G3-02 certification does not start Product 1 runtime.",
        "Deployment and release handoff remain later Generation 3 workstreams.",
    ]


def _event(*, event_index: int, event_type: str, occurred_at: str, event_payload: dict[str, Any]) -> dict[str, Any]:
    event = {
        "event_index": event_index,
        "event_type": event_type,
        "occurred_at": _safe_string(occurred_at),
        "event_payload": deepcopy(event_payload),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if path.exists():
        raise FailClosedRuntimeError("ACLI primary development interface certification failed closed: replay already exists")
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


def _load_verified_wrapper(path: Path) -> dict[str, Any]:
    wrapper = load_json(path)
    _verify_hash_field(wrapper, "replay_hash", "ACLI primary development interface certification replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI primary development interface certification replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "ACLI primary development interface certification artifact hash mismatch")
    return wrapper


def _validated_artifact(artifact: dict[str, Any], artifact_type: str, label: str) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"ACLI primary development interface certification failed closed: {label} must be object")
    if artifact.get("artifact_type") != artifact_type:
        raise FailClosedRuntimeError(f"ACLI primary development interface certification failed closed: invalid {label} artifact")
    _verify_hash_field(artifact, "artifact_hash", f"ACLI primary development interface certification {label} hash mismatch")
    return deepcopy(artifact)


def _verify_hash_field(value: dict[str, Any], field_name: str, message: str) -> None:
    actual = value.get(field_name)
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field_name)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_RUNTIME_VERSION,
        "certification_artifact": deepcopy(artifact),
        "certification_id": artifact["certification_id"],
        "certification_status": artifact["certification_status"],
        "recommended_certification": artifact["recommended_certification"],
        "certification_check_count": artifact["certification_check_count"],
        "passed_check_count": artifact["passed_check_count"],
        "failed_check_count": artifact["failed_check_count"],
        "replay_reference": str(replay_path),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "failure_reason": artifact["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _failure_reason(exc: Exception) -> str:
    return str(exc) if str(exc) else exc.__class__.__name__


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "UNKNOWN"
