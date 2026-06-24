"""Certification tests for the ACLI governed development execution bridge."""

from __future__ import annotations

import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.acli_human_friendly_explanation_runtime import (
    reconstruct_acli_human_friendly_explanation_replay,
)
from aigol.runtime.acli_governed_development_execution_bridge import (
    APPROVAL_REQUIRED,
    EXECUTION_COMPLETED,
)
from aigol.runtime.governed_development_workflow_runtime import GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED


CREATED_AT = "2026-06-23T00:00:00Z"
SESSION_ID = "SESSION-ACLI-GOVERNED-DEVELOPMENT-BRIDGE-000001"


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _conversation_args(tmp_path: Path, repo: Path):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            SESSION_ID,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(repo),
        ]
    )


def test_acli_governed_development_bridge_executes_after_explicit_approval(tmp_path) -> None:
    repo = _repo(tmp_path)
    output: list[str] = []

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(["Add replay validation", "APPROVE", "exit"]),
        output_func=output.append,
    )

    rendered = "\n".join(output)
    proposal_turn = result["turns"][0]
    execution_turn = result["turns"][1]

    assert result["failed_turns"] == 0
    assert result["execution_requested"] is True
    assert result["worker_invoked"] is True
    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert proposal_turn["repository_mutation_performed"] is False
    assert proposal_turn["worker_invoked"] is False
    assert proposal_turn["human_friendly_explanation_artifact_type"] == (
        "ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1"
    )
    assert proposal_turn["human_friendly_explanation_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert proposal_turn["human_friendly_explanation_visibility_only"] is True
    assert proposal_turn["human_friendly_explanation_authority_granted"] is False
    assert execution_turn["response_status"] == EXECUTION_COMPLETED
    assert execution_turn["approval_bypassed"] is False
    assert execution_turn["repository_mutation_performed"] is True
    assert execution_turn["validation_executed"] is True
    assert execution_turn["worker_invoked"] is True
    assert execution_turn["routing_visibility_status"] == "ROUTING_SELECTED"
    assert execution_turn["routing_visibility_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert execution_turn["universal_intake_source_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert "Governed Development Proposal" in rendered
    assert rendered.index("HUMAN-FRIENDLY EXPLANATION") < rendered.index("Governed Development Proposal")
    assert "WHAT I UNDERSTOOD" in rendered
    assert "WHAT WILL HAPPEN" in rendered
    assert "WHAT WILL NOT HAPPEN" in rendered
    assert "WHAT REQUIRES YOUR APPROVAL" in rendered
    assert "WHAT TO TYPE NEXT" in rendered
    assert "REPLAY VISIBILITY" in rendered
    assert "Type APPROVE to continue." in rendered
    assert "no worker will execute before approval" in rendered
    assert "next_action: APPROVE, REJECT, or REQUEST_MODIFICATION" in rendered
    assert "approval_boundary: explicit human APPROVE required before mutation" in rendered
    assert "Governed Development Execution" in rendered
    assert "ROUTING FAILED CLOSED" not in rendered
    assert "Stateful governed development approval decision detected" in rendered
    assert "approval_decision: APPROVED" in rendered
    assert "approval_hash: sha256:" in rendered
    assert "worker_protections_preserved: true" in rendered
    assert "validation_allowlists_preserved: true" in rendered
    assert "workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED" in rendered

    replay_root = Path(execution_turn["governed_development_replay_reference"])
    explanation_replay = reconstruct_acli_human_friendly_explanation_replay(
        proposal_turn["human_friendly_explanation_replay_reference"]
    )
    assert explanation_replay["workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert explanation_replay["visibility_only"] is True
    assert explanation_replay["authority_granted"] is False
    assert replay_root.exists()
    assert (replay_root / "008_governed_development_outcome_recorded.json").exists()
    assert any(repo.glob("docs/governance/ACLI_GOVERNED_DEVELOPMENT_*_V1.md"))
    assert any(repo.glob("aigol/runtime/acli_governed_development_*.py"))


def test_acli_governed_development_bridge_rejection_does_not_mutate(tmp_path) -> None:
    repo = _repo(tmp_path)

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(["Add replay validation", "REJECT", "exit"]),
        output_func=lambda _line: None,
    )

    proposal_turn = result["turns"][0]
    rejection_turn = result["turns"][1]

    assert result["failed_turns"] == 0
    assert result["execution_requested"] is False
    assert result["worker_invoked"] is False
    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert rejection_turn["response_status"] == "REJECTED"
    assert rejection_turn["repository_mutation_performed"] is False
    assert not any(repo.glob("docs/governance/ACLI_GOVERNED_DEVELOPMENT_*_V1.md"))
    assert not any(repo.glob("aigol/runtime/acli_governed_development_*.py"))


def test_acli_governed_development_bridge_pending_approval_exits_without_mutation(tmp_path) -> None:
    repo = _repo(tmp_path)

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(["Add replay validation", "exit"]),
        output_func=lambda _line: None,
    )

    proposal_turn = result["turns"][0]

    assert result["failed_turns"] == 0
    assert result["execution_requested"] is False
    assert result["worker_invoked"] is False
    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert proposal_turn["repository_mutation_performed"] is False
    assert not any(repo.glob("docs/governance/ACLI_GOVERNED_DEVELOPMENT_*_V1.md"))
    assert not any(repo.glob("aigol/runtime/acli_governed_development_*.py"))
