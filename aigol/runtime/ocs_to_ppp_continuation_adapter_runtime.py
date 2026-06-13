"""Replay-visible continuation from OCS-to-PPP handoff candidates into PPP routing."""

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
from aigol.runtime.ocs_to_ppp_binding_runtime import (
    OCS_TO_PPP_HANDOFF_ARTIFACT_V1,
    OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_TO_PPP_CONTINUATION_ADAPTER_VERSION = "AIGOL_OCS_TO_PPP_CONTINUATION_ADAPTER_V1"
OCS_TO_PPP_CONTINUATION_ARTIFACT_V1 = "OCS_TO_PPP_CONTINUATION_ARTIFACT_V1"
OCS_TO_PPP_CONTINUATION_RETURNED_V1 = "OCS_TO_PPP_CONTINUATION_RETURNED_V1"
OCS_TO_PPP_CONTINUATION_REACHED_PPP = "OCS_TO_PPP_CONTINUATION_REACHED_PPP"
OCS_TO_PPP_PROPOSAL_ONLY_PRESERVED = "OCS_TO_PPP_PROPOSAL_ONLY_PRESERVED"

REPLAY_STEPS = (
    "ocs_to_ppp_continuation_recorded",
    "ocs_to_ppp_continuation_returned",
)


def continue_ocs_to_ppp_routing(
    *,
    continuation_id: str,
    ocs_to_ppp_handoff_artifact: dict[str, Any],
    execution_required: bool,
    provider_id: str,
    created_at: str,
    replay_dir: str | Path,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    governance_root: str | Path = "governance",
    prompt_id: str | None = None,
    session_id: str | None = None,
    turn_id: str | None = None,
    current_chain_id: str | None = None,
    latest_chain_id: str | None = None,
    selected_candidate_id: str | None = None,
) -> dict[str, Any]:
    """Continue an execution-required OCS handoff through existing PPP routing."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        handoff = deepcopy(ocs_to_ppp_handoff_artifact)
        _validate_handoff(handoff)
        candidate = _selected_candidate(handoff, selected_candidate_id)
        normalized_prompt = _normalized_ppp_prompt(candidate, handoff)
        if execution_required is not True:
            artifact = _continuation_artifact(
                continuation_id=continuation_id,
                handoff=handoff,
                candidate=candidate,
                execution_required=False,
                normalized_prompt=normalized_prompt,
                ppp_capture=None,
                created_at=created_at,
                replay_reference=str(replay_path),
                continuation_status=OCS_TO_PPP_PROPOSAL_ONLY_PRESERVED,
                failure_reason=None,
            )
            returned = _returned_artifact(artifact)
            _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
            _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
            return _capture(artifact, returned, None, replay_path)
        ppp_capture = run_conversation_ppp_routing_integration(
            prompt_id=prompt_id or f"{_require_string(continuation_id, 'continuation_id')}:PPP",
            human_prompt=normalized_prompt,
            provider_id=provider_id,
            created_at=created_at,
            replay_dir=replay_path / "conversation_ppp_routing",
            registry=registry,
            adapter=adapter,
            governance_root=governance_root,
            session_id=session_id,
            turn_id=turn_id,
            current_chain_id=current_chain_id or handoff.get("source_context_id") or handoff["handoff_id"],
            latest_chain_id=latest_chain_id or current_chain_id or handoff.get("source_context_id") or handoff["handoff_id"],
        )
        if ppp_capture.get("fail_closed") is True:
            raise FailClosedRuntimeError(
                ppp_capture.get("failure_reason") or "OCS-to-PPP continuation failed closed: PPP routing failed"
            )
        artifact = _continuation_artifact(
            continuation_id=continuation_id,
            handoff=handoff,
            candidate=candidate,
            execution_required=True,
            normalized_prompt=normalized_prompt,
            ppp_capture=ppp_capture,
            created_at=created_at,
            replay_reference=str(replay_path),
            continuation_status=OCS_TO_PPP_CONTINUATION_REACHED_PPP,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, ppp_capture, replay_path)
    except Exception as exc:
        ppp_capture = locals().get("ppp_capture")
        handoff = deepcopy(ocs_to_ppp_handoff_artifact) if isinstance(ocs_to_ppp_handoff_artifact, dict) else {}
        candidate = locals().get("candidate") if isinstance(locals().get("candidate"), dict) else {}
        normalized_prompt = locals().get("normalized_prompt") if isinstance(locals().get("normalized_prompt"), str) else ""
        artifact = _failed_artifact(
            continuation_id=continuation_id,
            handoff=handoff,
            candidate=candidate,
            execution_required=execution_required,
            normalized_prompt=normalized_prompt,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, ppp_capture if isinstance(ppp_capture, dict) else None, replay_path)


def reconstruct_ocs_to_ppp_continuation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS-to-PPP continuation replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS-to-PPP continuation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS-to-PPP continuation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    artifact = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("continuation_reference") != artifact["continuation_id"]:
        raise FailClosedRuntimeError("OCS-to-PPP continuation returned reference mismatch")
    if returned.get("continuation_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("OCS-to-PPP continuation returned hash mismatch")
    return {
        "continuation_id": artifact["continuation_id"],
        "continuation_status": artifact["continuation_status"],
        "execution_required": artifact["execution_required"],
        "source_ocs_handoff": artifact["source_ocs_handoff"],
        "source_ocs_handoff_hash": artifact["source_ocs_handoff_hash"],
        "selected_candidate_id": artifact["selected_candidate_id"],
        "normalized_prompt_hash": artifact["normalized_prompt_hash"],
        "ppp_route_status": artifact["ppp_route_status"],
        "ppp_route_reference": artifact["ppp_route_reference"],
        "ppp_route_hash": artifact["ppp_route_hash"],
        "provider_invoked_directly": artifact["provider_invoked_directly"],
        "worker_invoked_directly": artifact["worker_invoked_directly"],
        "approval_created": artifact["approval_created"],
        "worker_invoked": artifact["worker_invoked"],
        "execution_requested": artifact["execution_requested"],
        "dispatch_requested": artifact["dispatch_requested"],
        "replay_visible": True,
        "fail_closed": artifact["fail_closed"],
        "failure_reason": artifact["failure_reason"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _continuation_artifact(
    *,
    continuation_id: str,
    handoff: dict[str, Any],
    candidate: dict[str, Any],
    execution_required: bool,
    normalized_prompt: str,
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
        "artifact_type": OCS_TO_PPP_CONTINUATION_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_TO_PPP_CONTINUATION_ADAPTER_VERSION,
        "continuation_id": _require_string(continuation_id, "continuation_id"),
        "continuation_status": continuation_status,
        "execution_required": execution_required is True,
        "source_ocs_handoff": handoff.get("handoff_id"),
        "source_ocs_handoff_hash": handoff.get("artifact_hash"),
        "source_ocs_handoff_status": handoff.get("handoff_status"),
        "source_ocs_handoff_proposal_only": handoff.get("proposal_only") is True,
        "source_context_id": handoff.get("source_context_id"),
        "source_context_hash": handoff.get("source_context_hash"),
        "source_cognition_id": handoff.get("source_cognition_id"),
        "source_cognition_hash": handoff.get("source_cognition_hash"),
        "source_semantic_resolution_id": handoff.get("source_semantic_resolution_id"),
        "source_semantic_hash": handoff.get("source_semantic_hash"),
        "selected_candidate_id": candidate.get("candidate_id"),
        "selected_candidate_type": candidate.get("candidate_type"),
        "selected_candidate_hash": replay_hash(candidate) if candidate else None,
        "normalized_prompt_hash": replay_hash(normalized_prompt) if normalized_prompt else None,
        "normalized_prompt_authority": False,
        "ppp_route_reference": route.get("route_id"),
        "ppp_route_hash": route.get("artifact_hash"),
        "ppp_route_status": route.get("route_status"),
        "ppp_invoked": bool(route),
        "provider_invoked_via_ppp": ppp_capture.get("provider_invoked") is True if isinstance(ppp_capture, dict) else False,
        "provider_invoked_directly": False,
        "worker_invoked_directly": False,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "human_approval_boundary_preserved": True,
        "worker_backbone_reused": route.get("route_status") is not None,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "fail_closed": continuation_status == FAILED_CLOSED,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(continuation: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(continuation)
    returned = {
        "artifact_type": OCS_TO_PPP_CONTINUATION_RETURNED_V1,
        "runtime_version": AIGOL_OCS_TO_PPP_CONTINUATION_ADAPTER_VERSION,
        "continuation_reference": continuation["continuation_id"],
        "continuation_hash": continuation["artifact_hash"],
        "continuation_status": continuation["continuation_status"],
        "execution_required": continuation["execution_required"],
        "source_ocs_handoff": continuation["source_ocs_handoff"],
        "source_ocs_handoff_hash": continuation["source_ocs_handoff_hash"],
        "ppp_route_status": continuation["ppp_route_status"],
        "replay_visible": True,
        "failure_reason": continuation["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _failed_artifact(
    *,
    continuation_id: str,
    handoff: dict[str, Any],
    candidate: dict[str, Any],
    execution_required: bool,
    normalized_prompt: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    return _continuation_artifact(
        continuation_id=continuation_id,
        handoff=handoff if isinstance(handoff, dict) else {},
        candidate=candidate if isinstance(candidate, dict) else {},
        execution_required=execution_required,
        normalized_prompt=normalized_prompt,
        ppp_capture=None,
        created_at=created_at,
        replay_reference=replay_reference,
        continuation_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _capture(
    artifact: dict[str, Any],
    returned: dict[str, Any],
    ppp_capture: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    return {
        "ocs_to_ppp_continuation_artifact": deepcopy(artifact),
        "ocs_to_ppp_continuation_returned": deepcopy(returned),
        "ocs_to_ppp_continuation_replay_reference": str(replay_path),
        "conversation_ppp_routing": deepcopy(ppp_capture),
        "continuation_status": artifact["continuation_status"],
        "execution_required": artifact["execution_required"],
        "ppp_route_status": artifact["ppp_route_status"],
        "ppp_route_reference": artifact["ppp_route_reference"],
        "ppp_invoked": artifact["ppp_invoked"],
        "provider_invoked_directly": False,
        "worker_invoked_directly": False,
        "provider_invoked_via_ppp": artifact["provider_invoked_via_ppp"],
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "approval_created": False,
        "worker_backbone_reused": artifact["worker_backbone_reused"],
        "replay_visible": True,
        "fail_closed": artifact["fail_closed"],
        "failure_reason": artifact["failure_reason"],
    }


def _validate_handoff(handoff: dict[str, Any]) -> None:
    if handoff.get("artifact_type") != OCS_TO_PPP_HANDOFF_ARTIFACT_V1:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: invalid handoff artifact")
    if handoff.get("handoff_status") != OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: handoff candidate not created")
    if handoff.get("proposal_only") is not True:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: proposal-only handoff required")
    if handoff.get("replay_visible") is not True:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: handoff is not replay-visible")
    if handoff.get("ppp_invoked") is not False:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: source handoff already invoked PPP")
    for flag in ("provider_invoked", "worker_invoked", "execution_requested", "dispatch_requested"):
        if handoff.get(flag) is not False:
            raise FailClosedRuntimeError(f"OCS-to-PPP continuation failed closed: source handoff has {flag}")
    _verify_artifact_hash(handoff)
    if not handoff.get("handoff_candidates"):
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: no handoff candidates")


def _selected_candidate(handoff: dict[str, Any], selected_candidate_id: str | None) -> dict[str, Any]:
    candidates = handoff.get("handoff_candidates")
    if not isinstance(candidates, list) or not candidates:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: handoff candidates missing")
    selected = None
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        if selected_candidate_id is None or candidate.get("candidate_id") == selected_candidate_id:
            selected = deepcopy(candidate)
            break
    if selected is None:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: selected candidate not found")
    if selected.get("clarification_required") is True:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: selected candidate requires clarification")
    if selected.get("ppp_invoked") is not False:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: candidate already invoked PPP")
    if selected.get("proposal_created") is not False:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: candidate already created proposal")
    return selected


def _normalized_ppp_prompt(candidate: dict[str, Any], handoff: dict[str, Any]) -> str:
    domains = candidate.get("target_domains")
    workers = candidate.get("worker_candidates")
    if not isinstance(workers, list) or not workers:
        workers = handoff.get("worker_candidate_findings")
    if not isinstance(domains, list) or not domains:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: candidate domain missing")
    if not isinstance(workers, list) or not workers:
        raise FailClosedRuntimeError("OCS-to-PPP continuation failed closed: candidate worker missing")
    domain = _require_string(domains[0], "target_domain").upper()
    worker = _require_string(
        workers[0].get("worker_family_id") or workers[0].get("worker_id"),
        "worker_family_id",
    ).upper()
    milestone = _milestone_id(domain, worker)
    return (
        f"Implement {milestone}. Foundation only. "
        "Continue OCS execution-required handoff into PPP governance. "
        "No dispatch. No invocation. No execution. No governance mutation. No replay mutation."
    )


def _milestone_id(domain: str, worker: str) -> str:
    if domain == "AIGOL" and worker == "CLAUDE_EXTERNAL":
        return "CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1"
    return f"{domain}_{worker}_WORKER_FOUNDATION_V1"


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS-to-PPP continuation replay step ordering mismatch")
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
    except Exception:
        return


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"OCS-to-PPP continuation {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS-to-PPP continuation failed closed"


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("OCS-to-PPP continuation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("OCS-to-PPP continuation replay hash mismatch")
