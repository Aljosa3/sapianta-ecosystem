import json
from pathlib import Path
import stat

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import (
    add_provider_credential,
    assert_vault_file_permissions,
    delete_provider_credential,
    disable_provider_credential,
    provider_credential_diagnostic,
    provider_credential_history,
    retrieve_provider_credential,
    rotate_provider_credential,
    verify_provider_credential,
)
from aigol.runtime.providers.provider_config import ProviderConfig
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash


CREATED_AT = "2026-06-21T00:00:00Z"


def _approval(operation: str) -> dict:
    artifact = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_HUMAN_APPROVAL_ARTIFACT_V1",
        "operation": operation,
        "approval_status": "APPROVED",
        "approved_by": "human.operator",
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def test_vault_add_verify_and_retrieve_keep_replay_secret_free(tmp_path):
    vault_path = tmp_path / "operator-home" / ".config" / "aigol" / "provider-credentials.json"
    replay_dir = tmp_path / "replay"
    secret = "sk-test-provider-vault-secret"

    add_event = add_provider_credential(
        provider_id="openai",
        credential_value=secret,
        created_at=CREATED_AT,
        vault_path=vault_path,
        replay_dir=replay_dir / "add",
    )
    verify_event = verify_provider_credential(
        provider_id="openai",
        created_at=CREATED_AT,
        vault_path=vault_path,
        replay_dir=replay_dir / "verify",
    )
    retrieval = retrieve_provider_credential(
        provider_id="openai",
        authorization_context={"approved": True},
        vault_path=vault_path,
        allow_env_fallback=False,
        created_at=CREATED_AT,
        replay_dir=replay_dir / "retrieval",
    )

    assert retrieval["_credential_secret"] == secret
    assert add_event["credential_value_recorded"] is False
    assert verify_event["credential_value_recorded"] is False
    assert vault_path.exists()
    assert stat.S_IMODE(vault_path.stat().st_mode) == 0o600
    assert Path.cwd().resolve() not in vault_path.resolve().parents

    replay_serialized = ""
    for path in sorted(replay_dir.rglob("*.json")):
        replay_serialized += canonical_serialize(load_json(path))
    assert secret not in replay_serialized
    assert "sk-test-provider-vault-secret" not in replay_serialized
    assert "Bearer " not in replay_serialized

    vault_serialized = vault_path.read_text(encoding="utf-8")
    assert secret in vault_serialized


def test_vault_path_inside_repository_fails_closed(tmp_path):
    inside_repo = Path.cwd() / ".tmp-provider-credentials.json"
    with pytest.raises(FailClosedRuntimeError, match="outside repository"):
        add_provider_credential(
            provider_id="openai",
            credential_value="sk-test-provider-vault-secret",
            created_at=CREATED_AT,
            vault_path=inside_repo,
        )


def test_vault_file_permission_check_fails_closed(tmp_path):
    vault_path = tmp_path / "provider-credentials.json"
    add_provider_credential(
        provider_id="openai",
        credential_value="sk-test-provider-vault-secret",
        created_at=CREATED_AT,
        vault_path=vault_path,
    )
    vault_path.chmod(0o644)

    with pytest.raises(FailClosedRuntimeError, match="chmod 0600"):
        assert_vault_file_permissions(vault_path)


def test_openai_provider_config_resolves_from_vault(tmp_path, monkeypatch):
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)
    vault_path = tmp_path / "provider-credentials.json"
    add_provider_credential(
        provider_id="openai",
        credential_value="vault-openai-secret",
        created_at=CREATED_AT,
        vault_path=vault_path,
    )

    config = ProviderConfig(vault_path=str(vault_path), allow_env_fallback=False)

    assert config.credential_reference == "vault://provider/openai"
    assert config.api_key() == "vault-openai-secret"


def test_env_fallback_still_works_during_migration(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "env-openai-secret")

    config = ProviderConfig(vault_path=str(tmp_path / "missing-vault.json"), allow_env_fallback=True)

    assert config.api_key() == "env-openai-secret"


def test_disabled_credential_fails_closed_even_when_env_exists(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "env-openai-secret")
    vault_path = tmp_path / "provider-credentials.json"
    add_provider_credential(
        provider_id="openai",
        credential_value="vault-openai-secret",
        created_at=CREATED_AT,
        vault_path=vault_path,
    )
    disable_provider_credential(
        provider_id="openai",
        created_at=CREATED_AT,
        human_approval_artifact=_approval("DISABLE"),
        vault_path=vault_path,
    )

    with pytest.raises(FailClosedRuntimeError, match="credential disabled"):
        retrieve_provider_credential(provider_id="openai", vault_path=vault_path, allow_env_fallback=True)


def test_deleted_credential_fails_closed_even_when_env_exists(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "env-openai-secret")
    vault_path = tmp_path / "provider-credentials.json"
    add_provider_credential(
        provider_id="openai",
        credential_value="vault-openai-secret",
        created_at=CREATED_AT,
        vault_path=vault_path,
    )
    delete_provider_credential(
        provider_id="openai",
        created_at=CREATED_AT,
        human_approval_artifact=_approval("DELETE"),
        vault_path=vault_path,
    )

    with pytest.raises(FailClosedRuntimeError, match="credential deleted"):
        retrieve_provider_credential(provider_id="openai", vault_path=vault_path, allow_env_fallback=True)


def test_rotation_requires_approval_and_changes_safe_identifier(tmp_path):
    vault_path = tmp_path / "provider-credentials.json"
    add_provider_credential(
        provider_id="openai",
        credential_value="first-secret",
        created_at=CREATED_AT,
        vault_path=vault_path,
    )
    before = provider_credential_diagnostic(provider_id="openai", vault_path=vault_path)

    with pytest.raises(FailClosedRuntimeError, match="ROTATE approval was not approved"):
        rotate_provider_credential(
            provider_id="openai",
            credential_value="second-secret",
            created_at=CREATED_AT,
            human_approval_artifact={},
            vault_path=vault_path,
        )

    rotate_provider_credential(
        provider_id="openai",
        credential_value="second-secret",
        created_at=CREATED_AT,
        human_approval_artifact=_approval("ROTATE"),
        vault_path=vault_path,
    )
    after = provider_credential_diagnostic(provider_id="openai", vault_path=vault_path)
    history = provider_credential_history(provider_id="openai", vault_path=vault_path)

    assert before["display_identifier"] != after["display_identifier"]
    assert after["display_identifier"].startswith("...")
    assert "first-secret" not in json.dumps(after)
    assert "second-secret" not in json.dumps(history)
