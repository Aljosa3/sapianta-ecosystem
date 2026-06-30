"""First executable governed self-development session for Generation 4."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.g4_governed_development_loop_execution_scaffold import (
    ADVISORY_ONLY_CHECKPOINT_PASSED,
    BLOCKED_PENDING_GOVERNANCE,
    SCAFFOLD_RECORDED,
    reconstruct_g4_governed_development_loop_scaffold_replay,
    run_g4_governed_development_loop_scaffold,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


G4_SELF_DEVELOPMENT_SESSION_VERSION = "G4_FIRST_EXECUTABLE_GOVERNED_SELF_DEVELOPMENT_SESSION_V1"
SESSION_REQUEST_ARTIFACT_V1 = "G4_SELF_DEVELOPMENT_SESSION_REQUEST_ARTIFACT_V1"
SESSION_SCENARIO_FIXTURE_ARTIFACT_V1 = "G4_SELF_DEVELOPMENT_SCENARIO_FIXTURE_ARTIFACT_V1"
SESSION_SCAFFOLD_CAPTURE_ARTIFACT_V1 = "G4_SELF_DEVELOPMENT_SCAFFOLD_CAPTURE_ARTIFACT_V1"
SESSION_GOVERNANCE_FIXTURE_ARTIFACT_V1 = "G4_SELF_DEVELOPMENT_GOVERNANCE_FIXTURE_ARTIFACT_V1"
SESSION_REPLAY_FIXTURE_ARTIFACT_V1 = "G4_SELF_DEVELOPMENT_REPLAY_FIXTURE_ARTIFACT_V1"
SESSION_SUMMARY_ARTIFACT_V1 = "G4_SELF_DEVELOPMENT_SESSION_SUMMARY_ARTIFACT_V1"

SESSION_RECORDED = "G4_SELF_DEVELOPMENT_SESSION_RECORDED"
SCENARIO_ID = "FIRST_GOVERNED_SELF_DEVELOPMENT_REPLAY_EVIDENCE_REQUEST"
DEFAULT_SELF_DEVELOPMENT_REQUEST = "Add replay evidence for the G4 governed development scaffold."

REPLAY_STEPS = (
    "self_development_session_request_recorded",
    "self_development_scenario_fixture_recorded",
    "self_development_scaffold_capture_recorded",
    "self_development_governance_fixture_recorded",
    "self_development_replay_fixture_recorded",
    "self_development_session_summary_recorded",
)


def run_g4_first_executable_governed_self_development_session(
    *,
    session_id: str,
    operator_request: str = DEFAULT_SELF_DEVELOPMENT_REQUEST,
    operator_response: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute the first governed self-development session in advisory mode."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)

    request = _session_request_artifact(
        session_id=session_id,
        operator_request=operator_request,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], request)

    scenario = _scenario_fixture_artifact(
        session_id=session_id,
        request=request,
        created_at=created_at,
    )
    _persist_step(replay_path, 1, REPLAY_STEPS[1], scenario)

    scaffold_capture = run_g4_governed_development_loop_scaffold(
        scaffold_id=f"{session_id}:G4-02-SCAFFOLD",
        human_intent=request["operator_request"],
        operator_response=operator_response,
        created_at=created_at,
        replay_dir=replay_path / "g4_02_scaffold",
        session_context={
            "g4_session_id": session_id,
            "g4_scenario_id": SCENARIO_ID,
            "copy_paste_workflow_replaced": True,
        },
    )
    scaffold_projection = _scaffold_capture_artifact(
        session_id=session_id,
        scaffold_capture=scaffold_capture,
        created_at=created_at,
    )
    _persist_step(replay_path, 2, REPLAY_STEPS[2], scaffold_projection)

    governance = _governance_fixture_artifact(
        session_id=session_id,
        scaffold_capture=scaffold_capture,
        created_at=created_at,
    )
    _persist_step(replay_path, 3, REPLAY_STEPS[3], governance)

    scaffold_replay = reconstruct_g4_governed_development_loop_scaffold_replay(scaffold_capture["replay_reference"])
    replay_fixture = _replay_fixture_artifact(
        session_id=session_id,
        scaffold_capture=scaffold_capture,
        scaffold_replay=scaffold_replay,
        created_at=created_at,
    )
    _persist_step(replay_path, 4, REPLAY_STEPS[4], replay_fixture)

    summary = _session_summary_artifact(
        session_id=session_id,
        request=request,
        scenario=scenario,
        scaffold_projection=scaffold_projection,
        governance=governance,
        replay_fixture=replay_fixture,
        scaffold_capture=scaffold_capture,
        replay_reference=str(replay_path),
        created_at=created_at,
    )
    _persist_step(replay_path, 5, REPLAY_STEPS[5], summary)
    return _capture(summary, replay_path)


def reconstruct_g4_first_executable_self_development_session_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct the first governed self-development session replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("G4 self-development session replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = _require_mapping(wrapper.get("artifact"), "artifact")
        _verify_artifact_hash(artifact)
        _validate_no_authority(artifact)
        wrappers.append(wrapper)

    request = wrappers[0]["artifact"]
    scenario = wrappers[1]["artifact"]
    scaffold_projection = wrappers[2]["artifact"]
    governance = wrappers[3]["artifact"]
    replay_fixture = wrappers[4]["artifact"]
    summary = wrappers[5]["artifact"]

    if summary["request_hash"] != request["artifact_hash"]:
        raise FailClosedRuntimeError("G4 self-development session request hash mismatch")
    if summary["scenario_fixture_hash"] != scenario["artifact_hash"]:
        raise FailClosedRuntimeError("G4 self-development session scenario hash mismatch")
    if summary["scaffold_capture_hash"] != scaffold_projection["artifact_hash"]:
        raise FailClosedRuntimeError("G4 self-development session scaffold hash mismatch")
    if summary["governance_fixture_hash"] != governance["artifact_hash"]:
        raise FailClosedRuntimeError("G4 self-development session governance hash mismatch")
    if summary["replay_fixture_hash"] != replay_fixture["artifact_hash"]:
        raise FailClosedRuntimeError("G4 self-development session replay fixture hash mismatch")

    scaffold_replay = reconstruct_g4_governed_development_loop_scaffold_replay(
        scaffold_projection["scaffold_replay_reference"]
    )
    if scaffold_replay["replay_hash"] != replay_fixture["scaffold_replay_hash"]:
        raise FailClosedRuntimeError("G4 self-development session scaffold replay hash mismatch")

    return {
        "runtime_version": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "session_id": summary["session_id"],
        "session_status": summary["session_status"],
        "scenario_id": summary["scenario_id"],
        "scaffold_status": scaffold_replay["scaffold_status"],
        "canonical_response_class": summary["canonical_response_class"],
        "governance_checkpoint_status": governance["governance_checkpoint_status"],
        "execution_intent_status": summary["execution_intent_status"],
        "replay_artifact_count": len(wrappers),
        "scaffold_replay_artifact_count": scaffold_replay["replay_artifact_count"],
        "replay_checkpoints": deepcopy(replay_fixture["replay_checkpoints"]),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "copy_paste_workflow_used": False,
        "replay_visible": True,
        "replay_hash": replay_hash(wrappers),
    }


def _session_request_artifact(*, session_id: str, operator_request: str, created_at: str) -> dict[str, Any]:
    request_text = _require_string(operator_request, "operator_request")
    artifact = {
        "artifact_type": SESSION_REQUEST_ARTIFACT_V1,
        "runtime_version": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "scenario_id": SCENARIO_ID,
        "operator_request": request_text,
        "operator_request_hash": replay_hash(request_text),
        "interface_adapter": "ACLI",
        "copy_paste_workflow_used": False,
        "semantic_translation_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _scenario_fixture_artifact(
    *,
    session_id: str,
    request: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": SESSION_SCENARIO_FIXTURE_ARTIFACT_V1,
        "runtime_version": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "fixture_id": f"{_require_string(session_id, 'session_id')}:SCENARIO-FIXTURE",
        "scenario_id": SCENARIO_ID,
        "operator_request_hash": request["artifact_hash"],
        "expected_flow": ["ACLI", "UBTR", "CSA", "OCS", "UHCL", "ACLI", "HUMAN", "GOVERNANCE", "REPLAY"],
        "expected_governance_status": ADVISORY_ONLY_CHECKPOINT_PASSED,
        "expected_execution_intent_status": BLOCKED_PENDING_GOVERNANCE,
        "allowed_human_response_classes": ["CLARIFICATION", "CONFIRMATION", "CONTINUATION", "MODIFICATION", "REJECTION"],
        "repository_mutation_allowed": False,
        "provider_execution_allowed": False,
        "worker_execution_allowed": False,
        "deployment_allowed": False,
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _scaffold_capture_artifact(
    *,
    session_id: str,
    scaffold_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": SESSION_SCAFFOLD_CAPTURE_ARTIFACT_V1,
        "runtime_version": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "capture_id": f"{_require_string(session_id, 'session_id')}:SCAFFOLD-CAPTURE",
        "scaffold_id": scaffold_capture["scaffold_id"],
        "scaffold_status": scaffold_capture["scaffold_status"],
        "scaffold_summary_hash": scaffold_capture["summary_hash"],
        "scaffold_replay_reference": scaffold_capture["replay_reference"],
        "integrated_components": deepcopy(scaffold_capture["integrated_components"]),
        "governance_checkpoint_status": scaffold_capture["governance_checkpoint_status"],
        "canonical_response_class": scaffold_capture["canonical_response_class"],
        "execution_intent_status": scaffold_capture["execution_intent_status"],
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _governance_fixture_artifact(
    *,
    session_id: str,
    scaffold_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": SESSION_GOVERNANCE_FIXTURE_ARTIFACT_V1,
        "runtime_version": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "fixture_id": f"{_require_string(session_id, 'session_id')}:GOVERNANCE-FIXTURE",
        "scaffold_summary_hash": scaffold_capture["summary_hash"],
        "governance_checkpoint_status": scaffold_capture["governance_checkpoint_status"],
        "execution_intent_status": scaffold_capture["execution_intent_status"],
        "semantic_boundary_preserved": True,
        "communication_boundary_preserved": True,
        "proposal_boundary_preserved": True,
        "approval_boundary_preserved": True,
        "authorization_boundary_preserved": True,
        "provider_boundary_preserved": True,
        "worker_boundary_preserved": True,
        "mutation_boundary_preserved": True,
        "replay_boundary_preserved": True,
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


def _replay_fixture_artifact(
    *,
    session_id: str,
    scaffold_capture: dict[str, Any],
    scaffold_replay: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    checkpoints = [
        "session_request",
        "scenario_fixture",
        "scaffold_capture",
        "governance_fixture",
        "replay_fixture",
        "session_summary",
        "scaffold_acli_input",
        "scaffold_ubtr_translation",
        "scaffold_csa_structured_intent",
        "scaffold_ocs_proposal",
        "scaffold_uhcl_communication",
        "scaffold_human_response",
        "scaffold_advisory_execution_intent",
    ]
    artifact = {
        "artifact_type": SESSION_REPLAY_FIXTURE_ARTIFACT_V1,
        "runtime_version": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "fixture_id": f"{_require_string(session_id, 'session_id')}:REPLAY-FIXTURE",
        "scaffold_replay_reference": scaffold_capture["replay_reference"],
        "scaffold_replay_hash": scaffold_replay["replay_hash"],
        "scaffold_replay_artifact_count": scaffold_replay["replay_artifact_count"],
        "scaffold_sub_replay_artifact_count": scaffold_replay["sub_replay_artifact_count"],
        "replay_checkpoints": checkpoints,
        "replay_checkpoint_count": len(checkpoints),
        "deterministic_reconstruction_required": True,
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _session_summary_artifact(
    *,
    session_id: str,
    request: dict[str, Any],
    scenario: dict[str, Any],
    scaffold_projection: dict[str, Any],
    governance: dict[str, Any],
    replay_fixture: dict[str, Any],
    scaffold_capture: dict[str, Any],
    replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": SESSION_SUMMARY_ARTIFACT_V1,
        "runtime_version": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "session_status": SESSION_RECORDED,
        "scenario_id": SCENARIO_ID,
        "request_hash": request["artifact_hash"],
        "scenario_fixture_hash": scenario["artifact_hash"],
        "scaffold_capture_hash": scaffold_projection["artifact_hash"],
        "governance_fixture_hash": governance["artifact_hash"],
        "replay_fixture_hash": replay_fixture["artifact_hash"],
        "scaffold_summary_hash": scaffold_capture["summary_hash"],
        "canonical_response_class": scaffold_capture["canonical_response_class"],
        "governance_checkpoint_status": governance["governance_checkpoint_status"],
        "execution_intent_status": scaffold_capture["execution_intent_status"],
        "copy_paste_workflow_used": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
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


def _capture(summary: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "runtime_version": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "session_id": summary["session_id"],
        "session_status": summary["session_status"],
        "scenario_id": summary["scenario_id"],
        "summary_artifact": deepcopy(summary),
        "summary_hash": summary["artifact_hash"],
        "replay_reference": str(replay_path),
        "canonical_response_class": summary["canonical_response_class"],
        "governance_checkpoint_status": summary["governance_checkpoint_status"],
        "execution_intent_status": summary["execution_intent_status"],
        "provider_invoked": False,
        "worker_invoked": False,
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
        "event_type": G4_SELF_DEVELOPMENT_SESSION_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{replay_index:03d}_{replay_step}.json", wrapper)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("G4 self-development session replay already exists")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("G4 self-development session replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("G4 self-development session artifact hash mismatch")


def _validate_no_authority(artifact: dict[str, Any]) -> None:
    for field in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"G4 self-development session cannot set {field}")


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
