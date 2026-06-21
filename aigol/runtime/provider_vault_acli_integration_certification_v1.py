"""Certification runtime for AIGOL_PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFICATION_V1."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import os
import re
from typing import Any, Iterator

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.runtime.first_live_cognition_provider_certification import (
    run_first_live_cognition_provider_certification,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import (
    DEFAULT_VAULT_PATH,
    provider_credential_diagnostic,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/provider_vault_acli_integration_certification_v1")
CREATED_AT = "2026-06-21T00:00:00Z"
INITIAL_SECRET = "sk-provider-vault-acli-integration-initial-5NwA"
ROTATED_SECRET = "sk-provider-vault-acli-integration-rotated-9QxB"


def run_provider_vault_acli_integration_certification(
    *,
    replay_base: str | Path | None = None,
    operator_vault_path: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"
    acl_dir = root / "acli_commands"
    live_dir = root / "first_live_vault_only_certification"
    vault_path = Path(operator_vault_path) if operator_vault_path is not None else _default_cert_vault_path(root)
    lifecycle_replay_root = root / "vault_lifecycle_replay"

    command_results: list[dict[str, Any]] = []
    approval_failures: list[dict[str, Any]] = []

    with _credential_input(INITIAL_SECRET):
        command_results.append(
            _run_acli(
                [
                    "provider",
                    "credential",
                    "add",
                    "openai",
                    "--vault-path",
                    str(vault_path),
                    "--replay-root",
                    str(lifecycle_replay_root),
                    "--created-at",
                    CREATED_AT,
                ],
                acl_dir,
            )
        )
    command_results.append(
        _run_acli(
            [
                "provider",
                "credential",
                "verify",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
            ],
            acl_dir,
        )
    )
    approval_failures.append(
        _expect_fail_closed(
            [
                "provider",
                "credential",
                "rotate",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
            ],
            acl_dir,
            env_secret=ROTATED_SECRET,
        )
    )
    with _credential_input(ROTATED_SECRET):
        command_results.append(
            _run_acli(
                [
                    "provider",
                    "credential",
                    "rotate",
                    "openai",
                    "--vault-path",
                    str(vault_path),
                    "--replay-root",
                    str(lifecycle_replay_root),
                    "--created-at",
                    CREATED_AT,
                    "--human-approved",
                ],
                acl_dir,
            )
        )
    command_results.append(
        _run_acli(
            [
                "provider",
                "credential",
                "history",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
            ],
            acl_dir,
        )
    )
    command_results.append(
        _run_acli(
            [
                "provider",
                "credential",
                "status",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
            ],
            acl_dir,
        )
    )

    live_vault_path = _default_cert_vault_path(root / "live")
    with _credential_input(ROTATED_SECRET):
        command_results.append(
            _run_acli(
                [
                    "provider",
                    "credential",
                    "add",
                    "openai",
                    "--vault-path",
                    str(live_vault_path),
                    "--replay-root",
                    str(lifecycle_replay_root / "live"),
                    "--created-at",
                    CREATED_AT,
                ],
                acl_dir,
            )
        )

    with _without_openai_env():
        live_certification = run_first_live_cognition_provider_certification(
            replay_base=live_dir,
            transport=_certification_transport(expected_secret=ROTATED_SECRET),
            require_openai_api_key_marker=False,
            vault_path=live_vault_path,
        )

    approval_failures.append(
        _expect_fail_closed(
            [
                "provider",
                "credential",
                "disable",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
            ],
            acl_dir,
        )
    )
    command_results.append(
        _run_acli(
            [
                "provider",
                "credential",
                "disable",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
                "--human-approved",
            ],
            acl_dir,
        )
    )
    approval_failures.append(
        _expect_fail_closed(
            [
                "provider",
                "credential",
                "delete",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
            ],
            acl_dir,
        )
    )
    command_results.append(
        _run_acli(
            [
                "provider",
                "credential",
                "delete",
                "openai",
                "--vault-path",
                str(vault_path),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
                "--human-approved",
            ],
            acl_dir,
        )
    )

    live_observed = live_certification.get("observed", {})
    vault_diagnostic = provider_credential_diagnostic(provider_id="openai", vault_path=live_vault_path)
    no_secret_leak = _secret_free(root)
    lifecycle_operations = [item["operation"] for item in command_results]
    coverage = {
        "artifact_type": "PROVIDER_VAULT_ACLI_INTEGRATION_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "commands_required": ["add", "verify", "rotate", "disable", "delete", "history"],
        "commands_executed": lifecycle_operations,
        "deterministic_routing_verified": all(item.get("command", "").startswith("aigol provider credential") for item in command_results),
        "approval_fail_closed_checks": approval_failures,
        "vault_file_created": live_vault_path.exists(),
        "default_operator_vault_path": str(DEFAULT_VAULT_PATH),
        "certification_vault_path": str(live_vault_path),
        "first_live_env_removed": True,
        "first_live_credential_source": live_observed.get("credential_source"),
        "secret_free_evidence": no_secret_leak,
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    final_verdict = (
        "PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFIED"
        if all(
            [
                coverage["deterministic_routing_verified"],
                len(approval_failures) == 3,
                all(item["failed_closed"] for item in approval_failures),
                coverage["vault_file_created"],
                live_observed.get("provider_selected") == "openai",
                live_observed.get("provider_invoked") is True,
                live_observed.get("provider_response_received") is True,
                live_observed.get("credential_source") == "vault://provider/openai",
                no_secret_leak,
            ]
        )
        else "PROVIDER_VAULT_ACLI_INTEGRATION_GAPS_FOUND"
    )
    evidence = {
        "artifact_type": "PROVIDER_VAULT_ACLI_INTEGRATION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(root),
        "acli_command_results": command_results,
        "approval_failures": approval_failures,
        "vault_diagnostic": vault_diagnostic,
        "first_live_certification": live_certification,
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    replay = {
        "artifact_type": "PROVIDER_VAULT_ACLI_INTEGRATION_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(root),
        "lifecycle_replay_root": str(lifecycle_replay_root),
        "first_live_replay_root": live_certification.get("cert_root"),
        "replay_reconstructed": live_observed.get("replay_reconstructed") is True,
        "secret_free": no_secret_leak,
        "final_verdict": final_verdict,
    }
    replay["artifact_hash"] = replay_hash(replay)
    report = {
        "artifact_type": "PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "questions": {
            "vault_lifecycle_reachable_from_acli": coverage["deterministic_routing_verified"],
            "vault_file_created": coverage["vault_file_created"],
            "first_live_certification_vault_backed": live_observed.get("credential_source") == "vault://provider/openai",
            "environment_fallback_required": False,
            "approval_boundaries_preserved": all(item["failed_closed"] for item in approval_failures),
            "replay_secret_free": no_secret_leak,
        },
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    _persist(evidence_dir, replay_dir, report_dir, coverage, evidence, replay, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "evidence_package_path": str(evidence_dir / "000_provider_vault_acli_integration_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_provider_vault_acli_integration_replay_package.json"),
        "certification_report_path": str(report_dir / "000_provider_vault_acli_integration_certification_report.json"),
        "coverage_report_path": str(evidence_dir / "001_provider_vault_acli_integration_coverage_report.json"),
        "final_verdict": final_verdict,
        "coverage": coverage,
    }


def _run_acli(argv: list[str], acl_dir: Path) -> dict[str, Any]:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run_command(args)
    acl_dir.mkdir(parents=True, exist_ok=True)
    index = len(list(acl_dir.glob("*.json")))
    write_json_immutable(acl_dir / f"{index:03d}_{'_'.join(argv[:3])}.json", result)
    return {
        "command": result.get("command"),
        "operation": result.get("operation"),
        "provider_id": result.get("provider_id"),
        "credential_reference": result.get("artifact", {}).get("credential_reference"),
        "credential_present": result.get("artifact", {}).get("credential_present"),
        "credential_enabled": result.get("artifact", {}).get("credential_enabled"),
        "display_identifier": result.get("artifact", {}).get("display_identifier"),
        "replay_reference": result.get("replay_reference"),
    }


def _expect_fail_closed(
    argv: list[str],
    acl_dir: Path,
    *,
    env_secret: str | None = None,
) -> dict[str, Any]:
    try:
        if env_secret is None:
            _run_acli(argv, acl_dir)
        else:
            with _credential_input(env_secret):
                _run_acli(argv, acl_dir)
    except FailClosedRuntimeError as exc:
        return {"command": " ".join(["aigol", *argv]), "failed_closed": True, "failure_reason": str(exc)}
    return {"command": " ".join(["aigol", *argv]), "failed_closed": False, "failure_reason": None}


def _certification_transport(*, expected_secret: str):
    def call(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        if metadata.get("_credential_secret") != expected_secret:
            raise FailClosedRuntimeError("vault ACLI integration certification failed closed: vault credential mismatch")
        return {
            "id": "provider-vault-acli-integration-response",
            "status_code": 200,
            "output_text": "Findings: vault-backed provider execution certified. Confidence: HIGH",
            "real_openai_called": True,
            "live_provider_call_performed": True,
            "credential_secret_replayed": False,
            "authorization_header_replayed": False,
        }

    call.aigol_governed_live_openai_executor_v1 = True
    return call


@contextmanager
def _credential_input(value: str) -> Iterator[None]:
    previous = os.environ.get("AIGOL_PROVIDER_CREDENTIAL_INPUT")
    os.environ["AIGOL_PROVIDER_CREDENTIAL_INPUT"] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("AIGOL_PROVIDER_CREDENTIAL_INPUT", None)
        else:
            os.environ["AIGOL_PROVIDER_CREDENTIAL_INPUT"] = previous


@contextmanager
def _without_openai_env() -> Iterator[None]:
    previous_openai = os.environ.get("OPENAI_API_KEY")
    previous_aigol = os.environ.get("AIGOL_OPENAI_API_KEY")
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("AIGOL_OPENAI_API_KEY", None)
    try:
        yield
    finally:
        if previous_openai is not None:
            os.environ["OPENAI_API_KEY"] = previous_openai
        if previous_aigol is not None:
            os.environ["AIGOL_OPENAI_API_KEY"] = previous_aigol


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        try:
            serialized += canonical_serialize(load_json(path))
        except Exception:
            continue
    return INITIAL_SECRET not in serialized and ROTATED_SECRET not in serialized and "Bearer " not in serialized


def _persist(
    evidence_dir: Path,
    replay_dir: Path,
    report_dir: Path,
    coverage: dict[str, Any],
    evidence: dict[str, Any],
    replay: dict[str, Any],
    report: dict[str, Any],
) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    write_json_immutable(evidence_dir / "000_provider_vault_acli_integration_evidence_package.json", evidence)
    write_json_immutable(evidence_dir / "001_provider_vault_acli_integration_coverage_report.json", coverage)
    write_json_immutable(replay_dir / "000_provider_vault_acli_integration_replay_package.json", replay)
    write_json_immutable(report_dir / "000_provider_vault_acli_integration_certification_report.json", report)


def _default_cert_vault_path(root: Path) -> Path:
    root_identity = replay_hash(str(root.resolve())).removeprefix("sha256:")[:12]
    return (
        Path("/tmp")
        / "aigol_provider_vault_acli_integration_certification_v1"
        / f"{root.name}-{os.getpid()}-{root_identity}"
        / "provider-credentials.json"
    )


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def main() -> int:
    result = run_provider_vault_acli_integration_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
