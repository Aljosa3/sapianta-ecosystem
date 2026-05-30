"""Minimal reference-only Constitutional Memory access path."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


REQUESTED = "REQUESTED"
RETRIEVED = "RETRIEVED"
RETURNED = "RETURNED"
FAILED = "FAILED"

REFERENCE_RESULT = "REFERENCE_RESULT"
REPLAY_STEPS = ("retrieval_request", "citation_bundle", "retrieval_result")

ALLOWED_REQUESTERS = frozenset({"HUMAN", "OPERATOR", "AIGOL_GOVERNANCE"})
CONDITIONAL_REQUESTERS = frozenset({"RUNTIME_VALIDATION_STEP"})
FORBIDDEN_REQUESTERS = frozenset({"PROVIDER", "WORKER"})

RETRIEVABLE_SCOPES = frozenset(
    {
        "CONSTITUTIONAL_INVARIANTS",
        "AUTHORITY_INVARIANTS",
        "FREEZE_MANIFESTS",
        "CERTIFICATIONS",
        "ACCEPTANCE_EVIDENCE",
        "GOVERNANCE_REVIEWS",
        "OPERATIONAL_BASELINES",
    }
)
CONDITIONAL_SCOPES = frozenset({"REPLAY_LINEAGE", "RUNTIME_EVIDENCE", "DERIVED_SUMMARIES"})
ALLOWED_CLASSIFICATIONS = frozenset({"CANONICAL", "SUPPORTING", "DERIVED"})
FORBIDDEN_REQUEST_TERMS = (
    "authorize",
    "authorization decision",
    "execute",
    "execution request",
    "governance decision",
    "worker command",
    "provider command",
    "proposal generation",
    "correction instruction",
    "mutate",
    "write",
    "delete",
    "shell",
    "network",
    "api",
)

CONSTITUTIONAL_MEMORY_CATALOG: dict[str, dict[str, Any]] = {
    "CONSTITUTIONAL_ARCHITECTURE_SPEC": {
        "path": "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
        "classification": "CANONICAL",
        "layer": "M0_CONSTITUTIONAL_SOURCE",
        "scopes": ["CONSTITUTIONAL_INVARIANTS", "GOVERNANCE_REVIEWS"],
    },
    "CONSTITUTIONAL_INVARIANTS": {
        "path": "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
        "classification": "CANONICAL",
        "layer": "M0_CONSTITUTIONAL_SOURCE",
        "scopes": ["CONSTITUTIONAL_INVARIANTS", "AUTHORITY_INVARIANTS"],
    },
    "CANONICAL_LAYER_MODEL": {
        "path": "docs/governance/CANONICAL_LAYER_MODEL.md",
        "classification": "CANONICAL",
        "layer": "M0_CONSTITUTIONAL_SOURCE",
        "scopes": ["CONSTITUTIONAL_INVARIANTS", "GOVERNANCE_REVIEWS"],
    },
    "GOVERNANCE_ENFORCEMENT_HIERARCHY": {
        "path": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
        "classification": "CANONICAL",
        "layer": "M0_CONSTITUTIONAL_SOURCE",
        "scopes": ["GOVERNANCE_REVIEWS", "AUTHORITY_INVARIANTS"],
    },
    "GOVERNANCE_LINEAGE_MODEL": {
        "path": "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        "classification": "CANONICAL",
        "layer": "M0_CONSTITUTIONAL_SOURCE",
        "scopes": ["GOVERNANCE_REVIEWS", "REPLAY_LINEAGE"],
    },
    "CANONICAL_AUTHORITY_MODEL": {
        "path": "governance/CANONICAL_AUTHORITY_MODEL_V1.md",
        "classification": "CANONICAL",
        "layer": "M1_CANONICAL_LANGUAGE_AND_AUTHORITY",
        "scopes": ["AUTHORITY_INVARIANTS"],
    },
    "CANONICAL_REPLAY_LANGUAGE": {
        "path": "governance/CANONICAL_REPLAY_LANGUAGE_V1.md",
        "classification": "CANONICAL",
        "layer": "M1_CANONICAL_LANGUAGE_AND_AUTHORITY",
        "scopes": ["REPLAY_LINEAGE"],
    },
    "FIRST_USEFUL_AIGOL_FREEZE": {
        "path": "governance/FIRST_USEFUL_AIGOL_V1_FREEZE.md",
        "classification": "CANONICAL",
        "layer": "M2_FREEZE_AND_BASELINE_MEMORY",
        "scopes": ["FREEZE_MANIFESTS", "OPERATIONAL_BASELINES"],
    },
    "FIRST_USEFUL_AIGOL_BASELINE": {
        "path": "governance/FIRST_USEFUL_AIGOL_V1_BASELINE.md",
        "classification": "CANONICAL",
        "layer": "M2_FREEZE_AND_BASELINE_MEMORY",
        "scopes": ["OPERATIONAL_BASELINES"],
    },
    "FIRST_USEFUL_AIGOL_GUARANTEES": {
        "path": "governance/FIRST_USEFUL_AIGOL_V1_GUARANTEES.md",
        "classification": "CANONICAL",
        "layer": "M2_FREEZE_AND_BASELINE_MEMORY",
        "scopes": ["AUTHORITY_INVARIANTS", "OPERATIONAL_BASELINES"],
    },
    "CONSTITUTIONAL_MEMORY_POSITION_REVIEW": {
        "path": "governance/CONSTITUTIONAL_MEMORY_POSITION_REVIEW_V1.md",
        "classification": "SUPPORTING",
        "layer": "M4_POSITION_AND_RECONSTRUCTION_MEMORY",
        "scopes": ["GOVERNANCE_REVIEWS"],
    },
    "CONSTITUTIONAL_MEMORY_INDEX_MODEL": {
        "path": "governance/CONSTITUTIONAL_MEMORY_INDEX_MODEL_V1.md",
        "classification": "SUPPORTING",
        "layer": "M4_POSITION_AND_RECONSTRUCTION_MEMORY",
        "scopes": ["GOVERNANCE_REVIEWS"],
    },
    "CONSTITUTIONAL_MEMORY_RETRIEVAL_MODEL": {
        "path": "governance/CONSTITUTIONAL_MEMORY_RETRIEVAL_MODEL_V1.md",
        "classification": "SUPPORTING",
        "layer": "M4_POSITION_AND_RECONSTRUCTION_MEMORY",
        "scopes": ["GOVERNANCE_REVIEWS"],
    },
    "FIRST_USEFUL_AIGOL_ACCEPTANCE": {
        "path": "governance/FIRST_USEFUL_AIGOL_V1_ACCEPTANCE.json",
        "classification": "SUPPORTING",
        "layer": "M3_GOVERNANCE_CERTIFICATION_MEMORY",
        "scopes": ["ACCEPTANCE_EVIDENCE"],
    },
    "FIRST_USEFUL_AIGOL_CERTIFICATION": {
        "path": "governance/FIRST_USEFUL_AIGOL_V1_CERTIFICATION.json",
        "classification": "SUPPORTING",
        "layer": "M3_GOVERNANCE_CERTIFICATION_MEMORY",
        "scopes": ["CERTIFICATIONS"],
    },
}


def retrieve_constitutional_memory(
    *,
    retrieval_id: str,
    requested_by: str,
    retrieval_scope: str,
    query: str,
    created_at: str,
    replay_dir: str | Path,
    artifact_query: str | None = None,
    governance_context: bool = False,
    repository_root: str | Path | None = None,
    artifact_catalog: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Retrieve citation-bound Constitutional Memory references."""

    replay_path = Path(replay_dir)
    request: dict[str, Any] | None = None
    try:
        request = _create_retrieval_request(
            retrieval_id=retrieval_id,
            requested_by=requested_by,
            retrieval_scope=retrieval_scope,
            query=query,
            artifact_query=artifact_query,
            governance_context=governance_context,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, "retrieval_request", request)
        catalog = artifact_catalog or CONSTITUTIONAL_MEMORY_CATALOG
        selected = _select_artifacts(
            catalog=catalog,
            retrieval_scope=request["retrieval_scope"],
            artifact_query=request.get("artifact_query"),
            governance_context=governance_context,
        )
        citations = _create_citation_bundle(
            request=request,
            selected_artifacts=selected,
            repository_root=Path(repository_root) if repository_root is not None else Path.cwd(),
        )
        _persist_step(replay_path, 1, "citation_bundle", citations)
        result = _create_retrieval_result(request=request, citations=citations)
        _persist_step(replay_path, 2, "retrieval_result", result)
        return _capture(request, citations, result)
    except Exception as exc:
        if request is None:
            request = _failed_retrieval_request(
                retrieval_id=retrieval_id,
                requested_by=requested_by,
                retrieval_scope=retrieval_scope,
                query=query,
                artifact_query=artifact_query,
                governance_context=governance_context,
                created_at=created_at,
                failure_reason=_failure_reason(exc),
            )
            _persist_request_if_absent(replay_path, request)
        failure = _failure_artifact(request=request, failure_reason=_failure_reason(exc))
        _persist_failure_sequence(replay_path, failure)
        return _capture(request, None, failure)


