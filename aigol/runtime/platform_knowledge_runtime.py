"""Read-only Platform Knowledge Runtime composition service.

The runtime composes existing Platform Core knowledge sources. It does not
create a registry, own certification, perform diagnostics, invoke providers or
workers, modify replay, or replace Project Services knowledge reuse.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    is_platform_capability_certified,
    list_platform_capability_certifications,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_core_cognition_layer import BINDING_REFERENCE_OWNER_BY_TYPE
from aigol.runtime.platform_core_project_services import (
    PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION,
    PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION,
    PLATFORM_CORE_PROJECT_SERVICES_VERSION,
    discover_candidate_capabilities,
    project_knowledge_context_from_workspace,
)
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_KNOWLEDGE_RUNTIME_VERSION = "G19_02_PLATFORM_KNOWLEDGE_RUNTIME_V1"
PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1 = "PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1"

PLATFORM_KNOWLEDGE_SOURCE_PRECEDENCE = (
    "CERTIFICATION_REGISTRY",
    "PLATFORM_CORE_PROJECT_SERVICES",
    "PROJECT_KNOWLEDGE_REUSE",
    "GOVERNANCE_EVIDENCE",
    "PCCL_REFERENCE_METADATA",
    "REPLAY_WORKSPACE_METADATA",
)

PLATFORM_KNOWLEDGE_BOUNDARY_FLAGS = {
    "read_only": True,
    "composition_layer_only": True,
    "new_registry_created": False,
    "duplicate_architectural_metadata_created": False,
    "certification_owned": False,
    "capability_discovery_owned": False,
    "knowledge_reuse_replaced": False,
    "root_cause_trace_invoked": False,
    "runtime_diagnostics_performed": False,
    "governance_modified": False,
    "replay_modified": False,
    "provider_invoked": False,
    "worker_invoked": False,
}


def query_platform_knowledge(
    *,
    query: str,
    capability_identifier: str | None = None,
    goal_target: str | None = None,
    workspace_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only Platform Knowledge response.

    Explicit capability identifiers are resolved through the certification
    registry and fail closed when unknown. Free-form queries use existing
    Project Services capability discovery and Knowledge Reuse, then search the
    certification registry metadata without creating a new registry.
    """

    raw_query = _require_string(query, "query")
    explicit_capability = _optional_normalized_identifier(capability_identifier)
    discovery = discover_candidate_capabilities(
        message=raw_query,
        workspace_state=workspace_state,
    )
    selected_goal_target = _selected_goal_target(
        explicit_goal_target=goal_target,
        discovery=discovery,
    )
    knowledge_reuse = project_knowledge_context_from_workspace(
        message=raw_query,
        workspace_state=workspace_state,
        goal_target=selected_goal_target,
        governed_request=raw_query,
        candidate_capability_discovery=discovery,
    )
    certification_record = _resolve_certification_record(
        query=raw_query,
        explicit_capability_identifier=explicit_capability,
    )
    certification_summary = _certification_summary(certification_record)
    project_summary = _project_knowledge_summary(
        discovery=discovery,
        knowledge_reuse=knowledge_reuse,
    )
    recommended_service = _recommended_platform_service(
        certification_record=certification_record,
        project_summary=project_summary,
    )
    capability_exists = bool(certification_record) or bool(project_summary["project_capability_detected"])
    response = {
        "artifact_type": PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1,
        "platform_knowledge_runtime_version": PLATFORM_KNOWLEDGE_RUNTIME_VERSION,
        "query": raw_query,
        "query_hash": replay_hash(raw_query),
        "query_classification": _query_classification(
            certification_record=certification_record,
            project_summary=project_summary,
        ),
        "explicit_capability_identifier": explicit_capability,
        "canonical_capability_identifier": (
            certification_record.get("capability_identifier")
            if isinstance(certification_record, dict)
            else None
        ),
        "goal_target": selected_goal_target,
        "capability_exists": capability_exists,
        "certified_capability_exists": certification_record is not None,
        "project_capability_detected": project_summary["project_capability_detected"],
        "capability_owner": certification_summary["capability_owner"],
        "architectural_owner": certification_summary["architectural_owner"],
        "implementation_owner": certification_summary["implementation_owner"],
        "certification_status": certification_summary["certification_status"],
        "certification_scope": certification_summary["certification_scope"],
        "certification_milestone": certification_summary["certification_milestone"],
        "certification_evidence": certification_summary["certification_evidence"],
        "certification_record_hash": certification_summary["certification_record_hash"],
        "certification_registry_version": PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
        "is_certified": (
            is_platform_capability_certified(certification_record["capability_identifier"])
            if isinstance(certification_record, dict)
            else False
        ),
        "knowledge_reuse_version": PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION,
        "knowledge_reuse_classification": knowledge_reuse["classification"],
        "reuse_recommended": knowledge_reuse["reuse_recommended"] is True,
        "reuse_reason": knowledge_reuse["reuse_reason"],
        "duplicate_work_avoided": knowledge_reuse["duplicate_work_avoided"] is True,
        "new_work_required": knowledge_reuse["new_work_required"] is True,
        "recommended_platform_service": recommended_service,
        "source_precedence": list(PLATFORM_KNOWLEDGE_SOURCE_PRECEDENCE),
        "source_evidence": _source_evidence(
            certification_record=certification_record,
            discovery=discovery,
            knowledge_reuse=knowledge_reuse,
        ),
        "pccl_reference_owners": _pccl_reference_owners(),
        "unknown_or_missing_evidence": _missing_evidence(
            certification_record=certification_record,
            project_summary=project_summary,
        ),
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "human_intent_capability_resolution_version": (
            PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION
        ),
        "platform_knowledge_authority": "PLATFORM_CORE",
        "human_interface_authority": False,
        "provider_platform_preserved": True,
        "worker_platform_preserved": True,
        "governance_authority_preserved": True,
        "replay_authority_preserved": True,
        "root_cause_trace_boundary_preserved": True,
        **PLATFORM_KNOWLEDGE_BOUNDARY_FLAGS,
    }
    response["artifact_hash"] = replay_hash(response)
    return response


