"""Tests for UBTR_HUMAN_COMMUNICATION_MODEL_RUNTIME_V1."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash
from aigol.runtime.ubtr_human_communication_model_runtime import (
    COMMUNICATION_ARTIFACT_TYPE,
    COMMUNICATION_BINDING_ARTIFACT_TYPE,
    COMMUNICATION_BINDING_TYPES,
    COMMUNICATION_DOMAINS,
    COMMUNICATION_LEVELS,
    DOMAIN_UNDERSTANDING,
    LEVEL_STANDARD,
    PROGRESSIVE_EXPLANATION_ARTIFACT_TYPE,
    RESPONSE_CLARIFICATION,
    RESPONSE_CONFIRMATION,
    RESPONSE_CONTINUATION,
    RESPONSE_MODIFICATION,
    RESPONSE_REJECTION,
    RECOVERY_GUIDANCE_ARTIFACT_TYPE,
    SHARED_CONFIRMATION_ARTIFACT_TYPE,
    SOURCE_COMPONENT_GOVERNANCE,
    SOURCE_COMPONENT_PRODUCT,
    TYPED_SECTION_ARTIFACT_TYPE,
    TYPED_SECTION_TYPES,
    create_communication_binding,
    create_recovery_guidance_model,
    create_shared_confirmation_model,
    derive_progressive_explanation,
    create_ubtr_human_communication_artifact,
    create_typed_communication_section,
    reconstruct_communication_binding_replay,
    reconstruct_progressive_explanation_replay,
    reconstruct_recovery_guidance_replay,
    reconstruct_shared_confirmation_replay,
    reconstruct_typed_communication_section_replay,
    reconstruct_ubtr_human_communication_replay,
)


CREATED_AT = "2026-06-29T00:00:00Z"


def _lineage(name: str = "communication") -> list[dict]:
    return [
        {
            "replay_reference": f"runtime/ubtr/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _sections() -> dict:
    return {
        "understanding_section": {
            "understood_request_summary": "Create a governed Product 1 decision validation packet.",
            "normalized_intent": "PRODUCT_1_DECISION_VALIDATION",
            "domain": "PRODUCT",
            "requested_actions": ["CREATE"],
            "ambiguity_status": "NO_AMBIGUITY",
            "confidence": "HIGH",
        },
        "explanation_section": {
            "summary": "The platform can prepare non-authoritative decision evidence.",
            "because": "The request maps to the certified Product 1 workflow.",
            "evidence_references": ["CSA-001"],
            "limitations": ["No provider or worker execution is included."],
        },
        "recommendation_section": {
            "recommendation": "Proceed to proposal review.",
            "alternatives": ["Request clarification"],
            "tradeoffs": ["Faster review versus additional context gathering"],
            "advisory_only": True,
        },
        "guidance_section": {
            "next_action": "Review the generated proposal evidence.",
            "available_options": ["confirm", "reject", "clarify", "modify", "continue"],
            "blocked_actions": ["execute worker"],
            "recovery_path": "Ask for clarification if scope is incomplete.",
        },
        "confirmation_section": {
            "supported_classes": ["confirm", "reject", "clarify", "modify", "continue", "unknown"],
            "confirmation_required": True,
            "confirmation_status": "PENDING",
        },
        "transparency_section": {
            "assumptions": ["The operator is requesting governed development evidence."],
            "risks": ["Scope drift without confirmation."],
            "uncertainties": ["Exact target artifact may need confirmation."],
            "provider_provenance": "NO_PROVIDER_INVOKED",
            "worker_provenance": "NO_WORKER_INVOKED",
        },
        "conversation_continuation_section": {
            "conversation_id": "CONV-001",
            "session_id": "SESSION-001",
            "turn_id": "TURN-001",
            "parent_turn": None,
            "continuation_status": "AWAITING_CONFIRMATION",
        },
    }


def _create(tmp_path, *, domain: str = DOMAIN_UNDERSTANDING, level: str = LEVEL_STANDARD) -> dict:
    return create_ubtr_human_communication_artifact(
        communication_id=f"COMM-{domain}-{level}",
        source_component="UBTR",
        target_human_context="ACLI_OPERATOR",
        csa_reference="CSA-001",
        csa_hash=replay_hash({"csa": "001"}),
        ocs_reference="OCS-001",
        ocs_hash=replay_hash({"ocs": "001"}),
        communication_domain=domain,
        communication_level=level,
        required_human_action="review communication model evidence",
        replay_lineage=_lineage(f"{domain}-{level}"),
        rollback_reference="ROLLBACK-COMM-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{domain}_{level}",
        **_sections(),
    )


def _evidence(name: str = "source") -> list[dict]:
    return [
        {
            "evidence_reference": f"EVIDENCE-{name}",
            "evidence_hash": replay_hash({"evidence": name}),
            "evidence_role": "SOURCE_EVIDENCE",
        }
    ]


def _typed_section(tmp_path, *, section_type: str, level: str = LEVEL_STANDARD) -> dict:
    return create_typed_communication_section(
        section_id=f"SECTION-{section_type}-{level}",
        section_type=section_type,
        communication_level=level,
        structured_content={
            "summary": f"{section_type} section summary.",
            "required_human_action": "review typed section evidence",
            "non_authority_notice": "Evidence only.",
        },
        evidence_references=_evidence(section_type),
        source_component="UBTR",
        csa_reference="CSA-SECTION-001",
        csa_hash=replay_hash({"csa": section_type}),
        ocs_reference="OCS-SECTION-001",
        ocs_hash=replay_hash({"ocs": section_type}),
        communication_level_variants={
            level: {
                "summary": f"{section_type} section summary.",
                "required_human_action": "review typed section evidence",
                "non_authority_notice": "Evidence only.",
            },
            "DETAILED": {
                "summary": f"Detailed {section_type} section summary.",
                "details": ["source evidence is hash-bound"],
            },
        },
        replay_lineage=_lineage(section_type),
        rollback_reference="ROLLBACK-TYPED-SECTION-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"typed_{section_type}_{level}",
    )


def _evidence_bound_section(tmp_path) -> dict:
    return create_typed_communication_section(
        section_id="SECTION-EVIDENCE-BOUND-001",
        section_type="TRANSPARENCY",
        communication_level=LEVEL_STANDARD,
        structured_content={
            "summary": "Product 1 evidence is bound to communication.",
            "assumptions": ["Decision packet is the source of product assumptions."],
            "risks": ["Provider output remains advisory."],
            "uncertainties": ["Operator may request more evidence."],
        },
        evidence_references=[
            {
                "evidence_reference": "PRODUCT1-DECISION-PACKET-001",
                "evidence_hash": replay_hash({"packet": "001"}),
                "evidence_role": "PRODUCT_SOURCE",
            },
            {
                "evidence_reference": "GOVERNANCE-CHECKPOINT-001",
                "evidence_hash": replay_hash({"governance": "001"}),
                "evidence_role": "GOVERNANCE_SOURCE",
            },
        ],
        source_component=SOURCE_COMPONENT_PRODUCT,
        source_evidence_bindings={
            "specific_sources": {
                "replay": {
                    "reference": "REPLAY-001",
                    "hash": replay_hash({"replay": "001"}),
                },
                "governance": {
                    "reference": "GOVERNANCE-CHECKPOINT-001",
                    "hash": replay_hash({"governance": "001"}),
                },
                "provider": {
                    "reference": "PROVIDER-PROVENANCE-001",
                    "hash": replay_hash({"provider": "001"}),
                },
                "worker": {
                    "reference": "WORKER-RESULT-001",
                    "hash": replay_hash({"worker": "001"}),
                },
                "product": {
                    "reference": "PRODUCT1-DECISION-PACKET-001",
                    "hash": replay_hash({"packet": "001"}),
                },
            },
        },
        csa_reference="CSA-EVIDENCE-BOUND-001",
        csa_hash=replay_hash({"csa": "evidence-bound"}),
        ocs_reference="OCS-EVIDENCE-BOUND-001",
        ocs_hash=replay_hash({"ocs": "evidence-bound"}),
        replay_lineage=_lineage("evidence-bound"),
        rollback_reference="ROLLBACK-EVIDENCE-BOUND-001",
        non_authority_notices=["Evidence binding is explanatory only."],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "evidence_bound_section",
    )


def _progressive_communication(tmp_path) -> dict:
    variants = {
        "CONCISE": {
            "summary": "Decision evidence is available for review.",
            "detail_policy": "minimal",
        },
        "STANDARD": {
            "summary": "Decision evidence is available for governed review.",
            "detail_policy": "normal",
        },
        "DETAILED": {
            "summary": "Decision evidence is available for governed review.",
            "details": ["CSA, replay, and governance sources remain hash-bound."],
            "detail_policy": "expanded",
        },
        "BEGINNER": {
            "summary": "The platform explains why this decision can be reviewed.",
            "plain_language": "This does not approve or execute the decision.",
        },
        "TECHNICAL": {
            "summary": "UHCL derives this explanation from a typed section variant.",
            "hash_controls": ["source_evidence_binding_hash", "artifact_hash"],
        },
        "AUDITOR": {
            "summary": "The explanation preserves source evidence lineage.",
            "audit_controls": ["semantic_meaning_hash", "evidence_lineage_hash"],
        },
        "EXECUTIVE": {
            "summary": "The review is evidence-backed and non-authoritative.",
            "business_context": "Operator decision support only.",
        },
    }
    explanation = create_typed_communication_section(
        section_id="SECTION-PROGRESSIVE-EXPLANATION-001",
        section_type="EXPLANATION",
        communication_level=LEVEL_STANDARD,
        structured_content=variants[LEVEL_STANDARD],
        evidence_references=[
            {
                "evidence_reference": "GOVERNANCE-CHECKPOINT-PROGRESSIVE-001",
                "evidence_hash": replay_hash({"governance": "progressive"}),
                "evidence_role": "GOVERNANCE_SOURCE",
            }
        ],
        source_component=SOURCE_COMPONENT_GOVERNANCE,
        source_evidence_bindings={
            "specific_sources": {
                "replay": {
                    "reference": "REPLAY-PROGRESSIVE-001",
                    "hash": replay_hash({"replay": "progressive"}),
                },
                "governance": {
                    "reference": "GOVERNANCE-CHECKPOINT-PROGRESSIVE-001",
                    "hash": replay_hash({"governance": "progressive"}),
                },
            },
        },
        csa_reference="CSA-PROGRESSIVE-001",
        csa_hash=replay_hash({"csa": "progressive"}),
        ocs_reference="OCS-PROGRESSIVE-001",
        ocs_hash=replay_hash({"ocs": "progressive"}),
        communication_level_variants=variants,
        replay_lineage=_lineage("progressive-section"),
        rollback_reference="ROLLBACK-PROGRESSIVE-SECTION-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "progressive_section",
    )
    return create_ubtr_human_communication_artifact(
        communication_id="COMM-PROGRESSIVE-EXPLANATION-001",
        source_component="UBTR",
        target_human_context="ACLI_OPERATOR",
        communication_domain="EXPLANATION",
        communication_level=LEVEL_STANDARD,
        required_human_action="review progressive explanation variants",
        replay_lineage=_lineage("progressive-communication"),
        rollback_reference="ROLLBACK-PROGRESSIVE-COMM-001",
        csa_reference="CSA-PROGRESSIVE-001",
        csa_hash=replay_hash({"csa": "progressive"}),
        explanation_section=explanation["typed_section_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "progressive_communication",
    )


def _shared_confirmation(tmp_path) -> dict:
    return create_shared_confirmation_model(
        confirmation_id="CONFIRMATION-SHARED-001",
        source_component=SOURCE_COMPONENT_GOVERNANCE,
        target_human_context="ACLI_OPERATOR",
        communication_level=LEVEL_STANDARD,
        confirmation_prompt="Review the governed communication and choose a response.",
        required_human_action="choose confirm, clarify, modify, reject, or continue",
        evidence_references=[
            {
                "evidence_reference": "APPROVAL-EVIDENCE-001",
                "evidence_hash": replay_hash({"approval": "001"}),
                "evidence_role": "APPROVAL_SOURCE",
            },
            {
                "evidence_reference": "AUTHORIZATION-EVIDENCE-001",
                "evidence_hash": replay_hash({"authorization": "001"}),
                "evidence_role": "AUTHORIZATION_SOURCE",
            },
        ],
        source_evidence_bindings={
            "specific_sources": {
                "governance": {
                    "reference": "GOVERNANCE-CONFIRMATION-001",
                    "hash": replay_hash({"governance": "confirmation"}),
                },
            },
        },
        csa_reference="CSA-CONFIRMATION-001",
        csa_hash=replay_hash({"csa": "confirmation"}),
        ocs_reference="OCS-CONFIRMATION-001",
        ocs_hash=replay_hash({"ocs": "confirmation"}),
        approval_reference="APPROVAL-EVIDENCE-001",
        approval_hash=replay_hash({"approval": "001"}),
        authorization_reference="AUTHORIZATION-EVIDENCE-001",
        authorization_hash=replay_hash({"authorization": "001"}),
        replay_lineage=_lineage("shared-confirmation"),
        rollback_reference="ROLLBACK-SHARED-CONFIRMATION-001",
        non_authority_notices=["Confirmation response classification is evidence only."],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "shared_confirmation",
    )


def _binding_evidence(binding_type: str) -> list[dict]:
    return [
        {
            "evidence_reference": f"{binding_type}-EVIDENCE-001",
            "evidence_hash": replay_hash({"binding": binding_type, "evidence": "001"}),
            "evidence_role": "COMMUNICATION_BINDING_SOURCE",
        }
    ]


def _communication_binding(tmp_path, *, binding_type: str) -> dict:
    group = "PROVIDER" if binding_type.startswith("PROVIDER") else "WORKER" if binding_type.startswith("WORKER") else "PRODUCT"
    specific_sources = {
        "replay": {
            "reference": f"REPLAY-{binding_type}-001",
            "hash": replay_hash({"replay": binding_type}),
        },
        group.lower(): {
            "reference": f"{group}-{binding_type}-001",
            "hash": replay_hash({group.lower(): binding_type}),
        },
    }
    return create_communication_binding(
        binding_id=f"BINDING-{binding_type}-001",
        binding_type=binding_type,
        target_human_context="ACLI_OPERATOR",
        communication_level=LEVEL_STANDARD,
        summary_content={
            "summary": f"{binding_type} is available for human review.",
            "human_readable_status": "EVIDENCE_BOUND",
            "limitations": ["Communication is non-authoritative."],
        },
        evidence_references=_binding_evidence(binding_type),
        source_evidence_bindings={"specific_sources": specific_sources},
        csa_reference=f"CSA-{binding_type}-001",
        csa_hash=replay_hash({"csa": binding_type}),
        ocs_reference=f"OCS-{binding_type}-001",
        ocs_hash=replay_hash({"ocs": binding_type}),
        replay_lineage=_lineage(binding_type.lower()),
        rollback_reference=f"ROLLBACK-{binding_type}-001",
        non_authority_notices=[f"{binding_type} communication binding is evidence only."],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"binding_{binding_type}",
    )


def _recovery_guidance(tmp_path) -> dict:
    return create_recovery_guidance_model(
        recovery_id="RECOVERY-GUIDANCE-001",
        source_component=SOURCE_COMPONENT_GOVERNANCE,
        target_human_context="ACLI_OPERATOR",
        communication_level=LEVEL_STANDARD,
        blocked_operation="Provider activation cannot continue.",
        cannot_continue_reason="Required governance approval evidence is missing.",
        missing_prerequisites=[
            {
                "prerequisite_id": "GOVERNANCE-APPROVAL-REQUIRED",
                "description": "Governance approval evidence must be present.",
                "evidence_reference": "GOVERNANCE-CHECKPOINT-RECOVERY-001",
                "evidence_hash": replay_hash({"governance": "recovery"}),
            }
        ],
        available_recovery_actions=[
            {
                "action_id": "REQUEST_APPROVAL_EVIDENCE",
                "description": "Ask the operator to supply or select approval evidence.",
            },
            {
                "action_id": "REQUEST_CLARIFICATION",
                "description": "Ask the operator to clarify the intended governed action.",
            },
        ],
        recommended_next_action={
            "action_id": "REQUEST_APPROVAL_EVIDENCE",
            "reason": "Approval evidence is the missing prerequisite blocking continuation.",
        },
        evidence_references=[
            {
                "evidence_reference": "GOVERNANCE-CHECKPOINT-RECOVERY-001",
                "evidence_hash": replay_hash({"governance": "recovery"}),
                "evidence_role": "GOVERNANCE_SOURCE",
            }
        ],
        source_evidence_bindings={
            "specific_sources": {
                "governance": {
                    "reference": "GOVERNANCE-CHECKPOINT-RECOVERY-001",
                    "hash": replay_hash({"governance": "recovery"}),
                },
                "replay": {
                    "reference": "REPLAY-RECOVERY-001",
                    "hash": replay_hash({"replay": "recovery"}),
                },
            },
        },
        csa_reference="CSA-RECOVERY-001",
        csa_hash=replay_hash({"csa": "recovery"}),
        ocs_reference="OCS-RECOVERY-001",
        ocs_hash=replay_hash({"ocs": "recovery"}),
        replay_lineage=_lineage("recovery-guidance"),
        rollback_reference="ROLLBACK-RECOVERY-GUIDANCE-001",
        non_authority_notices=["Recovery guidance is advisory only."],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "recovery_guidance",
    )


def test_creates_interface_neutral_communication_artifact_with_all_sections(tmp_path) -> None:
    result = _create(tmp_path)
    artifact = result["communication_artifact"]

    assert artifact["artifact_type"] == COMMUNICATION_ARTIFACT_TYPE
    assert artifact["communication_domain"] == DOMAIN_UNDERSTANDING
    assert artifact["communication_level"] == LEVEL_STANDARD
    assert artifact["source_references"]["csa_reference"] == "CSA-001"
    assert artifact["source_references"]["csa_hash"].startswith("sha256:")
    assert artifact["sections_rendered"] == sorted(
        [
            "confirmation",
            "conversation_continuation",
            "explanation",
            "guidance",
            "recommendation",
            "transparency",
            "understanding",
        ]
    )
    assert artifact["authority_flags"]["execution_authority"] is False
    assert artifact["authority_flags"]["provider_authority"] is False
    assert artifact["authority_flags"]["worker_authority"] is False
    assert artifact["interface_neutral"] is True
    assert result["interface_specific_rendering"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_creates_typed_sections_for_all_required_uhcl_section_types(tmp_path) -> None:
    for section_type in sorted(TYPED_SECTION_TYPES):
        result = _typed_section(tmp_path, section_type=section_type)
        artifact = result["typed_section_artifact"]

        assert artifact["artifact_type"] == TYPED_SECTION_ARTIFACT_TYPE
        assert artifact["section_type"] == section_type
        assert artifact["communication_level"] == LEVEL_STANDARD
        assert artifact["evidence_reference_count"] == 1
        assert artifact["evidence_references_hash"].startswith("sha256:")
        assert artifact["source_component"] == "UBTR"
        assert artifact["source_evidence_binding_hash"].startswith("sha256:")
        assert artifact["source_bindings"]["specific_sources"]["csa"]["hash"].startswith("sha256:")
        assert artifact["source_bindings"]["source_evidence_hashes"] == [
            artifact["evidence_references"][0]["evidence_hash"]
        ]
        assert "DETAILED" in artifact["communication_level_variants"]
        assert artifact["non_authority_notices"]
        assert artifact["authority_flags"]["approval_authority"] is False
        assert artifact["authority_flags"]["execution_authority"] is False
        assert result["interface_specific_rendering"] is False


def test_source_evidence_binding_records_platform_source_lineage(tmp_path) -> None:
    result = _evidence_bound_section(tmp_path)
    artifact = result["typed_section_artifact"]
    bindings = artifact["source_bindings"]

    assert artifact["source_component"] == SOURCE_COMPONENT_PRODUCT
    assert result["source_component"] == SOURCE_COMPONENT_PRODUCT
    assert bindings["binding_schema_version"] == "UHCL_SOURCE_EVIDENCE_BINDING_V1"
    assert bindings["source_component"] == SOURCE_COMPONENT_PRODUCT
    assert bindings["source_evidence_reference_count"] == 2
    assert bindings["source_evidence_hashes"] == [
        item["evidence_hash"] for item in artifact["evidence_references"]
    ]
    assert bindings["source_evidence_references_hash"] == artifact["evidence_references_hash"]
    assert bindings["specific_sources"]["csa"]["reference"] == "CSA-EVIDENCE-BOUND-001"
    assert bindings["specific_sources"]["ocs"]["reference"] == "OCS-EVIDENCE-BOUND-001"
    assert bindings["specific_sources"]["replay"]["reference"] == "REPLAY-001"
    assert bindings["specific_sources"]["governance"]["reference"] == "GOVERNANCE-CHECKPOINT-001"
    assert bindings["specific_sources"]["provider"]["reference"] == "PROVIDER-PROVENANCE-001"
    assert bindings["specific_sources"]["worker"]["reference"] == "WORKER-RESULT-001"
    assert bindings["specific_sources"]["product"]["reference"] == "PRODUCT1-DECISION-PACKET-001"
    assert bindings["non_authoritative"] is True
    assert artifact["source_evidence_binding_hash"] == result["source_evidence_binding_hash"]
    assert "Evidence binding is explanatory only." in artifact["non_authority_notices"]
    assert artifact["authority_flags"]["provider_authority"] is False
    assert artifact["authority_flags"]["worker_authority"] is False


def test_source_evidence_binding_reconstructs_with_binding_hash(tmp_path) -> None:
    result = _evidence_bound_section(tmp_path)

    reconstructed = reconstruct_typed_communication_section_replay(tmp_path / "evidence_bound_section")

    assert reconstructed["typed_section_artifact"] == result["typed_section_artifact"]
    assert reconstructed["source_component"] == SOURCE_COMPONENT_PRODUCT
    assert reconstructed["source_evidence_binding_hash"] == result["source_evidence_binding_hash"]
    assert reconstructed["non_authority_notices"]


def test_derives_progressive_explanations_for_all_levels_from_same_artifact(tmp_path) -> None:
    communication = _progressive_communication(tmp_path)

    result = derive_progressive_explanation(
        derivation_id="DERIVE-PROGRESSIVE-001",
        source_communication_artifact=communication["communication_artifact"],
        target_levels=sorted(COMMUNICATION_LEVELS),
        replay_lineage=_lineage("progressive-derivation"),
        rollback_reference="ROLLBACK-PROGRESSIVE-DERIVATION-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "progressive_derivation",
    )
    artifact = result["progressive_explanation_artifact"]

    assert artifact["artifact_type"] == PROGRESSIVE_EXPLANATION_ARTIFACT_TYPE
    assert artifact["source_communication_hash"] == communication["communication_artifact_hash"]
    assert artifact["target_levels"] == sorted(COMMUNICATION_LEVELS)
    assert artifact["semantic_meaning_hash"] == result["semantic_meaning_hash"]
    assert artifact["evidence_lineage_hash"] == result["evidence_lineage_hash"]
    assert artifact["level_derivation_policy"]["new_facts_allowed"] is False
    assert artifact["source_sections"][0]["section_type"] == "EXPLANATION"
    assert artifact["source_sections"][0]["source_evidence_binding_hash"].startswith("sha256:")
    for level in sorted(COMMUNICATION_LEVELS):
        explanation = artifact["derived_explanations"][level]
        assert explanation["semantic_meaning_hash"] == artifact["semantic_meaning_hash"]
        assert explanation["evidence_lineage_hash"] == artifact["evidence_lineage_hash"]
        assert explanation["new_facts_introduced"] is False
        assert explanation["authority_granted"] is False
        assert explanation["section_derivations"][0]["source_section_hash"] == artifact["source_section_hashes"][0]
        assert explanation["section_derivations"][0]["new_facts_introduced"] is False
    assert result["interface_specific_rendering"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False


def test_progressive_explanation_replay_reconstructs_and_preserves_hash(tmp_path) -> None:
    communication = _progressive_communication(tmp_path)
    result = derive_progressive_explanation(
        derivation_id="DERIVE-PROGRESSIVE-REPLAY-001",
        source_communication_artifact=communication["communication_artifact"],
        target_levels=["CONCISE", "AUDITOR"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "progressive_derivation_replay",
    )

    reconstructed = reconstruct_progressive_explanation_replay(
        tmp_path / "progressive_derivation_replay"
    )

    assert reconstructed["progressive_explanation_artifact"] == result["progressive_explanation_artifact"]
    assert reconstructed["progressive_explanation_artifact_hash"] == result["progressive_explanation_artifact_hash"]
    assert reconstructed["target_levels"] == ["AUDITOR", "CONCISE"]
    assert reconstructed["authority_granted"] is False


def test_progressive_explanation_rejects_unsupported_level(tmp_path) -> None:
    communication = _progressive_communication(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="target_level is not supported"):
        derive_progressive_explanation(
            derivation_id="DERIVE-PROGRESSIVE-INVALID-001",
            source_communication_artifact=communication["communication_artifact"],
            target_levels=["TERMINAL_VERBOSE"],
            created_at=CREATED_AT,
            replay_dir=tmp_path / "progressive_invalid_level",
        )


def test_progressive_explanation_tampering_fails_closed(tmp_path) -> None:
    communication = _progressive_communication(tmp_path)
    derive_progressive_explanation(
        derivation_id="DERIVE-PROGRESSIVE-TAMPER-001",
        source_communication_artifact=communication["communication_artifact"],
        target_levels=["CONCISE", "STANDARD"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "progressive_derivation_tamper",
    )
    replay_file = (
        tmp_path
        / "progressive_derivation_tamper"
        / "000_uhcl_progressive_explanation_derivation_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["derived_explanations"]["CONCISE"]["new_facts_introduced"] = True
    wrapper["replay_hash"] = replay_hash(
        {
            "replay_index": wrapper["replay_index"],
            "replay_step": wrapper["replay_step"],
            "event_type": wrapper["event_type"],
            "artifact": wrapper["artifact"],
        }
    )
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="cannot introduce new facts"):
        reconstruct_progressive_explanation_replay(tmp_path / "progressive_derivation_tamper")


def test_creates_shared_confirmation_model_with_all_response_classes(tmp_path) -> None:
    result = _shared_confirmation(tmp_path)
    artifact = result["shared_confirmation_artifact"]
    section = result["confirmation_section"]

    assert artifact["artifact_type"] == SHARED_CONFIRMATION_ARTIFACT_TYPE
    assert artifact["communication_level"] == LEVEL_STANDARD
    assert artifact["supported_response_types"] == sorted(
        [
            RESPONSE_CLARIFICATION,
            RESPONSE_CONFIRMATION,
            RESPONSE_CONTINUATION,
            RESPONSE_MODIFICATION,
            RESPONSE_REJECTION,
        ]
    )
    assert section["section_type"] == "CONFIRMATION"
    assert section["confirmation_status"] == "PENDING"
    assert section["source_evidence_binding_hash"] == artifact["source_evidence_binding_hash"]
    assert artifact["source_bindings"]["specific_sources"]["approval"]["reference"] == "APPROVAL-EVIDENCE-001"
    assert artifact["source_bindings"]["specific_sources"]["authorization"]["reference"] == "AUTHORIZATION-EVIDENCE-001"
    for response_type, model in artifact["response_models"].items():
        assert model["response_type"] == response_type
        assert model["creates_approval"] is False
        assert model["creates_authorization"] is False
        assert model["creates_execution_authority"] is False
        assert model["invokes_provider"] is False
        assert model["invokes_worker"] is False
        assert model["mutates_repository"] is False
        assert model["non_authoritative"] is True
    assert result["approval_created"] is False
    assert result["authorization_created"] is False
    assert result["execution_authorized"] is False
    assert result["interface_specific_rendering"] is False


def test_shared_confirmation_replay_reconstructs_and_preserves_hash(tmp_path) -> None:
    result = _shared_confirmation(tmp_path)

    reconstructed = reconstruct_shared_confirmation_replay(tmp_path / "shared_confirmation")

    assert reconstructed["shared_confirmation_artifact"] == result["shared_confirmation_artifact"]
    assert reconstructed["shared_confirmation_artifact_hash"] == result["shared_confirmation_artifact_hash"]
    assert reconstructed["source_evidence_binding_hash"] == result["source_evidence_binding_hash"]
    assert reconstructed["authority_granted"] is False
    assert reconstructed["approval_created"] is False
    assert reconstructed["authorization_created"] is False


def test_shared_confirmation_section_embeds_in_canonical_communication_artifact(tmp_path) -> None:
    confirmation = _shared_confirmation(tmp_path)

    result = create_ubtr_human_communication_artifact(
        communication_id="COMM-SHARED-CONFIRMATION-001",
        source_component="UBTR",
        target_human_context="ACLI_OPERATOR",
        communication_domain="HUMAN_CONFIRMATION",
        communication_level=LEVEL_STANDARD,
        required_human_action="review shared confirmation section",
        replay_lineage=_lineage("shared-confirmation-communication"),
        rollback_reference="ROLLBACK-SHARED-CONFIRMATION-COMM-001",
        csa_reference="CSA-SHARED-CONFIRMATION-001",
        csa_hash=replay_hash({"csa": "shared-confirmation"}),
        confirmation_section=confirmation["confirmation_section"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "shared_confirmation_communication",
    )
    artifact = result["communication_artifact"]

    assert artifact["sections_rendered"] == ["confirmation"]
    assert artifact["sections"]["confirmation"]["section_type"] == "CONFIRMATION"
    assert artifact["sections"]["confirmation"]["source_evidence_binding_hash"].startswith("sha256:")
    assert artifact["authority_flags"]["approval_authority"] is False
    assert artifact["authority_flags"]["authorization_authority"] is False


def test_shared_confirmation_rejects_authoritative_response_model(tmp_path) -> None:
    _shared_confirmation(tmp_path)
    replay_file = (
        tmp_path
        / "shared_confirmation"
        / "000_uhcl_shared_confirmation_model_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["response_models"]["CONFIRMATION"]["creates_authorization"] = True
    wrapper["replay_hash"] = replay_hash(
        {
            "replay_index": wrapper["replay_index"],
            "replay_step": wrapper["replay_step"],
            "event_type": wrapper["event_type"],
            "artifact": wrapper["artifact"],
        }
    )
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="response cannot set creates_authorization"):
        reconstruct_shared_confirmation_replay(tmp_path / "shared_confirmation")


def test_creates_all_provider_worker_product_communication_bindings(tmp_path) -> None:
    for binding_type in sorted(COMMUNICATION_BINDING_TYPES):
        result = _communication_binding(tmp_path, binding_type=binding_type)
        artifact = result["communication_binding_artifact"]
        section = result["typed_section_artifact"]

        assert artifact["artifact_type"] == COMMUNICATION_BINDING_ARTIFACT_TYPE
        assert artifact["binding_type"] == binding_type
        assert artifact["binding_group"] in {"PROVIDER", "WORKER", "PRODUCT"}
        assert artifact["typed_section_artifact_hash"] == section["artifact_hash"]
        assert artifact["source_evidence_binding_hash"] == section["source_evidence_binding_hash"]
        assert artifact["evidence_references_hash"] == section["evidence_references_hash"]
        assert artifact["binding_lineage"]["typed_section_artifact_hash"] == section["artifact_hash"]
        assert artifact["binding_lineage"]["source_evidence_binding_hash"] == artifact["source_evidence_binding_hash"]
        assert section["structured_content"]["binding_type"] == binding_type
        assert section["structured_content"]["non_authoritative"] is True
        assert result["provider_invoked"] is False
        assert result["worker_invoked"] is False
        assert result["product_behavior_created"] is False
        assert result["approval_created"] is False
        assert result["authorization_created"] is False
        assert result["repository_mutated"] is False


def test_communication_binding_replay_reconstructs_and_preserves_hash(tmp_path) -> None:
    result = _communication_binding(tmp_path, binding_type="PRODUCT1_AUDIT_PACKET_SUMMARY")

    reconstructed = reconstruct_communication_binding_replay(
        tmp_path / "binding_PRODUCT1_AUDIT_PACKET_SUMMARY"
    )

    assert reconstructed["communication_binding_artifact"] == result["communication_binding_artifact"]
    assert reconstructed["communication_binding_artifact_hash"] == result["communication_binding_artifact_hash"]
    assert reconstructed["binding_type"] == "PRODUCT1_AUDIT_PACKET_SUMMARY"
    assert reconstructed["binding_group"] == "PRODUCT"
    assert reconstructed["authority_granted"] is False


def test_communication_binding_typed_section_embeds_in_canonical_artifact(tmp_path) -> None:
    binding = _communication_binding(tmp_path, binding_type="PROVIDER_PROVENANCE")

    result = create_ubtr_human_communication_artifact(
        communication_id="COMM-BINDING-PROVIDER-PROVENANCE-001",
        source_component="UBTR",
        target_human_context="ACLI_OPERATOR",
        communication_domain="TRANSPARENCY",
        communication_level=LEVEL_STANDARD,
        required_human_action="review provider provenance communication binding",
        replay_lineage=_lineage("binding-provider-provenance-communication"),
        rollback_reference="ROLLBACK-BINDING-PROVIDER-PROVENANCE-COMM-001",
        csa_reference="CSA-BINDING-PROVIDER-PROVENANCE-001",
        csa_hash=replay_hash({"csa": "binding-provider-provenance"}),
        transparency_section=binding["typed_section_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "binding_provider_provenance_communication",
    )
    artifact = result["communication_artifact"]

    assert artifact["sections_rendered"] == ["transparency"]
    assert artifact["sections"]["transparency"]["structured_content"]["binding_type"] == "PROVIDER_PROVENANCE"
    assert artifact["sections"]["transparency"]["source_evidence_binding_hash"].startswith("sha256:")
    assert artifact["authority_flags"]["provider_authority"] is False


def test_communication_binding_tampering_fails_closed(tmp_path) -> None:
    _communication_binding(tmp_path, binding_type="WORKER_EXECUTION_SUMMARY")
    replay_file = (
        tmp_path
        / "binding_WORKER_EXECUTION_SUMMARY"
        / "000_uhcl_provider_worker_product_communication_binding_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["authority_flags"]["worker_authority"] = True
    wrapper["replay_hash"] = replay_hash(
        {
            "replay_index": wrapper["replay_index"],
            "replay_step": wrapper["replay_step"],
            "event_type": wrapper["event_type"],
            "artifact": wrapper["artifact"],
        }
    )
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="cannot grant worker_authority"):
        reconstruct_communication_binding_replay(tmp_path / "binding_WORKER_EXECUTION_SUMMARY")


def test_creates_recovery_guidance_with_recommendation_and_evidence(tmp_path) -> None:
    result = _recovery_guidance(tmp_path)
    artifact = result["recovery_guidance_artifact"]
    section = result["recovery_section"]

    assert artifact["artifact_type"] == RECOVERY_GUIDANCE_ARTIFACT_TYPE
    assert artifact["blocked_operation"] == "Provider activation cannot continue."
    assert artifact["cannot_continue_reason"] == "Required governance approval evidence is missing."
    assert artifact["missing_prerequisites"][0]["prerequisite_id"] == "GOVERNANCE-APPROVAL-REQUIRED"
    assert artifact["recommended_next_action"]["action_id"] == "REQUEST_APPROVAL_EVIDENCE"
    assert artifact["recommended_next_action"]["non_authoritative"] is True
    assert artifact["recovery_policy"]["automatic_recovery_allowed"] is False
    assert artifact["recovery_policy"]["provider_invocation_allowed"] is False
    assert artifact["recovery_policy"]["worker_execution_allowed"] is False
    assert artifact["recovery_policy"]["repository_mutation_allowed"] is False
    assert artifact["source_bindings"]["specific_sources"]["governance"]["reference"] == "GOVERNANCE-CHECKPOINT-RECOVERY-001"
    assert section["section_type"] == "RECOVERY"
    assert section["structured_content"]["automatic_recovery_performed"] is False
    assert section["structured_content"]["provider_invoked"] is False
    assert section["structured_content"]["worker_invoked"] is False
    assert result["automatic_recovery_performed"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_recovery_guidance_replay_reconstructs_and_preserves_hash(tmp_path) -> None:
    result = _recovery_guidance(tmp_path)

    reconstructed = reconstruct_recovery_guidance_replay(tmp_path / "recovery_guidance")

    assert reconstructed["recovery_guidance_artifact"] == result["recovery_guidance_artifact"]
    assert reconstructed["recovery_guidance_artifact_hash"] == result["recovery_guidance_artifact_hash"]
    assert reconstructed["recommended_next_action"] == result["recommended_next_action"]
    assert reconstructed["authority_granted"] is False
    assert reconstructed["automatic_recovery_performed"] is False


def test_recovery_guidance_section_embeds_in_canonical_communication_artifact(tmp_path) -> None:
    recovery = _recovery_guidance(tmp_path)

    result = create_ubtr_human_communication_artifact(
        communication_id="COMM-RECOVERY-GUIDANCE-001",
        source_component="UBTR",
        target_human_context="ACLI_OPERATOR",
        communication_domain="GUIDANCE",
        communication_level=LEVEL_STANDARD,
        required_human_action="review recovery guidance",
        replay_lineage=_lineage("recovery-guidance-communication"),
        rollback_reference="ROLLBACK-RECOVERY-GUIDANCE-COMM-001",
        csa_reference="CSA-RECOVERY-GUIDANCE-COMM-001",
        csa_hash=replay_hash({"csa": "recovery-guidance-communication"}),
        recovery_section=recovery["recovery_section"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "recovery_guidance_communication",
    )
    artifact = result["communication_artifact"]

    assert artifact["sections_rendered"] == ["recovery"]
    assert artifact["sections"]["recovery"]["section_type"] == "RECOVERY"
    assert artifact["sections"]["recovery"]["structured_content"]["recommended_next_action"]["action_id"] == "REQUEST_APPROVAL_EVIDENCE"
    assert artifact["authority_flags"]["execution_authority"] is False
    assert artifact["authority_flags"]["mutation_authority"] is False


def test_recovery_guidance_rejects_recommendation_outside_available_actions(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="recommended_next_action must reference an available action"):
        create_recovery_guidance_model(
            recovery_id="RECOVERY-GUIDANCE-INVALID",
            source_component=SOURCE_COMPONENT_GOVERNANCE,
            target_human_context="ACLI_OPERATOR",
            communication_level=LEVEL_STANDARD,
            blocked_operation="Operation blocked.",
            cannot_continue_reason="Missing prerequisite.",
            missing_prerequisites=[
                {
                    "prerequisite_id": "PREREQ-001",
                    "description": "A required input is missing.",
                }
            ],
            available_recovery_actions=[
                {
                    "action_id": "REQUEST_INPUT",
                    "description": "Ask for input.",
                }
            ],
            recommended_next_action={
                "action_id": "EXECUTE_ANYWAY",
                "reason": "Invalid recommendation.",
            },
            evidence_references=_evidence("invalid-recovery"),
            created_at=CREATED_AT,
            replay_dir=tmp_path / "recovery_guidance_invalid",
        )


def test_recovery_guidance_tampering_fails_closed(tmp_path) -> None:
    _recovery_guidance(tmp_path)
    replay_file = (
        tmp_path
        / "recovery_guidance"
        / "000_uhcl_recovery_guidance_model_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["recovery_policy"]["automatic_recovery_allowed"] = True
    wrapper["replay_hash"] = replay_hash(
        {
            "replay_index": wrapper["replay_index"],
            "replay_step": wrapper["replay_step"],
            "event_type": wrapper["event_type"],
            "artifact": wrapper["artifact"],
        }
    )
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="policy mismatch"):
        reconstruct_recovery_guidance_replay(tmp_path / "recovery_guidance")


def test_typed_section_replay_reconstructs_and_preserves_hash(tmp_path) -> None:
    result = _typed_section(tmp_path, section_type="RISKS")

    reconstructed = reconstruct_typed_communication_section_replay(
        tmp_path / "typed_RISKS_STANDARD"
    )

    assert reconstructed["typed_section_artifact"] == result["typed_section_artifact"]
    assert reconstructed["typed_section_artifact_hash"] == result["typed_section_artifact_hash"]
    assert reconstructed["section_type"] == "RISKS"
    assert reconstructed["authority_granted"] is False


def test_typed_section_can_be_embedded_in_canonical_communication_artifact(tmp_path) -> None:
    assumptions = _typed_section(tmp_path, section_type="ASSUMPTIONS")
    risks = _typed_section(tmp_path, section_type="RISKS")
    uncertainties = _typed_section(tmp_path, section_type="UNCERTAINTIES")
    recovery = _typed_section(tmp_path, section_type="RECOVERY")

    result = create_ubtr_human_communication_artifact(
        communication_id="COMM-TYPED-SECTIONS-001",
        source_component="UBTR",
        target_human_context="ACLI_OPERATOR",
        communication_domain=DOMAIN_UNDERSTANDING,
        communication_level=LEVEL_STANDARD,
        required_human_action="review typed communication sections",
        replay_lineage=_lineage("typed-communication"),
        rollback_reference="ROLLBACK-COMM-TYPED-001",
        csa_reference="CSA-TYPED-001",
        csa_hash=replay_hash({"csa": "typed"}),
        assumptions_section=assumptions["typed_section_artifact"],
        risks_section=risks["typed_section_artifact"],
        uncertainties_section=uncertainties["typed_section_artifact"],
        recovery_section=recovery["typed_section_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "typed_communication",
    )

    artifact = result["communication_artifact"]

    assert artifact["sections_rendered"] == [
        "assumptions",
        "recovery",
        "risks",
        "uncertainties",
    ]
    assert artifact["sections"]["assumptions"]["section_type"] == "ASSUMPTIONS"
    assert artifact["sections"]["recovery"]["section_type"] == "RECOVERY"
    assert artifact["source_references"]["sections_hash"].startswith("sha256:")


def test_supports_all_canonical_domains_and_levels(tmp_path) -> None:
    for domain in sorted(COMMUNICATION_DOMAINS):
        for level in sorted(COMMUNICATION_LEVELS):
            result = _create(tmp_path, domain=domain, level=level)
            assert result["communication_domain"] == domain
            assert result["communication_level"] == level


def test_reconstructs_replay_and_preserves_hash(tmp_path) -> None:
    result = _create(tmp_path)

    reconstructed = reconstruct_ubtr_human_communication_replay(tmp_path / "UNDERSTANDING_STANDARD")

    assert reconstructed["communication_artifact"] == result["communication_artifact"]
    assert reconstructed["communication_artifact_hash"] == result["communication_artifact_hash"]
    assert reconstructed["communication_domain"] == DOMAIN_UNDERSTANDING
    assert reconstructed["communication_level"] == LEVEL_STANDARD
    assert reconstructed["authority_granted"] is False


def test_invalid_domain_fails_closed_before_replay_write(tmp_path) -> None:
    replay_dir = tmp_path / "invalid"

    with pytest.raises(FailClosedRuntimeError, match="communication_domain is not supported"):
        create_ubtr_human_communication_artifact(
            communication_id="COMM-INVALID",
            source_component="UBTR",
            target_human_context="ACLI_OPERATOR",
            communication_domain="TERMINAL_RENDERING",
            communication_level=LEVEL_STANDARD,
            required_human_action="review",
            replay_lineage=_lineage("invalid"),
            rollback_reference="ROLLBACK-INVALID",
            created_at=CREATED_AT,
            replay_dir=replay_dir,
            understanding_section={"summary": "Invalid domain."},
        )

    assert not replay_dir.exists()


def test_empty_sections_fail_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="at least one communication section is required"):
        create_ubtr_human_communication_artifact(
            communication_id="COMM-EMPTY",
            source_component="UBTR",
            target_human_context="ACLI_OPERATOR",
            communication_domain=DOMAIN_UNDERSTANDING,
            communication_level=LEVEL_STANDARD,
            required_human_action="review",
            replay_lineage=_lineage("empty"),
            rollback_reference="ROLLBACK-EMPTY",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "empty",
        )


def test_replay_tampering_fails_closed(tmp_path) -> None:
    _create(tmp_path)
    replay_file = (
        tmp_path
        / "UNDERSTANDING_STANDARD"
        / "000_ubtr_human_communication_artifact_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["authority_flags"]["execution_authority"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_ubtr_human_communication_replay(tmp_path / "UNDERSTANDING_STANDARD")


def test_typed_section_replay_tampering_fails_closed(tmp_path) -> None:
    _typed_section(tmp_path, section_type="CONFIRMATION")
    replay_file = (
        tmp_path
        / "typed_CONFIRMATION_STANDARD"
        / "000_uhcl_typed_communication_section_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["authority_flags"]["approval_authority"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_typed_communication_section_replay(tmp_path / "typed_CONFIRMATION_STANDARD")


def test_invalid_typed_section_evidence_fails_closed_before_replay_write(tmp_path) -> None:
    replay_dir = tmp_path / "typed_invalid"

    with pytest.raises(FailClosedRuntimeError, match="evidence_references\\[0\\].evidence_hash"):
        create_typed_communication_section(
            section_id="SECTION-INVALID-EVIDENCE",
            section_type="EXPLANATION",
            communication_level=LEVEL_STANDARD,
            structured_content={"summary": "Invalid evidence hash."},
            evidence_references=[
                {
                    "evidence_reference": "EVIDENCE-INVALID",
                    "evidence_hash": "not-a-hash",
                }
            ],
            created_at=CREATED_AT,
            replay_dir=replay_dir,
        )

    assert not replay_dir.exists()


def test_invalid_source_evidence_binding_component_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="source_component is not supported"):
        create_typed_communication_section(
            section_id="SECTION-INVALID-SOURCE-COMPONENT",
            section_type="GUIDANCE",
            communication_level=LEVEL_STANDARD,
            structured_content={"summary": "Invalid source component."},
            evidence_references=_evidence("invalid-component"),
            source_component="TERMINAL",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "invalid_source_component",
        )


def test_source_evidence_binding_tampering_fails_closed(tmp_path) -> None:
    _evidence_bound_section(tmp_path)
    replay_file = (
        tmp_path
        / "evidence_bound_section"
        / "000_uhcl_typed_communication_section_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["source_bindings"]["source_evidence_hashes"] = [replay_hash({"tampered": True})]
    wrapper["replay_hash"] = replay_hash(
        {
            "replay_index": wrapper["replay_index"],
            "replay_step": wrapper["replay_step"],
            "event_type": wrapper["event_type"],
            "artifact": wrapper["artifact"],
        }
    )
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="source evidence binding hash list mismatch"):
        reconstruct_typed_communication_section_replay(tmp_path / "evidence_bound_section")


def test_runtime_has_no_interface_provider_worker_deployment_or_mutation_surfaces() -> None:
    import aigol.runtime.ubtr_human_communication_model_runtime as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "render_operator_response(" not in source
    assert "write_text(" not in source
