"""Focused G31-02 Product 1 Decision Validation Packet onboarding tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli.aicli import run_reference_uhi_session
from aigol.runtime.certified_capability_invocation_binding_runtime import (
    CERTIFIED_CAPABILITY_INVOCATION_COMPLETED,
    PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION,
    invoke_certified_capability,
    reconstruct_certified_capability_invocation_replay,
)
from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
    INGRESS_FAILED_CLOSED,
    reconstruct_explicit_canonical_artifact_ingress,
    run_explicit_canonical_artifact_ingress,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
    reconstruct_operational_turn_binding,
)
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge
from aigol.runtime.product1_decision_validation_packet_certification_v1 import (
    PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1,
    PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1,
    create_product1_decision_validation_request,
    reconstruct_product1_decision_validation_packet_replay,
    validate_product1_decision_validation_request,
)
from aigol.runtime.project_context_semantic_capability_route import (
    reconstruct_project_context_semantic_capability_route,
)
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


CREATED_AT = "2026-07-15T00:00:00Z"
SESSION_ID = "SESSION-G31-02"
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


def _request(name: str = "VALID") -> dict:
    return create_product1_decision_validation_request(
        request_id=f"G31-02-{name}",
        product1_cert_root=PRODUCT1_CERT_ROOT,
        multi_provider_cert_root=MULTI_PROVIDER_CERT_ROOT,
        created_at=CREATED_AT,
    )


def _wrapper(tmp_path: Path, artifact: dict | None = None, name: str = "valid") -> Path:
    wrapper = {
        "replay_index": 0,
        "replay_step": "product1_decision_validation_request_recorded",
        "artifact": deepcopy(artifact or _request()),
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    path = tmp_path / "runtime" / "canonical-input" / f"{name}.json"
    write_json_immutable(path, wrapper)
    return path


def _reader(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def test_request_pins_exact_certification_and_replay_evidence() -> None:
    request = _request()

    assert request["artifact_type"] == (
        PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1
    )
    assert request["source_artifact_count"] == 19
    assert request["artifact_discovery_performed"] is False
    assert request["provider_invoked"] is False
    assert request["worker_invoked"] is False
    assert request["repository_mutated"] is False
    assert validate_product1_decision_validation_request(request) == request

    substituted = deepcopy(request)
    substituted["source_artifacts"][0]["source_content_hash"] = replay_hash(
        "substituted"
    )
    substituted["source_manifest_hash"] = replay_hash(
        substituted["source_artifacts"]
    )
    substituted.pop("artifact_hash")
    substituted["artifact_hash"] = replay_hash(substituted)
    with pytest.raises(FailClosedRuntimeError, match="source substitution"):
        validate_product1_decision_validation_request(substituted)


def test_direct_g28_invocation_reuses_packet_generator_and_reconstructs(
    tmp_path: Path,
) -> None:
    request = _request()
    knowledge = query_platform_knowledge(
        query=REQUEST,
        capability_identifier=PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION,
    )
    capture = invoke_certified_capability(
        invocation_id="G31-02-DIRECT-G28",
        session_id=SESSION_ID,
        platform_knowledge_response=knowledge,
        platform_knowledge_response_reference="G31-02-KNOWLEDGE",
        discovered_capability_identifier=(
            PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION
        ),
        capability_inputs={
            "decision_validation_request_artifact": request,
            "decision_validation_request_reference": request["request_id"],
            "decision_validation_request_hash": request["artifact_hash"],
        },
        invoked_by="PLATFORM_CORE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / "g28",
    )
    reconstructed = reconstruct_certified_capability_invocation_replay(
        tmp_path / "g28"
    )
    native = reconstruct_product1_decision_validation_packet_replay(
        tmp_path / "g28" / "capability_runtime"
    )

    assert capture["invocation_status"] == (
        CERTIFIED_CAPABILITY_INVOCATION_COMPLETED
    )
    assert capture["capability_output_artifact"]["artifact_type"] == (
        PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1
    )
    assert reconstructed["capability_identifier"] == (
        PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION
    )
    assert native["replay_reconstructed"] is True
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["repository_mutated"] is False


def test_natural_language_without_evidence_clarifies_and_valid_attachment_completes(
    tmp_path: Path,
) -> None:
    missing = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=f"{SESSION_ID}-MISSING",
        message=REQUEST,
        runtime_root=tmp_path / "missing-runtime",
        workspace=Path.cwd(),
        created_at=CREATED_AT,
    )
    assert missing["semantic_capability_runtime_route"]["route_status"] == (
        "SEMANTIC_CAPABILITY_ROUTE_CLARIFICATION_REQUIRED"
    )
    assert missing["semantic_capability_runtime_route"][
        "selected_capability_identifier"
    ] is None
    assert PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION in missing[
        "semantic_capability_runtime_route"
    ]["clarification_artifact"]["candidate_identifiers"]
    assert missing["semantic_capability_runtime_route"]["clarification_artifact"][
        "selected_missing_slot"
    ] == "input_artifact_family"
    assert missing["semantic_capability_runtime_route"]["lifecycle_result_hash"] is None

    reference = _wrapper(tmp_path)
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=Path.cwd(),
        created_at=CREATED_AT,
        explicit_canonical_artifact_references=[str(reference)],
    )
    route = context["semantic_capability_runtime_route"]
    result = context["governed_read_only_work_result"]
    presentation = route["canonical_platform_presentation"]
    packet_answer = presentation["answer"]["product1_decision_validation_packet"]

    assert route["route_status"] == "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    assert route["selected_capability_identifier"] == (
        PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION
    )
    assert "Historical evidence records Provider participation" in (
        presentation["summary"]
    )
    assert packet_answer["audit_conclusion"]["audit_status"] == "PASS"
    assert packet_answer["current_invocation"] == {
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
    }
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False
    assert reconstruct_project_context_semantic_capability_route(
        route["replay_reference"]
    )["artifact_hash"] == route["artifact_hash"]


def test_invalid_explicit_request_fails_closed_before_semantic_invocation(
    tmp_path: Path,
) -> None:
    invalid = _request("INVALID")
    invalid["source_artifacts"][0]["source_content_hash"] = replay_hash("invalid")
    invalid["source_manifest_hash"] = replay_hash(invalid["source_artifacts"])
    invalid.pop("artifact_hash")
    invalid["artifact_hash"] = replay_hash(invalid)
    reference = _wrapper(tmp_path, invalid, "invalid")

    ingress = run_explicit_canonical_artifact_ingress(
        ingress_id="G31-02-INVALID-INGRESS",
        session_id=SESSION_ID,
        opaque_artifact_references=[str(reference)],
        runtime_root=tmp_path / "runtime",
        workspace=Path.cwd(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invalid-ingress",
    )

    assert ingress["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "source substitution" in ingress["failure_reason"]
    assert ingress["provider_invoked"] is False
    assert ingress["worker_invoked"] is False
    assert ingress["repository_mutated"] is False


def test_real_aicli_attachment_completes_with_thin_interface_authority(
    tmp_path: Path,
) -> None:
    reference = _wrapper(tmp_path)
    output: list[str] = []
    result = run_reference_uhi_session(
        session_id=f"{SESSION_ID}-AICLI",
        runtime_root=tmp_path / "runtime",
        workspace=Path.cwd(),
        created_at=CREATED_AT,
        input_reader=_reader([REQUEST, "/send", f"/attach {reference}", "/exit"]),
        output_writer=output.append,
    )
    context = result["platform_core_project_services_context"]
    route = context["semantic_capability_runtime_route"]
    turn = context["operational_turn_binding"]
    rendered = "\n".join(output)

    assert "Clarification required before governed execution." in rendered
    assert "Opaque artifact reference attached" in rendered
    assert "Product 1 Decision Validation Packet was generated" in rendered
    assert route["route_status"] == "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    assert reconstruct_operational_turn_binding(turn["turn_reference"])[
        "artifact_hash"
    ] == turn["artifact_hash"]
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["aicli_owns_replay"] is False
    assert route["provider_invoked"] is False
    assert route["worker_invoked"] is False
    assert route["repository_mutated"] is False


def test_packet_replay_and_registry_fail_closed_on_substitution(
    tmp_path: Path,
) -> None:
    request = _request()
    knowledge = query_platform_knowledge(
        query=REQUEST,
        capability_identifier=PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION,
    )
    invoke_certified_capability(
        invocation_id="G31-02-TAMPER-G28",
        session_id=SESSION_ID,
        platform_knowledge_response=knowledge,
        platform_knowledge_response_reference="G31-02-TAMPER-KNOWLEDGE",
        discovered_capability_identifier=(
            PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION
        ),
        capability_inputs={
            "decision_validation_request_artifact": request,
            "decision_validation_request_reference": request["request_id"],
            "decision_validation_request_hash": request["artifact_hash"],
        },
        invoked_by="PLATFORM_CORE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / "tamper-g28",
    )
    native_path = (
        tmp_path
        / "tamper-g28"
        / "capability_runtime"
        / "000_product1_decision_validation_packet_generated.json"
    )
    wrapper = json.loads(native_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["packet_id"] = "SUBSTITUTED"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("wrapper_hash")
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    native_path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="deterministic reconstruction mismatch"):
        reconstruct_certified_capability_invocation_replay(tmp_path / "tamper-g28")

    record = lookup_platform_capability_certification(
        PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION
    )
    assert record["certification_milestone"] == "G31-02"
    assert record["runtime_execution_authority"] is False
    assert (
        "docs/governance/G31_02_PRODUCT1_DECISION_VALIDATION_PACKET_CERTIFIED_OPERATIONAL_ONBOARDING.md"
        in record["certification_evidence"]
    )
