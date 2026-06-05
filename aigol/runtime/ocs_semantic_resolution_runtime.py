"""Deterministic semantic resolution over bounded OCS memory for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import OCS_COGNITION_ARTIFACT_V1, OCS_COGNITION_COMPLETED
from aigol.runtime.ocs_memory_and_continuity_runtime import (
    OCS_CONTINUITY_ARTIFACT_V1,
    OCS_MEMORY_AND_CONTINUITY_RECORDED,
    OCS_MEMORY_ARTIFACT_V1,
)
from aigol.runtime.ocs_replay_derived_intent_runtime import (
    OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1,
    OCS_REPLAY_DERIVED_INTENT_CREATED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_SEMANTIC_RESOLUTION_RUNTIME_VERSION = "AIGOL_OCS_SEMANTIC_RESOLUTION_RUNTIME_V1"
OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1 = "OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1"
OCS_SEMANTIC_RESOLUTION_COMPLETED = "OCS_SEMANTIC_RESOLUTION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_semantic_resolution_recorded",
    "ocs_semantic_resolution_returned",
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


def resolve_ocs_semantics(
    *,
    semantic_resolution_id: str,
    ocs_memory_artifact: dict[str, Any],
    ocs_continuity_artifact: dict[str, Any],
    ocs_cognition_artifact: dict[str, Any],
    replay_derived_intent_artifact: dict[str, Any],
    domain_registry_context: list[dict[str, Any]] | None,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Resolve OCS semantic references without creating authority."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        memory = deepcopy(ocs_memory_artifact)
        continuity = deepcopy(ocs_continuity_artifact)
        cognition = deepcopy(ocs_cognition_artifact)
        intent = deepcopy(replay_derived_intent_artifact)
        registry = _normalize_registry_context(domain_registry_context or [])
        _validate_inputs(memory, continuity, cognition, intent)
        resolution = _resolution_payload(memory, continuity, cognition, intent, registry)
        artifact = _semantic_artifact(
            semantic_resolution_id=semantic_resolution_id,
            memory=memory,
            continuity=continuity,
            cognition=cognition,
            intent=intent,
            registry=registry,
            resolution=resolution,
            created_at=created_at,
            resolution_status=OCS_SEMANTIC_RESOLUTION_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        artifact = _failed_semantic_artifact(
            semantic_resolution_id=semantic_resolution_id,
            memory=ocs_memory_artifact if isinstance(ocs_memory_artifact, dict) else {},
            continuity=ocs_continuity_artifact if isinstance(ocs_continuity_artifact, dict) else {},
            cognition=ocs_cognition_artifact if isinstance(ocs_cognition_artifact, dict) else {},
            intent=replay_derived_intent_artifact if isinstance(replay_derived_intent_artifact, dict) else {},
            created_at=created_at,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_ocs_semantic_resolution_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS semantic resolution evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS semantic resolution replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS semantic resolution replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    recorded = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("semantic_resolution_reference") != recorded["semantic_resolution_id"]:
        raise FailClosedRuntimeError("OCS semantic resolution returned reference mismatch")
    if returned.get("semantic_resolution_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("OCS semantic resolution returned hash mismatch")
    if recorded.get("semantic_hash") != _compute_semantic_hash(recorded):
        raise FailClosedRuntimeError("OCS semantic hash mismatch")
    return {
        "semantic_resolution_id": recorded["semantic_resolution_id"],
        "resolution_status": recorded["resolution_status"],
        "source_memory_hash": recorded["source_memory_hash"],
        "source_continuity_hash": recorded["source_continuity_hash"],
        "semantic_reference_resolution": deepcopy(recorded["semantic_reference_resolution"]),
        "domain_identity_resolution": deepcopy(recorded["domain_identity_resolution"]),
        "capability_identity_resolution": deepcopy(recorded["capability_identity_resolution"]),
        "worker_identity_resolution": deepcopy(recorded["worker_identity_resolution"]),
        "continuity_reference_linking": deepcopy(recorded["continuity_reference_linking"]),
        "ambiguity_detection": deepcopy(recorded["ambiguity_detection"]),
        "clarification_candidates": deepcopy(recorded["clarification_candidates"]),
        "semantic_hash": recorded["semantic_hash"],
        "authority_flags": deepcopy(recorded["authority_flags"]),
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


def _validate_inputs(memory: dict[str, Any], continuity: dict[str, Any], cognition: dict[str, Any], intent: dict[str, Any]) -> None:
    _validate_artifact(memory, OCS_MEMORY_ARTIFACT_V1, "memory")
    _validate_artifact(continuity, OCS_CONTINUITY_ARTIFACT_V1, "continuity")
    _validate_artifact(cognition, OCS_COGNITION_ARTIFACT_V1, "cognition")
    _validate_artifact(intent, OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1, "replay-derived intent")
    if memory.get("memory_status") != OCS_MEMORY_AND_CONTINUITY_RECORDED:
        raise FailClosedRuntimeError("OCS semantic resolution failed closed: memory not recorded")
    if continuity.get("continuity_status") != OCS_MEMORY_AND_CONTINUITY_RECORDED:
        raise FailClosedRuntimeError("OCS semantic resolution failed closed: continuity not recorded")
    if cognition.get("cognition_status") != OCS_COGNITION_COMPLETED:
        raise FailClosedRuntimeError("OCS semantic resolution failed closed: cognition not completed")
    if intent.get("intent_status") != OCS_REPLAY_DERIVED_INTENT_CREATED:
        raise FailClosedRuntimeError("OCS semantic resolution failed closed: replay-derived intent not created")
    if continuity.get("memory_hash") != memory.get("memory_hash"):
        raise FailClosedRuntimeError("OCS semantic resolution failed closed: memory continuity hash mismatch")
    _reject_prohibited_flags(memory)
    _reject_prohibited_flags(continuity)
    _reject_prohibited_flags(cognition)
    _reject_prohibited_flags(intent)


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"OCS semantic resolution failed closed: invalid {label} artifact")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError(f"OCS semantic resolution failed closed: {label} artifact is not replay-visible")
    _verify_artifact_hash(artifact)


def _normalize_registry_context(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(entries, list):
        raise FailClosedRuntimeError("OCS semantic resolution failed closed: domain registry context must be a list")
    normalized = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise FailClosedRuntimeError("OCS semantic resolution failed closed: registry entry must be a JSON object")
        artifact = deepcopy(entry)
        if artifact.get("replay_visible") is not True:
            raise FailClosedRuntimeError("OCS semantic resolution failed closed: registry entry is not replay-visible")
        _reject_prohibited_flags(artifact)
        if "artifact_hash" in artifact:
            _verify_artifact_hash(artifact)
        domain = _normalize_identity(artifact.get("domain_id") or artifact.get("requested_domain") or artifact.get("display_name"))
        bundle = _optional_string(artifact.get("bundle_id"))
        source_id = _optional_string(artifact.get("artifact_id")) or _optional_string(artifact.get("resolution_id")) or f"REGISTRY-{index:06d}"
        source_hash = _optional_string(artifact.get("artifact_hash")) or replay_hash(artifact)
        normalized.append(
            {
                "source_id": source_id,
                "source_hash": source_hash,
                "domain_id": domain or "UNKNOWN",
                "bundle_id": bundle,
                "artifact_type": _optional_string(artifact.get("artifact_type")) or "DOMAIN_REGISTRY_CONTEXT",
                "replay_visible": True,
                "authority": False,
            }
        )
    return sorted(normalized, key=lambda item: (item["domain_id"], item["source_id"], item["source_hash"]))


def _resolution_payload(
    memory: dict[str, Any],
    continuity: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    registry: list[dict[str, Any]],
) -> dict[str, Any]:
    semantic_refs = _semantic_references(memory, continuity, cognition, intent, registry)
    domains = _domain_resolution(memory, continuity, cognition, registry, semantic_refs)
    capabilities = _capability_resolution(memory, continuity, cognition, intent)
    workers = _worker_resolution(cognition, memory, continuity)
    links = _continuity_links(continuity, semantic_refs)
    ambiguity = _ambiguity(domains, capabilities, workers, semantic_refs)
    clarification = _clarification_candidates(ambiguity)
    return {
        "semantic_reference_resolution": semantic_refs,
        "domain_identity_resolution": domains,
        "capability_identity_resolution": capabilities,
        "worker_identity_resolution": workers,
        "continuity_reference_linking": links,
        "ambiguity_detection": ambiguity,
        "clarification_candidates": clarification,
    }


def _semantic_references(
    memory: dict[str, Any],
    continuity: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    registry: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for domain in memory.get("memory_summary", {}).get("domains", []):
        refs.append(_semantic_ref("DOMAIN", domain, "memory_summary", memory["memory_hash"]))
    for item in continuity.get("domain_continuity", []):
        if _normalize_identity(item.get("domain_id")) != "UNKNOWN":
            refs.append(_semantic_ref("DOMAIN", item.get("domain_id"), "domain_continuity", continuity["continuity_hash"]))
    for candidate in cognition.get("domain_candidates", []):
        refs.append(_semantic_ref("DOMAIN", candidate.get("domain_id"), "cognition_domain_candidate", cognition["cognition_hash"]))
    for candidate in cognition.get("worker_candidates", []):
        refs.append(_semantic_ref("WORKER", candidate.get("worker_family_id"), "cognition_worker_candidate", cognition["cognition_hash"]))
    for candidate in intent.get("improvement_candidates", []):
        refs.append(_semantic_ref("CAPABILITY", candidate.get("candidate_type"), "replay_derived_intent_candidate", intent["intent_hash"]))
    for item in registry:
        refs.append(_semantic_ref("DOMAIN", item.get("domain_id"), "domain_registry_context", item["source_hash"]))
    dedup: dict[tuple[str, str, str], dict[str, Any]] = {}
    for ref in refs:
        key = (ref["reference_type"], ref["canonical_id"], ref["source_kind"])
        dedup.setdefault(key, ref)
    return sorted(dedup.values(), key=lambda item: (item["reference_type"], item["canonical_id"], item["source_kind"]))


def _semantic_ref(reference_type: str, value: Any, source_kind: str, source_hash: str) -> dict[str, Any]:
    canonical = _normalize_identity(value) or "UNKNOWN"
    return {
        "reference_type": reference_type,
        "canonical_id": canonical,
        "source_kind": source_kind,
        "source_hash": source_hash,
        "resolved": canonical != "UNKNOWN",
        "authority": False,
    }


def _domain_resolution(
    memory: dict[str, Any],
    continuity: dict[str, Any],
    cognition: dict[str, Any],
    registry: list[dict[str, Any]],
    semantic_refs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    domains: dict[str, set[str]] = {}
    for domain in memory.get("memory_summary", {}).get("domains", []):
        domains.setdefault(_normalize_identity(domain) or "UNKNOWN", set()).add("memory_summary")
    for item in continuity.get("domain_continuity", []):
        domain = _normalize_identity(item.get("domain_id"))
        if domain and domain != "UNKNOWN":
            domains.setdefault(domain, set()).add("domain_continuity")
    for candidate in cognition.get("domain_candidates", []):
        domains.setdefault(_normalize_identity(candidate.get("domain_id")) or "UNKNOWN", set()).add("cognition")
    for item in registry:
        domains.setdefault(_normalize_identity(item.get("domain_id")) or "UNKNOWN", set()).add("registry")
    for ref in semantic_refs:
        if ref["reference_type"] == "DOMAIN":
            domains.setdefault(ref["canonical_id"], set()).add("semantic_reference")
    return [
        {
            "domain_id": domain,
            "resolution_status": "RESOLVED" if domain != "UNKNOWN" else "UNRESOLVED",
            "evidence": sorted(evidence),
            "authority": False,
        }
        for domain, evidence in sorted(domains.items())
    ]


def _capability_resolution(
    memory: dict[str, Any],
    continuity: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
) -> list[dict[str, Any]]:
    capabilities: dict[str, set[str]] = {}
    for key in memory.get("memory_summary", {}).get("intent_keys", []):
        capabilities.setdefault(_normalize_identity(key) or "UNKNOWN", set()).add("memory_intent_key")
    for item in continuity.get("intent_continuity", []):
        capabilities.setdefault(_normalize_identity(item.get("intent_key")) or "UNKNOWN", set()).add("intent_continuity")
    provider = cognition.get("provider_necessity", {}).get("necessity_classification")
    if isinstance(provider, str):
        capabilities.setdefault(f"PROVIDER_{provider}", set()).add("provider_necessity")
    for candidate in intent.get("improvement_candidates", []):
        value = candidate.get("candidate_type")
        if isinstance(value, str):
            capabilities.setdefault(_normalize_identity(value) or "UNKNOWN", set()).add("improvement_candidate")
    return [
        {
            "capability_id": capability,
            "resolution_status": "RESOLVED" if capability != "UNKNOWN" else "UNRESOLVED",
            "evidence": sorted(evidence),
            "authority": False,
        }
        for capability, evidence in sorted(capabilities.items())
    ]


def _worker_resolution(cognition: dict[str, Any], memory: dict[str, Any], continuity: dict[str, Any]) -> list[dict[str, Any]]:
    workers: dict[str, set[str]] = {}
    for candidate in cognition.get("worker_candidates", []):
        workers.setdefault(_normalize_identity(candidate.get("worker_family_id")) or "UNKNOWN", set()).add("cognition")
    for source in memory.get("normalized_sources", {}).get("replay_visible_operation_history", []):
        value = source.get("summary", {}).get("worker_family_id")
        if isinstance(value, str):
            workers.setdefault(_normalize_identity(value) or "UNKNOWN", set()).add("operation_history")
    for item in continuity.get("intent_continuity", []):
        intent = _normalize_identity(item.get("intent_key"))
        if intent and any(token in intent for token in ("WORKER", "MARKET_EVIDENCE", "STRATEGY", "RISK", "PORTFOLIO")):
            workers.setdefault(intent, set()).add("intent_continuity")
    return [
        {
            "worker_id": worker,
            "resolution_status": "RESOLVED" if worker != "UNKNOWN" else "UNRESOLVED",
            "evidence": sorted(evidence),
            "authority": False,
        }
        for worker, evidence in sorted(workers.items())
    ]


def _continuity_links(continuity: dict[str, Any], semantic_refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    links = []
    domain_ids = {ref["canonical_id"] for ref in semantic_refs if ref["reference_type"] == "DOMAIN" and ref["resolved"]}
    for group in continuity.get("operation_groups", []):
        linked_domains = sorted(set(group.get("domains", [])) & domain_ids)
        links.append(
            {
                "operation_key": group.get("operation_key"),
                "linked_domains": linked_domains,
                "source_count": group.get("source_count"),
                "source_references": deepcopy(group.get("source_references", [])),
                "authority": False,
            }
        )
    return sorted(links, key=lambda item: (str(item["operation_key"]), item["source_count"] or 0))


def _ambiguity(domains: list[dict[str, Any]], capabilities: list[dict[str, Any]], workers: list[dict[str, Any]], refs: list[dict[str, Any]]) -> dict[str, Any]:
    reasons = []
    resolved_domains = [item["domain_id"] for item in domains if item["resolution_status"] == "RESOLVED"]
    resolved_workers = [item["worker_id"] for item in workers if item["resolution_status"] == "RESOLVED"]
    unresolved_refs = [ref for ref in refs if ref["resolved"] is False]
    if len(resolved_domains) > 1:
        reasons.append("multiple domain identities resolved")
    if len(resolved_workers) > 1:
        reasons.append("multiple worker identities resolved")
    if any(item["resolution_status"] == "UNRESOLVED" for item in capabilities):
        reasons.append("unresolved capability identity")
    if unresolved_refs:
        reasons.append("unresolved semantic references")
    return {
        "is_ambiguous": bool(reasons),
        "ambiguity_reasons": sorted(reasons),
        "unresolved_reference_count": len(unresolved_refs),
        "authority": False,
    }


def _clarification_candidates(ambiguity: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "clarification_id": reason.upper().replace(" ", "_"),
            "reason": reason,
            "required": True,
            "authority": False,
        }
        for reason in ambiguity["ambiguity_reasons"]
    ]


def _semantic_artifact(
    *,
    semantic_resolution_id: str,
    memory: dict[str, Any],
    continuity: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    registry: list[dict[str, Any]],
    resolution: dict[str, Any],
    created_at: str,
    resolution_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_SEMANTIC_RESOLUTION_RUNTIME_VERSION,
        "semantic_resolution_id": _require_string(semantic_resolution_id, "semantic_resolution_id"),
        "source_memory_id": memory["memory_id"],
        "source_memory_artifact_hash": memory["artifact_hash"],
        "source_memory_hash": memory["memory_hash"],
        "source_continuity_id": continuity["continuity_id"],
        "source_continuity_artifact_hash": continuity["artifact_hash"],
        "source_continuity_hash": continuity["continuity_hash"],
        "source_cognition_id": cognition["cognition_id"],
        "source_cognition_hash": cognition["cognition_hash"],
        "source_intent_generation_id": intent["intent_generation_id"],
        "source_intent_hash": intent["intent_hash"],
        "domain_registry_context": deepcopy(registry),
        **deepcopy(resolution),
        "resolution_status": resolution_status,
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
    artifact["semantic_hash"] = _compute_semantic_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_semantic_artifact(
    *,
    semantic_resolution_id: str,
    memory: dict[str, Any],
    continuity: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    safe_memory = {
        "memory_id": memory.get("memory_id", "INVALID_MEMORY_ID"),
        "artifact_hash": memory.get("artifact_hash", "INVALID_MEMORY_ARTIFACT_HASH"),
        "memory_hash": memory.get("memory_hash", "INVALID_MEMORY_HASH"),
    }
    safe_continuity = {
        "continuity_id": continuity.get("continuity_id", "INVALID_CONTINUITY_ID"),
        "artifact_hash": continuity.get("artifact_hash", "INVALID_CONTINUITY_ARTIFACT_HASH"),
        "continuity_hash": continuity.get("continuity_hash", "INVALID_CONTINUITY_HASH"),
    }
    safe_cognition = {
        "cognition_id": cognition.get("cognition_id", "INVALID_COGNITION_ID"),
        "cognition_hash": cognition.get("cognition_hash", "INVALID_COGNITION_HASH"),
    }
    safe_intent = {
        "intent_generation_id": intent.get("intent_generation_id", "INVALID_INTENT_GENERATION_ID"),
        "intent_hash": intent.get("intent_hash", "INVALID_INTENT_HASH"),
    }
    empty_resolution = {
        "semantic_reference_resolution": [],
        "domain_identity_resolution": [],
        "capability_identity_resolution": [],
        "worker_identity_resolution": [],
        "continuity_reference_linking": [],
        "ambiguity_detection": {
            "is_ambiguous": True,
            "ambiguity_reasons": ["OCS semantic resolution failed closed"],
            "unresolved_reference_count": 0,
            "authority": False,
        },
        "clarification_candidates": [
            {
                "clarification_id": "OCS_SEMANTIC_RESOLUTION_FAILED_CLOSED",
                "reason": failure_reason,
                "required": True,
                "authority": False,
            }
        ],
    }
    return _semantic_artifact(
        semantic_resolution_id=semantic_resolution_id,
        memory=safe_memory,
        continuity=safe_continuity,
        cognition=safe_cognition,
        intent=safe_intent,
        registry=[],
        resolution=empty_resolution,
        created_at=created_at,
        resolution_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact)
    returned = {
        "event_type": "OCS_SEMANTIC_RESOLUTION_RETURNED",
        "semantic_resolution_reference": artifact["semantic_resolution_id"],
        "semantic_resolution_hash": artifact["artifact_hash"],
        "resolution_status": artifact["resolution_status"],
        "semantic_hash": artifact["semantic_hash"],
        "ambiguity_detected": artifact["ambiguity_detection"]["is_ambiguous"],
        "clarification_candidate_count": len(artifact["clarification_candidates"]),
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": artifact["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_semantic_resolution_artifact": deepcopy(artifact),
        "ocs_semantic_resolution_returned": deepcopy(returned),
        "ocs_semantic_resolution_replay_reference": str(replay_path),
        "resolution_status": artifact["resolution_status"],
        "semantic_hash": artifact["semantic_hash"],
        "semantic_reference_resolution": deepcopy(artifact["semantic_reference_resolution"]),
        "domain_identity_resolution": deepcopy(artifact["domain_identity_resolution"]),
        "capability_identity_resolution": deepcopy(artifact["capability_identity_resolution"]),
        "worker_identity_resolution": deepcopy(artifact["worker_identity_resolution"]),
        "continuity_reference_linking": deepcopy(artifact["continuity_reference_linking"]),
        "ambiguity_detection": deepcopy(artifact["ambiguity_detection"]),
        "clarification_candidates": deepcopy(artifact["clarification_candidates"]),
        "fail_closed": artifact["resolution_status"] != OCS_SEMANTIC_RESOLUTION_COMPLETED,
        "failure_reason": artifact["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
    }
    capture["ocs_semantic_resolution_capture_hash"] = replay_hash(capture)
    return capture


def _compute_semantic_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "source_memory_hash": artifact["source_memory_hash"],
            "source_continuity_hash": artifact["source_continuity_hash"],
            "source_cognition_hash": artifact["source_cognition_hash"],
            "source_intent_hash": artifact["source_intent_hash"],
            "domain_registry_context": artifact["domain_registry_context"],
            "semantic_reference_resolution": artifact["semantic_reference_resolution"],
            "domain_identity_resolution": artifact["domain_identity_resolution"],
            "capability_identity_resolution": artifact["capability_identity_resolution"],
            "worker_identity_resolution": artifact["worker_identity_resolution"],
            "continuity_reference_linking": artifact["continuity_reference_linking"],
            "ambiguity_detection": artifact["ambiguity_detection"],
            "clarification_candidates": artifact["clarification_candidates"],
            "resolution_status": artifact["resolution_status"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _normalize_identity(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip().upper().replace(" ", "_").replace("-", "_")


def _reject_prohibited_flags(artifact: dict[str, Any]) -> None:
    for flag in PROHIBITED_FLAGS:
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS semantic resolution failed closed: source carries prohibited flag {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        for flag in AUTHORITY_FLAGS:
            if flags.get(flag) is True:
                raise FailClosedRuntimeError(f"OCS semantic resolution failed closed: source carries prohibited authority flag {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS semantic resolution replay step ordering mismatch")
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
        raise FailClosedRuntimeError("OCS semantic resolution artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS semantic resolution artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS semantic resolution replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS semantic resolution replay hash mismatch")


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
    return "OCS semantic resolution failed closed"
