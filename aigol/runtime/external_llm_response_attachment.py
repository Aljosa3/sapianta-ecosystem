"""External LLM response attachment for proposal-only ingestion."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.minimal_cognition_to_execution_bridge import (
    READ_ONLY_RUNTIME_INSPECTION,
    execute_cognition_to_execution_bridge,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


RAW_CAPTURED = "RAW_CAPTURED"
PROPOSAL_NORMALIZED = "PROPOSAL_NORMALIZED"
PROPOSAL_VALIDATED = "PROPOSAL_VALIDATED"
GOVERNED_RESULT_RETURNED = "GOVERNED_RESULT_RETURNED"
ATTACHMENT_FAILED = "FAILED"

REPLAY_STEPS = ("raw_external_response", "normalized_proposal", "proposal_validation", "governed_result")
SUPPORTED_ATTACHMENT_CAPABILITIES = frozenset({READ_ONLY_RUNTIME_INSPECTION})
MAX_EXTERNAL_RESPONSE_CHARS = 4096
HIDDEN_CONTINUATION_TERMS = (
    "continue autonomously",
    "hidden continuation",
    "auto retry",
    "recursive",
    "agent",
    "orchestrate",
)
FORBIDDEN_RESPONSE_TERMS = (
    "write",
    "delete",
    "move",
    "modify",
    "shell",
    "network",
    "api",
    "mutate",
    "authorize",
    "execute directly",
)


def attach_external_llm_response(
    *,
    attachment_id: str,
    provider_identity: str,
    external_response: Any,
    created_at: str,
    replay_dir: str | Path,
    target_capability: str = READ_ONLY_RUNTIME_INSPECTION,
    authorize: bool = True,
) -> dict[str, Any]:
    """Attach one externally supplied LLM response as untrusted proposal input."""

    replay_path = Path(replay_dir)
    try:
        raw = capture_raw_external_response(
            attachment_id=attachment_id,
            provider_identity=provider_identity,
            external_response=external_response,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, "raw_external_response", raw)
        proposal = normalize_external_response_to_proposal(
            raw,
            replay_dir=replay_path,
            target_capability=target_capability,
        )
        _persist_step(replay_path, 1, "normalized_proposal", proposal)
        validation = validate_external_llm_proposal(proposal)
        _persist_step(replay_path, 2, "proposal_validation", validation)
        bridge_capture = execute_cognition_to_execution_bridge(
            bridge_id=f"{attachment_id}:BRIDGE",
            execution_id=f"{attachment_id}:EXECUTION",
            request_id=f"{attachment_id}:REQUEST",
            cognition_output=proposal["proposal_artifact"],
            created_at=raw["created_at"],
            replay_dir=replay_path / "bridge_replay",
            authorize=authorize,
        )
        governed_result = create_external_llm_governed_result(raw, proposal, validation, bridge_capture)
        _persist_step(replay_path, 3, "governed_result", governed_result)
        return _capture(raw, proposal, validation, governed_result)
    except Exception as exc:
        failure = _failure_artifact(
            attachment_id=attachment_id if isinstance(attachment_id, str) and attachment_id.strip() else "ATTACHMENT-INVALID",
            provider_identity=provider_identity if isinstance(provider_identity, str) and provider_identity.strip() else "PROVIDER-INVALID",
            created_at=created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00+00:00",
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_sequence(replay_path, failure)
        return _capture(None, None, None, failure)


def capture_raw_external_response(
    *,
    attachment_id: str,
    provider_identity: str,
    external_response: Any,
    created_at: str,
) -> dict[str, Any]:
    """Capture raw external LLM response before normalization."""

    response_text = _normalize_response_text(external_response)
    provider = _normalize_provider_identity(provider_identity)
    artifact = {
        "attachment_id": _require_string(attachment_id, "attachment_id"),
        "state": RAW_CAPTURED,
        "provider_identity": provider,
        "created_at": _require_string(created_at, "created_at"),
        "raw_response_text": response_text,
        "raw_response_hash": replay_hash(response_text),
        "untrusted_input": True,
        "llm_proposes_only": True,
        "llm_execution_authority": False,
        "llm_authorization_authority": False,
        "llm_governance_authority": False,
        "replay_bypass_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def normalize_external_response_to_proposal(
    raw_artifact: dict[str, Any],
    *,
    replay_dir: str | Path,
    target_capability: str = READ_ONLY_RUNTIME_INSPECTION,
) -> dict[str, Any]:
    """Normalize raw external text into the existing bridge proposal shape."""

    _verify_artifact_hash(raw_artifact)
    if raw_artifact.get("state") != RAW_CAPTURED:
        raise FailClosedRuntimeError("raw external response is required")
    response_text = _normalize_response_text(raw_artifact.get("raw_response_text"))
    _reject_unsafe_response(response_text)
    capability = _normalize_token(target_capability, "target_capability")
    if capability not in SUPPORTED_ATTACHMENT_CAPABILITIES:
        raise FailClosedRuntimeError("unsupported attachment capability")
    proposal = {
        "contribution_id": f"{raw_artifact['attachment_id']}:EXTERNAL-LLM-PROPOSAL",
        "human_prompt": response_text,
        "target_capability": capability,
        "intent": "inspect runtime metadata",
        "created_at": raw_artifact["created_at"],
        "arguments": {
            "capability_replay_dir": str(Path(replay_dir) / "capability_replay"),
        },
    }
    artifact = {
        "attachment_id": raw_artifact["attachment_id"],
        "state": PROPOSAL_NORMALIZED,
        "provider_identity": raw_artifact["provider_identity"],
        "raw_external_response_hash": raw_artifact["artifact_hash"],
        "proposal_artifact": proposal,
        "proposal_artifact_hash": replay_hash(proposal),
        "untrusted_proposal_input": True,
        "llm_execution_authority": False,
        "llm_authorization_authority": False,
        "llm_governance_authority": False,
        "worker_instruction_authority": False,
        "new_capability_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_external_llm_proposal(proposal_artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate normalized external LLM proposal before bridge handoff."""

    _verify_artifact_hash(proposal_artifact)
    if proposal_artifact.get("state") != PROPOSAL_NORMALIZED:
        raise FailClosedRuntimeError("normalized proposal artifact is required")
    proposal = proposal_artifact.get("proposal_artifact")
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError("invalid proposal structure")
    required_fields = {"contribution_id", "human_prompt", "target_capability", "intent", "created_at", "arguments"}
    if set(proposal) != required_fields:
        raise FailClosedRuntimeError("invalid proposal structure")
    if proposal.get("target_capability") not in SUPPORTED_ATTACHMENT_CAPABILITIES:
        raise FailClosedRuntimeError("unsupported attachment capability")
    if proposal_artifact.get("llm_execution_authority") is not False:
        raise FailClosedRuntimeError("external llm execution authority detected")
    if proposal_artifact.get("llm_authorization_authority") is not False:
        raise FailClosedRuntimeError("external llm authorization authority detected")
    if proposal_artifact.get("llm_governance_authority") is not False:
        raise FailClosedRuntimeError("external llm governance authority detected")
    validation = {
        "attachment_id": proposal_artifact["attachment_id"],
        "state": PROPOSAL_VALIDATED,
        "provider_identity": proposal_artifact["provider_identity"],
        "normalized_proposal_hash": proposal_artifact["artifact_hash"],
        "proposal_artifact_hash": proposal_artifact["proposal_artifact_hash"],
        "proposal_only_preserved": True,
        "aigol_governance_required": True,
        "authorization_required": True,
        "worker_execution_only_after_authorization": True,
        "replay_visible": True,
    }
    validation["artifact_hash"] = replay_hash(validation)
    return validation


