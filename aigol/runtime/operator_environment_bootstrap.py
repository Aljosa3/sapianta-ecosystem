"""Operator environment bootstrap for AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import stat
import sys
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError


MILESTONE_ID = "AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1"
BOOTSTRAP_ARTIFACT_TYPE = "OPERATOR_ENVIRONMENT_BOOTSTRAP_DIAGNOSTIC_V1"
DEFAULT_BOOTSTRAP_PATH = Path.home() / ".config" / "aigol" / "operator-bootstrap.sh"
MISSING_CREDENTIAL = "MISSING_CREDENTIAL"
READY = "READY"

BOOTSTRAP_SCRIPT = """# ~/.config/aigol/operator-bootstrap.sh
# AiGOL operator environment bootstrap.
# Do not enable shell tracing while sourcing this file.

set +x

if [ -z "${AIGOL_OPENAI_API_KEY:-}" ] && [ -n "${OPENAI_API_KEY:-}" ]; then
  export AIGOL_OPENAI_API_KEY="$OPENAI_API_KEY"
fi

if [ -z "${AIGOL_ANTHROPIC_API_KEY:-}" ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  export AIGOL_ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
fi

if [ -z "${AIGOL_GEMINI_API_KEY:-}" ] && [ -n "${GEMINI_API_KEY:-}" ]; then
  export AIGOL_GEMINI_API_KEY="$GEMINI_API_KEY"
fi

if [ -z "${AIGOL_MISTRAL_API_KEY:-}" ] && [ -n "${MISTRAL_API_KEY:-}" ]; then
  export AIGOL_MISTRAL_API_KEY="$MISTRAL_API_KEY"
fi
"""

PROVIDER_CREDENTIALS: dict[str, dict[str, str]] = {
    "openai": {
        "canonical_env": "AIGOL_OPENAI_API_KEY",
        "alias_env": "OPENAI_API_KEY",
        "credential_reference": "env:AIGOL_OPENAI_API_KEY",
    },
    "claude": {
        "canonical_env": "AIGOL_ANTHROPIC_API_KEY",
        "alias_env": "ANTHROPIC_API_KEY",
        "credential_reference": "env:AIGOL_ANTHROPIC_API_KEY",
    },
    "gemini": {
        "canonical_env": "AIGOL_GEMINI_API_KEY",
        "alias_env": "GEMINI_API_KEY",
        "credential_reference": "env:AIGOL_GEMINI_API_KEY",
    },
    "mistral": {
        "canonical_env": "AIGOL_MISTRAL_API_KEY",
        "alias_env": "MISTRAL_API_KEY",
        "credential_reference": "env:AIGOL_MISTRAL_API_KEY",
    },
}


def install_operator_bootstrap(
    *,
    path: str | Path = DEFAULT_BOOTSTRAP_PATH,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Install the sourceable operator bootstrap script without storing secrets."""

    bootstrap_path = Path(path).expanduser()
    existing = bootstrap_path.read_text(encoding="utf-8") if bootstrap_path.exists() else None
    if existing is not None and existing != BOOTSTRAP_SCRIPT and not overwrite:
        raise FailClosedRuntimeError(
            "operator bootstrap install failed closed: existing bootstrap differs; rerun with --overwrite"
        )

    bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
    if existing != BOOTSTRAP_SCRIPT:
        bootstrap_path.write_text(BOOTSTRAP_SCRIPT, encoding="utf-8")
        mode = "UPDATED" if existing is not None else "CREATED"
    else:
        mode = "UNCHANGED"
    bootstrap_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return {
        "milestone_id": MILESTONE_ID,
        "bootstrap_path": str(bootstrap_path),
        "installed": True,
        "install_mode": mode,
        "file_mode": "0600",
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "replay_safe": True,
    }


def build_operator_environment_diagnostic(
    *,
    provider_id: str = "openai",
    env: dict[str, str] | None = None,
    bootstrap_path: str | Path = DEFAULT_BOOTSTRAP_PATH,
) -> dict[str, Any]:
    """Build a replay-safe credential presence diagnostic."""

    provider = _provider(provider_id)
    environment = os.environ if env is None else env
    canonical_env = provider["canonical_env"]
    alias_env = provider["alias_env"]
    canonical_present = bool(environment.get(canonical_env))
    alias_present = bool(environment.get(alias_env))
    bootstrap_file_present = Path(bootstrap_path).expanduser().exists()
    failure = None if canonical_present else MISSING_CREDENTIAL
    return {
        "artifact_type": BOOTSTRAP_ARTIFACT_TYPE,
        "milestone_id": MILESTONE_ID,
        "provider_id": provider_id,
        "canonical_credential_reference": provider["credential_reference"],
        "canonical_credential_env": canonical_env,
        "canonical_credential_present": canonical_present,
        "provider_native_alias": f"env:{alias_env}",
        "provider_native_alias_present": alias_present,
        "bootstrap_file_reference": str(Path(bootstrap_path).expanduser()),
        "bootstrap_file_present": bootstrap_file_present,
        "failure_classification": failure,
        "operator_safe_message": _operator_safe_message(provider_id, canonical_present),
        "remediation_hint": _remediation_hint(provider["credential_reference"]),
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "authorization_header_recorded": False,
        "replay_safe": True,
    }


def verify_operator_environment(
    *,
    provider_id: str = "openai",
    env: dict[str, str] | None = None,
    bootstrap_path: str | Path = DEFAULT_BOOTSTRAP_PATH,
) -> dict[str, Any]:
    """Return verification status for the canonical provider credential reference."""

    diagnostic = build_operator_environment_diagnostic(
        provider_id=provider_id,
        env=env,
        bootstrap_path=bootstrap_path,
    )
    return {
        "milestone_id": MILESTONE_ID,
        "provider_id": provider_id,
        "diagnostic": diagnostic,
        "verification_status": READY if diagnostic["canonical_credential_present"] else MISSING_CREDENTIAL,
    }


def shell_startup_snippets() -> dict[str, str]:
    """Return operator-visible startup snippets for supported shells."""

    snippet = (
        'if [ -r "$HOME/.config/aigol/operator-bootstrap.sh" ]; then\n'
        '  . "$HOME/.config/aigol/operator-bootstrap.sh"\n'
        "fi"
    )
    return {
        "bash": snippet,
        "zsh": snippet,
        "login_shell": snippet,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m aigol.runtime.operator_environment_bootstrap")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("--path", default=str(DEFAULT_BOOTSTRAP_PATH))
    install_parser.add_argument("--overwrite", action="store_true")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--provider", default="openai", choices=sorted(PROVIDER_CREDENTIALS))
    verify_parser.add_argument("--path", default=str(DEFAULT_BOOTSTRAP_PATH))

    subparsers.add_parser("shell-integration")

    args = parser.parse_args(argv)
    try:
        if args.command == "install":
            result = install_operator_bootstrap(path=args.path, overwrite=args.overwrite)
            print(f"OPERATOR_BOOTSTRAP_PATH={result['bootstrap_path']}")
            print(f"OPERATOR_BOOTSTRAP_INSTALLED={result['installed']}")
            print(f"OPERATOR_BOOTSTRAP_INSTALL_MODE={result['install_mode']}")
            print(f"OPERATOR_BOOTSTRAP_FILE_MODE={result['file_mode']}")
            return 0
        if args.command == "verify":
            result = verify_operator_environment(provider_id=args.provider, bootstrap_path=args.path)
            diagnostic = result["diagnostic"]
            canonical_env = diagnostic["canonical_credential_env"]
            alias_name = diagnostic["provider_native_alias"].removeprefix("env:")
            print(f"OPERATOR_BOOTSTRAP_FILE_PRESENT={diagnostic['bootstrap_file_present']}")
            print(f"{canonical_env}_PRESENT={diagnostic['canonical_credential_present']}")
            print(f"{alias_name}_PRESENT={diagnostic['provider_native_alias_present']}")
            print(f"DEPENDENCY_FAILURE_CLASSIFICATION={diagnostic['failure_classification']}")
            print(f"OPERATOR_BOOTSTRAP_VERIFICATION_STATUS={result['verification_status']}")
            return 0 if result["verification_status"] == READY else 1
        if args.command == "shell-integration":
            for shell, snippet in shell_startup_snippets().items():
                print(f"[{shell}]")
                print(snippet)
            return 0
    except FailClosedRuntimeError as exc:
        print(f"OPERATOR_BOOTSTRAP_FAILED={exc}", file=sys.stderr)
        return 1
    return 1


def _provider(provider_id: str) -> dict[str, str]:
    try:
        return PROVIDER_CREDENTIALS[provider_id]
    except KeyError as exc:
        raise FailClosedRuntimeError(f"unsupported provider credential bootstrap: {provider_id}") from exc


def _operator_safe_message(provider_id: str, credential_present: bool) -> str:
    if credential_present:
        return f"{provider_id} credential reference is present in the governed process environment."
    return f"{provider_id} credential reference is unavailable in the governed process environment."


def _remediation_hint(credential_reference: str) -> str:
    return (
        f"Source $HOME/.config/aigol/operator-bootstrap.sh in the shell that launches AiGOL, "
        f"then verify {credential_reference} presence without printing the value."
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
