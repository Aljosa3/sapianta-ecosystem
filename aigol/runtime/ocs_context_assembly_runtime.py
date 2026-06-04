"""Bounded OCS context assembly runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_CONTEXT_ASSEMBLY_RUNTIME_VERSION = "AIGOL_OCS_CONTEXT_ASSEMBLY_RUNTIME_V1"
OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1 = "OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1"
OCS_CONTEXT_ASSEMBLED = "OCS_CONTEXT_ASSEMBLED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_context_assembly_recorded",
    "ocs_context_assembly_returned",
)

CONTEXT_CATEGORIES = (
    "conversation_context",
    "clarification_context",
    "ppp_context",
    "approval_context",
    "replay_visible_operation_context",
    "domain_context",
    "registry_context",
)

PROHIBITED_AUTHORITY_FLAGS = (
    "authority",
    "authorizes_execution",
    "authorizes_dispatch",
    "authorizes_worker_invocation",
    "authorizes_provider_invocation",
    "authorizes_governance_mutation",
    "authorizes_replay_mutation",
    "execution_authorized",
    "execution_requested",
    "dispatch_requested",
    "worker_assignment_requested",
    "worker_dispatch_requested",
    "worker_invocation_requested",
    "governance_modified",
    "replay_modified",
    "approval_inferred",
    "domain_creation_authorized",
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
}


def assemble_ocs_context(
    *,
    context_assembly_id: str,
    created_at: str,
    replay_dir: str | Path,
    source_context: dict[str, Any],
    source_chain_id: str | None = None,
    source_request_reference: str | None = None,
) -> dict[str, Any]:
    """Assemble deterministic, replay-visible OCS context evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        normalized = _normalize_source_context(source_context)
        context_artifact = _context_artifact(
            context_assembly_id=context_assembly_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            source_chain_id=source_chain_id,
            source_request_reference=source_request_reference,
            normalized=normalized,
            context_status=OCS_CONTEXT_ASSEMBLED,
            failure_reason=None,
        )
        returned = _returned_artifact(context_artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], context_artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(context_artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        context_artifact = _context_artifact(
            context_assembly_id=context_assembly_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            source_chain_id=source_chain_id,
            source_request_reference=source_request_reference,
            normalized=_empty_normalized_context(),
            context_status=FAILED_CLOSED,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(context_artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], context_artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(context_artifact, returned, replay_path)


def reconstruct_ocs_context_assembly_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS context assembly replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        wrapper = load_json(path)
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS context assembly replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS context assembly replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    recorded = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("context_assembly_reference") != recorded["context_assembly_id"]:
        raise FailClosedRuntimeError("OCS context assembly replay reference mismatch")
    if returned.get("context_assembly_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("OCS context assembly replay hash mismatch")
    if recorded.get("context_hash") != _compute_context_hash(recorded):
        raise FailClosedRuntimeError("OCS context assembly context hash mismatch")
    return {
        "context_assembly_id": recorded["context_assembly_id"],
        "context_status": recorded["context_status"],
        "source_chain_id": recorded.get("source_chain_id"),
        "source_request_reference": recorded.get("source_request_reference"),
        "accepted_input_count": recorded["accepted_input_count"],
        "deduplicated_input_count": recorded["deduplicated_input_count"],
        "rejected_input_count": recorded["rejected_input_count"],
        "context_sections": deepcopy(recorded["context_sections"]),
        "accepted_inputs": deepcopy(recorded["accepted_inputs"]),
        "rejected_inputs": deepcopy(recorded["rejected_inputs"]),
        "known_gaps": deepcopy(recorded["known_gaps"]),
        "context_hash": recorded["context_hash"],
        "authority_flags": deepcopy(recorded["authority_flags"]),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _normalize_source_context(source_context: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(source_context, dict):
        raise FailClosedRuntimeError("OCS context assembly failed closed: source context must be a JSON object")

    accepted_inputs: list[dict[str, Any]] = []
    rejected_inputs: list[dict[str, Any]] = []
    section_sources: dict[str, list[dict[str, Any]]] = {category: [] for category in CONTEXT_CATEGORIES}
    seen_fingerprints: set[str] = set()

    for category in CONTEXT_CATEGORIES:
        raw_items = source_context.get(category, [])
        if raw_items is None:
            raw_items = []
        if isinstance(raw_items, dict):
            raw_items = [raw_items]
        if not isinstance(raw_items, list):
            raise FailClosedRuntimeError("OCS context assembly failed closed: category value must be a list or object")
        for position, item in enumerate(raw_items):
            normalized = _normalize_item(category, position, item)
            fingerprint = normalized["source_fingerprint"]
            if fingerprint in seen_fingerprints:
                normalized["dedupe_status"] = "DUPLICATE_SUPPRESSED"
                rejected_inputs.append(
                    _rejected_input(
                        category,
                        normalized["source_id"],
                        "duplicate source suppressed during deterministic OCS context assembly",
                    )
                )
                continue
            seen_fingerprints.add(fingerprint)
            accepted_inputs.append(normalized)
            section_sources[category].append(
                {
                    "source_id": normalized["source_id"],
                    "artifact_type": normalized["artifact_type"],
                    "source_hash": normalized["source_hash"],
                    "summary": normalized["summary"],
                }
            )

    accepted_inputs = sorted(
        accepted_inputs,
        key=lambda item: (
            item["category"],
            item["source_id"],
            item["artifact_type"],
            item["source_hash"],
        ),
    )
    rejected_inputs = sorted(rejected_inputs, key=lambda item: (item["category"], item["source_id"], item["reason"]))
    context_sections = [
        {
            "category": category,
            "source_count": len(section_sources[category]),
            "sources": sorted(
                section_sources[category],
                key=lambda item: (item["source_id"], item["artifact_type"], item["source_hash"]),
            ),
            "empty_reason": None if section_sources[category] else "no approved replay-visible source supplied",
        }
        for category in CONTEXT_CATEGORIES
    ]
    return {
        "accepted_inputs": accepted_inputs,
        "rejected_inputs": rejected_inputs,
        "context_sections": context_sections,
        "known_gaps": _known_gaps(),
    }


def _normalize_item(category: str, position: int, item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise FailClosedRuntimeError("source item must be a JSON object")
    artifact = deepcopy(item)
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("source item is not replay-visible")
    _reject_prohibited_authority(artifact)
    _verify_artifact_hash_if_present(artifact)
    artifact_type = _optional_string(artifact.get("artifact_type")) or _optional_string(artifact.get("event_type")) or "UNKNOWN"
    source_id = (
        _optional_string(artifact.get("artifact_id"))
        or _optional_string(artifact.get("context_assembly_id"))
        or _optional_string(artifact.get("route_id"))
        or _optional_string(artifact.get("handoff_id"))
        or _optional_string(artifact.get("resolution_id"))
        or _optional_string(artifact.get("decision_id"))
        or _optional_string(artifact.get("source_id"))
        or f"{category}:ITEM-{position:06d}"
    )
    source_hash = (
        _optional_string(artifact.get("artifact_hash"))
        or _optional_string(artifact.get("replay_hash"))
        or _optional_string(artifact.get("context_hash"))
        or replay_hash(artifact)
    )
    summary = _summary_fields(artifact)
    fingerprint = replay_hash(
        {
            "artifact_type": artifact_type,
            "source_hash": source_hash,
            "summary": summary,
        }
    )
    return {
        "category": category,
        "source_id": source_id,
        "artifact_type": artifact_type,
        "source_hash": source_hash,
        "source_fingerprint": fingerprint,
        "summary": summary,
        "dedupe_status": "ACCEPTED",
        "replay_visible": True,
        "authority": False,
    }


def _context_artifact(
    *,
    context_assembly_id: str,
    created_at: str,
    replay_reference: str,
    source_chain_id: str | None,
    source_request_reference: str | None,
    normalized: dict[str, Any],
    context_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_CONTEXT_ASSEMBLY_RUNTIME_VERSION,
        "contract_reference": "AIGOL_OCS_BOUNDARY_AND_CONTEXT_ASSEMBLY_CONTRACT_V1",
        "context_assembly_id": _require_string(context_assembly_id, "context_assembly_id"),
        "source_chain_id": source_chain_id,
        "source_request_reference": source_request_reference,
        "input_categories": list(CONTEXT_CATEGORIES),
        "accepted_inputs": deepcopy(normalized["accepted_inputs"]),
        "rejected_inputs": deepcopy(normalized["rejected_inputs"]),
        "context_sections": deepcopy(normalized["context_sections"]),
        "normalization_policy": {
            "source_visibility_required": True,
            "deterministic_sorting": True,
            "dedupe_key": "artifact_type + source_hash + summary",
            "prohibited_authority_flags_rejected": list(PROHIBITED_AUTHORITY_FLAGS),
        },
        "known_gaps": deepcopy(normalized["known_gaps"]),
        "accepted_input_count": len(normalized["accepted_inputs"]),
        "deduplicated_input_count": len(
            [item for item in normalized["rejected_inputs"] if "duplicate source" in item["reason"]]
        ),
        "rejected_input_count": len(normalized["rejected_inputs"]),
        "context_status": context_status,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "approval_inferred": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_assignment_requested": False,
        "worker_dispatch_requested": False,
        "worker_invocation_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": failure_reason,
    }
    artifact["context_hash"] = _compute_context_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(context_artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(context_artifact)
    returned = {
        "event_type": "OCS_CONTEXT_ASSEMBLY_RETURNED",
        "context_assembly_reference": context_artifact["context_assembly_id"],
        "context_assembly_hash": context_artifact["artifact_hash"],
        "context_status": context_artifact["context_status"],
        "context_hash": context_artifact["context_hash"],
        "accepted_input_count": context_artifact["accepted_input_count"],
        "deduplicated_input_count": context_artifact["deduplicated_input_count"],
        "rejected_input_count": context_artifact["rejected_input_count"],
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": context_artifact["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(context_artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_context_assembly_artifact": deepcopy(context_artifact),
        "ocs_context_assembly_returned": deepcopy(returned),
        "ocs_context_assembly_replay_reference": str(replay_path),
        "context_status": context_artifact["context_status"],
        "context_hash": context_artifact["context_hash"],
        "accepted_input_count": context_artifact["accepted_input_count"],
        "deduplicated_input_count": context_artifact["deduplicated_input_count"],
        "rejected_input_count": context_artifact["rejected_input_count"],
        "fail_closed": context_artifact["context_status"] != OCS_CONTEXT_ASSEMBLED,
        "failure_reason": context_artifact["failure_reason"],
        "authority_flags": deepcopy(context_artifact["authority_flags"]),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    capture["ocs_context_assembly_capture_hash"] = replay_hash(capture)
    return capture


def _compute_context_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "contract_reference": artifact["contract_reference"],
            "source_chain_id": artifact.get("source_chain_id"),
            "source_request_reference": artifact.get("source_request_reference"),
            "input_categories": artifact["input_categories"],
            "accepted_inputs": artifact["accepted_inputs"],
            "rejected_inputs": artifact["rejected_inputs"],
            "context_sections": artifact["context_sections"],
            "normalization_policy": artifact["normalization_policy"],
            "known_gaps": artifact["known_gaps"],
            "authority_flags": artifact["authority_flags"],
            "context_status": artifact["context_status"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _summary_fields(artifact: dict[str, Any]) -> dict[str, Any]:
    preferred_fields = (
        "artifact_type",
        "event_type",
        "status",
        "context_status",
        "route_status",
        "terminal_status",
        "approval_status",
        "decision_status",
        "resolution_status",
        "domain_id",
        "requested_domain",
        "bundle_id",
        "provider_necessity_classification",
        "ppp_resource_status",
        "failure_reason",
    )
    return {field: deepcopy(artifact[field]) for field in preferred_fields if field in artifact}


def _reject_prohibited_authority(artifact: dict[str, Any]) -> None:
    for flag in PROHIBITED_AUTHORITY_FLAGS:
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"source item carries prohibited OCS authority flag: {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        for flag in AUTHORITY_FLAGS:
            if flags.get(flag) is True:
                raise FailClosedRuntimeError(f"source item carries prohibited OCS authority flag: {flag}")


def _empty_normalized_context() -> dict[str, Any]:
    return {
        "accepted_inputs": [],
        "rejected_inputs": [],
        "context_sections": [
            {
                "category": category,
                "source_count": 0,
                "sources": [],
                "empty_reason": "OCS context assembly failed before source normalization completed",
            }
            for category in CONTEXT_CATEGORIES
        ],
        "known_gaps": _known_gaps(),
    }


def _known_gaps() -> list[str]:
    return [
        "OCS provider necessity policy is not implemented in this milestone.",
        "OCS-to-PPP handoff runtime is not implemented in this milestone.",
        "OCS coverage matrix is not implemented in this milestone.",
        "OCS pressure and multi-operation validation remain future work.",
    ]


def _rejected_input(category: str, source_id: str, reason: str) -> dict[str, Any]:
    return {
        "category": category,
        "source_id": source_id,
        "reason": reason,
        "replay_visible": True,
        "authority": False,
    }


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS context assembly replay step ordering mismatch")
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


def _verify_artifact_hash_if_present(artifact: dict[str, Any]) -> None:
    if "artifact_hash" in artifact:
        _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("OCS context assembly artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS context assembly artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS context assembly replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS context assembly replay hash mismatch")


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
    return "OCS context assembly failed closed"
