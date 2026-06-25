"""Tests for HUMAN_TO_GOVERNANCE_TRANSLATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.human_to_governance_translation_runtime import (
    DOMAIN_GOVERNANCE,
    HUMAN_TO_GOVERNANCE,
    MATERIAL_AMBIGUITY,
    NO_AMBIGUITY,
    UNSAFE_AMBIGUITY,
    reconstruct_human_to_governance_translation_replay,
    translate_human_to_governance,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.universal_translation_artifact_schema import translation_artifact_hash


CREATED_AT = "2026-06-25T00:00:00Z"


def test_translates_governance_artifact_request_to_universal_translation_artifact(tmp_path) -> None:
    result = translate_human_to_governance(
        translation_request_id="HTG-001",
        human_request=(
            "Create governance artifact ACLI_OPERATOR_GUIDE_V1 explaining ACLI approval, "
            "replay, validation, and execution behavior for a non-technical operator."
        ),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
        available_workflows=["GOVERNED_DEVELOPMENT_WORKFLOW"],
    )

    artifact = result["translation_artifact"]
    governance_payload = artifact["translated_governance_payload"]

    assert result["translation_status"] == "TRANSLATED"
    assert artifact["source_direction"] == HUMAN_TO_GOVERNANCE
    assert artifact["normalized_intent"]["domain_candidate"] == DOMAIN_GOVERNANCE
    assert artifact["normalized_intent"]["requested_actions"] == ["CREATE"]
    assert governance_payload["workflow_candidate"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert governance_payload["entities"]["artifact_identifiers"] == ["ACLI_OPERATOR_GUIDE_V1"]
    assert governance_payload["approval_required"] is True
    assert governance_payload["execution_requested"] is True
    assert artifact["ambiguity_flags"]["ambiguity_status"] == NO_AMBIGUITY
    assert artifact["provider_metadata"]["provider_used"] is False
    assert artifact["authority_flags"]["authority_granted"] is False
    assert result["provider_invoked"] is False
    assert result["workflow_executed"] is False
    assert result["governance_mutated"] is False


def test_translation_replay_reconstructs_and_preserves_hash(tmp_path) -> None:
    result = translate_human_to_governance(
        translation_request_id="HTG-002",
        human_request="Implement worker authorization checks in docs/governance/WORKER_AUTHORIZATION_V1.md.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )

    reconstructed = reconstruct_human_to_governance_translation_replay(tmp_path / "translation")

    assert reconstructed["translation_artifact"] == result["translation_artifact"]
    assert reconstructed["artifact_hash"] == translation_artifact_hash(result["translation_artifact"])
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["workflow_executed"] is False
    assert reconstructed["governance_mutated"] is False


def test_translation_output_is_deterministic_except_replay_location(tmp_path) -> None:
    kwargs = {
        "translation_request_id": "HTG-003",
        "human_request": "Add replay validation artifact REPLAY_VALIDATION_GUIDE_V1.",
        "created_at": CREATED_AT,
    }
    first = translate_human_to_governance(replay_dir=tmp_path / "first", **kwargs)
    second = translate_human_to_governance(replay_dir=tmp_path / "second", **kwargs)

    first_artifact = deepcopy(first["translation_artifact"])
    second_artifact = deepcopy(second["translation_artifact"])
    first_artifact.pop("artifact_hash")
    second_artifact.pop("artifact_hash")
    first_artifact.pop("replay_reference")
    second_artifact.pop("replay_reference")

    assert first_artifact == second_artifact
    assert first["normalized_intent"] == second["normalized_intent"]
    assert first["governance_intent_candidate"] == second["governance_intent_candidate"]


def test_ambiguous_request_fails_closed_into_clarification_candidate(tmp_path) -> None:
    result = translate_human_to_governance(
        translation_request_id="HTG-004",
        human_request="Fix this.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )

    artifact = result["translation_artifact"]
    governance_payload = artifact["translated_governance_payload"]

    assert artifact["ambiguity_flags"]["ambiguity_status"] == MATERIAL_AMBIGUITY
    assert artifact["ambiguity_flags"]["clarification_required"] is True
    assert governance_payload["workflow_candidate"] == "HUMAN_INTENT_CLARIFICATION_INTAKE"
    assert governance_payload["clarification_required"] is True
    assert result["workflow_executed"] is False
    assert result["governance_mutated"] is False


def test_unsafe_approval_bypass_request_is_marked_unsafe_without_execution(tmp_path) -> None:
    result = translate_human_to_governance(
        translation_request_id="HTG-005",
        human_request="Create governance artifact TEST_ARTIFACT_V1 without approval.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )

    artifact = result["translation_artifact"]

    assert artifact["ambiguity_flags"]["ambiguity_status"] == UNSAFE_AMBIGUITY
    assert artifact["ambiguity_flags"]["clarification_required"] is True
    assert artifact["confidence"] == "LOW"
    assert result["provider_invoked"] is False
    assert result["workflow_executed"] is False
    assert result["governance_mutated"] is False


def test_malformed_request_fails_closed_before_replay_write(tmp_path) -> None:
    replay_dir = tmp_path / "translation"

    with pytest.raises(FailClosedRuntimeError, match="human_request is required"):
        translate_human_to_governance(
            translation_request_id="HTG-006",
            human_request="   ",
            created_at=CREATED_AT,
            replay_dir=replay_dir,
        )

    assert not replay_dir.exists()


def test_replay_tampering_fails_closed(tmp_path) -> None:
    replay_dir = tmp_path / "translation"
    translate_human_to_governance(
        translation_request_id="HTG-007",
        human_request="Create governance artifact TAMPER_TEST_V1.",
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    replay_file = replay_dir / "000_human_to_governance_translation_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["confidence"] = "LOW"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_human_to_governance_translation_replay(replay_dir)
