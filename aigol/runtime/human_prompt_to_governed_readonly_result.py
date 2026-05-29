"""End-to-end human prompt to governed read-only result flow."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.filesystem_read_only_capability import FILESYSTEM_READ_ONLY_INSPECTION
from aigol.runtime.minimal_cognition_to_execution_bridge import (
    FAILED,
    READ_ONLY_RUNTIME_INSPECTION,
    RETURNED,
    execute_cognition_to_execution_bridge,
    reconstruct_cognition_execution_bridge_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


HUMAN_PROMPT_CAPTURED = "HUMAN_PROMPT_CAPTURED"
PROPOSAL_CREATED = "PROPOSAL_CREATED"
BRIDGE_CAPTURED = "BRIDGE_CAPTURED"
GOVERNED_RESULT_RETURNED = "GOVERNED_RESULT_RETURNED"
OPERATOR_FAILED = "FAILED"
OPERATOR_COMPLETED = "COMPLETED"

SUPPORTED_READONLY_CAPABILITIES = frozenset({READ_ONLY_RUNTIME_INSPECTION, FILESYSTEM_READ_ONLY_INSPECTION})
REPLAY_STEPS = ("human_prompt", "cognition_proposal", "bridge_capture", "governed_result")
HIDDEN_CONTINUATION_TERMS = (
    "continue autonomously",
    "hidden continuation",
    "auto retry",
    "recursive",
    "agent",
    "orchestrate",
)
FORBIDDEN_PROMPT_TERMS = (
    "write",
    "delete",
    "move",
    "modify",
    "shell",
    "network",
    "api",
    "mutate",
)


def run_human_prompt_to_governed_readonly_result(
    *,
    operator_flow_id: str,
    human_prompt: str,
    target_capability: str,
    created_at: str,
    replay_dir: str | Path,
    root_path: str | Path | None = None,
    requested_path: str | Path | None = None,
    allowed_paths: list[str | Path] | None = None,
    authorize: bool = True,
) -> dict[str, Any]:
    """Run one bounded prompt -> proposal -> governed read-only result flow."""

    replay_path = Path(replay_dir)
    try:
        prompt_artifact = create_human_prompt_artifact(
            operator_flow_id=operator_flow_id,
            human_prompt=human_prompt,
            target_capability=target_capability,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, "human_prompt", prompt_artifact)
        proposal = create_cognition_proposal_from_human_prompt(
            prompt_artifact,
            replay_dir=replay_path,
            root_path=root_path,
            requested_path=requested_path,
            allowed_paths=allowed_paths,
        )
        _persist_step(replay_path, 1, "cognition_proposal", proposal)
        bridge_capture = execute_cognition_to_execution_bridge(
            bridge_id=f"{operator_flow_id}:BRIDGE",
            execution_id=f"{operator_flow_id}:EXECUTION",
            request_id=f"{operator_flow_id}:REQUEST",
            cognition_output=proposal["cognition_proposal"],
            created_at=prompt_artifact["created_at"],
            replay_dir=replay_path / "bridge_replay",
            authorize=authorize,
        )
        bridge_artifact = create_bridge_capture_artifact(prompt_artifact, proposal, bridge_capture)
        _persist_step(replay_path, 2, "bridge_capture", bridge_artifact)
        governed_result = create_governed_readonly_result(prompt_artifact, proposal, bridge_artifact)
        _persist_step(replay_path, 3, "governed_result", governed_result)
        return _capture(prompt_artifact, proposal, bridge_artifact, governed_result)
    except Exception as exc:
        failure = _failure_artifact(
            operator_flow_id=operator_flow_id if isinstance(operator_flow_id, str) and operator_flow_id else "OPERATOR-FLOW-INVALID",
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_sequence(replay_path, failure)
        return _capture(None, None, None, failure)


def create_human_prompt_artifact(
    *,
    operator_flow_id: str,
    human_prompt: str,
    target_capability: str,
    created_at: str,
) -> dict[str, Any]:
    """Capture an operator prompt before creating a proposal."""

    prompt = _normalize_text(human_prompt, "human_prompt")
    _reject_unsafe_prompt(prompt)
    capability = _normalize_token(target_capability, "target_capability")
    if capability not in SUPPORTED_READONLY_CAPABILITIES:
        raise FailClosedRuntimeError("unsupported read-only capability")
    artifact = {
        "operator_flow_id": _require_string(operator_flow_id, "operator_flow_id"),
        "state": HUMAN_PROMPT_CAPTURED,
        "human_prompt": prompt,
        "target_capability": capability,
        "created_at": _require_string(created_at, "created_at"),
        "llm_proposes_only": True,
        "aigol_governs": True,
        "worker_executes_only_after_authorization": True,
        "replay_records": True,
        "execution_authority": False,
        "authorization_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_cognition_proposal_from_human_prompt(
    prompt_artifact: dict[str, Any],
    *,
    replay_dir: str | Path,
    root_path: str | Path | None = None,
    requested_path: str | Path | None = None,
    allowed_paths: list[str | Path] | None = None,
) -> dict[str, Any]:
    """Create deterministic proposal input for the existing bridge."""

    _verify_artifact_hash(prompt_artifact)
    capability = prompt_artifact["target_capability"]
    arguments: dict[str, Any] = {"capability_replay_dir": str(Path(replay_dir) / "capability_replay")}
    intent = "inspect runtime metadata"
    if capability == FILESYSTEM_READ_ONLY_INSPECTION:
        if root_path is None or requested_path is None or not allowed_paths:
            raise FailClosedRuntimeError("filesystem read-only proposal requires explicit allowed path scope")
        arguments.update(
            {
                "root_path": _require_string(str(root_path), "root_path"),
                "requested_path": _require_string(str(requested_path), "requested_path"),
                "allowed_paths": [_require_string(str(path), "allowed_path") for path in allowed_paths],
            }
        )
        intent = "inspect allowed file"
    proposal = {
        "contribution_id": f"{prompt_artifact['operator_flow_id']}:COGNITION-PROPOSAL",
        "human_prompt": prompt_artifact["human_prompt"],
        "target_capability": capability,
        "intent": intent,
        "created_at": prompt_artifact["created_at"],
        "arguments": arguments,
    }
    artifact = {
        "operator_flow_id": prompt_artifact["operator_flow_id"],
        "state": PROPOSAL_CREATED,
        "human_prompt_hash": prompt_artifact["artifact_hash"],
        "cognition_proposal": proposal,
        "untrusted_proposal_input": True,
        "llm_execution_authority": False,
        "llm_authorization_authority": False,
        "new_capability_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_bridge_capture_artifact(
    prompt_artifact: dict[str, Any],
    proposal_artifact: dict[str, Any],
    bridge_capture: dict[str, Any],
) -> dict[str, Any]:
    """Capture bridge result evidence without granting proposal authority."""

    _verify_artifact_hash(prompt_artifact)
    _verify_artifact_hash(proposal_artifact)
    if not isinstance(bridge_capture, dict) or "return" not in bridge_capture:
        raise FailClosedRuntimeError("bridge capture is malformed")
    governed_return = bridge_capture["return"]
    if not isinstance(governed_return, dict):
        raise FailClosedRuntimeError("bridge governed return is malformed")
    bridge_status = governed_return.get("final_status")
    artifact = {
        "operator_flow_id": prompt_artifact["operator_flow_id"],
        "state": BRIDGE_CAPTURED,
        "human_prompt_hash": prompt_artifact["artifact_hash"],
        "proposal_hash": proposal_artifact["artifact_hash"],
        "bridge_hash": bridge_capture.get("bridge_hash"),
        "bridge_final_status": bridge_status,
        "bridge_capture": deepcopy(bridge_capture),
        "aigol_validation_required": True,
        "aigol_authorization_required": True,
        "worker_self_authorized": False,
        "llm_executed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_governed_readonly_result(
    prompt_artifact: dict[str, Any],
    proposal_artifact: dict[str, Any],
    bridge_artifact: dict[str, Any],
) -> dict[str, Any]:
    """Create final governed operator result."""

    _verify_artifact_hash(prompt_artifact)
    _verify_artifact_hash(proposal_artifact)
    _verify_artifact_hash(bridge_artifact)
    bridge_status = bridge_artifact["bridge_final_status"]
    completed = bridge_status == RETURNED
    if bridge_status not in {RETURNED, FAILED}:
        raise FailClosedRuntimeError("bridge final status is invalid")
    result = {
        "operator_flow_id": prompt_artifact["operator_flow_id"],
        "state": GOVERNED_RESULT_RETURNED if completed else OPERATOR_FAILED,
        "final_status": OPERATOR_COMPLETED if completed else OPERATOR_FAILED,
        "target_capability": prompt_artifact["target_capability"],
        "human_prompt_hash": prompt_artifact["artifact_hash"],
        "proposal_hash": proposal_artifact["artifact_hash"],
        "bridge_artifact_hash": bridge_artifact["artifact_hash"],
        "llm_proposes_only": True,
        "aigol_governs": True,
        "worker_executes_only_after_authorization": True,
        "replay_records": True,
        "read_only": completed,
        "filesystem_mutation": False,
        "network_execution": False,
        "shell_execution": False,
        "orchestration_runtime": False,
        "agent_runtime": False,
        "new_capability_created": False,
        "governed_return": (
            "human prompt completed through governed read-only result"
            if completed
            else "human prompt failed closed before governed read-only completion"
        ),
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def reconstruct_human_prompt_governed_result_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct operator-level replay evidence for the end-to-end flow."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("human prompt governed result replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("human prompt governed result artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    final_artifact = wrappers[-1]["artifact"]
    bridge_replay = None
    if (replay_path / "bridge_replay").exists():
        bridge_replay = reconstruct_cognition_execution_bridge_replay(replay_path / "bridge_replay")
    return {
        "operator_flow_id": final_artifact["operator_flow_id"],
        "final_status": final_artifact["final_status"],
        "target_capability": final_artifact.get("target_capability", "UNAVAILABLE"),
        "lifecycle_transitions": [wrapper["artifact"]["state"] for wrapper in wrappers],
        "replay_artifact_count": len(wrappers),
        "bridge_replay": bridge_replay,
        "append_only_valid": True,
        "llm_proposes_only": True,
        "aigol_governs": True,
        "worker_executes_only_after_authorization": True,
        "replay_records": True,
        "replay_hash": replay_hash(wrappers),
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("human prompt governed result replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_sequence(replay_dir: Path, failure: dict[str, Any]) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, _failure_step(failure, step))


def _failure_artifact(*, operator_flow_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "operator_flow_id": operator_flow_id,
        "state": OPERATOR_FAILED,
        "final_status": OPERATOR_FAILED,
        "created_at": created_at,
        "failure_reason": failure_reason,
        "llm_proposes_only": True,
        "aigol_governs": True,
        "worker_executes_only_after_authorization": False,
        "replay_records": True,
        "read_only": False,
        "filesystem_mutation": False,
        "network_execution": False,
        "shell_execution": False,
        "orchestration_runtime": False,
        "agent_runtime": False,
        "new_capability_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_step(failure: dict[str, Any], step: str) -> dict[str, Any]:
    artifact = deepcopy(failure)
    artifact["failed_step"] = step
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    prompt_artifact: dict[str, Any] | None,
    proposal_artifact: dict[str, Any] | None,
    bridge_artifact: dict[str, Any] | None,
    governed_result: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "human_prompt": deepcopy(prompt_artifact),
        "cognition_proposal": deepcopy(proposal_artifact),
        "bridge_capture": deepcopy(bridge_artifact),
        "governed_result": deepcopy(governed_result),
    }
    capture["operator_flow_hash"] = replay_hash(capture)
    return capture


def _reject_unsafe_prompt(prompt: str) -> None:
    lowered = prompt.lower()
    for term in HIDDEN_CONTINUATION_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("hidden continuation attempt detected")
    for term in FORBIDDEN_PROMPT_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("unsupported read-only prompt intent")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("human prompt governed result artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("human prompt governed result artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("human prompt governed result artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("human prompt governed result replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("human prompt governed result replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "human prompt governed read-only result failed closed"


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
