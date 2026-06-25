"""Certification tests for the ACLI governed development execution bridge."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import aigol.cli.aigol_cli as aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.acli_human_friendly_explanation_runtime import (
    reconstruct_acli_human_friendly_explanation_replay,
)
from aigol.runtime.acli_llm_assisted_explanation_runtime import (
    DETERMINISTIC_FALLBACK_USED,
    PROVIDER_EXPLANATION_USED,
    reconstruct_acli_llm_assisted_explanation_replay,
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
    assert "EXPLANATION TRANSPARENCY" in rendered
    assert "Authoritative State" in rendered
    assert "AiGOL Governance" in rendered
    assert "Explanation Confidence" in rendered
    assert "Governance Only" in rendered
    assert "Type APPROVE to continue." in rendered
    assert "no worker will execute before approval" in rendered
    assert "Operator Summary" in rendered
    assert "Diagnostics" in rendered
    assert "Proposal ready for review." in rendered
    assert "Nothing has changed yet." in rendered
    assert "No worker has run yet." in rendered
    assert "Validation has not run yet because execution has not been approved." in rendered
    assert "next_action: APPROVE, REJECT, or REQUEST_MODIFICATION" in rendered
    assert "approval_boundary: explicit human APPROVE required before mutation" in rendered
    assert "Governed Development Execution" in rendered
    assert "Approved and executed." in rendered
    assert "What happened:" in rendered
    assert "- validation ran successfully" in rendered
    assert "Safety checks:" in rendered
    assert "- approval was not bypassed" in rendered
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


def test_acli_governed_development_bare_approval_after_session_resume_shows_summary_only(tmp_path) -> None:
    repo = _repo(tmp_path)
    first_output: list[str] = []
    second_output: list[str] = []
    args = _conversation_args(tmp_path, repo)

    first = run_interactive_conversation(
        args,
        input_func=_input_sequence(["Add replay validation", "exit"]),
        output_func=first_output.append,
    )
    second = run_interactive_conversation(
        args,
        input_func=_input_sequence(["APPROVE", "exit"]),
        output_func=second_output.append,
    )

    proposal_turn = first["turns"][0]
    resume_turn = second["turns"][0]
    rendered = "\n".join(second_output)

    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert proposal_turn["repository_mutation_performed"] is False
    assert resume_turn["routing_visibility_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert resume_turn["response_status"] == APPROVAL_REQUIRED
    assert resume_turn["approval_bypassed"] is False
    assert resume_turn["repository_mutation_performed"] is False
    assert resume_turn["validation_executed"] is False
    assert resume_turn["worker_invoked"] is False
    assert "Stateful governed development approval decision detected" in rendered
    assert "Restored Governed Development Proposal" in rendered
    assert "bare APPROVE will not execute a restored proposal" in rendered
    assert "APPROVE THIS PROPOSAL" in rendered
    assert "Governed Development Execution" not in rendered
    assert "HUMAN INTENT CLARIFICATION REQUIRED" not in rendered

    restore_replay = (
        tmp_path
        / "runtime"
        / SESSION_ID
        / "TURN-000002"
        / "acli_governed_development_pending_proposal_restore"
        / "000_acli_governed_development_pending_proposal_restored.json"
    )
    assert restore_replay.exists()
    restore_artifact = json.loads(restore_replay.read_text())["artifact"]
    assert restore_artifact["restore_status"] == "PENDING_PROPOSAL_RESTORED"
    assert restore_artifact["approval_granted"] is False
    assert restore_artifact["execution_authorized"] is False


def test_acli_governed_development_explicit_resume_approval_executes(tmp_path) -> None:
    repo = _repo(tmp_path)
    args = _conversation_args(tmp_path, repo)

    first = run_interactive_conversation(
        args,
        input_func=_input_sequence(["Add replay validation", "exit"]),
        output_func=lambda _line: None,
    )
    assert first["turns"][0]["response_status"] == APPROVAL_REQUIRED

    output: list[str] = []
    second = run_interactive_conversation(
        args,
        input_func=_input_sequence(["APPROVE THIS PROPOSAL", "exit"]),
        output_func=output.append,
    )
    rendered = "\n".join(output)
    execution_turn = second["turns"][0]

    assert execution_turn["routing_visibility_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert execution_turn["response_status"] == EXECUTION_COMPLETED
    assert execution_turn["approval_bypassed"] is False
    assert execution_turn["repository_mutation_performed"] is True
    assert execution_turn["validation_executed"] is True
    assert execution_turn["worker_invoked"] is True
    assert "Governed Development Execution" in rendered
    assert "HUMAN INTENT CLARIFICATION REQUIRED" not in rendered


def test_acli_governed_development_artifact_resume_approval_executes(tmp_path) -> None:
    repo = _repo(tmp_path)
    args = _conversation_args(tmp_path, repo)

    first = run_interactive_conversation(
        args,
        input_func=_input_sequence(
            [
                (
                    "Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator "
                    "practices for using ACLI as the primary development interface."
                ),
                "exit",
            ]
        ),
        output_func=lambda _line: None,
    )
    assert first["turns"][0]["response_status"] == APPROVAL_REQUIRED

    output: list[str] = []
    second = run_interactive_conversation(
        args,
        input_func=_input_sequence(["APPROVE ACLI_USAGE_GUIDELINES_V1", "exit"]),
        output_func=output.append,
    )
    execution_turn = second["turns"][0]

    assert execution_turn["routing_visibility_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert execution_turn["response_status"] == EXECUTION_COMPLETED
    assert execution_turn["approval_bypassed"] is False
    assert execution_turn["repository_mutation_performed"] is True
    assert execution_turn["validation_executed"] is True
    assert execution_turn["worker_invoked"] is True


def test_restored_governed_development_bare_approval_bypasses_clarification_without_execution(
    tmp_path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    args = _conversation_args(tmp_path, repo)

    first = run_interactive_conversation(
        args,
        input_func=_input_sequence(["Add replay validation", "exit"]),
        output_func=lambda _line: None,
    )
    assert first["turns"][0]["response_status"] == APPROVAL_REQUIRED

    monkeypatch.setattr(
        aigol_cli,
        "detect_active_clarification",
        lambda *, session_root: {
            "open_clarification_detected": True,
            "active_clarification_count": 1,
            "active_clarification": {
                "originating_workflow_id": "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION",
            },
        },
    )
    monkeypatch.setattr(
        aigol_cli,
        "should_bind_operator_reply_to_active_clarification",
        lambda *, session_root, human_prompt: {
            "should_bind_reply": True,
            "binding_decision_reason": "REPLY_MATCHES_ACTIVE_CLARIFICATION_SCOPE",
            "active_clarification": {
                "originating_workflow_id": "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION",
            },
        },
    )

    output: list[str] = []
    second = run_interactive_conversation(
        args,
        input_func=_input_sequence(["APPROVE", "exit"]),
        output_func=output.append,
    )
    rendered = "\n".join(output)
    resume_turn = second["turns"][0]

    assert resume_turn["routing_visibility_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert resume_turn["response_status"] == APPROVAL_REQUIRED
    assert resume_turn["repository_mutation_performed"] is False
    assert resume_turn["validation_executed"] is False
    assert resume_turn["worker_invoked"] is False
    assert resume_turn["conversational_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert "HUMAN INTENT CLARIFICATION REQUIRED" not in rendered
    assert "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION" not in rendered
    assert "Restored Governed Development Proposal" in rendered
    assert "Governed Development Execution" not in rendered


def test_same_session_governed_development_approval_wins_over_clarification_continuity(
    tmp_path, monkeypatch
) -> None:
    repo = _repo(tmp_path)
    calls = {"count": 0}

    def active_clarification(*, session_root):
        calls["count"] += 1
        if calls["count"] == 1:
            return {
                "open_clarification_detected": False,
                "active_clarification_count": 0,
                "active_clarification": None,
            }
        return {
            "open_clarification_detected": True,
            "active_clarification_count": 1,
            "active_clarification": {
                "originating_workflow_id": "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION",
            },
        }

    monkeypatch.setattr(aigol_cli, "detect_active_clarification", active_clarification)
    monkeypatch.setattr(
        aigol_cli,
        "should_bind_operator_reply_to_active_clarification",
        lambda *, session_root, human_prompt: {
            "should_bind_reply": True,
            "binding_decision_reason": "REPLY_MATCHES_ACTIVE_CLARIFICATION_SCOPE",
            "active_clarification": {
                "originating_workflow_id": "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION",
            },
        },
    )

    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(["Add replay validation", "APPROVE", "exit"]),
        output_func=output.append,
    )
    rendered = "\n".join(output)
    execution_turn = result["turns"][1]

    assert execution_turn["routing_visibility_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert execution_turn["response_status"] == EXECUTION_COMPLETED
    assert execution_turn["repository_mutation_performed"] is True
    assert execution_turn["validation_executed"] is True
    assert execution_turn["worker_invoked"] is True
    assert execution_turn["conversational_workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert "HUMAN INTENT CLARIFICATION REQUIRED" not in rendered
    assert "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION" not in rendered
    assert "Governed Development Execution" in rendered


def test_acli_governed_development_approval_without_pending_proposal_does_not_execute(tmp_path) -> None:
    repo = _repo(tmp_path)
    output: list[str] = []

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(["APPROVE", "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]
    rendered = "\n".join(output)

    assert turn["response_status"] == "CLARIFICATION_REQUIRED"
    assert turn["conversational_workflow_id"] == "HUMAN_INTENT_CLARIFICATION_INTAKE"
    assert turn.get("repository_mutation_performed") is not True
    assert turn["worker_invoked"] is False
    assert "HUMAN INTENT CLARIFICATION REQUIRED" in rendered


def test_acli_governed_development_invalid_pending_replay_fails_closed(tmp_path) -> None:
    repo = _repo(tmp_path)
    args = _conversation_args(tmp_path, repo)

    first = run_interactive_conversation(
        args,
        input_func=_input_sequence(["Add replay validation", "exit"]),
        output_func=lambda _line: None,
    )
    assert first["turns"][0]["response_status"] == APPROVAL_REQUIRED

    proposal_replay = (
        tmp_path
        / "runtime"
        / SESSION_ID
        / "TURN-000001"
        / "acli_governed_development_execution_bridge"
        / "000_acli_governed_development_proposal_recorded.json"
    )
    wrapper = json.loads(proposal_replay.read_text())
    wrapper["artifact"]["artifact_hash"] = "sha256:tampered"
    proposal_replay.write_text(json.dumps(wrapper, indent=2, sort_keys=True))

    output: list[str] = []
    second = run_interactive_conversation(
        args,
        input_func=_input_sequence(["APPROVE", "exit"]),
        output_func=output.append,
    )
    rendered = "\n".join(output)

    assert second["failed_turns"] == 1
    assert "FAILED_CLOSED" in rendered
    assert "hash mismatch" in rendered
    assert not any(repo.glob("aigol/runtime/acli_governed_development_*.py"))


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
    assert "Proposal ready for review." in rendered
    assert "Requested artifact: ACLI_USAGE_GUIDELINES_V1" in rendered
    assert "Selected artifact: ACLI_USAGE_GUIDELINES_V1" in rendered
    assert "File ACLI plans to create: docs/governance/ACLI_USAGE_GUIDELINES_V1.md" in rendered
    assert "Target path mode: REQUESTED_IDENTIFIER" in rendered
    assert "Title: ACLI_USAGE_GUIDELINES_V1" in rendered
    assert "Purpose: Document recommended operator practices" in rendered
    assert "approval_boundary: explicit human APPROVE required before mutation" in rendered
    assert "Governed Development Execution" in rendered
    assert "Approved and executed." in rendered
    assert "workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED" in rendered

    explanation_replay = reconstruct_acli_human_friendly_explanation_replay(
        proposal_turn["human_friendly_explanation_replay_reference"]
    )
    assert explanation_replay["workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert explanation_replay["visibility_only"] is True
    assert explanation_replay["authority_granted"] is False
    assert (repo / "docs/governance/ACLI_USAGE_GUIDELINES_V1.md").exists()
    assert not any(repo.glob("docs/governance/ACLI_GOVERNED_DEVELOPMENT_*_V1.md"))
    assert any(repo.glob("aigol/runtime/acli_governed_development_*.py"))

    proposal_replay = json.loads(
        (Path(proposal_turn["replay_reference"]) / "000_acli_governed_development_proposal_recorded.json").read_text()
    )
    proposal_artifact = proposal_replay["artifact"]
    naming_decision = proposal_artifact["proposal_naming_decision"]
    preview_artifact = proposal_artifact["proposal_preview_artifact"]
    proposal = proposal_artifact["proposal_artifact"]
    assert naming_decision["requested_artifact_identifier"] == "ACLI_USAGE_GUIDELINES_V1"
    assert naming_decision["selected_artifact_identifier"] == "ACLI_USAGE_GUIDELINES_V1"
    assert naming_decision["selected_target_path"] == "docs/governance/ACLI_USAGE_GUIDELINES_V1.md"
    assert naming_decision["target_path_mode"] == "REQUESTED_IDENTIFIER"
    assert naming_decision["collision_status"] == "NO_COLLISION"
    assert preview_artifact["selected_artifact_identifier"] == "ACLI_USAGE_GUIDELINES_V1"
    assert preview_artifact["selected_target_path"] == "docs/governance/ACLI_USAGE_GUIDELINES_V1.md"
    assert proposal["governance_artifact_proposal"]["target_path"] == (
        "docs/governance/ACLI_USAGE_GUIDELINES_V1.md"
    )
    assert proposal["governance_artifact_proposal"]["artifact_title"] == "ACLI_USAGE_GUIDELINES_V1"


def test_governance_artifact_requested_name_collision_fails_closed(tmp_path) -> None:
    repo = _repo(tmp_path)
    target = repo / "docs/governance/ACLI_USAGE_GUIDELINES_V1.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Existing\n", encoding="utf-8")
    output: list[str] = []

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(
            [
                (
                    "Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator "
                    "practices for using ACLI as the primary development interface."
                ),
                "exit",
            ]
        ),
        output_func=output.append,
    )

    rendered = "\n".join(output)
    proposal_turn = result["turns"][0]

    assert result["failed_turns"] == 1
    assert result["execution_requested"] is False
    assert result["worker_invoked"] is False
    assert proposal_turn["response_status"] == "FAILED_CLOSED"
    assert proposal_turn["repository_mutation_performed"] is False
    assert "target path collision at docs/governance/ACLI_USAGE_GUIDELINES_V1.md" in rendered
    assert target.read_text(encoding="utf-8") == "# Existing\n"
    assert not any(repo.glob("aigol/runtime/acli_governed_development_*.py"))


def test_acli_governed_development_bridge_rejection_does_not_mutate(tmp_path) -> None:
    repo = _repo(tmp_path)
    output: list[str] = []

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(["Add replay validation", "REJECT", "exit"]),
        output_func=output.append,
    )

    proposal_turn = result["turns"][0]
    rejection_turn = result["turns"][1]
    rejection_rendered = output[1]

    assert result["failed_turns"] == 0
    assert result["execution_requested"] is False
    assert result["worker_invoked"] is False
    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert rejection_turn["response_status"] == "REJECTED"
    assert rejection_turn["repository_mutation_performed"] is False
    assert "Governed Development Rejected" in rejection_rendered
    assert "Operator Summary" in rejection_rendered
    assert "Diagnostics" in rejection_rendered
    assert "Proposal rejected." in rejection_rendered
    assert "The current proposal is canceled." in rejection_rendered
    assert "Nothing was approved." in rejection_rendered
    assert "No repository changes were made." in rejection_rendered
    assert "No worker ran." in rejection_rendered
    assert "Replay evidence records the rejection." in rejection_rendered
    assert "bridge_status: REJECTED" in rejection_rendered
    assert "approval_hash:" not in rejection_rendered
    assert "failure_reason:" not in rejection_rendered
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
    assert "Operator Summary" in modification_rendered
    assert "Diagnostics" in modification_rendered
    assert "Modification requested." in modification_rendered
    assert "The current proposal has been stopped." in modification_rendered
    assert "Nothing was approved." in modification_rendered
    assert "No repository changes were made." in modification_rendered
    assert "No worker ran." in modification_rendered
    assert "Please describe what you want changed in the proposal." in modification_rendered
    assert "bridge_status: MODIFICATION_REQUESTED" in modification_rendered
    assert "workflow_state: WAITING_FOR_OPERATOR_REVISION" in modification_rendered
    assert "approval_granted: false" in modification_rendered
    assert "approval_hash:" not in modification_rendered
    assert "execution_authorized: false" in modification_rendered
    assert "mutation_performed: false" in modification_rendered
    assert "worker_invoked: false" in modification_rendered
    assert "validation_executed: false" in modification_rendered
    assert "next_action: Describe the required proposal change." in modification_rendered
    assert "failure_reason:" not in modification_rendered
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


def test_live_acli_uses_optional_llm_assisted_explanation_provider(tmp_path) -> None:
    repo = _repo(tmp_path)
    output: list[str] = []

    def provider(request: dict) -> dict:
        state = request["authoritative_state"]
        return {
            "explanation_text": (
                "Provider explanation: ACLI_USAGE_GUIDELINES_V1 will wait for approval before mutation."
            ),
            "preserved_artifact_identifiers": list(state["artifact_identifiers"]),
            "preserved_target_paths": list(state["target_paths"]),
            "preserved_approval_state": state["approval_state"],
            "preserved_replay_references": list(state["replay_references"]),
            "advisory_only": True,
            "authority_granted": False,
        }

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(
            [
                (
                    "Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended "
                    "operator practices for using ACLI as the primary development interface."
                ),
                "exit",
            ]
        ),
        output_func=output.append,
        llm_explanation_provider=provider,
    )

    rendered = "\n".join(output)
    proposal_turn = result["turns"][0]

    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert proposal_turn["repository_mutation_performed"] is False
    assert proposal_turn["worker_invoked"] is False
    assert proposal_turn["human_friendly_explanation_artifact_type"] == (
        "ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1"
    )
    assert proposal_turn["llm_assisted_explanation_artifact_type"] == (
        "ACLI_LLM_ASSISTED_EXPLANATION_ARTIFACT_V1"
    )
    assert proposal_turn["llm_assisted_explanation_status"] == PROVIDER_EXPLANATION_USED
    assert proposal_turn["llm_assisted_explanation_provider_invoked"] is True
    assert proposal_turn["llm_assisted_explanation_provider_used"] is True
    assert proposal_turn["llm_assisted_explanation_advisory_only"] is True
    assert proposal_turn["llm_assisted_explanation_authority_granted"] is False
    assert "HUMAN-FRIENDLY EXPLANATION" in rendered
    assert "PROVIDER-ASSISTED EXPLANATION" in rendered
    assert "Provider explanation: ACLI_USAGE_GUIDELINES_V1" in rendered
    assert "EXPLANATION TRANSPARENCY" in rendered
    assert "Provider Name" in rendered
    assert "Explanation Confidence" in rendered
    assert "High" in rendered
    assert "Explanation Completeness" in rendered
    assert "Complete" in rendered
    assert "Governed Development Proposal" in rendered
    assert rendered.index("HUMAN-FRIENDLY EXPLANATION") < rendered.index("PROVIDER-ASSISTED EXPLANATION")
    assert rendered.index("PROVIDER-ASSISTED EXPLANATION") < rendered.index("Governed Development Proposal")

    replay = reconstruct_acli_llm_assisted_explanation_replay(
        proposal_turn["llm_assisted_explanation_replay_reference"]
    )
    state = replay["authoritative_state"]
    assert replay["explanation_status"] == PROVIDER_EXPLANATION_USED
    assert replay["provider_explanation_used"] is True
    assert replay["authority_granted"] is False
    assert replay["explanation_transparency_artifact"]["provider_status"] == PROVIDER_EXPLANATION_USED
    assert replay["rendered_operator_view_hash"].startswith("sha256:")
    assert state["artifact_identifiers"] == ["ACLI_USAGE_GUIDELINES_V1"]
    assert "docs/governance/ACLI_USAGE_GUIDELINES_V1.md" in state["target_paths"]
    assert state["approval_state"] == APPROVAL_REQUIRED
    assert state["proposal_hash"].startswith("sha256:")


def test_live_acli_llm_assisted_explanation_provider_failure_falls_back(tmp_path) -> None:
    repo = _repo(tmp_path)
    output: list[str] = []

    def unavailable(_request: dict) -> dict:
        raise RuntimeError("provider unavailable")

    result = run_interactive_conversation(
        _conversation_args(tmp_path, repo),
        input_func=_input_sequence(["Add replay validation", "exit"]),
        output_func=output.append,
        llm_explanation_provider=unavailable,
    )

    rendered = "\n".join(output)
    proposal_turn = result["turns"][0]

    assert proposal_turn["response_status"] == APPROVAL_REQUIRED
    assert proposal_turn["repository_mutation_performed"] is False
    assert proposal_turn["worker_invoked"] is False
    assert proposal_turn["llm_assisted_explanation_status"] == DETERMINISTIC_FALLBACK_USED
    assert proposal_turn["llm_assisted_explanation_provider_invoked"] is True
    assert proposal_turn["llm_assisted_explanation_provider_used"] is False
    assert proposal_turn["llm_assisted_explanation_deterministic_fallback_used"] is True
    assert proposal_turn["llm_assisted_explanation_authority_granted"] is False
    assert "HUMAN-FRIENDLY EXPLANATION" in rendered
    assert "PROVIDER-ASSISTED EXPLANATION" not in rendered
    assert "Governed Development Proposal" in rendered

    replay = reconstruct_acli_llm_assisted_explanation_replay(
        proposal_turn["llm_assisted_explanation_replay_reference"]
    )
    assert replay["explanation_status"] == DETERMINISTIC_FALLBACK_USED
    assert replay["deterministic_fallback_used"] is True
    assert replay["authority_granted"] is False
    assert replay["authoritative_state"]["approval_state"] == APPROVAL_REQUIRED
