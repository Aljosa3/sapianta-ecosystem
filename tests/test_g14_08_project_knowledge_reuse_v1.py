"""Regression tests for G14-08 project knowledge reuse in AiGOL Next."""

from __future__ import annotations

import json

from aigol.cli import aigol_cli


CREATED_AT = "2026-07-03T00:00:00Z"
SESSION_ID = "G14-08-PROJECT-KNOWLEDGE-REUSE"


def _run_aigol_next(monkeypatch, tmp_path, inputs: list[str]) -> int:
    class TtyStdin:
        def isatty(self) -> bool:
            return True

    iterator = iter(inputs)
    monkeypatch.setattr("sys.stdin", TtyStdin())
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))
    return aigol_cli.main(
        [
            "next",
            "--session-id",
            SESSION_ID,
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )


def test_project_workspace_records_reusable_goal_knowledge(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        [
            "I want AiGOL Next to support GitHub Actions.",
            "/send",
            "exit",
        ],
    )
    output = capsys.readouterr().out
    state_path = (
        tmp_path
        / "runtime"
        / SESSION_ID
        / "workspace_state"
        / "001_acli_next_workspace_state_recorded.json"
    )
    workspace_state = json.loads(state_path.read_text(encoding="utf-8"))
    knowledge_index = workspace_state["project_knowledge_index"]

    assert result == 0
    assert "contextual_task_mapping:" in output
    assert "classification: RELATES_TO_CERTIFIED_CAPABILITY" in output
    assert "reuse_recommended: True" in output
    assert "knowledge_reuse_count: 1" in output
    assert knowledge_index["knowledge_source"] == "deterministic_workspace_state"
    assert "github_actions" in knowledge_index["known_goal_targets"]
    assert knowledge_index["conversation_history_is_authority"] is False
    assert knowledge_index["acli_next_executes_recommendation"] is False


def test_contextual_mapping_reuses_workspace_for_existing_modified_extended_and_new_goals(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    _run_aigol_next(
        monkeypatch,
        tmp_path,
        [
            "I want AiGOL Next to support GitHub Actions.",
            "/send",
            "exit",
        ],
    )
    capsys.readouterr()

    result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        [
            "I want AiGOL Next to support GitHub Actions. It is already implemented.",
            "/send",
            "/cancel",
            "Let's improve GitHub Actions support.",
            "/send",
            "/cancel",
            "Continue GitHub Actions support.",
            "/send",
            "/cancel",
            "I want AiGOL Next to support release notes.",
            "/send",
            "exit",
        ],
    )
    output = capsys.readouterr().out

    assert result == 0
    assert "Persistent development workspace restored." in output
    assert "classification: ALREADY_SATISFIED" in output
    assert "duplicate_work_avoided: True" in output
    assert "classification: MODIFIES_EXISTING_CAPABILITY" in output
    assert "classification: EXTENDS_EXISTING_MILESTONE" in output
    assert "classification: NEW_GOVERNED_WORK" in output
    assert "implementation_history_matches: Add GitHub Actions support." in output
    assert "knowledge_reuse_count: 4" in output
    assert "runtime_bound_count: 0" in output
