"""Conversation native-development context integration for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.conversation_chain_continuity_runtime import attach_conversation_chain_continuity
from aigol.runtime.development_context_assembly_runtime import (
    CONTEXT_ASSEMBLED,
    assemble_development_context,
    reconstruct_development_context_assembly_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_task_intake_runtime import (
    NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED,
    reconstruct_native_development_task_intake_replay,
    run_native_development_task_intake,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_VERSION = (
    "AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_V1"
)
CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED = "CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = (
    "conversation_native_development_context_integrated",
    "conversation_native_development_context_returned",
)


def run_conversation_native_development_context_integration(
    *,
    prompt_id: str,
    human_prompt: str,
    created_at: str,
    replay_dir: str | Path,
    governance_root: str | Path = "governance",
    session_id: str | None = None,
    turn_id: str | None = None,
    current_chain_id: str | None = None,
    latest_chain_id: str | None = None,
) -> dict[str, Any]:
    """Run native-development intake and deterministic context assembly for a conversation turn."""

    root = Path(replay_dir)
    integration_replay = root / "native_development_context_integration"
    try:
        _ensure_replay_available(integration_replay)
        prompt = _require_string(prompt_id, "prompt_id")
        intake_capture = run_native_development_task_intake(
            intake_id=f"{prompt}:NATIVE_DEVELOPMENT_TASK_INTAKE",
            human_prompt_reference=prompt,
            human_prompt=human_prompt,
            created_at=created_at,
            replay_dir=root / "native_development_task_intake",
            session_id=session_id,
            turn_id=turn_id,
        )
        if intake_capture.get("intake_status") != NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED:
            raise FailClosedRuntimeError(
                intake_capture.get("failure_reason") or "conversation native development intake failed closed"
            )
        context_capture = assemble_development_context(
            context_assembly_id=f"{prompt}:DEVELOPMENT_CONTEXT_ASSEMBLY",
            development_task_intake_artifact=intake_capture["native_development_task_intake_artifact"],
            governance_root=governance_root,
            replay_dir=root / "development_context_assembly",
            created_at=created_at,
        )
        if context_capture.get("context_status") != CONTEXT_ASSEMBLED:
            raise FailClosedRuntimeError(
                context_capture.get("failure_reason") or "conversation native development context assembly failed closed"
            )
        integration = _integration_artifact(
            prompt_id=prompt,
            intake_capture=intake_capture,
            context_capture=context_capture,
            integration_status=CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED,
            created_at=created_at,
            replay_reference=str(integration_replay),
            failure_reason=None,
        )
        returned = _returned_artifact(integration)
        _persist_step(integration_replay, 0, REPLAY_STEPS[0], integration)
        _persist_step(integration_replay, 1, REPLAY_STEPS[1], returned)
        capture = _capture(
            intake_capture=intake_capture,
            context_capture=context_capture,
            integration=integration,
            returned=returned,
            replay_path=integration_replay,
        )
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        intake_capture = locals().get("intake_capture")
        context_capture = locals().get("context_capture")
        integration = _failed_integration_artifact(
            prompt_id=prompt_id,
            intake_capture=intake_capture if isinstance(intake_capture, dict) else None,
            context_capture=context_capture if isinstance(context_capture, dict) else None,
            created_at=created_at,
            replay_reference=str(integration_replay),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(integration)
        _persist_failure_if_possible(integration_replay, 0, REPLAY_STEPS[0], integration)
        _persist_failure_if_possible(integration_replay, 1, REPLAY_STEPS[1], returned)
        capture = _capture(
            intake_capture=intake_capture if isinstance(intake_capture, dict) else None,
            context_capture=context_capture if isinstance(context_capture, dict) else None,
            integration=integration,
            returned=returned,
            replay_path=integration_replay,
        )

    continuity_capture = attach_conversation_chain_continuity(
        prompt_id=prompt_id,
        conversation_capture=_continuity_capture(capture),
        created_at=created_at,
        replay_dir=root / "chain_continuity",
        session_id=session_id,
        current_chain_id=current_chain_id,
        latest_chain_id=latest_chain_id,
    )
    updated = deepcopy(capture)
    updated.update(
        {
            "canonical_chain_id": continuity_capture["canonical_chain_id"],
            "current_chain_id": continuity_capture["current_chain_id"],
            "latest_chain_id": continuity_capture["latest_chain_id"],
            "related_chain_id": continuity_capture["related_chain_id"],
            "suggested_inspection_commands": deepcopy(continuity_capture["suggested_inspection_commands"]),
            "suggested_next_actions": _suggested_next_actions(
                canonical_chain_id=continuity_capture["canonical_chain_id"],
                context_status=updated["context_status"],
                provider_necessity_classification=updated["provider_necessity_classification"],
            ),
            "conversation_chain_continuity_replay_reference": continuity_capture[
                "conversation_chain_continuity_replay_reference"
            ],
            "conversation_chain_continuity_hash": continuity_capture["conversation_chain_continuity_capture_hash"],
        }
    )
    updated["conversation_native_development_context_capture_hash"] = replay_hash(updated)
    return updated


def reconstruct_conversation_native_development_context_integration_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct conversation native-development integration replay."""

    root = Path(replay_dir)
    integration_replay = root / "native_development_context_integration"
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(integration_replay / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversation native development context replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversation native development context replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    integration = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("integration_reference") != integration["integration_id"]:
        raise FailClosedRuntimeError("conversation native development context replay reference mismatch")
    if returned.get("integration_hash") != integration["artifact_hash"]:
        raise FailClosedRuntimeError("conversation native development context replay hash mismatch")
    intake = None
    context = None
    if (root / "native_development_task_intake").exists():
        intake = reconstruct_native_development_task_intake_replay(root / "native_development_task_intake")
    if (root / "development_context_assembly").exists():
        context = reconstruct_development_context_assembly_replay(root / "development_context_assembly")
    return {
        "integration_id": integration["integration_id"],
        "integration_status": integration["integration_status"],
        "prompt_id": integration["prompt_id"],
        "task_intake_reference": integration["task_intake_reference"],
        "context_assembly_reference": integration["context_assembly_reference"],
        "context_status": integration["context_status"],
        "context_hash": integration["context_hash"],
        "missing_context": deepcopy(integration["missing_context"]),
        "ambiguous_context": deepcopy(integration["ambiguous_context"]),
        "provider_necessity_classification": integration["provider_necessity_classification"],
        "intake_replay": deepcopy(intake),
        "context_replay": deepcopy(context),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_artifact_count": len(wrappers)
        + (intake["replay_artifact_count"] if intake else 0)
        + (context["replay_artifact_count"] if context else 0),
        "replay_hash": replay_hash({"integration": wrappers, "intake": intake, "context": context}),
    }


def render_conversation_native_development_context_summary(capture: dict[str, Any]) -> str:
    lines = [
        f"task_intake_reference: {capture.get('task_intake_reference')}",
        f"context_assembly_reference: {capture.get('context_assembly_reference')}",
        f"context_status: {capture.get('context_status')}",
        f"context_hash: {capture.get('context_hash')}",
        f"canonical_chain_id: {capture.get('canonical_chain_id')}",
        f"provider_necessity_classification: {capture.get('provider_necessity_classification')}",
        f"missing_context: {len(capture.get('missing_context', []))}",
        f"ambiguous_context: {len(capture.get('ambiguous_context', []))}",
        f"suggested_next_actions: {', '.join(capture.get('suggested_next_actions', []))}",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _integration_artifact(
    *,
    prompt_id: str,
    intake_capture: dict[str, Any],
    context_capture: dict[str, Any],
    integration_status: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    intake_artifact = intake_capture["native_development_task_intake_artifact"]
    context_artifact = context_capture["development_context_assembly_artifact"]
    artifact = {
        "artifact_type": "CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_ARTIFACT_V1",
        "runtime_version": CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_VERSION,
        "integration_id": f"{_require_string(prompt_id, 'prompt_id')}:NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION",
        "prompt_id": prompt_id,
        "task_intake_reference": intake_artifact["intake_id"],
        "task_intake_hash": intake_artifact["artifact_hash"],
        "task_intake_replay_reference": intake_capture["native_development_task_intake_replay_reference"],
        "context_assembly_reference": context_artifact["context_assembly_id"],
        "context_assembly_hash": context_artifact["artifact_hash"],
        "context_assembly_replay_reference": context_capture["development_context_assembly_replay_reference"],
        "context_status": context_capture["context_status"],
        "context_hash": context_capture["context_hash"],
        "missing_context": deepcopy(context_capture["missing_context"]),
        "ambiguous_context": deepcopy(context_capture["ambiguous_context"]),
        "provider_necessity_classification": context_capture["provider_necessity_classification"],
        "integration_status": integration_status,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "authority": False,
        "provider_invoked": False,
        "provider_authority": False,
        "proposal_generated": False,
        "governance_modified": False,
        "domain_created": False,
        "worker_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_integration_artifact(
    *,
    prompt_id: str,
    intake_capture: dict[str, Any] | None,
    context_capture: dict[str, Any] | None,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    intake_artifact = intake_capture.get("native_development_task_intake_artifact") if intake_capture else {}
    context_artifact = context_capture.get("development_context_assembly_artifact") if context_capture else {}
    artifact = {
        "artifact_type": "CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_ARTIFACT_V1",
        "runtime_version": CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_VERSION,
        "integration_id": f"{_require_string(prompt_id, 'prompt_id')}:NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION",
        "prompt_id": prompt_id,
        "task_intake_reference": intake_artifact.get("intake_id"),
        "task_intake_hash": intake_artifact.get("artifact_hash"),
        "task_intake_replay_reference": intake_capture.get("native_development_task_intake_replay_reference")
        if intake_capture
        else None,
        "context_assembly_reference": context_artifact.get("context_assembly_id"),
        "context_assembly_hash": context_artifact.get("artifact_hash"),
        "context_assembly_replay_reference": context_capture.get("development_context_assembly_replay_reference")
        if context_capture
        else None,
        "context_status": context_capture.get("context_status") if context_capture else FAILED_CLOSED,
        "context_hash": context_capture.get("context_hash") if context_capture else None,
        "missing_context": deepcopy(context_capture.get("missing_context", [])) if context_capture else [],
        "ambiguous_context": deepcopy(context_capture.get("ambiguous_context", [])) if context_capture else [],
        "provider_necessity_classification": context_capture.get("provider_necessity_classification")
        if context_capture
        else "PROVIDER_NOT_REQUIRED",
        "integration_status": FAILED_CLOSED,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "authority": False,
        "provider_invoked": False,
        "provider_authority": False,
        "proposal_generated": False,
        "governance_modified": False,
        "domain_created": False,
        "worker_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(integration: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(integration)
    returned = {
        "event_type": "CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_RETURNED",
        "integration_reference": integration["integration_id"],
        "integration_hash": integration["artifact_hash"],
        "integration_status": integration["integration_status"],
        "task_intake_reference": integration["task_intake_reference"],
        "context_assembly_reference": integration["context_assembly_reference"],
        "context_status": integration["context_status"],
        "context_hash": integration["context_hash"],
        "provider_necessity_classification": integration["provider_necessity_classification"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": integration["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(
    *,
    intake_capture: dict[str, Any] | None,
    context_capture: dict[str, Any] | None,
    integration: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "conversation_native_development_context_integration_artifact": deepcopy(integration),
        "conversation_native_development_context_integration_replay": deepcopy(returned),
        "native_development_task_intake": deepcopy(intake_capture),
        "development_context_assembly": deepcopy(context_capture),
        "conversation_replay_reference": str(replay_path),
        "replay_reference": str(replay_path.parent),
        "response_status": integration["integration_status"],
        "response_source": "NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY",
        "response_text": "",
        "task_intake_reference": integration["task_intake_reference"],
        "context_assembly_reference": integration["context_assembly_reference"],
        "context_status": integration["context_status"],
        "context_hash": integration["context_hash"],
        "missing_context": deepcopy(integration["missing_context"]),
        "ambiguous_context": deepcopy(integration["ambiguous_context"]),
        "provider_necessity_classification": integration["provider_necessity_classification"],
        "fail_closed": integration["integration_status"] == FAILED_CLOSED,
        "failure_reason": integration["failure_reason"],
        "provider_invoked": False,
        "provider_used": False,
        "proposal_generated": False,
        "governance_modified": False,
        "domain_created": False,
        "worker_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
    }
    capture["conversation_native_development_context_capture_hash"] = replay_hash(capture)
    return capture


def _continuity_capture(capture: dict[str, Any]) -> dict[str, Any]:
    return {
        "prompt_id": capture["conversation_native_development_context_integration_artifact"]["prompt_id"],
        "response_status": capture["response_status"],
        "response_source": capture["response_source"],
        "response_text": capture["response_text"],
        "conversation_replay_reference": capture["conversation_replay_reference"],
        "replay_reference": capture["replay_reference"],
        "fail_closed": capture["fail_closed"],
        "worker_invoked": False,
        "execution_requested": False,
    }


def _suggested_next_actions(
    *,
    canonical_chain_id: str,
    context_status: str,
    provider_necessity_classification: str,
) -> list[str]:
    actions = [
        f"show-chain {canonical_chain_id}",
        f"show-full-lineage {canonical_chain_id}",
    ]
    if context_status == CONTEXT_ASSEMBLED:
        actions.append("prepare governed development proposal contract")
    if provider_necessity_classification == "PROVIDER_REQUIRED_FOR_PROPOSAL":
        actions.append("provider proposal may be requested only after proposal contract validation")
    return actions


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("conversation native development context replay step ordering mismatch")
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
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("conversation native development context artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversation native development context artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("conversation native development context replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversation native development context replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "conversation native development context integration failed closed"