def create_external_llm_governed_result(
    raw_artifact: dict[str, Any],
    proposal_artifact: dict[str, Any],
    validation_artifact: dict[str, Any],
    bridge_capture: dict[str, Any],
) -> dict[str, Any]:
    """Create governed result for external LLM attachment path."""

    _verify_artifact_hash(raw_artifact)
    _verify_artifact_hash(proposal_artifact)
    _verify_artifact_hash(validation_artifact)
    if not isinstance(bridge_capture, dict) or "return" not in bridge_capture:
        raise FailClosedRuntimeError("bridge capture is malformed")
    bridge_return = bridge_capture["return"]
    if not isinstance(bridge_return, dict):
        raise FailClosedRuntimeError("bridge governed return is malformed")
    completed = bridge_return.get("final_status") == "RETURNED"
    result = {
        "attachment_id": raw_artifact["attachment_id"],
        "state": GOVERNED_RESULT_RETURNED if completed else ATTACHMENT_FAILED,
        "final_status": "COMPLETED" if completed else ATTACHMENT_FAILED,
        "provider_identity": raw_artifact["provider_identity"],
        "raw_external_response_hash": raw_artifact["artifact_hash"],
        "normalized_proposal_hash": proposal_artifact["artifact_hash"],
        "proposal_validation_hash": validation_artifact["artifact_hash"],
        "bridge_hash": bridge_capture.get("bridge_hash"),
        "bridge_final_status": bridge_return.get("final_status"),
        "bridge_capture": deepcopy(bridge_capture),
        "llm_proposes_only": True,
        "aigol_governs": True,
        "worker_executes_only_after_authorization": completed,
        "replay_records": True,
        "external_response_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "governance_authority": False,
        "new_capability_created": False,
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def reconstruct_external_llm_response_attachment_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate external LLM attachment replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("external llm attachment replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("external llm attachment artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    final_artifact = wrappers[-1]["artifact"]
    return {
        "attachment_id": final_artifact["attachment_id"],
        "provider_identity": final_artifact["provider_identity"],
        "final_status": final_artifact["final_status"],
        "lifecycle_transitions": [wrapper["artifact"]["state"] for wrapper in wrappers],
        "replay_artifact_count": len(wrappers),
        "append_only_valid": True,
        "replay_visible": True,
        "llm_proposes_only": True,
        "aigol_governs": True,
        "worker_executes_only_after_authorization": final_artifact.get("worker_executes_only_after_authorization") is True,
        "replay_records": True,
        "replay_hash": replay_hash(wrappers),
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("external llm attachment replay step ordering mismatch")
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


def _failure_artifact(*, attachment_id: str, provider_identity: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "attachment_id": attachment_id,
        "state": ATTACHMENT_FAILED,
        "final_status": ATTACHMENT_FAILED,
        "provider_identity": provider_identity,
        "created_at": created_at,
        "failure_reason": failure_reason,
        "llm_proposes_only": True,
        "aigol_governs": True,
        "worker_executes_only_after_authorization": False,
        "replay_records": True,
        "external_response_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "governance_authority": False,
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
    raw_artifact: dict[str, Any] | None,
    proposal_artifact: dict[str, Any] | None,
    validation_artifact: dict[str, Any] | None,
    governed_result: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "raw_external_response": deepcopy(raw_artifact),
        "normalized_proposal": deepcopy(proposal_artifact),
        "proposal_validation": deepcopy(validation_artifact),
        "governed_result": deepcopy(governed_result),
    }
    capture["attachment_hash"] = replay_hash(capture)
    return capture


def _reject_unsafe_response(response_text: str) -> None:
    lowered = response_text.lower()
    for term in HIDDEN_CONTINUATION_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("hidden continuation attempt detected")
    for term in FORBIDDEN_RESPONSE_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("unsupported external response intent")


def _normalize_response_text(value: Any) -> str:
    raw = _require_string(value, "external_response")
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError("external_response is required")
    if len(normalized) > MAX_EXTERNAL_RESPONSE_CHARS:
        raise FailClosedRuntimeError("external_response exceeds bounded size")
    return normalized


def _normalize_provider_identity(value: Any) -> str:
    identity = _require_string(value, "provider_identity").strip()
    if any(char.isspace() for char in identity):
        raise FailClosedRuntimeError("provider_identity must be deterministic")
    return identity


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("external llm attachment artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("external llm attachment artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("external llm attachment artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("external llm attachment replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("external llm attachment replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "external llm response attachment failed closed"
