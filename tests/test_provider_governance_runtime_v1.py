import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_governance_runtime import (
    COGNITION_PARTICIPATION_ARTIFACT_V1,
    PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1,
    PROVIDER_USAGE_METRIC_ARTIFACT_V1,
    build_provider_credential_diagnostic,
    execute_provider_lifecycle_operation,
    query_provider_credentials,
    record_cognition_participation,
    record_provider_usage_metric,
    reconstruct_provider_governance_replay,
)
from aigol.runtime.transport.serialization import load_json


def test_provider_governance_verify_records_secret_free_event(tmp_path):
    event = execute_provider_lifecycle_operation(
        event_id="PGV-VERIFY-001",
        operation="VERIFY",
        provider_id="openai",
        requested_by="human.operator",
        created_at="2026-06-21T00:00:00Z",
        replay_dir=tmp_path / "events",
        env={"AIGOL_OPENAI_API_KEY": "sk-test-secret"},
    )

    assert event["artifact_type"] == PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1
    assert event["credential_present"] is True
    assert event["credential_value_recorded"] is False
    assert event["credential_hash_recorded"] is False
    assert event["credential_display_identifier"].startswith("ref:...")
    assert "sk-test-secret" not in json.dumps(event)

    persisted = load_json(tmp_path / "events" / "000_provider_governance_event.json")
    assert persisted["artifact_hash"] == event["artifact_hash"]


def test_destructive_provider_operations_require_human_approval(tmp_path):
    with pytest.raises(FailClosedRuntimeError, match="requires human approval"):
        execute_provider_lifecycle_operation(
            event_id="PGV-DISABLE-001",
            operation="DISABLE",
            provider_id="openai",
            requested_by="human.operator",
            created_at="2026-06-21T00:00:00Z",
            replay_dir=tmp_path,
        )

    event = execute_provider_lifecycle_operation(
        event_id="PGV-DISABLE-002",
        operation="DISABLE",
        provider_id="openai",
        requested_by="human.operator",
        created_at="2026-06-21T00:00:00Z",
        human_approval_artifact={"approval_status": "APPROVED", "artifact_hash": "approval-artifact-hash"},
        replay_dir=tmp_path / "approved",
    )

    assert event["human_approval_required"] is True
    assert event["human_approval_recorded"] is True
    assert event["lifecycle_status"] == "DISABLED"


def test_usage_metric_and_cognition_participation_are_replay_reconstructable(tmp_path):
    record_provider_usage_metric(
        metric_id="PGV-USAGE-001",
        provider_id="openai",
        model="gpt-4.1-mini",
        status="SUCCESS",
        availability="AVAILABLE",
        success_count=1,
        failure_count=0,
        last_used="2026-06-21T00:00:00Z",
        latency_ms=350,
        token_usage={"input_tokens": 12, "output_tokens": 8},
        cost_tracking={"estimated_cost_usd": 0.001},
        created_at="2026-06-21T00:00:01Z",
        replay_dir=tmp_path / "usage",
    )
    record_cognition_participation(
        participation_id="PGV-PARTICIPATION-001",
        provider_id="openai",
        participation_location="OCS_LLM_COGNITION",
        participation_role="proposal_only_cognition",
        workflow_id="OCS_LLM_COGNITION",
        invocation_reason="semantic ambiguity escalation",
        purpose="proposal generation",
        response_used=True,
        worker_invoked_after=False,
        human_confirmation_required=True,
        created_at="2026-06-21T00:00:02Z",
        replay_dir=tmp_path / "participation",
    )

    reconstruction = reconstruct_provider_governance_replay(tmp_path)

    assert reconstruction["provider_usage_metric_count"] == 1
    assert reconstruction["cognition_participation_count"] == 1
    assert reconstruction["provider_usage"][0]["artifact_type"] == PROVIDER_USAGE_METRIC_ARTIFACT_V1
    assert reconstruction["cognition_participation"][0]["artifact_type"] == COGNITION_PARTICIPATION_ARTIFACT_V1
    assert reconstruction["cognition_participation"][0]["human_confirmation_required"] is True


def test_invalid_participation_location_fails_closed():
    with pytest.raises(FailClosedRuntimeError, match="unsupported participation location"):
        record_cognition_participation(
            participation_id="PGV-PARTICIPATION-INVALID",
            provider_id="openai",
            participation_location="UNBOUNDED_AGENT_AUTONOMY",
            participation_role="proposal_only_cognition",
            workflow_id="UNKNOWN",
            invocation_reason="invalid",
            purpose="invalid",
            response_used=False,
            worker_invoked_after=False,
            human_confirmation_required=True,
            created_at="2026-06-21T00:00:00Z",
        )


def test_provider_credentials_query_is_secret_free():
    rows = query_provider_credentials(env={"AIGOL_OPENAI_API_KEY": "sk-test-secret"})
    openai = next(row for row in rows if row["provider_id"] == "openai")

    assert openai["credential_present"] is True
    assert openai["credential_reference"] == "env:AIGOL_OPENAI_API_KEY"
    serialized = json.dumps(rows)
    assert "sk-test-secret" not in serialized
    assert openai["credential_hash_recorded"] is False


def test_provider_governance_cli_query_renders_replay_visible_status(tmp_path):
    record_provider_usage_metric(
        metric_id="PGV-USAGE-CLI",
        provider_id="openai",
        model="gpt-4.1-mini",
        status="FAILED",
        availability="DEPENDENCY_UNAVAILABLE",
        success_count=0,
        failure_count=1,
        last_failure="transport failure",
        created_at="2026-06-21T00:00:00Z",
        replay_dir=tmp_path / "usage",
    )

    args = build_parser().parse_args(
        ["provider", "governance", "failures", "--replay-root", str(tmp_path)]
    )
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol provider governance failures"
    assert result["rows"][0]["provider_id"] == "openai"
    assert "AIGOL PROVIDER GOVERNANCE" in rendered
    assert "transport failure" in rendered


def test_credential_diagnostic_rejects_unknown_provider():
    with pytest.raises(FailClosedRuntimeError, match="unknown provider_id"):
        build_provider_credential_diagnostic(provider_id="unknown-provider")
