"""Certification runtime for AIGOL_PROVIDER_GOVERNANCE_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.operator_environment_bootstrap import verify_operator_environment
from aigol.runtime.provider_governance_runtime import (
    build_provider_credential_diagnostic,
    execute_provider_lifecycle_operation,
    record_cognition_participation,
    record_provider_usage_metric,
    reconstruct_provider_governance_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_GOVERNANCE_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/provider_governance_certification_v1")
CREATED_AT = "2026-06-21T00:00:00+00:00"
REFERENCE_CERT_000009 = Path("runtime/first_live_cognition_provider_certification_v1/CERT-000009")


def run_provider_governance_certification(
    *,
    replay_base: str | Path | None = None,
    created_at: str = CREATED_AT,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    cert_suffix = root.name.removeprefix("CERT-")
    lifecycle_dir = root / "lifecycle"
    approval_dir = root / "approval_enforcement"
    observability_dir = root / "observability"
    acli_dir = root / "acli_queries"
    coverage_dir = root / "coverage_report"
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"

    env = {
        "AIGOL_OPENAI_API_KEY": "operator-safe-present-marker",
        "OPENAI_API_KEY": "operator-safe-present-marker",
    }
    lifecycle_results = _execute_lifecycle_campaign(
        lifecycle_dir=lifecycle_dir,
        cert_suffix=cert_suffix,
        created_at=created_at,
        env=env,
    )
    approval_results = _execute_approval_enforcement_campaign(
        approval_dir=approval_dir,
        cert_suffix=cert_suffix,
        created_at=created_at,
    )
    observability_results = _execute_observability_campaign(
        observability_dir=observability_dir,
        cert_suffix=cert_suffix,
        created_at=created_at,
    )
    replay_reconstruction = reconstruct_provider_governance_replay(root)
    credential_diagnostic = build_provider_credential_diagnostic(provider_id="openai", env=env)
    bootstrap_verification = verify_operator_environment(provider_id="openai", env=env)
    acli_results = _execute_acli_query_campaign(acli_dir=acli_dir, replay_root=root)

    coverage = _build_coverage_report(
        created_at=created_at,
        lifecycle_results=lifecycle_results,
        approval_results=approval_results,
        observability_results=observability_results,
        replay_reconstruction=replay_reconstruction,
        credential_diagnostic=credential_diagnostic,
        bootstrap_verification=bootstrap_verification,
        acli_results=acli_results,
    )
    success_criteria = _evaluate_success_criteria(
        coverage=coverage,
        replay_reconstruction=replay_reconstruction,
        credential_diagnostic=credential_diagnostic,
        bootstrap_verification=bootstrap_verification,
        acli_results=acli_results,
    )
    final_verdict = (
        "PROVIDER_GOVERNANCE_CERTIFIED"
        if all(success_criteria.values())
        else "PROVIDER_GOVERNANCE_GAPS_FOUND"
    )
    evidence_package = _build_evidence_package(
        root=root,
        created_at=created_at,
        coverage=coverage,
        replay_reconstruction=replay_reconstruction,
        credential_diagnostic=credential_diagnostic,
        bootstrap_verification=bootstrap_verification,
        acli_results=acli_results,
        final_verdict=final_verdict,
    )
    replay_package = _build_replay_package(
        root=root,
        created_at=created_at,
        replay_reconstruction=replay_reconstruction,
        acli_results=acli_results,
        final_verdict=final_verdict,
    )
    report = _build_certification_report(
        root=root,
        created_at=created_at,
        coverage=coverage,
        success_criteria=success_criteria,
        final_verdict=final_verdict,
    )
    _persist_certification_artifacts(
        coverage_dir=coverage_dir,
        evidence_dir=evidence_dir,
        replay_dir=replay_dir,
        report_dir=report_dir,
        coverage=coverage,
        evidence_package=evidence_package,
        replay_package=replay_package,
        report=report,
    )
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "coverage_report_path": str(coverage_dir / "000_provider_governance_coverage_report.json"),
        "evidence_package_path": str(evidence_dir / "000_provider_governance_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_provider_governance_replay_package.json"),
        "certification_report_path": str(report_dir / "000_provider_governance_certification_report.json"),
        "success_criteria": success_criteria,
        "final_verdict": final_verdict,
    }


def main() -> int:
    result = run_provider_governance_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"coverage_report_path={result['coverage_report_path']}")
    print(f"evidence_package_path={result['evidence_package_path']}")
    print(f"replay_package_path={result['replay_package_path']}")
    print(f"certification_report_path={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "PROVIDER_GOVERNANCE_CERTIFIED" else 1


def _execute_lifecycle_campaign(
    *,
    lifecycle_dir: Path,
    cert_suffix: str,
    created_at: str,
    env: dict[str, str],
) -> list[dict[str, Any]]:
    operations = ("VERIFY", "ENABLE", "DISABLE", "ROTATE", "DELETE")
    results = []
    for operation in operations:
        approval = None
        if operation in {"DISABLE", "ROTATE", "DELETE"}:
            approval = _approval_artifact(operation=operation, cert_suffix=cert_suffix, created_at=created_at)
        event = execute_provider_lifecycle_operation(
            event_id=f"PROVIDER-GOVERNANCE-CERT-{cert_suffix}:{operation}",
            operation=operation,
            provider_id="openai",
            requested_by="human.operator",
            created_at=created_at,
            replay_dir=lifecycle_dir / operation.lower(),
            human_approval_artifact=approval,
            reason=f"Provider governance certification {operation}",
            env=env,
        )
        results.append(
            {
                "operation": operation,
                "passed": True,
                "human_approval_required": event["human_approval_required"],
                "human_approval_recorded": event["human_approval_recorded"],
                "lifecycle_status": event["lifecycle_status"],
                "artifact_hash": event["artifact_hash"],
            }
        )
    return results


def _execute_approval_enforcement_campaign(
    *,
    approval_dir: Path,
    cert_suffix: str,
    created_at: str,
) -> list[dict[str, Any]]:
    results = []
    for operation in ("DISABLE", "ROTATE", "DELETE", "REPLACE"):
        try:
            execute_provider_lifecycle_operation(
                event_id=f"PROVIDER-GOVERNANCE-CERT-{cert_suffix}:UNAPPROVED-{operation}",
                operation=operation,
                provider_id="openai",
                requested_by="human.operator",
                created_at=created_at,
                replay_dir=approval_dir / operation.lower(),
            )
        except FailClosedRuntimeError as exc:
            result = {
                "artifact_type": "PROVIDER_GOVERNANCE_APPROVAL_ENFORCEMENT_EVIDENCE_V1",
                "operation": operation,
                "approval_missing": True,
                "failed_closed": True,
                "failure_reason": str(exc),
                "created_at": created_at,
            }
            result["artifact_hash"] = replay_hash(result)
            write_json_immutable(approval_dir / operation.lower() / "000_approval_enforcement.json", result)
            results.append(result)
        else:
            results.append(
                {
                    "operation": operation,
                    "approval_missing": True,
                    "failed_closed": False,
                    "failure_reason": "",
                    "created_at": created_at,
                }
            )
    return results


def _execute_observability_campaign(
    *,
    observability_dir: Path,
    cert_suffix: str,
    created_at: str,
) -> dict[str, Any]:
    success_metric = record_provider_usage_metric(
        metric_id=f"PROVIDER-GOVERNANCE-CERT-{cert_suffix}:USAGE-SUCCESS",
        provider_id="openai",
        model="gpt-5.1",
        status="SUCCESS",
        availability="AVAILABLE",
        success_count=1,
        failure_count=0,
        last_used=created_at,
        latency_ms=410,
        token_usage={"input_tokens": 24, "output_tokens": 18},
        cost_tracking={"hook_status": "AVAILABLE_FOR_COST_ACCOUNTING"},
        created_at=created_at,
        replay_dir=observability_dir / "usage_success",
    )
    failure_metric = record_provider_usage_metric(
        metric_id=f"PROVIDER-GOVERNANCE-CERT-{cert_suffix}:USAGE-FAILURE",
        provider_id="openai",
        model="gpt-5.1",
        status="FAILED",
        availability="DEPENDENCY_UNAVAILABLE",
        success_count=0,
        failure_count=1,
        last_failure="certification simulated dependency failure",
        latency_ms=0,
        token_usage={"input_tokens": 0, "output_tokens": 0},
        cost_tracking={"hook_status": "NO_COST_RECORDED_FOR_FAILED_ATTEMPT"},
        created_at=created_at,
        replay_dir=observability_dir / "usage_failure",
    )
    participation = record_cognition_participation(
        participation_id=f"PROVIDER-GOVERNANCE-CERT-{cert_suffix}:PARTICIPATION",
        provider_id="openai",
        participation_location="OCS_LLM_COGNITION",
        participation_role="proposal_only_cognition",
        workflow_id="OCS_LLM_COGNITION",
        invocation_reason="provider governance certification observability probe",
        purpose="certify cognition participation replay visibility",
        response_used=True,
        worker_invoked_after=False,
        human_confirmation_required=True,
        created_at=created_at,
        replay_dir=observability_dir / "participation",
    )
    return {
        "success_metric_hash": success_metric["artifact_hash"],
        "failure_metric_hash": failure_metric["artifact_hash"],
        "participation_hash": participation["artifact_hash"],
    }


def _execute_acli_query_campaign(*, acli_dir: Path, replay_root: Path) -> dict[str, dict[str, Any]]:
    results = {}
    for query_name in ("status", "credentials", "usage", "failures", "costs", "participation"):
        args = build_parser().parse_args(
            ["provider", "governance", query_name, "--replay-root", str(replay_root)]
        )
        result = run_command(args)
        rendered = render_command_result(result)
        query_capture = {
            "artifact_type": "PROVIDER_GOVERNANCE_ACLI_QUERY_EVIDENCE_V1",
            "query_name": query_name,
            "command": result["command"],
            "row_count": len(result["rows"]),
            "rendered_summary": rendered,
            "replay_visible": result["replay_visible"],
        }
        query_capture["artifact_hash"] = replay_hash(query_capture)
        write_json_immutable(acli_dir / query_name / "000_acli_query_evidence.json", query_capture)
        results[query_name] = query_capture
    return results


def _build_coverage_report(
    *,
    created_at: str,
    lifecycle_results: list[dict[str, Any]],
    approval_results: list[dict[str, Any]],
    observability_results: dict[str, Any],
    replay_reconstruction: dict[str, Any],
    credential_diagnostic: dict[str, Any],
    bootstrap_verification: dict[str, Any],
    acli_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    lifecycle_operations = {item["operation"]: item["passed"] for item in lifecycle_results}
    approval_operations = {item["operation"]: item["failed_closed"] for item in approval_results}
    coverage = {
        "artifact_type": "PROVIDER_GOVERNANCE_CERTIFICATION_COVERAGE_REPORT_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "governing_artifacts": [
            "AIGOL_PROVIDER_GOVERNANCE_RUNTIME_V1",
            "AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1",
            "AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1",
            "CERT-000009",
        ],
        "reference_cert_000009_present": REFERENCE_CERT_000009.exists(),
        "lifecycle_operations": lifecycle_operations,
        "approval_enforcement": approval_operations,
        "operator_safe_credential_display": {
            "provider_id": credential_diagnostic["provider_id"],
            "credential_reference": credential_diagnostic["credential_reference"],
            "credential_display_identifier": credential_diagnostic["credential_display_identifier"],
            "credential_present": credential_diagnostic["credential_present"],
            "credential_value_recorded": credential_diagnostic["credential_value_recorded"],
            "credential_hash_recorded": credential_diagnostic["credential_hash_recorded"],
        },
        "operator_bootstrap_verification": {
            "verification_status": bootstrap_verification["verification_status"],
            "canonical_credential_reference": bootstrap_verification["diagnostic"][
                "canonical_credential_reference"
            ],
            "canonical_credential_present": bootstrap_verification["diagnostic"][
                "canonical_credential_present"
            ],
            "provider_native_alias_present": bootstrap_verification["diagnostic"][
                "provider_native_alias_present"
            ],
            "credential_value_recorded": bootstrap_verification["diagnostic"]["credential_value_recorded"],
            "credential_hash_recorded": bootstrap_verification["diagnostic"]["credential_hash_recorded"],
        },
        "replay_reconstruction": {
            "provider_governance_event_count": replay_reconstruction["provider_governance_event_count"],
            "provider_usage_metric_count": replay_reconstruction["provider_usage_metric_count"],
            "cognition_participation_count": replay_reconstruction["cognition_participation_count"],
            "append_only_valid": replay_reconstruction["append_only_valid"],
        },
        "observability": observability_results,
        "acli_queries": {name: item["row_count"] for name, item in acli_results.items()},
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    return coverage


def _evaluate_success_criteria(
    *,
    coverage: dict[str, Any],
    replay_reconstruction: dict[str, Any],
    credential_diagnostic: dict[str, Any],
    bootstrap_verification: dict[str, Any],
    acli_results: dict[str, dict[str, Any]],
) -> dict[str, bool]:
    lifecycle = coverage["lifecycle_operations"]
    approval = coverage["approval_enforcement"]
    serialized_credential = canonical_serialize(credential_diagnostic)
    return {
        "lifecycle_operations_certified": all(
            lifecycle.get(operation) is True for operation in ("VERIFY", "ENABLE", "DISABLE", "ROTATE", "DELETE")
        ),
        "approval_boundaries_preserved": all(
            approval.get(operation) is True for operation in ("DISABLE", "ROTATE", "DELETE", "REPLACE")
        ),
        "replay_reconstruction_certified": (
            replay_reconstruction["append_only_valid"] is True
            and replay_reconstruction["provider_governance_event_count"] >= 5
            and replay_reconstruction["provider_usage_metric_count"] >= 2
            and replay_reconstruction["cognition_participation_count"] >= 1
        ),
        "operator_safe_credentials_certified": (
            credential_diagnostic["credential_display_identifier"].startswith("ref:...")
            and credential_diagnostic["credential_value_recorded"] is False
            and credential_diagnostic["credential_hash_recorded"] is False
            and bootstrap_verification["verification_status"] == "READY"
            and bootstrap_verification["diagnostic"]["credential_value_recorded"] is False
            and bootstrap_verification["diagnostic"]["credential_hash_recorded"] is False
            and "operator-safe-present-marker" not in serialized_credential
        ),
        "usage_and_failure_metrics_certified": (
            len(replay_reconstruction["provider_usage"]) >= 2
            and len(replay_reconstruction["provider_failures"]) >= 1
            and len(replay_reconstruction["provider_costs"]) >= 2
        ),
        "participation_observability_certified": len(replay_reconstruction["cognition_participation"]) >= 1,
        "acli_queries_certified": all(item["row_count"] >= 1 for item in acli_results.values()),
    }


def _build_evidence_package(
    *,
    root: Path,
    created_at: str,
    coverage: dict[str, Any],
    replay_reconstruction: dict[str, Any],
    credential_diagnostic: dict[str, Any],
    bootstrap_verification: dict[str, Any],
    acli_results: dict[str, dict[str, Any]],
    final_verdict: str,
) -> dict[str, Any]:
    package = {
        "artifact_type": "PROVIDER_GOVERNANCE_CERTIFICATION_EVIDENCE_PACKAGE_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "cert_root": str(root),
        "coverage_hash": coverage["artifact_hash"],
        "replay_hash": replay_reconstruction["replay_hash"],
        "credential_diagnostic": credential_diagnostic,
        "operator_bootstrap_verification": bootstrap_verification,
        "acli_query_hashes": {name: item["artifact_hash"] for name, item in acli_results.items()},
        "final_verdict": final_verdict,
    }
    package["artifact_hash"] = replay_hash(package)
    return package


def _build_replay_package(
    *,
    root: Path,
    created_at: str,
    replay_reconstruction: dict[str, Any],
    acli_results: dict[str, dict[str, Any]],
    final_verdict: str,
) -> dict[str, Any]:
    package = {
        "artifact_type": "PROVIDER_GOVERNANCE_CERTIFICATION_REPLAY_PACKAGE_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "replay_root": str(root),
        "replay_reconstruction": replay_reconstruction,
        "acli_queries_replay_visible": all(item["replay_visible"] is True for item in acli_results.values()),
        "final_verdict": final_verdict,
    }
    package["artifact_hash"] = replay_hash(package)
    return package


def _build_certification_report(
    *,
    root: Path,
    created_at: str,
    coverage: dict[str, Any],
    success_criteria: dict[str, bool],
    final_verdict: str,
) -> dict[str, Any]:
    failed = [name for name, passed in success_criteria.items() if not passed]
    report = {
        "artifact_type": "PROVIDER_GOVERNANCE_CERTIFICATION_REPORT_V1",
        "milestone_id": MILESTONE_ID,
        "created_at": created_at,
        "cert_root": str(root),
        "coverage_hash": coverage["artifact_hash"],
        "questions": {
            "can_provider_lifecycle_actions_be_governed_safely": success_criteria[
                "lifecycle_operations_certified"
            ]
            and success_criteria["approval_boundaries_preserved"],
            "can_replay_reconstruct_all_provider_governance_actions": success_criteria[
                "replay_reconstruction_certified"
            ],
            "are_approval_boundaries_preserved": success_criteria["approval_boundaries_preserved"],
        },
        "success_criteria": success_criteria,
        "gap_analysis": [] if not failed else failed,
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    return report


def _persist_certification_artifacts(
    *,
    coverage_dir: Path,
    evidence_dir: Path,
    replay_dir: Path,
    report_dir: Path,
    coverage: dict[str, Any],
    evidence_package: dict[str, Any],
    replay_package: dict[str, Any],
    report: dict[str, Any],
) -> None:
    write_json_immutable(coverage_dir / "000_provider_governance_coverage_report.json", coverage)
    write_json_immutable(evidence_dir / "000_provider_governance_evidence_package.json", evidence_package)
    write_json_immutable(replay_dir / "000_provider_governance_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_provider_governance_certification_report.json", report)


def _approval_artifact(*, operation: str, cert_suffix: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "PROVIDER_GOVERNANCE_HUMAN_APPROVAL_ARTIFACT_V1",
        "approval_id": f"PROVIDER-GOVERNANCE-CERT-{cert_suffix}:APPROVAL-{operation}",
        "operation": operation,
        "approval_status": "APPROVED",
        "approved_by": "human.operator",
        "created_at": created_at,
        "execution_authority_granted": False,
        "worker_authority_granted": False,
        "provider_authority_granted": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


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