def validate_platform_knowledge_response(response: dict[str, Any]) -> dict[str, Any]:
    """Validate a Platform Knowledge response without consulting new state."""

    if not isinstance(response, dict):
        raise FailClosedRuntimeError("platform knowledge response must be a dict")
    if response.get("artifact_type") != PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform knowledge response artifact type is invalid")
    if response.get("platform_knowledge_runtime_version") != PLATFORM_KNOWLEDGE_RUNTIME_VERSION:
        raise FailClosedRuntimeError("platform knowledge runtime version is invalid")
    for field_name, expected in PLATFORM_KNOWLEDGE_BOUNDARY_FLAGS.items():
        if response.get(field_name) is not expected:
            raise FailClosedRuntimeError("platform knowledge response boundary flags invalid")
    if response.get("human_interface_authority") is not False:
        raise FailClosedRuntimeError("platform knowledge response human interface authority invalid")
    artifact_hash = response.get("artifact_hash")
    if not isinstance(artifact_hash, str) or not artifact_hash.startswith("sha256:"):
        raise FailClosedRuntimeError("platform knowledge response hash is required")
    body = deepcopy(response)
    body.pop("artifact_hash", None)
    if replay_hash(body) != artifact_hash:
        raise FailClosedRuntimeError("platform knowledge response hash mismatch")
    return deepcopy(response)


def _resolve_certification_record(
    *,
    query: str,
    explicit_capability_identifier: str | None,
) -> dict[str, Any] | None:
    if explicit_capability_identifier:
        return lookup_platform_capability_certification(explicit_capability_identifier)
    candidates = _registry_candidates_for_query(query)
    if not candidates:
        return None
    return deepcopy(candidates[0]["record"])


def _registry_candidates_for_query(query: str) -> list[dict[str, Any]]:
    query_tokens = _token_set(query)
    candidates: list[dict[str, Any]] = []
    for record in list_platform_capability_certifications():
        record_tokens = _record_tokens(record)
        score = len(query_tokens.intersection(record_tokens))
        if score < 2:
            continue
        candidates.append(
            {
                "score": score,
                "capability_identifier": record["capability_identifier"],
                "record": record,
            }
        )
    return sorted(
        candidates,
        key=lambda candidate: (
            -int(candidate["score"]),
            str(candidate["capability_identifier"]),
        ),
    )


def _record_tokens(record: dict[str, Any]) -> set[str]:
    fields = [
        record.get("capability_identifier"),
        record.get("capability_owner"),
        record.get("architectural_owner"),
        record.get("implementation_owner"),
        record.get("certification_milestone"),
        record.get("verification_type"),
        " ".join(str(item) for item in record.get("certification_evidence", ())),
    ]
    tokens: set[str] = set()
    for value in fields:
        tokens.update(_token_set(str(value or "")))
    return tokens


def _token_set(value: str) -> set[str]:
    normalized = (
        value.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace(".", " ")
    )
    return {token for token in normalized.split() if len(token) > 2}


