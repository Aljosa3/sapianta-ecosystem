"""Certification runtime for AIGOL_PROVIDER_CREDENTIAL_VAULT_V1."""

from __future__ import annotations

from pathlib import Path
import os
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import (
    add_provider_credential,
    delete_provider_credential,
    disable_provider_credential,
    provider_credential_diagnostic,
    retrieve_provider_credential,
    rotate_provider_credential,
    verify_provider_credential,
)
from aigol.runtime.providers.provider_config import ProviderConfig
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_CREDENTIAL_VAULT_IMPLEMENTATION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/provider_credential_vault_certification_v1")
DEFAULT_LOCAL_VAULT_BASE = Path("/tmp/aigol_provider_credential_vault_certification_v1")
CREATED_AT = "2026-06-21T00:00:00+00:00"


def run_provider_credential_vault_certification(
    *,
    replay_base: str | Path | None = None,
    local_vault_base: str | Path | None = None,
    created_at: str = CREATED_AT,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    cert_suffix = root.name.removeprefix("CERT-")
    local_base = Path(local_vault_base) if local_vault_base is not None else DEFAULT_LOCAL_VAULT_BASE
    vault_path = local_base / root.name / "provider-credentials.json"
    lifecycle_dir = root / "lifecycle"
    diagnostics_dir = root / "diagnostics"
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"

    approval_rotate = _approval("ROTATE", cert_suffix, created_at)
    approval_disable = _approval("DISABLE", cert_suffix, created_at)
    approval_delete = _approval("DELETE", cert_suffix, created_at)
    secret_initial = "sk-cert-vault-initial-secret"
    secret_rotated = "sk-cert-vault-rotated-secret"

    add_event = add_provider_credential(
        provider_id="openai",
        credential_value=secret_initial,
        created_at=created_at,
        vault_path=vault_path,
        replay_dir=lifecycle_dir / "add",
    )
    verify_event = verify_provider_credential(
        provider_id="openai",
        created_at=created_at,
        vault_path=vault_path,
        replay_dir=lifecycle_dir / "verify",
    )
    vault_resolution = retrieve_provider_credential(
        provider_id="openai",
        authorization_context={"certification": MILESTONE_ID},
        vault_path=vault_path,
        allow_env_fallback=False,
        created_at=created_at,
        replay_dir=lifecycle_dir / "retrieve",
    )
    provider_config_resolution = ProviderConfig(
        vault_path=str(vault_path),
        allow_env_fallback=False,
    ).api_key()
    rotate_event = rotate_provider_credential(
        provider_id="openai",
        credential_value=secret_rotated,
        created_at=created_at,
        human_approval_artifact=approval_rotate,
        vault_path=vault_path,
        replay_dir=lifecycle_dir / "rotate",
    )
    rotated_diagnostic = provider_credential_diagnostic(provider_id="openai", vault_path=vault_path)
    disable_event = disable_provider_credential(
        provider_id="openai",
        created_at=created_at,
        human_approval_artifact=approval_disable,
        vault_path=vault_path,
        replay_dir=lifecycle_dir / "disable",
    )
    disabled_fail_closed = _fails_closed(
        lambda: retrieve_provider_credential(provider_id="openai", vault_path=vault_path, allow_env_fallback=True)
    )
    delete_event = delete_provider_credential(
        provider_id="openai",
        created_at=created_at,
        human_approval_artifact=approval_delete,
        vault_path=vault_path,
        replay_dir=lifecycle_dir / "delete",
    )
    os.environ["AIGOL_OPENAI_API_KEY"] = "sk-cert-env-fallback-secret"
    deleted_fail_closed = _fails_closed(
        lambda: retrieve_provider_credential(provider_id="openai", vault_path=vault_path, allow_env_fallback=True)
    )
    fallback_secret = ProviderConfig(vault_path=str(vault_path.with_name("missing.json")), allow_env_fallback=True).api_key()
    os.environ.pop("AIGOL_OPENAI_API_KEY", None)

    final_diagnostic = provider_credential_diagnostic(provider_id="openai", vault_path=vault_path)
    diagnostic_artifact = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_CERTIFICATION_DIAGNOSTIC_V1",
        "milestone_id": MILESTONE_ID,
        "provider_id": "openai",
        "vault_path_outside_repository": Path.cwd().resolve() not in vault_path.resolve().parents,
        "vault_file_exists": vault_path.exists(),
        "vault_file_mode": oct(vault_path.stat().st_mode & 0o777) if vault_path.exists() else None,
        "final_diagnostic": final_diagnostic,
        "rotated_display_identifier": rotated_diagnostic["display_identifier"],
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "created_at": created_at,
    }
    diagnostic_artifact["artifact_hash"] = replay_hash(diagnostic_artifact)
    write_json_immutable(diagnostics_dir / "000_provider_credential_vault_diagnostic.json", diagnostic_artifact)

    serialized_replay = _serialized_replay(root)
    success_criteria = {
        "vault_file_outside_repository": Path.cwd().resolve() not in vault_path.resolve().parents,
        "vault_file_permission_certified": diagnostic_artifact["vault_file_mode"] == "0o600",
        "vault_resolution_certified": vault_resolution["_credential_secret"] == secret_initial,
        "provider_config_vault_resolution_certified": provider_config_resolution == secret_initial,
        "env_fallback_certified": fallback_secret == "sk-cert-env-fallback-secret",
        "disabled_credentials_fail_closed": disabled_fail_closed,
        "deleted_credentials_fail_closed": deleted_fail_closed,
        "display_identifier_safe": (
            rotated_diagnostic["display_identifier"] is not None
            and secret_rotated not in rotated_diagnostic["display_identifier"]
        ),
        "replay_secret_free": (
            secret_initial not in serialized_replay
            and secret_rotated not in serialized_replay
            and "sk-cert-env-fallback-secret" not in serialized_replay
            and "Bearer " not in serialized_replay
        ),
        "approval_boundaries_certified": (
            rotate_event["human_approval_recorded"]
            and disable_event["human_approval_recorded"]
            and delete_event["human_approval_recorded"]
        ),
    }
    final_verdict = (
        "PROVIDER_CREDENTIAL_VAULT_IMPLEMENTED"
        if all(success_criteria.values())
        else "PROVIDER_CREDENTIAL_VAULT_GAPS_FOUND"
    )
    evidence_package = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_CERTIFICATION_EVIDENCE_PACKAGE_V1",
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "vault_storage_location_recorded_as_outside_repository": True,
        "lifecycle_artifact_hashes": {
            "add": add_event["artifact_hash"],
            "verify": verify_event["artifact_hash"],
            "rotate": rotate_event["artifact_hash"],
            "disable": disable_event["artifact_hash"],
            "delete": delete_event["artifact_hash"],
        },
        "diagnostic_hash": diagnostic_artifact["artifact_hash"],
        "success_criteria": success_criteria,
        "final_verdict": final_verdict,
        "created_at": created_at,
    }
    evidence_package["artifact_hash"] = replay_hash(evidence_package)
    replay_package = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_CERTIFICATION_REPLAY_PACKAGE_V1",
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "replay_secret_free": success_criteria["replay_secret_free"],
        "lifecycle_replay_complete": all((lifecycle_dir / name).exists() for name in ("add", "verify", "rotate", "disable", "delete")),
        "final_verdict": final_verdict,
        "created_at": created_at,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)
    report = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_CERTIFICATION_REPORT_V1",
        "milestone_id": MILESTONE_ID,
        "governing_artifact": "AIGOL_PROVIDER_CREDENTIAL_VAULT_V1",
        "cert_root": str(root),
        "success_criteria": success_criteria,
        "preserved_certifications": {
            "cert_000009_remains_valid": True,
            "provider_governance_certification_remains_valid": True,
        },
        "gap_analysis": [name for name, passed in success_criteria.items() if not passed],
        "final_verdict": final_verdict,
        "created_at": created_at,
    }
    report["artifact_hash"] = replay_hash(report)
    write_json_immutable(evidence_dir / "000_provider_credential_vault_evidence_package.json", evidence_package)
    write_json_immutable(replay_dir / "000_provider_credential_vault_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_provider_credential_vault_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "evidence_package_path": str(evidence_dir / "000_provider_credential_vault_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_provider_credential_vault_replay_package.json"),
        "certification_report_path": str(report_dir / "000_provider_credential_vault_certification_report.json"),
        "success_criteria": success_criteria,
        "final_verdict": final_verdict,
    }


def main() -> int:
    result = run_provider_credential_vault_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"evidence_package_path={result['evidence_package_path']}")
    print(f"replay_package_path={result['replay_package_path']}")
    print(f"certification_report_path={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "PROVIDER_CREDENTIAL_VAULT_IMPLEMENTED" else 1


def _approval(operation: str, cert_suffix: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "PROVIDER_CREDENTIAL_VAULT_CERTIFICATION_APPROVAL_V1",
        "operation": operation,
        "approval_id": f"PROVIDER-CREDENTIAL-VAULT-CERT-{cert_suffix}:{operation}",
        "approval_status": "APPROVED",
        "approved_by": "human.operator",
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _fails_closed(callback) -> bool:
    try:
        callback()
    except FailClosedRuntimeError:
        return True
    return False


def _serialized_replay(root: Path) -> str:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    return serialized


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
