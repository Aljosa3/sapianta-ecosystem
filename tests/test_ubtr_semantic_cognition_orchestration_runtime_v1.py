"""Tests for UBTR semantic cognition orchestration runtime."""

from __future__ import annotations

import pytest

from aigol.runtime.canonical_semantic_artifact_runtime import create_canonical_semantic_artifact_from_translation
from aigol.runtime.human_to_governance_translation_runtime import translate_human_to_governance
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.ubtr_semantic_cognition_orchestration_runtime import (
    DETERMINISTIC_SEMANTIC_ARTIFACT_VALID,
    OCS_COGNITION_REQUESTED,
    orchestrate_ubtr_semantic_cognition,
    reconstruct_ubtr_semantic_cognition_orchestration_replay,
)


CREATED_AT = "2026-06-26T00:00:00Z"


def _canonical_semantic_artifact(tmp_path, human_request: str) -> dict:
    translation = translate_human_to_governance(
        translation_request_id="TRANSLATION-001",
        human_request=human_request,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
        session_context={"canonical_chain_id": "CHAIN-001", "prompt_id": "PROMPT-001"},
        available_workflows=["GOVERNED_DEVELOPMENT_WORKFLOW"],
    )
    semantic = create_canonical_semantic_artifact_from_translation(
        semantic_artifact_id="SEMANTIC-001",
        translation_artifact=translation["translation_artifact"],
        conversation_id="CHAIN-001",
        workflow_id=None,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "semantic",
    )
    return semantic["semantic_artifact"]


def test_valid_canonical_semantic_artifact_continues_deterministically(tmp_path) -> None:
    semantic_artifact = _canonical_semantic_artifact(
        tmp_path,
        "Create governance artifact ACLI_USAGE_GUIDELINES_V1.",
    )

    result = orchestrate_ubtr_semantic_cognition(
        orchestration_id="UBTR-ORCH-001",
        canonical_semantic_artifact=semantic_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "orchestration",
    )

    assert result["semantic_decision"] == DETERMINISTIC_SEMANTIC_ARTIFACT_VALID
    assert result["decision_reasons"] == []
    assert result["ocs_cognition_request"] is None
    assert result["ocs_cognition_request_hash"] is None
    assert result["provider_invoked"] is False
    assert result["provider_selected"] is False
    assert result["worker_invoked"] is False
    assert result["execution_authorized"] is False
    assert result["authority_granted"] is False

    reconstructed = reconstruct_ubtr_semantic_cognition_orchestration_replay(tmp_path / "orchestration")
    assert reconstructed["semantic_decision"] == DETERMINISTIC_SEMANTIC_ARTIFACT_VALID
    assert reconstructed["canonical_semantic_artifact_hash"] == semantic_artifact["artifact_hash"]


def test_ambiguous_semantics_create_governed_ocs_cognition_request_without_provider_invocation(tmp_path) -> None:
    semantic_artifact = _canonical_semantic_artifact(
        tmp_path,
        "Create a governance artifact for the new runtime",
    )

    result = orchestrate_ubtr_semantic_cognition(
        orchestration_id="UBTR-ORCH-002",
        canonical_semantic_artifact=semantic_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "orchestration",
    )

    request = result["ocs_cognition_request"]

    assert result["semantic_decision"] == OCS_COGNITION_REQUESTED
    assert "SEMANTIC_AMBIGUITY_REQUIRES_COGNITION" in result["decision_reasons"]
    assert "GOVERNANCE_TARGET_ENTITY_MISSING" in result["decision_reasons"]
    assert result["ocs_cognition_request_hash"].startswith("sha256:")
    assert request["artifact_type"] == "UBTR_GOVERNED_OCS_COGNITION_REQUEST_V1"
    assert request["provider_selection_owner"] == "OCS"
    assert request["capability_escalation_owner"] == "OCS"
    assert request["multi_provider_comparison_owner"] == "OCS"
    assert request["provider_selection_required"] is True
    assert request["provider_invoked"] is False
    assert request["provider_selected"] is False
    assert request["worker_invoked"] is False
    assert request["execution_authorized"] is False
    assert request["authority_granted"] is False

    reconstructed = reconstruct_ubtr_semantic_cognition_orchestration_replay(tmp_path / "orchestration")
    assert reconstructed["semantic_decision"] == OCS_COGNITION_REQUESTED
    assert reconstructed["ocs_cognition_request_hash"] == result["ocs_cognition_request_hash"]


def test_orchestration_replay_tampering_fails_closed(tmp_path) -> None:
    semantic_artifact = _canonical_semantic_artifact(
        tmp_path,
        "Create governance artifact ACLI_USAGE_GUIDELINES_V1.",
    )
    orchestrate_ubtr_semantic_cognition(
        orchestration_id="UBTR-ORCH-003",
        canonical_semantic_artifact=semantic_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "orchestration",
    )
    replay_file = tmp_path / "orchestration" / "000_ubtr_semantic_cognition_orchestration_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["execution_authorized"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_ubtr_semantic_cognition_orchestration_replay(tmp_path / "orchestration")
