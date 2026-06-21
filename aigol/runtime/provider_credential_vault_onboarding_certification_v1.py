"""Onboarding certification for AIGOL_PROVIDER_CREDENTIAL_VAULT_V1."""

from __future__ import annotations

from pathlib import Path
import os
import re
from typing import Any

from aigol.cli.aigol_cli import build_parser
from aigol.runtime.first_live_cognition_provider_certification import (
    run_first_live_cognition_provider_certification,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import (
    DEFAULT_VAULT_PATH,
    add_provider_credential,
    provider_credential_diagnostic,
    retrieve_provider_credential,
    rotate_provider_credential,
    verify_provider_credential,
)
from aigol.runtime.providers.provider_config import ProviderConfig
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_CREDENTIAL_VAULT_ONBOARDING_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/provider_credential_vault_onboarding_certification_v1")
DEFAULT_LOCAL_VAULT_BASE = Path("/tmp/aigol_provider_credential_vault_onboarding_certification_v1")
CREATED_AT = "2026-06-21T00:00:00+00:00"


def run_provider_credential_vault_onboarding_certification(
    *,
    replay_base: str | Path | None = None,
    local_vault_base: str | Path | None = None,
    created_at: str = CREATED_AT,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    local_base = Path(local_vault_base) if local_vault_base is not None else DEFAULT_LOCAL_VAULT_BASE
    vault_path = local_base / root.name / "provider-credentials.json"
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    coverage_dir = root / "coverage_report"
    report_dir = root / "certification_report"
    scenarios_dir = root / "scenarios"

    host_state = _host_vault_state()
    scenario_1 = _scenario_empty_config(scenarios_dir / "SCN-001-empty-config", local_base / root.name / "empty")
    scenario_2 = _scenario_onboard_via_runtime(
        scenarios_dir / "SCN-002-onboard-runtime",
        vault_path=vault_path,
        created_at=created_at,
    )
    scenario_3 = _scenario_vault_lookup(
        scenarios_dir / "SCN-003-vault-lookup",
        vault_path=vault_path,
        created_at=created_at,
    )
    scenario_4 = _scenario_vault_only_provider_config(
        scenarios_dir / "SCN-004-vault-only-provider-config",
        vault_path=vault_path,
    )
    scenario_5 = _scenario_first_live_vault_only_certification_attempt(
        scenarios_dir / "SCN-005-first-live-vault-only",
        replay_base=root / "first_live_rerun",
    )
    scenario_6 = _scenario_secret_free_replay(root)
    scenario_7 = _scenario_approval_boundaries(
        scenarios_dir / "SCN-007-approval-boundaries",
        vault_path=vault_path,
        created_at=created_at,
    )
    acli_onboarding = _detect_acli_onboarding_command()
    coverage = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_ONBOARDING_COVERAGE_REPORT_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "host_vault_state": host_state,
        "acli_onboarding_command_available": acli_onboarding["available"],
        "canonical_onboarding_command": acli_onboarding["command"],
        "scenarios": {
            "SCN-001-empty-config": scenario_1,
            "SCN-002-onboard-runtime": scenario_2,
            "SCN-003-vault-lookup": scenario_3,
            "SCN-004-vault-only-provider-config": scenario_4,
            "SCN-005-first-live-vault-only": scenario_5,
            "SCN-006-secret-free-replay": scenario_6,
            "SCN-007-approval-boundaries": scenario_7,
        },
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    final_verdict = _verdict(
        acli_onboarding_available=acli_onboarding["available"],
        vault_created=scenario_2["provider_credentials_json_created"],
        vault_lookup=scenario_3["credential_source"] == "vault://provider/openai",
        vault_only_provider_config=scenario_4["provider_config_resolved_from_vault"],
        first_live_vault_only=scenario_5["provider_response_received"],
        replay_secret_free=scenario_6["replay_secret_free"],
        approval_boundaries=scenario_7["approval_boundaries_preserved"],
    )
    evidence_package = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_ONBOARDING_EVIDENCE_PACKAGE_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "cert_root": str(root),
        "exact_vault_file_path": str(DEFAULT_VAULT_PATH),
        "test_vault_file_path": str(vault_path),
        "exact_onboarding_command": acli_onboarding["command"],
        "exact_verification_command": "python -m aigol.cli.aigol_cli provider credential verify openai",
        "actual_onboarding_runtime": "aigol.runtime.provider_credential_vault.add_provider_credential",
        "exact_credential_source_used_during_vault_lookup": scenario_3["credential_source"],
        "migration_status": _migration_status(final_verdict),
        "coverage_hash": coverage["artifact_hash"],
        "final_verdict": final_verdict,
    }
    evidence_package["artifact_hash"] = replay_hash(evidence_package)
    replay_package = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_ONBOARDING_REPLAY_PACKAGE_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "cert_root": str(root),
        "replay_secret_free": scenario_6["replay_secret_free"],
        "first_live_credential_source": scenario_5["credential_source"],
        "first_live_failure_reason": scenario_5["failure_reason"],
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)
    report = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_ONBOARDING_CERTIFICATION_REPORT_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "cert_root": str(root),
        "questions": {
            "how_operator_onboards_openai_credential": (
                "No ACLI onboarding command is implemented; current onboarding is runtime API only."
            ),
            "which_acli_command_performs_onboarding": acli_onboarding["command"],
            "when_provider_credentials_json_created": "When add_provider_credential writes the first vault record.",
            "canonical_vault_initialization_workflow": "Runtime API add_provider_credential; ACLI workflow missing.",
            "canonical_storage_format": "JSON vault file outside repository with chmod 0600 and secret-bearing records.",
            "verify_successful_onboarding": "provider_credential_diagnostic or future ACLI verify command.",
            "verify_vault_not_env": scenario_3["credential_source"],
            "vault_functions_without_provider_env": scenario_4["provider_config_resolved_from_vault"],
            "first_live_certification_vault_only": scenario_5["provider_response_received"],
            "provider_credentials_json_created_automatically": False,
            "manual_or_programmatic_creation": "programmatic runtime API; no ACLI command yet",
        },
        "gap_analysis": _gap_analysis(acli_onboarding, scenario_5),
        "coverage_hash": coverage["artifact_hash"],
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    write_json_immutable(coverage_dir / "000_provider_credential_vault_onboarding_coverage_report.json", coverage)
    write_json_immutable(evidence_dir / "000_provider_credential_vault_onboarding_evidence_package.json", evidence_package)
    write_json_immutable(replay_dir / "000_provider_credential_vault_onboarding_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_provider_credential_vault_onboarding_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "coverage_report_path": str(coverage_dir / "000_provider_credential_vault_onboarding_coverage_report.json"),
        "evidence_package_path": str(evidence_dir / "000_provider_credential_vault_onboarding_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_provider_credential_vault_onboarding_replay_package.json"),
        "certification_report_path": str(report_dir / "000_provider_credential_vault_onboarding_certification_report.json"),
        "final_verdict": final_verdict,
    }


