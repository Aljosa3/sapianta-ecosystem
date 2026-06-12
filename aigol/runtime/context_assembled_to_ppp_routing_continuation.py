"""Replay-visible continuation from native context assembly to PPP routing."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import ProviderRegistry
from aigol.runtime.conversation_ppp_routing_integration import (
    FAILED_CLOSED,
    run_conversation_ppp_routing_integration,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CONTEXT_ASSEMBLED_TO_PPP_ROUTING_CONTINUATION_VERSION = (
    "AIGOL_CONTEXT_ASSEMBLED_TO_PPP_ROUTING_CONTINUATION_V1"
)
POST_CONTEXT_CONTINUATION_ARTIFACT_V1 = "POST_CONTEXT_CONTINUATION_ARTIFACT_V1"
POST_CONTEXT_CONTINUATION_RETURNED_V1 = "POST_CONTEXT_CONTINUATION_RETURNED_V1"
POST_CONTEXT_CONTINUATION_REACHED_PPP = "POST_CONTEXT_CONTINUATION_REACHED_PPP"

REPLAY_STEPS = (
    "post_context_continuation_recorded",
    "post_context_continuation_returned",
)


def continue_context_assembled_to_ppp_routing(
    *,
    continuation_id: str,
    prompt_id: str,
    human_prompt: str,
    provider_id: str,
    created_at: str,
    replay_dir: str | Path,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    governance_root: str | Path = "governance",
    session_id: str | None = None,
    turn_id: str | None = None,
    current_chain_id: str | None = None,
    latest_chain_id: str | None = None,
) -> dict[str, Any]:
    """Continue a context-assembled native prompt through existing PPP routing."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        ppp_capture = run_conversation_ppp_routing_integration(
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            provider_id=provider_id,
            created_at=created_at,
            replay_dir=replay_path / "conversation_ppp_routing",
            registry=registry,
            adapter=adapter,
            governance_root=governance_root,
            session_id=session_id,
            turn_id=turn_id,
            current_chain_id=current_chain_id,
            latest_chain_id=latest_chain_id,
        )
        if ppp_capture.get("fail_closed") is True:
            raise FailClosedRuntimeError(
                ppp_capture.get("failure_reason") or "post-context continuation failed closed: PPP routing failed"
            )
        artifact = _continuation_artifact(
            continuation_id=continuation_id,
            prompt_id=prompt_id,
            ppp_capture=ppp_capture,
            created_at=created_at,
            replay_reference=str(replay_path),
            continuation_status=POST_CONTEXT_CONTINUATION_REACHED_PPP,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, ppp_capture, replay_path)
    except Exception as exc:
        ppp_capture = locals().get("ppp_capture")
        artifact = _continuation_artifact(
            continuation_id=continuation_id,
            prompt_id=prompt_id,
            ppp_capture=ppp_capture if isinstance(ppp_capture, dict) else None,
            created_at=created_at,
            replay_reference=str(replay_path),
            continuation_status=FAILED_CLOSED,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, ppp_capture if isinstance(ppp_capture, dict) else None, replay_path)


