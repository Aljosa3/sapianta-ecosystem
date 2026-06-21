"""Certification runtime for AIGOL_PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFICATION_V1."""

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
from aigol.runtime.provider_credential_vault import (
    DEFAULT_VAULT_PATH,
    provider_credential_diagnostic,
    retrieve_provider_credential,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/provider_vault_source_of_truth_certification_v1")
CREATED_AT = "2026-06-21T00:00:00Z"


def run_provider_vault_source_of_truth_certification(
    *,
    replay_base: str | Path | None = None,
    vault_path: str | Path = DEFAULT_VAULT_PATH,
    transport: Any | None = None,
    require_real_transport: bool = True,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"
    lifecycle_replay_root = root / "vault_onboarding_replay"
    live_replay_base = root / "first_live_vault_only_certification"
    vault = Path(vault_path).expanduser()

    onboarding_secret = ""
    pre_existing_vault = vault.exists()
    onboarding_result: dict[str, Any] | None = None
    verification_result: dict[str, Any] | None = None
    resolution_result: dict[str, Any] | None = None
    live_result: dict[str, Any] | None = None
    failure_reason: str | None = None
    try:
        onboarding_secret = _operator_onboarding_secret()
        with _credential_input(onboarding_secret):
            onboarding_result = _run_acli(
                [
                    "provider",
                    "credential",
                    "add",
                    "openai",
                    "--vault-path",
                    str(vault),
                    "--replay-root",
                    str(lifecycle_replay_root),
                    "--created-at",
                    CREATED_AT,
                    "--human-approved",
                ]
            )
        verification_result = _run_acli(
            [
                "provider",
                "credential",
                "verify",
                "openai",
                "--vault-path",
                str(vault),
                "--replay-root",
                str(lifecycle_replay_root),
                "--created-at",
                CREATED_AT,
            ]
        )
        resolution = retrieve_provider_credential(
            provider_id="openai",
            authorization_context={"runtime": MILESTONE_ID, "stage": "source_of_truth_resolution"},
            vault_path=vault,
            allow_env_fallback=False,
            created_at=CREATED_AT,
            replay_dir=root / "vault_resolution",
        )
        resolution_result = _safe_resolution_summary(resolution)
        with _without_openai_env():
            live_result = run_first_live_cognition_provider_certification(
                replay_base=live_replay_base,
                transport=transport,
                require_openai_api_key_marker=False,
                vault_path=vault,
            )
    except Exception as exc:
        failure_reason = str(exc)

    vault_exists = vault.exists()
    diagnostic: dict[str, Any] | None = None
    try:
        diagnostic = provider_credential_diagnostic(provider_id="openai", vault_path=vault)
    except Exception as exc:
        if failure_reason is None:
            failure_reason = str(exc)

    live_observed = live_result.get("observed", {}) if isinstance(live_result, dict) else {}
    no_secret_leak = _secret_free(root, onboarding_secret)
    approval_preserved = bool(onboarding_result and onboarding_result.get("artifact", {}).get("human_approval_recorded") is True)
    coverage = {
        "artifact_type": "PROVIDER_VAULT_SOURCE_OF_TRUTH_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "default_vault_path": str(DEFAULT_VAULT_PATH),
        "certification_vault_path": str(vault),
        "pre_existing_vault": pre_existing_vault,
        "vault_file_exists": vault_exists,
        "vault_resolution_attempted": resolution_result is not None,
        "vault_resolution_successful": bool(resolution_result and resolution_result.get("credential_source") == "vault://provider/openai"),
        "openai_env_removed_for_execution": True,
        "provider_selected": live_observed.get("provider_selected"),
        "provider_invoked": live_observed.get("provider_invoked"),
        "provider_response_received": live_observed.get("provider_response_received"),
        "human_confirmation_recorded": live_observed.get("human_confirmation_recorded"),
        "replay_reconstructed": live_observed.get("replay_reconstructed"),
        "credential_source": live_observed.get("credential_source"),
        "approval_boundaries_preserved": approval_preserved,
        "secret_free_evidence": no_secret_leak,
        "require_real_transport": require_real_transport,
        "failure_reason": failure_reason or live_observed.get("failure_reason"),
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    final_verdict = (
        "PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFIED"
        if all(
            [
                vault_exists,
                coverage["vault_resolution_successful"],
                coverage["provider_selected"] == "openai",
                coverage["provider_invoked"] is True,
                coverage["provider_response_received"] is True,
                coverage["credential_source"] == "vault://provider/openai",
                coverage["secret_free_evidence"],
                coverage["approval_boundaries_preserved"],
            ]
        )
        else "PROVIDER_VAULT_SOURCE_OF_TRUTH_GAPS_FOUND"
    )
    evidence = {
        "artifact_type": "PROVIDER_VAULT_SOURCE_OF_TRUTH_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(root),
        "vault_path": str(vault),
        "onboarding_result": _safe_command_result(onboarding_result),
        "verification_result": _safe_command_result(verification_result),
        "resolution_result": resolution_result,
        "vault_diagnostic": diagnostic,
        "first_live_certification": live_result,
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    replay = {
        "artifact_type": "PROVIDER_VAULT_SOURCE_OF_TRUTH_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(root),
        "vault_lifecycle_replay_root": str(lifecycle_replay_root),
        "vault_resolution_replay": str(root / "vault_resolution"),
        "first_live_replay_root": live_result.get("cert_root") if isinstance(live_result, dict) else None,
        "replay_reconstructed": coverage["replay_reconstructed"] is True,
        "secret_free": no_secret_leak,
        "final_verdict": final_verdict,
    }
    replay["artifact_hash"] = replay_hash(replay)
    report = {
        "artifact_type": "PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "most_important_question": {
            "can_execute_live_cognition_provider_using_only_provider_vault": final_verdict
            == "PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFIED"
        },
        "coverage_report": coverage,
        "blocker_analysis": [] if final_verdict == "PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFIED" else [coverage["failure_reason"]],
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    _persist(evidence_dir, replay_dir, report_dir, coverage, evidence, replay, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "evidence_package_path": str(evidence_dir / "000_provider_vault_source_of_truth_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_provider_vault_source_of_truth_replay_package.json"),
        "certification_report_path": str(report_dir / "000_provider_vault_source_of_truth_certification_report.json"),
        "coverage_report_path": str(evidence_dir / "001_provider_vault_source_of_truth_coverage_report.json"),
        "final_verdict": final_verdict,
        "coverage": coverage,
    }


def _operator_onboarding_secret() -> str:
    for name in ("OPENAI_API_KEY", "AIGOL_OPENAI_API_KEY", "AIGOL_PROVIDER_CREDENTIAL_INPUT"):
        value = os.environ.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise RuntimeError("provider vault source-of-truth certification requires an OpenAI credential in operator env")


def _run_acli(argv: list[str]) -> dict[str, Any]:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_command(args)


def _safe_command_result(result: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(result, dict):
        return None
    artifact = result.get("artifact", {})
    return {
        "command": result.get("command"),
        "operation": result.get("operation"),
        "provider_id": result.get("provider_id"),
        "vault_path": result.get("vault_path"),
        "credential_reference": artifact.get("credential_reference"),
        "credential_source": artifact.get("credential_source"),
        "credential_present": artifact.get("credential_present"),
        "credential_enabled": artifact.get("credential_enabled"),
        "display_identifier": artifact.get("display_identifier"),
        "human_approval_required": artifact.get("human_approval_required"),
        "human_approval_recorded": artifact.get("human_approval_recorded"),
        "replay_reference": result.get("replay_reference"),
    }


def _safe_resolution_summary(resolution: dict[str, Any]) -> dict[str, Any]:
    artifact = resolution.get("retrieval_artifact", {})
    return {
        "provider_id": resolution.get("provider_id"),
        "credential_reference": resolution.get("credential_reference"),
        "credential_source": resolution.get("credential_source"),
        "display_identifier": artifact.get("display_identifier"),
        "credential_present": artifact.get("credential_present"),
        "credential_enabled": artifact.get("credential_enabled"),
        "credential_value_recorded": artifact.get("credential_value_recorded"),
        "credential_hash_recorded": artifact.get("credential_hash_recorded"),
        "authorization_header_recorded": artifact.get("authorization_header_recorded"),
    }


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


def _secret_free(root: Path, secret: str) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        try:
            serialized += canonical_serialize(load_json(path))
        except Exception:
            continue
    return (not secret or secret not in serialized) and "Bearer " not in serialized


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
    write_json_immutable(evidence_dir / "000_provider_vault_source_of_truth_evidence_package.json", evidence)
    write_json_immutable(evidence_dir / "001_provider_vault_source_of_truth_coverage_report.json", coverage)
    write_json_immutable(replay_dir / "000_provider_vault_source_of_truth_replay_package.json", replay)
    write_json_immutable(report_dir / "000_provider_vault_source_of_truth_certification_report.json", report)


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def main() -> int:
    result = run_provider_vault_source_of_truth_certification()
    coverage = result["coverage"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"vault_file_exists={coverage['vault_file_exists']}")
    print(f"credential_source={coverage['credential_source']}")
    print(f"provider_selected={coverage['provider_selected']}")
    print(f"provider_invoked={coverage['provider_invoked']}")
    print(f"provider_response_received={coverage['provider_response_received']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
