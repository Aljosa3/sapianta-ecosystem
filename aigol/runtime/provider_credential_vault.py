"""Provider credential vault runtime for AIGOL_PROVIDER_CREDENTIAL_VAULT_V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import os
import secrets
import stat
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_CREDENTIAL_VAULT_V1"
DEFAULT_VAULT_PATH = Path.home() / ".config" / "aigol" / "provider-credentials.json"

PROVIDER_CREDENTIAL_VAULT_EVENT_ARTIFACT_V1 = "PROVIDER_CREDENTIAL_VAULT_EVENT_ARTIFACT_V1"
PROVIDER_CREDENTIAL_VAULT_DIAGNOSTIC_ARTIFACT_V1 = "PROVIDER_CREDENTIAL_VAULT_DIAGNOSTIC_ARTIFACT_V1"
PROVIDER_CREDENTIAL_VAULT_RETRIEVAL_ATTEMPT_ARTIFACT_V1 = (
    "PROVIDER_CREDENTIAL_VAULT_RETRIEVAL_ATTEMPT_ARTIFACT_V1"
)

ADD = "ADD"
VERIFY = "VERIFY"
ROTATE = "ROTATE"
DISABLE = "DISABLE"
DELETE = "DELETE"
REPLACE = "REPLACE"
SHOW = "SHOW"
APPROVAL_REQUIRED_OPERATIONS = {ROTATE, DISABLE, DELETE, REPLACE}

PROVIDER_REFERENCES = {
    "openai": "vault://provider/openai",
    "claude": "vault://provider/claude",
    "gemini": "vault://provider/gemini",
    "mistral": "vault://provider/mistral",
}
ENV_FALLBACKS = {
    "openai": "AIGOL_OPENAI_API_KEY",
    "claude": "AIGOL_ANTHROPIC_API_KEY",
    "gemini": "AIGOL_GEMINI_API_KEY",
    "mistral": "AIGOL_MISTRAL_API_KEY",
}
SECRET_MARKERS = ("sk-", "Bearer ", "operator-safe-present-marker", "test-live-openai-secret")


def add_provider_credential(
    *,
    provider_id: str,
    credential_value: str,
    created_at: str,
    vault_path: str | Path = DEFAULT_VAULT_PATH,
    replay_dir: str | Path | None = None,
    human_approval_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provider = _provider_id(provider_id)
    value = _credential_value(credential_value)
    vault = _load_vault(vault_path)
    operation = REPLACE if provider in vault["records"] else ADD
    if operation == REPLACE:
        _require_human_approval(operation, human_approval_artifact)
    generation_id = _new_generation_id()
    vault["records"][provider] = {
        "provider_id": provider,
        "credential_reference": PROVIDER_REFERENCES[provider],
        "credential_value": value,
        "credential_enabled": True,
        "generation_id": generation_id,
        "created_at": created_at,
        "last_verified": None,
        "last_rotated": None,
        "last_used": None,
    }
    _append_history(
        vault,
        provider_id=provider,
        operation=operation,
        created_at=created_at,
        generation_id=generation_id,
        human_approval_recorded=human_approval_artifact is not None,
    )
    _write_vault(vault_path, vault)
    return _record_event(
        operation=operation,
        provider_id=provider,
        record=vault["records"][provider],
        created_at=created_at,
        replay_dir=replay_dir,
        human_approval_artifact=human_approval_artifact,
    )


def verify_provider_credential(
    *,
    provider_id: str,
    created_at: str,
    vault_path: str | Path = DEFAULT_VAULT_PATH,
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    provider = _provider_id(provider_id)
    vault = _load_vault(vault_path)
    record = vault["records"].get(provider)
    if record is not None:
        record["last_verified"] = created_at
        _append_history(
            vault,
            provider_id=provider,
            operation=VERIFY,
            created_at=created_at,
            generation_id=record.get("generation_id"),
            human_approval_recorded=False,
        )
        _write_vault(vault_path, vault)
    return _record_event(
        operation=VERIFY,
        provider_id=provider,
        record=record,
        created_at=created_at,
        replay_dir=replay_dir,
        human_approval_artifact=None,
    )


def rotate_provider_credential(
    *,
    provider_id: str,
    credential_value: str,
    created_at: str,
    human_approval_artifact: dict[str, Any],
    vault_path: str | Path = DEFAULT_VAULT_PATH,
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    provider = _provider_id(provider_id)
    _require_human_approval(ROTATE, human_approval_artifact)
    value = _credential_value(credential_value)
    vault = _load_vault(vault_path)
    record = _enabled_record(vault, provider)
    generation_id = _new_generation_id()
    record["credential_value"] = value
    record["credential_enabled"] = True
    record["generation_id"] = generation_id
    record["last_rotated"] = created_at
    _append_history(
        vault,
        provider_id=provider,
        operation=ROTATE,
        created_at=created_at,
        generation_id=generation_id,
        human_approval_recorded=True,
    )
    _write_vault(vault_path, vault)
    return _record_event(
        operation=ROTATE,
        provider_id=provider,
        record=record,
        created_at=created_at,
        replay_dir=replay_dir,
        human_approval_artifact=human_approval_artifact,
    )


def disable_provider_credential(
    *,
    provider_id: str,
    created_at: str,
    human_approval_artifact: dict[str, Any],
    vault_path: str | Path = DEFAULT_VAULT_PATH,
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    provider = _provider_id(provider_id)
    _require_human_approval(DISABLE, human_approval_artifact)
    vault = _load_vault(vault_path)
    record = _existing_record(vault, provider)
    record["credential_enabled"] = False
    _append_history(
        vault,
        provider_id=provider,
        operation=DISABLE,
        created_at=created_at,
        generation_id=record.get("generation_id"),
        human_approval_recorded=True,
    )
    _write_vault(vault_path, vault)
    return _record_event(
        operation=DISABLE,
        provider_id=provider,
        record=record,
        created_at=created_at,
        replay_dir=replay_dir,
        human_approval_artifact=human_approval_artifact,
    )


def delete_provider_credential(
    *,
    provider_id: str,
    created_at: str,
    human_approval_artifact: dict[str, Any],
    vault_path: str | Path = DEFAULT_VAULT_PATH,
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    provider = _provider_id(provider_id)
    _require_human_approval(DELETE, human_approval_artifact)
    vault = _load_vault(vault_path)
    record = _existing_record(vault, provider)
    safe_record = deepcopy(record)
    vault["records"].pop(provider, None)
    _append_history(
        vault,
        provider_id=provider,
        operation=DELETE,
        created_at=created_at,
        generation_id=record.get("generation_id"),
        human_approval_recorded=True,
    )
    _write_vault(vault_path, vault)
    safe_record["credential_enabled"] = False
    return _record_event(
        operation=DELETE,
        provider_id=provider,
        record=safe_record,
        created_at=created_at,
        replay_dir=replay_dir,
        human_approval_artifact=human_approval_artifact,
        credential_present=False,
    )


def provider_credential_diagnostic(
    *,
    provider_id: str,
    vault_path: str | Path = DEFAULT_VAULT_PATH,
) -> dict[str, Any]:
    provider = _provider_id(provider_id)
    vault = _load_vault(vault_path)
    record = vault["records"].get(provider)
    return _diagnostic(provider_id=provider, record=record)


def provider_credential_history(
    *,
    provider_id: str,
    vault_path: str | Path = DEFAULT_VAULT_PATH,
) -> dict[str, Any]:
    provider = _provider_id(provider_id)
    vault = _load_vault(vault_path)
    history = [item for item in vault.get("history", []) if item.get("provider_id") == provider]
    artifact = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_HISTORY_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "provider_id": provider,
        "credential_reference": PROVIDER_REFERENCES[provider],
        "history": deepcopy(history),
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "replay_safe": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_secret_safe(artifact)
    return artifact


def retrieve_provider_credential(
    *,
    provider_id: str,
    authorization_context: dict[str, Any] | None = None,
    vault_path: str | Path = DEFAULT_VAULT_PATH,
    allow_env_fallback: bool = True,
    created_at: str | None = None,
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    provider = _provider_id(provider_id)
    source = PROVIDER_REFERENCES[provider]
    secret_value = None
    diagnostic: dict[str, Any]
    try:
        vault = _load_vault(vault_path)
        record = vault["records"].get(provider)
        if record is None:
            if _provider_deleted(vault, provider):
                raise FailClosedRuntimeError("provider credential vault failed closed: credential deleted")
            raise _MissingVaultCredential("provider credential vault missing credential")
        if not isinstance(record, dict):
            raise FailClosedRuntimeError("provider credential vault failed closed: malformed credential record")
        if record.get("credential_enabled") is not True:
            raise FailClosedRuntimeError("provider credential vault failed closed: credential disabled")
        if not isinstance(record.get("credential_value"), str) or not record.get("credential_value", "").strip():
            raise FailClosedRuntimeError("provider credential vault failed closed: credential unavailable")
        secret_value = _credential_value(record.get("credential_value"))
        record["last_used"] = created_at
        _write_vault(vault_path, vault)
        diagnostic = _diagnostic(provider_id=provider, record=record)
    except _MissingVaultCredential:
        if not allow_env_fallback:
            raise FailClosedRuntimeError("provider credential vault failed closed: credential unavailable")
        env_name = ENV_FALLBACKS[provider]
        env_secret = os.environ.get(env_name)
        if not isinstance(env_secret, str) or not env_secret.strip():
            raise FailClosedRuntimeError("provider credential vault failed closed: credential unavailable")
        source = f"env:{env_name}"
        secret_value = env_secret.strip()
        diagnostic = {
            "provider_id": provider,
            "credential_source": source,
            "credential_reference": PROVIDER_REFERENCES[provider],
            "credential_present": True,
            "credential_enabled": True,
            "display_identifier": _display_identifier_from_secret(secret_value),
            "last_verified": None,
            "last_rotated": None,
            "last_used": created_at,
            "credential_value_recorded": False,
            "credential_hash_recorded": False,
            "authorization_header_recorded": False,
            "replay_safe": True,
        }
    except FailClosedRuntimeError:
        raise
    artifact = {
        "artifact_type": PROVIDER_CREDENTIAL_VAULT_RETRIEVAL_ATTEMPT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "provider_id": provider,
        "credential_reference": PROVIDER_REFERENCES[provider],
        "credential_source": source,
        "authorization_context_recorded": authorization_context is not None,
        "retrieval_attempted": True,
        "credential_present": True,
        "credential_enabled": True,
        "display_identifier": diagnostic["display_identifier"],
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "authorization_header_recorded": False,
        "created_at": created_at,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_secret_safe(artifact)
    if replay_dir is not None:
        write_json_immutable(Path(replay_dir) / "000_provider_credential_vault_retrieval_attempt.json", artifact)
    return {
        "provider_id": provider,
        "credential_reference": PROVIDER_REFERENCES[provider],
        "credential_source": source,
        "_credential_secret": secret_value,
        "diagnostic": diagnostic,
        "retrieval_artifact": artifact,
    }


def resolve_provider_credential_reference(
    *,
    credential_reference: str,
    authorization_context: dict[str, Any] | None = None,
    vault_path: str | Path = DEFAULT_VAULT_PATH,
    allow_env_fallback: bool = True,
    created_at: str | None = None,
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    if credential_reference.startswith("vault://provider/"):
        provider = credential_reference.removeprefix("vault://provider/")
        return retrieve_provider_credential(
            provider_id=provider,
            authorization_context=authorization_context,
            vault_path=vault_path,
            allow_env_fallback=allow_env_fallback,
            created_at=created_at,
            replay_dir=replay_dir,
        )
    if credential_reference == "env:AIGOL_OPENAI_API_KEY" and allow_env_fallback:
        return retrieve_provider_credential(
            provider_id="openai",
            authorization_context=authorization_context,
            vault_path=vault_path,
            allow_env_fallback=True,
            created_at=created_at,
            replay_dir=replay_dir,
        )
    raise FailClosedRuntimeError("provider credential vault failed closed: unsupported credential reference")


def assert_vault_file_permissions(vault_path: str | Path = DEFAULT_VAULT_PATH) -> None:
    path = Path(vault_path).expanduser()
    if not path.exists():
        return
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode != 0o600:
        raise FailClosedRuntimeError("provider credential vault failed closed: vault file must have chmod 0600")


def _record_event(
    *,
    operation: str,
    provider_id: str,
    record: dict[str, Any] | None,
    created_at: str,
    replay_dir: str | Path | None,
    human_approval_artifact: dict[str, Any] | None,
    credential_present: bool | None = None,
) -> dict[str, Any]:
    diagnostic = _diagnostic(provider_id=provider_id, record=record)
    if credential_present is not None:
        diagnostic["credential_present"] = credential_present
    artifact = {
        "artifact_type": PROVIDER_CREDENTIAL_VAULT_EVENT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "operation": operation,
        "provider_id": provider_id,
        "credential_reference": PROVIDER_REFERENCES[provider_id],
        "credential_source": PROVIDER_REFERENCES[provider_id],
        "credential_present": diagnostic["credential_present"],
        "credential_enabled": diagnostic["credential_enabled"],
        "display_identifier": diagnostic["display_identifier"],
        "last_verified": diagnostic["last_verified"],
        "last_rotated": diagnostic["last_rotated"],
        "last_used": diagnostic["last_used"],
        "human_approval_required": operation in APPROVAL_REQUIRED_OPERATIONS,
        "human_approval_recorded": human_approval_artifact is not None,
        "human_approval_artifact_hash": human_approval_artifact.get("artifact_hash") if human_approval_artifact else None,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "authorization_header_recorded": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_visible": True,
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_secret_safe(artifact)
    if replay_dir is not None:
        write_json_immutable(Path(replay_dir) / "000_provider_credential_vault_event.json", artifact)
    return artifact


def _diagnostic(*, provider_id: str, record: dict[str, Any] | None) -> dict[str, Any]:
    present = record is not None and bool(record.get("credential_value"))
    enabled = present and record.get("credential_enabled") is True
    diagnostic = {
        "artifact_type": PROVIDER_CREDENTIAL_VAULT_DIAGNOSTIC_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "provider_id": provider_id,
        "credential_reference": PROVIDER_REFERENCES[provider_id],
        "credential_source": PROVIDER_REFERENCES[provider_id],
        "credential_present": present,
        "credential_enabled": enabled,
        "display_identifier": _display_identifier(record),
        "last_verified": record.get("last_verified") if record else None,
        "last_rotated": record.get("last_rotated") if record else None,
        "last_used": record.get("last_used") if record else None,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "authorization_header_recorded": False,
        "replay_safe": True,
    }
    diagnostic["artifact_hash"] = replay_hash(diagnostic)
    _assert_secret_safe(diagnostic)
    return diagnostic


def _load_vault(vault_path: str | Path) -> dict[str, Any]:
    path = _vault_path(vault_path)
    if not path.exists():
        return {"vault_version": MILESTONE_ID, "records": {}, "history": []}
    assert_vault_file_permissions(path)
    loaded = load_json(path)
    if not isinstance(loaded, dict):
        raise FailClosedRuntimeError("provider credential vault failed closed: malformed vault")
    loaded.setdefault("vault_version", MILESTONE_ID)
    loaded.setdefault("records", {})
    loaded.setdefault("history", [])
    if not isinstance(loaded["records"], dict) or not isinstance(loaded["history"], list):
        raise FailClosedRuntimeError("provider credential vault failed closed: malformed vault")
    return loaded


def _write_vault(vault_path: str | Path, vault: dict[str, Any]) -> None:
    path = _vault_path(vault_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(vault, sort_keys=True, indent=2), encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def _vault_path(vault_path: str | Path) -> Path:
    path = Path(vault_path).expanduser().resolve()
    cwd = Path.cwd().resolve()
    if path == cwd or cwd in path.parents:
        raise FailClosedRuntimeError("provider credential vault failed closed: vault path must be outside repository")
    return path


def _append_history(
    vault: dict[str, Any],
    *,
    provider_id: str,
    operation: str,
    created_at: str,
    generation_id: Any,
    human_approval_recorded: bool,
) -> None:
    event = {
        "provider_id": provider_id,
        "operation": operation,
        "credential_reference": PROVIDER_REFERENCES[provider_id],
        "display_identifier": _display_identifier_from_generation(generation_id),
        "human_approval_recorded": human_approval_recorded,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "created_at": created_at,
    }
    event["artifact_hash"] = replay_hash(event)
    vault.setdefault("history", []).append(event)


def _provider_deleted(vault: dict[str, Any], provider_id: str) -> bool:
    events = [item for item in vault.get("history", []) if item.get("provider_id") == provider_id]
    if not events:
        return False
    return events[-1].get("operation") == DELETE


def _existing_record(vault: dict[str, Any], provider_id: str) -> dict[str, Any]:
    record = vault["records"].get(provider_id)
    if not isinstance(record, dict):
        raise FailClosedRuntimeError("provider credential vault failed closed: credential unavailable")
    return record


def _enabled_record(vault: dict[str, Any], provider_id: str) -> dict[str, Any]:
    record = _existing_record(vault, provider_id)
    if record.get("credential_enabled") is not True:
        raise FailClosedRuntimeError("provider credential vault failed closed: credential disabled")
    if not isinstance(record.get("credential_value"), str) or not record.get("credential_value", "").strip():
        raise FailClosedRuntimeError("provider credential vault failed closed: credential unavailable")
    return record


def _provider_id(provider_id: str) -> str:
    if not isinstance(provider_id, str) or not provider_id.strip():
        raise FailClosedRuntimeError("provider credential vault failed closed: provider_id is required")
    provider = provider_id.strip().lower()
    if provider not in PROVIDER_REFERENCES:
        raise FailClosedRuntimeError("provider credential vault failed closed: provider is not registered")
    return provider


def _credential_value(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("provider credential vault failed closed: credential value is required")
    return value.strip()


def _require_human_approval(operation: str, artifact: dict[str, Any] | None) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"provider credential vault failed closed: {operation} requires human approval")
    if artifact.get("decision") != "APPROVED" and artifact.get("approval_status") != "APPROVED":
        raise FailClosedRuntimeError(f"provider credential vault failed closed: {operation} approval was not approved")


def _new_generation_id() -> str:
    return secrets.token_urlsafe(12)


def _display_identifier(record: dict[str, Any] | None) -> str | None:
    if not isinstance(record, dict):
        return None
    return _display_identifier_from_generation(record.get("generation_id"))


def _display_identifier_from_generation(generation_id: Any) -> str | None:
    if not isinstance(generation_id, str) or not generation_id:
        return None
    return "..." + generation_id[-4:]


def _display_identifier_from_secret(secret: str) -> str:
    return f"...{secret[-4:]}"


def _assert_secret_safe(value: Any) -> None:
    serialized = repr(value)
    for marker in SECRET_MARKERS:
        if marker in serialized:
            raise FailClosedRuntimeError("provider credential vault failed closed: secret-like material recorded")


class _MissingVaultCredential(Exception):
    pass
