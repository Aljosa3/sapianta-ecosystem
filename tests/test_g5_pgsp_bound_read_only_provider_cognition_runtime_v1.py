"""Tests for G5-02 PGSP-bound read-only provider cognition runtime."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.g5_pgsp_bound_read_only_provider_cognition_runtime import (
    AUTHORIZATION_SCOPE,
    G5_02_RUNTIME_VERSION,
    PGSP_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1,
    PGSP_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1,
    READ_ONLY_PROVIDER_COGNITION_COMPLETED,
    READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED,
    reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay,
    run_g5_pgsp_bound_read_only_provider_cognition_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_identity_boundaries import (
    COGNITION_PROVIDER,
    CREDENTIAL_CONFIGURED_INACTIVE,
    PROVIDER_REGISTERED_INACTIVE,
    TRANSLATION_WORKER,
    create_provider_credential_reference,
    create_provider_identity,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-30T00:00:00Z"
SESSION_ID = "G5-02-PGSP-SESSION-000001"


def _capability(role: str) -> list[dict]:
    return [
        {
            "capability_id": f"G5-02-CAPABILITY-{role}",
            "capability": "bounded read-only cognition",
            "capability_scope": role,
            "advisory_only": True,
            "execution_authority": False,
        }
    ]


def _provider_identity(tmp_path, *, role: str = COGNITION_PROVIDER) -> dict:
    credential = create_provider_credential_reference(
        credential_reference_id=f"G5-02-CREDENTIAL-{role}",
        credential_reference=f"vault://provider/{role.lower()}",
        credential_role=role,
        credential_lifecycle_state=CREDENTIAL_CONFIGURED_INACTIVE,
        secret_present=False,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"credential_{role.lower()}",
    )["credential_reference_artifact"]
    return create_provider_identity(
        provider_id="openai",
        external_provider_family="openai",
        model_id="gpt-governed-read-only",
        provider_role=role,
        capability_declarations=_capability(role),
        credential_reference_artifact=credential,
        activation_status=PROVIDER_REGISTERED_INACTIVE,
        replay_lineage=[
            {
                "replay_reference": f"provider_identity:{role}",
                "replay_hash": replay_hash({"role": role}),
            }
        ],
        rollback_reference=f"rollback:g5-02:{role}",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"provider_{role.lower()}",
    )["provider_identity_artifact"]


def _authorization(*, session_id: str = SESSION_ID, provider_role: str = COGNITION_PROVIDER) -> dict:
    artifact = {
        "artifact_type": "G5_02_READ_ONLY_PROVIDER_COGNITION_AUTHORIZATION_V1",
        "authorization_id": f"{session_id}:AUTHORIZATION",
        "authorization_status": "AUTHORIZED",
        "authorization_scope": AUTHORIZATION_SCOPE,
        "session_id": session_id,
        "provider_id": "openai",
        "provider_role": provider_role,
        "read_only": True,
        "cognition_only": True,
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_consumed": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "worker_invoked": False,
        "deployment_performed": False,
        "replay_visible": True,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_executor(calls: list[dict] | None = None):
    def execute(request_envelope: dict) -> dict:
        if calls is not None:
            calls.append(request_envelope)
        return {
            "output_text": "Cognition evidence: summarize replay state and recommend review. Confidence: HIGH.",
            "metadata": {"deterministic_test_provider": True},
        }

    return execute


def test_g5_02_executes_one_read_only_provider_cognition_request(tmp_path) -> None:
    calls: list[dict] = []
    result = run_g5_pgsp_bound_read_only_provider_cognition_runtime(
        session_id=SESSION_ID,
        cognition_request="Review the PGSP replay evidence and summarize risks.",
        provider_identity_artifact=_provider_identity(tmp_path),
        execution_authorization_artifact=_authorization(),
        provider_executor=_provider_executor(calls),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_02",
    )
    replay = reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay(tmp_path / "g5_02")

    assert len(calls) == 1
    assert result["runtime_version"] == G5_02_RUNTIME_VERSION
    assert result["execution_status"] == READ_ONLY_PROVIDER_COGNITION_COMPLETED
    assert result["provider_invoked"] is True
    assert result["provider_dispatch_count"] == 1
    assert result["provider_response_received"] is True
    assert result["worker_invoked"] is False
    assert result["approval_created"] is False
    assert result["authorization_created"] is False
    assert result["repository_mutated"] is False
    assert result["deployment_performed"] is False
    assert replay["execution_status"] == READ_ONLY_PROVIDER_COGNITION_COMPLETED
    assert replay["provider_dispatch_count"] == 1
    assert replay["replay_artifact_count"] == 9
    assert replay["worker_invoked"] is False
    assert replay["repository_mutated"] is False


def test_g5_02_replay_records_response_participation_review_and_uhcl_summary(tmp_path) -> None:
    run_g5_pgsp_bound_read_only_provider_cognition_runtime(
        session_id=SESSION_ID,
        cognition_request="Provide read-only cognition evidence.",
        provider_identity_artifact=_provider_identity(tmp_path),
        execution_authorization_artifact=_authorization(),
        provider_executor=_provider_executor(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_02",
    )

    response = json.loads((tmp_path / "g5_02" / "004_provider_result_envelope_recorded.json").read_text())["artifact"]
    participation = json.loads((tmp_path / "g5_02" / "005_provider_participation_evidence_recorded.json").read_text())["artifact"]
    review = json.loads((tmp_path / "g5_02" / "006_post_execution_review_recorded.json").read_text())["artifact"]
    uhcl = json.loads((tmp_path / "g5_02" / "007_uhcl_execution_summary_recorded.json").read_text())["artifact"]

    assert response["artifact_type"] == PGSP_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1
    assert participation["cognition_participation"]["participation_location"] == "OCS_LLM_COGNITION"
    assert participation["provider_usage_metric"]["status"] == "SUCCESS"
    assert review["provider_output_non_authoritative"] is True
    assert uhcl["communication_owner"] == "UHCL"
    assert uhcl["provider_output_renderable"] is True


def test_g5_02_rejects_non_cognition_provider_identity(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="provider role must be COGNITION_PROVIDER"):
        run_g5_pgsp_bound_read_only_provider_cognition_runtime(
            session_id=SESSION_ID,
            cognition_request="This must not use a translation worker identity.",
            provider_identity_artifact=_provider_identity(tmp_path, role=TRANSLATION_WORKER),
            execution_authorization_artifact=_authorization(provider_role=TRANSLATION_WORKER),
            provider_executor=_provider_executor(),
            created_at=CREATED_AT,
            replay_dir=tmp_path / "g5_02",
        )


def test_g5_02_rejects_missing_or_stale_authorization(tmp_path) -> None:
    authorization = _authorization()
    authorization["dispatch_attempt_consumed"] = True
    authorization["artifact_hash"] = replay_hash({k: v for k, v in authorization.items() if k != "artifact_hash"})

    with pytest.raises(FailClosedRuntimeError, match="fresh one-attempt"):
        run_g5_pgsp_bound_read_only_provider_cognition_runtime(
            session_id=SESSION_ID,
            cognition_request="This must not run with stale authorization.",
            provider_identity_artifact=_provider_identity(tmp_path),
            execution_authorization_artifact=authorization,
            provider_executor=_provider_executor(),
            created_at=CREATED_AT,
            replay_dir=tmp_path / "g5_02",
        )


def test_g5_02_authority_bearing_provider_output_fails_closed_with_error_envelope(tmp_path) -> None:
    def authority_provider(_request_envelope: dict) -> dict:
        return {"output_text": "I approve this. execution authorized."}

    result = run_g5_pgsp_bound_read_only_provider_cognition_runtime(
        session_id=SESSION_ID,
        cognition_request="Provider must not grant authority.",
        provider_identity_artifact=_provider_identity(tmp_path),
        execution_authorization_artifact=_authorization(),
        provider_executor=authority_provider,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_02",
    )
    error = json.loads((tmp_path / "g5_02" / "004_provider_result_envelope_recorded.json").read_text())["artifact"]
    replay = reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay(tmp_path / "g5_02")

    assert result["execution_status"] == READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED
    assert result["provider_invoked"] is True
    assert result["provider_dispatch_count"] == 1
    assert result["provider_error_recorded"] is True
    assert error["artifact_type"] == PGSP_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1
    assert "authority-bearing" in error["failure_reason"]
    assert replay["execution_status"] == READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED
    assert replay["provider_error_recorded"] is True
    assert replay["worker_invoked"] is False


def test_g5_02_replay_tampering_fails_closed(tmp_path) -> None:
    run_g5_pgsp_bound_read_only_provider_cognition_runtime(
        session_id=SESSION_ID,
        cognition_request="Record tamper-resistant replay.",
        provider_identity_artifact=_provider_identity(tmp_path),
        execution_authorization_artifact=_authorization(),
        provider_executor=_provider_executor(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_02",
    )
    path = tmp_path / "g5_02" / "008_provider_cognition_runtime_summary_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["repository_mutated"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay(tmp_path / "g5_02")
