"""Canonical read-only Platform Development Composition Plan for G20-05."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.generation_certification_composition import (
    GENERATION_CERTIFICATION_COMPOSITION_VERSION,
)
from aigol.runtime.implementation_manifest_runtime import (
    AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_VERSION,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    COVERAGE_FAILED_CLOSED,
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION,
    discover_platform_capability_composition_coverage,
    validate_platform_capability_composition_coverage,
)
from aigol.runtime.platform_capability_certification_registry import (
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
)
from aigol.runtime.platform_core_governance_preview import (
    PLATFORM_CORE_GOVERNANCE_PREVIEW_VERSION,
    governance_checkpoints,
)
from aigol.runtime.platform_core_replay_preview import (
    PLATFORM_CORE_REPLAY_PREVIEW_VERSION,
)
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_VERSION = (
    "G20_05_PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME_V1"
)
PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1 = (
    "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1"
)

DEVELOPMENT_COMPOSITION_PLAN_READY = "DEVELOPMENT_COMPOSITION_PLAN_READY"
DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED = (
    "DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED"
)
DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED = "DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED"

PLAN_BOUNDARY_FLAGS = {
    "read_only": True,
    "advisory_only": True,
    "platform_core_authority": True,
    "composition_service_only": True,
    "new_planning_engine_created": False,
    "coverage_runtime_replaced": False,
    "execution_planning_replaced": False,
    "governance_authority_created": False,
    "certification_authority_created": False,
    "human_interface_authority": False,
    "approval_created": False,
    "execution_authorized": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "repository_mutated": False,
    "governance_modified": False,
    "replay_modified": False,
    "deployment_performed": False,
}


def compose_platform_development_plan(
    *,
    capability_coverage_artifact: dict[str, Any],
    created_at: str = "2026-07-11T00:00:00Z",
) -> dict[str, Any]:
    """Transform validated G20-03 coverage into one advisory development plan."""

    try:
        coverage = validate_platform_capability_composition_coverage(
            capability_coverage_artifact
        )
        if coverage.get("coverage_status") == COVERAGE_FAILED_CLOSED:
            raise FailClosedRuntimeError(
                "development composition plan failed closed: capability coverage failed closed"
            )
        minimal_extension = deepcopy(
            coverage.get("minimal_required_platform_extension") or {}
        )
        implementation_required = minimal_extension.get("required") is True
        reusable_capabilities = deepcopy(
            coverage.get("discovered_reusable_capabilities") or []
        )
        reusable_compositions = [
            deepcopy(item)
            for item in coverage.get("certified_reusable_compositions", [])
            if isinstance(item, dict) and item.get("reusable") is True
        ]
        residual_gaps = deepcopy(coverage.get("uncovered_residual_gaps") or [])
        work_items = _implementation_work_items(
            implementation_required=implementation_required,
            reusable_capabilities=reusable_capabilities,
            residual_gaps=residual_gaps,
            minimal_extension=minimal_extension,
        )
        dependency_graph = _dependency_graph(work_items)
        status = (
            DEVELOPMENT_COMPOSITION_PLAN_READY
            if implementation_required
            else DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED
        )
        failure_reason = None
    except Exception as exc:
        coverage = deepcopy(capability_coverage_artifact)
        minimal_extension = {}
        implementation_required = False
        reusable_capabilities = []
        reusable_compositions = []
        residual_gaps = []
        work_items = []
        dependency_graph = {"nodes": [], "edges": [], "topological_order": []}
        status = DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED
        failure_reason = str(exc) or "development composition plan failed closed"

    governance_dependencies = _governance_dependencies()
    certification_dependencies = _certification_dependencies(
        reusable_capabilities=reusable_capabilities,
        reusable_compositions=reusable_compositions,
        implementation_required=implementation_required,
    )
    replay_dependencies = _replay_dependencies()
    validation_requirements = _validation_requirements(implementation_required)
    boundary = _implementation_boundary(
        implementation_required=implementation_required,
        minimal_extension=minimal_extension,
    )
    artifact = {
        "artifact_type": PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1,
        "runtime_version": PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_VERSION,
        "created_at": _require_string(created_at, "created_at"),
        "plan_status": status,
        "source_request": coverage.get("query") if isinstance(coverage, dict) else None,
        "source_request_hash": coverage.get("query_hash") if isinstance(coverage, dict) else None,
        "capability_coverage_reference": (
            coverage.get("artifact_type") if isinstance(coverage, dict) else None
        ),
        "capability_coverage_hash": (
            coverage.get("artifact_hash") if isinstance(coverage, dict) else None
        ),
        "capability_coverage_runtime_version": PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION,
        "reusable_certified_capabilities": reusable_capabilities,
        "reusable_certified_compositions": reusable_compositions,
        "residual_capability_gaps": residual_gaps,
        "minimal_required_platform_extension": minimal_extension,
        "implementation_required": implementation_required,
        "required_implementation_work": work_items,
        "ordered_implementation_sequence": [
            item["work_item_id"] for item in work_items
        ],
        "dependency_graph": dependency_graph,
        "governance_dependencies": governance_dependencies,
        "certification_dependencies": certification_dependencies,
        "replay_dependencies": replay_dependencies,
        "validation_requirements": validation_requirements,
        "implementation_boundary": boundary,
        "planning_contracts_reused": {
            "governance_preview_version": PLATFORM_CORE_GOVERNANCE_PREVIEW_VERSION,
            "replay_preview_version": PLATFORM_CORE_REPLAY_PREVIEW_VERSION,
            "implementation_manifest_runtime_version": (
                AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_VERSION
            ),
            "generation_certification_composition_version": (
                GENERATION_CERTIFICATION_COMPOSITION_VERSION
            ),
            "capability_certification_registry_version": (
                PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION
            ),
        },
        "failure_reason": failure_reason,
        "replay_visible": True,
        "requires_future_human_approval": implementation_required,
        "requires_separate_execution_authorization": implementation_required,
        "reused_platform_core_services": [
            "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME",
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
            "GENERATION_CERTIFICATION_COMPOSITION_SERVICE",
            "UNIFIED_PLATFORM_QUERY_ROUTER",
            "PLATFORM_CORE_GOVERNANCE_PREVIEW",
            "PLATFORM_CORE_REPLAY_PREVIEW",
            "IMPLEMENTATION_MANIFEST_RUNTIME",
        ],
        **PLAN_BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def compose_platform_development_plan_for_query(
    *,
    query: str,
    workspace_state: dict[str, Any] | None = None,
    replay_evidence: list[dict[str, Any]] | None = None,
    governance_root: str = ".",
    created_at: str = "2026-07-11T00:00:00Z",
) -> dict[str, Any]:
    """Compose coverage first, then create its canonical development plan."""

    coverage = discover_platform_capability_composition_coverage(
        query=query,
        workspace_state=workspace_state,
        replay_evidence=replay_evidence,
        governance_root=governance_root,
        created_at=created_at,
    )
    return compose_platform_development_plan(
        capability_coverage_artifact=coverage,
        created_at=created_at,
    )


def validate_platform_development_composition_plan(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate a canonical development composition plan artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("development composition plan must be a dict")
    if artifact.get("artifact_type") != PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1:
        raise FailClosedRuntimeError("development composition plan artifact type is invalid")
    if artifact.get("runtime_version") != PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_VERSION:
        raise FailClosedRuntimeError("development composition plan version is invalid")
    if artifact.get("plan_status") not in {
        DEVELOPMENT_COMPOSITION_PLAN_READY,
        DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED,
        DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("development composition plan status is invalid")
    for field, expected in PLAN_BOUNDARY_FLAGS.items():
        if artifact.get(field) is not expected:
            raise FailClosedRuntimeError("development composition plan boundary flags invalid")
    body = deepcopy(artifact)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("development composition plan hash mismatch")
    return deepcopy(artifact)


def _implementation_work_items(
    *,
    implementation_required: bool,
    reusable_capabilities: list[dict[str, Any]],
    residual_gaps: list[dict[str, Any]],
    minimal_extension: dict[str, Any],
) -> list[dict[str, Any]]:
    items = [
        _work_item(
            "REUSE_CERTIFIED_CAPABILITIES",
            10,
            "Bind existing certified capabilities and compositions without duplication.",
            [str(item.get("capability_identifier")) for item in reusable_capabilities],
            [],
        )
    ]
    if not implementation_required:
        items.append(
            _work_item(
                "VERIFY_EXISTING_COMPOSITION",
                20,
                "Validate that the existing capability or composition satisfies the request.",
                ["CAPABILITY_COVERAGE_EVIDENCE", "CERTIFICATION_EVIDENCE"],
                ["REUSE_CERTIFIED_CAPABILITIES"],
            )
        )
        return items
    items.extend(
        [
            _work_item(
                "IMPLEMENT_RESIDUAL_CAPABILITY_GAPS",
                20,
                "Implement only uncovered residual capability or composition gaps.",
                [str(item.get("facet")) for item in residual_gaps]
                or list(minimal_extension.get("recommended_components") or []),
                ["REUSE_CERTIFIED_CAPABILITIES"],
            ),
            _work_item(
                "DEFINE_CANONICAL_ARTIFACT_CONTRACT",
                30,
                "Define one deterministic, hash-bound, fail-closed Platform artifact.",
                ["CANONICAL_ARTIFACT", "VALIDATOR", "BOUNDARY_FLAGS"],
                ["IMPLEMENT_RESIDUAL_CAPABILITY_GAPS"],
            ),
            _work_item(
                "BIND_PLATFORM_QUERY_ROUTER",
                40,
                "Register the minimal Platform service route and required-input contract.",
                ["ROUTE_DESCRIPTOR", "ROUTE_ADAPTER"],
                ["DEFINE_CANONICAL_ARTIFACT_CONTRACT"],
            ),
            _work_item(
                "BIND_CANONICAL_PRESENTATION",
                50,
                "Normalize the new artifact through the existing presentation layer.",
                ["PRESENTATION_ADAPTER"],
                ["BIND_PLATFORM_QUERY_ROUTER"],
            ),
            _work_item(
                "ADD_FAIL_CLOSED_REGRESSIONS",
                60,
                "Prove deterministic success, ambiguity, hash, lineage, and boundary behavior.",
                ["FOCUSED_TESTS", "ROUTER_TESTS", "PRESENTATION_TESTS"],
                ["BIND_CANONICAL_PRESENTATION"],
            ),
            _work_item(
                "VALIDATE_GOVERNANCE_CONFORMANCE",
                70,
                "Run focused, conformance, full-suite, compilation, and diff validation.",
                ["GOVERNANCE_CONFORMANCE", "FULL_REGRESSION", "PY_COMPILE", "DIFF_CHECK"],
                ["ADD_FAIL_CLOSED_REGRESSIONS"],
            ),
            _work_item(
                "RECORD_IMPLEMENTATION_CERTIFICATION_METADATA",
                80,
                "Record certification metadata only after implementation evidence validates.",
                ["GOVERNANCE_REPORT", "CERTIFICATION_REGISTRY_RECORD"],
                ["VALIDATE_GOVERNANCE_CONFORMANCE"],
            ),
        ]
    )
    return items


def _work_item(
    work_item_id: str,
    order: int,
    description: str,
    expected_outputs: list[str],
    depends_on: list[str],
) -> dict[str, Any]:
    return {
        "work_item_id": work_item_id,
        "order": order,
        "description": description,
        "expected_outputs": expected_outputs,
        "depends_on": depends_on,
        "advisory_only": True,
        "execution_authorized": False,
    }


def _dependency_graph(work_items: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = [item["work_item_id"] for item in work_items]
    edges = [
        {"from": dependency, "to": item["work_item_id"]}
        for item in work_items
        for dependency in item["depends_on"]
    ]
    return {"nodes": nodes, "edges": edges, "topological_order": nodes}


def _governance_dependencies() -> list[dict[str, Any]]:
    return [
        *deepcopy(governance_checkpoints()),
        {
            "checkpoint": "constitutional_invariants",
            "required_state": "preserved",
        },
        {"checkpoint": "mutation_boundaries", "required_state": "declared"},
        {"checkpoint": "known_limitations", "required_state": "visible"},
    ]


def _certification_dependencies(
    *,
    reusable_capabilities: list[dict[str, Any]],
    reusable_compositions: list[dict[str, Any]],
    implementation_required: bool,
) -> list[dict[str, Any]]:
    dependencies = [
        {
            "dependency_type": "REUSABLE_CAPABILITY_CERTIFICATION",
            "capability_identifier": item.get("capability_identifier"),
            "certification_record_hash": item.get("certification_record_hash"),
            "required_state": "CERTIFIED_OR_VERIFIED_NOT_SUPERSEDED",
        }
        for item in reusable_capabilities
    ]
    dependencies.extend(
        {
            "dependency_type": "REUSABLE_COMPOSITION_CERTIFICATION",
            "composition_identifier": item.get("composition_identifier"),
            "certification_record_hash": item.get("certification_record_hash"),
            "required_state": "CERTIFIED_NOT_SUPERSEDED",
        }
        for item in reusable_compositions
    )
    if implementation_required:
        dependencies.append(
            {
                "dependency_type": "FUTURE_IMPLEMENTATION_CERTIFICATION",
                "required_state": "NOT_YET_CREATED",
                "creation_allowed_only_after_validation": True,
            }
        )
    return dependencies


def _replay_dependencies() -> list[dict[str, Any]]:
    return [
        {
            "dependency": "SOURCE_COVERAGE_ARTIFACT",
            "required_state": "HASH_VALIDATED",
            "replay_owner": "PLATFORM_CORE_REPLAY",
        },
        {
            "dependency": "DEVELOPMENT_PLAN_ARTIFACT",
            "required_state": "REPLAY_VISIBLE_READ_ONLY",
            "replay_owner": "PLATFORM_CORE_REPLAY",
        },
        {
            "dependency": "IMPLEMENTATION_EVIDENCE",
            "required_state": "FUTURE_APPEND_ONLY_AFTER_APPROVAL",
            "replay_owner": "PLATFORM_CORE_REPLAY",
        },
        {
            "dependency": "REPLAY_CERTIFICATION",
            "required_state": "FUTURE_VALIDATED_EXECUTION_ONLY",
            "replay_owner": "PLATFORM_CORE_REPLAY",
        },
    ]


def _validation_requirements(implementation_required: bool) -> list[str]:
    requirements = [
        "FOCUSED_DEVELOPMENT_COMPOSITION_PLAN_REGRESSIONS",
        "UNIFIED_PLATFORM_QUERY_ROUTER_REGRESSIONS",
        "CANONICAL_PLATFORM_PRESENTATION_REGRESSIONS",
        "GOVERNANCE_CONFORMANCE",
        "PY_COMPILE",
        "GIT_DIFF_CHECK",
    ]
    if implementation_required:
        requirements.append("FULL_REGRESSION_SUITE")
    return requirements


def _implementation_boundary(
    *,
    implementation_required: bool,
    minimal_extension: dict[str, Any],
) -> dict[str, Any]:
    return {
        "implementation_required": implementation_required,
        "minimal_extension_classification": minimal_extension.get("classification"),
        "allowed_scope": "RESIDUAL_GAPS_AND_MINIMAL_BINDINGS_ONLY",
        "reuse_first": True,
        "human_approval_required_before_implementation": implementation_required,
        "separate_execution_authorization_required": implementation_required,
        "provider_invocation_allowed_in_plan": False,
        "worker_invocation_allowed_in_plan": False,
        "repository_mutation_allowed_in_plan": False,
        "governance_mutation_allowed_in_plan": False,
        "replay_mutation_allowed_in_plan": False,
        "deployment_allowed_in_plan": False,
    }


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


__all__ = [
    "DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED",
    "DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED",
    "DEVELOPMENT_COMPOSITION_PLAN_READY",
    "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1",
    "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_VERSION",
    "compose_platform_development_plan",
    "compose_platform_development_plan_for_query",
    "validate_platform_development_composition_plan",
]
