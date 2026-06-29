"""Tests for G3-04 provider identity and credential boundaries."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_identity_boundaries import (
    COGNITION_PROVIDER,
    CREDENTIAL_CONFIGURED_INACTIVE,
    PROVIDER_IDENTITY_ARTIFACT_V1,
    PROVIDER_REGISTERED_INACTIVE,
    REPAIR_WORKER,
    TRANSLATION_WORKER,
    create_provider_credential_reference,
    create_provider_identity,
    reconstruct_provider_identity_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-29T00:00:00Z"


def _lineage(name: str) -> list[dict]:
    return [
        {
            "replay_reference": f"runtime/g3/provider-identity/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _capability(role: str) -> list[dict]:
    return [
        {
            "capability_id": f"CAPABILITY-{role}-000001",
            "capability": "advisory language model contribution",
            "capability_scope": role,
            "advisory_only": True,
            "execution_authority": False,
        }
    ]


def _credential(tmp_path, role: str, reference: str):
    return create_provider_credential_reference(
        credential_reference_id=f"CREDENTIAL-REFERENCE-{role}-000001",
        credential_reference=reference,
        credential_role=role,
        credential_lifecycle_state=CREDENTIAL_CONFIGURED_INACTIVE,
        secret_present=False,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"credential_{role.lower()}",
    )["credential_reference_artifact"]


def _provider(tmp_path, role: str, reference: str, provider_id: str):
    credential = _credential(tmp_path, role, reference)
    return create_provider_identity(
        provider_id=provider_id,
        external_provider_family="openai",
        model_id="gpt-governed-placeholder",
        provider_role=role,
        capability_declarations=_capability(role),
        credential_reference_artifact=credential,
        activation_status=PROVIDER_REGISTERED_INACTIVE,
        replay_lineage=_lineage(provider_id),
        rollback_reference=f"rollback:{provider_id}",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"provider_{provider_id}",
    )


def test_creates_role_separated_provider_identities_for_same_external_api(tmp_path) -> None:
    cognition = _provider(
        tmp_path,
        COGNITION_PROVIDER,
        "vault://provider/openai-cognition-g3-04",
        "PROVIDER-OPENAI-COGNITION-G3-04-000001",
    )["provider_identity_artifact"]
    translation = _provider(
        tmp_path,
        TRANSLATION_WORKER,
        "vault://worker/openai-translation-g3-04",
        "PROVIDER-OPENAI-TRANSLATION-G3-04-000001",
    )["provider_identity_artifact"]
    repair = _provider(
        tmp_path,
        REPAIR_WORKER,
        "vault://worker/openai-repair-g3-04",
        "PROVIDER-OPENAI-REPAIR-G3-04-000001",
    )["provider_identity_artifact"]

    assert {cognition["external_provider_family"], translation["external_provider_family"], repair["external_provider_family"]} == {
        "openai"
    }
    assert {cognition["provider_role"], translation["provider_role"], repair["provider_role"]} == {
        COGNITION_PROVIDER,
        TRANSLATION_WORKER,
        REPAIR_WORKER,
    }
    assert {cognition["credential_reference"], translation["credential_reference"], repair["credential_reference"]} == {
        "vault://provider/openai-cognition-g3-04",
        "vault://worker/openai-translation-g3-04",
        "vault://worker/openai-repair-g3-04",
    }
    assert cognition["artifact_type"] == PROVIDER_IDENTITY_ARTIFACT_V1
    assert cognition["provider_invoked"] is False
    assert cognition["provider_selection_performed"] is False
    assert cognition["credential_secret_stored"] is False

    reconstructed = reconstruct_provider_identity_replay(tmp_path / "provider_PROVIDER-OPENAI-COGNITION-G3-04-000001")
    assert reconstructed["provider_id"] == "PROVIDER-OPENAI-COGNITION-G3-04-000001"
    assert reconstructed["provider_role"] == COGNITION_PROVIDER
    assert reconstructed["credential_lifecycle_state"] == CREDENTIAL_CONFIGURED_INACTIVE
    assert reconstructed["activation_status"] == PROVIDER_REGISTERED_INACTIVE
    assert reconstructed["replay_lineage_count"] == 3


def test_credential_reference_rejects_secret_material(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="credential secret must not be replayed"):
        create_provider_credential_reference(
            credential_reference_id="CREDENTIAL-REFERENCE-SECRET-000001",
            credential_reference="sk-real-looking-secret",
            credential_role=COGNITION_PROVIDER,
            credential_lifecycle_state=CREDENTIAL_CONFIGURED_INACTIVE,
            secret_present=False,
            created_at=CREATED_AT,
            replay_dir=tmp_path / "secret",
        )


def test_provider_identity_requires_matching_credential_role(tmp_path) -> None:
    credential = _credential(tmp_path, COGNITION_PROVIDER, "vault://provider/openai-cognition-g3-04")

    with pytest.raises(FailClosedRuntimeError, match="credential role does not match provider role"):
        create_provider_identity(
            provider_id="PROVIDER-OPENAI-MISMATCH-G3-04-000001",
            external_provider_family="openai",
            model_id="gpt-governed-placeholder",
            provider_role=TRANSLATION_WORKER,
            capability_declarations=_capability(TRANSLATION_WORKER),
            credential_reference_artifact=credential,
            activation_status=PROVIDER_REGISTERED_INACTIVE,
            replay_lineage=_lineage("mismatch"),
            rollback_reference="rollback:mismatch",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "mismatch",
        )


def test_provider_identity_rejects_execution_authority_capability(tmp_path) -> None:
    credential = _credential(tmp_path, COGNITION_PROVIDER, "vault://provider/openai-cognition-g3-04")

    with pytest.raises(FailClosedRuntimeError, match="capability must not grant execution authority"):
        create_provider_identity(
            provider_id="PROVIDER-OPENAI-AUTHORITY-G3-04-000001",
            external_provider_family="openai",
            model_id="gpt-governed-placeholder",
            provider_role=COGNITION_PROVIDER,
            capability_declarations=[
                {
                    "capability_id": "CAPABILITY-AUTHORITY-000001",
                    "capability": "bad execution capability",
                    "capability_scope": COGNITION_PROVIDER,
                    "advisory_only": True,
                    "execution_authority": True,
                }
            ],
            credential_reference_artifact=credential,
            activation_status=PROVIDER_REGISTERED_INACTIVE,
            replay_lineage=_lineage("authority"),
            rollback_reference="rollback:authority",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "authority",
        )


def test_provider_identity_replay_tamper_fails_closed(tmp_path) -> None:
    _provider(
        tmp_path,
        COGNITION_PROVIDER,
        "vault://provider/openai-cognition-g3-04",
        "PROVIDER-OPENAI-TAMPER-G3-04-000001",
    )
    path = (
        tmp_path
        / "provider_PROVIDER-OPENAI-TAMPER-G3-04-000001"
        / "000_provider_identity_created.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_provider_identity_replay(tmp_path / "provider_PROVIDER-OPENAI-TAMPER-G3-04-000001")


def test_provider_identity_runtime_has_no_invocation_or_secret_surfaces() -> None:
    import aigol.runtime.provider_identity_boundaries as runtime

    source = inspect.getsource(runtime)

    assert "requests." not in source
    assert "httpx." not in source
    assert "openai." not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "provider_adapter" not in source
    assert "retrieve_provider_credential(" not in source
    assert "subprocess." not in source
    assert "os.environ" not in source
    assert "write_text(" not in source
    assert '"provider_invoked": True' not in source
    assert '"provider_selection_performed": True' not in source
    assert '"provider_request_created": True' not in source
    assert '"provider_response_received": True' not in source
    assert '"worker_invoked": True' not in source
    assert '"execution_requested": True' not in source