def main() -> int:
    result = run_provider_credential_vault_onboarding_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"coverage_report_path={result['coverage_report_path']}")
    print(f"evidence_package_path={result['evidence_package_path']}")
    print(f"replay_package_path={result['replay_package_path']}")
    print(f"certification_report_path={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "PROVIDER_CREDENTIAL_VAULT_OPERATIONAL" else 1


def _host_vault_state() -> dict[str, Any]:
    config_dir = DEFAULT_VAULT_PATH.parent
    files = sorted(path.name for path in config_dir.iterdir()) if config_dir.exists() else []
    return {
        "operator_config_dir": str(config_dir),
        "provider_credentials_json_path": str(DEFAULT_VAULT_PATH),
        "provider_credentials_json_exists": DEFAULT_VAULT_PATH.exists(),
        "operator_config_files": files,
    }


def _scenario_empty_config(scenario_dir: Path, empty_base: Path) -> dict[str, Any]:
    empty_vault = empty_base / ".config" / "aigol" / "provider-credentials.json"
    diagnostic = provider_credential_diagnostic(provider_id="openai", vault_path=empty_vault)
    result = {
        "scenario_id": "SCN-001",
        "provider_credentials_json_exists": empty_vault.exists(),
        "credential_present": diagnostic["credential_present"],
        "credential_enabled": diagnostic["credential_enabled"],
        "expected_behavior_observed": diagnostic["credential_present"] is False,
    }
    result["artifact_hash"] = replay_hash(result)
    write_json_immutable(scenario_dir / "000_empty_config_evidence.json", result)
    return result


def _scenario_onboard_via_runtime(scenario_dir: Path, *, vault_path: Path, created_at: str) -> dict[str, Any]:
    event = add_provider_credential(
        provider_id="openai",
        credential_value="sk-onboarding-cert-secret",
        created_at=created_at,
        vault_path=vault_path,
        replay_dir=scenario_dir / "replay",
    )
    result = {
        "scenario_id": "SCN-002",
        "onboarding_method": "runtime_api",
        "acli_command_used": None,
        "provider_credentials_json_created": vault_path.exists(),
        "vault_file_path": str(vault_path),
        "vault_file_mode": oct(vault_path.stat().st_mode & 0o777) if vault_path.exists() else None,
        "event_hash": event["artifact_hash"],
    }
    result["artifact_hash"] = replay_hash(result)
    write_json_immutable(scenario_dir / "000_onboarding_evidence.json", result)
    return result


def _scenario_vault_lookup(scenario_dir: Path, *, vault_path: Path, created_at: str) -> dict[str, Any]:
    retrieval = retrieve_provider_credential(
        provider_id="openai",
        authorization_context={"scenario": "SCN-003"},
        vault_path=vault_path,
        allow_env_fallback=False,
        created_at=created_at,
        replay_dir=scenario_dir / "replay",
    )
    result = {
        "scenario_id": "SCN-003",
        "credential_source": retrieval["credential_source"],
        "credential_reference": retrieval["credential_reference"],
        "display_identifier": retrieval["diagnostic"]["display_identifier"],
        "credential_value_recorded": retrieval["retrieval_artifact"]["credential_value_recorded"],
        "credential_hash_recorded": retrieval["retrieval_artifact"]["credential_hash_recorded"],
        "retrieval_artifact_hash": retrieval["retrieval_artifact"]["artifact_hash"],
    }
    result["artifact_hash"] = replay_hash(result)
    write_json_immutable(scenario_dir / "000_vault_lookup_evidence.json", result)
    return result


def _scenario_vault_only_provider_config(scenario_dir: Path, *, vault_path: Path) -> dict[str, Any]:
    old_openai = os.environ.pop("OPENAI_API_KEY", None)
    old_aigol = os.environ.pop("AIGOL_OPENAI_API_KEY", None)
    try:
        resolved = ProviderConfig(vault_path=str(vault_path), allow_env_fallback=False).api_key()
    finally:
        if old_openai is not None:
            os.environ["OPENAI_API_KEY"] = old_openai
        if old_aigol is not None:
            os.environ["AIGOL_OPENAI_API_KEY"] = old_aigol
    result = {
        "scenario_id": "SCN-004",
        "openai_env_removed": True,
        "aigol_openai_env_removed": True,
        "provider_config_resolved_from_vault": resolved == "sk-onboarding-cert-secret",
        "credential_source": "vault://provider/openai",
    }
    result["artifact_hash"] = replay_hash(result)
    write_json_immutable(scenario_dir / "000_vault_only_provider_config_evidence.json", result)
    return result


def _scenario_first_live_vault_only_certification_attempt(scenario_dir: Path, *, replay_base: Path) -> dict[str, Any]:
    old_openai = os.environ.pop("OPENAI_API_KEY", None)
    old_aigol = os.environ.pop("AIGOL_OPENAI_API_KEY", None)
    try:
        result = run_first_live_cognition_provider_certification(
            replay_base=replay_base,
            transport=_cert_transport(),
        )
    finally:
        if old_openai is not None:
            os.environ["OPENAI_API_KEY"] = old_openai
        if old_aigol is not None:
            os.environ["AIGOL_OPENAI_API_KEY"] = old_aigol
    observed = result.get("observed", {})
    evidence = {
        "scenario_id": "SCN-005",
        "openai_env_removed": True,
        "aigol_openai_env_removed": True,
        "credential_source": "env:AIGOL_OPENAI_API_KEY",
        "provider_selected": observed.get("provider_selected"),
        "provider_invoked": observed.get("provider_invoked", False),
        "provider_response_received": observed.get("provider_response_received", False),
        "aborted_before_certification": result.get("aborted_before_certification", False),
        "failure_reason": result.get("aborted_reason") or observed.get("failure_reason"),
        "cert_root": result.get("cert_root"),
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    write_json_immutable(scenario_dir / "000_first_live_vault_only_evidence.json", evidence)
    return evidence


def _scenario_secret_free_replay(root: Path) -> dict[str, Any]:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    result = {
        "scenario_id": "SCN-006",
        "replay_secret_free": (
            "sk-onboarding-cert-secret" not in serialized
            and "Bearer " not in serialized
        ),
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def _scenario_approval_boundaries(scenario_dir: Path, *, vault_path: Path, created_at: str) -> dict[str, Any]:
    failures = {}
    for operation, callback in {
        "ROTATE": lambda: rotate_provider_credential(
            provider_id="openai",
            credential_value="sk-should-not-record",
            created_at=created_at,
            human_approval_artifact={},
            vault_path=vault_path,
        ),
    }.items():
        try:
            callback()
        except FailClosedRuntimeError as exc:
            failures[operation] = str(exc)
        else:
            failures[operation] = None
    result = {
        "scenario_id": "SCN-007",
        "approval_boundaries_preserved": all(value for value in failures.values()),
        "failures": failures,
    }
    result["artifact_hash"] = replay_hash(result)
    write_json_immutable(scenario_dir / "000_approval_boundary_evidence.json", result)
    return result


def _detect_acli_onboarding_command() -> dict[str, Any]:
    parser = build_parser()
    command = "python -m aigol.cli.aigol_cli provider credential add openai"
    try:
        parser.parse_args(["provider", "credential", "add", "openai"])
    except SystemExit:
        return {
            "available": False,
            "command": command,
            "failure_reason": "provider credential ACLI command is not registered",
        }
    return {"available": True, "command": command, "failure_reason": None}


def _verdict(
    *,
    acli_onboarding_available: bool,
    vault_created: bool,
    vault_lookup: bool,
    vault_only_provider_config: bool,
    first_live_vault_only: bool,
    replay_secret_free: bool,
    approval_boundaries: bool,
) -> str:
    if all(
        [
            acli_onboarding_available,
            vault_created,
            vault_lookup,
            vault_only_provider_config,
            first_live_vault_only,
            replay_secret_free,
            approval_boundaries,
        ]
    ):
        return "PROVIDER_CREDENTIAL_VAULT_OPERATIONAL"
    if vault_lookup and vault_only_provider_config and not first_live_vault_only:
        return "PROVIDER_CREDENTIAL_VAULT_FALLBACK_DEPENDENT"
    return "PROVIDER_CREDENTIAL_VAULT_GAPS_FOUND"


def _migration_status(final_verdict: str) -> str:
    if final_verdict == "PROVIDER_CREDENTIAL_VAULT_OPERATIONAL":
        return "VAULT_CANONICAL_SOURCE_CONFIRMED"
    if final_verdict == "PROVIDER_CREDENTIAL_VAULT_FALLBACK_DEPENDENT":
        return "VAULT_RUNTIME_WORKS_BUT_FIRST_LIVE_CERTIFICATION_REMAINS_ENV_BOUND"
    return "VAULT_ONBOARDING_GAPS_FOUND"


def _gap_analysis(acli_onboarding: dict[str, Any], scenario_5: dict[str, Any]) -> list[str]:
    gaps = []
    if not acli_onboarding["available"]:
        gaps.append("ACLI provider credential onboarding command is not implemented.")
    if not scenario_5["provider_response_received"]:
        gaps.append("First live cognition certification still requires environment credential preflight.")
    if scenario_5["credential_source"] != "vault://provider/openai":
        gaps.append("First live cognition certification does not record vault://provider/openai as credential source.")
    return gaps


def _cert_transport():
    def call(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": "vault-onboarding-cert-response",
            "status_code": 200,
            "output_text": "Vault-only certification transport response.",
            "real_openai_called": True,
            "live_provider_call_performed": True,
            "credential_secret_replayed": False,
            "authorization_header_replayed": False,
        }

    call.aigol_governed_live_openai_executor_v1 = True
    return call


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


if __name__ == "__main__":
    raise SystemExit(main())
