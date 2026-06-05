"""Bounded OCS memory and continuity runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import OCS_COGNITION_ARTIFACT_V1, OCS_COGNITION_COMPLETED
from aigol.runtime.ocs_context_assembly_runtime import OCS_CONTEXT_ASSEMBLED, OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1
from aigol.runtime.ocs_replay_derived_intent_runtime import (
    OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1,
    OCS_REPLAY_DERIVED_INTENT_CREATED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_MEMORY_AND_CONTINUITY_RUNTIME_VERSION = "AIGOL_OCS_MEMORY_AND_CONTINUITY_RUNTIME_V1"
OCS_MEMORY_ARTIFACT_V1 = "OCS_MEMORY_ARTIFACT_V1"
OCS_CONTINUITY_ARTIFACT_V1 = "OCS_CONTINUITY_ARTIFACT_V1"
OCS_MEMORY_AND_CONTINUITY_RECORDED = "OCS_MEMORY_AND_CONTINUITY_RECORDED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_memory_recorded",
    "ocs_continuity_recorded",
    "ocs_memory_and_continuity_returned",
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_domain_creation": False,
    "authorizes_human_approval": False,
    "authorizes_automatic_implementation": False,
}

PROHIBITED_FLAGS = (
    "authority",
    "approval_created",
    "approval_inferred",
    "execution_requested",
    "dispatch_requested",
    "worker_assignment_requested",
    "worker_dispatch_requested",
    "worker_invocation_requested",
    "worker_invoked",
    "provider_invoked",
    "domain_created",
    "governance_modified",
    "replay_modified",
    "automatic_implementation_requested",
)


def build_ocs_memory_and_continuity(
    *,
    memory_continuity_id: str,
    created_at: str,
    replay_dir: str | Path,
    ocs_context_artifacts: list[dict[str, Any]] | None = None,
    ocs_cognition_artifacts: list[dict[str, Any]] | None = None,
    replay_derived_intent_artifacts: list[dict[str, Any]] | None = None,
    domain_registry_context: list[dict[str, Any]] | None = None,
    replay_visible_operation_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build bounded OCS memory and continuity artifacts from explicit replay-visible inputs."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        sources = _normalize_sources(
            ocs_context_artifacts=ocs_context_artifacts or [],
            ocs_cognition_artifacts=ocs_cognition_artifacts or [],
            replay_derived_intent_artifacts=replay_derived_intent_artifacts or [],
            domain_registry_context=domain_registry_context or [],
            replay_visible_operation_history=replay_visible_operation_history or [],
        )
        memory = _memory_artifact(
            memory_continuity_id=memory_continuity_id,
            sources=sources,
            created_at=created_at,
            memory_status=OCS_MEMORY_AND_CONTINUITY_RECORDED,
            failure_reason=None,
        )
        continuity = _continuity_artifact(
            memory_continuity_id=memory_continuity_id,
            memory=memory,
            sources=sources,
            created_at=created_at,
            continuity_status=OCS_MEMORY_AND_CONTINUITY_RECORDED,
            failure_reason=None,
        )
        returned = _returned_artifact(memory, continuity)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], memory)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], continuity)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(memory, continuity, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        sources = _empty_sources()
        memory = _memory_artifact(
            memory_continuity_id=memory_continuity_id,
            sources=sources,
            created_at=created_at,
            memory_status=FAILED_CLOSED,
            failure_reason=failure_reason,
        )
        continuity = _continuity_artifact(
            memory_continuity_id=memory_continuity_id,
            memory=memory,
            sources=sources,
            created_at=created_at,
            continuity_status=FAILED_CLOSED,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(memory, continuity)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], memory)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], continuity)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(memory, continuity, returned, replay_path)


def reconstruct_ocs_memory_and_continuity_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS memory and continuity replay evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS memory and continuity replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS memory and continuity replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    memory = wrappers[0]["artifact"]
    continuity = wrappers[1]["artifact"]
    returned = wrappers[2]["artifact"]
    if memory.get("memory_hash") != _compute_memory_hash(memory):
        raise FailClosedRuntimeError("OCS memory hash mismatch")
    if continuity.get("continuity_hash") != _compute_continuity_hash(continuity):
        raise FailClosedRuntimeError("OCS continuity hash mismatch")
    if continuity.get("memory_reference") != memory["memory_id"]:
        raise FailClosedRuntimeError("OCS continuity memory reference mismatch")
    if continuity.get("memory_hash") != memory["memory_hash"]:
        raise FailClosedRuntimeError("OCS continuity memory hash mismatch")
    if returned.get("memory_reference") != memory["memory_id"]:
        raise FailClosedRuntimeError("OCS memory returned reference mismatch")
    if returned.get("continuity_reference") != continuity["continuity_id"]:
        raise FailClosedRuntimeError("OCS continuity returned reference mismatch")
    if returned.get("memory_artifact_hash") != memory["artifact_hash"]:
        raise FailClosedRuntimeError("OCS memory returned hash mismatch")
    if returned.get("continuity_artifact_hash") != continuity["artifact_hash"]:
        raise FailClosedRuntimeError("OCS continuity returned hash mismatch")
    return {
        "memory_continuity_id": memory["memory_continuity_id"],
        "memory_status": memory["memory_status"],
        "continuity_status": continuity["continuity_status"],
        "memory_summary": deepcopy(memory["memory_summary"]),
        "operation_groups": deepcopy(continuity["operation_groups"]),
        "domain_continuity": deepcopy(continuity["domain_continuity"]),
        "intent_continuity": deepcopy(continuity["intent_continuity"]),
        "context_linkage": deepcopy(continuity["context_linkage"]),
        "memory_hash": memory["memory_hash"],
        "continuity_hash": continuity["continuity_hash"],
        "authority_flags": deepcopy(memory["authority_flags"]),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _normalize_sources(
    *,
    ocs_context_artifacts: list[dict[str, Any]],
    ocs_cognition_artifacts: list[dict[str, Any]],
    replay_derived_intent_artifacts: list[dict[str, Any]],
    domain_registry_context: list[dict[str, Any]],
    replay_visible_operation_history: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    raw = {
        "ocs_context_artifacts": ocs_context_artifacts,
        "ocs_cognition_artifacts": ocs_cognition_artifacts,
        "replay_derived_intent_artifacts": replay_derived_intent_artifacts,
        "domain_registry_context": domain_registry_context,
        "replay_visible_operation_history": replay_visible_operation_history,
    }
    normalized: dict[str, list[dict[str, Any]]] = {}
    for category, entries in raw.items():
        if not isinstance(entries, list):
            raise FailClosedRuntimeError("OCS memory failed closed: source category must be a list")
        normalized[category] = sorted(
            [_normalize_source_item(category, index, entry) for index, entry in enumerate(entries)],
            key=lambda item: (item["operation_key"], item["domain_id"], item["source_id"], item["source_hash"]),
        )
    return normalized


def _normalize_source_item(category: str, index: int, entry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise FailClosedRuntimeError("OCS memory failed closed: source item must be a JSON object")
    artifact = deepcopy(entry)
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("OCS memory failed closed: source item is not replay-visible")
    _reject_prohibited_flags(artifact)
    if "artifact_hash" in artifact:
        _verify_artifact_hash(artifact)
    _validate_known_artifact(category, artifact)
    artifact_type = _optional_string(artifact.get("artifact_type")) or _optional_string(artifact.get("event_type")) or "UNKNOWN"
    source_id = _source_id(category, index, artifact)
    source_hash = _optional_string(artifact.get("artifact_hash")) or _optional_string(artifact.get("replay_hash")) or replay_hash(artifact)
    summary = _summary(artifact)
    domain_id = _domain_id(artifact, summary)
    operation_key = _operation_key(category, artifact, summary, domain_id)
    intent_keys = _intent_keys(artifact, summary)
    return {
        "category": category,
        "source_id": source_id,
        "artifact_type": artifact_type,
        "source_hash": source_hash,
        "domain_id": domain_id,
        "operation_key": operation_key,
        "intent_keys": intent_keys,
        "summary": summary,
        "replay_visible": True,
        "authority": False,
    }


def _validate_known_artifact(category: str, artifact: dict[str, Any]) -> None:
    artifact_type = artifact.get("artifact_type")
    if category == "ocs_context_artifacts":
        if artifact_type != OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1:
            raise FailClosedRuntimeError("OCS memory failed closed: invalid OCS context artifact")
        if artifact.get("context_status") != OCS_CONTEXT_ASSEMBLED:
            raise FailClosedRuntimeError("OCS memory failed closed: OCS context is not assembled")
    elif category == "ocs_cognition_artifacts":
        if artifact_type != OCS_COGNITION_ARTIFACT_V1:
            raise FailClosedRuntimeError("OCS memory failed closed: invalid OCS cognition artifact")
        if artifact.get("cognition_status") != OCS_COGNITION_COMPLETED:
            raise FailClosedRuntimeError("OCS memory failed closed: OCS cognition is not completed")
    elif category == "replay_derived_intent_artifacts":
        if artifact_type != OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1:
            raise FailClosedRuntimeError("OCS memory failed closed: invalid OCS replay-derived intent artifact")
        if artifact.get("intent_status") != OCS_REPLAY_DERIVED_INTENT_CREATED:
            raise FailClosedRuntimeError("OCS memory failed closed: OCS replay-derived intent is not created")


def _memory_artifact(
    *,
    memory_continuity_id: str,
    sources: dict[str, list[dict[str, Any]]],
    created_at: str,
    memory_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    memory_summary = _memory_summary(sources)
    artifact = {
        "artifact_type": OCS_MEMORY_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_MEMORY_AND_CONTINUITY_RUNTIME_VERSION,
        "memory_continuity_id": _require_string(memory_continuity_id, "memory_continuity_id"),
        "memory_id": f"{_require_string(memory_continuity_id, 'memory_continuity_id')}:MEMORY",
        "source_categories": sorted(sources),
        "normalized_sources": deepcopy(sources),
        "memory_summary": memory_summary,
        "memory_status": memory_status,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["memory_hash"] = _compute_memory_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _continuity_artifact(
    *,
    memory_continuity_id: str,
    memory: dict[str, Any],
    sources: dict[str, list[dict[str, Any]]],
    created_at: str,
    continuity_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_CONTINUITY_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_MEMORY_AND_CONTINUITY_RUNTIME_VERSION,
        "memory_continuity_id": _require_string(memory_continuity_id, "memory_continuity_id"),
        "continuity_id": f"{_require_string(memory_continuity_id, 'memory_continuity_id')}:CONTINUITY",
        "memory_reference": memory["memory_id"],
        "memory_hash": memory["memory_hash"],
        "context_linkage": _context_linkage(sources),
        "operation_groups": _operation_groups(sources),
        "domain_continuity": _domain_continuity(sources),
        "intent_continuity": _intent_continuity(sources),
        "continuity_status": continuity_status,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["continuity_hash"] = _compute_continuity_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _memory_summary(sources: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    all_sources = _all_sources(sources)
    domains = sorted({source["domain_id"] for source in all_sources if source["domain_id"] != "UNKNOWN"})
    intent_keys = sorted({intent for source in all_sources for intent in source["intent_keys"]})
    operation_keys = sorted({source["operation_key"] for source in all_sources})
    return {
        "source_count": len(all_sources),
        "context_count": len(sources["ocs_context_artifacts"]),
        "cognition_count": len(sources["ocs_cognition_artifacts"]),
        "replay_derived_intent_count": len(sources["replay_derived_intent_artifacts"]),
        "domain_registry_count": len(sources["domain_registry_context"]),
        "operation_history_count": len(sources["replay_visible_operation_history"]),
        "domain_count": len(domains),
        "domains": domains,
        "intent_count": len(intent_keys),
        "intent_keys": intent_keys,
        "operation_group_count": len(operation_keys),
        "memory_summary_text": (
            f"{len(all_sources)} replay-visible OCS sources across {len(domains)} domains "
            f"and {len(operation_keys)} operation groups."
        ),
        "authority": False,
    }


def _context_linkage(sources: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    links = []
    for source in sources["ocs_context_artifacts"]:
        links.append(
            {
                "context_source_id": source["source_id"],
                "context_hash": source["summary"].get("context_hash"),
                "domain_id": source["domain_id"],
                "operation_key": source["operation_key"],
                "source_hash": source["source_hash"],
                "authority": False,
            }
        )
    return sorted(links, key=lambda item: (item["operation_key"], item["context_source_id"], item["source_hash"]))


def _operation_groups(sources: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for source in _all_sources(sources):
        groups.setdefault(source["operation_key"], []).append(source)
    return [
        {
            "operation_key": key,
            "source_count": len(items),
            "domains": sorted({item["domain_id"] for item in items if item["domain_id"] != "UNKNOWN"}),
            "source_references": _source_refs(items),
            "authority": False,
        }
        for key, items in sorted(groups.items())
    ]


def _domain_continuity(sources: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for source in _all_sources(sources):
        groups.setdefault(source["domain_id"], []).append(source)
    return [
        {
            "domain_id": domain,
            "source_count": len(items),
            "operation_keys": sorted({item["operation_key"] for item in items}),
            "intent_keys": sorted({intent for item in items for intent in item["intent_keys"]}),
            "source_references": _source_refs(items),
            "authority": False,
        }
        for domain, items in sorted(groups.items())
    ]


def _intent_continuity(sources: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for source in _all_sources(sources):
        for intent in source["intent_keys"]:
            groups.setdefault(intent, []).append(source)
    return [
        {
            "intent_key": intent,
            "source_count": len(items),
            "domains": sorted({item["domain_id"] for item in items if item["domain_id"] != "UNKNOWN"}),
            "operation_keys": sorted({item["operation_key"] for item in items}),
            "source_references": _source_refs(items),
            "authority": False,
        }
        for intent, items in sorted(groups.items())
    ]


def _returned_artifact(memory: dict[str, Any], continuity: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(memory)
    _verify_artifact_hash(continuity)
    returned = {
        "event_type": "OCS_MEMORY_AND_CONTINUITY_RETURNED",
        "memory_reference": memory["memory_id"],
        "memory_artifact_hash": memory["artifact_hash"],
        "memory_hash": memory["memory_hash"],
        "continuity_reference": continuity["continuity_id"],
        "continuity_artifact_hash": continuity["artifact_hash"],
        "continuity_hash": continuity["continuity_hash"],
        "memory_status": memory["memory_status"],
        "continuity_status": continuity["continuity_status"],
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": memory["failure_reason"] or continuity["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(memory: dict[str, Any], continuity: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_memory_artifact": deepcopy(memory),
        "ocs_continuity_artifact": deepcopy(continuity),
        "ocs_memory_and_continuity_returned": deepcopy(returned),
        "ocs_memory_and_continuity_replay_reference": str(replay_path),
        "memory_status": memory["memory_status"],
        "continuity_status": continuity["continuity_status"],
        "memory_hash": memory["memory_hash"],
        "continuity_hash": continuity["continuity_hash"],
        "memory_summary": deepcopy(memory["memory_summary"]),
        "operation_groups": deepcopy(continuity["operation_groups"]),
        "domain_continuity": deepcopy(continuity["domain_continuity"]),
        "intent_continuity": deepcopy(continuity["intent_continuity"]),
        "fail_closed": memory["memory_status"] != OCS_MEMORY_AND_CONTINUITY_RECORDED
        or continuity["continuity_status"] != OCS_MEMORY_AND_CONTINUITY_RECORDED,
        "failure_reason": memory["failure_reason"] or continuity["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
    }
    capture["ocs_memory_and_continuity_capture_hash"] = replay_hash(capture)
    return capture


def _compute_memory_hash(memory: dict[str, Any]) -> str:
    return replay_hash(
        {
            "source_categories": memory["source_categories"],
            "normalized_sources": memory["normalized_sources"],
            "memory_summary": memory["memory_summary"],
            "memory_status": memory["memory_status"],
            "authority_flags": memory["authority_flags"],
            "failure_reason": memory["failure_reason"],
        }
    )


def _compute_continuity_hash(continuity: dict[str, Any]) -> str:
    return replay_hash(
        {
            "memory_hash": continuity["memory_hash"],
            "context_linkage": continuity["context_linkage"],
            "operation_groups": continuity["operation_groups"],
            "domain_continuity": continuity["domain_continuity"],
            "intent_continuity": continuity["intent_continuity"],
            "continuity_status": continuity["continuity_status"],
            "authority_flags": continuity["authority_flags"],
            "failure_reason": continuity["failure_reason"],
        }
    )


def _summary(artifact: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "artifact_type",
        "event_type",
        "context_assembly_id",
        "context_hash",
        "cognition_id",
        "cognition_hash",
        "intent_generation_id",
        "intent_hash",
        "operation_id",
        "canonical_chain_id",
        "chain_id",
        "domain_id",
        "requested_domain",
        "bundle_id",
        "task_intent",
        "provider_necessity",
        "improvement_candidates",
        "candidate_count",
        "status",
        "validation_status",
        "failure_reason",
        "decision_status",
    )
    return {field: deepcopy(artifact[field]) for field in fields if field in artifact}


def _domain_id(artifact: dict[str, Any], summary: dict[str, Any]) -> str:
    for field in ("domain_id", "requested_domain"):
        value = summary.get(field) or artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip().upper().replace(" ", "_").replace("-", "_")
    candidates = artifact.get("domain_candidates")
    if isinstance(candidates, list) and len(candidates) == 1 and isinstance(candidates[0], dict):
        value = candidates[0].get("domain_id")
        if isinstance(value, str) and value.strip():
            return value.strip().upper()
    bundle_id = summary.get("bundle_id")
    if isinstance(bundle_id, str) and bundle_id.strip():
        return bundle_id.split("_", 1)[0].upper()
    return "UNKNOWN"


def _operation_key(category: str, artifact: dict[str, Any], summary: dict[str, Any], domain_id: str) -> str:
    for field in ("operation_id", "canonical_chain_id", "chain_id", "source_chain_id"):
        value = summary.get(field) or artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for field in ("source_context_assembly_id", "context_assembly_id", "source_cognition_id", "cognition_id"):
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"{category}:{domain_id}"


def _intent_keys(artifact: dict[str, Any], summary: dict[str, Any]) -> list[str]:
    keys: set[str] = set()
    task_intent = artifact.get("task_intent") or summary.get("task_intent")
    if isinstance(task_intent, dict) and isinstance(task_intent.get("intent"), str):
        keys.add(task_intent["intent"])
    provider = artifact.get("provider_necessity") or summary.get("provider_necessity")
    if isinstance(provider, dict) and isinstance(provider.get("necessity_classification"), str):
        keys.add(f"PROVIDER:{provider['necessity_classification']}")
    for candidate in artifact.get("improvement_candidates", []):
        if isinstance(candidate, dict):
            value = candidate.get("candidate_type")
            if isinstance(value, str):
                keys.add(value)
    status = summary.get("status") or summary.get("validation_status") or summary.get("decision_status")
    if isinstance(status, str) and status.strip():
        keys.add(status.strip().upper())
    return sorted(keys) or ["UNCLASSIFIED"]


def _source_id(category: str, index: int, artifact: dict[str, Any]) -> str:
    for field in (
        "artifact_id",
        "context_assembly_id",
        "cognition_id",
        "intent_generation_id",
        "operation_id",
        "canonical_chain_id",
        "chain_id",
        "resolution_id",
        "source_id",
    ):
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"{category}:ITEM-{index:06d}"


def _source_refs(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "category": item["category"],
                "source_id": item["source_id"],
                "source_hash": item["source_hash"],
            }
            for item in items
        ],
        key=lambda item: (item["category"], item["source_id"], item["source_hash"]),
    )


def _all_sources(sources: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [source for category in sorted(sources) for source in sources[category]]


def _empty_sources() -> dict[str, list[dict[str, Any]]]:
    return {
        "ocs_context_artifacts": [],
        "ocs_cognition_artifacts": [],
        "replay_derived_intent_artifacts": [],
        "domain_registry_context": [],
        "replay_visible_operation_history": [],
    }


def _reject_prohibited_flags(artifact: dict[str, Any]) -> None:
    for flag in PROHIBITED_FLAGS:
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS memory failed closed: source item carries prohibited flag {flag}")
    authority_flags = artifact.get("authority_flags")
    if isinstance(authority_flags, dict):
        for flag in AUTHORITY_FLAGS:
            if authority_flags.get(flag) is True:
                raise FailClosedRuntimeError(f"OCS memory failed closed: source item carries prohibited authority flag {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS memory and continuity replay step ordering mismatch")
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
        raise FailClosedRuntimeError("OCS memory artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS memory artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS memory replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS memory replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS memory and continuity failed closed"
