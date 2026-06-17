"""Tests for AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.first_live_provider_activation_package_instantiation import (
    instantiate_first_live_provider_activation_package,
)
from aigol.runtime.first_live_provider_dispatch_authorization_instantiation import (
    instantiate_first_live_provider_dispatch_authorization,
)
from aigol.runtime.first_live_provider_operator_entrypoint import (
    FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_REQUEST_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_RESULT_ARTIFACT_V1,
    MILESTONE_ID,
    STATUS_FAILED_CLOSED,
    STATUS_OPERATOR_DISPATCH_COMPLETED,
    reconstruct_first_live_provider_operator_entrypoint_replay,
    run_first_live_provider_operator_entrypoint,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


CREATED_AT = "2026-06-17T00:00:00+00:00"
EXPIRES_AT = "2026-06-17T01:00:00+00:00"


def _transport(response_text: str = "Findings: operator entrypoint dispatch captured. Confidence: HIGH"):
    def call(payload: dict, metadata: dict) -> dict:
        assert payload["stream"] is False
        assert metadata["provider_id"] == "openai"
        assert metadata["credential_secret_replayed"] is False
        return {
            "id": "operator-entrypoint-response",
            "status_code": 200,
            "output_text": response_text,
            "real_openai_called": False,
        }

    return call


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


def _run(tmp_path: Path, monkeypatch, **overrides) -> dict:
    _prepare_authorization(tmp_path)
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")
    args = {
        "operator_request_id": "FIRST-LIVE-PROVIDER-OPERATOR-DISPATCH-000001",
        "operator_id": "human.operator",
        "human_request": "Validate one governed OpenAI dispatch attempt.",
        "created_at": CREATED_AT,
        "activation_package_replay_dir": tmp_path / "activation",
        "dispatch_authorization_replay_dir": tmp_path / "dispatch_authorization",
        "execution_replay_dir": tmp_path / "execution",
        "operator_replay_dir": tmp_path / "operator_entrypoint",
        "transport": _transport(),
        "confirm_dispatch": True,
    }
    args.update(overrides)
    return run_first_live_provider_operator_entrypoint(**args)


def test_operator_entrypoint_invokes_execution_runtime_and_returns_replay_location(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch)
    replay = reconstruct_first_live_provider_operator_entrypoint_replay(tmp_path / "operator_entrypoint")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_status"] == STATUS_OPERATOR_DISPATCH_COMPLETED
    assert result["execution_capture"]["final_status"] == "DISPATCH_EXECUTION_COMPLETED"
    assert result["execution_replay_reference"] == str(tmp_path / "execution")
    assert result["operator_replay_reference"] == str(tmp_path / "operator_entrypoint")
    assert result["operator_dispatch_request_artifact"]["artifact_type"] == (
        FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_REQUEST_ARTIFACT_V1
    )
    assert result["operator_dispatch_result_artifact"]["artifact_type"] == (
        FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_RESULT_ARTIFACT_V1
    )
    assert result["credential_secret_replayed"] is False
    assert result["authorization_header_replayed"] is False
    assert result["worker_invoked"] is False
    assert result["governance_modified"] is False
    assert result["replay_modified"] is False
    assert replay["final_status"] == "DISPATCH_EXECUTION_COMPLETED"
    assert replay["execution_replay_reference"] == str(tmp_path / "execution")
    assert (tmp_path / "execution" / "007_first_live_provider_dispatch_execution_packet.json").exists()


def test_operator_entrypoint_records_ordered_replay(tmp_path, monkeypatch):
    _run(tmp_path, monkeypatch)
    expected = (
        "first_live_provider_operator_dispatch_request",
        "first_live_provider_operator_dispatch_result",
    )

    for index, step in enumerate(expected):
        wrapper = load_json(tmp_path / "operator_entrypoint" / f"{index:03d}_{step}.json")
        assert wrapper["replay_index"] == index
        assert wrapper["replay_step"] == step
        assert wrapper["artifact"]["replay_visible"] is True
        assert wrapper["artifact"]["credential_secret_replayed"] is False
        assert wrapper["artifact"]["worker_invoked"] is False


def test_operator_entrypoint_does_not_replay_secret_material(tmp_path, monkeypatch):
    _run(tmp_path, monkeypatch)
    serialized = "".join(
        canonical_serialize(load_json(path)) for path in sorted((tmp_path / "operator_entrypoint").glob("*.json"))
    )
    serialized += "".join(canonical_serialize(load_json(path)) for path in sorted((tmp_path / "execution").glob("*.json")))

    assert "test-live-openai-secret" not in serialized
    assert "sk-" not in serialized
    assert "Bearer " not in serialized


def test_operator_entrypoint_fails_closed_without_operator_confirmation(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, confirm_dispatch=False)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "operator confirmation missing" in result["failure_reason"]
    assert result["execution_capture"] is None
    assert not (tmp_path / "execution" / "007_first_live_provider_dispatch_execution_packet.json").exists()


def test_operator_entrypoint_fails_closed_without_credential(tmp_path, monkeypatch):
    _prepare_authorization(tmp_path)
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)

    result = run_first_live_provider_operator_entrypoint(
        operator_request_id="FIRST-LIVE-PROVIDER-OPERATOR-DISPATCH-000001",
        operator_id="human.operator",
        human_request="Validate one governed OpenAI dispatch attempt.",
        created_at=CREATED_AT,
        activation_package_replay_dir=tmp_path / "activation",
        dispatch_authorization_replay_dir=tmp_path / "dispatch_authorization",
        execution_replay_dir=tmp_path / "execution",
        operator_replay_dir=tmp_path / "operator_entrypoint",
        transport=_transport(),
        confirm_dispatch=True,
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "credential unavailable" in result["failure_reason"]
    assert result["execution_capture"] is None


def test_operator_entrypoint_refuses_reused_operator_replay(tmp_path, monkeypatch):
    _prepare_authorization(tmp_path)
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")
    args = {
        "operator_request_id": "FIRST-LIVE-PROVIDER-OPERATOR-DISPATCH-000001",
        "operator_id": "human.operator",
        "human_request": "Validate one governed OpenAI dispatch attempt.",
        "created_at": CREATED_AT,
        "activation_package_replay_dir": tmp_path / "activation",
        "dispatch_authorization_replay_dir": tmp_path / "dispatch_authorization",
        "execution_replay_dir": tmp_path / "execution",
        "operator_replay_dir": tmp_path / "operator_entrypoint",
        "transport": _transport(),
        "confirm_dispatch": True,
    }
    run_first_live_provider_operator_entrypoint(**args)

    result = run_first_live_provider_operator_entrypoint(**args)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "replay artifact already exists" in result["failure_reason"]
