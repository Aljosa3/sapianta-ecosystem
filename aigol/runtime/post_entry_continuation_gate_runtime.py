"""Replay-visible ACLI post-entry continuation gate."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_ACLI_POST_ENTRY_CONTINUATION_GATE_VERSION = "AIGOL_ACLI_POST_ENTRY_CONTINUATION_GATE_V1"
POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1 = "POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1"
POST_ENTRY_CONTINUATION_GATE_RETURNED_V1 = "POST_ENTRY_CONTINUATION_GATE_RETURNED_V1"

CONTINUATION_ALLOWED = "CONTINUATION_ALLOWED"
PROPOSAL_BOUNDARY_REACHED = "PROPOSAL_BOUNDARY_REACHED"
COGNITION_BOUNDARY_REACHED = "COGNITION_BOUNDARY_REACHED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION = "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION"
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION = "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
OPERATOR_DECISION_SUPPORT = "OPERATOR_DECISION_SUPPORT"
OCS_LLM_COGNITION = "OCS_LLM_COGNITION"
IMPROVE_PROVIDER_LAYER = "IMPROVE_PROVIDER_LAYER"

REPLAY_STEPS = (
    "post_entry_continuation_gate_recorded",
    "post_entry_continuation_gate_returned",
)


def evaluate_post_entry_continuation_gate(
    *,
    gate_id: str,
    prompt_id: str,
    human_prompt: str,
    workflow_id: str,
    lifecycle_entry_status: str,
    provider_necessity_classification: str | None,
    auto_continue_enabled: bool,
    created_at: str,
    replay_dir: str | Path,
    lifecycle_replay_reference: str | None = None,
) -> dict[str, Any]:
    """Record whether a selected lifecycle entry may continue to certified execution preparation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        decision = _decide(
            human_prompt=human_prompt,
            workflow_id=workflow_id,
            lifecycle_entry_status=lifecycle_entry_status,
            provider_necessity_classification=provider_necessity_classification,
            auto_continue_enabled=auto_continue_enabled,
        )
        artifact = _gate_artifact(
            gate_id=gate_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            workflow_id=workflow_id,
            lifecycle_entry_status=lifecycle_entry_status,
            provider_necessity_classification=provider_necessity_classification,
            auto_continue_enabled=auto_continue_enabled,
            decision=decision,
            created_at=created_at,
            replay_reference=str(replay_path),
            lifecycle_replay_reference=lifecycle_replay_reference,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _gate_artifact(
            gate_id=gate_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            workflow_id=workflow_id,
            lifecycle_entry_status=lifecycle_entry_status,
            provider_necessity_classification=provider_necessity_classification,
            auto_continue_enabled=auto_continue_enabled,
            decision={
                "gate_status": FAILED_CLOSED,
                "continuation_allowed": False,
                "execution_capable": False,
                "execution_summary_required": False,
                "human_confirmation_required": False,
                "authorization_required": False,
                "continuation_runtime": None,
                "decision_reason": _failure_reason(exc),
            },
            created_at=created_at,
            replay_reference=str(replay_path),
            lifecycle_replay_reference=lifecycle_replay_reference,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_post_entry_continuation_gate_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct ACLI post-entry continuation gate replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("post-entry continuation gate replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("post-entry continuation gate replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    artifact = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("gate_reference") != artifact["gate_id"]:
        raise FailClosedRuntimeError("post-entry continuation gate replay reference mismatch")
    if returned.get("gate_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("post-entry continuation gate replay hash mismatch")
    return {
        "gate_status": artifact["gate_status"],
        "continuation_allowed": artifact["continuation_allowed"],
        "execution_capable": artifact["execution_capable"],
        "execution_summary_required": artifact["execution_summary_required"],
        "human_confirmation_required": artifact["human_confirmation_required"],
        "authorization_required": artifact["authorization_required"],
        "continuation_runtime": artifact["continuation_runtime"],
        "workflow_id": artifact["workflow_id"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "authorization_created": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _decide(
    *,
    human_prompt: str,
    workflow_id: str,
    lifecycle_entry_status: str,
    provider_necessity_classification: str | None,
    auto_continue_enabled: bool,
) -> dict[str, Any]:
    workflow = _require_string(workflow_id, "workflow_id")
    lifecycle_status = _require_string(lifecycle_entry_status, "lifecycle_entry_status")
    if workflow == NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION:
        if lifecycle_status != "CONTEXT_ASSEMBLED":
            return _decision(
                gate_status=FAILED_CLOSED,
                continuation_allowed=False,
                execution_capable=True,
                reason="native development context is not assembled",
            )
        provider_necessity = str(provider_necessity_classification or "")
        if "PROVIDER_REQUIRED" not in provider_necessity:
            return _decision(
                gate_status=PROPOSAL_BOUNDARY_REACHED,
                continuation_allowed=False,
                execution_capable=False,
                reason="native development entry does not require provider-backed execution preparation",
            )
        if auto_continue_enabled or _explicit_ppp_continuation_requested(human_prompt):
            return _decision(
                gate_status=CONTINUATION_ALLOWED,
                continuation_allowed=True,
                execution_capable=True,
                reason="explicit continuation condition satisfied",
                continuation_runtime="context_assembled_to_ppp_routing_continuation",
            )
        return _decision(
            gate_status=CLARIFICATION_REQUIRED,
            continuation_allowed=False,
            execution_capable=True,
            reason="execution-capable lifecycle entry requires explicit continuation approval",
            continuation_runtime="context_assembled_to_ppp_routing_continuation",
        )
    if workflow in {CREATE_DOMAIN_COMPLIANCE_CLARIFICATION, IMPROVE_PROVIDER_LAYER}:
        return _decision(
            gate_status=PROPOSAL_BOUNDARY_REACHED,
            continuation_allowed=False,
            execution_capable=False,
            reason="proposal-only lifecycle entry stops for human review",
        )
    if workflow in {OPERATOR_DECISION_SUPPORT, OCS_LLM_COGNITION}:
        return _decision(
            gate_status=COGNITION_BOUNDARY_REACHED,
            continuation_allowed=False,
            execution_capable=False,
            reason="cognition-only lifecycle entry does not create an execution request",
        )
    return _decision(
        gate_status=FAILED_CLOSED,
        continuation_allowed=False,
        execution_capable=False,
        reason="no certified post-entry continuation mapping exists",
    )


def _decision(
    *,
    gate_status: str,
    continuation_allowed: bool,
    execution_capable: bool,
    reason: str,
    continuation_runtime: str | None = None,
) -> dict[str, Any]:
    requires_execution_boundary = continuation_allowed and execution_capable
    return {
        "gate_status": gate_status,
        "continuation_allowed": continuation_allowed,
        "execution_capable": execution_capable,
        "execution_summary_required": requires_execution_boundary,
        "human_confirmation_required": requires_execution_boundary,
        "authorization_required": requires_execution_boundary,
        "continuation_runtime": continuation_runtime,
        "decision_reason": _require_string(reason, "decision_reason"),
    }


def _gate_artifact(
    *,
    gate_id: str,
    prompt_id: str,
    human_prompt: str,
    workflow_id: str,
    lifecycle_entry_status: str,
    provider_necessity_classification: str | None,
    auto_continue_enabled: bool,
    decision: dict[str, Any],
    created_at: str,
    replay_reference: str,
    lifecycle_replay_reference: str | None,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1,
        "runtime_version": AIGOL_ACLI_POST_ENTRY_CONTINUATION_GATE_VERSION,
        "gate_id": _require_string(gate_id, "gate_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "workflow_id": _require_string(workflow_id, "workflow_id"),
        "lifecycle_entry_status": _require_string(lifecycle_entry_status, "lifecycle_entry_status"),
        "provider_necessity_classification": provider_necessity_classification,
        "auto_continue_enabled": bool(auto_continue_enabled),
        "explicit_ppp_continuation_requested": _explicit_ppp_continuation_requested(human_prompt),
        "gate_status": _require_string(decision.get("gate_status"), "gate_status"),
        "continuation_allowed": decision.get("continuation_allowed") is True,
        "execution_capable": decision.get("execution_capable") is True,
        "execution_summary_required": decision.get("execution_summary_required") is True,
        "human_confirmation_required": decision.get("human_confirmation_required") is True,
        "authorization_required": decision.get("authorization_required") is True,
        "continuation_runtime": decision.get("continuation_runtime"),
        "decision_reason": _require_string(decision.get("decision_reason"), "decision_reason"),
        "lifecycle_replay_reference": lifecycle_replay_reference,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "provider_authority": False,
        "worker_invoked": False,
        "execution_requested": False,
        "authorization_created": False,
        "approval_bypassed": False,
        "governance_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason
        or (
            _require_string(decision.get("decision_reason"), "decision_reason")
            if decision.get("gate_status") == FAILED_CLOSED
            else None
        ),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _verify_artifact_hash(artifact)
    return artifact


def _returned_artifact(gate: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(gate)
    returned = {
        "artifact_type": POST_ENTRY_CONTINUATION_GATE_RETURNED_V1,
        "runtime_version": AIGOL_ACLI_POST_ENTRY_CONTINUATION_GATE_VERSION,
        "gate_reference": gate["gate_id"],
        "gate_hash": gate["artifact_hash"],
        "gate_status": gate["gate_status"],
        "continuation_allowed": gate["continuation_allowed"],
        "execution_summary_required": gate["execution_summary_required"],
        "human_confirmation_required": gate["human_confirmation_required"],
        "authorization_required": gate["authorization_required"],
        "continuation_runtime": gate["continuation_runtime"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "authorization_created": False,
        "replay_visible": True,
        "failure_reason": gate["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(gate: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "post_entry_continuation_gate_artifact": deepcopy(gate),
        "post_entry_continuation_gate_returned": deepcopy(returned),
        "post_entry_continuation_gate_replay_reference": str(replay_path),
        "gate_status": gate["gate_status"],
        "continuation_allowed": gate["continuation_allowed"],
        "execution_capable": gate["execution_capable"],
        "execution_summary_required": gate["execution_summary_required"],
        "human_confirmation_required": gate["human_confirmation_required"],
        "authorization_required": gate["authorization_required"],
        "continuation_runtime": gate["continuation_runtime"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "authorization_created": False,
        "fail_closed": gate["gate_status"] == FAILED_CLOSED,
        "failure_reason": gate["failure_reason"],
    }
    capture["post_entry_continuation_gate_capture_hash"] = replay_hash(capture)
    return capture


def _explicit_ppp_continuation_requested(human_prompt: str) -> bool:
    normalized = " ".join(_require_string(human_prompt, "human_prompt").lower().split())
    return "continue" in normalized and "ppp" in normalized


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("post-entry continuation gate replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("post-entry continuation gate hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("post-entry continuation gate hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("post-entry continuation gate wrapper hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("post-entry continuation gate wrapper hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "post-entry continuation gate failed closed"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
