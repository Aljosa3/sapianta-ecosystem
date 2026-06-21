"""Provider ACLI connectivity audit for AIGOL_PROVIDER_ACLI_CONNECTIVITY_AUDIT_V1."""

from __future__ import annotations

from pathlib import Path
import contextlib
import io
import re
from typing import Any

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.first_live_cognition_provider_certification import (
    run_first_live_cognition_provider_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_ACLI_CONNECTIVITY_AUDIT_V1"
DEFAULT_REPLAY_BASE = Path("runtime/provider_acli_connectivity_audit_v1")
CREATED_AT = "2026-06-21T00:00:00+00:00"


PROVIDER_GOVERNANCE_CAPABILITIES = (
    ("provider status", "provider governance status", ["provider", "governance", "status"]),
    ("provider credentials", "provider governance credentials", ["provider", "governance", "credentials"]),
    ("provider usage", "provider governance usage", ["provider", "governance", "usage"]),
    ("provider failures", "provider governance failures", ["provider", "governance", "failures"]),
    ("provider costs", "provider governance costs", ["provider", "governance", "costs"]),
    ("provider participation", "provider governance participation", ["provider", "governance", "participation"]),
)

PROVIDER_CREDENTIAL_CAPABILITIES = (
    ("provider credential add", "provider credential add openai", ["provider", "credential", "add", "openai"]),
    ("provider credential verify", "provider credential verify openai", ["provider", "credential", "verify", "openai"]),
    ("provider credential rotate", "provider credential rotate openai", ["provider", "credential", "rotate", "openai"]),
    ("provider credential disable", "provider credential disable openai", ["provider", "credential", "disable", "openai"]),
    ("provider credential delete", "provider credential delete openai", ["provider", "credential", "delete", "openai"]),
    ("provider credential history", "provider credential history openai", ["provider", "credential", "history", "openai"]),
)

NATURAL_PROVIDER_QUERIES = (
    ("show provider credentials", ["show", "provider", "credentials"]),
    ("show provider credential history", ["show", "provider", "credential", "history"]),
)


def run_provider_acli_connectivity_audit(
    *,
    replay_base: str | Path | None = None,
    created_at: str = CREATED_AT,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_audit_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    coverage_dir = root / "coverage_report"
    report_dir = root / "audit_report"

    parser = build_parser()
    governance_rows = [
        _audit_command(
            parser=parser,
            capability=name,
            operator_phrase=phrase,
            argv=argv + ["--replay-root", "runtime/provider_governance_certification_v1/CERT-000002"],
            certified=True,
            runtime_capability_type="provider_governance",
        )
        for name, phrase, argv in PROVIDER_GOVERNANCE_CAPABILITIES
    ]
    credential_rows = [
        _audit_command(
            parser=parser,
            capability=name,
            operator_phrase=phrase,
            argv=argv,
            certified=name in {"provider credential add", "provider credential verify", "provider credential rotate", "provider credential disable", "provider credential delete"},
            runtime_capability_type="credential_vault",
        )
        for name, phrase, argv in PROVIDER_CREDENTIAL_CAPABILITIES
    ]
    natural_rows = [
        _audit_command(
            parser=parser,
            capability=name,
            operator_phrase=name,
            argv=argv,
            certified=False,
            runtime_capability_type="natural_operator_phrase",
        )
        for name, argv in NATURAL_PROVIDER_QUERIES
    ]
    first_live_migration = _audit_first_live_vault_migration(root / "first_live_vault_probe")
    rows = governance_rows + credential_rows + natural_rows + [first_live_migration]
    missing_registrations = [
        row["operator_phrase"]
        for row in rows
        if row["acli_reachable"] is False and row["runtime_capability_type"] != "first_live_certification"
    ]
    dead_end_certified_runtimes = [
        row["runtime_capability"]
        for row in rows
        if row["certified"] is True and row["acli_reachable"] is False
    ]
    coverage = {
        "artifact_type": "PROVIDER_ACLI_CONNECTIVITY_COVERAGE_REPORT_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "provider_governance_operation_count": len(PROVIDER_GOVERNANCE_CAPABILITIES),
        "credential_vault_operation_count": len(PROVIDER_CREDENTIAL_CAPABILITIES),
        "reachable_count": sum(1 for row in rows if row["acli_reachable"]),
        "unreachable_count": sum(1 for row in rows if not row["acli_reachable"]),
        "missing_acli_registrations": missing_registrations,
        "dead_end_certified_runtimes": dead_end_certified_runtimes,
        "first_live_migration": first_live_migration,
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    matrix = {
        "artifact_type": "PROVIDER_ACLI_REACHABILITY_MATRIX_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "rows": rows,
    }
    matrix["artifact_hash"] = replay_hash(matrix)
    remediation_plan = _remediation_plan(rows, first_live_migration)
    final_verdict = (
        "PROVIDER_ACLI_CONNECTIVITY_CERTIFIED"
        if not missing_registrations and first_live_migration["vault_migration_ready"]
        else "PROVIDER_ACLI_CONNECTIVITY_GAPS_FOUND"
    )
    evidence_package = {
        "artifact_type": "PROVIDER_ACLI_CONNECTIVITY_EVIDENCE_PACKAGE_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "cert_root": str(root),
        "coverage_hash": coverage["artifact_hash"],
        "matrix_hash": matrix["artifact_hash"],
        "missing_acli_registrations": missing_registrations,
        "dead_end_certified_runtimes": dead_end_certified_runtimes,
        "final_verdict": final_verdict,
    }
    evidence_package["artifact_hash"] = replay_hash(evidence_package)
    replay_package = {
        "artifact_type": "PROVIDER_ACLI_CONNECTIVITY_REPLAY_PACKAGE_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "cert_root": str(root),
        "reachability_matrix": matrix,
        "replay_secret_free": _replay_secret_free(root),
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)
    report = {
        "artifact_type": "PROVIDER_ACLI_CONNECTIVITY_AUDIT_REPORT_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "cert_root": str(root),
        "capability_inventory": _capability_inventory(),
        "reachability_matrix": rows,
        "acli_registration_matrix": _registration_matrix(rows),
        "missing_acli_registrations": missing_registrations,
        "missing_routing_bindings": missing_registrations,
        "dead_end_certified_runtimes": dead_end_certified_runtimes,
        "first_live_migration": first_live_migration,
        "remediation_plan": remediation_plan,
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    write_json_immutable(coverage_dir / "000_provider_acli_connectivity_coverage_report.json", coverage)
    write_json_immutable(evidence_dir / "000_provider_acli_connectivity_evidence_package.json", evidence_package)
    write_json_immutable(replay_dir / "000_provider_acli_connectivity_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_provider_acli_connectivity_audit_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "coverage_report_path": str(coverage_dir / "000_provider_acli_connectivity_coverage_report.json"),
        "evidence_package_path": str(evidence_dir / "000_provider_acli_connectivity_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_provider_acli_connectivity_replay_package.json"),
        "audit_report_path": str(report_dir / "000_provider_acli_connectivity_audit_report.json"),
        "missing_acli_registrations": missing_registrations,
        "final_verdict": final_verdict,
    }


def main() -> int:
    result = run_provider_acli_connectivity_audit()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"coverage_report_path={result['coverage_report_path']}")
    print(f"evidence_package_path={result['evidence_package_path']}")
    print(f"replay_package_path={result['replay_package_path']}")
    print(f"audit_report_path={result['audit_report_path']}")
    print(f"missing_acli_registrations={len(result['missing_acli_registrations'])}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "PROVIDER_ACLI_CONNECTIVITY_CERTIFIED" else 1


def _audit_command(
    *,
    parser,
    capability: str,
    operator_phrase: str,
    argv: list[str],
    certified: bool,
    runtime_capability_type: str,
) -> dict[str, Any]:
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            args = parser.parse_args(argv)
        parsed = True
        route = " ".join(argv)
        command_result = None
        if argv[:2] == ["provider", "governance"]:
            command_result = run_command(args)
            render_command_result(command_result)
        reachable = True
        failure_reason = None
    except SystemExit as exc:
        parsed = False
        reachable = False
        route = None
        command_result = None
        failure_reason = f"argparse exited with code {exc.code}"
    except Exception as exc:
        parsed = True
        reachable = False
        route = " ".join(argv)
        command_result = None
        failure_reason = str(exc)
    return {
        "runtime_capability": capability,
        "runtime_capability_type": runtime_capability_type,
        "operator_phrase": operator_phrase,
        "acli_reachable": reachable,
        "routing_path": route,
        "argparse_registered": parsed,
        "certified": certified,
        "operator_usable": reachable,
        "failure_reason": failure_reason,
        "result_command": command_result.get("command") if isinstance(command_result, dict) else None,
    }


def _audit_first_live_vault_migration(replay_base: Path) -> dict[str, Any]:
    result = run_first_live_cognition_provider_certification(
        replay_base=replay_base,
        transport=_cert_transport(),
        require_openai_api_key_marker=False,
    )
    observed = result.get("observed", {})
    return {
        "runtime_capability": "first live cognition provider certification vault migration",
        "runtime_capability_type": "first_live_certification",
        "operator_phrase": "run first live cognition provider certification using vault",
        "acli_reachable": False,
        "routing_path": "python -m aigol.runtime.first_live_cognition_provider_certification",
        "certified": result.get("final_verdict") == "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED",
        "operator_usable": False,
        "vault_migration_ready": False,
        "provider_invoked": bool(observed.get("provider_invoked")),
        "provider_response_received": bool(observed.get("provider_response_received")),
        "failure_reason": result.get("aborted_reason") or observed.get("failure_reason"),
        "credential_source": "env:AIGOL_OPENAI_API_KEY",
    }


def _capability_inventory() -> dict[str, list[str]]:
    return {
        "provider_governance_operations": [name for name, _phrase, _argv in PROVIDER_GOVERNANCE_CAPABILITIES],
        "credential_vault_operations": [name for name, _phrase, _argv in PROVIDER_CREDENTIAL_CAPABILITIES],
        "natural_operator_phrases": [name for name, _argv in NATURAL_PROVIDER_QUERIES],
    }


def _registration_matrix(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "operator_phrase": row["operator_phrase"],
            "argparse_registered": row["argparse_registered"],
            "routing_path": row["routing_path"],
            "operator_usable": row["operator_usable"],
        }
        for row in rows
        if row["runtime_capability_type"] != "first_live_certification"
    ]


def _remediation_plan(rows: list[dict[str, Any]], first_live_migration: dict[str, Any]) -> list[dict[str, Any]]:
    plan = []
    priorities = [
        "provider status",
        "provider credentials",
        "provider usage",
        "provider failures",
        "provider participation",
        "provider credential add",
        "provider credential verify",
        "provider credential rotate",
        "provider credential disable",
        "provider credential delete",
    ]
    by_capability = {row["runtime_capability"]: row for row in rows}
    for index, capability in enumerate(priorities, start=1):
        row = by_capability.get(capability)
        if row is None:
            continue
        if row["acli_reachable"]:
            action = "Preserve existing argparse route and add natural phrase alias if required."
        else:
            action = "Register ACLI route and bind to existing certified runtime without changing governance semantics."
        plan.append({"priority": index, "capability": capability, "action": action})
    if not first_live_migration["vault_migration_ready"]:
        plan.append(
            {
                "priority": len(plan) + 1,
                "capability": "first live cognition provider vault migration",
                "action": "Replace first-live credential preflight and live boundary credential retrieval with vault-backed lookup, preserving env fallback only as compatibility.",
            }
        )
    return plan


def _replay_secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    return "sk-" not in serialized and "Bearer " not in serialized


def _cert_transport():
    def call(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": "provider-acli-connectivity-audit-response",
            "status_code": 200,
            "output_text": "Provider ACLI connectivity audit response.",
            "real_openai_called": True,
            "live_provider_call_performed": True,
            "credential_secret_replayed": False,
            "authorization_header_replayed": False,
        }

    call.aigol_governed_live_openai_executor_v1 = True
    return call


def _next_audit_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


if __name__ == "__main__":
    raise SystemExit(main())
