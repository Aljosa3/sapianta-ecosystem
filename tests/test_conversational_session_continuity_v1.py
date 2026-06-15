"""Session continuity tests for AIGOL_CONVERSATIONAL_SESSION_CONTINUITY_V1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "governance" / "AIGOL_CONVERSATIONAL_SESSION_CONTINUITY_V1.json"
CREATED_AT = "2026-06-15T00:00:00Z"
MESSAGE_1 = "Prepare the foundation for the first AI Decision Validator domain."
MESSAGE_2 = "I approve the proposal."
MESSAGE_3 = "Continue with the next governed step."


def _args(tmp_path: Path):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            "SESSION-CONVERSATIONAL-CONTINUITY-000001",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "continuity_runtime"),
            "--workspace",
            str(tmp_path),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _run_continuity_scenario(tmp_path: Path) -> dict[str, Any]:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=_input_sequence([MESSAGE_1, MESSAGE_2, MESSAGE_3, "exit"]),
        output_func=output.append,
    )
    result["captured_output"] = output
    return result


def test_conversational_acli_preserves_domain_proposal_session_continuity(tmp_path) -> None:
    result = _run_continuity_scenario(tmp_path)
    proposal_turn, approval_turn, continuation_turn = result["turns"]

    assert result["turn_count"] == 3
    assert result["failed_turns"] == 0

    assert proposal_turn["response_source"] == "DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME"
    assert proposal_turn["domain_proposal_status"] == "DOMAIN_PROPOSAL_CREATED"
    assert proposal_turn["workflow_status"]["workflow_state"] == "WAITING_FOR_APPROVAL"
    assert proposal_turn["proposed_domain"] == "AIDecisionValidator"
    assert proposal_turn["approval_required"] is True
    assert proposal_turn["domain_created"] is False
    assert proposal_turn["worker_invoked"] is False

    assert approval_turn["response_source"] == "DOMAIN_PROPOSAL_REVIEW_RUNTIME"
    assert approval_turn["domain_review_status"] == "APPROVED"
    assert approval_turn["domain_candidate_created"] is True
    assert approval_turn["replay_lineage_preserved"] is True
    assert approval_turn["canonical_chain_id"] == proposal_turn["canonical_chain_id"]
    assert approval_turn["approval_bypassed"] is False
    assert approval_turn["domain_created"] is False
    assert approval_turn["worker_invoked"] is False

    assert continuation_turn["response_source"] == "DOMAIN_CANDIDATE_CONTINUATION_BOUNDARY"
    assert continuation_turn["response_status"] == "WAITING_FOR_SEPARATE_DOMAIN_CREATION_AUTHORIZATION"
    assert continuation_turn["conversation_state_preserved"] is True
    assert continuation_turn["replay_lineage_preserved"] is True
    assert continuation_turn["authorization_boundary_preserved"] is True
    assert continuation_turn["canonical_chain_id"] == proposal_turn["canonical_chain_id"]
    assert continuation_turn["required_next_step"] == "SEPARATE_DOMAIN_CREATION_AUTHORIZATION"
    assert continuation_turn["approval_bypassed"] is False
    assert continuation_turn["domain_created"] is False
    assert continuation_turn["worker_invoked"] is False

    assert Path(proposal_turn["domain_proposal_replay_reference"]).exists()
    assert Path(approval_turn["domain_review_replay_reference"]).exists()
    assert Path(continuation_turn["replay_reference"]).exists()
    assert "Domain Candidate Continuation" in "\n".join(result["captured_output"])


def test_conversational_session_continuity_report_matches_runtime_evidence(tmp_path) -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    result = _run_continuity_scenario(tmp_path)
    proposal_turn, approval_turn, continuation_turn = result["turns"]

    assert report["artifact_type"] == "AIGOL_CONVERSATIONAL_SESSION_CONTINUITY_V1"
    assert report["status"] == "ACCEPTED"
    assert report["messages"] == [MESSAGE_1, MESSAGE_2, MESSAGE_3]
    assert report["manual_routing_used"] is False
    assert report["manual_artifact_lookup_used"] is False
    assert report["governance_bypass_used"] is False
    assert report["evidence_summary"]["proposal_status"] == proposal_turn["domain_proposal_status"]
    assert report["evidence_summary"]["approval_status"] == approval_turn["domain_review_status"]
    assert report["evidence_summary"]["continuation_status"] == continuation_turn["response_status"]
    assert report["evidence_summary"]["canonical_chain_id_preserved"] is True
    assert report["final_fields"] == {
        "SESSION_CONTINUITY_PRESERVED": "YES",
        "REPLAY_LINEAGE_CONTINUOUS": "YES",
        "APPROVAL_CONTINUITY_WORKING": "YES",
        "CONVERSATIONAL_WORKFLOW_CONTINUITY": "YES",
    }
