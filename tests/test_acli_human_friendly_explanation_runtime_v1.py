"""Tests for HUMAN_FRIENDLY_ACLI_EXPLANATION_IMPLEMENTATION_V1."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.acli_human_friendly_explanation_runtime import (
    ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1,
    create_acli_human_friendly_explanation,
    reconstruct_acli_human_friendly_explanation_replay,
    render_acli_human_friendly_explanation,
)
from aigol.runtime.conversational_routing_visibility_runtime import (
    ROUTING_SELECTED,
    record_conversational_routing_visibility,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.universal_intake_layer_runtime import record_universal_intake


CREATED_AT = "2026-06-24T00:00:00Z"


def _routing_capture(tmp_path):
    return record_conversational_routing_visibility(
        turn_id="TURN-000001",
        prompt_id="SESSION:TURN-000001",
        human_prompt="Add replay validation",
        workflow_id="GOVERNED_DEVELOPMENT_WORKFLOW",
        routing_status=ROUTING_SELECTED,
        routing_confidence="HIGH",
        matched_signals=["development-intent"],
        competing_signals=[],
        routing_reason="Governed development workflow selected.",
        routing_timestamp=CREATED_AT,
        replay_dir=tmp_path / "routing_visibility",
    )


def _intake_capture(tmp_path, routing_capture):
    return record_universal_intake(
        intake_id="SESSION:TURN-000001:UNIVERSAL-INTAKE",
        turn_id="TURN-000001",
        prompt_id="SESSION:TURN-000001",
        human_prompt="Add replay validation",
        chain_id="SESSION:TURN-000001",
        workflow_id="GOVERNED_DEVELOPMENT_WORKFLOW",
        routing_visibility_artifact=routing_capture["conversational_routing_visibility_artifact"],
        routing_visibility_replay_reference=routing_capture[
            "conversational_routing_visibility_replay_reference"
        ],
        source_router_replay_reference=str(tmp_path / "source_router"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "universal_intake",
    )


def _proposal_capture() -> dict:
    proposal = {
        "proposal_id": "PROPOSAL-001",
        "artifact_hash": "sha256:proposal",
    }
    return {
        "proposal_artifact": proposal,
        "target_paths": ["docs/governance/ACLI_GOVERNED_DEVELOPMENT_TEST_V1.md"],
        "replay_reference": "runtime/session/TURN-000001/acli_governed_development_execution_bridge",
    }


def _canonical_semantic_lineage() -> dict:
    return {
        "canonical_semantic_artifact_reference": "CSA-EXPLANATION-RENDERING-000001",
        "canonical_semantic_artifact_hash": "sha256:explanation-rendering-csa-000001",
        "semantic_routing_source": "CANONICAL_SEMANTIC_ARTIFACT",
        "migration_batch_id": "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_10",
    }


def _capture(tmp_path):
    routing = _routing_capture(tmp_path)
    intake = _intake_capture(tmp_path, routing)
    return create_acli_human_friendly_explanation(
        explanation_id="SESSION:TURN-000001:HUMAN-FRIENDLY-EXPLANATION",
        turn_id="TURN-000001",
        prompt_id="SESSION:TURN-000001",
        human_prompt="Add replay validation",
        workflow_id="GOVERNED_DEVELOPMENT_WORKFLOW",
        routing_visibility_artifact=routing["conversational_routing_visibility_artifact"],
        universal_intake_artifact=intake["universal_intake_artifact"],
        proposal_capture=_proposal_capture(),
        replay_dir=tmp_path / "human_friendly_explanation",
        created_at=CREATED_AT,
    )


def _capture_with_csa(tmp_path):
    routing = _routing_capture(tmp_path)
    intake = _intake_capture(tmp_path, routing)
    return create_acli_human_friendly_explanation(
        explanation_id="SESSION:TURN-000001:HUMAN-FRIENDLY-EXPLANATION-G2-11",
        turn_id="TURN-000001",
        prompt_id="SESSION:TURN-000001",
        human_prompt="Add replay validation",
        workflow_id="GOVERNED_DEVELOPMENT_WORKFLOW",
        routing_visibility_artifact=routing["conversational_routing_visibility_artifact"],
        universal_intake_artifact=intake["universal_intake_artifact"],
        proposal_capture=_proposal_capture(),
        replay_dir=tmp_path / "human_friendly_explanation_g2_11",
        created_at=CREATED_AT,
        canonical_semantic_lineage=_canonical_semantic_lineage(),
    )


def test_explanation_renders_required_sections_and_preserves_authority_flags(tmp_path) -> None:
    capture = _capture(tmp_path)
    artifact = capture["human_friendly_explanation_artifact"]
    rendered = render_acli_human_friendly_explanation(capture)

    assert artifact["artifact_type"] == ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1
    assert artifact["ubtr_human_output_primary"] is True
    assert artifact["ubtr_human_output_reference"].endswith("ubtr_human_output")
    assert artifact["ubtr_human_output_hash"].startswith("sha256:")
    assert artifact["primary_render_source"] == "UBTR_GOVERNANCE_TO_HUMAN_TRANSLATION"
    assert artifact["explanation_rendering_source"] == "UBTR_GOVERNANCE_TO_HUMAN_TRANSLATION_WITH_COMPATIBILITY_FALLBACK"
    assert artifact["explanation_rendering_parity_status"] == "CSA_LINEAGE_UNAVAILABLE_COMPATIBILITY_FALLBACK_VISIBLE"
    assert artifact["compatibility_fallback_active"] is True
    assert artifact["visibility_only"] is True
    assert artifact["authority_granted"] is False
    assert artifact["provider_authority"] is False
    assert artifact["approval_authority"] is False
    assert artifact["execution_authority"] is False
    assert artifact["worker_authority"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["repository_mutation_performed"] is False
    assert artifact["uhcl_wrapper_wiring"]["uhcl_consumed"] is True
    assert artifact["uhcl_wrapper_wiring"]["legacy_contract_preserved"] is True
    assert artifact["uhcl_wrapper_wiring"]["new_communication_semantics_introduced"] is False
    assert "WHAT I UNDERSTOOD" in rendered
    assert "GOVERNANCE STATE EXPLANATION" in rendered
    assert "COMPATIBILITY OPERATOR DETAILS" in rendered
    assert "WHAT WILL HAPPEN" in rendered
    assert "WHAT WILL NOT HAPPEN" in rendered
    assert "WHAT REQUIRES YOUR APPROVAL" in rendered
    assert "WHAT TO TYPE NEXT" in rendered
    assert "REPLAY VISIBILITY" in rendered
    assert "EXPLANATION TRANSPARENCY" in rendered
    assert "Authoritative State" in rendered
    assert "AiGOL Governance" in rendered
    assert "Explanation Source" in rendered
    assert "Deterministic ACLI" in rendered
    assert "Provider" in rendered
    assert "Disabled By Configuration" in rendered
    assert "Explanation Confidence" in rendered
    assert "Governance Only" in rendered
    assert "Type APPROVE to continue." in rendered
    assert "no repository mutation will occur before approval" in rendered


def test_explanation_rendering_records_csa_primary_section_parity(tmp_path) -> None:
    capture = _capture_with_csa(tmp_path)
    artifact = capture["human_friendly_explanation_artifact"]
    comparison = artifact["explanation_rendering_comparison_artifact"]
    replay = reconstruct_acli_human_friendly_explanation_replay(
        capture["human_friendly_explanation_replay_reference"]
    )

    assert artifact["explanation_rendering_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert artifact["explanation_rendering_parity_status"] == "CSA_COMPATIBILITY_SECTION_PARITY_PROVEN"
    assert artifact["canonical_semantic_artifact_hash"] == "sha256:explanation-rendering-csa-000001"
    assert comparison["previous_compatibility_explanation"]["source"] == "COMPATIBILITY_HUMAN_FRIENDLY_EXPLANATION"
    assert comparison["csa_explanation_projection"]["available"] is True
    assert comparison["semantic_equivalence_result"] == "EQUIVALENT"
    assert comparison["semantic_differences"] == []
    assert all(comparison["semantic_parity_evidence"]["section_parity"].values())
    assert comparison["semantic_parity_evidence"]["compatibility_fallback_available"] is True
    assert comparison["semantic_parity_evidence"]["provider_wording_advisory_only"] is True
    assert artifact["authority_granted"] is False
    assert artifact["provider_authority"] is False
    assert artifact["approval_authority"] is False
    assert artifact["execution_authority"] is False
    assert artifact["worker_authority"] is False
    assert replay["explanation_rendering_comparison_hash"] == comparison["artifact_hash"]
    assert replay["explanation_rendering_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert replay["canonical_semantic_artifact_hash"] == "sha256:explanation-rendering-csa-000001"


def test_explanation_replay_reconstructs_and_detects_tampering(tmp_path) -> None:
    capture = _capture(tmp_path)
    replay_dir = capture["human_friendly_explanation_replay_reference"]

    replay = reconstruct_acli_human_friendly_explanation_replay(replay_dir)
    assert replay["workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert replay["visibility_only"] is True
    assert replay["authority_granted"] is False
    assert replay["explanation_confidence"] == "GOVERNANCE_ONLY"
    assert replay["explanation_completeness"] == "COMPLETE"
    assert replay["render_mode"] == "DETERMINISTIC_ONLY"
    assert replay["ubtr_human_output_primary"] is True
    assert replay["ubtr_human_output_hash"].startswith("sha256:")
    assert replay["compatibility_fallback_active"] is True
    assert replay["primary_render_source"] == "UBTR_GOVERNANCE_TO_HUMAN_TRANSLATION"
    assert replay["explanation_transparency_artifact"]["provider_status"] == "DISABLED_BY_CONFIGURATION"

    replay_file = tmp_path / "human_friendly_explanation" / "000_acli_human_friendly_explanation_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["rendered_explanation"] = "tampered"
    artifact_without_hash = dict(wrapper["artifact"])
    artifact_without_hash.pop("artifact_hash", None)
    wrapper["artifact"]["artifact_hash"] = replay_hash(artifact_without_hash)
    wrapper_without_hash = dict(wrapper)
    wrapper_without_hash.pop("replay_hash", None)
    wrapper["replay_hash"] = replay_hash(wrapper_without_hash)
    replay_file.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="rendered output hash mismatch"):
        reconstruct_acli_human_friendly_explanation_replay(replay_dir)
