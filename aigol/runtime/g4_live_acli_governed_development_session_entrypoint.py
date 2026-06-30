"""Live ACLI entrypoint for the G4 governed development session."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.g4_first_executable_governed_self_development_session import (
    G4_SELF_DEVELOPMENT_SESSION_VERSION,
    reconstruct_g4_first_executable_self_development_session_replay,
    run_g4_first_executable_governed_self_development_session,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION = "G4_05_LIVE_ACLI_GOVERNED_DEVELOPMENT_SESSION_ENTRYPOINT_V1"
LIVE_ACLI_CAPTURE_ARTIFACT_V1 = "G4_05_LIVE_ACLI_CAPTURE_ARTIFACT_V1"
LIVE_SESSION_CREATION_ARTIFACT_V1 = "G4_05_LIVE_SESSION_CREATION_ARTIFACT_V1"
LIVE_G4_04_ROUTING_ARTIFACT_V1 = "G4_05_LIVE_G4_04_ROUTING_ARTIFACT_V1"
LIVE_G4_04_CAPTURE_ARTIFACT_V1 = "G4_05_LIVE_G4_04_CAPTURE_ARTIFACT_V1"
LIVE_SESSION_EVIDENCE_ARTIFACT_V1 = "G4_05_LIVE_SESSION_EVIDENCE_ARTIFACT_V1"

LIVE_ACLI_SESSION_RECORDED = "G4_05_LIVE_ACLI_SESSION_RECORDED"
LIVE_ACLI_ROUTED_TO_G4_04 = "G4_05_LIVE_ACLI_ROUTED_TO_G4_04"
COMMAND_NAME = "aigol g4-live-session"

REPLAY_STEPS = (
    "live_acli_capture_recorded",
    "live_session_creation_recorded",
    "live_g4_04_routing_recorded",
    "live_g4_04_capture_recorded",
    "live_session_evidence_recorded",
)


def run_g4_live_acli_governed_development_session_entrypoint(
    *,
    session_id: str,
    operator_request: str,
    operator_response: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Capture a live ACLI request and route it into the certified G4-04 session."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)

    capture = _live_acli_capture_artifact(
        session_id=session_id,
        operator_request=operator_request,
        operator_response=operator_response,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], capture)

    session = _live_session_creation_artifact(
        session_id=session_id,
        capture=capture,
        created_at=created_at,
    )
    _persist_step(replay_path, 1, REPLAY_STEPS[1], session)

    routing = _live_routing_artifact(
        session_id=session_id,
        capture=capture,
        session=session,
        created_at=created_at,
    )
    _persist_step(replay_path, 2, REPLAY_STEPS[2], routing)

    g4_04_capture = run_g4_first_executable_governed_self_development_session(
        session_id=f"{session_id}:G4-04",
        operator_request=capture["operator_request"],
        operator_response=capture["operator_response"],
        created_at=created_at,
        replay_dir=replay_path / "g4_04_session",
    )
    g4_04_projection = _g4_04_capture_artifact(
        session_id=session_id,
        routing=routing,
        g4_04_capture=g4_04_capture,
        created_at=created_at,
    )
    _persist_step(replay_path, 3, REPLAY_STEPS[3], g4_04_projection)

    g4_04_replay = reconstruct_g4_first_executable_self_development_session_replay(
        g4_04_capture["replay_reference"]
    )
    evidence = _live_session_evidence_artifact(
        session_id=session_id,
        capture=capture,
        session=session,
        routing=routing,
        g4_04_projection=g4_04_projection,
        g4_04_capture=g4_04_capture,
        g4_04_replay=g4_04_replay,
        replay_reference=str(replay_path),
        created_at=created_at,
    )
    _persist_step(replay_path, 4, REPLAY_STEPS[4], evidence)
    return _result(evidence, replay_path)


def reconstruct_g4_live_acli_governed_development_session_entrypoint_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct the G4-05 live ACLI session replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("G4-05 live ACLI session replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = _require_mapping(wrapper.get("artifact"), "artifact")
        _verify_artifact_hash(artifact)
        _validate_no_authority(artifact)
        wrappers.append(wrapper)

    capture = wrappers[0]["artifact"]
    session = wrappers[1]["artifact"]
    routing = wrappers[2]["artifact"]
    g4_04_projection = wrappers[3]["artifact"]
    evidence = wrappers[4]["artifact"]

    if session["live_acli_capture_hash"] != capture["artifact_hash"]:
        raise FailClosedRuntimeError("G4-05 live ACLI capture hash mismatch")
    if routing["live_session_creation_hash"] != session["artifact_hash"]:
        raise FailClosedRuntimeError("G4-05 live session hash mismatch")
    if g4_04_projection["routing_hash"] != routing["artifact_hash"]:
        raise FailClosedRuntimeError("G4-05 routing hash mismatch")
    if evidence["g4_04_capture_hash"] != g4_04_projection["artifact_hash"]:
        raise FailClosedRuntimeError("G4-05 G4-04 projection hash mismatch")

    g4_04_replay = reconstruct_g4_first_executable_self_development_session_replay(
        g4_04_projection["g4_04_replay_reference"]
    )
    if g4_04_replay["replay_hash"] != evidence["g4_04_replay_hash"]:
        raise FailClosedRuntimeError("G4-05 G4-04 replay hash mismatch")

    return {
        "runtime_version": G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
        "command": COMMAND_NAME,
        "session_id": evidence["session_id"],
        "session_status": evidence["session_status"],
        "routing_status": routing["routing_status"],
        "target_runtime": routing["target_runtime"],
        "canonical_response_class": evidence["canonical_response_class"],
        "governance_checkpoint_status": evidence["governance_checkpoint_status"],
        "execution_intent_status": evidence["execution_intent_status"],
        "replay_artifact_count": len(wrappers),
        "g4_04_replay_artifact_count": g4_04_replay["replay_artifact_count"],
        "replay_reference": str(replay_path),
        "g4_04_replay_reference": g4_04_projection["g4_04_replay_reference"],
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "copy_paste_workflow_used": False,
        "replay_visible": True,
        "replay_hash": replay_hash(wrappers),
    }


def render_g4_live_acli_session_summary(result: dict[str, Any]) -> str:
    """Render the live ACLI session result without creating reusable communication semantics."""

    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"session_id: {result.get('session_id')}",
            f"session_status: {result.get('session_status')}",
            f"routing_status: {result.get('routing_status')}",
            f"target_runtime: {result.get('target_runtime')}",
            f"canonical_response_class: {result.get('canonical_response_class')}",
            f"governance_checkpoint_status: {result.get('governance_checkpoint_status')}",
            f"execution_intent_status: {result.get('execution_intent_status')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"g4_04_replay_reference: {result.get('g4_04_replay_reference')}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"worker_invoked: {result.get('worker_invoked')}",
            f"approval_created: {result.get('approval_created')}",
            f"authorization_created: {result.get('authorization_created')}",
            f"repository_mutated: {result.get('repository_mutated')}",
            f"deployment_performed: {result.get('deployment_performed')}",
        ]
    )


def _live_acli_capture_artifact(
    *,
    session_id: str,
    operator_request: str,
    operator_response: str,
    created_at: str,
) -> dict[str, Any]:
    request = _require_string(operator_request, "operator_request")
    response = _require_string(operator_response, "operator_response")
    artifact = {
        "artifact_type": LIVE_ACLI_CAPTURE_ARTIFACT_V1,
        "runtime_version": G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
        "capture_id": f"{_require_string(session_id, 'session_id')}:LIVE-ACLI-CAPTURE",
        "session_id": _require_string(session_id, "session_id"),
        "command": COMMAND_NAME,
        "interface_adapter": "ACLI",
        "adapter_scope": [
            "input_capture",
            "terminal_rendering",
            "response_capture",
            "session_interaction",
        ],
        "operator_request": request,
        "operator_request_hash": replay_hash(request),
        "operator_response": response,
        "operator_response_hash": replay_hash(response),
        "semantic_translation_performed": False,
        "communication_generated": False,
        "provider_logic_owned": False,
        "worker_logic_owned": False,
        "replay_logic_owned": False,
        "governance_logic_owned": False,
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _live_session_creation_artifact(
    *,
    session_id: str,
    capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": LIVE_SESSION_CREATION_ARTIFACT_V1,
        "runtime_version": G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "session_status": LIVE_ACLI_SESSION_RECORDED,
        "live_acli_capture_hash": capture["artifact_hash"],
        "session_source": "LIVE_ACLI_OPERATOR_INPUT",
        "fixture_entrypoint_used": False,
        "copy_paste_workflow_used": False,
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _live_routing_artifact(
    *,
    session_id: str,
    capture: dict[str, Any],
    session: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": LIVE_G4_04_ROUTING_ARTIFACT_V1,
        "runtime_version": G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
        "route_id": f"{_require_string(session_id, 'session_id')}:ROUTE-G4-04",
        "session_id": _require_string(session_id, "session_id"),
        "routing_status": LIVE_ACLI_ROUTED_TO_G4_04,
        "live_acli_capture_hash": capture["artifact_hash"],
        "live_session_creation_hash": session["artifact_hash"],
        "source_interface_adapter": "ACLI",
        "target_runtime": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "target_runtime_scope": "ADVISORY_ONLY_GOVERNED_DEVELOPMENT_SESSION",
        "route_reason": "Live ACLI request is passed unchanged into the certified G4-04 governed self-development session.",
        "semantic_translation_owner": "UBTR",
        "structured_intent_owner": "CSA",
        "orchestration_owner": "OCS",
        "human_communication_owner": "UHCL",
        "adapter_owner": "ACLI",
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _g4_04_capture_artifact(
    *,
    session_id: str,
    routing: dict[str, Any],
    g4_04_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": LIVE_G4_04_CAPTURE_ARTIFACT_V1,
        "runtime_version": G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
        "capture_id": f"{_require_string(session_id, 'session_id')}:G4-04-CAPTURE",
        "session_id": _require_string(session_id, "session_id"),
        "routing_hash": routing["artifact_hash"],
        "g4_04_session_id": g4_04_capture["session_id"],
        "g4_04_session_status": g4_04_capture["session_status"],
        "g4_04_summary_hash": g4_04_capture["summary_hash"],
        "g4_04_replay_reference": g4_04_capture["replay_reference"],
        "canonical_response_class": g4_04_capture["canonical_response_class"],
        "governance_checkpoint_status": g4_04_capture["governance_checkpoint_status"],
        "execution_intent_status": g4_04_capture["execution_intent_status"],
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _live_session_evidence_artifact(
    *,
    session_id: str,
    capture: dict[str, Any],
    session: dict[str, Any],
    routing: dict[str, Any],
    g4_04_projection: dict[str, Any],
    g4_04_capture: dict[str, Any],
    g4_04_replay: dict[str, Any],
    replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": LIVE_SESSION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "session_status": LIVE_ACLI_SESSION_RECORDED,
        "live_acli_capture_hash": capture["artifact_hash"],
        "live_session_creation_hash": session["artifact_hash"],
        "routing_hash": routing["artifact_hash"],
        "g4_04_capture_hash": g4_04_projection["artifact_hash"],
        "g4_04_summary_hash": g4_04_capture["summary_hash"],
        "g4_04_replay_hash": g4_04_replay["replay_hash"],
        "routing_status": routing["routing_status"],
        "target_runtime": routing["target_runtime"],
        "canonical_response_class": g4_04_capture["canonical_response_class"],
        "governance_checkpoint_status": g4_04_capture["governance_checkpoint_status"],
        "execution_intent_status": g4_04_capture["execution_intent_status"],
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "g4_04_replay_reference": g4_04_capture["replay_reference"],
        "replay_evidence": {
            "live_replay_steps": list(REPLAY_STEPS),
            "g4_04_replay_hash": g4_04_replay["replay_hash"],
            "g4_04_replay_artifact_count": g4_04_replay["replay_artifact_count"],
        },
        "governance_evidence": {
            "governance_checkpoint_status": g4_04_capture["governance_checkpoint_status"],
            "execution_intent_status": g4_04_capture["execution_intent_status"],
            "approval_boundary_preserved": True,
            "authorization_boundary_preserved": True,
            "provider_boundary_preserved": True,
            "worker_boundary_preserved": True,
            "mutation_boundary_preserved": True,
            "replay_boundary_preserved": True,
        },
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "copy_paste_workflow_used": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _result(evidence: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "command": COMMAND_NAME,
        "runtime_version": G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
        "session_id": evidence["session_id"],
        "session_status": evidence["session_status"],
        "routing_status": evidence["routing_status"],
        "target_runtime": evidence["target_runtime"],
        "canonical_response_class": evidence["canonical_response_class"],
        "governance_checkpoint_status": evidence["governance_checkpoint_status"],
        "execution_intent_status": evidence["execution_intent_status"],
        "summary_artifact": deepcopy(evidence),
        "summary_hash": evidence["artifact_hash"],
        "replay_reference": str(replay_path),
        "g4_04_replay_reference": evidence["g4_04_replay_reference"],
        "g4_04_replay_hash": evidence["g4_04_replay_hash"],
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "copy_paste_workflow_used": False,
        "replay_visible": True,
    }


def _persist_step(replay_path: Path, replay_index: int, replay_step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": replay_index,
        "replay_step": replay_step,
        "event_type": G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{replay_index:03d}_{replay_step}.json", wrapper)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("G4-05 live ACLI session replay already exists")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("G4-05 live ACLI session replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("G4-05 live ACLI session artifact hash mismatch")


def _validate_no_authority(artifact: dict[str, Any]) -> None:
    for field in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
        "authority_granted",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"G4-05 live ACLI session cannot set {field}")


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
