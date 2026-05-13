from pathlib import Path

from sapianta_bridge.hygiene.worktree_validator import (
    validate_candidate_paths,
    validate_staged_worktree,
)


def test_worktree_validator_accepts_canonical_candidates() -> None:
    result = validate_candidate_paths(
        [".github/governance/finalize/FINALIZE_REPO_WIDE_TEST_COLLECTION_STABILIZATION_V1.json"],
        gitignore_text="__pycache__/\n*.pyc\n.pytest_cache/\n*.pyo\n",
    )

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["mutated_repository"] is False


def test_worktree_validator_blocks_transient_candidates() -> None:
    result = validate_candidate_paths(
        ["sapianta_bridge/hygiene/__pycache__/artifact_classifier.cpython-312.pyc"],
        gitignore_text="__pycache__/\n*.pyc\n.pytest_cache/\n*.pyo\n",
    )

    assert result["valid"] is False
    assert result["errors"] == [{"field": "artifacts", "reason": "replay pollution detected"}]
    assert result["pollution"]["replay_pollution_detected"] is True


def test_worktree_validator_blocks_unknown_candidates() -> None:
    result = validate_candidate_paths(
        ["scratch/output.txt"],
        gitignore_text="__pycache__/\n*.pyc\n.pytest_cache/\n*.pyo\n",
    )

    assert result["valid"] is False
    assert result["pollution"]["polluting_artifacts"][0]["classification"] == "UNKNOWN_ARTIFACT"


def test_worktree_validator_reports_gitignore_policy_gap() -> None:
    result = validate_candidate_paths(
        [".github/governance/evidence/GOVERNANCE_SCOPE_LOCK_V1.md"],
        gitignore_text="*.pyc\n",
    )

    assert result["valid"] is False
    assert {"field": ".gitignore", "reason": "required hygiene patterns missing"} in result["errors"]


def test_staged_worktree_validator_is_read_only(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("__pycache__/\n*.pyc\n.pytest_cache/\n*.pyo\n", encoding="utf-8")
    result = validate_staged_worktree(tmp_path)

    assert result["mutated_repository"] is False
    assert result["gitignore"]["valid"] is True
