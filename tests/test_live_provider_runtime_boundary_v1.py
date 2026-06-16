"""Tests for AIGOL_LIVE_PROVIDER_RUNTIME_BOUNDARY_V1."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from aigol.runtime.external_resource_registry_runtime import (
    ACTIVE,
    COGNITION_PROVIDER,
    OPENAI_PROVIDER_ID,
    create_err_v0_registry,
    register_resource,
)
from aigol.runtime.live_provider_invocation_prerequisites import (
    create_live_provider_credential_policy,
    create_live_provider_invocation_approval,
)
from aigol.runtime.live_provider_runtime_boundary import (
    CANONICAL_COGNITION_PROVIDER_INPUT_V1,
    CANONICAL_COGNITION_PROVIDER_OUTPUT_V1,
    ERROR_AUTHORITY_BOUNDARY_VIOLATION,
    ERROR_MALFORMED_RESPONSE,
    ERROR_RATE_LIMIT,
    ERROR_TIMEOUT,
    LIVE_PROVIDER_CREDENTIAL_RETRIEVAL_ATTEMPT_ARTIFACT_V1,
    LIVE_PROVIDER_CREDENTIAL_USE_BOUNDARY_ARTIFACT_V1,
    LIVE_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1,
    LIVE_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1,
    LIVE_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1,
    LIVE_PROVIDER_RUNTIME_BOUNDARY_AUDIT_ARTIFACT_V1,
    MILESTONE_ID,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    reconstruct_live_provider_runtime_boundary_replay,
    run_live_provider_runtime_boundary,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json


CREATED_AT = "2026-06-16T00:00:00+00:00"


def _approval(tmp_path: Path, **overrides) -> dict:
    args = {
        "approval_id": "LIVE-BOUNDARY-APPROVAL-000001",
        "provider_id": OPENAI_PROVIDER_ID,
        "required_capability": "reasoning",
        "runtime_path": "AIGOL_LIVE_PROVIDER_RUNTIME_BOUNDARY_V1",
        "replay_dir_reference": str(tmp_path / "live_boundary"),
        "approved_by": "human.operator",
        "created_at": CREATED_AT,
        "expires_at": "2026-06-16T01:00:00+00:00",
    }
    args.update(overrides)
    return create_live_provider_invocation_approval(**args)


def _credential_policy(**overrides) -> dict:
    args = {
        "policy_id": "LIVE-BOUNDARY-CREDENTIAL-POLICY-000001",
        "provider_id": OPENAI_PROVIDER_ID,
        "credential_reference": "env:AIGOL_OPENAI_API_KEY",
        "created_at": CREATED_AT,
    }
    args.update(overrides)
    return create_live_provider_credential_policy(**args)


def _transport(response_text: str = "Boundary response captured as non-authoritative cognition."):
    def call(payload: dict, metadata: dict) -> dict:
        assert payload["stream"] is False
        assert metadata["provider_id"] == OPENAI_PROVIDER_ID
        assert metadata["credential_secret_replayed"] is False
        assert metadata["live_provider_call_performed"] is False
        return {
            "id": "deterministic-live-boundary-response",
            "output_text": response_text,
            "real_openai_called": False,
        }

    return call


def _run(tmp_path: Path, monkeypatch, **overrides) -> dict:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")
    args = {
        "invocation_id": "LIVE-BOUNDARY-INVOCATION-000001",
        "human_request": "Validate the governed live provider runtime boundary.",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "live_boundary",
        "approval_artifact": _approval(tmp_path),
        "credential_policy_artifact": _credential_policy(),
        "transport": _transport(),
    }
    args.update(overrides)
    return run_live_provider_runtime_boundary(**args)


def test_live_provider_boundary_records_successful_deterministic_boundary_without_live_call(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch)
    replay = reconstruct_live_provider_runtime_boundary_replay(tmp_path / "live_boundary")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_status"] == STATUS_COMPLETED
    assert result["live_provider_call_performed"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["governance_modified"] is False
    assert result["replay_modified"] is False
    assert result["credential_secret_replayed"] is False
    assert result["credential_retrieval_artifact"]["artifact_type"] == LIVE_PROVIDER_CREDENTIAL_RETRIEVAL_ATTEMPT_ARTIFACT_V1
    assert result["credential_use_boundary_artifact"]["artifact_type"] == LIVE_PROVIDER_CREDENTIAL_USE_BOUNDARY_ARTIFACT_V1
    assert result["live_request_envelope_artifact"]["artifact_type"] == LIVE_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1
    assert result["live_response_envelope_artifact"]["artifact_type"] == LIVE_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1
    assert result["live_boundary_audit_artifact"]["artifact_type"] == LIVE_PROVIDER_RUNTIME_BOUNDARY_AUDIT_ARTIFACT_V1
    assert result["canonical_provider_input"]["artifact_type"] == CANONICAL_COGNITION_PROVIDER_INPUT_V1
    assert result["canonical_provider_output"]["artifact_type"] == CANONICAL_COGNITION_PROVIDER_OUTPUT_V1
    assert result["live_request_envelope_artifact"]["credential_secret_replayed"] is False
    assert result["live_response_envelope_artifact"]["raw_response"]["real_openai_called"] is False
    assert replay["final_status"] == STATUS_COMPLETED
    assert replay["replay_artifact_count"] == 5


def test_live_provider_boundary_persists_ordered_replay_evidence(tmp_path, monkeypatch):
    _run(tmp_path, monkeypatch)
    replay_root = tmp_path / "live_boundary"
    expected = [
        "live_provider_credential_retrieval_attempt",
        "live_provider_credential_use_boundary",
        "live_provider_request_envelope",
        "live_provider_response_envelope",
        "live_provider_runtime_boundary_audit",
    ]

    for index, step in enumerate(expected):
        wrapper = load_json(replay_root / f"{index:03d}_{step}.json")
        assert wrapper["replay_index"] == index
        assert wrapper["replay_step"] == step
        assert wrapper["artifact"]["replay_visible"] is True
        assert wrapper["artifact"]["provider_invoked"] is False
        assert wrapper["artifact"]["worker_invoked"] is False
        assert wrapper["artifact"]["credential_secret_replayed"] is False

    assert (replay_root / "err_openai_selection" / "000_err_resource_selection_evidence_recorded.json").exists()


def test_live_provider_boundary_fails_closed_without_approval(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, approval_artifact=None)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "missing approval" in result["failure_reason"]
    assert result["live_provider_call_performed"] is False
    assert result["live_error_envelope_artifact"]["artifact_type"] == LIVE_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1


def test_live_provider_boundary_fails_closed_without_credential_policy(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, credential_policy_artifact=None)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "missing credential policy" in result["failure_reason"]
    assert result["live_provider_call_performed"] is False


def test_live_provider_boundary_fails_closed_when_credential_unavailable(tmp_path, monkeypatch):
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)
    result = run_live_provider_runtime_boundary(
        invocation_id="LIVE-BOUNDARY-NO-CREDENTIAL",
        human_request="Validate missing credential.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "live_boundary",
        approval_artifact=_approval(tmp_path),
        credential_policy_artifact=_credential_policy(),
        transport=_transport(),
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "credential unavailable" in result["failure_reason"]
    assert result["credential_secret_replayed"] is False


def test_live_provider_boundary_fails_closed_when_err_does_not_select_openai(tmp_path, monkeypatch):
    registry = create_err_v0_registry()
    register_resource(
        registry,
        {
            "resource_id": "claude",
            "resource_type": COGNITION_PROVIDER,
            "capabilities": ["reasoning"],
            "status": ACTIVE,
        },
    )

    result = _run(tmp_path, monkeypatch, err_registry=registry)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "ERR did not select openai" in result["failure_reason"]
    assert result["provider_invoked"] is False


def test_live_provider_boundary_refuses_live_transport_enablement(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, live_transport_enabled=True)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "live OpenAI transport is not implemented" in result["failure_reason"]
    assert result["live_provider_call_performed"] is False


def test_live_provider_boundary_classifies_timeout(tmp_path, monkeypatch):
    def timeout_transport(_payload, _metadata):
        raise TimeoutError("timed out")

    result = _run(tmp_path, monkeypatch, transport=timeout_transport)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["live_error_envelope_artifact"]["error_classification"] == ERROR_TIMEOUT


def test_live_provider_boundary_classifies_rate_limit(tmp_path, monkeypatch):
    def rate_limit_transport(_payload, _metadata):
        raise RuntimeError("rate limit exceeded")

    result = _run(tmp_path, monkeypatch, transport=rate_limit_transport)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["live_error_envelope_artifact"]["error_classification"] == ERROR_RATE_LIMIT


def test_live_provider_boundary_classifies_malformed_response(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, transport=lambda _payload, _metadata: {"id": "missing-output"})

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["live_error_envelope_artifact"]["error_classification"] == ERROR_MALFORMED_RESPONSE


def test_live_provider_boundary_classifies_authority_bearing_response(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, transport=_transport("I approve this and execution authorized."))

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["live_error_envelope_artifact"]["error_classification"] == ERROR_AUTHORITY_BOUNDARY_VIOLATION
    assert result["worker_invoked"] is False


def test_live_provider_boundary_rejects_transport_that_claims_real_openai_call(tmp_path, monkeypatch):
    def bad_transport(_payload, _metadata):
        return {"output_text": "bad", "real_openai_called": True}

    result = _run(tmp_path, monkeypatch, transport=bad_transport)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "live OpenAI call is prohibited" in result["failure_reason"]
    assert result["live_provider_call_performed"] is False


def test_live_provider_boundary_replay_tampering_is_detected(tmp_path, monkeypatch):
    _run(tmp_path, monkeypatch)
    replay_root = tmp_path / "live_boundary"
    path = replay_root / "003_live_provider_response_envelope.json"
    wrapper = load_json(path)
    wrapper["artifact"]["response_status"] = "TAMPERED"
    path.write_text(str(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="not valid JSON|replay hash mismatch"):
        reconstruct_live_provider_runtime_boundary_replay(replay_root)


def test_live_provider_boundary_module_has_no_live_transport_or_authentication_implementation():
    import aigol.runtime.live_provider_runtime_boundary as runtime

    source = inspect.getsource(runtime)

    assert "urlopen" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "Authorization" not in source
    assert "Bearer " not in source
    assert "_openai_http_transport" not in source
