"""Tests for AIGOL_RECOMMENDATION_APPROVAL_AND_FOLLOWUP_RUNTIME_V1."""

from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.operator_decision_support_runtime import run_operator_decision_support
from aigol.runtime.recommendation_approval_followup_runtime import (
    APPROVAL_RECORDED,
    APPROVAL_REQUIRED,
    APPROVE,
    CONTINUITY_RECORDED,
    FOLLOWUP_CANDIDATE_GENERATED,
    PREPARE_IMPLEMENTATION_CANDIDATE,
    PREPARE_PROPOSAL,
    RECOMMENDATION_APPROVAL_ARTIFACT_V1,
    RECOMMENDATION_CONTINUITY_ARTIFACT_V1,
    RECOMMENDATION_FOLLOWUP_ARTIFACT_V1,
    create_recommendation_continuity,
    create_recommendation_followup,
    is_recommendation_approval_prompt,
    is_recommendation_followup_prompt,
    reconstruct_recommendation_approval_replay,
    reconstruct_recommendation_continuity_replay,
    reconstruct_recommendation_followup_replay,
    record_recommendation_approval,
)
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-05T00:00:00Z"
SESSION_ID = "SESSION-RECOMMENDATION-CONTINUITY-000001"


def _recommendation(tmp_path):
    capture = run_operator_decision_support(
        recommendation_id="RECOMMENDATION-1",
        prompt_id=f"{SESSION_ID}:TURN-000001",
        human_prompt="I want to create the first real AiGOL product domain.",
        canonical_chain_id=f"{SESSION_ID}:TURN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "decision_support",
    )
    return capture["operator_decision_support_artifact"]


def _continuity(tmp_path):
    return create_recommendation_continuity(
        continuity_id="CONTINUITY-1",
        recommendation_artifact=_recommendation(tmp_path),
        conversation_reference=f"{SESSION_ID}:TURN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuity",
    )


def _approval(tmp_path):
    continuity = _continuity(tmp_path)
    return record_recommendation_approval(
        approval_id="APPROVAL-1",
        recommendation_continuity_artifact=continuity["recommendation_continuity_artifact"],
        operator_decision=APPROVE,
        approval_timestamp=CREATED_AT,
        replay_dir=tmp_path / "approval",
    )


def _canonical_semantic_lineage() -> dict:
    return {
        "canonical_semantic_artifact_reference": "CSA-COMMAND-BOUNDARY-000001",
        "canonical_semantic_artifact_hash": "sha256:command-boundary-csa-000001",
        "semantic_routing_source": "CANONICAL_SEMANTIC_ARTIFACT",
        "migration_batch_id": "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_09",
    }


def _conversation_args(tmp_path):
    (tmp_path / "governance").mkdir(exist_ok=True)
    (tmp_path / "aigol" / "runtime").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            SESSION_ID,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
            "--workspace",
            str(tmp_path),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def test_recommendation_continuity_records_followup_candidates(tmp_path) -> None:
    capture = _continuity(tmp_path)
    replay = reconstruct_recommendation_continuity_replay(tmp_path / "continuity")
    artifact = capture["recommendation_continuity_artifact"]

    assert artifact["artifact_type"] == RECOMMENDATION_CONTINUITY_ARTIFACT_V1
    assert artifact["continuity_status"] == CONTINUITY_RECORDED
    assert artifact["approval_required"] is True
    assert artifact["approval_status"] == APPROVAL_REQUIRED
    assert artifact["recommended"] == "SAPIANTA_AI_PR_GATE"
    assert "Prepare Product Domain Proposal" in artifact["followup_candidates"]
    assert replay["continuity_status"] == CONTINUITY_RECORDED
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_requested"] is False
    assert replay["domain_created"] is False


def test_explicit_human_approval_records_approval_artifact(tmp_path) -> None:
    continuity = _continuity(tmp_path)
    capture = record_recommendation_approval(
        approval_id="APPROVAL-1",
        recommendation_continuity_artifact=continuity["recommendation_continuity_artifact"],
        operator_decision=APPROVE,
        approval_timestamp=CREATED_AT,
        replay_dir=tmp_path / "approval",
    )
    replay = reconstruct_recommendation_approval_replay(tmp_path / "approval")
    artifact = capture["recommendation_approval_artifact"]

    assert artifact["artifact_type"] == RECOMMENDATION_APPROVAL_ARTIFACT_V1
    assert artifact["operator_decision"] == APPROVE
    assert artifact["approval_status"] == APPROVAL_RECORDED
    assert artifact["approval_hash"]
    assert artifact["recommended"] == "SAPIANTA_AI_PR_GATE"
    assert "Prepare Product Domain Proposal" in artifact["available_next_actions"]
    assert replay["approval_status"] == APPROVAL_RECORDED
    assert replay["execution_requested"] is False
    assert replay["implementation_authorized"] is False
    assert replay["approval_bypassed"] is False


