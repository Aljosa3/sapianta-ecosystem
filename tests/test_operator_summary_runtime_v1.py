"""Tests for AIGOL_OPERATOR_SUMMARY_RUNTIME_V1."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.operator_summary_runtime import (
    OPERATOR_SUMMARY_ARTIFACT_V1,
    OPERATOR_SUMMARY_CREATED,
    create_operator_summary,
    reconstruct_operator_summary_replay,
    render_operator_summary,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CREATED_AT = "2026-06-05T12:00:00Z"


def _domain_lifecycle() -> dict:
    return {
        "conversation_to_ppp_terminal_status": "IMPLEMENTATION_HANDOFF_CREATED",
        "intent_class": "CREATE_DOMAIN",
        "target_domain": "MARKETING",
        "proposal_production_status": "PROVIDER_PROPOSAL_PRODUCED",
        "proposal_validation_status": "DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED",
        "worker_assignment": {"assignment_status": "WORKER_ASSIGNED"},
        "worker_dispatch": {"dispatch_status": "WORKER_DISPATCHED"},
        "worker_invocation": {"invocation_status": "WORKER_INVOKED"},
        "worker_result_capture": {"result_capture_status": "WORKER_RESULT_CAPTURED"},
        "worker_result_validation": {"validation_status": "RESULT_VALIDATED"},
        "executable_bundle": {"executable_bundle_verification_status": "EXECUTABLE_BUNDLE_VERIFIED"},
        "post_execution_replay_review": {"review_status": "REVIEW_COMPLETED"},
        "governed_termination": {"termination_status": "TERMINATED"},
    }


def test_operator_summary_translates_verbose_domain_lifecycle(tmp_path) -> None:
    capture = create_operator_summary(
        operator_summary_id="OPERATOR-SUMMARY-000001",
        lifecycle_input=_domain_lifecycle(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "summary",
        source_replay_reference="/tmp/source/replay",
    )
    reconstructed = reconstruct_operator_summary_replay(tmp_path / "summary")
    artifact = capture["operator_summary_artifact"]

    assert artifact["artifact_type"] == OPERATOR_SUMMARY_ARTIFACT_V1
    assert capture["summary_status"] == OPERATOR_SUMMARY_CREATED
    assert capture["headline"] == "Domain bundle created and verified."
    assert "authorized create-only domain bundle for MARKETING" in capture["details"][0]
    assert "worker_lifecycle" in capture["technical_stage_groups"]
    assert capture["source_replay_mutated"] is False
    assert capture["lifecycle_modified"] is False
    assert all(value is False for value in capture["authority_flags"].values())
    assert reconstructed["operator_summary_hash"] == capture["operator_summary_hash"]
    assert reconstructed["replay_artifact_count"] == 2
    assert "Domain bundle created and verified." in render_operator_summary(capture)


def test_operator_summary_is_deterministic_for_identical_lifecycle_inputs(tmp_path) -> None:
    first = create_operator_summary(
        operator_summary_id="OPERATOR-SUMMARY-DETERMINISTIC",
        lifecycle_input=_domain_lifecycle(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
        source_replay_reference="/tmp/source/replay",
    )
    second = create_operator_summary(
        operator_summary_id="OPERATOR-SUMMARY-DETERMINISTIC",
        lifecycle_input=_domain_lifecycle(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
        source_replay_reference="/tmp/source/replay",
    )

    assert first["operator_summary_hash"] == second["operator_summary_hash"]
    assert first["headline"] == second["headline"]
    assert first["details"] == second["details"]


def test_operator_summary_records_human_decision_required(tmp_path) -> None:
    capture = create_operator_summary(
        operator_summary_id="OPERATOR-SUMMARY-APPROVAL-000001",
        lifecycle_input={
            "target_domain": "TRADING",
            "conversation_to_ppp_terminal_status": "HUMAN_APPROVAL_REQUIRED",
            "approval_status": "HUMAN_APPROVAL_REQUIRED",
        },
        created_at=CREATED_AT,
        replay_dir=tmp_path / "approval",
    )

    assert capture["headline"] == "Human decision required."
    assert capture["operator_next_steps"] == ["Choose APPROVE, REJECT, or REQUEST_MODIFICATION."]
    assert capture["authority_flags"]["creates_approval"] is False


def test_operator_summary_records_rejection_and_modification(tmp_path) -> None:
    rejection = create_operator_summary(
        operator_summary_id="OPERATOR-SUMMARY-REJECT-000001",
        lifecycle_input={
            "decision_status": "GOVERNED_REJECTION_RECORDED",
            "terminal_status": "GOVERNED_REJECTION_TERMINATED",
        },
        created_at=CREATED_AT,
        replay_dir=tmp_path / "rejection",
    )
    modification = create_operator_summary(
        operator_summary_id="OPERATOR-SUMMARY-MODIFY-000001",
        lifecycle_input={"decision_status": "MODIFICATION_REQUEST_RECORDED", "terminal_status": "CLARIFICATION_REQUIRED"},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "modification",
    )

    assert rejection["headline"] == "Request rejected and closed."
    assert modification["headline"] == "Modification requested; clarification is required."


def test_operator_summary_fails_closed_for_invalid_lifecycle_input(tmp_path) -> None:
    capture = create_operator_summary(
        operator_summary_id="OPERATOR-SUMMARY-FAIL-000001",
        lifecycle_input=[],  # type: ignore[arg-type]
        created_at=CREATED_AT,
        replay_dir=tmp_path / "failure",
    )
    reconstructed = reconstruct_operator_summary_replay(tmp_path / "failure")

    assert capture["fail_closed"] is True
    assert capture["summary_status"] == "FAILED_CLOSED"
    assert "lifecycle input must be a JSON object" in capture["failure_reason"]
    assert reconstructed["summary_status"] == "FAILED_CLOSED"


def test_operator_summary_replay_fails_closed_on_tamper(tmp_path) -> None:
    create_operator_summary(
        operator_summary_id="OPERATOR-SUMMARY-TAMPER-000001",
        lifecycle_input=_domain_lifecycle(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "tamper",
    )
    wrapper_path = tmp_path / "tamper" / "000_operator_summary_recorded.json"
    wrapper = load_json(wrapper_path)
    wrapper["artifact"]["headline"] = "tampered"
    wrapper_path.unlink()
    write_json_immutable(wrapper_path, wrapper)

    with pytest.raises(FailClosedRuntimeError, match="operator summary replay hash mismatch"):
        reconstruct_operator_summary_replay(tmp_path / "tamper")


def test_operator_summary_runtime_does_not_import_cli_or_mutating_lifecycle_runtime() -> None:
    import aigol.runtime.operator_summary_runtime as module

    source = inspect.getsource(module)

    assert "aigol.cli" not in source
    assert "terminate_reviewed_operation(" not in source
    assert "authorize_execution(" not in source
    assert "assign_worker(" not in source
    assert "dispatch_worker(" not in source

