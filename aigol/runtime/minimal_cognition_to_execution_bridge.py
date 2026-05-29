"""Minimal bounded cognition-to-execution bridge."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.filesystem_read_only_capability import (
    FILESYSTEM_READ_ONLY_INSPECTION,
    execute_filesystem_read_only_capability,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.read_only_capability_attachment import (
    READ_ONLY_RUNTIME_INSPECTION,
    execute_read_only_capability,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


NORMALIZED = "NORMALIZED"
VALIDATED = "VALIDATED"
AUTHORIZED = "AUTHORIZED"
EXECUTED = "EXECUTED"
FAILED = "FAILED"
RETURNED = "RETURNED"

SUPPORTED_CAPABILITIES = frozenset({READ_ONLY_RUNTIME_INSPECTION, FILESYSTEM_READ_ONLY_INSPECTION})
REPLAY_STEPS = ("contribution", "normalized_request", "validation", "authorization", "execution", "return")
REQUIRED_FIELDS = frozenset(
    {
        "contribution_id",
        "human_prompt",
        "target_capability",
        "intent",
        "created_at",
        "arguments",
    }
)
HIDDEN_CONTINUATION_TERMS = (
    "continue autonomously",
    "hidden continuation",
    "auto retry",
    "recursive",
    "agent",
    "orchestrate",
)
FORBIDDEN_INTENT_TERMS = (
    "write",
    "delete",
    "move",
    "modify",
    "shell",
    "network",
    "api",
    "mutate",
)


def execute_cognition_to_execution_bridge(
    *,
    bridge_id: str,
    execution_id: str,
    request_id: str,
    cognition_output: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    authorize: bool = True,
) -> dict[str, Any]:
    """Translate one untrusted cognition output into a bounded read-only execution."""

    replay_path = Path(replay_dir)
    contribution = create_cognition_contribution_artifact(
        bridge_id=bridge_id,
        execution_id=execution_id,
        request_id=request_id,
        cognition_output=cognition_output,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, "contribution", contribution)
    try:
        normalized = normalize_cognition_execution_request(contribution)
        _persist_step(replay_path, 1, "normalized_request", normalized)
        validation = validate_cognition_execution_request(normalized)
        _persist_step(replay_path, 2, "validation", validation)
        authorization = authorize_cognition_execution_request(validation, authorized=authorize)
        _persist_step(replay_path, 3, "authorization", authorization)
        execution = execute_authorized_cognition_request(authorization, normalized_request=normalized)
        _persist_step(replay_path, 4, "execution", execution)
        governed_return = create_governed_cognition_execution_return(execution)
        _persist_step(replay_path, 5, "return", governed_return)
        return _capture(contribution, normalized, validation, authorization, execution, governed_return)
    except Exception as exc:
        failure = _failure_artifact(contribution=contribution, failure_reason=_failure_reason(exc))
        _persist_failure_sequence(replay_path, failure)
        return _capture(contribution, None, None, None, None, failure)


def create_cognition_contribution_artifact(
    *,
    bridge_id: str,
    execution_id: str,
    request_id: str,
    cognition_output: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Capture untrusted cognition output as replay-visible bridge input."""

    if not isinstance(cognition_output, dict):
        raise FailClosedRuntimeError("cognition output must be a JSON object")
    artifact = {
        "bridge_id": _require_string(bridge_id, "bridge_id"),
        "execution_id": _require_string(execution_id, "execution_id"),
        "request_id": _require_string(request_id, "request_id"),
        "created_at": _require_string(created_at, "created_at"),
        "state": "CONTRIBUTION",
        "untrusted_execution_request_input": True,
        "cognition_output": deepcopy(cognition_output),
        "cognition_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "hidden_continuation": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def normalize_cognition_execution_request(contribution: dict[str, Any]) -> dict[str, Any]:
    """Normalize untrusted cognition output into a deterministic execution request."""

    _verify_artifact_hash(contribution)
    output = contribution.get("cognition_output")
    if not isinstance(output, dict):
        raise FailClosedRuntimeError("malformed cognition output")
    if set(output) != REQUIRED_FIELDS:
        raise FailClosedRuntimeError("malformed cognition output")
    target_capability = _normalize_token(output["target_capability"], "target_capability")
    intent = _normalize_text(output["intent"], "intent")
    human_prompt = _normalize_text(output["human_prompt"], "human_prompt")
    arguments = output["arguments"]
    if not isinstance(arguments, dict):
        raise FailClosedRuntimeError("malformed cognition output")
    _reject_hidden_continuation(" ".join([intent, human_prompt]))
    _reject_forbidden_intent(intent)
    normalized_arguments = _normalize_arguments(target_capability, arguments)
    normalized = {
        "bridge_id": contribution["bridge_id"],
        "execution_id": contribution["execution_id"],
        "request_id": contribution["request_id"],
        "contribution_id": _require_string(output["contribution_id"], "contribution_id"),
        "state": NORMALIZED,
        "target_capability": target_capability,
        "intent": intent,
        "human_prompt": human_prompt,
        "arguments": normalized_arguments,
        "created_at": _require_string(output["created_at"], "created_at"),
        "contribution_hash": contribution["artifact_hash"],
        "untrusted_input_normalized": True,
        "read_only_requested": True,
        "execution_authority": False,
        "authorization_authority": False,
        "hidden_continuation": False,
    }
    normalized["artifact_hash"] = replay_hash(normalized)
    return normalized


def validate_cognition_execution_request(normalized: dict[str, Any]) -> dict[str, Any]:
    """Validate target capability, arguments, and bridge boundary."""

    _verify_artifact_hash(normalized)
    if normalized.get("state") != NORMALIZED:
        raise FailClosedRuntimeError("normalized cognition execution request is required")
    target = normalized.get("target_capability")
    if target not in SUPPORTED_CAPABILITIES:
        raise FailClosedRuntimeError("unsupported capability")
    if normalized.get("execution_authority") is not False or normalized.get("authorization_authority") is not False:
        raise FailClosedRuntimeError("cognition output authority escalation detected")
    if normalized.get("hidden_continuation") is not False:
        raise FailClosedRuntimeError("hidden continuation attempt detected")
    validation = {
        "bridge_id": normalized["bridge_id"],
        "execution_id": normalized["execution_id"],
        "request_id": normalized["request_id"],
        "state": VALIDATED,
        "target_capability": target,
        "normalized_request_hash": normalized["artifact_hash"],
        "replay_centrality_preserved": True,
        "authority_separation_preserved": True,
        "boundedness_preserved": True,
        "execution_boundary_enforcement_preserved": True,
        "constitutional_freeze_compatible": True,
        "authorization_required": True,
    }
    validation["artifact_hash"] = replay_hash(validation)
    return validation


def authorize_cognition_execution_request(validation: dict[str, Any], *, authorized: bool = True) -> dict[str, Any]:
    """Create bridge authorization evidence; cognition cannot self-authorize."""

    _verify_artifact_hash(validation)
    if validation.get("state") != VALIDATED:
        raise FailClosedRuntimeError("cognition execution authorization requires VALIDATED state")
    if authorized is not True:
        raise FailClosedRuntimeError("cognition execution request unauthorized")
    authorization = {
        "bridge_id": validation["bridge_id"],
        "execution_id": validation["execution_id"],
        "request_id": validation["request_id"],
        "state": AUTHORIZED,
        "target_capability": validation["target_capability"],
        "validation_hash": validation["artifact_hash"],
        "authorization_scope": "READ_ONLY_EXECUTION_BRIDGE",
        "cognition_self_authorized": False,
        "filesystem_write_authority": False,
        "network_authority": False,
        "shell_authority": False,
        "api_authority": False,
        "orchestration_authority": False,
    }
    authorization["artifact_hash"] = replay_hash(authorization)
    return authorization


def execute_authorized_cognition_request(authorization: dict[str, Any], *, normalized_request: dict[str, Any]) -> dict[str, Any]:
    """Execute only supported read-only capability target."""

    _verify_artifact_hash(authorization)
    if authorization.get("state") != AUTHORIZED:
        raise FailClosedRuntimeError("authorized cognition execution request is required")
    if authorization.get("cognition_self_authorized") is not False:
        raise FailClosedRuntimeError("cognition output cannot self-authorize")
    _verify_artifact_hash(normalized_request)
    if normalized_request.get("state") != NORMALIZED:
        raise FailClosedRuntimeError("normalized cognition execution request is required")
    if normalized_request.get("execution_id") != authorization.get("execution_id"):
        raise FailClosedRuntimeError("bridge execution lineage mismatch")
    if normalized_request.get("request_id") != authorization.get("request_id"):
        raise FailClosedRuntimeError("bridge request lineage mismatch")
    if normalized_request.get("target_capability") != authorization.get("target_capability"):
        raise FailClosedRuntimeError("bridge capability lineage mismatch")
    target = authorization["target_capability"]
    capability_replay_dir = Path(normalized_request["arguments"]["capability_replay_dir"])
    if target == READ_ONLY_RUNTIME_INSPECTION:
        capability_result = execute_read_only_capability(
            execution_id=authorization["execution_id"],
            request_id=authorization["request_id"],
            created_at=normalized_request["created_at"],
            replay_dir=capability_replay_dir,
            lineage_parent=authorization["artifact_hash"],
        )
    elif target == FILESYSTEM_READ_ONLY_INSPECTION:
        capability_result = execute_filesystem_read_only_capability(
            execution_id=authorization["execution_id"],
            request_id=authorization["request_id"],
            created_at=normalized_request["created_at"],
            replay_dir=capability_replay_dir,
            root_path=normalized_request["arguments"]["root_path"],
            requested_path=normalized_request["arguments"]["requested_path"],
            allowed_paths=normalized_request["arguments"]["allowed_paths"],
            lineage_parent=authorization["artifact_hash"],
        )
    else:
        raise FailClosedRuntimeError("unsupported capability")
    capability_status = capability_result["termination"]["final_status"]
    if capability_status != "TERMINATED":
        raise FailClosedRuntimeError("capability execution failed closed")
    execution = {
        "bridge_id": authorization["bridge_id"],
        "execution_id": authorization["execution_id"],
        "request_id": authorization["request_id"],
        "state": EXECUTED,
        "target_capability": target,
        "authorization_hash": authorization["artifact_hash"],
        "capability_result": deepcopy(capability_result),
        "capability_result_hash": replay_hash(capability_result),
        "replay_visible_result": True,
        "read_only": True,
        "filesystem_mutation": False,
        "network_invocation": False,
        "shell_invocation": False,
        "api_invocation": False,
        "hidden_continuation": False,
    }
    execution["artifact_hash"] = replay_hash(execution)
    return execution


def create_governed_cognition_execution_return(execution: dict[str, Any]) -> dict[str, Any]:
    """Create governed return artifact for bridge result."""

    _verify_artifact_hash(execution)
    if execution.get("state") != EXECUTED:
        raise FailClosedRuntimeError("executed bridge result is required")
    governed_return = {
        "bridge_id": execution["bridge_id"],
        "execution_id": execution["execution_id"],
        "request_id": execution["request_id"],
        "state": RETURNED,
        "target_capability": execution["target_capability"],
        "execution_hash": execution["artifact_hash"],
        "final_status": RETURNED,
        "replay_visible": True,
        "bounded": True,
        "authorized": True,
        "read_only": True,
        "cognition_authority": False,
        "hidden_continuation": False,
    }
    governed_return["artifact_hash"] = replay_hash(governed_return)
    return governed_return


def reconstruct_cognition_execution_bridge_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate bridge replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("cognition execution bridge replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("cognition execution bridge artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    states = [wrapper["artifact"]["state"] for wrapper in wrappers]
    _validate_reconstructed_states(states)
    final_artifact = wrappers[-1]["artifact"]
    return {
        "bridge_id": final_artifact["bridge_id"],
        "execution_id": final_artifact["execution_id"],
        "target_capability": final_artifact["target_capability"],
        "final_status": final_artifact["final_status"],
        "lifecycle_transitions": states,
        "replay_artifact_count": len(wrappers),
        "append_only_valid": True,
        "replay_visible": True,
        "authorized": final_artifact.get("authorized") is True,
        "read_only": final_artifact.get("read_only") is True,
        "replay_hash": replay_hash(wrappers),
    }


def _normalize_arguments(target_capability: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if "capability_replay_dir" not in arguments:
        raise FailClosedRuntimeError("capability replay directory is required")
    normalized = {"capability_replay_dir": _require_string(arguments["capability_replay_dir"], "capability_replay_dir")}
    if target_capability == READ_ONLY_RUNTIME_INSPECTION:
        if set(arguments) != {"capability_replay_dir"}:
            raise FailClosedRuntimeError("ambiguous intent")
        return normalized
    if target_capability == FILESYSTEM_READ_ONLY_INSPECTION:
        required = {"capability_replay_dir", "root_path", "requested_path", "allowed_paths"}
        if set(arguments) != required:
            raise FailClosedRuntimeError("malformed cognition output")
        allowed_paths = arguments["allowed_paths"]
        if not isinstance(allowed_paths, list) or not allowed_paths:
            raise FailClosedRuntimeError("malformed cognition output")
        normalized.update(
            {
                "root_path": _require_string(arguments["root_path"], "root_path"),
                "requested_path": _require_string(arguments["requested_path"], "requested_path"),
                "allowed_paths": [_require_string(path, "allowed_path") for path in allowed_paths],
            }
        )
        return normalized
    raise FailClosedRuntimeError("unsupported capability")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("cognition execution bridge replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_sequence(replay_dir: Path, failure: dict[str, Any]) -> None:
    for index, step in enumerate(REPLAY_STEPS[1:], start=1):
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, _failure_step(failure, step))


def _failure_artifact(*, contribution: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    target = "UNAVAILABLE"
    output = contribution.get("cognition_output")
    if isinstance(output, dict) and "target_capability" in output:
        try:
            target = _normalize_token(output["target_capability"], "target_capability")
        except FailClosedRuntimeError:
            target = "UNAVAILABLE"
    artifact = {
        "bridge_id": contribution["bridge_id"],
        "execution_id": contribution["execution_id"],
        "request_id": contribution["request_id"],
        "state": FAILED,
        "target_capability": target,
        "contribution_hash": contribution["artifact_hash"],
        "final_status": FAILED,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "bounded": True,
        "authorized": False,
        "read_only": False,
        "hidden_continuation": False,
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
    contribution: dict[str, Any],
    normalized: dict[str, Any] | None,
    validation: dict[str, Any] | None,
    authorization: dict[str, Any] | None,
    execution: dict[str, Any] | None,
    governed_return: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "contribution": deepcopy(contribution),
        "normalized_request": deepcopy(normalized),
        "validation": deepcopy(validation),
        "authorization": deepcopy(authorization),
        "execution": deepcopy(execution),
        "return": deepcopy(governed_return),
    }
    capture["bridge_hash"] = replay_hash(capture)
    return capture


def _validate_reconstructed_states(states: list[str]) -> None:
    if states == ["CONTRIBUTION", NORMALIZED, VALIDATED, AUTHORIZED, EXECUTED, RETURNED]:
        return
    if states[-1] == FAILED:
        try:
            first_failed_index = states.index(FAILED)
        except ValueError as exc:
            raise FailClosedRuntimeError("cognition execution bridge final status is invalid") from exc
        success_prefix = ["CONTRIBUTION", NORMALIZED, VALIDATED, AUTHORIZED, EXECUTED]
        if states[:first_failed_index] == success_prefix[:first_failed_index] and all(
            state == FAILED for state in states[first_failed_index:]
        ):
            return
    raise FailClosedRuntimeError("cognition execution bridge lifecycle ordering mismatch")


def _reject_hidden_continuation(text: str) -> None:
    lowered = text.lower()
    for term in HIDDEN_CONTINUATION_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("hidden continuation attempt detected")


def _reject_forbidden_intent(intent: str) -> None:
    lowered = intent.lower()
    for term in FORBIDDEN_INTENT_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("unsupported capability intent")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("cognition execution bridge artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("cognition execution bridge artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("cognition execution bridge artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("cognition execution bridge replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("cognition execution bridge replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "cognition execution bridge failed closed"


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
