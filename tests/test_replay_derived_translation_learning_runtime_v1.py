"""Tests for REPLAY_DERIVED_TRANSLATION_LEARNING_RUNTIME_V1."""

from __future__ import annotations

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_derived_translation_learning_runtime import (
    IMPROVEMENT_PROPOSAL_TYPE,
    NO_PROMOTION_CANDIDATES,
    PROMOTION_CANDIDATES_IDENTIFIED,
    analyze_replay_derived_translation_learning,
    reconstruct_replay_derived_translation_learning_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash
from aigol.runtime.universal_translation_artifact_schema import (
    HIGH,
    HUMAN_TO_GOVERNANCE,
    NO_AMBIGUITY,
    create_universal_translation_artifact,
)


CREATED_AT = "2026-06-25T00:00:00Z"


def _translation_request(index: int) -> dict:
    return {
        "translation_request_id": f"LEARNING-REQUEST-{index:03d}",
        "operator_context": "test-operator",
        "created_at": CREATED_AT,
    }


def _artifact(index: int, human_request: str, payload: dict | None = None) -> dict:
    governance_payload = payload or {
        "workflow_candidate": "GOVERNED_DEVELOPMENT_WORKFLOW",
        "intent_family": "GOVERNANCE_CREATE_INTENT",
        "requested_actions": ["CREATE"],
        "approval_required": True,
        "entities": {"artifact_identifiers": [], "target_paths": []},
    }
    return create_universal_translation_artifact(
        translation_id=f"LEARNING-TRANSLATION-{index:03d}",
        translation_request=_translation_request(index),
        source_direction=HUMAN_TO_GOVERNANCE,
        source_payload={"human_request": human_request},
        normalized_intent={"normalized_text": human_request.lower()},
        translated_governance_payload=governance_payload,
        ambiguity_flags={
            "ambiguity_status": NO_AMBIGUITY,
            "clarification_required": False,
            "clarification_questions": [],
        },
        confidence=HIGH,
        replay_reference=f"/tmp/replay/learning-{index:03d}",
        created_at=CREATED_AT,
    )


def test_repeated_confirmed_translation_pattern_emits_proposal_only_candidate(tmp_path) -> None:
    artifacts = [
        _artifact(1, "Create governance artifact ALPHA_GUIDE_V1."),
        _artifact(2, "Add governance artifact BETA_GUIDE_V1."),
        _artifact(3, "Draft governance artifact GAMMA_GUIDE_V1."),
    ]

    result = analyze_replay_derived_translation_learning(
        learning_id="LEARNING-001",
        translation_artifacts=artifacts,
        human_confirmations=[
            {
                "confirmation_id": "CONFIRM-001",
                "confirmed": True,
                "translation_artifact_hash": artifacts[0]["artifact_hash"],
                "confirmed_by": "human",
            }
        ],
        provider_explanations=[{"provider_id": "explanation-provider", "status": "ACCEPTED"}],
        clarification_history=[],
        err_evidence={"err_id": "ERR-LEARNING-001", "status": "RECORDED"},
        replay_dir=tmp_path / "learning",
        created_at=CREATED_AT,
    )

    proposal = result["improvement_proposals"][0]
    cluster = result["pattern_clusters"][0]

    assert result["learning_status"] == PROMOTION_CANDIDATES_IDENTIFIED
    assert result["proposal_count"] == 1
    assert cluster["promotion_candidate"] is True
    assert cluster["occurrence_count"] == 3
    assert cluster["unique_expression_count"] == 3
    assert cluster["human_confirmation_count"] == 1
    assert proposal["artifact_type"] == IMPROVEMENT_PROPOSAL_TYPE
    assert proposal["proposal_kind"] == "DETERMINISTIC_TRANSLATION_RULE_CANDIDATE"
    assert proposal["ppp_route_required"] is True
    assert proposal["human_approval_required"] is True
    assert proposal["implementation_authorized"] is False
    assert proposal["deterministic_rule_modified"] is False
    assert result["runtime_behavior_modified"] is False
    assert result["deterministic_rules_modified"] is False
    assert result["governance_mutated"] is False


def test_unconfirmed_pattern_does_not_emit_promotion_proposal(tmp_path) -> None:
    artifacts = [
        _artifact(1, "Create governance artifact ALPHA_GUIDE_V1."),
        _artifact(2, "Add governance artifact BETA_GUIDE_V1."),
        _artifact(3, "Draft governance artifact GAMMA_GUIDE_V1."),
    ]

    result = analyze_replay_derived_translation_learning(
        learning_id="LEARNING-002",
        translation_artifacts=artifacts,
        replay_dir=tmp_path / "learning",
        created_at=CREATED_AT,
    )

    assert result["learning_status"] == NO_PROMOTION_CANDIDATES
    assert result["proposal_count"] == 0
    assert result["pattern_clusters"][0]["promotion_candidate"] is False


def test_unstable_mappings_are_separate_clusters_without_candidate(tmp_path) -> None:
    artifacts = [
        _artifact(1, "Create governance artifact ALPHA_GUIDE_V1."),
        _artifact(
            2,
            "Create governance artifact BETA_GUIDE_V1.",
            payload={
                "workflow_candidate": "SECURITY_GOVERNED_WORKFLOW",
                "intent_family": "SECURITY_CREATE_INTENT",
                "requested_actions": ["CREATE"],
                "approval_required": True,
                "entities": {"artifact_identifiers": [], "target_paths": []},
            },
        ),
    ]

    result = analyze_replay_derived_translation_learning(
        learning_id="LEARNING-003",
        translation_artifacts=artifacts,
        human_confirmations=[
            {"confirmed": True, "translation_artifact_hash": artifacts[0]["artifact_hash"]},
            {"confirmed": True, "translation_artifact_hash": artifacts[1]["artifact_hash"]},
        ],
        replay_dir=tmp_path / "learning",
        created_at=CREATED_AT,
    )

    assert result["learning_status"] == NO_PROMOTION_CANDIDATES
    assert len(result["pattern_clusters"]) == 2
    assert all(cluster["occurrence_count"] == 1 for cluster in result["pattern_clusters"])


def test_replay_history_wrappers_are_accepted_as_input(tmp_path) -> None:
    artifact = _artifact(1, "Create governance artifact ALPHA_GUIDE_V1.")
    wrapper = {
        "replay_index": 0,
        "replay_step": "translation",
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)

    result = analyze_replay_derived_translation_learning(
        learning_id="LEARNING-004",
        translation_artifacts=[],
        replay_history=[wrapper],
        replay_dir=tmp_path / "learning",
        created_at=CREATED_AT,
    )

    assert result["learning_artifact"]["translation_artifact_count"] == 1
    assert result["pattern_clusters"][0]["translation_artifact_hashes"] == [artifact["artifact_hash"]]


def test_learning_replay_reconstructs_proposals_and_authority_boundaries(tmp_path) -> None:
    artifacts = [
        _artifact(1, "Create governance artifact ALPHA_GUIDE_V1."),
        _artifact(2, "Add governance artifact BETA_GUIDE_V1."),
        _artifact(3, "Draft governance artifact GAMMA_GUIDE_V1."),
    ]
    result = analyze_replay_derived_translation_learning(
        learning_id="LEARNING-005",
        translation_artifacts=artifacts,
        human_confirmations=[{"confirmed": True, "translation_artifact_hash": artifacts[0]["artifact_hash"]}],
        replay_dir=tmp_path / "learning",
        created_at=CREATED_AT,
    )

    reconstructed = reconstruct_replay_derived_translation_learning_replay(tmp_path / "learning")

    assert reconstructed["learning_artifact"] == result["learning_artifact"]
    assert reconstructed["proposal_count"] == 1
    assert reconstructed["proposal_only"] is True
    assert reconstructed["authority_granted"] is False
    assert reconstructed["deterministic_rules_modified"] is False
    assert reconstructed["execution_requested"] is False


def test_malformed_translation_artifact_fails_closed_before_replay_write(tmp_path) -> None:
    replay_dir = tmp_path / "learning"

    with pytest.raises(FailClosedRuntimeError, match="malformed structure"):
        analyze_replay_derived_translation_learning(
            learning_id="LEARNING-006",
            translation_artifacts=[{"bad": "artifact"}],
            replay_dir=replay_dir,
            created_at=CREATED_AT,
        )

    assert not replay_dir.exists()


def test_replay_tampering_fails_closed(tmp_path) -> None:
    artifacts = [
        _artifact(1, "Create governance artifact ALPHA_GUIDE_V1."),
        _artifact(2, "Add governance artifact BETA_GUIDE_V1."),
        _artifact(3, "Draft governance artifact GAMMA_GUIDE_V1."),
    ]
    analyze_replay_derived_translation_learning(
        learning_id="LEARNING-007",
        translation_artifacts=artifacts,
        human_confirmations=[{"confirmed": True, "translation_artifact_hash": artifacts[0]["artifact_hash"]}],
        replay_dir=tmp_path / "learning",
        created_at=CREATED_AT,
    )
    replay_file = tmp_path / "learning" / "000_replay_derived_translation_learning_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["deterministic_rules_modified"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_replay_derived_translation_learning_replay(tmp_path / "learning")