def test_recommendation_approval_certifies_exact_command_boundary(tmp_path) -> None:
    continuity = _continuity(tmp_path)
    capture = record_recommendation_approval(
        approval_id="APPROVAL-G2-10-EXACT",
        recommendation_continuity_artifact=continuity["recommendation_continuity_artifact"],
        operator_decision=APPROVE,
        approval_timestamp=CREATED_AT,
        replay_dir=tmp_path / "approval_g2_10",
        canonical_semantic_lineage=_canonical_semantic_lineage(),
    )
    replay = reconstruct_recommendation_approval_replay(tmp_path / "approval_g2_10")
    artifact = capture["recommendation_approval_artifact"]
    boundary = artifact["command_boundary_comparison_artifact"]

    assert artifact["operator_decision"] == APPROVE
    assert artifact["command_boundary_source"] == "DETERMINISTIC_COMMAND_PARSER"
    assert artifact["command_boundary_parity_status"] == "COMMAND_PARSER_AUTHORITATIVE"
    assert artifact["canonical_semantic_artifact_hash"] == "sha256:command-boundary-csa-000001"
    assert boundary["command_parser_decision"]["parser_matched"] is True
    assert boundary["command_parser_decision"]["parser_authoritative"] is True
    assert boundary["csa_command_prose_interpretation"]["used"] is False
    assert boundary["semantic_parity_evidence"]["csa_requires_parser_non_match"] is True
    assert replay["command_boundary_comparison_hash"] == boundary["artifact_hash"]
    assert replay["execution_requested"] is False
    assert replay["worker_invoked"] is False


@pytest.mark.parametrize(
    ("prompt", "action"),
    [
        ("Prepare the first product domain proposal.", PREPARE_PROPOSAL),
        ("Prepare implementation candidate.", PREPARE_IMPLEMENTATION_CANDIDATE),
    ],
)
def test_approved_recommendation_generates_followup_candidates(tmp_path, prompt: str, action: str) -> None:
    continuity = _continuity(tmp_path)
    approval = record_recommendation_approval(
        approval_id="APPROVAL-1",
        recommendation_continuity_artifact=continuity["recommendation_continuity_artifact"],
        operator_decision=APPROVE,
        approval_timestamp=CREATED_AT,
        replay_dir=tmp_path / "approval",
    )
    capture = create_recommendation_followup(
        followup_id="FOLLOWUP-1",
        recommendation_continuity_artifact=continuity["recommendation_continuity_artifact"],
        recommendation_approval_artifact=approval["recommendation_approval_artifact"],
        human_prompt=prompt,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "followup",
    )
    replay = reconstruct_recommendation_followup_replay(tmp_path / "followup")
    artifact = capture["recommendation_followup_artifact"]

    assert artifact["artifact_type"] == RECOMMENDATION_FOLLOWUP_ARTIFACT_V1
    assert artifact["followup_action"] == action
    assert artifact["followup_status"] == FOLLOWUP_CANDIDATE_GENERATED
    assert artifact["candidate_status"] == FOLLOWUP_CANDIDATE_GENERATED
    assert artifact["candidate"]["candidate_only"] is True
    assert artifact["candidate"]["creates_domain"] is False
    assert artifact["candidate"]["authorizes_implementation"] is False
    assert replay["followup_status"] == FOLLOWUP_CANDIDATE_GENERATED
    assert replay["execution_requested"] is False
    assert replay["implementation_authorized"] is False
    assert replay["domain_created"] is False