def _certification_summary(record: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {
            "capability_owner": None,
            "architectural_owner": None,
            "implementation_owner": None,
            "certification_status": "NOT_CERTIFIED",
            "certification_scope": None,
            "certification_milestone": None,
            "certification_evidence": [],
            "certification_record_hash": None,
        }
    return {
        "capability_owner": record["capability_owner"],
        "architectural_owner": record["architectural_owner"],
        "implementation_owner": record["implementation_owner"],
        "certification_status": record["certification_status"],
        "certification_scope": record["certification_scope"],
        "certification_milestone": record["certification_milestone"],
        "certification_evidence": list(record["certification_evidence"]),
        "certification_record_hash": record["certification_record_hash"],
    }


def _project_knowledge_summary(
    *,
    discovery: dict[str, Any],
    knowledge_reuse: dict[str, Any],
) -> dict[str, Any]:
    selected = (
        discovery.get("selected_candidate_capability")
        if isinstance(discovery.get("selected_candidate_capability"), dict)
        else None
    )
    goal_target = str(discovery.get("selected_goal_target") or "")
    project_capability_detected = bool(selected) and goal_target != "general_project_goal"
    return {
        "project_capability_detected": project_capability_detected,
        "selected_candidate_capability": deepcopy(selected),
        "selected_goal_target": goal_target or "general_project_goal",
        "knowledge_reuse_classification": knowledge_reuse["classification"],
    }


def _recommended_platform_service(
    *,
    certification_record: dict[str, Any] | None,
    project_summary: dict[str, Any],
) -> str | None:
    if isinstance(certification_record, dict):
        return str(certification_record["implementation_owner"])
    if project_summary["project_capability_detected"]:
        return "aigol.runtime.platform_core_project_services"
    return None


def _source_evidence(
    *,
    certification_record: dict[str, Any] | None,
    discovery: dict[str, Any],
    knowledge_reuse: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence = [
        {
            "source_type": "CAPABILITY_DISCOVERY",
            "source_owner": "PLATFORM_CORE_HUMAN_INTENT_RESOLUTION",
            "source_version": discovery["runtime_version"],
            "artifact_hash": discovery["artifact_hash"],
            "selected_goal_target": discovery["selected_goal_target"],
            "capability_resolution_decision": discovery["capability_resolution_decision"],
        },
        {
            "source_type": "KNOWLEDGE_REUSE",
            "source_owner": "PLATFORM_CORE_KNOWLEDGE_REUSE",
            "source_version": knowledge_reuse["knowledge_reuse_version"],
            "classification": knowledge_reuse["classification"],
            "reuse_recommended": knowledge_reuse["reuse_recommended"],
            "relevant_certified_artifacts": list(knowledge_reuse["relevant_certified_artifacts"]),
        },
    ]
    if isinstance(certification_record, dict):
        evidence.insert(
            0,
            {
                "source_type": "CERTIFICATION_REGISTRY",
                "source_owner": "PLATFORM_CORE_CERTIFICATION",
                "source_version": PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
                "capability_identifier": certification_record["capability_identifier"],
                "certification_record_hash": certification_record["certification_record_hash"],
                "certification_evidence": list(certification_record["certification_evidence"]),
            },
        )
    return evidence


def _pccl_reference_owners() -> dict[str, str]:
    reference_types = (
        "CAPABILITY_DISCOVERY",
        "KNOWLEDGE_REUSE",
        "CERTIFICATION_REGISTRY",
        "GOVERNANCE",
        "REPLAY",
        "PROVIDER_PLATFORM",
        "WORKER_RESOLUTION",
    )
    return {
        reference_type: BINDING_REFERENCE_OWNER_BY_TYPE[reference_type]
        for reference_type in reference_types
    }


def _missing_evidence(
    *,
    certification_record: dict[str, Any] | None,
    project_summary: dict[str, Any],
) -> list[str]:
    missing: list[str] = []
    if certification_record is None:
        missing.append("NO_CERTIFICATION_REGISTRY_MATCH")
    if not project_summary["project_capability_detected"]:
        missing.append("NO_PROJECT_CAPABILITY_DISCOVERY_MATCH")
    return missing


def _query_classification(
    *,
    certification_record: dict[str, Any] | None,
    project_summary: dict[str, Any],
) -> str:
    if isinstance(certification_record, dict) and project_summary["project_capability_detected"]:
        return "CERTIFIED_CAPABILITY_WITH_PROJECT_REUSE_CONTEXT"
    if isinstance(certification_record, dict):
        return "CERTIFIED_CAPABILITY"
    if project_summary["project_capability_detected"]:
        return "PROJECT_CAPABILITY_KNOWLEDGE"
    return "UNKNOWN_PLATFORM_KNOWLEDGE"


def _selected_goal_target(
    *,
    explicit_goal_target: str | None,
    discovery: dict[str, Any],
) -> str:
    if explicit_goal_target is not None and str(explicit_goal_target).strip():
        return str(explicit_goal_target).strip()
    return str(discovery.get("selected_goal_target") or "general_project_goal")


def _optional_normalized_identifier(value: str | None) -> str | None:
    if value is None:
        return None
    return _require_string(value, "capability_identifier").upper().replace("-", "_").replace(" ", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
