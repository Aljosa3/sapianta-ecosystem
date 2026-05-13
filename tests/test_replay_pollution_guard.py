from sapianta_bridge.hygiene.replay_pollution_guard import detect_replay_pollution


def test_replay_pollution_guard_allows_canonical_artifacts() -> None:
    result = detect_replay_pollution(
        [
            ".github/governance/evidence/GOVERNANCE_SCOPE_LOCK_V1.md",
            "sapianta_bridge/hygiene/evidence/WORKTREE_HYGIENE_POLICY.json",
        ]
    )

    assert result["replay_pollution_detected"] is False
    assert len(result["canonical_artifacts"]) == 2
    assert result["polluting_artifacts"] == []
    assert result["automatic_cleanup_performed"] is False


def test_replay_pollution_guard_detects_transient_artifacts() -> None:
    result = detect_replay_pollution(
        [
            ".github/governance/evidence/GOVERNANCE_SCOPE_LOCK_V1.md",
            "sapianta_bridge/architecture/__pycache__/layer_model.cpython-312.pyc",
        ]
    )

    assert result["replay_pollution_detected"] is True
    assert result["requires_human_review"] is True
    assert result["polluting_artifacts"][0]["classification"] == "TRANSIENT_RUNTIME_ARTIFACT"


def test_replay_pollution_guard_detects_unknown_artifacts() -> None:
    result = detect_replay_pollution(["local-notes/output.bin"])

    assert result["replay_pollution_detected"] is True
    assert result["polluting_artifacts"][0]["classification"] == "UNKNOWN_ARTIFACT"
