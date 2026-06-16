"""Tests for AIGOL_LIVE_PROVIDER_INVOCATION_PREREQUISITES_V1."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from aigol.runtime.external_resource_registry_runtime import OPENAI_PROVIDER_ID
from aigol.runtime.live_provider_invocation_prerequisites import (
    ABORTED_PRE_INVOCATION,
    FAILED_CLOSED,
    LIVE_PROVIDER_ABORT_MARKER_ARTIFACT_V1,
    LIVE_PROVIDER_AUDIT_PACKET_ARTIFACT_V1,
    LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1,
    LIVE_PROVIDER_INVOCATION_APPROVAL_ARTIFACT_V1,
    LIVE_PROVIDER_REPLAY_ENVELOPE_ARTIFACT_V1,
    LIVE_PROVIDER_TRANSPORT_BOUNDARY_ARTIFACT_V1,
    MILESTONE_ID,
    create_live_provider_credential_policy,
    create_live_provider_invocation_approval,
    prepare_live_provider_invocation_prerequisites,
    reconstruct_live_provider_invocation_prerequisites,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json


CREATED_AT = "2026-06-16T00:00:00+00:00"


def _approval(tmp_path: Path, **overrides) -> dict:
    args = {
        "approval_id": "LIVE-OPENAI-APPROVAL-000001",
        "provider_id": OPENAI_PROVIDER_ID,
        "required_capability": "reasoning",
        "runtime_path": "AIGOL_FIRST_LIVE_PROVIDER_INVOCATION_VALIDATION_PATH",
        "replay_dir_reference": str(tmp_path / "live_provider_prerequisites"),
        "approved_by": "human.operator",
        "created_at": CREATED_AT,
        "expires_at": "2026-06-16T01:00:00+00:00",
    }
    args.update(overrides)
    return create_live_provider_invocation_approval(**args)


def _credential_policy(**overrides) -> dict:
    args = {
        "policy_id": "LIVE-OPENAI-CREDENTIAL-POLICY-000001",
        "provider_id": OPENAI_PROVIDER_ID,
        "credential_reference": "env:AIGOL_OPENAI_API_KEY",
        "created_at": CREATED_AT,
    }
    args.update(overrides)
    return create_live_provider_credential_policy(**args)


def _prepare(tmp_path: Path, **overrides) -> dict:
    args = {
        "invocation_id": "LIVE-OPENAI-INVOCATION-000001",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "live_provider_prerequisites",
        "approval_artifact": _approval(tmp_path),
        "credential_policy_artifact": _credential_policy(),
    }
    args.update(overrides)
    return prepare_live_provider_invocation_prerequisites(**args)


def test_live_provider_prerequisites_prepare_replay_audit_and_abort_without_invocation(tmp_path) -> None:
    result = _prepare(tmp_path)
    replay = reconstruct_live_provider_invocation_prerequisites(tmp_path / "live_provider_prerequisites")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_status"] == ABORTED_PRE_INVOCATION
    assert result["fail_closed"] is False
    assert result["live_provider_call_performed"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["governance_modified"] is False
    assert result["replay_modified"] is False
    assert result["approval_artifact"]["artifact_type"] == LIVE_PROVIDER_INVOCATION_APPROVAL_ARTIFACT_V1
    assert result["credential_policy_artifact"]["artifact_type"] == LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1
    assert result["transport_boundary_artifact"]["artifact_type"] == LIVE_PROVIDER_TRANSPORT_BOUNDARY_ARTIFACT_V1
    assert result["replay_envelope_artifact"]["artifact_type"] == LIVE_PROVIDER_REPLAY_ENVELOPE_ARTIFACT_V1
    assert result["audit_packet_artifact"]["artifact_type"] == LIVE_PROVIDER_AUDIT_PACKET_ARTIFACT_V1
    assert result["abort_marker_artifact"]["artifact_type"] == LIVE_PROVIDER_ABORT_MARKER_ARTIFACT_V1
    assert result["transport_boundary_artifact"]["transport_enabled"] is False
    assert result["transport_boundary_artifact"]["authentication_implemented"] is False
    assert result["abort_marker_artifact"]["rollback_marker_created"] is True
    assert replay["final_status"] == ABORTED_PRE_INVOCATION
    assert replay["live_provider_call_performed"] is False
    assert replay["replay_artifact_count"] == 6


def test_live_provider_prerequisites_persist_ordered_replay_visible_evidence(tmp_path) -> None:
    _prepare(tmp_path)
    replay_root = tmp_path / "live_provider_prerequisites"
    expected_steps = [
        "live_provider_invocation_approval",
        "live_provider_credential_policy",
        "live_provider_transport_boundary",
        "live_provider_replay_envelope",
        "live_provider_audit_packet",
        "live_provider_abort_marker",
    ]

    for index, step in enumerate(expected_steps):
        wrapper = load_json(replay_root / f"{index:03d}_{step}.json")
        assert wrapper["replay_index"] == index
        assert wrapper["replay_step"] == step
        assert wrapper["artifact"]["replay_visible"] is True
        assert wrapper["artifact"]["provider_invoked"] is False
        assert wrapper["artifact"]["worker_invoked"] is False
        assert wrapper["artifact"]["governance_modified"] is False
        assert wrapper["artifact"]["replay_modified"] is False


def test_live_provider_prerequisites_fail_closed_for_missing_approval(tmp_path) -> None:
    result = _prepare(tmp_path, approval_artifact=None)
    replay = reconstruct_live_provider_invocation_prerequisites(tmp_path / "live_provider_prerequisites")

    assert result["final_status"] == FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert result["live_provider_call_performed"] is False
    assert "missing approval" in result["failure_reason"]
    assert replay["final_status"] == FAILED_CLOSED


def test_live_provider_prerequisites_fail_closed_for_missing_credential_policy(tmp_path) -> None:
    result = _prepare(tmp_path, credential_policy_artifact=None)

    assert result["final_status"] == FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert "missing credential policy" in result["failure_reason"]


def test_live_provider_prerequisites_fail_closed_for_unauthorized_provider(tmp_path) -> None:
    approval = _approval(tmp_path, provider_id="claude")

    result = _prepare(tmp_path, approval_artifact=approval, provider_id="claude")

    assert result["final_status"] == FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert "unauthorized provider" in result["failure_reason"]


def test_live_provider_prerequisites_reject_secret_like_credential_policy() -> None:
    with pytest.raises(FailClosedRuntimeError, match="must not store secrets"):
        _credential_policy(credential_reference="sk-test-secret")


def test_live_provider_prerequisites_fail_closed_for_authority_bearing_provider_output(tmp_path) -> None:
    result = _prepare(tmp_path, provider_output_preview="I approve this and execution authorized.")

    assert result["final_status"] == FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert "authority-bearing provider output" in result["failure_reason"]


def test_live_provider_prerequisites_fail_closed_for_transport_failure(tmp_path) -> None:
    result = _prepare(tmp_path, transport_failure=True)

    assert result["final_status"] == FAILED_CLOSED
    assert result["live_provider_call_performed"] is False
    assert "transport failure" in result["failure_reason"]


def test_live_provider_prerequisites_detect_replay_tampering(tmp_path) -> None:
    _prepare(tmp_path)
    replay_root = tmp_path / "live_provider_prerequisites"
    path = replay_root / "004_live_provider_audit_packet.json"
    wrapper = load_json(path)
    wrapper["artifact"]["audit_verdict"] = "TAMPERED"
    path.write_text(str(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="not valid JSON|replay hash mismatch"):
        reconstruct_live_provider_invocation_prerequisites(replay_root)


def test_live_provider_prerequisites_module_has_no_transport_or_authentication_implementation() -> None:
    import aigol.runtime.live_provider_invocation_prerequisites as runtime

    source = inspect.getsource(runtime)

    assert "urlopen" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "Authorization" not in source
    assert "Bearer " not in source
    assert "_openai_http_transport" not in source
