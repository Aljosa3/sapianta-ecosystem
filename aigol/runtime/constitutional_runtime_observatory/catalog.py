"""Closed, versioned evidence adapter catalog for the G67-02 CRO core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from aigol.runtime.execution_authorization_runtime import (
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.execution_runtime import reconstruct_execution_replay
from aigol.runtime.governed_termination_runtime import (
    reconstruct_governed_termination_replay,
)
from aigol.runtime.human_interface_conversation_execution_integration_v2 import (
    reconstruct_committed_objective_execution_preparation_v2,
)
from aigol.runtime.platform_change_normalization_worker_completion_adapter import (
    reconstruct_platform_change_normalization_worker_completion_replay,
)
from aigol.runtime.post_execution_replay_review_runtime import (
    reconstruct_post_execution_replay_review,
)
from aigol.runtime.production_conversation_flow_binding import (
    reconstruct_production_conversation_flow_binding_v1,
)
from aigol.runtime.replay_certification_runtime import (
    reconstruct_replay_certification_replay,
)
from aigol.runtime.worker_assignment_runtime import (
    reconstruct_worker_assignment_runtime_replay,
)
from aigol.runtime.worker_dispatch_runtime import reconstruct_worker_dispatch_replay
from aigol.runtime.worker_invocation_request_runtime import (
    reconstruct_worker_invocation_request_replay,
)
from aigol.runtime.worker_invocation_runtime import (
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_result_capture_runtime import (
    reconstruct_worker_result_capture_replay,
)
from aigol.runtime.worker_result_validation_runtime import (
    reconstruct_worker_result_validation_replay,
)


ADAPTER_CATALOG_VERSION = "G67_02_EVIDENCE_ADAPTER_CATALOG_V1"


@dataclass(frozen=True)
class EvidenceAdapter:
    adapter_id: str
    source_artifact_type: str
    source_version: str
    source_owner: str
    root_kind: str
    principal_file: str | None
    stages: tuple[str, ...]
    event_classification: str
    certified_generation: str
    reconstructor_name: str
    reconstructor: Callable[[Any], dict[str, Any]]


def _adapter(
    adapter_id: str,
    source_artifact_type: str,
    source_version: str,
    owner: str,
    root_kind: str,
    principal_file: str | None,
    stages: tuple[str, ...],
    event_classification: str,
    generation: str,
    reconstructor: Callable[[Any], dict[str, Any]],
) -> EvidenceAdapter:
    return EvidenceAdapter(
        adapter_id,
        source_artifact_type,
        source_version,
        owner,
        root_kind,
        principal_file,
        stages,
        event_classification,
        generation,
        f"{reconstructor.__module__}.{reconstructor.__name__}",
        reconstructor,
    )


CATALOG = (
    _adapter("G66_FLOW_BINDING", "PRODUCTION_CONVERSATION_FLOW_BINDING_V1", "V1", "G66_CONVERSATION_FLOW_BINDING", "DIRECTORY", None, (), "CONVERSATION", "G66-01..18", reconstruct_production_conversation_flow_binding_v1),
    _adapter("G60_EXECUTION_PREPARATION", "COMMITTED_OBJECTIVE_EXECUTION_PREPARATION_ARTIFACT_V1", "FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2", "G60_02_ORCHESTRATION", "FILE", None, ("COMMITMENT_HANDOFF", "PLATFORM_OBJECTIVE", "PLATFORM_ADMISSION", "PRODUCTION_REUSE_PROOF", "DEVELOPMENT_GOVERNANCE", "CAPABILITY_ROUTE", "EXECUTION_PREPARATION", "EXECUTION_SUMMARY", "HUMAN_EXECUTION_DECISION"), "ADMISSION_AND_PREPARATION", "G60-02/G66-14", reconstruct_committed_objective_execution_preparation_v2),
    _adapter("EXECUTION_AUTHORIZATION", "EXECUTION_AUTHORIZATION_ARTIFACT_V1", "AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_V1", "EXECUTION_AUTHORIZATION", "DIRECTORY", "002_authorization_artifact_recorded.json", ("EXECUTION_AUTHORIZATION",), "AUTHORIZATION", "G31/G66-14", reconstruct_execution_authorization_replay),
    _adapter("WORKER_INVOCATION_REQUEST", "WORKER_INVOCATION_REQUEST_ARTIFACT_V1", "AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_V1", "WORKER_INVOCATION_REQUEST", "DIRECTORY", "002_invocation_request_artifact_recorded.json", ("RESOURCE_SELECTION", "WORKER_INVOCATION_REQUEST"), "WORKER", "G31/G66-14", reconstruct_worker_invocation_request_replay),
    _adapter("WORKER_ASSIGNMENT", "WORKER_ASSIGNMENT_ARTIFACT_V1", "V1", "WORKER_ASSIGNMENT", "DIRECTORY", "002_assignment_artifact_recorded.json", ("WORKER_ASSIGNMENT",), "WORKER", "G31/G66-14", reconstruct_worker_assignment_runtime_replay),
    _adapter("WORKER_DISPATCH", "WORKER_DISPATCH_ARTIFACT_V1", "AIGOL_WORKER_DISPATCH_RUNTIME_V1", "WORKER_DISPATCH", "DIRECTORY", "002_dispatch_artifact_recorded.json", ("WORKER_DISPATCH",), "WORKER", "G31/G66-14", reconstruct_worker_dispatch_replay),
    _adapter("WORKER_INVOCATION", "WORKER_INVOCATION_ARTIFACT_V1", "AIGOL_WORKER_INVOCATION_RUNTIME_V1", "WORKER_INVOCATION", "DIRECTORY", "002_invocation_artifact_recorded.json", ("WORKER_INVOCATION",), "WORKER", "G31/G66-14", reconstruct_worker_invocation_replay),
    _adapter("EXECUTION", "EXECUTION_ARTIFACT_V1", "EXECUTION_RUNTIME_V1", "EXECUTION", "DIRECTORY", "000_execution_started.json", ("EXECUTION",), "EXECUTION", "G31/G66-14", reconstruct_execution_replay),
    _adapter("RESULT_CAPTURE", "WORKER_RESULT_CAPTURE_ARTIFACT_V1", "AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_V1", "RESULT_CAPTURE", "DIRECTORY", "002_result_capture_artifact_recorded.json", ("RESULT_CAPTURE",), "RESULT", "G31/G66-14", reconstruct_worker_result_capture_replay),
    _adapter("RESULT_VALIDATION", "WORKER_RESULT_VALIDATION_ARTIFACT_V1", "AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_V1", "RESULT_VALIDATION", "DIRECTORY", "002_validation_artifact_recorded.json", ("RESULT_VALIDATION",), "RESULT", "G31/G66-14", reconstruct_worker_result_validation_replay),
    _adapter("CAPABILITY_COMPLETION", "PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ARTIFACT_V1", "G54_05_PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ADAPTER_V1", "CAPABILITY_COMPLETION", "DIRECTORY", "001_worker_capability_completion_recorded.json", ("CAPABILITY_COMPLETION",), "COMPLETION", "G54/G66-14", reconstruct_platform_change_normalization_worker_completion_replay),
    _adapter("POST_EXECUTION_REPLAY_REVIEW", "POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1", "AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_V1", "POST_EXECUTION_REPLAY_REVIEW", "DIRECTORY", "002_review_artifact_recorded.json", ("POST_EXECUTION_REPLAY_REVIEW",), "DECISION", "G31/G66-14", reconstruct_post_execution_replay_review),
    _adapter("GOVERNED_TERMINATION", "GOVERNED_TERMINATION_ARTIFACT_V1", "AIGOL_GOVERNED_TERMINATION_RUNTIME_V1", "GOVERNED_TERMINATION", "DIRECTORY", "002_termination_artifact_recorded.json", ("GOVERNED_TERMINATION",), "TERMINATION", "G31/G66-14", reconstruct_governed_termination_replay),
    _adapter("FINAL_EXECUTION_CERTIFICATION", "REPLAY_CERTIFICATION_ARTIFACT_V1", "AIGOL_REPLAY_CERTIFICATION_RUNTIME_V1", "FINAL_EXECUTION_CERTIFICATION", "DIRECTORY", "000_replay_certification_artifact_recorded.json", ("FINAL_EXECUTION_CERTIFICATION",), "CERTIFICATION", "G31/G66-14", reconstruct_replay_certification_replay),
)

CATALOG_BY_ID = {adapter.adapter_id: adapter for adapter in CATALOG}


def catalog_projection() -> dict[str, Any]:
    """Return the passive catalog without exposing callable objects."""

    return {
        "catalog_version": ADAPTER_CATALOG_VERSION,
        "read_only": True,
        "grants_authority": False,
        "adapters": [
            {
                "adapter_id": item.adapter_id,
                "adapter_version": "V1",
                "source_artifact_type": item.source_artifact_type,
                "source_version": item.source_version,
                "source_owner": item.source_owner,
                "root_kind": item.root_kind,
                "accepted_explicit_evidence_root_class": item.root_kind,
                "principal_file": item.principal_file,
                "stages": list(item.stages),
                "event_classification": item.event_classification,
                "certified_generation": item.certified_generation,
                "reconstructor": item.reconstructor_name,
                "identity_fields": [
                    "artifact_hash",
                    "owner-local *_id or *_identity",
                    "canonical chain identity where source-defined",
                ],
                "predecessor_reference_fields": [
                    "source-declared *_reference",
                    "source-declared *_hash",
                    "owner-local replay reference",
                ],
                "revision_fields": [
                    "CWM/global/semantic revision where source-defined"
                ],
                "branch_predicates": [
                    "source owner status/disposition only"
                ],
                "terminal_predicates": [
                    "source owner terminal/certification status only"
                ],
                "source_visibility_classification": "OWNER_REPLAY_VISIBLE_METADATA_ONLY",
                "read_only": True,
                "pure_reconstruction": True,
                "grants_authority": False,
            }
            for item in CATALOG
        ],
    }
