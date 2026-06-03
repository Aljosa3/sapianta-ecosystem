"""Tests for AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.intent_clarification_dialog_runtime import (
    CLARIFICATION_RESOLVED,
    FAILED_CLOSED,
    HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1,
    HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1,
    HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1,
    reconstruct_intent_clarification_dialog_replay,
    run_intent_clarification_dialog,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-03T21:30:00+00:00"
CHAIN_ID = "CHAIN-CLARIFICATION-000001"


def _candidates() -> list[dict]:
    return [
        {
            "interpretation_id": "WORKER_FOUNDATION",
            "label": "Create a Trading workstation worker foundation.",
            "domain_id": "TRADING",
            "worker_family_id": "RISK_ANALYSIS",
            "milestone_type": "WORKER_FOUNDATION",
            "capability_id": "ANALYSIS",
            "resource_category": "WORKER",
            "output_scope": "GOVERNANCE_FOUNDATION",
            "resume_stage": "COGNITION",
        },
        {
            "interpretation_id": "INFRASTRUCTURE_TOOL",
            "label": "Create an operator workstation infrastructure artifact.",
            "domain_id": "AIGOL_CORE",
            "worker_family_id": None,
            "milestone_type": "OPERATOR_TOOL_FOUNDATION",
            "capability_id": "INFRASTRUCTURE",
            "resource_category": "OPERATOR_TOOL",
            "output_scope": "INFRASTRUCTURE_FOUNDATION",
            "resume_stage": "TASK_INTAKE",
        },
    ]


def _response(**overrides) -> dict:
    response = {
        "selected_interpretation": "WORKER_FOUNDATION",
        "selected_domain_id": "TRADING",
        "selected_worker_family_id": "RISK_ANALYSIS",
        "selected_milestone_type": "WORKER_FOUNDATION",
        "selected_output_scope": "GOVERNANCE_FOUNDATION",
        "human_response_text": "Create the Trading Risk Analysis worker foundation.",
        "resume_stage": "COGNITION",
    }
    response.update(overrides)
    return response


def test_intent_clarification_dialog_resolves_ambiguous_prompt(tmp_path) -> None:
    capture = run_intent_clarification_dialog(
        clarification_id="CLARIFICATION-000001",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference="PROMPT-CLARIFICATION-000001",
        human_prompt="Create a workstation.",
        ambiguity_categories=["INTENT_AMBIGUITY", "WORKER_AMBIGUITY", "RESOURCE_AMBIGUITY"],
        candidate_interpretations=_candidates(),
        human_response=_response(),
        source_artifact_reference="PROMPT-CLARIFICATION-000001",
        source_artifact_hash="sha256:prompt",
        context_reference="CONTEXT-OPTIONAL",
        context_hash="sha256:context",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resolved",
    )
    reconstructed = reconstruct_intent_clarification_dialog_replay(tmp_path / "resolved")
    request = capture["human_clarification_request_artifact"]
    response = capture["human_clarification_response_artifact"]
    resolution = capture["human_clarification_resolution_artifact"]

    assert request["artifact_type"] == HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1
    assert response["artifact_type"] == HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1
    assert resolution["artifact_type"] == HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1
    assert capture["resolution_status"] == CLARIFICATION_RESOLVED
    assert capture["resolved_intent"]["domain_id"] == "TRADING"
    assert capture["resolved_intent"]["worker_family_id"] == "RISK_ANALYSIS"
    assert capture["resolved_intent"]["milestone_type"] == "WORKER_FOUNDATION"
    assert capture["resume_stage"] == "COGNITION"
    assert request["bounded_questions"]
    assert request["clarification_history_hash"]
    assert resolution["clarification_history_preserved"] is True
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["authorization_created"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["resolution_status"] == CLARIFICATION_RESOLVED
    assert reconstructed["replay_artifact_count"] == 4


def test_clarification_preserves_history(tmp_path) -> None:
    history = [
        {
            "clarification_request_reference": "OLD-REQUEST",
            "clarification_response_reference": "OLD-RESPONSE",
            "resolution_status": "ADDITIONAL_CLARIFICATION_REQUIRED",
        }
    ]
    capture = run_intent_clarification_dialog(
        clarification_id="CLARIFICATION-HISTORY-000001",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference="PROMPT-CLARIFICATION-HISTORY-000001",
        human_prompt="Add analysis.",
        ambiguity_categories=["CAPABILITY_AMBIGUITY", "WORKER_AMBIGUITY"],
        candidate_interpretations=_candidates(),
        human_response=_response(),
        clarification_history=history,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "history",
    )

    assert capture["resolution_status"] == CLARIFICATION_RESOLVED
    assert len(capture["clarification_history"]) == 2
    assert capture["clarification_history"][0]["clarification_request_reference"] == "OLD-REQUEST"


def test_clarification_fails_closed_when_ambiguity_remains_unresolved(tmp_path) -> None:
    capture = run_intent_clarification_dialog(
        clarification_id="CLARIFICATION-UNRESOLVED-000001",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference="PROMPT-CLARIFICATION-UNRESOLVED-000001",
        human_prompt="Improve trading.",
        ambiguity_categories=["INTENT_AMBIGUITY"],
        candidate_interpretations=_candidates(),
        human_response=_response(selected_interpretation="UNKNOWN_CHOICE"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unresolved",
    )

    assert capture["resolution_status"] == FAILED_CLOSED
    assert "ambiguity remains unresolved" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_clarification_fails_closed_when_answers_contradict_candidate(tmp_path) -> None:
    capture = run_intent_clarification_dialog(
        clarification_id="CLARIFICATION-CONTRADICTION-000001",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference="PROMPT-CLARIFICATION-CONTRADICTION-000001",
        human_prompt="Create reporting.",
        ambiguity_categories=["DOMAIN_AMBIGUITY", "WORKER_AMBIGUITY"],
        candidate_interpretations=_candidates(),
        human_response=_response(selected_domain_id="MARKETING"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "contradiction",
    )

    assert capture["resolution_status"] == FAILED_CLOSED
    assert "contradictory answers detected" in capture["failure_reason"]


def test_clarification_fails_closed_when_limit_exceeded(tmp_path) -> None:
    history = [
        {"clarification_request_reference": "R1"},
        {"clarification_request_reference": "R2"},
        {"clarification_request_reference": "R3"},
    ]
    capture = run_intent_clarification_dialog(
        clarification_id="CLARIFICATION-LIMIT-000001",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference="PROMPT-CLARIFICATION-LIMIT-000001",
        human_prompt="Create a workstation.",
        ambiguity_categories=["INTENT_AMBIGUITY"],
        candidate_interpretations=_candidates(),
        human_response=_response(),
        clarification_history=history,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "limit",
    )

    assert capture["resolution_status"] == FAILED_CLOSED
    assert "clarification exceeds limits" in capture["failure_reason"]


def test_clarification_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    run_intent_clarification_dialog(
        clarification_id="CLARIFICATION-CORRUPT-000001",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference="PROMPT-CLARIFICATION-CORRUPT-000001",
        human_prompt="Create a workstation.",
        ambiguity_categories=["INTENT_AMBIGUITY"],
        candidate_interpretations=_candidates(),
        human_response=_response(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "002_human_clarification_resolution_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["resolution_status"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_intent_clarification_dialog_replay(tmp_path / "corrupt")


def test_intent_clarification_dialog_runtime_has_no_provider_worker_or_execution_invocations() -> None:
    import aigol.runtime.intent_clarification_dialog_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
