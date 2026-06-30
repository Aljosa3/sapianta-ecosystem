"""Tests for G3-04 Phase 8B compatibility wrapper wiring."""

from __future__ import annotations

from aigol.runtime.platform_communication_wrapper_wiring import (
    PLATFORM_COMMUNICATION_WRAPPER_WIRING_VERSION,
    product1_audit_packet_summary_binding_type,
    provider_cognition_summary_binding_type,
    wire_authorization_wrapper_to_uhcl,
    wire_binding_wrapper_to_uhcl,
    wire_confirmation_wrapper_to_uhcl,
    wire_explanation_wrapper_to_uhcl,
    worker_execution_summary_binding_type,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-30T00:00:00Z"


def _evidence(name: str) -> list[dict[str, str]]:
    return [
        {
            "evidence_reference": f"evidence:{name}",
            "evidence_hash": replay_hash({"evidence": name}),
        }
    ]


def _assert_non_authoritative(wiring: dict) -> None:
    assert wiring["wiring_version"] == PLATFORM_COMMUNICATION_WRAPPER_WIRING_VERSION
    assert wiring["uhcl_consumed"] is True
    assert wiring["legacy_contract_preserved"] is True
    assert wiring["replay_compatibility_preserved"] is True
    assert wiring["rollback_capability_preserved"] is True
    assert wiring["deterministic"] is True
    assert wiring["new_communication_semantics_introduced"] is False
    assert wiring["provider_invoked_by_wiring"] is False
    assert wiring["worker_invoked_by_wiring"] is False
    assert wiring["approval_created_by_wiring"] is False
    assert wiring["authorization_created_by_wiring"] is False
    assert wiring["execution_authorized_by_wiring"] is False
    assert wiring["repository_mutated_by_wiring"] is False
    assert wiring["uhcl_artifact_hash"].startswith("sha256:")


def test_explanation_wrapper_consumes_uhcl_typed_section(tmp_path) -> None:
    wiring = wire_explanation_wrapper_to_uhcl(
        wrapper_surface="TEST_EXPLANATION_WRAPPER",
        wrapper_id="WRAPPER-EXPLANATION-001",
        summary_content={"rendered_explanation_hash": replay_hash("hello")},
        evidence_references=_evidence("explanation"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "explanation",
    )

    _assert_non_authoritative(wiring)
    assert wiring["uhcl_artifact_type"] == "UHCL_TYPED_COMMUNICATION_SECTION_ARTIFACT_V1"


def test_confirmation_wrapper_consumes_uhcl_shared_confirmation(tmp_path) -> None:
    wiring = wire_confirmation_wrapper_to_uhcl(
        wrapper_surface="TEST_CONFIRMATION_WRAPPER",
        wrapper_id="WRAPPER-CONFIRMATION-001",
        confirmation_prompt="Review this compatibility wrapper confirmation.",
        required_human_action="Choose confirm, clarify, modify, reject, or continue.",
        evidence_references=_evidence("confirmation"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "confirmation",
    )

    _assert_non_authoritative(wiring)
    assert wiring["uhcl_artifact_type"] == "UHCL_SHARED_CONFIRMATION_MODEL_ARTIFACT_V1"


def test_authorization_wrapper_uses_recovery_when_blocked(tmp_path) -> None:
    wiring = wire_authorization_wrapper_to_uhcl(
        wrapper_surface="TEST_AUTHORIZATION_WRAPPER",
        wrapper_id="WRAPPER-AUTHORIZATION-001",
        readiness_status="AUTHORIZATION_BLOCKED",
        cannot_continue_reason="approval decision is missing",
        missing_prerequisites=[
            {
                "prerequisite_id": "approval_decision_present",
                "description": "Approval decision must be present.",
                "evidence_reference": "approval:missing",
                "evidence_hash": replay_hash({"approval": "missing"}),
            }
        ],
        summary_content={"authorization_readiness_status": "AUTHORIZATION_BLOCKED"},
        evidence_references=_evidence("authorization"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authorization",
    )

    _assert_non_authoritative(wiring)
    assert wiring["uhcl_artifact_type"] == "UHCL_RECOVERY_GUIDANCE_MODEL_ARTIFACT_V1"


def test_provider_worker_product_summary_wrappers_consume_uhcl_bindings(tmp_path) -> None:
    cases = [
        ("PROVIDER", provider_cognition_summary_binding_type()),
        ("WORKER", worker_execution_summary_binding_type()),
        ("PRODUCT1", product1_audit_packet_summary_binding_type()),
    ]
    for name, binding_type in cases:
        wiring = wire_binding_wrapper_to_uhcl(
            wrapper_surface=f"TEST_{name}_SUMMARY_WRAPPER",
            wrapper_id=f"WRAPPER-{name}-001",
            binding_type=binding_type,
            summary_content={"summary": f"{name} summary remains interface-neutral."},
            evidence_references=_evidence(name),
            created_at=CREATED_AT,
            replay_dir=tmp_path / name.lower(),
        )

        _assert_non_authoritative(wiring)
        assert wiring["uhcl_artifact_type"] == "UHCL_PROVIDER_WORKER_PRODUCT_COMMUNICATION_BINDING_ARTIFACT_V1"
