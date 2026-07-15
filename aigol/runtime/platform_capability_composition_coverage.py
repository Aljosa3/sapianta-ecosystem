"""Read-only Platform capability composition coverage for G20-03.

The service joins existing Platform Knowledge, capability certification,
router metadata, generation composition metadata, governance references, and
optional replay evidence. It does not own or replace any of those sources.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
from typing import Any

from aigol.runtime.generation_certification_composition import (
    canonical_generation_evidence_profile,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    CERTIFIED_STATES,
    list_platform_capability_certifications,
)
from aigol.runtime.platform_core_project_services import discover_candidate_capabilities
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION = (
    "G20_03_PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME_V1"
)
PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1 = (
    "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1"
)
PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1 = (
    "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1"
)

CAPABILITY_COMPOSITION_COVERAGE_REQUEST_CREATED = (
    "CAPABILITY_COMPOSITION_COVERAGE_REQUEST_CREATED"
)

COVERAGE_COMPLETE = "CAPABILITY_COMPOSITION_COVERAGE_COMPLETE"
COVERAGE_PARTIAL = "CAPABILITY_COMPOSITION_COVERAGE_PARTIAL"
COVERAGE_FAILED_CLOSED = "CAPABILITY_COMPOSITION_COVERAGE_FAILED_CLOSED"

NO_GAP_EXISTING_CAPABILITY_SUFFICIENT = "NO_GAP_EXISTING_CAPABILITY_SUFFICIENT"
NO_GAP_EXISTING_CERTIFIED_COMPOSITION_SUFFICIENT = (
    "NO_GAP_EXISTING_CERTIFIED_COMPOSITION_SUFFICIENT"
)
MINIMAL_COMPOSITION_SERVICE_REQUIRED = "MINIMAL_COMPOSITION_SERVICE_REQUIRED"
GENUINELY_NEW_CAPABILITY_REQUIRED = "GENUINELY_NEW_CAPABILITY_REQUIRED"
DISCOVERY_AMBIGUOUS_FAILED_CLOSED = "DISCOVERY_AMBIGUOUS_FAILED_CLOSED"

COVERAGE_BOUNDARY_FLAGS = {
    "read_only": True,
    "platform_core_authority": True,
    "composition_service_only": True,
    "new_platform_subsystem_created": False,
    "capability_registry_replaced": False,
    "platform_knowledge_replaced": False,
    "platform_query_router_replaced": False,
    "generation_certification_replaced": False,
    "replay_evidence_interpreted_read_only": True,
    "human_interface_authority": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "repository_mutated": False,
    "governance_modified": False,
    "replay_modified": False,
}


CAPABILITY_FACET_BINDINGS: tuple[dict[str, Any], ...] = (
    {
        "facet": "PLATFORM_KNOWLEDGE",
        "terms": ("platform knowledge", "knowledge runtime", "capability knowledge"),
        "capabilities": ("PLATFORM_KNOWLEDGE_RUNTIME",),
    },
    {
        "facet": "QUERY_ROUTING",
        "terms": ("query router", "query routing", "route platform", "service routing"),
        "capabilities": ("UNIFIED_PLATFORM_QUERY_ROUTER",),
    },
    {
        "facet": "CANONICAL_PRESENTATION",
        "terms": ("presentation layer", "canonical presentation", "present result"),
        "capabilities": ("CANONICAL_PLATFORM_PRESENTATION_LAYER",),
    },
    {
        "facet": "GENERATION_CERTIFICATION",
        "terms": ("generation certification", "certify generation", "generation evidence profile"),
        "capabilities": ("GENERATION_CERTIFICATION_COMPOSITION_SERVICE",),
    },
    {
        "facet": "REPLAY_CERTIFICATION",
        "terms": ("replay certification", "certify replay", "validated replay"),
        "capabilities": ("REPLAY_CERTIFICATION_RUNTIME",),
    },
    {
        "facet": "REPLAY_OBSERVATION",
        "terms": ("replay observation", "observe replay", "replay observations"),
        "capabilities": ("REPLAY_OBSERVATION_LAYER",),
    },
    {
        "facet": "ROOT_CAUSE_TRACE",
        "terms": ("root cause", "runtime causality", "explain failure"),
        "capabilities": ("DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING",),
    },
    {
        "facet": "PCCL",
        "terms": ("pccl", "cognition layer", "context envelope", "policy envelope"),
        "capabilities": (
            "PLATFORM_CORE_COGNITION_LAYER_FOUNDATION",
            "PCCL_SESSION_RUNTIME",
            "CANONICAL_CONTEXT_ENVELOPE",
            "CANONICAL_POLICY_ENVELOPE",
            "PCCL_REFERENCE_BINDING",
        ),
    },
    {
        "facet": "HUMAN_INTERFACE_RUNTIME_ENTRY",
        "terms": ("human interface runtime", "canonical runtime entry", "aicli runtime entry"),
        "capabilities": ("CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",),
    },
    {
        "facet": "CAPABILITY_COMPOSITION_DISCOVERY",
        "terms": (
            "capability composition",
            "capability coverage",
            "composition coverage",
            "composition discovery",
            "reusable capabilities",
            "residual gap",
        ),
        "capabilities": ("PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME",),
    },
)


KNOWN_COMPOSITION_DEPENDENCIES = {
    "PLATFORM_KNOWLEDGE_RUNTIME": (),
    "UNIFIED_PLATFORM_QUERY_ROUTER": ("PLATFORM_KNOWLEDGE_RUNTIME",),
    "CANONICAL_PLATFORM_PRESENTATION_LAYER": (
        "PLATFORM_KNOWLEDGE_RUNTIME",
        "UNIFIED_PLATFORM_QUERY_ROUTER",
    ),
    "GENERATION_CERTIFICATION_COMPOSITION_SERVICE": (
        "PLATFORM_KNOWLEDGE_RUNTIME",
        "UNIFIED_PLATFORM_QUERY_ROUTER",
        "CANONICAL_PLATFORM_PRESENTATION_LAYER",
    ),
}


def create_platform_capability_composition_coverage_request(
    *,
    request_id: str,
    query: str,
    created_at: str = "2026-07-15T00:00:00Z",
) -> dict[str, Any]:
    """Create the immutable canonical input used by the G29 onboarding route."""

    raw_query = _require_string(query, "query")
    artifact = {
        "artifact_type": PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1,
        "runtime_version": PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION,
        "request_status": CAPABILITY_COMPOSITION_COVERAGE_REQUEST_CREATED,
        "request_id": _require_string(request_id, "request_id"),
        "query": raw_query,
        "query_hash": replay_hash(raw_query),
        "created_at": _require_string(created_at, "created_at"),
        "read_only": True,
        "replay_visible": True,
        "human_interface_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_platform_capability_composition_coverage_request(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one immutable composition-coverage request artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("capability composition coverage request must be a dict")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != (
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError("capability composition coverage request type is invalid")
    if candidate.get("runtime_version") != PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION:
        raise FailClosedRuntimeError("capability composition coverage request version is invalid")
    if candidate.get("request_status") != CAPABILITY_COMPOSITION_COVERAGE_REQUEST_CREATED:
        raise FailClosedRuntimeError("capability composition coverage request status is invalid")
    _require_string(candidate.get("request_id"), "request_id")
    query = _require_string(candidate.get("query"), "query")
    if candidate.get("query_hash") != replay_hash(query):
        raise FailClosedRuntimeError("capability composition coverage request query hash mismatch")
    for field, expected in {
        "read_only": True,
        "replay_visible": True,
        "human_interface_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "governance_modified": False,
        "replay_modified": False,
    }.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError(
                "capability composition coverage request boundary invalid"
            )
    body = deepcopy(candidate)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("capability composition coverage request hash mismatch")
    return candidate


def discover_platform_capability_composition_coverage(
    *,
    query: str,
    workspace_state: dict[str, Any] | None = None,
    replay_evidence: list[dict[str, Any]] | None = None,
    governance_root: str | Path = ".",
    created_at: str = "2026-07-11T00:00:00Z",
) -> dict[str, Any]:
    """Compose deterministic capability coverage and residual gaps."""

    raw_query = _require_string(query, "query")
    try:
        registry = list_platform_capability_certifications()
        registry_by_id = {
            str(record["capability_identifier"]): record for record in registry
        }
        discovery = discover_candidate_capabilities(
            message=raw_query,
            workspace_state=workspace_state,
        )
        knowledge = query_platform_knowledge(
            query=raw_query,
            workspace_state=workspace_state,
        )
        route_descriptors = _route_descriptors()
        generation_profile = canonical_generation_evidence_profile()
        facets = _discover_facets(raw_query)
        coverage = _compose_coverage(
            facets=facets,
            registry_by_id=registry_by_id,
            route_descriptors=route_descriptors,
        )
        residual_gaps = _residual_gaps(coverage)
        compositions = _certified_compositions(
            registry=registry,
            coverage=coverage,
            generation_profile=generation_profile,
            governance_root=Path(governance_root),
        )
        replay = _resolve_replay_evidence(replay_evidence or [])
        replay_invalid = any(
            item.get("hash_valid") is not True or item.get("lineage_complete") is not True
            for item in replay
        )
        if replay_invalid:
            residual_gaps.append(
                {
                    "facet": "REPLAY_EVIDENCE",
                    "reason": "Replay evidence hash or lineage validation failed.",
                    "gap_classification": "INVALID_REPLAY_EVIDENCE",
                }
            )
        minimal_extension = _minimal_extension(
            coverage=coverage,
            residual_gaps=residual_gaps,
            compositions=compositions,
        )
        status = (
            COVERAGE_FAILED_CLOSED
            if replay_invalid
            or minimal_extension["classification"] == DISCOVERY_AMBIGUOUS_FAILED_CLOSED
            else COVERAGE_PARTIAL
            if residual_gaps
            else COVERAGE_COMPLETE
        )
        failure_reason = (
            "Replay evidence hash or lineage validation failed."
            if replay_invalid
            else
            "No deterministic request facet matched existing Platform capability metadata."
            if status == COVERAGE_FAILED_CLOSED
            else None
        )
    except Exception as exc:
        discovery = None
        knowledge = None
        route_descriptors = []
        generation_profile = None
        facets = []
        coverage = []
        residual_gaps = [
            {"facet": "COMPOSITION_DISCOVERY", "reason": str(exc), "fail_closed": True}
        ]
        compositions = []
        replay = []
        minimal_extension = {
            "classification": DISCOVERY_AMBIGUOUS_FAILED_CLOSED,
            "required": False,
            "recommended_components": [],
            "rationale": "Capability composition coverage failed closed.",
        }
        status = COVERAGE_FAILED_CLOSED
        failure_reason = str(exc) or "capability composition coverage failed closed"

    artifact = {
        "artifact_type": PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1,
        "runtime_version": PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION,
        "query": raw_query,
        "query_hash": replay_hash(raw_query),
        "created_at": _require_string(created_at, "created_at"),
        "coverage_status": status,
        "request_facets": facets,
        "request_facet_count": len(facets),
        "discovered_reusable_capabilities": _discovered_capabilities(coverage),
        "capability_coverage": coverage,
        "covered_facet_count": sum(1 for item in coverage if item.get("covered") is True),
        "certified_reusable_compositions": compositions,
        "uncovered_residual_gaps": residual_gaps,
        "uncovered_residual_gap_count": len(residual_gaps),
        "minimal_required_platform_extension": minimal_extension,
        "candidate_capability_discovery": discovery,
        "candidate_capability_discovery_hash": (
            discovery.get("artifact_hash") if isinstance(discovery, dict) else None
        ),
        "platform_knowledge_response": knowledge,
        "platform_knowledge_response_hash": (
            knowledge.get("artifact_hash") if isinstance(knowledge, dict) else None
        ),
        "platform_query_route_descriptors": route_descriptors,
        "generation_evidence_profile": generation_profile,
        "generation_evidence_profile_hash": (
            generation_profile.get("profile_hash")
            if isinstance(generation_profile, dict)
            else None
        ),
        "governance_evidence": _governance_evidence(compositions),
        "replay_evidence": replay,
        "failure_reason": failure_reason,
        "source_precedence": [
            "CAPABILITY_CERTIFICATION_REGISTRY",
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "CANDIDATE_CAPABILITY_DISCOVERY",
            "PLATFORM_QUERY_ROUTE_DESCRIPTORS",
            "GENERATION_EVIDENCE_PROFILE",
            "GOVERNANCE_EVIDENCE",
            "REPLAY_EVIDENCE",
        ],
        "reused_platform_core_services": [
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
            "UNIFIED_PLATFORM_QUERY_ROUTER",
            "GENERATION_CERTIFICATION_COMPOSITION_SERVICE",
            "GOVERNANCE_EVIDENCE",
            "REPLAY_EVIDENCE",
        ],
        "replay_visible": True,
        **COVERAGE_BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_platform_capability_composition_coverage(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate a capability composition coverage artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("capability composition coverage must be a dict")
    if artifact.get("artifact_type") != PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability composition coverage artifact type is invalid")
    if artifact.get("runtime_version") != PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION:
        raise FailClosedRuntimeError("capability composition coverage version is invalid")
    if artifact.get("coverage_status") not in {
        COVERAGE_COMPLETE,
        COVERAGE_PARTIAL,
        COVERAGE_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("capability composition coverage status is invalid")
    for field, expected in COVERAGE_BOUNDARY_FLAGS.items():
        if artifact.get(field) is not expected:
            raise FailClosedRuntimeError("capability composition coverage boundary flags invalid")
    body = deepcopy(artifact)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("capability composition coverage hash mismatch")
    return deepcopy(artifact)


def _discover_facets(query: str) -> list[dict[str, Any]]:
    lowered = " ".join(query.lower().replace("_", " ").replace("-", " ").split())
    facets = []
    for binding in CAPABILITY_FACET_BINDINGS:
        matched = [term for term in binding["terms"] if term in lowered]
        if matched:
            facets.append(
                {
                    "facet": binding["facet"],
                    "matched_terms": matched,
                    "candidate_capability_identifiers": list(binding["capabilities"]),
                }
            )
    return facets


def _compose_coverage(
    *,
    facets: list[dict[str, Any]],
    registry_by_id: dict[str, dict[str, Any]],
    route_descriptors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    routable = {str(item.get("service_identifier")): item for item in route_descriptors}
    coverage = []
    for facet in facets:
        matches = []
        for capability_id in facet["candidate_capability_identifiers"]:
            record = registry_by_id.get(capability_id)
            if not isinstance(record, dict):
                continue
            certified = (
                record.get("certification_status") in CERTIFIED_STATES
                and record.get("superseded_by") is None
            )
            matches.append(
                {
                    "capability_identifier": capability_id,
                    "certified": certified,
                    "certification_status": record.get("certification_status"),
                    "certification_scope": record.get("certification_scope"),
                    "certification_record_hash": record.get("certification_record_hash"),
                    "certification_evidence": list(record.get("certification_evidence") or []),
                    "implementation_owner": record.get("implementation_owner"),
                    "service_routable": capability_id in routable,
                    "route_descriptor_hash": (
                        routable[capability_id].get("route_descriptor_hash")
                        if capability_id in routable
                        else None
                    ),
                }
            )
        coverage.append(
            {
                "facet": facet["facet"],
                "matched_terms": list(facet["matched_terms"]),
                "covered": any(item["certified"] for item in matches),
                "certified_capability_matches": matches,
                "coverage_basis": "CERTIFICATION_REGISTRY_AND_ROUTE_DESCRIPTOR",
            }
        )
    return coverage


def _residual_gaps(coverage: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "facet": item["facet"],
            "reason": "No current non-superseded certified capability covers the request facet.",
            "gap_classification": "UNCOVERED_CAPABILITY_FACET",
        }
        for item in coverage
        if item.get("covered") is not True
    ]


def _certified_compositions(
    *,
    registry: list[dict[str, Any]],
    coverage: list[dict[str, Any]],
    generation_profile: dict[str, Any],
    governance_root: Path,
) -> list[dict[str, Any]]:
    discovered = set(_discovered_capability_ids(coverage))
    generation_dependencies = tuple(generation_profile.get("required_capabilities") or ())
    dependencies = dict(KNOWN_COMPOSITION_DEPENDENCIES)
    dependencies["GENERATION_CERTIFICATION_COMPOSITION_SERVICE"] = generation_dependencies
    results = []
    for record in registry:
        capability_id = str(record.get("capability_identifier") or "")
        verification_type = str(record.get("verification_type") or "")
        if "COMPOSITION" not in verification_type:
            continue
        composed = list(dependencies.get(capability_id, ()))
        supplied = {capability_id, *composed}
        matched = sorted(discovered.intersection(supplied))
        if discovered and not matched:
            continue
        governance = [
            _resolve_governance_reference(reference, governance_root)
            for reference in record.get("certification_evidence", ())
        ]
        results.append(
            {
                "composition_identifier": capability_id,
                "certification_status": record.get("certification_status"),
                "certification_record_hash": record.get("certification_record_hash"),
                "composed_capabilities": composed,
                "matched_requested_capabilities": matched,
                "covers_all_discovered_capabilities": bool(discovered) and discovered.issubset(supplied),
                "governance_evidence": governance,
                "reusable": record.get("certification_status") in CERTIFIED_STATES
                and record.get("superseded_by") is None,
            }
        )
    return sorted(results, key=lambda item: item["composition_identifier"])


def _minimal_extension(
    *,
    coverage: list[dict[str, Any]],
    residual_gaps: list[dict[str, Any]],
    compositions: list[dict[str, Any]],
) -> dict[str, Any]:
    discovered = _discovered_capability_ids(coverage)
    if not coverage:
        return {
            "classification": DISCOVERY_AMBIGUOUS_FAILED_CLOSED,
            "required": False,
            "recommended_components": [],
            "rationale": "No deterministic capability facet could be resolved.",
        }
    if residual_gaps:
        return {
            "classification": GENUINELY_NEW_CAPABILITY_REQUIRED,
            "required": True,
            "recommended_components": discovered,
            "rationale": "At least one request facet has no certified capability coverage.",
        }
    complete_compositions = [
        item for item in compositions if item.get("covers_all_discovered_capabilities") is True
    ]
    if complete_compositions:
        return {
            "classification": NO_GAP_EXISTING_CERTIFIED_COMPOSITION_SUFFICIENT,
            "required": False,
            "recommended_components": [complete_compositions[0]["composition_identifier"]],
            "rationale": "An existing certified composition covers all discovered capabilities.",
        }
    if len(discovered) == 1:
        return {
            "classification": NO_GAP_EXISTING_CAPABILITY_SUFFICIENT,
            "required": False,
            "recommended_components": discovered,
            "rationale": "One existing certified capability covers the request.",
        }
    return {
        "classification": MINIMAL_COMPOSITION_SERVICE_REQUIRED,
        "required": True,
        "recommended_components": discovered,
        "rationale": "Certified capabilities exist but no known certified composition covers the complete set.",
    }


def _resolve_replay_evidence(evidence_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for evidence in evidence_items:
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("capability composition replay evidence must be an object")
        body = deepcopy(evidence)
        actual_hash = body.pop("artifact_hash", None)
        hash_valid = isinstance(actual_hash, str) and replay_hash(body) == actual_hash
        results.append(
            {
                "artifact_type": evidence.get("artifact_type"),
                "artifact_hash": actual_hash,
                "hash_valid": hash_valid,
                "lineage_complete": evidence.get(
                    "replay_lineage_preserved",
                    evidence.get("lineage_complete", True),
                )
                is True,
                "read_only": True,
            }
        )
    return results


def _route_descriptors() -> list[dict[str, Any]]:
    from aigol.runtime.platform_query_router import platform_query_route_descriptors

    return platform_query_route_descriptors()


def _resolve_governance_reference(reference: Any, root: Path) -> dict[str, Any]:
    value = _require_string(reference, "governance evidence reference")
    path = root / value
    if not path.is_file():
        return {"reference": value, "present": False, "artifact_hash": None}
    return {
        "reference": value,
        "present": True,
        "artifact_hash": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _governance_evidence(compositions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence = []
    seen = set()
    for composition in compositions:
        for item in composition.get("governance_evidence", []):
            reference = item.get("reference")
            if reference not in seen:
                evidence.append(deepcopy(item))
                seen.add(reference)
    return evidence


def _discovered_capabilities(coverage: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = {}
    for item in coverage:
        for match in item.get("certified_capability_matches", []):
            capability_id = str(match["capability_identifier"])
            value = results.setdefault(
                capability_id,
                {
                    "capability_identifier": capability_id,
                    "certified": match["certified"],
                    "implementation_owner": match["implementation_owner"],
                    "service_routable": match["service_routable"],
                    "covered_facets": [],
                    "certification_record_hash": match["certification_record_hash"],
                },
            )
            value["covered_facets"].append(item["facet"])
    return [results[key] for key in sorted(results)]


def _discovered_capability_ids(coverage: list[dict[str, Any]]) -> list[str]:
    return [item["capability_identifier"] for item in _discovered_capabilities(coverage)]


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


__all__ = [
    "COVERAGE_COMPLETE",
    "COVERAGE_FAILED_CLOSED",
    "COVERAGE_PARTIAL",
    "DISCOVERY_AMBIGUOUS_FAILED_CLOSED",
    "GENUINELY_NEW_CAPABILITY_REQUIRED",
    "MINIMAL_COMPOSITION_SERVICE_REQUIRED",
    "NO_GAP_EXISTING_CAPABILITY_SUFFICIENT",
    "NO_GAP_EXISTING_CERTIFIED_COMPOSITION_SUFFICIENT",
    "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1",
    "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1",
    "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION",
    "create_platform_capability_composition_coverage_request",
    "discover_platform_capability_composition_coverage",
    "validate_platform_capability_composition_coverage",
    "validate_platform_capability_composition_coverage_request",
]
