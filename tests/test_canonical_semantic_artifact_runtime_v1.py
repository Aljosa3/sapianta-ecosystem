"""Tests for CANONICAL_SEMANTIC_ARTIFACT_RUNTIME_V1."""

from __future__ import annotations

import pytest

from aigol.runtime.canonical_semantic_artifact_runtime import (
    CANONICAL_SEMANTIC_ARTIFACT_TYPE,
    create_canonical_semantic_artifact_from_translation,
    reconstruct_canonical_semantic_artifact_replay,
)
from aigol.runtime.human_to_governance_translation_runtime import translate_human_to_governance
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json


CREATED_AT = "2026-06-26T00:00:00Z"


def _translation(tmp_path):
    return translate_human_to_governance(
        translation_request_id="TRANSLATION-001",
        human_request="Create governance artifact ACLI_USAGE_GUIDELINES_V1.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
        session_context={"canonical_chain_id": "CHAIN-001", "prompt_id": "PROMPT-001"},
        available_workflows=["GOVERNED_DEVELOPMENT_WORKFLOW"],
    )


def test_canonical_semantic_artifact_is_generated_from_translation(tmp_path) -> None:
    translation = _translation(tmp_path)

    result = create_canonical_semantic_artifact_from_translation(
        semantic_artifact_id="SEMANTIC-001",
        translation_artifact=translation["translation_artifact"],
        conversation_id="CHAIN-001",
        workflow_id=None,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "semantic",
    )

    artifact = result["semantic_artifact"]

    assert artifact["artifact_type"] == CANONICAL_SEMANTIC_ARTIFACT_TYPE
    assert artifact["workflow_identity"]["workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert artifact["semantic_identity"]["intent_family"] == "GOVERNANCE_CREATE_INTENT"
    assert artifact["authority_flags"]["semantic_authority"] is True
    assert artifact["authority_flags"]["execution_authority"] is False
    assert artifact["authority_flags"]["governance_authority"] is False
    assert result["authority_granted"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False

    reconstructed = reconstruct_canonical_semantic_artifact_replay(tmp_path / "semantic")
    assert reconstructed["semantic_artifact_hash"] == result["semantic_artifact_hash"]
    assert reconstructed["workflow_candidate"] == "GOVERNED_DEVELOPMENT_WORKFLOW"


def test_canonical_semantic_artifact_replay_tampering_fails_closed(tmp_path) -> None:
    translation = _translation(tmp_path)
    create_canonical_semantic_artifact_from_translation(
        semantic_artifact_id="SEMANTIC-002",
        translation_artifact=translation["translation_artifact"],
        conversation_id="CHAIN-002",
        workflow_id=None,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "semantic",
    )
    replay_file = tmp_path / "semantic" / "000_canonical_semantic_artifact_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["authority_flags"]["execution_authority"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_canonical_semantic_artifact_replay(tmp_path / "semantic")
