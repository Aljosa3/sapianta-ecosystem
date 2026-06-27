"""Tests for UBTR to OCS cognition handoff runtime."""

from __future__ import annotations

import pytest

from aigol.runtime.canonical_semantic_artifact_runtime import create_canonical_semantic_artifact_from_translation
from aigol.runtime.human_to_governance_translation_runtime import translate_human_to_governance
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.ubtr_ocs_cognition_handoff_runtime import (
    HANDOFF_COMPLETED,
    run_ubtr_ocs_cognition_handoff,
    reconstruct_ubtr_ocs_cognition_handoff_replay,
)
from aigol.runtime.ubtr_semantic_cognition_orchestration_runtime import (
    OCS_COGNITION_REQUESTED,
    orchestrate_ubtr_semantic_cognition,
)


CREATED_AT = "2026-06-27T00:00:00Z"


def _ubtr_orchestration_artifact(tmp_path, human_request: str) -> dict:
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
    orchestration = orchestrate_ubtr_semantic_cognition(
        orchestration_id="UBTR-ORCH-001",
        canonical_semantic_artifact=semantic["semantic_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "orchestration",
    )
    return orchestration["orchestration_artifact"]


def test_ubtr_ocs_handoff_runs_existing_ocs_cognition_pipeline(tmp_path) -> None:
    orchestration_artifact = _ubtr_orchestration_artifact(
        tmp_path,
        "Create a governance artifact for the new runtime",
    )

    result = run_ubtr_ocs_cognition_handoff(
        handoff_id="UBTR-OCS-HANDOFF-001",
        ubtr_orchestration_artifact=orchestration_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )

    assert orchestration_artifact["semantic_decision"] == OCS_COGNITION_REQUESTED
    assert result["handoff_status"] == HANDOFF_COMPLETED
    assert result["ubtr_ocs_cognition_request_hash"] == orchestration_artifact["ocs_cognition_request_hash"]
    assert result["ocs_context_hash"].startswith("sha256:")
    assert result["ocs_cognition_hash"].startswith("sha256:")
    assert result["ocs_cognition_status"] == "OCS_COGNITION_COMPLETED"
    assert result["ocs_provider_necessity"]["necessity_classification"] == "PROVIDER_REQUIRED"
    assert result["provider_selection_owner"] == "OCS"
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["execution_authorized"] is False
    assert result["authority_granted"] is False

    reconstructed = reconstruct_ubtr_ocs_cognition_handoff_replay(tmp_path / "handoff")
    assert reconstructed["handoff_status"] == HANDOFF_COMPLETED
    assert reconstructed["ocs_cognition_hash"] == result["ocs_cognition_hash"]


def test_ubtr_ocs_handoff_fails_closed_without_ocs_request(tmp_path) -> None:
    orchestration_artifact = _ubtr_orchestration_artifact(
        tmp_path,
        "Create governance artifact ACLI_USAGE_GUIDELINES_V1.",
    )

    result = run_ubtr_ocs_cognition_handoff(
        handoff_id="UBTR-OCS-HANDOFF-002",
        ubtr_orchestration_artifact=orchestration_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )

    assert result["fail_closed"] is True
    assert "OCS cognition was not requested" in result["failure_reason"]
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["execution_authorized"] is False


def test_ubtr_ocs_handoff_replay_tampering_fails_closed(tmp_path) -> None:
    orchestration_artifact = _ubtr_orchestration_artifact(
        tmp_path,
        "Create a governance artifact for the new runtime",
    )
    run_ubtr_ocs_cognition_handoff(
        handoff_id="UBTR-OCS-HANDOFF-003",
        ubtr_orchestration_artifact=orchestration_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )
    replay_file = tmp_path / "handoff" / "000_ubtr_ocs_cognition_handoff_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["execution_authorized"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_ubtr_ocs_cognition_handoff_replay(tmp_path / "handoff")
