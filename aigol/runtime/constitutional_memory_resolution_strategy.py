"""Constitutional-memory answer resolution for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.constitutional_memory_access import (
    CONSTITUTIONAL_MEMORY_CATALOG,
    reconstruct_constitutional_memory_retrieval_replay,
    retrieve_constitutional_memory,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.resolution_strategy_runtime import CONSTITUTIONAL_MEMORY, select_resolution_strategy
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CONSTITUTIONAL_MEMORY_RESOLUTION_STRATEGY_VERSION = "CONSTITUTIONAL_MEMORY_RESOLUTION_STRATEGY_V1"
CONSTITUTIONAL_MEMORY_RESOLUTION_ARTIFACT_V1 = "CONSTITUTIONAL_MEMORY_RESOLUTION_ARTIFACT_V1"
CONSTITUTIONAL_MEMORY_RESOLUTION_CREATED = "CONSTITUTIONAL_MEMORY_RESOLUTION_CREATED"
CONSTITUTIONAL_MEMORY_RESOLUTION_RETURNED = "CONSTITUTIONAL_MEMORY_RESOLUTION_RETURNED"
RESOLVED = "RESOLVED"

REPLAY_STEPS = ("constitutional_memory_resolution_created", "constitutional_memory_resolution_returned")

CONSTITUTIONAL_PROMPT_MARKERS = (
    "what is aigol",
    "what is replay",
    "provider boundaries",
    "worker boundaries",
    "proposal approval",
    "purpose of governance",
    "constitutional guarantees",
)

CONSTITUTIONAL_RESOLUTION_CATALOG = {
    **CONSTITUTIONAL_MEMORY_CATALOG,
    "PROVIDER_BOUNDARY_GUARANTEES": {
        "path": "governance/PROVIDER_BOUNDARY_GUARANTEES_V1.md",
        "classification": "SUPPORTING",
        "layer": "M3_GOVERNANCE_CERTIFICATION_MEMORY",
        "scopes": ["AUTHORITY_INVARIANTS", "GOVERNANCE_REVIEWS"],
    },
    "WORKER_BOUNDARY_GUARANTEES": {
        "path": "governance/EXTERNAL_WORKER_BOUNDARY_GUARANTEES_V1.md",
        "classification": "SUPPORTING",
        "layer": "M3_GOVERNANCE_CERTIFICATION_MEMORY",
        "scopes": ["AUTHORITY_INVARIANTS", "GOVERNANCE_REVIEWS"],
    },
    "PROPOSAL_APPROVAL_FOUNDATION": {
        "path": "governance/PROPOSAL_APPROVAL_FOUNDATION_V1.md",
        "classification": "SUPPORTING",
        "layer": "M3_GOVERNANCE_CERTIFICATION_MEMORY",
        "scopes": ["GOVERNANCE_REVIEWS"],
    },
}


def is_constitutional_memory_prompt(human_prompt: str) -> bool:
    """Return whether the prompt asks for constitutional or architectural memory."""

    prompt = _normalize_text(human_prompt, "human_prompt").lower().rstrip("?.! ")
    return any(marker in prompt for marker in CONSTITUTIONAL_PROMPT_MARKERS)


def resolve_constitutional_memory_question(
    *,
    resolution_id: str,
    strategy_id: str,
    retrieval_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    created_at: str,
    replay_dir: str | Path,
    repository_root: str | Path | None = None,
    artifact_catalog: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Resolve a constitutional question from citation-bound memory evidence only."""

    replay_path = Path(replay_dir)
    _ensure_resolution_replay_available(replay_path)
    if not is_constitutional_memory_prompt(human_prompt):
        raise FailClosedRuntimeError(
            "constitutional memory resolution failed closed: prompt is not constitutional-memory-oriented"
        )

    query_plan = _query_plan(human_prompt)
    strategy_capture = select_resolution_strategy(
        strategy_id=strategy_id,
        selected_strategy=CONSTITUTIONAL_MEMORY,
        selection_reason="Prompt asks for citation-bound constitutional memory.",
        human_prompt_reference=human_prompt_reference,
        created_at=created_at,
        replay_dir=replay_path / "strategy_selection",
    )
    retrieval_capture = retrieve_constitutional_memory(
        retrieval_id=retrieval_id,
        requested_by="AIGOL_GOVERNANCE",
        retrieval_scope=query_plan["retrieval_scope"],
        query=query_plan["query"],
        artifact_query=query_plan["artifact_query"],
        governance_context=query_plan["governance_context"],
        created_at=created_at,
        replay_dir=replay_path / "constitutional_memory_access",
        repository_root=repository_root,
        artifact_catalog=CONSTITUTIONAL_RESOLUTION_CATALOG if artifact_catalog is None else artifact_catalog,
    )
    retrieval_result = retrieval_capture["retrieval_result"]
    if retrieval_result.get("retrieval_status") != "SUCCESS":
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: constitutional evidence missing")

    strategy_artifact = strategy_capture["resolution_strategy_artifact"]
    resolution = _resolution_artifact(
        resolution_id=resolution_id,
        strategy_artifact=strategy_artifact,
        retrieval_result=retrieval_result,
        human_prompt_reference=human_prompt_reference,
        human_prompt=human_prompt,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], resolution)
    returned = _resolution_returned(resolution)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(strategy_artifact, retrieval_result, resolution, returned)


