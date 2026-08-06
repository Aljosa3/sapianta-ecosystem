"""G71-09 authenticated Product 1 onboarding and packet-lineage evidence."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from aigol.runtime.certified_capability_invocation_binding_runtime import (
    CERTIFIED_CAPABILITY_INVOCATION_COMPLETED,
    PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION,
    reconstruct_certified_capability_invocation_replay,
)
from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
    INGRESS_COMPLETED,
    INGRESS_FAILED_CLOSED,
    reconstruct_explicit_canonical_artifact_ingress,
    run_explicit_canonical_artifact_ingress,
)
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
    reconstruct_operational_turn_binding,
)
from aigol.runtime.product1_decision_validation_packet_certification_v1 import (
    PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1,
    PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1,
    create_product1_decision_validation_request,
    reconstruct_product1_decision_validation_packet_replay,
)
from aigol.runtime.project_context_semantic_capability_route import (
    ROUTE_COMPLETED,
    reconstruct_project_context_semantic_capability_route,
)
from aigol.runtime.semantic_capability_invocation_lifecycle_runtime import (
    LIFECYCLE_COMPLETED,
    reconstruct_semantic_capability_invocation_lifecycle_replay,
)
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


CREATED_AT = "2026-08-06T00:00:00Z"
SESSION_ID = "G71-09-PRODUCT1-ONBOARDING"
PRODUCT1_CERT_ROOT = Path(
    "runtime/product1_end_to_end_certification_v1/CERT-000001"
)
MULTI_PROVIDER_CERT_ROOT = Path(
    "runtime/multi_provider_operational_readiness_certification_v1/CERT-000001"
)
REQUEST = (
    "Validate a Product 1 Decision Validation Packet from certified Replay "
    "evidence. Audit only. Do not implement anything. Do not mutate the repository."
)


def _request() -> dict:
    return create_product1_decision_validation_request(
        request_id="G71-09-PRODUCT1-REQUEST",
        product1_cert_root=PRODUCT1_CERT_ROOT,
        multi_provider_cert_root=MULTI_PROVIDER_CERT_ROOT,
        created_at=CREATED_AT,
    )


def _wrapper(tmp_path: Path, artifact: dict, name: str) -> Path:
    wrapper = {
        "replay_index": 0,
        "replay_step": "product1_decision_validation_request_recorded",
        "artifact": deepcopy(artifact),
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    path = tmp_path / "runtime" / "canonical-input" / f"{name}.json"
    write_json_immutable(path, wrapper)
    return path


def test_authenticated_product1_owner_reconstructs_complete_packet_lineage(
    tmp_path: Path,
) -> None:
    request = _request()
    reference = _wrapper(tmp_path, request, "valid")
    context = prepare_unified_human_interface_project_context(
        interface_name="CLIA",
        session_id=SESSION_ID,
        message=REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=Path.cwd(),
        created_at=CREATED_AT,
        explicit_canonical_artifact_references=[str(reference)],
    )

    ingress = reconstruct_explicit_canonical_artifact_ingress(
        context["explicit_canonical_artifact_ingress_reference"]
    )
    route = reconstruct_project_context_semantic_capability_route(
        context["semantic_capability_runtime_route"]["replay_reference"]
    )
    lifecycle = reconstruct_semantic_capability_invocation_lifecycle_replay(
        route["lifecycle_replay_reference"]
    )
    invocation = reconstruct_certified_capability_invocation_replay(
        Path(route["lifecycle_replay_reference"]) / "g28_invocation"
    )
    packet = reconstruct_product1_decision_validation_packet_replay(
        invocation["capability_replay_reference"]
    )
    turn = reconstruct_operational_turn_binding(
        context["operational_turn_binding_reference"]
    )

    assert request["artifact_type"] == PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1
    assert ingress["ingress_status"] == INGRESS_COMPLETED
    assert route["route_status"] == ROUTE_COMPLETED
    assert route["selected_capability_identifier"] == (
        PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION
    )
    assert route["bound_canonical_artifact_hash"] == request["artifact_hash"]
    assert lifecycle["lifecycle_status"] == LIFECYCLE_COMPLETED
    assert invocation["invocation_status"] == CERTIFIED_CAPABILITY_INVOCATION_COMPLETED
    assert invocation["output_artifact_type"] == (
        PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1
    )
    assert packet["request_artifact_hash"] == request["artifact_hash"]
    assert packet["source_manifest_hash"] == request["source_manifest_hash"]
    assert packet["packet_artifact_hash"] == invocation["output_artifact_hash"]
    assert packet["replay_reconstructed"] is True
    assert turn["artifact_hash"] == context["operational_turn_binding_hash"]
    assert route["provider_invoked"] is False
    assert route["worker_invoked"] is False
    assert route["repository_mutated"] is False


def test_product1_onboarding_fails_closed_before_owner_on_source_substitution(
    tmp_path: Path,
) -> None:
    request = _request()
    request["source_artifacts"][0]["source_content_hash"] = replay_hash("substituted")
    request["source_manifest_hash"] = replay_hash(request["source_artifacts"])
    request.pop("artifact_hash")
    request["artifact_hash"] = replay_hash(request)
    reference = _wrapper(tmp_path, request, "substituted")

    ingress = run_explicit_canonical_artifact_ingress(
        ingress_id="G71-09-SUBSTITUTED-INGRESS",
        session_id=SESSION_ID,
        opaque_artifact_references=[str(reference)],
        runtime_root=tmp_path / "runtime",
        workspace=Path.cwd(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "substituted-ingress",
    )

    assert ingress["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "source substitution" in ingress["failure_reason"]
    assert ingress["explicit_canonical_artifact_ingress_artifact"][
        "capability_invoked"
    ] is False
    assert ingress["provider_invoked"] is False
    assert ingress["worker_invoked"] is False
    assert ingress["repository_mutated"] is False


def test_product1_onboarding_uses_the_existing_certified_owner_only() -> None:
    record = lookup_platform_capability_certification(
        PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION
    )

    assert record["capability_owner"] == "PRODUCT1_AI_DECISION_VALIDATOR"
    assert record["architectural_owner"] == "PLATFORM_CORE"
    assert record["implementation_owner"] == (
        "aigol.runtime.product1_decision_validation_packet_certification_v1"
    )
    assert record["certification_milestone"] == "G31-02"
    assert record["verification_type"] == (
        "DETERMINISTIC_PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION"
    )
    assert record["runtime_execution_authority"] is False
