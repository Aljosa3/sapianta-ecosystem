"""Canonical Platform Core capability certification registry.

The registry is governance metadata: it indexes certification reports without
replacing them as evidence and without granting runtime authority.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION = (
    "G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_V1"
)

AUDIT = "AUDIT"
IMPLEMENTATION = "IMPLEMENTATION"
END_TO_END = "END_TO_END"
RUNTIME = "RUNTIME"
GOVERNANCE = "GOVERNANCE"
SUPPORTED_CERTIFICATION_SCOPES = frozenset({AUDIT, IMPLEMENTATION, END_TO_END, RUNTIME, GOVERNANCE})

DRAFT = "DRAFT"
VERIFIED = "VERIFIED"
CERTIFIED = "CERTIFIED"
SUPERSEDED = "SUPERSEDED"
DEPRECATED = "DEPRECATED"
SUPPORTED_CERTIFICATION_STATES = frozenset({DRAFT, VERIFIED, CERTIFIED, SUPERSEDED, DEPRECATED})
CERTIFIED_STATES = frozenset({VERIFIED, CERTIFIED})


@dataclass(frozen=True)
class CapabilityCertificationRecord:
    """Immutable registry record for one Platform Core capability."""

    capability_identifier: str
    capability_owner: str
    certification_status: str
    certification_scope: str
    certification_milestone: str
    certification_evidence: tuple[str, ...]
    certification_date: str
    architectural_owner: str
    implementation_owner: str
    verification_type: str
    certification_version: str
    superseded_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        record = {
            "capability_identifier": _normalize_identifier(
                self.capability_identifier,
                "capability_identifier",
            ),
            "capability_owner": _require_string(self.capability_owner, "capability_owner"),
            "certification_status": _normalize_token(
                self.certification_status,
                "certification_status",
            ),
            "certification_scope": _normalize_token(
                self.certification_scope,
                "certification_scope",
            ),
            "certification_milestone": _require_string(
                self.certification_milestone,
                "certification_milestone",
            ),
            "certification_evidence": _string_tuple(
                self.certification_evidence,
                "certification_evidence",
            ),
            "certification_date": _require_string(self.certification_date, "certification_date"),
            "architectural_owner": _require_string(self.architectural_owner, "architectural_owner"),
            "implementation_owner": _require_string(self.implementation_owner, "implementation_owner"),
            "verification_type": _normalize_token(self.verification_type, "verification_type"),
            "certification_version": _require_string(
                self.certification_version,
                "certification_version",
            ),
            "superseded_by": self.superseded_by,
            "governance_metadata_only": True,
            "governance_report_evidence_authoritative": True,
            "runtime_execution_authority": False,
            "human_interface_authority": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "replay_modified": False,
            "governance_modified": False,
        }
        _validate_record_shape(record)
        record["certification_record_hash"] = replay_hash(record)
        return record


PLATFORM_CAPABILITY_CERTIFICATION_RECORDS = (
    CapabilityCertificationRecord(
        capability_identifier="REPLAY_OBSERVATION_LAYER",
        capability_owner="PLATFORM_CORE_REPLAY",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G15_01_REPLAY_OBSERVATION_LAYER_V1",
        certification_evidence=("docs/governance/G15_01_REPLAY_OBSERVATION_LAYER_V1.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.replay_observation_layer",
        verification_type="DETERMINISTIC_REPLAY_RECONSTRUCTION",
        certification_version="G15-01",
    ),
    CapabilityCertificationRecord(
        capability_identifier="CLARIFICATION_CONTINUITY",
        capability_owner="PLATFORM_CORE_HUMAN_INTENT_RESOLUTION",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G15-HIR-02",
        certification_evidence=("docs/governance/G15_HIR_02_REPLAY_BACKED_CLARIFICATION_CONTINUITY.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_project_services",
        verification_type="REPLAY_BACKED_CONTINUATION",
        certification_version="G15-HIR-02",
    ),
    CapabilityCertificationRecord(
        capability_identifier="CANONICAL_SEMANTIC_ARTIFACT",
        capability_owner="PLATFORM_CORE_SEMANTICS",
        certification_status=VERIFIED,
        certification_scope=AUDIT,
        certification_milestone="G15-SEMANTICS-01",
        certification_evidence=("docs/governance/G15_SEMANTICS_01_CANONICAL_SEMANTIC_ARTIFACT_TRANSITION_AUDIT.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.canonical_semantic_artifact_runtime",
        verification_type="GATED_ARTIFACT_TRANSITION_AUDIT",
        certification_version="G15-SEMANTICS-01",
    ),
    CapabilityCertificationRecord(
        capability_identifier="DISPATCH_REPLAY_REFERENCE_RESOLUTION",
        capability_owner="PLATFORM_CORE_REPLAY_LINEAGE",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G15-RUNTIME-04",
        certification_evidence=("docs/governance/G15_RUNTIME_04_DISPATCH_REPLAY_REFERENCE_RESOLUTION.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.worker_invocation_to_execution_candidate_bridge_runtime",
        verification_type="REPLAY_REFERENCE_REGRESSION",
        certification_version="G15-RUNTIME-04",
    ),
    CapabilityCertificationRecord(
        capability_identifier="REPLAY_CERTIFICATION_RUNTIME",
        capability_owner="PLATFORM_CORE_REPLAY",
        certification_status=CERTIFIED,
        certification_scope=RUNTIME,
        certification_milestone="G15-REPLAY-01",
        certification_evidence=(
            "docs/governance/G15_REPLAY_01_REPLAY_CERTIFICATION_LINEAGE_AUDIT.md",
            "docs/governance/G15_RUNTIME_05_END_TO_END_RUNTIME_COMPLETION_VERIFICATION.md",
        ),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.replay_certification_runtime",
        verification_type="REPLAY_CERTIFICATION_AND_END_TO_END_RUNTIME",
        certification_version="G15-REPLAY-01",
    ),
    CapabilityCertificationRecord(
        capability_identifier="GOVERNED_DEVELOPMENT_RUNTIME_END_TO_END",
        capability_owner="PLATFORM_CORE_RUNTIME",
        certification_status=CERTIFIED,
        certification_scope=END_TO_END,
        certification_milestone="G15-RUNTIME-05",
        certification_evidence=("docs/governance/G15_RUNTIME_05_END_TO_END_RUNTIME_COMPLETION_VERIFICATION.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.cli.aigol_cli",
        verification_type="END_TO_END_CERTIFIED_RUNTIME_COMPLETION",
        certification_version="G15-RUNTIME-05",
    ),
    CapabilityCertificationRecord(
        capability_identifier="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
        capability_owner="PLATFORM_CORE_RUNTIME_ENTRY",
        certification_status=CERTIFIED,
        certification_scope=RUNTIME,
        certification_milestone="G14_41_REFERENCE_UHI_RUNTIME_COMPLETION_VALIDATION_V1",
        certification_evidence=(
            "docs/governance/G14_41_REFERENCE_UHI_RUNTIME_COMPLETION_VALIDATION_V1.md",
            "docs/governance/G15_RUNTIME_05_END_TO_END_RUNTIME_COMPLETION_VERIFICATION.md",
        ),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.human_interface_runtime_entry_service",
        verification_type="CANONICAL_RUNTIME_ENTRY_BOUNDARY",
        certification_version="G14-41",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PROVIDER_PLATFORM_OPERATIONAL_COMPLETION",
        capability_owner="PROVIDER_PLATFORM",
        certification_status=CERTIFIED,
        certification_scope=RUNTIME,
        certification_milestone="G14_43_PROVIDER_PLATFORM_OPERATIONAL_COMPLETION_V1",
        certification_evidence=("docs/governance/G14_43_PROVIDER_PLATFORM_OPERATIONAL_COMPLETION_V1.md",),
        certification_date="2026-07-08",
        architectural_owner="PROVIDER_PLATFORM",
        implementation_owner="aigol.provider",
        verification_type="PROVIDER_PLATFORM_OPERATIONAL_COMPLETION",
        certification_version="G14-43",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_CORE_COGNITION_LAYER_FOUNDATION",
        capability_owner="PLATFORM_CORE_COGNITION_LAYER",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G16-01",
        certification_evidence=("docs/governance/G16_01_PCCL_FOUNDATION.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_cognition_layer",
        verification_type="IMPLEMENTATION",
        certification_version="G16-01",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PCCL_SESSION_RUNTIME",
        capability_owner="PLATFORM_CORE_COGNITION_LAYER",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G16-02",
        certification_evidence=("docs/governance/G16_02_PCCL_SESSION_RUNTIME.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_cognition_layer",
        verification_type="IMPLEMENTATION",
        certification_version="G16-02",
    ),
    CapabilityCertificationRecord(
        capability_identifier="CANONICAL_CONTEXT_ENVELOPE",
        capability_owner="PLATFORM_CORE_COGNITION_LAYER",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G16-03",
        certification_evidence=("docs/governance/G16_03_CANONICAL_CONTEXT_ENVELOPE.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_cognition_layer",
        verification_type="IMPLEMENTATION",
        certification_version="G16-03",
    ),
    CapabilityCertificationRecord(
        capability_identifier="CANONICAL_POLICY_ENVELOPE",
        capability_owner="PLATFORM_CORE_COGNITION_LAYER",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G16-04",
        certification_evidence=("docs/governance/G16_04_CANONICAL_POLICY_ENVELOPE.md",),
        certification_date="2026-07-08",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_cognition_layer",
        verification_type="IMPLEMENTATION",
        certification_version="G16-04",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PCCL_REFERENCE_BINDING",
        capability_owner="PLATFORM_CORE_COGNITION_LAYER",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G16-08",
        certification_evidence=("docs/governance/G16_08_PCCL_REFERENCE_BINDING.md",),
        certification_date="2026-07-09",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_cognition_layer",
        verification_type="IMPLEMENTATION",
        certification_version="G16-08",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PCCL_PROPOSAL_LIFECYCLE",
        capability_owner="PLATFORM_CORE_COGNITION_LAYER",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G16-09",
        certification_evidence=("docs/governance/G16_09_PCCL_PROPOSAL_LIFECYCLE_FOUNDATION.md",),
        certification_date="2026-07-09",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_cognition_layer",
        verification_type="IMPLEMENTATION",
        certification_version="G16-09",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PCCL_ORCHESTRATION_DECISION_RECORD",
        capability_owner="PLATFORM_CORE_COGNITION_LAYER",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G16-11",
        certification_evidence=("docs/governance/G16_11_PCCL_ORCHESTRATION_DECISION_RECORD.md",),
        certification_date="2026-07-09",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_cognition_layer",
        verification_type="IMPLEMENTATION",
        certification_version="G16-11",
    ),
    CapabilityCertificationRecord(
        capability_identifier="DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING",
        capability_owner="PLATFORM_CORE_REPLAY",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G18-09",
        certification_evidence=(
            "docs/governance/G18_09_DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-11",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_core_root_cause_trace",
        verification_type="DETERMINISTIC_REPLAY_BACKED_TRACE_COMPOSITION",
        certification_version="G18-09",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_KNOWLEDGE_RUNTIME",
        capability_owner="PLATFORM_CORE_KNOWLEDGE",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G19-02",
        certification_evidence=(
            "docs/governance/G19_02_PLATFORM_KNOWLEDGE_RUNTIME_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-11",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_knowledge_runtime",
        verification_type="DETERMINISTIC_PLATFORM_KNOWLEDGE_COMPOSITION",
        certification_version="G19-02",
    ),
    CapabilityCertificationRecord(
        capability_identifier="UNIFIED_PLATFORM_QUERY_ROUTER",
        capability_owner="PLATFORM_CORE_QUERY_ROUTING",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G19-04",
        certification_evidence=(
            "docs/governance/G19_04_UNIFIED_PLATFORM_QUERY_ROUTER_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-11",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_query_router",
        verification_type="DETERMINISTIC_PLATFORM_QUERY_ROUTING_COMPOSITION",
        certification_version="G19-04",
    ),
    CapabilityCertificationRecord(
        capability_identifier="CANONICAL_PLATFORM_PRESENTATION_LAYER",
        capability_owner="PLATFORM_CORE_PRESENTATION",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G19-06",
        certification_evidence=(
            "docs/governance/G19_06_CANONICAL_PLATFORM_PRESENTATION_LAYER_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-11",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_presentation_layer",
        verification_type="DETERMINISTIC_PLATFORM_PRESENTATION_COMPOSITION",
        certification_version="G19-06",
    ),
    CapabilityCertificationRecord(
        capability_identifier="GENERATION_CERTIFICATION_COMPOSITION_SERVICE",
        capability_owner="PLATFORM_CORE_CERTIFICATION",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G20-01",
        certification_evidence=(
            "docs/governance/G20_01_GENERATION_CERTIFICATION_COMPOSITION_SERVICE_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-11",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.generation_certification_composition",
        verification_type="DETERMINISTIC_GENERATION_CERTIFICATION_COMPOSITION",
        certification_version="G20-01",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME",
        capability_owner="PLATFORM_CORE_CAPABILITY_DISCOVERY",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G20-03",
        certification_evidence=(
            "docs/governance/G20_03_PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-11",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_capability_composition_coverage",
        verification_type="DETERMINISTIC_MULTI_CAPABILITY_COVERAGE_COMPOSITION",
        certification_version="G20-03",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME",
        capability_owner="PLATFORM_CORE_DEVELOPMENT_PLANNING",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G20-05",
        certification_evidence=(
            "docs/governance/G20_05_PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-11",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_development_composition_plan",
        verification_type="DETERMINISTIC_COVERAGE_TO_DEVELOPMENT_PLAN_COMPOSITION",
        certification_version="G20-05",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_PROJECT_OBJECTIVE_INFERENCE_RUNTIME",
        capability_owner="PLATFORM_CORE_HUMAN_INTENT",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G21-02",
        certification_evidence=(
            "docs/governance/G21_02_PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_RUNTIME_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-11",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_project_objective_inference",
        verification_type="DETERMINISTIC_COMPLETE_REQUEST_TO_PROJECT_OBJECTIVE_COMPOSITION",
        certification_version="G21-02",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME",
        capability_owner="PLATFORM_CORE_DEVELOPMENT_LIFECYCLE",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G21-05",
        certification_evidence=(
            "docs/governance/G21_05_DURABLE_GOVERNED_WORK_ARTIFACT_RUNTIME_IMPLEMENTATION.md",
        ),
        certification_date="2026-07-12",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_durable_governed_work",
        verification_type="DETERMINISTIC_PLAN_TO_DURABLE_GOVERNED_WORK_BINDING",
        certification_version="G21-05",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_CHANGE_NORMALIZATION",
        capability_owner="PLATFORM_CORE_CHANGE_EVIDENCE",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G27-04",
        certification_evidence=(
            "docs/governance/G27_04_PLATFORM_CHANGE_NORMALIZATION_CAPABILITY.md",
        ),
        certification_date="2026-07-13",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_change_normalization_runtime",
        verification_type="DETERMINISTIC_CHANGE_ARTIFACT_NORMALIZATION",
        certification_version="G27-04",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_CHANGE_IMPACT_ANALYSIS",
        capability_owner="PLATFORM_CORE_CHANGE_EVIDENCE",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G27-05",
        certification_evidence=(
            "docs/governance/G27_05_PLATFORM_CHANGE_IMPACT_ANALYSIS.md",
        ),
        certification_date="2026-07-13",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_change_impact_analysis_runtime",
        verification_type="DETERMINISTIC_PLATFORM_CHANGE_IMPACT_ANALYSIS",
        certification_version="G27-05",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_VALIDATION_PLANNING",
        capability_owner="PLATFORM_CORE_VALIDATION_PLANNING",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G27-07",
        certification_evidence=(
            "docs/governance/G27_07_PLATFORM_VALIDATION_PLANNING.md",
        ),
        certification_date="2026-07-13",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_validation_planning_runtime",
        verification_type="DETERMINISTIC_PLATFORM_VALIDATION_PLANNING",
        certification_version="G27-07",
    ),
    CapabilityCertificationRecord(
        capability_identifier="PLATFORM_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION",
        capability_owner="PLATFORM_CORE_VALIDATION_PLANNING",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G27-09",
        certification_evidence=(
            "docs/governance/G27_09_PLATFORM_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION.md",
        ),
        certification_date="2026-07-13",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.platform_validation_plan_candidate_composition_runtime",
        verification_type="DETERMINISTIC_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION",
        certification_version="G27-09",
    ),
    CapabilityCertificationRecord(
        capability_identifier="VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF",
        capability_owner="PLATFORM_CORE_REPLAY_LINEAGE",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G27-11",
        certification_evidence=(
            "docs/governance/G27_11_VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF.md",
        ),
        certification_date="2026-07-13",
        architectural_owner="PLATFORM_CORE",
        implementation_owner=(
            "aigol.runtime.validation_completion_replay_certification_handoff_runtime"
        ),
        verification_type="DETERMINISTIC_VALIDATION_COMPLETION_CERTIFICATION_HANDOFF",
        certification_version="G27-11",
    ),
    CapabilityCertificationRecord(
        capability_identifier="CERTIFIED_CAPABILITY_INVOCATION_BINDING",
        capability_owner="PLATFORM_CORE_CAPABILITY_DELEGATION",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G28-02",
        certification_evidence=(
            "docs/governance/G28_02_CERTIFIED_CAPABILITY_INVOCATION_BINDING.md",
        ),
        certification_date="2026-07-13",
        architectural_owner="PLATFORM_CORE",
        implementation_owner=(
            "aigol.runtime.certified_capability_invocation_binding_runtime"
        ),
        verification_type="DETERMINISTIC_ALLOWLISTED_CAPABILITY_INVOCATION_BINDING",
        certification_version="G28-02",
    ),
    CapabilityCertificationRecord(
        capability_identifier="CANONICAL_SEMANTIC_CAPABILITY_SELECTION_BINDING",
        capability_owner="PLATFORM_CORE_SEMANTIC_CAPABILITY_SELECTION",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G29-02",
        certification_evidence=(
            "docs/governance/G29_02_CANONICAL_SEMANTIC_CAPABILITY_SELECTION_BINDING.md",
        ),
        certification_date="2026-07-13",
        architectural_owner="PLATFORM_CORE",
        implementation_owner="aigol.runtime.semantic_capability_selection_runtime",
        verification_type="DETERMINISTIC_SEMANTIC_CAPABILITY_SELECTION_BINDING",
        certification_version="G29-02",
    ),
    CapabilityCertificationRecord(
        capability_identifier=(
            "CANONICAL_SEMANTIC_SELECTION_TO_CERTIFIED_CAPABILITY_INVOCATION_LIFECYCLE_BINDING"
        ),
        capability_owner="PLATFORM_CORE_CAPABILITY_INVOCATION_LIFECYCLE",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G29-04",
        certification_evidence=(
            "docs/governance/G29_04_CANONICAL_SEMANTIC_SELECTION_TO_CERTIFIED_CAPABILITY_INVOCATION_LIFECYCLE_BINDING.md",
        ),
        certification_date="2026-07-14",
        architectural_owner="PLATFORM_CORE",
        implementation_owner=(
            "aigol.runtime.semantic_capability_invocation_lifecycle_runtime"
        ),
        verification_type=(
            "DETERMINISTIC_SEMANTIC_SELECTION_TO_CERTIFIED_INVOCATION_LIFECYCLE_BINDING"
        ),
        certification_version="G29-04",
    ),
    CapabilityCertificationRecord(
        capability_identifier=(
            "CANONICAL_PROJECT_CONTEXT_TO_SEMANTIC_CAPABILITY_RUNTIME_ROUTE_BINDING"
        ),
        capability_owner="PLATFORM_CORE_SEMANTIC_CAPABILITY_RUNTIME_ROUTING",
        certification_status=CERTIFIED,
        certification_scope=IMPLEMENTATION,
        certification_milestone="G29-06",
        certification_evidence=(
            "docs/governance/G29_06_CANONICAL_PROJECT_CONTEXT_TO_SEMANTIC_CAPABILITY_RUNTIME_ROUTE_BINDING.md",
        ),
        certification_date="2026-07-14",
        architectural_owner="PLATFORM_CORE",
        implementation_owner=(
            "aigol.runtime.project_context_semantic_capability_route"
        ),
        verification_type=(
            "DETERMINISTIC_PROJECT_CONTEXT_TO_SEMANTIC_CAPABILITY_RUNTIME_ROUTE_BINDING"
        ),
        certification_version="G29-06",
    ),
)


def platform_capability_certification_registry() -> dict[str, dict[str, Any]]:
    """Return the canonical runtime-readable certification registry."""

    registry: dict[str, dict[str, Any]] = {}
    for source_record in PLATFORM_CAPABILITY_CERTIFICATION_RECORDS:
        record = source_record.to_dict()
        capability_id = record["capability_identifier"]
        if capability_id in registry:
            raise FailClosedRuntimeError("capability certification registry duplicate capability")
        registry[capability_id] = record
    return {capability_id: deepcopy(registry[capability_id]) for capability_id in sorted(registry)}


def list_platform_capability_certifications() -> list[dict[str, Any]]:
    """Return all capability certification records in deterministic order."""

    return [deepcopy(record) for record in platform_capability_certification_registry().values()]


def lookup_platform_capability_certification(capability_identifier: str) -> dict[str, Any]:
    """Lookup one capability certification record by capability identifier."""

    capability_id = _normalize_identifier(capability_identifier, "capability_identifier")
    registry = platform_capability_certification_registry()
    record = registry.get(capability_id)
    if record is None:
        raise FailClosedRuntimeError("platform capability certification registry failed closed: unknown capability")
    return deepcopy(record)


def is_platform_capability_certified(capability_identifier: str) -> bool:
    """Return whether the capability currently has a certified or verified status."""

    record = lookup_platform_capability_certification(capability_identifier)
    return record["certification_status"] in CERTIFIED_STATES and record["superseded_by"] is None


def platform_capability_certification_milestone(capability_identifier: str) -> str:
    """Return the milestone that certified or verified the capability."""

    return str(lookup_platform_capability_certification(capability_identifier)["certification_milestone"])


def platform_capability_certification_evidence(capability_identifier: str) -> tuple[str, ...]:
    """Return immutable governance report references for the capability."""

    record = lookup_platform_capability_certification(capability_identifier)
    return tuple(record["certification_evidence"])


def platform_capability_certification_scope(capability_identifier: str) -> str:
    """Return the certification scope for the capability."""

    return str(lookup_platform_capability_certification(capability_identifier)["certification_scope"])


def is_platform_capability_superseded(capability_identifier: str) -> bool:
    """Return whether the capability certification has been superseded."""

    record = lookup_platform_capability_certification(capability_identifier)
    return record["certification_status"] == SUPERSEDED or record["superseded_by"] is not None


def platform_capability_owner(capability_identifier: str) -> str:
    """Return the Platform component that owns the capability."""

    return str(lookup_platform_capability_certification(capability_identifier)["capability_owner"])


def platform_capability_component_owner(capability_identifier: str) -> str:
    """Return the implementation owner for the capability."""

    return str(lookup_platform_capability_certification(capability_identifier)["implementation_owner"])


def _validate_record_shape(record: dict[str, Any]) -> None:
    if record["certification_status"] not in SUPPORTED_CERTIFICATION_STATES:
        raise FailClosedRuntimeError("capability certification status is invalid")
    if record["certification_scope"] not in SUPPORTED_CERTIFICATION_SCOPES:
        raise FailClosedRuntimeError("capability certification scope is invalid")
    if record["verification_type"] not in SUPPORTED_CERTIFICATION_SCOPES and not record["verification_type"]:
        raise FailClosedRuntimeError("capability verification type is invalid")
    if record["superseded_by"] is not None and not isinstance(record["superseded_by"], str):
        raise FailClosedRuntimeError("capability superseded_by must be string or null")
    for flag in (
        "governance_metadata_only",
        "governance_report_evidence_authoritative",
    ):
        if record.get(flag) is not True:
            raise FailClosedRuntimeError("capability certification registry authority flags invalid")
    for flag in (
        "runtime_execution_authority",
        "human_interface_authority",
        "provider_invoked",
        "worker_invoked",
        "replay_modified",
        "governance_modified",
    ):
        if record.get(flag) is not False:
            raise FailClosedRuntimeError("capability certification registry boundary flags invalid")


def _string_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple) or not values:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return tuple(_require_string(value, field_name) for value in values)


def _normalize_identifier(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_").replace(" ", "_")


def _normalize_token(value: Any, field_name: str) -> str:
    return _normalize_identifier(value, field_name)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
