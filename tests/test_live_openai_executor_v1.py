"""Tests for AIGOL_LIVE_OPENAI_EXECUTOR_V1."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from urllib import error, request

import pytest

from aigol.runtime.first_live_provider_activation_package_instantiation import (
    instantiate_first_live_provider_activation_package,
)
from aigol.runtime.first_live_provider_dispatch_authorization_instantiation import (
    instantiate_first_live_provider_dispatch_authorization,
)
from aigol.runtime.first_live_provider_operator_entrypoint import run_first_live_provider_operator_entrypoint
from aigol.runtime.live_openai_executor import (
    MILESTONE_ID,
    create_governed_live_openai_executor,
)
from aigol.runtime.llm_cognition_provider_runtime import OPENAI_RESPONSES_ENDPOINT
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json


CREATED_AT = "2026-06-17T00:00:00+00:00"
EXPIRES_AT = "2026-06-17T01:00:00+00:00"


class _FakeHTTPResponse:
    status = 200

    def __init__(self, body: dict) -> None:
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False

    def read(self) -> bytes:
        return self._body


def _metadata(secret: str = "test-live-openai-secret") -> dict:
    return {
        "provider_id": "openai",
        "timeout_seconds": 20,
        "credential_secret_replayed": False,
        "_credential_secret": secret,
    }


def _payload() -> dict:
    return {
        "model": "gpt-5.1",
        "input": "Produce a bounded cognition-only response.",
        "stream": False,
    }


def _prepare_authorization(tmp_path: Path) -> None:
    activation = instantiate_first_live_provider_activation_package(
        package_id="FIRST-LIVE-PROVIDER-ACTIVATION-000001",
        human_request="Validate one governed OpenAI dispatch attempt.",
        required_capability="reasoning",
        approved_by="human.operator",
        created_at=CREATED_AT,
        expires_at=EXPIRES_AT,
        replay_dir=tmp_path / "activation",
    )
    dispatch = instantiate_first_live_provider_dispatch_authorization(
        dispatch_authorization_id="FIRST-LIVE-PROVIDER-DISPATCH-AUTH-000001",
        activation_package_replay_dir=tmp_path / "activation",
        replay_dir=tmp_path / "dispatch_authorization",
        created_at=CREATED_AT,
        expires_at=EXPIRES_AT,
    )
    assert activation["final_status"] == "ACTIVATION_PACKAGE_INSTANTIATED_PRE_DISPATCH"
    assert dispatch["authorization_status"] == "DISPATCH_AUTHORIZED"


def test_live_openai_executor_constructs_https_request_and_returns_secret_free_response():
    captured: dict = {}

    def opener(http_request: request.Request, timeout: int):
        captured["url"] = http_request.full_url
        captured["timeout"] = timeout
        captured["authorization"] = http_request.get_header("Authorization")
        captured["content_type"] = http_request.get_header("Content-type")
        captured["payload"] = json.loads(http_request.data.decode("utf-8"))
        return _FakeHTTPResponse(
            {
                "id": "resp_live_executor_1",
                "output_text": "Findings: live executor response captured. Confidence: HIGH",
            }
        )

    executor = create_governed_live_openai_executor(opener=opener)
    result = executor(_payload(), _metadata())

    assert MILESTONE_ID == "AIGOL_LIVE_OPENAI_EXECUTOR_V1"
    assert executor.aigol_governed_live_openai_executor_v1 is True
    assert captured["url"] == OPENAI_RESPONSES_ENDPOINT
    assert captured["timeout"] == 20
    assert captured["authorization"] == "Bearer test-live-openai-secret"
    assert captured["content_type"] == "application/json"
    assert captured["payload"] == _payload()
    assert result["status_code"] == 200
    assert result["output_text"] == "Findings: live executor response captured. Confidence: HIGH"
    assert result["openai_response_id"] == "resp_live_executor_1"
    assert result["real_openai_called"] is True
    assert result["live_provider_call_performed"] is True
    assert result["credential_secret_replayed"] is False
    assert result["authorization_header_replayed"] is False
    assert "test-live-openai-secret" not in canonical_serialize(result)
    assert "Bearer " not in canonical_serialize(result)


def test_live_openai_executor_extracts_responses_api_output_content():
    def opener(_http_request: request.Request, _timeout: int):
        return _FakeHTTPResponse(
            {
                "id": "resp_nested",
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": "Nested response text captured.",
                            }
                        ]
                    }
                ],
            }
        )

    result = create_governed_live_openai_executor(opener=opener)(_payload(), _metadata())

    assert result["output_text"] == "Nested response text captured."
    assert result["credential_secret_replayed"] is False


def test_live_openai_executor_fails_closed_on_rate_limit():
    def opener(http_request: request.Request, _timeout: int):
        raise error.HTTPError(http_request.full_url, 429, "Too Many Requests", hdrs=None, fp=None)

    executor = create_governed_live_openai_executor(opener=opener)

    with pytest.raises(FailClosedRuntimeError, match="rate limit"):
        executor(_payload(), _metadata())


def test_live_openai_executor_fails_closed_on_timeout():
    def opener(_http_request: request.Request, _timeout: int):
        raise socket.timeout("timed out")

    executor = create_governed_live_openai_executor(opener=opener)

    with pytest.raises(FailClosedRuntimeError, match="timeout"):
        executor(_payload(), _metadata())


def test_live_openai_executor_fails_closed_on_malformed_response():
    class BadResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, _exc_type, _exc, _traceback):
            return False

        def read(self) -> bytes:
            return b"not-json"

    executor = create_governed_live_openai_executor(opener=lambda _request, _timeout: BadResponse())

    with pytest.raises(FailClosedRuntimeError, match="malformed response"):
        executor(_payload(), _metadata())


def test_operator_entrypoint_executes_through_governed_live_openai_executor_without_secret_replay(
    tmp_path,
    monkeypatch,
):
    captured: dict = {}

    def opener(http_request: request.Request, timeout: int):
        captured["url"] = http_request.full_url
        captured["timeout"] = timeout
        captured["authorization"] = http_request.get_header("Authorization")
        captured["payload"] = json.loads(http_request.data.decode("utf-8"))
        return _FakeHTTPResponse(
            {
                "id": "resp_operator_live_executor",
                "output_text": "Findings: governed OpenAI dispatch captured. Confidence: HIGH",
            }
        )

    _prepare_authorization(tmp_path)
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")

    result = run_first_live_provider_operator_entrypoint(
        operator_request_id="FIRST-LIVE-PROVIDER-OPERATOR-DISPATCH-000001",
        operator_id="human.operator",
        human_request="Validate one governed OpenAI dispatch attempt.",
        created_at=CREATED_AT,
        activation_package_replay_dir=tmp_path / "activation",
        dispatch_authorization_replay_dir=tmp_path / "dispatch_authorization",
        execution_replay_dir=tmp_path / "execution",
        operator_replay_dir=tmp_path / "operator_entrypoint",
        transport=create_governed_live_openai_executor(opener=opener),
        confirm_dispatch=True,
        live_transport_enabled=True,
    )

    assert result["final_status"] == "OPERATOR_DISPATCH_COMPLETED"
    assert result["execution_capture"]["final_status"] == "DISPATCH_EXECUTION_COMPLETED"
    assert result["execution_capture"]["live_transport_execution_evidence_artifact"][
        "live_provider_call_performed"
    ] is True
    assert result["execution_capture"]["live_transport_execution_evidence_artifact"][
        "deterministic_or_injected_transport_used"
    ] is False
    assert result["execution_capture"]["llm_cognition_artifact"]["provider_invoked"] is True
    assert captured["url"] == OPENAI_RESPONSES_ENDPOINT
    assert captured["authorization"] == "Bearer test-live-openai-secret"
    assert captured["payload"]["stream"] is False

    boundary_audit = load_json(
        tmp_path
        / "execution"
        / "live_provider_boundary"
        / "004_live_provider_runtime_boundary_audit.json"
    )["artifact"]
    assert boundary_audit["live_provider_call_performed"] is True
    assert boundary_audit["provider_invoked"] is True
    assert boundary_audit["worker_invoked"] is False
    assert boundary_audit["err_remained_passive"] is True

    replay_text = ""
    for replay_root in (
        tmp_path / "operator_entrypoint",
        tmp_path / "execution",
        tmp_path / "execution" / "live_provider_boundary",
    ):
        replay_text += "".join(canonical_serialize(load_json(path)) for path in sorted(replay_root.glob("*.json")))

    assert "test-live-openai-secret" not in replay_text
    assert "Bearer " not in replay_text
    assert "sk-" not in replay_text


def test_live_boundary_still_fails_closed_when_enabled_without_governed_executor(tmp_path, monkeypatch):
    _prepare_authorization(tmp_path)
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")

    def unmarked_transport(_payload: dict, _metadata: dict) -> dict:
        return {
            "id": "unmarked",
            "output_text": "This transport must not be accepted for live dispatch.",
            "real_openai_called": True,
        }

    result = run_first_live_provider_operator_entrypoint(
        operator_request_id="FIRST-LIVE-PROVIDER-OPERATOR-DISPATCH-000001",
        operator_id="human.operator",
        human_request="Validate one governed OpenAI dispatch attempt.",
        created_at=CREATED_AT,
        activation_package_replay_dir=tmp_path / "activation",
        dispatch_authorization_replay_dir=tmp_path / "dispatch_authorization",
        execution_replay_dir=tmp_path / "execution",
        operator_replay_dir=tmp_path / "operator_entrypoint",
        transport=unmarked_transport,
        confirm_dispatch=True,
        live_transport_enabled=True,
    )

    assert result["final_status"] == "FAILED_CLOSED"
    assert "live OpenAI transport is not implemented" in result["failure_reason"]
    assert result["execution_capture"]["live_transport_execution_evidence_artifact"][
        "live_provider_call_performed"
    ] is False
