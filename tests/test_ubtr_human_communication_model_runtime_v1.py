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
    create_ubtr_human_communication_artifact,
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
