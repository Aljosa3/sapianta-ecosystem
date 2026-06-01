"""Replay-visible Source Of Truth Router Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


SOURCE_OF_TRUTH_ROUTER_RUNTIME_VERSION = "SOURCE_OF_TRUTH_ROUTER_RUNTIME_V1"
SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1 = "SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1"
SOURCE_OF_TRUTH_ROUTER_SELECTED = "SOURCE_OF_TRUTH_ROUTER_SELECTED"
SOURCE_OF_TRUTH_ROUTER_RETURNED = "SOURCE_OF_TRUTH_ROUTER_RETURNED"
SELECTED = "SELECTED"

REPLAY = "REPLAY"
GOVERNANCE = "GOVERNANCE"
CONSTITUTIONAL_MEMORY = "CONSTITUTIONAL_MEMORY"
SELF_RESOLUTION = "SELF_RESOLUTION"
PROVIDER = "PROVIDER"

SOURCE_PRIORITY = (REPLAY, GOVERNANCE, CONSTITUTIONAL_MEMORY, SELF_RESOLUTION, PROVIDER)
SUPPORTED_SOURCES = frozenset(SOURCE_PRIORITY)
REPLAY_STEPS = ("source_of_truth_router_selected", "source_of_truth_router_returned")

REPLAY_MARKERS = (
    "what happened recently",
    "what changed",
    "show latest proposal",
    "show latest approval",
    "what was the last operation",
    "summarize recent activity",
)
GOVERNANCE_MARKERS = (
    "what governance exists",
    "what was certified",
    "which milestone was completed",
    "governance guarantees",
    "what adrs define this capability",
    "status of a governance milestone",
)
CONSTITUTIONAL_MEMORY_MARKERS = (
    "what is aigol",
    "what is replay",
    "provider boundaries",
    "worker boundaries",
    "proposal approval",
    "purpose of governance",
    "constitutional guarantees",
)
SELF_RESOLUTION_MARKERS = (
    "hello",
    "hi",
    "explain simply",
    "what can you do",
)
PROVIDER_MARKERS = (
    "explain ai alignment",
    "write a poem",
    "write poem",
    "draft",
    "summarize this idea",
)
EVIDENCE_BOUND_SOURCES = frozenset({REPLAY, GOVERNANCE, CONSTITUTIONAL_MEMORY})
FORBIDDEN_FIELDS = frozenset(
    {
        "approval_decision",
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "dispatch_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
    }
)


def route_source_of_truth(
    *,
    router_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    created_at: str,
    replay_dir: str | Path,
    evidence_refs: list[str] | None = None,
    created_by: str = "AIGOL",
) -> dict[str, Any]:
    """Select one source of truth for a prompt without invoking the source."""

    replay_path = Path(replay_dir)
    _ensure_router_replay_available(replay_path)
    prompt = _normalize_text(human_prompt, "human_prompt")
    candidate_sources = _candidate_sources(prompt)
    if not candidate_sources:
        raise FailClosedRuntimeError("source of truth router failed closed: no candidate source")
    selected_source = _select_by_priority(candidate_sources)
    refs = _evidence_refs(selected_source, evidence_refs)
    artifact = _router_artifact(
        router_id=router_id,
        human_prompt_reference=human_prompt_reference,
        human_prompt=prompt,
        candidate_sources=candidate_sources,
        selected_source=selected_source,
        selection_reason=_selection_reason(selected_source, candidate_sources),
        evidence_refs=refs,
        created_at=created_at,
        created_by=created_by,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
    returned = _router_returned(artifact)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(artifact, returned)


def reconstruct_source_of_truth_router_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Source Of Truth Router replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("source of truth router replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("source of truth router replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "source of truth router artifact")
        wrappers.append(wrapper)

    selection = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("router_reference") != selection["router_id"]:
        raise FailClosedRuntimeError("source of truth router replay reference mismatch")
    if returned.get("router_hash") != selection["artifact_hash"]:
        raise FailClosedRuntimeError("source of truth router replay hash mismatch")
    _validate_router_artifact(selection)
    return {
        "router_id": selection["router_id"],
        "selected_source": selection["selected_source"],
        "selection_reason": selection["selection_reason"],
        "human_prompt_reference": selection["human_prompt_reference"],
        "created_at": selection["created_at"],
        "candidate_sources": deepcopy(selection["candidate_sources"]),
        "source_priority": deepcopy(selection["source_priority"]),
        "selection_status": selection["selection_status"],
        "provider_required": selection["provider_required"],
        "provider_used": False,
        "worker_required": False,
        "execution_required": False,
        "proposal_lifecycle_required": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _router_artifact(
    *,
    router_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    candidate_sources: list[str],
    selected_source: str,
    selection_reason: str,
    evidence_refs: list[str],
    created_at: str,
    created_by: str,
) -> dict[str, Any]:
    source = _normalize_token(selected_source, "selected_source")
    artifact = {
        "artifact_type": SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1,
        "router_runtime_version": SOURCE_OF_TRUTH_ROUTER_RUNTIME_VERSION,
        "router_id": _require_string(router_id, "router_id"),
        "human_prompt_reference": _require_string(human_prompt_reference, "human_prompt_reference"),
        "human_prompt_hash": replay_hash({"human_prompt": _normalize_text(human_prompt, "human_prompt")}),
        "candidate_sources": list(candidate_sources),
        "selected_source": source,
        "source_priority": list(SOURCE_PRIORITY),
        "selection_reason": _normalize_text(selection_reason, "selection_reason"),
        "evidence_refs": list(evidence_refs),
        "provider_required": source == PROVIDER,
        "provider_used": False,
        "worker_required": False,
        "execution_required": False,
        "proposal_lifecycle_required": False,
        "selection_status": SELECTED,
        "created_by": _normalize_token(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": f"{_require_string(router_id, 'router_id')}:SOURCE_OF_TRUTH_ROUTER_REPLAY",
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "worker_invoked": False,
        "provider_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_router_artifact(artifact)
    return artifact


def _router_returned(selection: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(selection, "source of truth router artifact")
    returned = {
        "event_type": SOURCE_OF_TRUTH_ROUTER_RETURNED,
        "router_reference": selection["router_id"],
        "router_hash": selection["artifact_hash"],
        "selected_source": selection["selected_source"],
        "selection_status": selection["selection_status"],
        "human_prompt_reference": selection["human_prompt_reference"],
        "replay_visible": True,
        "provider_required": selection["provider_required"],
        "provider_used": False,
        "worker_required": False,
        "execution_required": False,
        "proposal_lifecycle_required": False,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "worker_invoked": False,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(selection: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "source_of_truth_router_artifact": deepcopy(selection),
        "source_of_truth_router_replay": deepcopy(returned),
    }
    capture["source_of_truth_router_capture_hash"] = replay_hash(capture)
    return capture


def _candidate_sources(human_prompt: str) -> list[str]:
    lowered = human_prompt.lower().rstrip("?.! ")
    candidates: list[str] = []
    if _contains_marker(lowered, REPLAY_MARKERS):
        candidates.append(REPLAY)
    if _contains_marker(lowered, GOVERNANCE_MARKERS):
        candidates.append(GOVERNANCE)
    if _contains_marker(lowered, CONSTITUTIONAL_MEMORY_MARKERS):
        candidates.append(CONSTITUTIONAL_MEMORY)
    if _contains_marker(lowered, SELF_RESOLUTION_MARKERS):
        candidates.append(SELF_RESOLUTION)
    if _contains_marker(lowered, PROVIDER_MARKERS):
        candidates.append(PROVIDER)
    if not candidates:
        candidates.append(PROVIDER)
    if PROVIDER not in candidates and _is_open_ended(lowered):
        candidates.append(PROVIDER)
    return candidates


def _select_by_priority(candidate_sources: list[str]) -> str:
    normalized = [_normalize_token(source, "candidate_source") for source in candidate_sources]
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError("source of truth router failed closed: ambiguous routing")
    for source in normalized:
        if source not in SUPPORTED_SOURCES:
            raise FailClosedRuntimeError("source of truth router failed closed: invalid source")
    for source in SOURCE_PRIORITY:
        if source in normalized:
            return source
    raise FailClosedRuntimeError("source of truth router failed closed: no candidate source")


def _evidence_refs(selected_source: str, evidence_refs: list[str] | None) -> list[str]:
    source = _normalize_token(selected_source, "selected_source")
    refs = list(evidence_refs) if evidence_refs is not None else [_default_evidence_ref(source)]
    if not refs or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise FailClosedRuntimeError("source of truth router failed closed: missing references")
    return refs


def _default_evidence_ref(source: str) -> str:
    if source == REPLAY:
        return "REPLAY_SOURCE_REQUIRED"
    if source == GOVERNANCE:
        return "GOVERNANCE_ARTIFACTS"
    if source == CONSTITUTIONAL_MEMORY:
        return "CONSTITUTIONAL_MEMORY_CITATIONS"
    if source == SELF_RESOLUTION:
        return "DETERMINISTIC_SELF_RESOLUTION_RULES"
    if source == PROVIDER:
        return "PROVIDER_VALIDATION_PATH"
    raise FailClosedRuntimeError("source of truth router failed closed: invalid source")


def _selection_reason(selected_source: str, candidate_sources: list[str]) -> str:
    source = _normalize_token(selected_source, "selected_source")
    candidates = ", ".join(candidate_sources)
    return f"Selected {source} using canonical source priority from candidates: {candidates}."


def _contains_marker(prompt: str, markers: tuple[str, ...]) -> bool:
    return any(marker in prompt for marker in markers)


def _is_open_ended(prompt: str) -> bool:
    return prompt.startswith(("explain ", "write ", "draft ", "summarize ")) or " poem" in prompt


def _validate_router_artifact(selection: dict[str, Any]) -> None:
    if selection.get("artifact_type") != SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("source of truth router failed closed: invalid artifact")
    selected = selection.get("selected_source")
    if selected not in SUPPORTED_SOURCES:
        raise FailClosedRuntimeError("source of truth router failed closed: invalid source")
    candidates = selection.get("candidate_sources")
    if not isinstance(candidates, list) or not candidates:
        raise FailClosedRuntimeError("source of truth router failed closed: no candidate source")
    if selected not in candidates:
        raise FailClosedRuntimeError("source of truth router failed closed: selected source not in candidates")
    if _select_by_priority(candidates) != selected:
        raise FailClosedRuntimeError("source of truth router failed closed: ambiguous routing")
    if selection.get("source_priority") != list(SOURCE_PRIORITY):
        raise FailClosedRuntimeError("source of truth router failed closed: invalid source priority")
    evidence_refs = selection.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise FailClosedRuntimeError("source of truth router failed closed: missing references")
    if selected in EVIDENCE_BOUND_SOURCES and any(not isinstance(ref, str) or not ref.strip() for ref in evidence_refs):
        raise FailClosedRuntimeError("source of truth router failed closed: missing references")
    if selected in {REPLAY, GOVERNANCE, CONSTITUTIONAL_MEMORY} and selection.get("provider_required") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: provider required for local truth")
    if selection.get("provider_required") is not (selected == PROVIDER):
        raise FailClosedRuntimeError("source of truth router failed closed: invalid provider requirement")
    if selection.get("provider_used") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: provider use introduced")
    if selection.get("worker_required") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: worker requirement introduced")
    if selection.get("execution_required") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: execution requirement introduced")
    if selection.get("proposal_lifecycle_required") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: proposal lifecycle introduced")
    if selection.get("selection_status") != SELECTED:
        raise FailClosedRuntimeError("source of truth router failed closed: invalid selection status")
    if selection.get("created_by") != "AIGOL":
        raise FailClosedRuntimeError("source of truth router failed closed: creator must be AIGOL")
    if selection.get("replay_visible") is not True:
        raise FailClosedRuntimeError("source of truth router failed closed: replay visibility missing")
    if selection.get("authority") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: authority introduced")
    if selection.get("approval_created") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: approval introduced")
    if selection.get("execution_requested") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: execution requested")
    if selection.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: worker invocation detected")
    if selection.get("provider_authority") is not False:
        raise FailClosedRuntimeError("source of truth router failed closed: provider authority introduced")
    if FORBIDDEN_FIELDS.intersection(selection):
        raise FailClosedRuntimeError("source of truth router failed closed: authority-bearing route")
    _require_string(selection.get("router_id"), "router_id")
    _require_string(selection.get("human_prompt_reference"), "human_prompt_reference")
    _require_string(selection.get("selection_reason"), "selection_reason")
    _require_string(selection.get("created_at"), "created_at")
    _require_string(selection.get("replay_reference"), "replay_reference")


def _ensure_router_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("source of truth router replay step ordering mismatch")
    _verify_artifact_hash(artifact, "source of truth router artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": SOURCE_OF_TRUTH_ROUTER_SELECTED if index == 0 else SOURCE_OF_TRUTH_ROUTER_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("source of truth router replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("source of truth router replay hash mismatch")


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
