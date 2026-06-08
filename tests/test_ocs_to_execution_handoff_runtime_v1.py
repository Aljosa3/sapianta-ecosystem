"""Tests for AIGOL_OCS_TO_EXECUTION_HANDOFF_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import create_default_cognition_provider_contract
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import run_ocs_llm_cognition_end_to_end
from aigol.runtime.ocs_to_execution_handoff_runtime import (
    EXECUTION_HANDOFF_CANDIDATE,
    FAILED_CLOSED,
    MILESTONE_ID,
    OCS_EXECUTION_HANDOFF_ARTIFACT_V1,
    create_ocs_execution_handoff,
    reconstruct_ocs_execution_handoff_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-08T00:00:00Z"


def _source_context() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-OCS-HANDOFF-001",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks OCS to identify execution-ready candidate context.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return {"conversation_context": [artifact]}


def _ocs_capture(tmp_path: Path) -> dict:
    response = json.dumps(
        {
            "findings": ["OCS found a bounded execution candidate for human review."],
            "assumptions": ["Execution must remain downstream of approval."],
            "risks": ["Worker selection must remain bounded."],
            "uncertainties": ["Exact worker implementation scope requires review."],
            "clarification_questions": ["Should this become an execution intake candidate?"],
            "recommended_next_milestone": "Create OCS execution handoff artifact.",
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )

    def transport(_payload: dict, metadata: dict) -> dict:
        assert metadata["provider_role"] == "COGNITION_PROVIDER"
        return {
            "model": "gpt-5.1",
            "output_text": response,
            "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        }

    return run_ocs_llm_cognition_end_to_end(
        end_to_end_id="OCS-HANDOFF-E2E-001",
        human_question="Turn this OCS cognition into a bounded execution candidate.",
        source_context=_source_context(),
        provider_contracts=[create_default_cognition_provider_contract(provider_id="openai", created_at=CREATED_AT)],
        transport_registry={"openai": transport},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_e2e",
        source_chain_id="CHAIN-OCS-HANDOFF-001",
        source_request_reference="HUMAN-REQUEST-OCS-HANDOFF-001",
        single_provider_primary_mode=True,
    )


def _handoff_args(tmp_path: Path) -> dict:
    ocs = _ocs_capture(tmp_path)
    assert ocs["fail_closed"] is False
    return {
        "handoff_id": "OCS-HANDOFF-001",
        "ocs_cognition_replay_reference": ocs["replay_reference"],
        "execution_intake_id": "OCS-EXECUTION-INTAKE-001",
        "execution_intent_summary": "Prepare a bounded execution candidate for human review.",
        "execution_candidate_scope": {
            "mode": "EXECUTION_INTAKE_ONLY",
            "domain": "product_build",
            "execution_authorized": False,
        },
        "requested_outcomes": ["execution intake candidate"],
        "non_goals": ["approval", "authorization", "worker dispatch"],
        "allowed_outputs": ["execution-ready candidate proposal"],
        "forbidden_operations": ["AUTHORIZE_EXECUTION", "INVOKE_WORKER", "DISPATCH_WORKER", "RETRY", "REPAIR"],
        "worker_role_requirements": ["bounded implementation worker"],
        "target_worker_family": "IMPLEMENTATION",
        "candidate_worker_constraints": {"single_worker_only": True, "human_review_required": True},
        "worker_capability_requirements": ["bounded file generation after downstream authorization"],
        "worker_exclusion_rules": ["no provider-as-worker", "no unregistered worker"],
        "worker_registry_requirements": ["registered worker identity required"],
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "ocs_handoff",
        "source_chain_id": "CHAIN-OCS-HANDOFF-001",
    }


def test_ocs_execution_handoff_artifact_is_created_without_downstream_authority(tmp_path):
    capture = create_ocs_execution_handoff(**_handoff_args(tmp_path))
    replay = reconstruct_ocs_execution_handoff_replay(tmp_path / "ocs_handoff")
    artifact = capture["ocs_execution_handoff_artifact"]

    assert capture["milestone_id"] == MILESTONE_ID
    assert capture["handoff_status"] == EXECUTION_HANDOFF_CANDIDATE
    assert artifact["artifact_type"] == OCS_EXECUTION_HANDOFF_ARTIFACT_V1
    assert artifact["handoff_status"] == EXECUTION_HANDOFF_CANDIDATE
    assert artifact["approval_status"] == "PENDING_HUMAN_REVIEW"
    assert artifact["approval_reference"] is None
    assert artifact["approval_hash"] is None
    assert artifact["worker_selection_status"] == "NOT_SELECTED"
    assert artifact["worker_reference"] is None
    assert artifact["worker_hash"] is None
    assert artifact["execution_readiness_status"] == "NOT_EXECUTION_READY"
    assert artifact["human_review_required"] is True
    assert artifact["authorization_created"] is False
    assert artifact["worker_request_created"] is False
    assert artifact["worker_assigned"] is False
    assert artifact["worker_dispatched"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_started"] is False
    assert artifact["repair_started"] is False
    assert artifact["retry_started"] is False
    assert artifact["ocs_cognition_hash"].startswith("sha256:")
    assert artifact["human_facing_cognition_hash"].startswith("sha256:")
    assert artifact["findings_hash"].startswith("sha256:")
    assert artifact["downstream_expected_artifact_refs"]
    assert replay["handoff_status"] == EXECUTION_HANDOFF_CANDIDATE
    assert replay["approval_status"] == "PENDING_HUMAN_REVIEW"
    assert replay["execution_readiness_status"] == "NOT_EXECUTION_READY"
    assert replay["worker_invoked"] is False
    assert replay["execution_started"] is False


def test_missing_ocs_replay_fails_closed_without_creating_authority(tmp_path):
    args = _handoff_args(tmp_path)
    args["ocs_cognition_replay_reference"] = str(tmp_path / "missing_ocs")
    args["replay_dir"] = tmp_path / "failed_handoff"
    capture = create_ocs_execution_handoff(**args)

    assert capture["handoff_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert "runtime artifact missing" in capture["failure_reason"]
    assert capture["authorization_created"] is False
    assert capture["worker_request_created"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_started"] is False


def test_ambiguous_execution_scope_fails_closed(tmp_path):
    args = _handoff_args(tmp_path)
    args["execution_candidate_scope"] = {}
    args["replay_dir"] = tmp_path / "ambiguous_handoff"
    capture = create_ocs_execution_handoff(**args)

    assert capture["handoff_status"] == FAILED_CLOSED
    assert "execution scope ambiguous" in capture["failure_reason"]


def test_handoff_replay_tampering_is_detected(tmp_path):
    create_ocs_execution_handoff(**_handoff_args(tmp_path))
    path = tmp_path / "ocs_handoff" / "000_ocs_execution_handoff_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_started"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch|hash mismatch"):
        reconstruct_ocs_execution_handoff_replay(tmp_path / "ocs_handoff")


def test_ocs_execution_handoff_runtime_preserves_non_execution_boundary() -> None:
    import aigol.runtime.ocs_to_execution_handoff_runtime as runtime

    source = inspect.getsource(runtime)

    forbidden_calls = (
        "authorize_execution_ready(",
        "create_worker_invocation_request(",
        "assign_worker(",
        "dispatch_worker(",
        "invoke_worker(",
        "repair(",
        "retry(",
    )
    for forbidden in forbidden_calls:
        assert forbidden not in source
