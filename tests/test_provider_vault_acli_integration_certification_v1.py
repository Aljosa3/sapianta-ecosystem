"""Tests for AIGOL_PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import retrieve_provider_credential
from aigol.runtime.provider_vault_acli_integration_certification_v1 import (
    INITIAL_SECRET,
    MILESTONE_ID,
    ROTATED_SECRET,
    run_provider_vault_acli_integration_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def _run(argv: list[str]) -> dict:
    args = build_parser().parse_args(argv)
    return run_command(args)


def test_provider_credential_acli_lifecycle_routes_and_updates_vault(tmp_path, monkeypatch):
    vault_path = tmp_path / "operator" / "provider-credentials.json"
    replay_root = tmp_path / "replay"

    monkeypatch.setenv("AIGOL_PROVIDER_CREDENTIAL_INPUT", INITIAL_SECRET)
    add = _run(
        [
            "provider",
            "credential",
            "add",
            "openai",
            "--vault-path",
            str(vault_path),
            "--replay-root",
            str(replay_root),
        ]
    )
    assert add["command"] == "aigol provider credential add"
    assert add["artifact"]["credential_reference"] == "vault://provider/openai"
    assert add["artifact"]["credential_present"] is True
    assert add["artifact"]["credential_enabled"] is True
    assert vault_path.exists()
    assert oct(vault_path.stat().st_mode & 0o777) == "0o600"

    verify = _run(
        [
            "provider",
            "credential",
            "verify",
            "openai",
            "--vault-path",
            str(vault_path),
            "--replay-root",
            str(replay_root),
        ]
    )
    assert verify["operation"] == "VERIFY"

    with pytest.raises(FailClosedRuntimeError):
        _run(
            [
                "provider",
                "credential",
                "rotate",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(replay_root),
            ]
        )

    monkeypatch.setenv("AIGOL_PROVIDER_CREDENTIAL_INPUT", ROTATED_SECRET)
    rotate = _run(
        [
            "provider",
            "credential",
            "rotate",
            "openai",
            "--vault-path",
            str(vault_path),
            "--replay-root",
            str(replay_root),
            "--human-approved",
        ]
    )
    assert rotate["operation"] == "ROTATE"
    credential = retrieve_provider_credential(provider_id="openai", vault_path=vault_path, allow_env_fallback=False)
    assert credential["credential_source"] == "vault://provider/openai"
    assert credential["_credential_secret"] == ROTATED_SECRET

    history = _run(["provider", "credential", "history", "openai", "--vault-path", str(vault_path)])
    assert history["artifact"]["credential_value_recorded"] is False
    assert [item["operation"] for item in history["artifact"]["history"]] == ["ADD", "VERIFY", "ROTATE"]


def test_provider_credential_acli_enforces_approval_for_disable_and_delete(tmp_path, monkeypatch):
    vault_path = tmp_path / "operator" / "provider-credentials.json"
    replay_root = tmp_path / "replay"
    monkeypatch.setenv("AIGOL_PROVIDER_CREDENTIAL_INPUT", INITIAL_SECRET)
    _run(
        [
            "provider",
            "credential",
            "add",
            "openai",
            "--vault-path",
            str(vault_path),
            "--replay-root",
            str(replay_root),
        ]
    )

    with pytest.raises(FailClosedRuntimeError):
        _run(
            [
                "provider",
                "credential",
                "disable",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(replay_root),
            ]
        )

    disabled = _run(
        [
            "provider",
            "credential",
            "disable",
            "openai",
            "--vault-path",
            str(vault_path),
            "--replay-root",
            str(replay_root),
            "--human-approved",
        ]
    )
    assert disabled["artifact"]["credential_enabled"] is False

    with pytest.raises(FailClosedRuntimeError):
        retrieve_provider_credential(provider_id="openai", vault_path=vault_path, allow_env_fallback=False)

    with pytest.raises(FailClosedRuntimeError):
        _run(
            [
                "provider",
                "credential",
                "delete",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(replay_root),
            ]
        )

    deleted = _run(
        [
            "provider",
            "credential",
            "delete",
            "openai",
            "--vault-path",
            str(vault_path),
            "--replay-root",
            str(replay_root),
            "--human-approved",
        ]
    )
    assert deleted["artifact"]["credential_present"] is False


def test_provider_vault_acli_integration_certification_certifies_vault_only_first_live(tmp_path, monkeypatch):
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = run_provider_vault_acli_integration_certification(
        replay_base=tmp_path / "provider_vault_acli_integration"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFIED"
    assert result["coverage"]["first_live_credential_source"] == "vault://provider/openai"
    assert result["coverage"]["secret_free_evidence"] is True

    root = Path(result["cert_root"])
    assert (root / "evidence_package" / "000_provider_vault_acli_integration_evidence_package.json").exists()
    assert (root / "replay_package" / "000_provider_vault_acli_integration_replay_package.json").exists()
    assert (root / "certification_report" / "000_provider_vault_acli_integration_certification_report.json").exists()

    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    assert INITIAL_SECRET not in serialized
    assert ROTATED_SECRET not in serialized
    assert "Bearer " not in serialized
