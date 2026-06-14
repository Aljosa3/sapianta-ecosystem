"""Real ACLI human-prompt acceptance tests for AIGOL_REAL_ACLI_HUMAN_PROMPT_ACCEPTANCE_V1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter, openai_provider_metadata
from aigol.runtime.domain_proposal_governance_runtime import (
    APPROVED,
    DOMAIN_CANDIDATE_ARTIFACT_V1,
    DOMAIN_CANDIDATE_CREATED,
    create_domain_proposal,
    review_domain_proposal,
)
from aigol.runtime.gap_to_improvement_intent_e2e_runtime import (
    GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED,
    PENDING_HUMAN_REVIEW,
    run_gap_to_improvement_intent_e2e,
)
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_COMPLETED
from aigol.runtime.transport.serialization import replay_hash


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "governance" / "REAL_ACLI_ACCEPTANCE_REPORT_V1.json"
ROUTING_REPAIR_REPORT_PATH = ROOT / "governance" / "AIGOL_HUMAN_PROMPT_ROUTING_REPAIR_V1.json"
CREATED_AT = "2026-06-14T00:00:00Z"

DEVELOPMENT_PROMPT = "Implement a simple calculator function"
CLARIFICATION_PROMPT = "Create a reporting system suitable for my business"
APPROVAL_PROMPT = "Deploy a production system affecting external users"
DOMAIN_PROPOSAL_PROMPT = "Create a new HR evaluation domain"


@dataclass
class FakeProviderAdapter:
    response: dict[str, Any]
    provider_id: str = "openai"
    provider_version: str = openai_provider_metadata().provider_version
    calls: int = 0

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str):
        self.calls += 1
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=self.response,
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
            str(tmp_path / f"{session_id.lower()}_runtime"),
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


def _valid_provider_response() -> dict[str, Any]:
    return {
        "proposal_summary": "Create bounded governed implementation evidence.",
        "proposed_outputs": [
            "governance/REAL_ACLI_ACCEPTANCE_EVIDENCE.md",
            "governance/REAL_ACLI_ACCEPTANCE_CERTIFICATION.json",
        ],
        "constraints_acknowledged": [
            "NO_DISPATCH",
            "NO_INVOCATION",
            "NO_EXECUTION",
            "PROPOSAL_ONLY",
        ],
        "assumptions": ["Execution remains behind canonical authorization."],
        "known_gaps": ["Acceptance prompts may not be canonical milestone prompts."],
    }


def _install_fake_proposal_adapter(monkeypatch) -> FakeProviderAdapter:
    adapter = FakeProviderAdapter(_valid_provider_response())
    monkeypatch.setattr(aigol_cli, "_post_context_continuation_provider_adapter", lambda: adapter)
    return adapter


def _install_fake_ocs_provider(monkeypatch) -> None:
    def fake_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        return {
            "id": "resp-real-acli-acceptance-ocs-001",
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
                                    "findings": ["The prompt requires governed OCS decision evidence."],
                                    "assumptions": ["No execution occurs before authorization."],
                                    "alternatives": ["Clarify", "Request approval", "Fail closed"],
                                    "risks": ["Execution must remain gated."],
                                    "uncertainties": ["Operator intent may be underspecified."],
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

    monkeypatch.setattr(
        aigol_cli,
        "_conversation_openai_provider_adapter",
        lambda: OpenAIProviderAdapter(api_key="test-openai-key", client=fake_client),
    )


def _install_fake_external_worker_openai_client(monkeypatch) -> None:
    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        return {
            "id": "resp-real-acli-acceptance-worker-001",
            "output_text": "Return bounded implementation result evidence.",
        }

    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)


def _run_acli_prompt(tmp_path: Path, monkeypatch, *, session_id: str, prompt: str) -> dict[str, Any]:
    _install_fake_proposal_adapter(monkeypatch)
    _install_fake_ocs_provider(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence([prompt, "exit"]),
        output_func=output.append,
    )
    result["captured_output"] = output
    return result


def _accepted_to_replay(result: dict[str, Any]) -> bool:
    if result.get("turn_count") != 1 or not result.get("turns"):
        return False
    turn = result["turns"][0]
    return (
        turn.get("replay_certification_status") == REPLAY_CERTIFICATION_COMPLETED
        and turn.get("worker_invoked") is True
        and (
            turn.get("authorization_created") is True
            or turn.get("execution_authorization_status") == "EXECUTION_AUTHORIZED"
        )
        and turn.get("approval_bypassed") is not True
    )


def _clarification_required(result: dict[str, Any]) -> bool:
    if result.get("turn_count") != 1 or not result.get("turns"):
        return False
    turn = result["turns"][0]
    return turn.get("clarification_required") is True and turn.get("worker_invoked") is False


def _approval_required(result: dict[str, Any]) -> bool:
    if result.get("turn_count") != 1 or not result.get("turns"):
        return False
    turn = result["turns"][0]
    return turn.get("approval_status") == "APPROVAL_REQUIRED" and turn.get("worker_invoked") is False


def _domain_prompt_reaches_proposal_boundary(result: dict[str, Any]) -> bool:
    if result.get("turn_count") != 1 or not result.get("turns"):
        return False
    turn = result["turns"][0]
    return (
        turn.get("domain_proposal_status") == "DOMAIN_PROPOSAL_CREATED"
        and turn.get("approval_required") is True
        and turn.get("domain_candidate_created") is False
        and turn.get("domain_created") is False
        and turn.get("worker_invoked") is False
    )


def _execution_replay() -> dict[str, Any]:
    payload = {
        "execution_id": "EXECUTION-REPLAY-REAL-ACLI-ACCEPTANCE-000001",
        "execution_status": "TERMINATED",
        "result_validation_status": "FAILED",
        "repair_started": False,
        "worker_execution_requested_by_e2e": False,
        "provider_change_requested": False,
    }
    return {
        "evidence_id": "EXECUTION-VALIDATION-REAL-ACLI-ACCEPTANCE-000001",
        "evidence_type": "VALIDATION_RESULT",
        "source_replay_reference": "replay/real-acli-acceptance-validation-000001.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": "CHAIN-REAL-ACLI-ACCEPTANCE-REPLAY-000001",
        "observed_condition": "Execution replay records failed validation.",
        "expected_condition": "Execution replay should record validated result.",
        "confidence": "DETERMINISTIC",
        "status": "FAILED",
    }


def _run_replay_improvement_acceptance(tmp_path: Path) -> dict[str, Any]:
    return run_gap_to_improvement_intent_e2e(
        run_id="REAL-ACLI-ACCEPTANCE-GAP-INTENT-000001",
        execution_replay_artifacts=[_execution_replay()],
        canonical_chain_id="CHAIN-REAL-ACLI-ACCEPTANCE-REPLAY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "replay_improvement_acceptance",
        domain_id="AIGOL_CORE",
        affected_layer="GOVERNANCE",
        affected_worker_family="REGRESSION_GAP_ANALYSIS",
    )


def _run_domain_proposal_acceptance(tmp_path: Path) -> dict[str, Any]:
    proposal = create_domain_proposal(
        proposal_id="DOMAIN-PROPOSAL-REAL-ACLI-ACCEPTANCE-HR-000001",
        source_type="HUMAN_REQUEST",
        proposed_domain="HREvaluation",
        need_summary=DOMAIN_PROPOSAL_PROMPT,
        requested_by="HUMAN_OPERATOR",
        canonical_chain_id="CHAIN-REAL-ACLI-ACCEPTANCE-DOMAIN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "domain_proposal_acceptance",
    )["domain_proposal_artifact"]
    return review_domain_proposal(
        review_id="DOMAIN-REVIEW-REAL-ACLI-ACCEPTANCE-HR-000001",
        domain_proposal_artifact=proposal,
        decision=APPROVED,
        decision_reason="Acceptance test supplies explicit human review to prove candidate boundary.",
        reviewed_by="HUMAN_OPERATOR",
        reviewed_at=CREATED_AT,
        human_approval_reference="HUMAN-DOMAIN-REVIEW-REAL-ACLI-ACCEPTANCE-HR-000001",
        replay_dir=tmp_path / "domain_proposal_review_acceptance",
    )


def _replay_improvement_accepted(capture: dict[str, Any]) -> bool:
    artifact = capture["gap_to_improvement_intent_e2e_artifact"]
    return (
        artifact["e2e_status"] == GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED
        and capture["human_review_gate_artifact"]["review_status"] == PENDING_HUMAN_REVIEW
    )


def test_real_acli_acceptance_report_matches_current_prompt_behavior(tmp_path, monkeypatch) -> None:
    development = _run_acli_prompt(
        tmp_path,
        monkeypatch,
        session_id="SESSION-REAL-ACLI-ACCEPTANCE-DEV",
        prompt=DEVELOPMENT_PROMPT,
    )
    clarification = _run_acli_prompt(
        tmp_path,
        monkeypatch,
        session_id="SESSION-REAL-ACLI-ACCEPTANCE-CLARIFICATION",
        prompt=CLARIFICATION_PROMPT,
    )
    approval = _run_acli_prompt(
        tmp_path,
        monkeypatch,
        session_id="SESSION-REAL-ACLI-ACCEPTANCE-APPROVAL",
        prompt=APPROVAL_PROMPT,
    )
    domain_prompt = _run_acli_prompt(
        tmp_path,
        monkeypatch,
        session_id="SESSION-REAL-ACLI-ACCEPTANCE-DOMAIN",
        prompt=DOMAIN_PROPOSAL_PROMPT,
    )
    replay_improvement = _run_replay_improvement_acceptance(tmp_path)
    domain_proposal = _run_domain_proposal_acceptance(tmp_path)
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    repair_report = json.loads(ROUTING_REPAIR_REPORT_PATH.read_text(encoding="utf-8"))

    assert report["artifact_type"] == "REAL_ACLI_ACCEPTANCE_REPORT_V1"
    assert repair_report["artifact_type"] == "AIGOL_HUMAN_PROMPT_ROUTING_REPAIR_V1"
    assert report["final_fields"]["DEVELOPMENT_PROMPT_ACCEPTED"] == _yes_no(_accepted_to_replay(development))
    assert report["final_fields"]["CLARIFICATION_PROMPT_ACCEPTED"] == _yes_no(_clarification_required(clarification))
    assert report["final_fields"]["APPROVAL_PROMPT_ACCEPTED"] == _yes_no(_approval_required(approval))
    assert report["final_fields"]["REPLAY_IMPROVEMENT_ACCEPTED"] == _yes_no(
        _replay_improvement_accepted(replay_improvement)
    )
    assert report["final_fields"]["DOMAIN_PROPOSAL_ACCEPTED"] == _yes_no(
        _domain_prompt_reaches_proposal_boundary(domain_prompt)
    )
    assert domain_proposal["domain_review_outcome_artifact"]["artifact_type"] == DOMAIN_CANDIDATE_ARTIFACT_V1
    assert domain_proposal["domain_review_outcome_artifact"]["outcome_status"] == DOMAIN_CANDIDATE_CREATED
    assert report["final_fields"]["END_TO_END_WORKFLOW_OPERATIONAL"] == "YES"
    assert report["final_fields"]["FIRST_FAILURE_STAGE"] == "NONE"
    assert repair_report["final_fields"] == {
        "DEVELOPMENT_ROUTING_FIXED": "YES",
        "OCS_ROUTING_FIXED": "YES",
        "APPROVAL_ROUTING_FIXED": "YES",
        "DOMAIN_ROUTING_FIXED": "YES",
        "REAL_HUMAN_PROMPT_ROUTING_OPERATIONAL": "YES",
    }


def test_real_acli_plain_development_prompt_does_not_bypass_routing_or_authorization(tmp_path, monkeypatch) -> None:
    result = _run_acli_prompt(
        tmp_path,
        monkeypatch,
        session_id="SESSION-REAL-ACLI-ACCEPTANCE-DEV-BOUNDARY",
        prompt=DEVELOPMENT_PROMPT,
    )
    turn = result["turns"][0]

    assert _accepted_to_replay(result) is True
    assert turn.get("routing_visibility_workflow_id") == "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION"
    assert turn.get("execution_authorization_status") == "EXECUTION_AUTHORIZED"
    assert turn.get("worker_invoked") is True
    assert turn.get("approval_bypassed") is not True


def test_replay_improvement_acceptance_reaches_human_review_boundary(tmp_path) -> None:
    capture = _run_replay_improvement_acceptance(tmp_path)
    intent = capture["improvement_intent_capture"]["improvement_intent_artifact"]
    gate = capture["human_review_gate_artifact"]

    assert capture["gap_to_improvement_intent_e2e_artifact"]["e2e_status"] == GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED
    assert intent["intent_status"] == "IMPROVEMENT_INTENT_CREATED"
    assert intent["worker_invoked"] is False
    assert intent["execution_requested"] is False
    assert gate["review_status"] == PENDING_HUMAN_REVIEW
    assert gate["approval_required"] is True
    assert gate["approval_granted"] is False


def test_domain_proposal_runtime_creates_candidate_only_after_explicit_review(tmp_path) -> None:
    capture = _run_domain_proposal_acceptance(tmp_path)
    proposal = capture["domain_review_decision_artifact"]
    outcome = capture["domain_review_outcome_artifact"]

    assert proposal["review_status"] == APPROVED
    assert proposal["domain_proposal_reference"] == "DOMAIN-PROPOSAL-REAL-ACLI-ACCEPTANCE-HR-000001"
    assert outcome["artifact_type"] == DOMAIN_CANDIDATE_ARTIFACT_V1
    assert outcome["outcome_status"] == DOMAIN_CANDIDATE_CREATED
    assert outcome["domain_created"] is False
    assert outcome["worker_invoked"] is False
    assert outcome["execution_started"] is False


def _yes_no(value: bool) -> str:
    return "YES" if value else "NO"
