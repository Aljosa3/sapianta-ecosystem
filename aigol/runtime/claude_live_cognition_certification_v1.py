"""Certification runner for AIGOL_CLAUDE_LIVE_COGNITION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path
import importlib
import os
import re
from typing import Any

from aigol.runtime.external_resource_registry_runtime import (
    ACTIVE,
    COGNITION_PROVIDER,
    CLAUDE_PROVIDER_ID,
    real_provider_err_v1_registry,
    select_resource_for_capability,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import (
    PROVIDER_REFERENCES,
    add_provider_credential,
    provider_credential_diagnostic,
    retrieve_provider_credential,
    verify_provider_credential,
)
from aigol.runtime.provider_governance_runtime import (
    record_cognition_participation,
    record_provider_usage_metric,
    reconstruct_provider_governance_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_CLAUDE_LIVE_COGNITION_CERTIFICATION_V1"
DEFAULT_RUNTIME_ROOT = Path("runtime/claude_live_cognition_certification_v1")
DEFAULT_CERT_VAULT_ROOT = Path("/tmp/aigol/claude_live_cognition_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

FINAL_VERDICT_CERTIFIED = "CLAUDE_LIVE_COGNITION_CERTIFIED"
FINAL_VERDICT_GAPS = "CLAUDE_LIVE_COGNITION_GAPS_FOUND"


def run_claude_live_cognition_certification_v1(
    *,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    vault_path: str | Path | None = None,
    transport: Any | None = None,
) -> dict[str, Any]:
    """Run first non-OpenAI Claude live cognition certification."""

    cert_root = _next_cert_root(Path(runtime_root))
    active_vault_path = Path(vault_path) if vault_path is not None else _default_vault_path(cert_root)
    evidence_dir = cert_root / "evidence_package"
    replay_dir = cert_root / "replay_package"
    report_dir = cert_root / "certification_report"

    credential_secret = _operator_claude_secret()
    credential_onboarded = False
    onboarding_event: dict[str, Any] | None = None
    verification_event: dict[str, Any] | None = None
    credential_resolution: dict[str, Any] | None = None
    failure_reason = ""
    try:
        if credential_secret:
            onboarding_event = add_provider_credential(
                provider_id=CLAUDE_PROVIDER_ID,
                credential_value=credential_secret,
                created_at=CREATED_AT,
                vault_path=active_vault_path,
                replay_dir=cert_root / "vault_lifecycle" / "add",
            )
            credential_onboarded = True
            verification_event = verify_provider_credential(
                provider_id=CLAUDE_PROVIDER_ID,
                created_at=CREATED_AT,
                vault_path=active_vault_path,
                replay_dir=cert_root / "vault_lifecycle" / "verify",
            )
            credential_resolution = retrieve_provider_credential(
                provider_id=CLAUDE_PROVIDER_ID,
                authorization_context={"runtime": MILESTONE_ID, "stage": "credential_resolution"},
                vault_path=active_vault_path,
                allow_env_fallback=False,
                created_at=CREATED_AT,
                replay_dir=cert_root / "vault_resolution",
            )
        else:
            failure_reason = "Claude credential unavailable in operator environment"
    except Exception as exc:
        failure_reason = str(exc)

    registration = _claude_registration(cert_root / "err_registration")
    executor, active_transport = _claude_executor_status(transport)
    live_execution = _live_execution_attempt(
        cert_root=cert_root,
        credential_resolution=credential_resolution,
        executor=executor,
        transport=active_transport,
        prior_failure=failure_reason,
    )
    governance = _provider_governance_observability(cert_root / "provider_governance", live_execution)
    diagnostic = _safe_diagnostic(active_vault_path)

    coverage = _coverage_report(
        cert_root=cert_root,
        vault_path=active_vault_path,
        credential_onboarded=credential_onboarded,
        onboarding_event=onboarding_event,
        verification_event=verification_event,
        credential_resolution=credential_resolution,
        registration=registration,
        executor=executor,
        live_execution=live_execution,
        governance=governance,
        diagnostic=diagnostic,
    )
    final_verdict = FINAL_VERDICT_CERTIFIED if _certified(coverage) else FINAL_VERDICT_GAPS
    coverage["final_verdict"] = final_verdict
    coverage["artifact_hash"] = replay_hash(coverage)

    evidence = _evidence_package(
        cert_root=cert_root,
        coverage=coverage,
        onboarding_event=onboarding_event,
        verification_event=verification_event,
        credential_resolution=credential_resolution,
        registration=registration,
        executor=executor,
        live_execution=live_execution,
        governance=governance,
        diagnostic=diagnostic,
        final_verdict=final_verdict,
    )
    replay = _replay_package(cert_root, coverage, evidence, final_verdict)
    report = _certification_report(cert_root, coverage, evidence, replay, final_verdict)

    write_json_immutable(evidence_dir / "000_claude_live_cognition_evidence_package.json", evidence)
    write_json_immutable(evidence_dir / "001_claude_live_cognition_coverage_report.json", coverage)
    write_json_immutable(replay_dir / "000_claude_live_cognition_replay_package.json", replay)
    write_json_immutable(report_dir / "000_claude_live_cognition_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "coverage_report_path": str(evidence_dir / "001_claude_live_cognition_coverage_report.json"),
        "evidence_package_path": str(evidence_dir / "000_claude_live_cognition_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_claude_live_cognition_replay_package.json"),
        "certification_report_path": str(report_dir / "000_claude_live_cognition_certification_report.json"),
        "coverage": coverage,
        "final_verdict": final_verdict,
    }


def reconstruct_claude_live_cognition_certification_v1(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    coverage = load_json(root / "evidence_package" / "001_claude_live_cognition_coverage_report.json")
    evidence = load_json(root / "evidence_package" / "000_claude_live_cognition_evidence_package.json")
    replay = load_json(root / "replay_package" / "000_claude_live_cognition_replay_package.json")
    report = load_json(root / "certification_report" / "000_claude_live_cognition_certification_report.json")
    for artifact in (coverage, evidence, replay, report):
        _verify_artifact_hash(artifact)
    return {
        "runtime_version": MILESTONE_ID,
        "replay_reconstructed": True,
        "coverage_report": coverage,
        "evidence_package": evidence,
        "replay_package": replay,
        "certification_report": report,
        "final_verdict": report["final_verdict"],
    }


def _claude_registration(replay_dir: Path) -> dict[str, Any]:
    registry = real_provider_err_v1_registry()
    for resource in registry["resources"]:
        resource["status"] = ACTIVE if resource["resource_id"] == CLAUDE_PROVIDER_ID else "INACTIVE"
    selection = select_resource_for_capability(
        selection_id="CLAUDE-LIVE-COGNITION:ERR-SELECTION",
        required_capability="reasoning",
        replay_dir=replay_dir,
        created_at=CREATED_AT,
        registry=registry,
        resource_type=COGNITION_PROVIDER,
        human_intent="Use Claude to propose the safest next step before any execution.",
        hirr_output={
            "runtime": MILESTONE_ID,
            "required_capability": "reasoning",
            "resource_type": COGNITION_PROVIDER,
        },
    )
    return {
        "provider_registered": selection["selected_resource_id"] == CLAUDE_PROVIDER_ID,
        "provider_selected": selection["selected_resource_id"],
        "selected_resource_type": selection["selected_resource_type"],
        "replay_reference": selection["replay_reference"],
    }


def _claude_executor_status(transport: Any | None) -> tuple[dict[str, Any], Any | None]:
    if transport is not None:
        return (
            {
                "live_executor_exists": bool(getattr(transport, "aigol_governed_live_claude_executor_v1", False)),
                "executor_source": "injected_transport",
                "executor_name": getattr(transport, "__name__", type(transport).__name__),
            },
            transport,
        )
    for module_name, factory_name in (
        ("aigol.runtime.live_claude_executor", "create_governed_live_claude_executor"),
        ("aigol.runtime.live_anthropic_executor", "create_governed_live_anthropic_executor"),
    ):
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        factory = getattr(module, factory_name, None)
        if callable(factory):
            return (
                {
                    "live_executor_exists": True,
                    "executor_source": module_name,
                    "executor_name": factory_name,
                },
                factory(),
            )
    return (
        {
            "live_executor_exists": False,
            "executor_source": None,
            "executor_name": None,
            "failure_reason": "governed live Claude executor is not implemented",
        },
        None,
    )


def _live_execution_attempt(
    *,
    cert_root: Path,
    credential_resolution: dict[str, Any] | None,
    executor: dict[str, Any],
    transport: Any | None,
    prior_failure: str,
) -> dict[str, Any]:
    if prior_failure:
        return _live_execution_result(False, False, False, prior_failure, cert_root / "live_execution")
    if credential_resolution is None:
        return _live_execution_result(False, False, False, "Claude credential resolution unavailable", cert_root / "live_execution")
    if executor["live_executor_exists"] is not True:
        return _live_execution_result(
            True,
            False,
            False,
            "governed live Claude executor is not implemented",
            cert_root / "live_execution",
        )
    if transport is None:
        return _live_execution_result(True, False, False, "governed live Claude executor is not available", cert_root / "live_execution")
    try:
        raw_response = transport(
            {
                "provider_id": CLAUDE_PROVIDER_ID,
                "prompt": "Provide a proposal-only safe next step for reviewing an AI decision.",
                "stream": False,
            },
            {
                "provider_id": CLAUDE_PROVIDER_ID,
                "_credential_secret": credential_resolution.get("_credential_secret"),
                "credential_secret_replayed": False,
                "timeout_seconds": 20,
            },
        )
        response_received = isinstance(raw_response, dict) and bool(raw_response)
        return _live_execution_result(True, True, response_received, "" if response_received else "empty Claude response", cert_root / "live_execution")
    except Exception as exc:
        return _live_execution_result(True, True, False, str(exc), cert_root / "live_execution")


def _live_execution_result(
    provider_selected: bool,
    provider_invoked: bool,
    provider_response_received: bool,
    failure_reason: str,
    replay_dir: Path,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "CLAUDE_LIVE_COGNITION_EXECUTION_ATTEMPT_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "provider_selected": CLAUDE_PROVIDER_ID if provider_selected else None,
        "provider_invoked": provider_invoked,
        "provider_response_received": provider_response_received,
        "credential_source": PROVIDER_REFERENCES[CLAUDE_PROVIDER_ID],
        "worker_invoked": False,
        "execution_requested": False,
        "human_confirmation_required": True,
        "failure_reason": failure_reason,
        "created_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    write_json_immutable(replay_dir / "000_claude_live_cognition_execution_attempt.json", artifact)
    return {
        "provider_selected": artifact["provider_selected"],
        "provider_invoked": provider_invoked,
        "provider_response_received": provider_response_received,
        "credential_source": artifact["credential_source"],
        "worker_invoked": False,
        "failure_reason": failure_reason,
        "replay_reference": str(replay_dir),
        "artifact_hash": artifact["artifact_hash"],
    }


def _provider_governance_observability(replay_root: Path, live_execution: dict[str, Any]) -> dict[str, Any]:
    record_provider_usage_metric(
        metric_id="CLAUDE-LIVE-COGNITION:USAGE",
        provider_id=CLAUDE_PROVIDER_ID,
        model="claude-live-certification",
        status="SUCCESS" if live_execution["provider_response_received"] else "FAILED",
        availability="AVAILABLE" if live_execution["provider_response_received"] else "UNAVAILABLE",
        success_count=1 if live_execution["provider_response_received"] else 0,
        failure_count=0 if live_execution["provider_response_received"] else 1,
        last_used=CREATED_AT if live_execution["provider_response_received"] else None,
        last_failure=live_execution["failure_reason"] or None,
        token_usage={"status": "not_recorded_no_live_response"} if not live_execution["provider_response_received"] else None,
        cost_tracking={"status": "cost_hook_present", "estimated_usd": None},
        created_at=CREATED_AT,
        replay_dir=replay_root / "usage",
    )
    record_cognition_participation(
        participation_id="CLAUDE-LIVE-COGNITION:PARTICIPATION",
        provider_id=CLAUDE_PROVIDER_ID,
        participation_location="OCS_LLM_COGNITION",
        participation_role="PROPOSAL_ONLY_COGNITION_PROVIDER",
        workflow_id="OCS_LLM_COGNITION",
        invocation_reason="first non-OpenAI live cognition certification",
        purpose="proposal-only Product 1 cognition",
        response_used=live_execution["provider_response_received"],
        worker_invoked_after=False,
        human_confirmation_required=True,
        created_at=CREATED_AT,
        replay_dir=replay_root / "participation",
    )
    return reconstruct_provider_governance_replay(replay_root)


def _coverage_report(
    *,
    cert_root: Path,
    vault_path: Path,
    credential_onboarded: bool,
    onboarding_event: dict[str, Any] | None,
    verification_event: dict[str, Any] | None,
    credential_resolution: dict[str, Any] | None,
    registration: dict[str, Any],
    executor: dict[str, Any],
    live_execution: dict[str, Any],
    governance: dict[str, Any],
    diagnostic: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_type": "CLAUDE_LIVE_COGNITION_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "vault_path": str(vault_path),
        "provider_registered": registration["provider_registered"],
        "credential_reference": PROVIDER_REFERENCES[CLAUDE_PROVIDER_ID],
        "credential_onboarded": credential_onboarded,
        "credential_status_verified": bool(verification_event and verification_event.get("operation") == "VERIFY"),
        "credential_resolution_successful": bool(
            credential_resolution and credential_resolution.get("credential_source") == PROVIDER_REFERENCES[CLAUDE_PROVIDER_ID]
        ),
        "credential_present": diagnostic.get("credential_present"),
        "credential_enabled": diagnostic.get("credential_enabled"),
        "live_executor_exists": executor["live_executor_exists"],
        "provider_selected": live_execution["provider_selected"],
        "provider_invoked": live_execution["provider_invoked"],
        "provider_response_received": live_execution["provider_response_received"],
        "credential_source": live_execution["credential_source"],
        "replay_reconstructed": governance["replay_visible"],
        "participation_metrics_recorded": governance["cognition_participation_count"] >= 1,
        "usage_metrics_recorded": governance["provider_usage_metric_count"] >= 1,
        "failure_metrics_recorded": len(governance["provider_failures"]) >= 1
        or live_execution["provider_response_received"] is True,
        "cost_hooks_recorded": len(governance["provider_costs"]) >= 1,
        "worker_invoked": live_execution["worker_invoked"],
        "secret_free_evidence": _secret_free(cert_root),
        "failure_reason": live_execution["failure_reason"] or executor.get("failure_reason") or "",
    }


def _certified(coverage: dict[str, Any]) -> bool:
    return all(
        [
            coverage["provider_registered"],
            coverage["credential_reference"] == PROVIDER_REFERENCES[CLAUDE_PROVIDER_ID],
            coverage["credential_onboarded"],
            coverage["credential_status_verified"],
            coverage["credential_resolution_successful"],
            coverage["live_executor_exists"],
            coverage["provider_selected"] == CLAUDE_PROVIDER_ID,
            coverage["provider_invoked"] is True,
            coverage["provider_response_received"] is True,
            coverage["credential_source"] == PROVIDER_REFERENCES[CLAUDE_PROVIDER_ID],
            coverage["replay_reconstructed"],
            coverage["participation_metrics_recorded"],
            coverage["usage_metrics_recorded"],
            coverage["cost_hooks_recorded"],
            coverage["worker_invoked"] is False,
            coverage["secret_free_evidence"],
        ]
    )


def _evidence_package(
    *,
    cert_root: Path,
    coverage: dict[str, Any],
    onboarding_event: dict[str, Any] | None,
    verification_event: dict[str, Any] | None,
    credential_resolution: dict[str, Any] | None,
    registration: dict[str, Any],
    executor: dict[str, Any],
    live_execution: dict[str, Any],
    governance: dict[str, Any],
    diagnostic: dict[str, Any],
    final_verdict: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "CLAUDE_LIVE_COGNITION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "coverage_report_hash": coverage["artifact_hash"],
        "onboarding_event": _safe_event(onboarding_event),
        "verification_event": _safe_event(verification_event),
        "credential_resolution": _safe_resolution(credential_resolution),
        "registration": registration,
        "executor": executor,
        "live_execution": live_execution,
        "provider_governance_reconstruction": governance,
        "vault_diagnostic": diagnostic,
        "final_verdict": final_verdict,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _replay_package(cert_root: Path, coverage: dict[str, Any], evidence: dict[str, Any], final_verdict: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "CLAUDE_LIVE_COGNITION_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "coverage_report_hash": coverage["artifact_hash"],
        "evidence_package_hash": evidence["artifact_hash"],
        "replay_references": [
            str(cert_root / "err_registration"),
            str(cert_root / "vault_lifecycle"),
            str(cert_root / "vault_resolution"),
            str(cert_root / "live_execution"),
            str(cert_root / "provider_governance"),
        ],
        "replay_reconstructed": coverage["replay_reconstructed"],
        "final_verdict": final_verdict,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _certification_report(
    cert_root: Path,
    coverage: dict[str, Any],
    evidence: dict[str, Any],
    replay: dict[str, Any],
    final_verdict: str,
) -> dict[str, Any]:
    gaps = [key for key, value in coverage.items() if key.endswith("_recorded") and value is False]
    if coverage["live_executor_exists"] is not True:
        gaps.append("live_executor_missing")
    if coverage["provider_response_received"] is not True:
        gaps.append("provider_response_not_received")
    artifact = {
        "artifact_type": "CLAUDE_LIVE_COGNITION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "coverage_report_hash": coverage["artifact_hash"],
        "evidence_package_hash": evidence["artifact_hash"],
        "replay_package_hash": replay["artifact_hash"],
        "coverage_report": coverage,
        "readiness_assessment": (
            "Claude can participate in the same governed cognition architecture as OpenAI."
            if final_verdict == FINAL_VERDICT_CERTIFIED
            else "Claude registration, vault reference, onboarding, and observability are present, but live Claude cognition is not certified."
        ),
        "gap_analysis": gaps,
        "remediation_recommendations": _remediation_recommendations(coverage),
        "final_verdict": final_verdict,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _remediation_recommendations(coverage: dict[str, Any]) -> list[str]:
    recommendations = []
    if coverage["live_executor_exists"] is not True:
        recommendations.append("Implement or attach a governed live Claude/Anthropic cognition executor.")
    if coverage["provider_response_received"] is not True:
        recommendations.append("Re-run Claude live cognition certification after the executor can return a replay-safe response.")
    if coverage["credential_onboarded"] is not True:
        recommendations.append("Provision ANTHROPIC_API_KEY or AIGOL_ANTHROPIC_API_KEY and onboard it into the provider vault.")
    return recommendations or ["No remediation required."]


def _safe_event(event: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(event, dict):
        return None
    return {
        "operation": event.get("operation"),
        "provider_id": event.get("provider_id"),
        "credential_reference": event.get("credential_reference"),
        "credential_source": event.get("credential_source"),
        "credential_present": event.get("credential_present"),
        "credential_enabled": event.get("credential_enabled"),
        "display_identifier": event.get("display_identifier"),
        "human_approval_required": event.get("human_approval_required"),
        "human_approval_recorded": event.get("human_approval_recorded"),
        "artifact_hash": event.get("artifact_hash"),
    }


def _safe_resolution(resolution: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(resolution, dict):
        return None
    artifact = resolution.get("retrieval_artifact", {})
    return {
        "provider_id": resolution.get("provider_id"),
        "credential_reference": resolution.get("credential_reference"),
        "credential_source": resolution.get("credential_source"),
        "credential_present": artifact.get("credential_present"),
        "credential_enabled": artifact.get("credential_enabled"),
        "display_identifier": artifact.get("display_identifier"),
        "credential_value_recorded": artifact.get("credential_value_recorded"),
        "credential_hash_recorded": artifact.get("credential_hash_recorded"),
        "authorization_header_recorded": artifact.get("authorization_header_recorded"),
    }


def _safe_diagnostic(vault_path: Path) -> dict[str, Any]:
    try:
        return provider_credential_diagnostic(provider_id=CLAUDE_PROVIDER_ID, vault_path=vault_path)
    except Exception as exc:
        return {
            "provider_id": CLAUDE_PROVIDER_ID,
            "credential_reference": PROVIDER_REFERENCES[CLAUDE_PROVIDER_ID],
            "credential_present": False,
            "credential_enabled": False,
            "failure_reason": str(exc),
            "replay_safe": True,
        }


def _operator_claude_secret() -> str:
    for name in ("ANTHROPIC_API_KEY", "AIGOL_ANTHROPIC_API_KEY", "AIGOL_PROVIDER_CLAUDE_CREDENTIAL_INPUT"):
        value = os.environ.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _default_vault_path(cert_root: Path) -> Path:
    return DEFAULT_CERT_VAULT_ROOT / f"{cert_root.name.lower()}-provider-credentials.json"


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        try:
            serialized += canonical_serialize(load_json(path))
        except Exception:
            continue
    return "Bearer " not in serialized and "_credential_secret" not in serialized and "secret-value" not in serialized.lower()


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing: list[int] = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = artifact.get("artifact_hash")
    if not isinstance(expected, str):
        raise FailClosedRuntimeError("Claude live cognition certification artifact hash missing")
    candidate = dict(artifact)
    candidate.pop("artifact_hash", None)
    if replay_hash(candidate) != expected:
        raise FailClosedRuntimeError("Claude live cognition certification artifact hash mismatch")


def main() -> int:
    result = run_claude_live_cognition_certification_v1()
    coverage = result["coverage"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"coverage_report={result['coverage_report_path']}")
    print(f"evidence_package={result['evidence_package_path']}")
    print(f"replay_package={result['replay_package_path']}")
    print(f"certification_report={result['certification_report_path']}")
    print(f"provider_registered={coverage['provider_registered']}")
    print(f"credential_source={coverage['credential_source']}")
    print(f"live_executor_exists={coverage['live_executor_exists']}")
    print(f"provider_selected={coverage['provider_selected']}")
    print(f"provider_invoked={coverage['provider_invoked']}")
    print(f"provider_response_received={coverage['provider_response_received']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
