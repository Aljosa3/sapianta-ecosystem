"""Dogfood tests for AIGOL_CONVERSATIONAL_ACLI_DOGFOOD_V1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "governance" / "AIGOL_CONVERSATIONAL_ACLI_DOGFOOD_V1.json"
CREATED_AT = "2026-06-15T00:00:00Z"
DOGFOOD_PROMPT = (
    "Prepare the foundation for the first AI Decision Validator domain, "
    "but do not implement production execution yet."
)


def _args(tmp_path: Path):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            "SESSION-CONVERSATIONAL-ACLI-DOGFOOD-000001",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "dogfood_runtime"),
            "--workspace",
            str(tmp_path),
            "--auto-continue",
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _run_dogfood_prompt(tmp_path: Path) -> dict[str, Any]:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=_input_sequence([DOGFOOD_PROMPT, "exit"]),
        output_func=output.append,
    )
    result["captured_output"] = output
    return result


def test_conversational_acli_dogfood_routes_product_domain_foundation(tmp_path) -> None:
    result = _run_dogfood_prompt(tmp_path)
    turn = result["turns"][0]
    workflow = turn["workflow_status"]

    assert result["turn_count"] == 1
    assert result["failed_turns"] == 0
    assert result["auto_continue_stop_reason"] == "WAITING_FOR_APPROVAL"
    assert turn["routing_visibility_workflow_id"] == "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
    assert turn["response_source"] == "DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME"
    assert turn["universal_intake_classification"] == "DOMAIN_INTAKE"
    assert turn["domain_proposal_status"] == "DOMAIN_PROPOSAL_CREATED"
    assert turn["proposed_domain"] == "AIDecisionValidator"
    assert turn["approval_required"] is True
    assert turn["approval_bypassed"] is False
    assert turn["authorization_created"] is False
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert turn["domain_created"] is False
    assert workflow["workflow_state"] == "WAITING_FOR_APPROVAL"
    assert workflow["current_lifecycle_stage"] == "DOMAIN_PROPOSAL_CREATED"
    assert Path(turn["conversational_cli_routing_replay_reference"]).exists()
    assert Path(turn["universal_intake_replay_reference"]).exists()
    assert Path(turn["domain_proposal_replay_reference"]).exists()
    assert "proposed_domain: AIDecisionValidator" in "\n".join(result["captured_output"])


def test_conversational_acli_dogfood_report_matches_runtime_evidence(tmp_path) -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    result = _run_dogfood_prompt(tmp_path)
    turn = result["turns"][0]

    assert report["artifact_type"] == "AIGOL_CONVERSATIONAL_ACLI_DOGFOOD_V1"
    assert report["status"] == "ACCEPTED"
    assert report["dogfood_prompt_used"] == DOGFOOD_PROMPT
    assert report["manual_routing_used"] is False
    assert report["manual_artifact_injection_used"] is False
    assert report["manual_downstream_runtime_invocation_used"] is False
    assert report["authorization_boundary_preserved"] is True
    assert report["replay_evidence_created"] is True
    assert report["evidence_summary"]["domain_proposal_status"] == turn["domain_proposal_status"]
    assert report["evidence_summary"]["proposed_domain"] == turn["proposed_domain"]
    assert report["evidence_summary"]["worker_invoked"] == turn["worker_invoked"]
    assert report["final_fields"] == {
        "DOGFOOD_PROMPT_USED": DOGFOOD_PROMPT,
        "ACLI_ROUTE_SELECTED": "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION -> DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME",
        "FINAL_TERMINAL_ARTIFACT": "DOMAIN_PROPOSAL_CREATED / WAITING_FOR_APPROVAL",
        "MANUAL_ROUTING_USED": "NO",
        "AUTHORIZATION_BOUNDARY_PRESERVED": "YES",
        "REPLAY_EVIDENCE_CREATED": "YES",
        "DOGFOOD_SUCCESSFUL": "YES",
    }