def reconstruct_constitutional_memory_retrieval_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate Constitutional Memory retrieval replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("constitutional memory retrieval replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("constitutional memory retrieval replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    states = [wrapper["artifact"]["state"] for wrapper in wrappers]
    _validate_replay_states(states)
    final_artifact = wrappers[-1]["artifact"]
    return {
        "retrieval_id": final_artifact["retrieval_id"],
        "retrieval_status": final_artifact["retrieval_status"],
        "final_status": final_artifact["final_status"],
        "lifecycle_transitions": states,
        "replay_visible": True,
        "reference_only": True,
        "citation_required": True,
        "citation_count": final_artifact.get("citation_count", 0),
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _create_retrieval_request(
    *,
    retrieval_id: str,
    requested_by: str,
    retrieval_scope: str,
    query: str,
    artifact_query: str | None,
    governance_context: bool,
    created_at: str,
) -> dict[str, Any]:
    requester = _normalize_token(requested_by, "requested_by")
    if requester in FORBIDDEN_REQUESTERS:
        raise FailClosedRuntimeError("constitutional memory retrieval requester is forbidden")
    if requester in CONDITIONAL_REQUESTERS and governance_context is not True:
        raise FailClosedRuntimeError("constitutional memory retrieval requires governance context")
    if requester not in ALLOWED_REQUESTERS and requester not in CONDITIONAL_REQUESTERS:
        raise FailClosedRuntimeError("constitutional memory retrieval requester is invalid")
    scope = _normalize_token(retrieval_scope, "retrieval_scope")
    _validate_query_is_reference_only(query)
    request = {
        "retrieval_id": _require_string(retrieval_id, "retrieval_id"),
        "requested_by": requester,
        "retrieval_scope": scope,
        "query": _normalize_text(query, "query"),
        "artifact_query": _normalize_text(artifact_query, "artifact_query") if artifact_query is not None else None,
        "governance_context": governance_context is True,
        "created_at": _require_string(created_at, "created_at"),
        "state": REQUESTED,
        "retrieval_type": REFERENCE_RESULT,
        "reference_only": True,
        "citation_required": True,
        "replay_visibility_required": True,
        "authorization_authority": False,
        "governance_authority": False,
        "execution_authority": False,
        "proposal_authority": False,
        "memory_mutation_authority": False,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def _failed_retrieval_request(
    *,
    retrieval_id: Any,
    requested_by: Any,
    retrieval_scope: Any,
    query: Any,
    artifact_query: str | None,
    governance_context: bool,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    request = {
        "retrieval_id": retrieval_id if isinstance(retrieval_id, str) and retrieval_id.strip() else "INVALID_RETRIEVAL_ID",
        "requested_by": _best_effort_token(requested_by),
        "retrieval_scope": _best_effort_token(retrieval_scope),
        "query": query if isinstance(query, str) and query.strip() else "INVALID_QUERY",
        "artifact_query": artifact_query,
        "governance_context": governance_context is True,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "state": FAILED,
        "retrieval_type": REFERENCE_RESULT,
        "retrieval_status": "FAILED_CLOSED",
        "failure_reason": failure_reason,
        "reference_only": True,
        "citation_required": True,
        "replay_visibility_required": True,
        "authorization_authority": False,
        "governance_authority": False,
        "execution_authority": False,
        "proposal_authority": False,
        "memory_mutation_authority": False,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def _select_artifacts(
    *,
    catalog: dict[str, dict[str, Any]],
    retrieval_scope: str,
    artifact_query: str | None,
    governance_context: bool,
) -> list[tuple[str, dict[str, Any]]]:
    if not isinstance(catalog, dict) or not catalog:
        raise FailClosedRuntimeError("constitutional memory catalog is invalid")
    _validate_scope(retrieval_scope, governance_context=governance_context)
    if artifact_query:
        normalized_query = _normalize_token(artifact_query, "artifact_query")
        if normalized_query in catalog:
            return [(normalized_query, _validate_catalog_entry(catalog[normalized_query]))]
        matches = [
            (artifact_id, _validate_catalog_entry(entry))
            for artifact_id, entry in sorted(catalog.items())
            if normalized_query in artifact_id
        ]
        if not matches:
            raise FailClosedRuntimeError("constitutional memory artifact missing")
        if len(matches) > 1:
            raise FailClosedRuntimeError("constitutional memory artifact is ambiguous")
        return matches
    matches = [
        (artifact_id, _validate_catalog_entry(entry))
        for artifact_id, entry in sorted(catalog.items())
        if retrieval_scope in {_normalize_token(scope, "scope") for scope in entry.get("scopes", [])}
    ]
    if not matches:
        raise FailClosedRuntimeError("constitutional memory artifact missing")
    return matches


def _create_citation_bundle(
    *,
    request: dict[str, Any],
    selected_artifacts: list[tuple[str, dict[str, Any]]],
    repository_root: Path,
) -> dict[str, Any]:
    citations = []
    for artifact_id, entry in selected_artifacts:
        path = repository_root / entry["path"]
        _validate_source_path(path)
        source_hash = _source_hash(path)
        citations.append(
            {
                "artifact_identity": artifact_id,
                "artifact_classification": entry["classification"],
                "artifact_path": entry["path"],
                "memory_layer": entry["layer"],
                "retrieval_timestamp": request["created_at"],
                "replay_visibility": "MANDATORY",
                "authority_status": "REFERENCE_ONLY",
                "citation_reference": f"{entry['path']}#{source_hash}",
                "citation_reason": f"retrieved for {request['retrieval_scope']}",
                "source_hash": source_hash,
            }
        )
    if not citations:
        raise FailClosedRuntimeError("constitutional memory citation is required")
    bundle = {
        "retrieval_id": request["retrieval_id"],
        "state": RETRIEVED,
        "previous_state": REQUESTED,
        "retrieval_request_hash": request["artifact_hash"],
        "citation_count": len(citations),
        "citations": citations,
        "returned_artifacts": [citation["artifact_identity"] for citation in citations],
        "retrieval_status": "RETRIEVED",
        "reference_only": True,
        "citation_required": True,
        "replay_visible": True,
        "authorization_authority": False,
        "governance_authority": False,
        "execution_authority": False,
        "proposal_authority": False,
    }
    bundle["artifact_hash"] = replay_hash(bundle)
    return bundle


def _create_retrieval_result(*, request: dict[str, Any], citations: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(request)
    _verify_artifact_hash(citations)
    result = {
        "retrieval_id": request["retrieval_id"],
        "state": RETURNED,
        "previous_state": RETRIEVED,
        "retrieval_request_hash": request["artifact_hash"],
        "citation_bundle_hash": citations["artifact_hash"],
        "retrieval_scope": request["retrieval_scope"],
        "returned_citations": deepcopy(citations["citations"]),
        "returned_artifacts": deepcopy(citations["returned_artifacts"]),
        "citation_count": citations["citation_count"],
        "retrieval_status": "SUCCESS",
        "final_status": "RETURNED_REFERENCE_RESULT",
        "result_type": REFERENCE_RESULT,
        "reference_only": True,
        "replay_visible": True,
        "citation_required": True,
        "authorization_decision": None,
        "governance_decision": None,
        "execution_request": None,
        "worker_command": None,
        "provider_command": None,
        "proposal_generation": None,
        "correction_instruction": None,
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def _failure_artifact(*, request: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    artifact = {
        "retrieval_id": request["retrieval_id"],
        "state": FAILED,
        "previous_state": request.get("state", REQUESTED),
        "retrieval_request_hash": request["artifact_hash"],
        "retrieval_scope": request["retrieval_scope"],
        "retrieval_status": "FAILED_CLOSED",
        "final_status": FAILED,
        "failure_reason": failure_reason,
        "result_type": REFERENCE_RESULT,
        "reference_only": True,
        "replay_visible": True,
        "citation_required": True,
        "authorization_decision": None,
        "governance_decision": None,
        "execution_request": None,
        "worker_command": None,
        "provider_command": None,
        "proposal_generation": None,
        "correction_instruction": None,
        "automatic_retry": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(request: dict[str, Any], citations: dict[str, Any] | None, result: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "retrieval_request": deepcopy(request),
        "citation_bundle": deepcopy(citations),
        "retrieval_result": deepcopy(result),
    }
    capture["constitutional_memory_access_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("constitutional memory retrieval replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_sequence(replay_dir: Path, failure: dict[str, Any]) -> None:
    for index, step in enumerate(REPLAY_STEPS[1:], start=1):
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, _failure_step(failure, step))


def _persist_request_if_absent(replay_dir: Path, request: dict[str, Any]) -> None:
    path = replay_dir / "000_retrieval_request.json"
    if not path.exists():
        _persist_step(replay_dir, 0, "retrieval_request", request)


def _failure_step(failure: dict[str, Any], step: str) -> dict[str, Any]:
    artifact = deepcopy(failure)
    artifact["failed_step"] = step
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validate_scope(scope: str, *, governance_context: bool) -> None:
    if scope in RETRIEVABLE_SCOPES:
        return
    if scope in CONDITIONAL_SCOPES and governance_context is True:
        return
    if scope in CONDITIONAL_SCOPES:
        raise FailClosedRuntimeError("constitutional memory retrieval requires governance context")
    raise FailClosedRuntimeError("constitutional memory index reference is invalid")


def _validate_catalog_entry(entry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise FailClosedRuntimeError("constitutional memory index entry is invalid")
    path = _require_string(entry.get("path"), "artifact_path")
    classification = _normalize_token(entry.get("classification"), "artifact_classification")
    if classification not in ALLOWED_CLASSIFICATIONS:
        raise FailClosedRuntimeError("constitutional memory artifact classification is invalid")
    layer = _require_string(entry.get("layer"), "memory_layer")
    scopes = entry.get("scopes")
    if not isinstance(scopes, list) or not scopes:
        raise FailClosedRuntimeError("constitutional memory artifact scopes are invalid")
    return {
        "path": path,
        "classification": classification,
        "layer": layer,
        "scopes": [_normalize_token(scope, "scope") for scope in scopes],
    }


def _validate_source_path(path: Path) -> None:
    if not path.exists():
        raise FailClosedRuntimeError("constitutional memory artifact missing")
    if not path.is_file():
        raise FailClosedRuntimeError("constitutional memory artifact is invalid")
    if path.suffix == ".json":
        load_json(path)


def _source_hash(path: Path) -> str:
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise FailClosedRuntimeError("constitutional memory artifact is invalid") from exc
    return replay_hash({"path": str(path), "content": content.decode("utf-8")})


def _validate_query_is_reference_only(query: str) -> None:
    lowered = _normalize_text(query, "query").lower()
    for term in FORBIDDEN_REQUEST_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("constitutional memory authority-bearing request rejected")


def _validate_replay_states(states: list[str]) -> None:
    if states == [REQUESTED, RETRIEVED, RETURNED]:
        return
    if states == [REQUESTED, FAILED, FAILED]:
        return
    if states == [FAILED, FAILED, FAILED]:
        return
    raise FailClosedRuntimeError("constitutional memory retrieval lifecycle ordering mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("constitutional memory retrieval artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("constitutional memory retrieval artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("constitutional memory retrieval artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("constitutional memory retrieval replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("constitutional memory retrieval replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "constitutional memory retrieval failed closed"


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _best_effort_token(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip().upper().replace("-", "_")
    return "INVALID"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
