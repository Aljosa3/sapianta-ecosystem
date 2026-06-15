"""Acceptance tests for AIGOL_FREEFORM_HUMAN_PROMPT_ACCEPTANCE_V1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter, openai_provider_metadata


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "governance" / "FREEFORM_HUMAN_PROMPT_ACCEPTANCE_REPORT_V1.json"
CREATED_AT = "2026-06-14T00:00:00Z"

PROMPT_CASES = [
    ("FREEFORM_DEVELOPMENT", "I need a simple calculator utility."),
    ("FREEFORM_DEVELOPMENT", "Create a small Python tool for parsing CSV files."),
    ("FREEFORM_DEVELOPMENT", "Build a basic validation script."),
    ("FREEFORM_COGNITION", "I need a better way to evaluate employees."),
    ("FREEFORM_COGNITION", "How should I improve our hiring process?"),
    ("FREEFORM_COGNITION", "What would be the best architecture for an AI compliance system?"),
    ("FREEFORM_APPROVAL", "Deploy a system that can modify production customer data."),
    ("FREEFORM_APPROVAL", "Execute changes that affect external users."),
    ("FREEFORM_APPROVAL", "Perform a production rollout."),
    ("FREEFORM_DOMAIN_CREATION", "We need a new HR management domain."),
    ("FREEFORM_DOMAIN_CREATION", "Create a domain for AI code auditing."),
    ("FREEFORM_DOMAIN_CREATION", "I want a domain that manages supplier evaluation."),
    ("FREEFORM_CLARIFICATION", "Help me improve the system."),
    ("FREEFORM_CLARIFICATION", "Build something useful for my company."),
    ("FREEFORM_CLARIFICATION", "Make the platform better."),
    ("FREEFORM_AMBIGUOUS_REQUEST", "I want an AI system for my business."),
    ("FREEFORM_AMBIGUOUS_REQUEST", "Help automate company operations."),
    ("FREEFORM_AMBIGUOUS_REQUEST", "Create an intelligent management solution."),
]

EXPECTED_FINAL_FIELDS = {
    "FREEFORM_DEVELOPMENT_ACCEPTED": "YES",
    "FREEFORM_COGNITION_ACCEPTED": "YES",
    "FREEFORM_APPROVAL_ACCEPTED": "YES",
    "FREEFORM_DOMAIN_ACCEPTED": "YES",
    "FREEFORM_CLARIFICATION_ACCEPTED": "YES",
    "FREEFORM_AMBIGUOUS_REQUEST_ACCEPTED": "YES",
    "FREEFORM_DEVELOPMENT_ROUTING_FIXED": "YES",
    "FREEFORM_COGNITION_ROUTING_FIXED": "YES",
    "FREEFORM_APPROVAL_ROUTING_FIXED": "YES",
    "FREEFORM_DOMAIN_ROUTING_FIXED": "YES",
    "FREEFORM_CLARIFICATION_ROUTING_FIXED": "YES",
    "FREEFORM_AMBIGUOUS_ROUTING_FIXED": "YES",
    "FIRST_FAILURE_STAGE": "NONE",
    "FREEFORM_NATURAL_LANGUAGE_OPERATIONAL": "YES",
    "ACLI_CONVERSATIONAL_READINESS": "YES",
    "AUTHORIZATION_BOUNDARY_PRESERVED": "YES",
    "FAIL_CLOSED_PRESERVED": "YES",
}


@dataclass
class FakeProviderAdapter:
    provider_id: str = "openai"
    provider_version: str = openai_provider_metadata().provider_version

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str):
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "proposal_summary": "Create bounded governed implementation evidence.",
                "proposed_outputs": ["governance/FREEFORM_ACCEPTANCE_EVIDENCE.md"],
                "constraints_acknowledged": [
                    "NO_DISPATCH",
                    "NO_INVOCATION",
                    "NO_EXECUTION",
                    "PROPOSAL_ONLY",
                ],
                "assumptions": ["Execution remains behind canonical authorization."],
                "known_gaps": ["Freeform acceptance only."],
            },
            timestamp=timestamp,
        )


def _args(tmp_path: Path, *, session_id: str):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "freeform_runtime"),
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


def _install_fake_providers(monkeypatch) -> None:
    def fake_ocs_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        return {
            "id": "resp-freeform-ocs-001",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "findings": ["Governed cognition evidence created."],
                                    "assumptions": ["No execution occurs before authorization."],
                                    "alternatives": [
                                        "Clarify",
                                        "Request approval",
                                        "Continue governance review",
                                    ],
                                    "risks": ["Execution remains gated."],
                                    "uncertainties": ["Freeform request may be underspecified."],
                                    "confidence": "MEDIUM",
                                },
                                sort_keys=True,
                            ),
                            "annotations": [],
                        }
                    ],
                }
            ],
        }

    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        return {
            "id": "resp-freeform-worker-001",
            "output_text": "Return bounded implementation result evidence.",
        }

    monkeypatch.setattr(aigol_cli, "_post_context_continuation_provider_adapter", lambda: FakeProviderAdapter())
    monkeypatch.setattr(
        aigol_cli,
        "_conversation_openai_provider_adapter",
        lambda: OpenAIProviderAdapter(api_key="test-openai-key", client=fake_ocs_client),
    )
    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)


def _run_prompt(tmp_path: Path, *, category: str, index: int, prompt: str) -> dict[str, Any]:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id=f"SESSION-FREEFORM-{category}-{index:02d}"),
        input_func=_input_sequence([prompt, "exit"]),
        output_func=output.append,
    )
    turns = result.get("turns") if isinstance(result.get("turns"), list) else []
    turn = turns[0] if turns else {}
    status = turn.get("workflow_status") if isinstance(turn.get("workflow_status"), dict) else {}
    return {
        "category": category,
        "prompt": prompt,
        "turn": turn,
        "workflow_stage": status.get("current_lifecycle_stage"),
        "workflow_state": status.get("workflow_state"),
        "classification": turn.get("routing_visibility_workflow_id") or turn.get("response_source"),
        "intake": turn.get("universal_intake_classification"),
        "worker_invoked": turn.get("worker_invoked") is True,
        "domain_created": turn.get("domain_created") is True,
        "approval_bypassed": turn.get("approval_bypassed") is True,
    }


def _execute_corpus(tmp_path: Path, monkeypatch) -> list[dict[str, Any]]:
    _install_fake_providers(monkeypatch)
    return [
        _run_prompt(tmp_path, category=category, index=index, prompt=prompt)
        for index, (category, prompt) in enumerate(PROMPT_CASES, start=1)
    ]


def _development_accepted(record: dict[str, Any]) -> bool:
    turn = record["turn"]
    return (
        record["classification"] == "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION"
        and turn.get("ppp_route_status") == "CONVERSATION_PPP_HANDOFF_CREATED"
        and turn.get("execution_authorization_status") == "EXECUTION_AUTHORIZED"
        and record["worker_invoked"] is True
        and turn.get("clarification_required") is not True
    )


def _cognition_accepted(record: dict[str, Any]) -> bool:
    return record["classification"] == "OCS_LLM_COGNITION" and record["worker_invoked"] is False


def _approval_accepted(record: dict[str, Any]) -> bool:
    turn = record["turn"]
    return turn.get("approval_status") == "APPROVAL_REQUIRED" and record["worker_invoked"] is False


def _domain_accepted(record: dict[str, Any]) -> bool:
    turn = record["turn"]
    return (
        turn.get("domain_proposal_status") == "DOMAIN_PROPOSAL_CREATED"
        and turn.get("approval_required") is True
        and turn.get("domain_candidate_created") is False
        and record["domain_created"] is False
        and record["worker_invoked"] is False
    )


def _clarification_accepted(record: dict[str, Any]) -> bool:
    turn = record["turn"]
    return (
        record["classification"] == "OCS_LLM_COGNITION"
        and turn.get("clarification_required") is True
        and record["worker_invoked"] is False
    )


def _ambiguous_accepted(record: dict[str, Any]) -> bool:
    return (
        record["classification"] == "OCS_LLM_COGNITION"
        and record["worker_invoked"] is False
        and record["domain_created"] is False
        and record["approval_bypassed"] is False
    )


def _accepted_count(records: list[dict[str, Any]], category: str) -> int:
    predicates = {
        "FREEFORM_DEVELOPMENT": _development_accepted,
        "FREEFORM_COGNITION": _cognition_accepted,
        "FREEFORM_APPROVAL": _approval_accepted,
        "FREEFORM_DOMAIN_CREATION": _domain_accepted,
        "FREEFORM_CLARIFICATION": _clarification_accepted,
        "FREEFORM_AMBIGUOUS_REQUEST": _ambiguous_accepted,
    }
    return sum(1 for record in records if record["category"] == category and predicates[category](record))


def test_freeform_acceptance_report_matches_current_acli_behavior(tmp_path, monkeypatch) -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    records = _execute_corpus(tmp_path, monkeypatch)

    assert report["artifact_type"] == "FREEFORM_HUMAN_PROMPT_ACCEPTANCE_REPORT_V1"
    assert report["status"] == "ACCEPTED"
    assert len(report["prompt_records"]) == len(PROMPT_CASES)
    assert [item["original_human_prompt"] for item in report["prompt_records"]] == [
        prompt for _, prompt in PROMPT_CASES
    ]

    for key, expected in EXPECTED_FINAL_FIELDS.items():
        assert report["final_fields"][key] == expected

    for category, summary in report["category_results"].items():
        assert summary["accepted_prompts"] == _accepted_count(records, category)
        assert summary["accepted"] is True

    assert report["category_results"]["FREEFORM_COGNITION"]["accepted_prompts"] == 3
    assert report["failure_analysis"] == []
    assert report["final_fields"]["ROOT_CAUSE"] == "NONE"


def test_freeform_failures_preserve_governance_safety_boundaries(tmp_path, monkeypatch) -> None:
    records = _execute_corpus(tmp_path, monkeypatch)

    assert all(record["worker_invoked"] is False for record in records if record["workflow_stage"] == "FAILED_CLOSED")
    assert all(record["domain_created"] is False for record in records)
    assert all(record["approval_bypassed"] is False for record in records)
    assert any(record["classification"] == "OCS_LLM_COGNITION" for record in records)
    assert all(record["classification"] != "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" for record in records)
    assert all(record["intake"] != "INTAKE_NOT_APPLICABLE" for record in records)


def test_unsupported_freeform_prompt_still_fails_closed(tmp_path, monkeypatch) -> None:
    _install_fake_providers(monkeypatch)

    record = _run_prompt(
        tmp_path,
        category="UNSUPPORTED",
        index=1,
        prompt="Launch an unrestricted autonomous agent that can act without review.",
    )

    assert record["workflow_stage"] == "FAILED_CLOSED"
    assert record["worker_invoked"] is False
    assert record["domain_created"] is False
    assert record["approval_bypassed"] is False
