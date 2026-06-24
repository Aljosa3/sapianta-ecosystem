"""Certification tests for the ACLI governed development execution bridge."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.acli_human_friendly_explanation_runtime import (
    reconstruct_acli_human_friendly_explanation_replay,
)
from aigol.runtime.acli_governed_development_execution_bridge import (
    APPROVAL_REQUIRED,
    EXECUTION_COMPLETED,
    MODIFICATION_REQUESTED,
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


def test_governance_artifact_operator_prompt_uses_governed_development_bridge(tmp_path) -> None:
    repo = _repo(tmp_path)
    output: list[str] = []

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(
            [
                (
                    "Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator "
                    "practices for using ACLI as the primary development interface."
                ),
                "APPROVE",
                "exit",
            ]
        ),
        output_func=output.append,
    )

    rendered = "\n".join(output)
    proposal_turn = result["turns"][0]
    execution_turn = result["turns"][1]

    assert result["failed_turns"] == 0
    assert proposal_turn["routing_visibility_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert proposal_turn["repository_mutation_performed"] is False
    assert proposal_turn["human_friendly_explanation_artifact_type"] == (
        "ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1"
    )
    assert execution_turn["response_status"] == EXECUTION_COMPLETED
    assert execution_turn["repository_mutation_performed"] is True
    assert execution_turn["validation_executed"] is True
    assert "unsupported conversational workflow selection: GOVERNANCE_ARTIFACT_CREATION" not in rendered
    assert "workflow: GOVERNED_DEVELOPMENT_WORKFLOW" in rendered
    assert "HUMAN-FRIENDLY EXPLANATION" in rendered
    assert "WHAT I UNDERSTOOD" in rendered
    assert "Governed Development Proposal" in rendered
    assert "approval_boundary: explicit human APPROVE required before mutation" in rendered
    assert "Governed Development Execution" in rendered
    assert "workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED" in rendered

    explanation_replay = reconstruct_acli_human_friendly_explanation_replay(
        proposal_turn["human_friendly_explanation_replay_reference"]
    )
    assert explanation_replay["workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert explanation_replay["visibility_only"] is True
    assert explanation_replay["authority_granted"] is False
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


def test_acli_governed_development_bridge_request_modification_waits_for_revision(tmp_path) -> None:
    repo = _repo(tmp_path)
    output: list[str] = []

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(["Add replay validation", "REQUEST_MODIFICATION", "exit"]),
        output_func=output.append,
    )

    proposal_turn = result["turns"][0]
    modification_turn = result["turns"][1]
    modification_rendered = output[1]

    assert result["failed_turns"] == 0
    assert result["execution_requested"] is False
    assert result["worker_invoked"] is False
    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert modification_turn["response_status"] == MODIFICATION_REQUESTED
    assert modification_turn["workflow_status"]["workflow_state"] == "WAITING_FOR_OPERATOR"
    assert modification_turn["workflow_status"]["current_lifecycle_stage"] == "MODIFICATION_REQUESTED"
    assert modification_turn["workflow_status"]["required_input"] == ["proposal revision description"]
    assert modification_turn["authorization_created"] is False
    assert modification_turn["approval_required"] is False
    assert modification_turn["execution_requested"] is False
    assert modification_turn["repository_mutation_performed"] is False
    assert modification_turn["worker_invoked"] is False
    assert modification_turn["validation_executed"] is False
    assert "Governed Development Modification Requested" in modification_rendered
    assert "bridge_status: MODIFICATION_REQUESTED" in modification_rendered
    assert "workflow_state: WAITING_FOR_OPERATOR_REVISION" in modification_rendered
    assert "approval_granted: false" in modification_rendered
    assert "approval_hash: " in modification_rendered
    assert "execution_authorized: false" in modification_rendered
    assert "mutation_performed: false" in modification_rendered
    assert "worker_invoked: false" in modification_rendered
    assert "validation_executed: false" in modification_rendered
    assert "next_action: Describe the required proposal change." in modification_rendered
    assert "Current Lifecycle Stage: EXECUTION_AUTHORIZED" not in modification_rendered
    assert "Create worker request" not in modification_rendered
    assert not any(repo.glob("docs/governance/ACLI_GOVERNED_DEVELOPMENT_*_V1.md"))
    assert not any(repo.glob("aigol/runtime/acli_governed_development_*.py"))

    replay_root = Path(modification_turn["replay_reference"])
    execution_replay = json.loads(
        (replay_root / "001_acli_governed_development_execution_recorded.json").read_text()
    )
    execution_artifact = execution_replay["artifact"]
    assert execution_artifact["bridge_status"] == MODIFICATION_REQUESTED
    assert execution_artifact["approval_granted"] is False
    assert execution_artifact["approval_hash"] is None
    assert execution_artifact["execution_authorized"] is False
    assert execution_artifact["mutation_performed"] is False


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
