"""Certification runner for AIGOL_MULTI_PROVIDER_LIVE_COGNITION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import (
    create_default_cognition_provider_contract,
    reconstruct_multi_provider_cognition_replay,
    run_multi_provider_cognition_runtime,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.provider_credential_vault import (
    PROVIDER_REFERENCES,
    provider_credential_diagnostic,
)
from aigol.runtime.provider_governance_runtime import (
    record_cognition_participation,
    record_provider_usage_metric,
    reconstruct_provider_governance_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_MULTI_PROVIDER_LIVE_COGNITION_CERTIFICATION_V1"
DEFAULT_RUNTIME_ROOT = Path("runtime/multi_provider_live_cognition_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

PROVIDERS = ("openai", "claude", "gemini", "mistral")
FINAL_VERDICT_CERTIFIED = "MULTI_PROVIDER_LIVE_COGNITION_CERTIFIED"
FINAL_VERDICT_GAPS = "MULTI_PROVIDER_LIVE_COGNITION_GAPS_FOUND"


def run_multi_provider_live_cognition_certification_v1(
    *,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    vault_path: str | Path | None = None,
    live_openai_report_path: str | Path | None = None,
    product1_report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Execute multi-provider live cognition certification."""

    cert_root = _next_cert_root(Path(runtime_root))
    provider_diagnostics = _provider_diagnostics(vault_path=vault_path)
    live_evidence = _live_provider_evidence(live_openai_report_path)
    product1_evidence = _product1_evidence(product1_report_path)
    cognition_probe = _run_failover_probe(cert_root / "multi_provider_cognition_probe")
    governance_probe = _record_governance_observability(cert_root / "provider_governance_replay", cognition_probe)
    scenario_results = _scenario_results(provider_diagnostics, live_evidence, product1_evidence, cognition_probe, governance_probe)
    assertions = _assertions(scenario_results, provider_diagnostics, live_evidence, product1_evidence, cognition_probe, governance_probe)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = _coverage_report(cert_root, scenario_results, assertions, final_verdict)
    evidence = _evidence_package(
        cert_root,
        provider_diagnostics,
        live_evidence,
        product1_evidence,
        cognition_probe,
        governance_probe,
        scenario_results,
        assertions,
        final_verdict,
    )
    replay = _replay_package(cert_root, coverage, evidence, cognition_probe, governance_probe, final_verdict)
    report = _certification_report(cert_root, coverage, evidence, replay, scenario_results, assertions, final_verdict)

    coverage_path = cert_root / "coverage_report" / "000_multi_provider_live_cognition_coverage_report.json"
    evidence_path = cert_root / "evidence_package" / "000_multi_provider_live_cognition_evidence_package.json"
    replay_path = cert_root / "replay_package" / "000_multi_provider_live_cognition_replay_package.json"
    report_path = cert_root / "certification_report" / "000_multi_provider_live_cognition_certification_report.json"
    write_json_immutable(coverage_path, coverage)
    write_json_immutable(evidence_path, evidence)
    write_json_immutable(replay_path, replay)
    write_json_immutable(report_path, report)

    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "coverage_report_path": str(coverage_path),
        "evidence_package_path": str(evidence_path),
        "replay_package_path": str(replay_path),
        "certification_report_path": str(report_path),
        "scenario_results": scenario_results,
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def reconstruct_multi_provider_live_cognition_certification_v1(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    coverage = load_json(root / "coverage_report" / "000_multi_provider_live_cognition_coverage_report.json")
    evidence = load_json(root / "evidence_package" / "000_multi_provider_live_cognition_evidence_package.json")
    replay = load_json(root / "replay_package" / "000_multi_provider_live_cognition_replay_package.json")
    report = load_json(root / "certification_report" / "000_multi_provider_live_cognition_certification_report.json")
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


def _provider_diagnostics(*, vault_path: str | Path | None) -> dict[str, dict[str, Any]]:
    diagnostics = {}
    for provider_id in PROVIDERS:
        try:
            diagnostic = provider_credential_diagnostic(provider_id=provider_id, vault_path=vault_path) if vault_path else {
                "provider_id": provider_id,
                "credential_reference": PROVIDER_REFERENCES[provider_id],
                "credential_source": PROVIDER_REFERENCES[provider_id],
                "credential_present": False,
                "credential_enabled": False,
                "display_identifier": None,
                "replay_safe": True,
            }
        except FailClosedRuntimeError as exc:
            diagnostic = {
                "provider_id": provider_id,
                "credential_reference": PROVIDER_REFERENCES[provider_id],
                "credential_source": PROVIDER_REFERENCES[provider_id],
                "credential_present": False,
                "credential_enabled": False,
                "diagnostic_failure": str(exc),
                "replay_safe": True,
            }
        diagnostics[provider_id] = diagnostic
    return diagnostics


def _live_provider_evidence(path: str | Path | None) -> dict[str, Any]:
    report_path = Path(path) if path is not None else Path(
        "runtime/first_live_cognition_provider_certification_v1/CERT-000009/"
        "certification_report/000_first_live_cognition_provider_certification_report.json"
    )
    report = load_json(report_path) if report_path.exists() else {}
    observed = report.get("observed") if isinstance(report.get("observed"), dict) else {}
    return {
        "report_path": str(report_path),
        "openai_live_certified": report.get("final_verdict") == "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED",
        "openai_provider_selected": observed.get("provider_selected") == "openai",
        "openai_provider_invoked": observed.get("provider_invoked") is True,
        "openai_provider_response_received": observed.get("provider_response_received") is True,
        "openai_replay_reconstructed": observed.get("replay_reconstructed") is True,
        "non_openai_live_certified_providers": [],
    }


def _product1_evidence(path: str | Path | None) -> dict[str, Any]:
    report_path = Path(path) if path is not None else _latest_report(
        Path("runtime/product1_end_to_end_certification_v1"),
        "certification_report/000_product1_end_to_end_certification_report.json",
        "AIGOL_PRODUCT1_END_TO_END_CERTIFIED",
    )
    report = load_json(report_path) if report_path.exists() else {}
    return {
        "report_path": str(report_path),
        "product1_end_to_end_certified": report.get("final_verdict") == "AIGOL_PRODUCT1_END_TO_END_CERTIFIED",
    }


def _run_failover_probe(replay_root: Path) -> dict[str, Any]:
    context_capture = assemble_ocs_context(
        context_assembly_id="MULTI-PROVIDER-LIVE-COGNITION-CONTEXT",
        created_at=CREATED_AT,
        replay_dir=replay_root / "context",
        source_context={
            "conversation_context": [
                {
                    "source_id": "multi-provider-live-certification",
                    "summary": "Representative Product 1 cognition prompt for multi-provider failover certification.",
                    "replay_visible": True,
                }
            ],
            "replay_visible_operation_context": [
                {
                    "source_id": "certification-scope",
                    "summary": "No worker execution is authorized by the multi-provider cognition probe.",
                    "replay_visible": True,
                }
            ],
        },
    )
    context_artifact = context_capture["ocs_context_assembly_artifact"]
    contracts = [
        create_default_cognition_provider_contract(provider_id=provider_id, created_at=CREATED_AT)
        for provider_id in PROVIDERS
    ]
    result = run_multi_provider_cognition_runtime(
        multi_provider_cognition_bundle_id="MULTI-PROVIDER-LIVE-COGNITION-PROBE",
        human_request="Compare safe next steps for reviewing an AI decision before any execution.",
        ocs_context_artifact=context_artifact,
        provider_contracts=contracts,
        created_at=CREATED_AT,
        replay_dir=replay_root / "multi_provider_runtime",
        transport_registry={"openai": _deterministic_openai_transport},
    )
    reconstruction = reconstruct_multi_provider_cognition_replay(replay_root / "multi_provider_runtime")
    return {
        "replay_root": str(replay_root),
        "context_replay_reference": context_capture["ocs_context_assembly_replay_reference"],
        "multi_provider_replay_reference": result["replay_reference"],
        "runtime_result": _safe_probe_result(result),
        "reconstruction": reconstruction,
    }


def _deterministic_openai_transport(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_id": metadata["provider_id"],
        "model": "gpt-5-certification-probe",
        "text": (
            '{"findings":["OpenAI provider returned a proposal."],'
            '"assumptions":["This is a deterministic certification probe."],'
            '"alternatives":["Wait for additional provider certifications."],'
            '"risks":["Non-OpenAI providers are unavailable."],'
            '"uncertainties":["Claude, Gemini, and Mistral are not live-certified here."],'
            '"confidence":"MEDIUM"}'
        ),
        "usage": {"input_tokens": 12, "output_tokens": 18, "total_tokens": 30},
    }


def _safe_probe_result(result: dict[str, Any]) -> dict[str, Any]:
    bundle = result.get("result_bundle") if isinstance(result.get("result_bundle"), dict) else {}
    return {
        "final_status": result.get("final_status"),
        "fail_closed": result.get("fail_closed"),
        "provider_count": bundle.get("provider_count"),
        "successful_provider_count": bundle.get("successful_provider_count"),
        "failed_provider_count": bundle.get("failed_provider_count"),
        "successful_providers": [item.get("provider_id") for item in bundle.get("provider_results", [])],
        "failed_providers": [item.get("provider_id") for item in bundle.get("provider_failures", [])],
        "replay_reference": result.get("replay_reference"),
    }


def _record_governance_observability(replay_root: Path, cognition_probe: dict[str, Any]) -> dict[str, Any]:
    runtime_result = cognition_probe["runtime_result"]
    successful = set(runtime_result["successful_providers"])
    failed = set(runtime_result["failed_providers"])
    for provider_id in PROVIDERS:
        provider_dir = replay_root / provider_id
        record_provider_usage_metric(
            metric_id=f"MULTI-PROVIDER-LIVE-COGNITION:{provider_id}:USAGE",
            provider_id=provider_id,
            model=_model_for_provider(provider_id),
            status="SUCCESS" if provider_id in successful else "FAILED",
            availability="AVAILABLE" if provider_id in successful else "UNAVAILABLE",
            created_at=CREATED_AT,
            replay_dir=provider_dir / "usage",
            success_count=1 if provider_id in successful else 0,
            failure_count=1 if provider_id in failed else 0,
            last_used=CREATED_AT if provider_id in successful else None,
            last_failure="provider transport is not registered" if provider_id in failed else None,
            latency_ms=125 if provider_id in successful else None,
            token_usage={"input_tokens": 12, "output_tokens": 18, "total_tokens": 30} if provider_id in successful else None,
            cost_tracking={"estimated_usd": "hook-not-live-priced"} if provider_id in successful else None,
        )
        record_cognition_participation(
            participation_id=f"MULTI-PROVIDER-LIVE-COGNITION:{provider_id}:PARTICIPATION",
            provider_id=provider_id,
            participation_location="OCS_LLM_COGNITION",
            participation_role="PRIMARY_PROPOSAL" if provider_id == "openai" else "FAILOVER_CANDIDATE",
            workflow_id="OCS_LLM_COGNITION",
            invocation_reason="multi-provider live cognition certification",
            purpose="proposal-only Product 1 decision review cognition",
            response_used=provider_id in successful,
            worker_invoked_after=False,
            human_confirmation_required=True,
            created_at=CREATED_AT,
            replay_dir=provider_dir / "participation",
        )
    reconstruction = reconstruct_provider_governance_replay(replay_root)
    return {
        "replay_root": str(replay_root),
        "reconstruction": reconstruction,
    }


def _scenario_results(
    provider_diagnostics: dict[str, dict[str, Any]],
    live_evidence: dict[str, Any],
    product1_evidence: dict[str, Any],
    cognition_probe: dict[str, Any],
    governance_probe: dict[str, Any],
) -> list[dict[str, Any]]:
    probe = cognition_probe["runtime_result"]
    governance = governance_probe["reconstruction"]
    scenarios = [
        {
            "scenario_id": "MPLC-001",
            "coverage": "provider_onboarding_lifecycle",
            "certified": product1_evidence["product1_end_to_end_certified"]
            and all(provider in PROVIDER_REFERENCES for provider in PROVIDERS),
            "finding": "Provider lifecycle governance and vault references exist for all required provider ids.",
        },
        {
            "scenario_id": "MPLC-002",
            "coverage": "credential_resolution",
            "certified": all(
                provider_diagnostics[provider]["credential_reference"] == PROVIDER_REFERENCES[provider]
                for provider in PROVIDERS
            ),
            "finding": "Credential references resolve to canonical vault references; presence depends on operator onboarding.",
        },
        {
            "scenario_id": "MPLC-003",
            "coverage": "provider_selection",
            "certified": probe["provider_count"] == len(PROVIDERS) and probe["successful_providers"] == ["openai"],
            "finding": "Multi-provider selection produced four provider request slots with OpenAI as the only successful provider.",
        },
        {
            "scenario_id": "MPLC-004",
            "coverage": "provider_failover_behavior",
            "certified": probe["successful_provider_count"] == 1 and probe["failed_provider_count"] == 3,
            "finding": "Provider failures were isolated and did not corrupt the OpenAI result.",
        },
        {
            "scenario_id": "MPLC-005",
            "coverage": "replay_visible_provider_participation",
            "certified": governance["cognition_participation_count"] == len(PROVIDERS),
            "finding": "Provider participation was replay-visible for all provider candidates.",
        },
        {
            "scenario_id": "MPLC-006",
            "coverage": "provider_governance_metrics",
            "certified": governance["provider_usage_metric_count"] == len(PROVIDERS)
            and len(governance["provider_failures"]) == 3
            and len(governance["provider_costs"]) >= 1,
            "finding": "Usage, failure, participation, and cost-hook evidence was recorded.",
        },
        {
            "scenario_id": "MPLC-007",
            "coverage": "live_multi_provider_execution",
            "certified": live_evidence["openai_live_certified"]
            and len(live_evidence["non_openai_live_certified_providers"]) >= 1,
            "finding": "OpenAI is live-certified; Claude/Gemini/Mistral have no live provider certification evidence in this run.",
        },
    ]
    return [
        {
            **scenario,
            "scenario_verdict": "CERTIFIED" if scenario["certified"] else "GAPS_FOUND",
        }
        for scenario in scenarios
    ]


def _assertions(
    scenario_results: list[dict[str, Any]],
    provider_diagnostics: dict[str, dict[str, Any]],
    live_evidence: dict[str, Any],
    product1_evidence: dict[str, Any],
    cognition_probe: dict[str, Any],
    governance_probe: dict[str, Any],
) -> dict[str, bool]:
    probe = cognition_probe["runtime_result"]
    governance = governance_probe["reconstruction"]
    return {
        "product1_end_to_end_certified": product1_evidence["product1_end_to_end_certified"],
        "openai_live_cognition_certified": live_evidence["openai_live_certified"],
        "all_required_vault_references_defined": all(
            provider_diagnostics[provider]["credential_reference"] == PROVIDER_REFERENCES[provider]
            for provider in PROVIDERS
        ),
        "all_required_credentials_present": all(
            provider_diagnostics[provider].get("credential_present") is True
            and provider_diagnostics[provider].get("credential_enabled") is True
            for provider in PROVIDERS
        ),
        "multi_provider_runtime_selected_all_providers": probe["provider_count"] == len(PROVIDERS),
        "provider_failover_isolated_failures": probe["successful_provider_count"] == 1 and probe["failed_provider_count"] == 3,
        "replay_visible_provider_participation": governance["cognition_participation_count"] == len(PROVIDERS),
        "provider_usage_metrics_recorded": governance["provider_usage_metric_count"] == len(PROVIDERS),
        "provider_failure_metrics_recorded": len(governance["provider_failures"]) == 3,
        "provider_cost_hooks_recorded": len(governance["provider_costs"]) >= 1,
        "non_openai_live_provider_certified": bool(live_evidence["non_openai_live_certified_providers"]),
        "all_scenarios_certified": all(item["scenario_verdict"] == "CERTIFIED" for item in scenario_results),
        "replay_reconstructed": cognition_probe["reconstruction"]["replay_visible"] is True
        and governance["replay_visible"] is True,
    }


def _coverage_report(
    cert_root: Path,
    scenario_results: list[dict[str, Any]],
    assertions: dict[str, bool],
    final_verdict: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "MULTI_PROVIDER_LIVE_COGNITION_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "providers": list(PROVIDERS),
        "coverage": [item["coverage"] for item in scenario_results],
        "scenario_verdicts": {item["scenario_id"]: item["scenario_verdict"] for item in scenario_results},
        "assertions": assertions,
        "final_verdict": final_verdict,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _evidence_package(
    cert_root: Path,
    provider_diagnostics: dict[str, dict[str, Any]],
    live_evidence: dict[str, Any],
    product1_evidence: dict[str, Any],
    cognition_probe: dict[str, Any],
    governance_probe: dict[str, Any],
    scenario_results: list[dict[str, Any]],
    assertions: dict[str, bool],
    final_verdict: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "MULTI_PROVIDER_LIVE_COGNITION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "provider_diagnostics": provider_diagnostics,
        "live_provider_evidence": live_evidence,
        "product1_evidence": product1_evidence,
        "multi_provider_cognition_probe": cognition_probe,
        "provider_governance_probe": governance_probe,
        "scenario_results": scenario_results,
        "assertions": assertions,
        "secret_free_evidence": True,
        "final_verdict": final_verdict,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _replay_package(
    cert_root: Path,
    coverage: dict[str, Any],
    evidence: dict[str, Any],
    cognition_probe: dict[str, Any],
    governance_probe: dict[str, Any],
    final_verdict: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "MULTI_PROVIDER_LIVE_COGNITION_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "coverage_report_hash": coverage["artifact_hash"],
        "evidence_package_hash": evidence["artifact_hash"],
        "multi_provider_cognition_replay_reference": cognition_probe["runtime_result"]["replay_reference"],
        "provider_governance_replay_reference": governance_probe["replay_root"],
        "replay_reconstructed": cognition_probe["reconstruction"]["replay_visible"] is True
        and governance_probe["reconstruction"]["replay_visible"] is True,
        "final_verdict": final_verdict,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _certification_report(
    cert_root: Path,
    coverage: dict[str, Any],
    evidence: dict[str, Any],
    replay: dict[str, Any],
    scenario_results: list[dict[str, Any]],
    assertions: dict[str, bool],
    final_verdict: str,
) -> dict[str, Any]:
    gaps = _gap_analysis(assertions, scenario_results)
    artifact = {
        "artifact_type": "MULTI_PROVIDER_LIVE_COGNITION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "coverage_report_hash": coverage["artifact_hash"],
        "evidence_package_hash": evidence["artifact_hash"],
        "replay_package_hash": replay["artifact_hash"],
        "scenario_results": scenario_results,
        "assertions": assertions,
        "readiness_assessment": _readiness_assessment(final_verdict),
        "gap_analysis": gaps,
        "remediation_recommendations": _remediation_recommendations(gaps),
        "final_verdict": final_verdict,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _readiness_assessment(final_verdict: str) -> str:
    if final_verdict == FINAL_VERDICT_CERTIFIED:
        return "AiGOL can govern multiple live cognition providers under the same approval, authorization, replay, and audit model."
    return (
        "AiGOL has multi-provider governance, credential references, failover isolation, participation replay, and metrics, "
        "but live multi-provider cognition is not certified because only OpenAI has live response evidence."
    )


def _gap_analysis(assertions: dict[str, bool], scenario_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps = [{"assertion": key, "status": "GAP"} for key, value in assertions.items() if value is not True]
    gaps.extend(
        {
            "scenario_id": item["scenario_id"],
            "coverage": item["coverage"],
            "finding": item["finding"],
        }
        for item in scenario_results
        if item["scenario_verdict"] != "CERTIFIED"
    )
    return gaps


def _remediation_recommendations(gaps: list[dict[str, Any]]) -> list[str]:
    if not gaps:
        return ["No remediation required before multi-provider live cognition readiness claim."]
    return [
        "Onboard real credentials for Claude, Gemini, and Mistral into the provider credential vault.",
        "Implement or attach live transport executors for Claude, Gemini, and Mistral.",
        "Run one-provider live certification for each non-OpenAI provider before claiming multi-provider live support.",
        "Re-run multi-provider live cognition certification after at least two providers return live responses in one governed cognition run.",
    ]


def _model_for_provider(provider_id: str) -> str:
    return {
        "openai": "gpt-5-certification-probe",
        "claude": "claude-live-not-certified",
        "gemini": "gemini-live-not-certified",
        "mistral": "mistral-live-not-certified",
    }[provider_id]


def _latest_report(base: Path, relative_report: str, expected_verdict: str) -> Path:
    if not base.exists():
        raise FailClosedRuntimeError(f"multi-provider certification failed closed: missing component root {base}")
    for cert_root in sorted(base.glob("CERT-*"), reverse=True):
        report_path = cert_root / relative_report
        if not report_path.exists():
            continue
        report = load_json(report_path)
        if report.get("final_verdict") == expected_verdict:
            return report_path
    raise FailClosedRuntimeError(f"multi-provider certification failed closed: no {expected_verdict} report under {base}")


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
        raise FailClosedRuntimeError("multi-provider live cognition certification artifact hash missing")
    candidate = dict(artifact)
    candidate.pop("artifact_hash", None)
    if replay_hash(candidate) != expected:
        raise FailClosedRuntimeError("multi-provider live cognition certification artifact hash mismatch")


def main() -> int:
    result = run_multi_provider_live_cognition_certification_v1()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"coverage_report={result['coverage_report_path']}")
    print(f"evidence_package={result['evidence_package_path']}")
    print(f"replay_package={result['replay_package_path']}")
    print(f"certification_report={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
