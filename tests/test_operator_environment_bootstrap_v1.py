"""Tests for AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1."""

from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess

from aigol.runtime.operator_environment_bootstrap import (
    BOOTSTRAP_SCRIPT,
    MISSING_CREDENTIAL,
    READY,
    build_operator_environment_diagnostic,
    install_operator_bootstrap,
    main,
    shell_startup_snippets,
    verify_operator_environment,
)


def test_operator_bootstrap_install_creates_secret_free_script(tmp_path):
    bootstrap_path = tmp_path / "operator-bootstrap.sh"

    result = install_operator_bootstrap(path=bootstrap_path)

    assert result["installed"] is True
    assert result["install_mode"] == "CREATED"
    assert result["credential_value_recorded"] is False
    assert result["credential_hash_recorded"] is False
    assert bootstrap_path.read_text(encoding="utf-8") == BOOTSTRAP_SCRIPT
    assert stat.S_IMODE(bootstrap_path.stat().st_mode) == 0o600
    assert "sk-test-secret" not in bootstrap_path.read_text(encoding="utf-8")


def test_operator_bootstrap_source_propagates_openai_alias_without_printing_secret(tmp_path):
    bootstrap_path = tmp_path / "operator-bootstrap.sh"
    install_operator_bootstrap(path=bootstrap_path)
    env = os.environ.copy()
    env.pop("AIGOL_OPENAI_API_KEY", None)
    env["OPENAI_API_KEY"] = "sk-test-secret"

    completed = subprocess.run(
        [
            "bash",
            "-c",
            (
                f'. "{bootstrap_path}"; '
                'python -c "import os; '
                'print(\'AIGOL_OPENAI_API_KEY_PRESENT=\' + str(bool(os.environ.get(\'AIGOL_OPENAI_API_KEY\')))); '
                'print(\'OPENAI_API_KEY_PRESENT=\' + str(bool(os.environ.get(\'OPENAI_API_KEY\'))))"'
            ),
        ],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    assert "AIGOL_OPENAI_API_KEY_PRESENT=True" in completed.stdout
    assert "OPENAI_API_KEY_PRESENT=True" in completed.stdout
    assert "sk-test-secret" not in completed.stdout


def test_operator_bootstrap_preserves_existing_canonical_value(tmp_path):
    bootstrap_path = tmp_path / "operator-bootstrap.sh"
    install_operator_bootstrap(path=bootstrap_path)
    env = os.environ.copy()
    env["AIGOL_OPENAI_API_KEY"] = "canonical-secret"
    env["OPENAI_API_KEY"] = "alias-secret"

    completed = subprocess.run(
        [
            "bash",
            "-c",
            f'. "{bootstrap_path}"; python -c "import os; print(os.environ[\'AIGOL_OPENAI_API_KEY\'] == \'canonical-secret\')"',
        ],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    assert completed.stdout.strip() == "True"


def test_operator_environment_diagnostic_is_replay_safe(tmp_path):
    env = {
        "AIGOL_OPENAI_API_KEY": "sk-test-secret",
        "OPENAI_API_KEY": "sk-test-secret",
    }

    diagnostic = build_operator_environment_diagnostic(
        env=env,
        bootstrap_path=tmp_path / "operator-bootstrap.sh",
    )
    serialized = repr(diagnostic)

    assert diagnostic["artifact_type"] == "OPERATOR_ENVIRONMENT_BOOTSTRAP_DIAGNOSTIC_V1"
    assert diagnostic["canonical_credential_reference"] == "env:AIGOL_OPENAI_API_KEY"
    assert diagnostic["canonical_credential_present"] is True
    assert diagnostic["provider_native_alias_present"] is True
    assert diagnostic["credential_value_recorded"] is False
    assert diagnostic["credential_hash_recorded"] is False
    assert "sk-test-secret" not in serialized


def test_operator_environment_verify_reports_missing_credential_without_secret(tmp_path):
    env = {"OPENAI_API_KEY": "sk-test-secret"}

    result = verify_operator_environment(
        env=env,
        bootstrap_path=tmp_path / "operator-bootstrap.sh",
    )
    serialized = repr(result)

    assert result["verification_status"] == MISSING_CREDENTIAL
    assert result["diagnostic"]["failure_classification"] == MISSING_CREDENTIAL
    assert result["diagnostic"]["canonical_credential_present"] is False
    assert result["diagnostic"]["provider_native_alias_present"] is True
    assert "sk-test-secret" not in serialized


def test_operator_environment_verify_reports_ready_when_canonical_present(tmp_path):
    result = verify_operator_environment(
        env={"AIGOL_OPENAI_API_KEY": "sk-test-secret"},
        bootstrap_path=tmp_path / "operator-bootstrap.sh",
    )

    assert result["verification_status"] == READY
    assert result["diagnostic"]["failure_classification"] is None


def test_operator_environment_cli_verify_prints_presence_only(tmp_path, monkeypatch, capsys):
    bootstrap_path = tmp_path / "operator-bootstrap.sh"
    install_operator_bootstrap(path=bootstrap_path)
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "sk-test-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-secret")

    exit_code = main(["verify", "--path", str(bootstrap_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "OPERATOR_BOOTSTRAP_FILE_PRESENT=True" in output
    assert "AIGOL_OPENAI_API_KEY_PRESENT=True" in output
    assert "OPENAI_API_KEY_PRESENT=True" in output
    assert "OPERATOR_BOOTSTRAP_VERIFICATION_STATUS=READY" in output
    assert "sk-test-secret" not in output


def test_operator_environment_shell_integration_supports_bash_zsh_and_login_shells():
    snippets = shell_startup_snippets()

    assert set(snippets) == {"bash", "zsh", "login_shell"}
    for snippet in snippets.values():
        assert "$HOME/.config/aigol/operator-bootstrap.sh" in snippet
        assert ". \"$HOME/.config/aigol/operator-bootstrap.sh\"" in snippet