def test_recommendation_followup_records_csa_only_after_parser_non_match(tmp_path) -> None:
    continuity = _continuity(tmp_path)
    approval = record_recommendation_approval(
        approval_id="APPROVAL-G2-10-NONMATCH",
        recommendation_continuity_artifact=continuity["recommendation_continuity_artifact"],
        operator_decision=APPROVE,
        approval_timestamp=CREATED_AT,
        replay_dir=tmp_path / "approval_nonmatch",
    )
    capture = create_recommendation_followup(
        followup_id="FOLLOWUP-G2-10-NONMATCH",
        recommendation_continuity_artifact=continuity["recommendation_continuity_artifact"],
        recommendation_approval_artifact=approval["recommendation_approval_artifact"],
        human_prompt="Please continue with the sensible next step.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "followup_nonmatch",
        canonical_semantic_lineage=_canonical_semantic_lineage(),
    )
    replay = reconstruct_recommendation_followup_replay(tmp_path / "followup_nonmatch")
    artifact = capture["recommendation_followup_artifact"]
    boundary = artifact["command_boundary_comparison_artifact"]

    assert capture["fail_closed"] is True
    assert artifact["command_boundary_source"] == "CANONICAL_SEMANTIC_ARTIFACT_AFTER_COMMAND_NON_MATCH"
    assert artifact["command_boundary_parity_status"] == "CSA_OBSERVATIONAL_AFTER_COMMAND_NON_MATCH"
    assert artifact["command_boundary_fallback_reason"] == "COMMAND_PARSER_NON_MATCH"
    assert artifact["canonical_semantic_artifact_hash"] == "sha256:command-boundary-csa-000001"
    assert boundary["command_parser_decision"]["parser_matched"] is False
    assert boundary["command_parser_decision"]["parser_authoritative"] is False
    assert boundary["csa_command_prose_interpretation"]["used"] is True
    assert boundary["semantic_parity_evidence"]["exact_command_authority_preserved"] is True
    assert replay["command_boundary_comparison_hash"] == boundary["artifact_hash"]
    assert replay["execution_requested"] is False
    assert replay["implementation_authorized"] is False


def test_followup_fails_closed_without_approval(tmp_path) -> None:
    continuity = _continuity(tmp_path)
    capture = create_recommendation_followup(
        followup_id="FOLLOWUP-1",
        recommendation_continuity_artifact=continuity["recommendation_continuity_artifact"],
        recommendation_approval_artifact={},
        human_prompt="Prepare the first product domain proposal.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "followup",
    )

    assert capture["fail_closed"] is True
    assert "invalid approval artifact" in capture["failure_reason"]


def test_recommendation_prompt_detection() -> None:
    assert is_recommendation_approval_prompt("I approve the recommendation.") is True
    assert is_recommendation_followup_prompt("Prepare the first product domain proposal.") is True
    assert is_recommendation_followup_prompt("Prepare implementation candidate.") is True
    assert is_recommendation_followup_prompt("Create a trading domain.") is False


def test_interactive_conversation_continues_recommendation_workflow(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                "I want to create the first real AiGOL product domain.",
                "I approve the recommendation.",
                "Prepare the first product domain proposal.",
                "Prepare implementation candidate.",
                "exit",
            ]
        ),
        output_func=output.append,
    )

    assert result["failed_turns"] == 0
    assert result["turns"][0]["recommendation"] == "SAPIANTA_AI_PR_GATE"
    assert result["turns"][0]["recommendation_continuity_status"] == CONTINUITY_RECORDED
    assert result["turns"][1]["operator_decision"] == APPROVE
    assert result["turns"][1]["approval_status"] == APPROVAL_RECORDED
    assert result["turns"][2]["followup_action"] == PREPARE_PROPOSAL
    assert result["turns"][2]["candidate_status"] == FOLLOWUP_CANDIDATE_GENERATED
    assert result["turns"][3]["followup_action"] == PREPARE_IMPLEMENTATION_CANDIDATE
    assert result["turns"][3]["candidate_status"] == FOLLOWUP_CANDIDATE_GENERATED
    assert result["turns"][3]["execution_requested"] is False
    assert result["turns"][3]["implementation_authorized"] is False
    assert "Recommendation Approval Recorded" in output[1]
    assert "Recommendation Follow-Up Candidate Generated" in output[2]


def test_resumed_interactive_conversation_recovers_recommendation_continuity(tmp_path) -> None:
    first_output: list[str] = []
    first = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(["I want to create the first real AiGOL product domain.", "exit"]),
        output_func=first_output.append,
    )
    second_output: list[str] = []
    second = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(["I approve the recommendation.", "Prepare implementation candidate.", "exit"]),
        output_func=second_output.append,
    )

    assert first["failed_turns"] == 0
    assert second["session_resumed"] is True
    assert second["failed_turns"] == 0
    assert second["turns"][0]["operator_decision"] == APPROVE
    assert second["turns"][1]["followup_action"] == PREPARE_IMPLEMENTATION_CANDIDATE
    assert second["turns"][1]["implementation_authorized"] is False
    assert "Recommendation Approval Recorded" in second_output[0]


def test_replay_tampering_is_detected(tmp_path) -> None:
    _approval(tmp_path)
    path = tmp_path / "approval" / "000_recommendation_approval_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["operator_decision"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_recommendation_approval_replay(tmp_path / "approval")
