"""Tests for UBTR_HUMAN_COMMUNICATION_MODEL_RUNTIME_V1."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash
from aigol.runtime.ubtr_human_communication_model_runtime import (
    COMMUNICATION_ARTIFACT_TYPE,
    COMMUNICATION_DOMAINS,
    COMMUNICATION_LEVELS,
    DOMAIN_UNDERSTANDING,
    LEVEL_STANDARD,
    PROGRESSIVE_EXPLANATION_ARTIFACT_TYPE,
    SOURCE_COMPONENT_GOVERNANCE,
    SOURCE_COMPONENT_PRODUCT,
    TYPED_SECTION_ARTIFACT_TYPE,
    TYPED_SECTION_TYPES,
    derive_progressive_explanation,
    create_ubtr_human_communication_artifact,
    create_typed_communication_section,
    reconstruct_progressive_explanation_replay,
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
