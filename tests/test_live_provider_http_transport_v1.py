"""Tests for AIGOL_LIVE_PROVIDER_HTTP_TRANSPORT_V1."""

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
from aigol.runtime.live_provider_http_transport import (
    ERROR_AUTHORITY_BOUNDARY_VIOLATION,
    ERROR_MALFORMED_RESPONSE,
    ERROR_RATE_LIMIT,
    ERROR_TIMEOUT,
    LIVE_PROVIDER_HTTP_ERROR_ARTIFACT_V1,
    LIVE_PROVIDER_HTTP_REQUEST_ARTIFACT_V1,
    LIVE_PROVIDER_HTTP_RESPONSE_ARTIFACT_V1,
    LIVE_PROVIDER_HTTP_TRANSPORT_AUDIT_ARTIFACT_V1,
    MILESTONE_ID,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    reconstruct_live_provider_http_transport_replay,
    run_live_provider_http_transport,
)
from aigol.runtime.live_provider_invocation_prerequisites import (
    create_live_provider_credential_policy,
    create_live_provider_invocation_approval,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json


CREATED_AT = "2026-06-16T00:00:00+00:00"


def _approval(tmp_path: Path, **overrides) -> dict:
    args = {
        "approval_id": "HTTP-TRANSPORT-APPROVAL-000001",
        "provider_id": OPENAI_PROVIDER_ID,
        "required_capability": "reasoning",
        "runtime_path": "AIGOL_LIVE_PROVIDER_HTTP_TRANSPORT_V1",
        "replay_dir_reference": str(tmp_path / "http_transport"),
        "approved_by": "human.operator",
        "created_at": CREATED_AT,
        "expires_at": "2026-06-16T01:00:00+00:00",
    }
    args.update(overrides)
    return create_live_provider_invocation_approval(**args)


def _credential_policy(**overrides) -> dict:
    args = {
        "policy_id": "HTTP-TRANSPORT-CREDENTIAL-POLICY-000001",
        "provider_id": OPENAI_PROVIDER_ID,
        "credential_reference": "env:AIGOL_OPENAI_API_KEY",
        "created_at": CREATED_AT,
    }
    args.update(overrides)
    return create_live_provider_credential_policy(**args)


def _transport(response_text: str = "HTTP transport mock response captured as cognition."):
    def call(request: dict, metadata: dict) -> dict:
        assert request["method"] == "POST"
        assert request["headers"]["Authorization"] == "<redacted>"
        assert request["body"]["stream"] is False
        assert metadata["provider_id"] == OPENAI_PROVIDER_ID
        assert metadata["authorization_header_redacted"] is True
        assert metadata["credential_secret_replayed"] is False
        assert metadata["live_http_dispatch_performed"] is False
        return {
            "id": "deterministic-http-transport-response",
            "status_code": 200,
            "output_text": response_text,
            "real_openai_called": False,
        }

    return call


def _run(tmp_path: Path, **overrides) -> dict:
    args = {
        "transport_id": "HTTP-TRANSPORT-INVOCATION-000001",
        "human_request": "Validate the governed HTTP transport boundary.",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "http_transport",
        "approval_artifact": _approval(tmp_path),
        "credential_policy_artifact": _credential_policy(),
        "transport": _transport(),
    }
    args.update(overrides)
    return run_live_provider_http_transport(**args)


def test_http_transport_records_success_with_injected_transport_without_live_call(tmp_path):
    result = _run(tmp_path)
    replay = reconstruct_live_provider_http_transport_replay(tmp_path / "http_transport")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_status"] == STATUS_COMPLETED
    assert result["live_http_dispatch_performed"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["governance_modified"] is False
    assert result["replay_modified"] is False
    assert result["credential_secret_replayed"] is False
    assert result["authorization_header_replayed"] is False
    assert result["http_request_artifact"]["artifact_type"] == LIVE_PROVIDER_HTTP_REQUEST_ARTIFACT_V1
    assert result["http_response_artifact"]["artifact_type"] == LIVE_PROVIDER_HTTP_RESPONSE_ARTIFACT_V1
    assert result["http_transport_audit_artifact"]["artifact_type"] == LIVE_PROVIDER_HTTP_TRANSPORT_AUDIT_ARTIFACT_V1
    assert result["http_request_artifact"]["http_request"]["headers"]["Authorization"] == "<redacted>"
    assert result["http_response_artifact"]["raw_response"]["real_openai_called"] is False
    assert replay["final_status"] == STATUS_COMPLETED
    assert replay["replay_artifact_count"] == 3


def test_http_transport_persists_ordered_replay_evidence(tmp_path):
    _run(tmp_path)
    replay_root = tmp_path / "http_transport"
    expected = [
        "live_provider_http_request",
        "live_provider_http_response",
        "live_provider_http_transport_audit",
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


def test_http_transport_replay_artifacts_do_not_contain_secret_material(tmp_path):
    _run(tmp_path)
    serialized = "".join(
        canonical_serialize(load_json(path))
        for path in sorted((tmp_path / "http_transport").glob("*.json"))
    )

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
    assert "env:AIGOL_OPENAI_API_KEY" not in serialized


def test_http_transport_fails_closed_without_injected_transport_by_default(tmp_path):
    result = _run(tmp_path, transport=None)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "injected transport is required" in result["failure_reason"]
    assert result["live_http_dispatch_performed"] is False
    assert result["http_error_artifact"]["artifact_type"] == LIVE_PROVIDER_HTTP_ERROR_ARTIFACT_V1


def test_http_transport_refuses_live_http_enablement(tmp_path):
    result = _run(tmp_path, live_http_enabled=True)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "live HTTP dispatch is not enabled" in result["failure_reason"]
    assert result["provider_invoked"] is False


def test_http_transport_fails_closed_without_approval(tmp_path):
    result = _run(tmp_path, approval_artifact=None)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "missing approval" in result["failure_reason"]
    assert result["provider_invoked"] is False


def test_http_transport_fails_closed_without_credential_policy(tmp_path):
    result = _run(tmp_path, credential_policy_artifact=None)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "missing credential policy" in result["failure_reason"]
    assert result["credential_secret_replayed"] is False


def test_http_transport_fails_closed_when_err_does_not_select_openai(tmp_path):
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

    result = _run(tmp_path, err_registry=registry)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "ERR did not select openai" in result["failure_reason"]
    assert result["provider_invoked"] is False


def test_http_transport_classifies_timeout(tmp_path):
    def timeout_transport(_request, _metadata):
        raise TimeoutError("timed out")

    result = _run(tmp_path, transport=timeout_transport)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["http_error_artifact"]["error_classification"] == ERROR_TIMEOUT


def test_http_transport_classifies_rate_limit_exception(tmp_path):
    def rate_limit_transport(_request, _metadata):
        raise RuntimeError("rate limit exceeded")

    result = _run(tmp_path, transport=rate_limit_transport)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["http_error_artifact"]["error_classification"] == ERROR_RATE_LIMIT


def test_http_transport_classifies_rate_limit_response(tmp_path):
    result = _run(
        tmp_path,
        transport=lambda _request, _metadata: {
            "status_code": 429,
            "output_text": "rate limited",
            "real_openai_called": False,
        },
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["http_error_artifact"]["error_classification"] == ERROR_RATE_LIMIT


def test_http_transport_classifies_malformed_response(tmp_path):
    result = _run(tmp_path, transport=lambda _request, _metadata: {"id": "missing-output"})

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["http_error_artifact"]["error_classification"] == ERROR_MALFORMED_RESPONSE


def test_http_transport_classifies_authority_bearing_response(tmp_path):
    result = _run(tmp_path, transport=_transport("I approve this and execution authorized."))

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["http_error_artifact"]["error_classification"] == ERROR_AUTHORITY_BOUNDARY_VIOLATION
    assert result["worker_invoked"] is False


def test_http_transport_rejects_transport_that_claims_real_openai_call(tmp_path):
    def bad_transport(_request, _metadata):
        return {"status_code": 200, "output_text": "bad", "real_openai_called": True}

    result = _run(tmp_path, transport=bad_transport)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "live OpenAI call is prohibited" in result["failure_reason"]
    assert result["live_http_dispatch_performed"] is False


def test_http_transport_replay_tampering_is_detected(tmp_path):
    _run(tmp_path)
    replay_root = tmp_path / "http_transport"
    path = replay_root / "001_live_provider_http_response.json"
    wrapper = load_json(path)
    wrapper["artifact"]["response_status"] = "TAMPERED"
    path.write_text(str(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="not valid JSON|replay hash mismatch"):
        reconstruct_live_provider_http_transport_replay(replay_root)


def test_http_transport_module_has_no_default_network_client():
    import aigol.runtime.live_provider_http_transport as runtime

    source = inspect.getsource(runtime)

    assert "urlopen" not in source
    assert "requests" not in source
    assert "httpx" not in source