def reconstruct_context_assembled_to_ppp_routing_continuation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct post-context continuation replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("post-context continuation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("post-context continuation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "post-context continuation")
        wrappers.append(wrapper)
    artifact = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("continuation_reference") != artifact["continuation_id"]:
        raise FailClosedRuntimeError("post-context continuation replay reference mismatch")
    if returned.get("continuation_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("post-context continuation replay hash mismatch")
    return {
        "continuation_id": artifact["continuation_id"],
        "continuation_status": artifact["continuation_status"],
        "ppp_route_status": artifact["ppp_route_status"],
        "context_hash": artifact["context_hash"],
        "domain_reference": artifact["domain_reference"],
        "worker_reference": artifact["worker_reference"],
        "provider_invoked": artifact["provider_invoked"],
        "worker_invoked": artifact["worker_invoked"],
        "execution_requested": artifact["execution_requested"],
        "dispatch_requested": artifact["dispatch_requested"],
        "failure_reason": artifact["failure_reason"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _continuation_artifact(
    *,
    continuation_id: str,
    prompt_id: str,
    ppp_capture: dict[str, Any] | None,
    created_at: str,
    replay_reference: str,
    continuation_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    route = ppp_capture.get("conversation_ppp_routing_artifact") if isinstance(ppp_capture, dict) else None
    if not isinstance(route, dict):
        route = {}
    artifact = {
        "artifact_type": POST_CONTEXT_CONTINUATION_ARTIFACT_V1,
        "runtime_version": AIGOL_CONTEXT_ASSEMBLED_TO_PPP_ROUTING_CONTINUATION_VERSION,
        "continuation_id": _require_string(continuation_id, "continuation_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "continuation_status": continuation_status,
        "ppp_route_reference": route.get("route_id"),
        "ppp_route_hash": route.get("artifact_hash"),
        "ppp_route_status": route.get("route_status"),
        "canonical_chain_id": route.get("canonical_chain_id"),
        "task_intake_reference": route.get("task_intake_reference"),
        "context_reference": route.get("context_reference"),
        "context_hash": route.get("context_hash"),
        "domain_reference": route.get("domain_reference"),
        "worker_reference": route.get("worker_reference"),
        "milestone_reference": route.get("milestone_reference"),
        "implementation_handoff_reference": route.get("implementation_handoff_reference"),
        "approval_required": route.get("approval_required", False),
        "clarification_required": route.get("clarification_required", False),
        "provider_invoked": route.get("provider_invoked") is True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(continuation: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(continuation, "post-context continuation")
    returned = {
        "artifact_type": POST_CONTEXT_CONTINUATION_RETURNED_V1,
        "runtime_version": AIGOL_CONTEXT_ASSEMBLED_TO_PPP_ROUTING_CONTINUATION_VERSION,
        "continuation_reference": continuation["continuation_id"],
        "continuation_hash": continuation["artifact_hash"],
        "continuation_status": continuation["continuation_status"],
        "ppp_route_status": continuation["ppp_route_status"],
        "context_hash": continuation["context_hash"],
        "domain_reference": continuation["domain_reference"],
        "worker_reference": continuation["worker_reference"],
        "provider_invoked": continuation["provider_invoked"],
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": continuation["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(
    continuation: dict[str, Any],
    returned: dict[str, Any],
    ppp_capture: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "post_context_continuation_artifact": deepcopy(continuation),
        "post_context_continuation_returned": deepcopy(returned),
        "post_context_continuation_replay_reference": str(replay_path),
        "conversation_ppp_routing": deepcopy(ppp_capture),
        "continuation_status": continuation["continuation_status"],
        "ppp_route_status": continuation["ppp_route_status"],
        "context_hash": continuation["context_hash"],
        "domain_reference": continuation["domain_reference"],
        "worker_reference": continuation["worker_reference"],
        "implementation_handoff_reference": continuation["implementation_handoff_reference"],
        "approval_required": continuation["approval_required"],
        "fail_closed": continuation["continuation_status"] == FAILED_CLOSED,
        "failure_reason": continuation["failure_reason"],
        "provider_invoked": continuation["provider_invoked"],
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["post_context_continuation_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("post-context continuation replay step ordering mismatch")
    _verify_artifact_hash(artifact, "post-context continuation")
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


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("post-context continuation replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("post-context continuation replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "post-context continuation failed closed"


__all__ = [
    "AIGOL_CONTEXT_ASSEMBLED_TO_PPP_ROUTING_CONTINUATION_VERSION",
    "POST_CONTEXT_CONTINUATION_ARTIFACT_V1",
    "POST_CONTEXT_CONTINUATION_REACHED_PPP",
    "continue_context_assembled_to_ppp_routing",
    "reconstruct_context_assembled_to_ppp_routing_continuation_replay",
]