def reconstruct_constitutional_memory_resolution(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct constitutional-memory resolution evidence deterministically."""

    replay_path = Path(replay_dir)
    memory_replay = reconstruct_constitutional_memory_retrieval_replay(replay_path / "constitutional_memory_access")
    if memory_replay.get("retrieval_status") != "SUCCESS":
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: corrupt constitutional artifacts")

    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("constitutional memory resolution ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("constitutional memory resolution artifact must be a JSON object")
        _verify_artifact_hash(artifact, "constitutional memory resolution artifact")
        wrappers.append(wrapper)

    resolution = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("resolution_reference") != resolution["resolution_id"]:
        raise FailClosedRuntimeError("constitutional memory resolution reference mismatch")
    if returned.get("resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("constitutional memory resolution hash mismatch")
    if memory_replay.get("retrieval_id") != resolution["retrieval_reference"]:
        raise FailClosedRuntimeError("constitutional memory resolution retrieval reference mismatch")
    _validate_resolution(resolution)
    return {
        "resolution_id": resolution["resolution_id"],
        "selected_strategy": resolution["selected_strategy"],
        "human_prompt_reference": resolution["human_prompt_reference"],
        "answer_text": resolution["answer_text"],
        "citation_count": resolution["citation_count"],
        "retrieval_reference": resolution["retrieval_reference"],
        "resolution_status": resolution["resolution_status"],
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_created": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers) + memory_replay["replay_artifact_count"],
        "replay_hash": replay_hash({"memory_replay": memory_replay, "resolution_replay": wrappers}),
    }


def _query_plan(human_prompt: str) -> dict[str, Any]:
    prompt = _normalize_text(human_prompt, "human_prompt").lower()
    if "what is replay" in prompt:
        return _plan("REPLAY_LINEAGE", "CANONICAL_REPLAY_LANGUAGE", "What is replay?", True)
    if "provider boundaries" in prompt:
        return _plan("AUTHORITY_INVARIANTS", "PROVIDER_BOUNDARY_GUARANTEES", "What are provider boundaries?", False)
    if "worker boundaries" in prompt:
        return _plan("AUTHORITY_INVARIANTS", "WORKER_BOUNDARY_GUARANTEES", "What are worker boundaries?", False)
    if "proposal approval" in prompt:
        return _plan("GOVERNANCE_REVIEWS", "PROPOSAL_APPROVAL_FOUNDATION", "What is proposal approval?", False)
    if "purpose of governance" in prompt:
        return _plan("GOVERNANCE_REVIEWS", "GOVERNANCE_ENFORCEMENT_HIERARCHY", "What is the purpose of governance?", False)
    if "constitutional guarantees" in prompt:
        return _plan("AUTHORITY_INVARIANTS", "FIRST_USEFUL_AIGOL_GUARANTEES", "What are constitutional guarantees?", False)
    return _plan("OPERATIONAL_BASELINES", "FIRST_USEFUL_AIGOL_BASELINE", "What is AiGOL?", False)


def _plan(retrieval_scope: str, artifact_query: str, query: str, governance_context: bool) -> dict[str, Any]:
    return {
        "retrieval_scope": retrieval_scope,
        "artifact_query": artifact_query,
        "query": query,
        "governance_context": governance_context,
    }


def _resolution_artifact(
    *,
    resolution_id: str,
    strategy_artifact: dict[str, Any],
    retrieval_result: dict[str, Any],
    human_prompt_reference: str,
    human_prompt: str,
    created_at: str,
) -> dict[str, Any]:
    citations = retrieval_result.get("returned_citations")
    if not isinstance(citations, list) or not citations:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: invalid references")
    primary = citations[0]
    artifact = {
        "artifact_type": CONSTITUTIONAL_MEMORY_RESOLUTION_ARTIFACT_V1,
        "constitutional_memory_resolution_version": CONSTITUTIONAL_MEMORY_RESOLUTION_STRATEGY_VERSION,
        "resolution_id": _require_string(resolution_id, "resolution_id"),
        "strategy_id": strategy_artifact["strategy_id"],
        "strategy_hash": strategy_artifact["artifact_hash"],
        "selected_strategy": CONSTITUTIONAL_MEMORY,
        "human_prompt_reference": _require_string(human_prompt_reference, "human_prompt_reference"),
        "human_prompt": _normalize_text(human_prompt, "human_prompt"),
        "retrieval_reference": retrieval_result["retrieval_id"],
        "retrieval_hash": retrieval_result["artifact_hash"],
        "citation_count": retrieval_result["citation_count"],
        "citations": deepcopy(citations),
        "answer_text": _answer_text(primary, retrieval_result["citation_count"]),
        "resolution_status": RESOLVED,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "reference_only": True,
        "authority": False,
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_resolution(artifact)
    return artifact


def _resolution_returned(resolution: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(resolution, "constitutional memory resolution artifact")
    returned = {
        "event_type": CONSTITUTIONAL_MEMORY_RESOLUTION_RETURNED,
        "resolution_reference": resolution["resolution_id"],
        "resolution_hash": resolution["artifact_hash"],
        "selected_strategy": CONSTITUTIONAL_MEMORY,
        "resolution_status": resolution["resolution_status"],
        "citation_count": resolution["citation_count"],
        "replay_visible": True,
        "reference_only": True,
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_created": False,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _answer_text(primary: dict[str, Any], citation_count: int) -> str:
    return (
        f"Constitutional Memory returned {citation_count} citation(s). "
        f"Primary citation: {primary['artifact_identity']} at {primary['artifact_path']}. "
        "The result is reference-only and carries no provider, worker, approval, or execution authority."
    )


def _capture(
    strategy: dict[str, Any],
    retrieval_result: dict[str, Any],
    resolution: dict[str, Any],
    returned: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "resolution_strategy_artifact": deepcopy(strategy),
        "constitutional_memory_retrieval_result": deepcopy(retrieval_result),
        "constitutional_memory_resolution_artifact": deepcopy(resolution),
        "constitutional_memory_resolution_replay": deepcopy(returned),
    }
    capture["constitutional_memory_resolution_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_resolution_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("constitutional memory resolution step ordering mismatch")
    _verify_artifact_hash(artifact, "constitutional memory resolution artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": CONSTITUTIONAL_MEMORY_RESOLUTION_CREATED
        if index == 0
        else CONSTITUTIONAL_MEMORY_RESOLUTION_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_resolution(resolution: dict[str, Any]) -> None:
    if resolution.get("artifact_type") != CONSTITUTIONAL_MEMORY_RESOLUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: invalid artifact")
    if resolution.get("selected_strategy") != CONSTITUTIONAL_MEMORY:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: invalid strategy")
    if resolution.get("resolution_status") != RESOLVED:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: invalid status")
    if int(resolution.get("citation_count", 0)) < 1:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: invalid references")
    citations = resolution.get("citations")
    if not isinstance(citations, list) or not citations:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: invalid references")
    for citation in citations:
        if not isinstance(citation, dict):
            raise FailClosedRuntimeError("constitutional memory resolution failed closed: invalid references")
        _require_string(citation.get("artifact_identity"), "artifact_identity")
        _require_string(citation.get("artifact_path"), "artifact_path")
        _require_string(citation.get("citation_reference"), "citation_reference")
        if citation.get("authority_status") != "REFERENCE_ONLY":
            raise FailClosedRuntimeError("constitutional memory resolution failed closed: authority introduced")
    if resolution.get("replay_visible") is not True:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: replay visibility missing")
    if resolution.get("reference_only") is not True:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: reference boundary missing")
    if resolution.get("authority") is not False:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: authority introduced")
    if resolution.get("provider_used") is not False:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: provider use introduced")
    if resolution.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: worker invocation detected")
    if resolution.get("execution_requested") is not False:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: execution requested")
    if resolution.get("approval_created") is not False:
        raise FailClosedRuntimeError("constitutional memory resolution failed closed: approval introduced")
    _require_string(resolution.get("resolution_id"), "resolution_id")
    _require_string(resolution.get("strategy_id"), "strategy_id")
    _require_string(resolution.get("strategy_hash"), "strategy_hash")
    _require_string(resolution.get("retrieval_reference"), "retrieval_reference")
    _require_string(resolution.get("retrieval_hash"), "retrieval_hash")
    _require_string(resolution.get("human_prompt_reference"), "human_prompt_reference")
    _require_string(resolution.get("answer_text"), "answer_text")
    _require_string(resolution.get("created_at"), "created_at")


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
        raise FailClosedRuntimeError("constitutional memory resolution replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("constitutional memory resolution replay hash mismatch")


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
