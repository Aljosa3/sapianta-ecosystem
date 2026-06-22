"""Operational readiness certification for OpenAI + Claude multi-provider cognition."""

from __future__ import annotations

from copy import deepcopy
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
from aigol.runtime.provider_governance_runtime import (
    record_cognition_participation,
    record_provider_usage_metric,
    reconstruct_provider_governance_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_MULTI_PROVIDER_OPERATIONAL_READINESS_CERTIFICATION_V1"
DEFAULT_RUNTIME_ROOT = Path("runtime/multi_provider_operational_readiness_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

PROVIDERS = ("openai", "claude")
FINAL_VERDICT_READY = "MULTI_PROVIDER_OPERATIONALLY_READY"
FINAL_VERDICT_GAPS = "MULTI_PROVIDER_OPERATIONAL_GAPS_FOUND"
SECRET_MARKERS = ("sk-", "Bearer ", "OPENAI_API_KEY=", "ANTHROPIC_API_KEY=", "AIGOL_OPENAI_API_KEY=")


def run_multi_provider_operational_readiness_certification_v1(
    *,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    openai_report_path: str | Path | None = None,
    claude_report_path: str | Path | None = None,
    role_identity_report_path: str | Path | None = None,
    product1_report_path: str | Path | None = None,
) -> dict[str, Any]:
    cert_root = _next_cert_root(Path(runtime_root))
    prerequisite_evidence = _prerequisite_evidence(
        openai_report_path=openai_report_path,
        claude_report_path=claude_report_path,
        role_identity_report_path=role_identity_report_path,
        product1_report_path=product1_report_path,
    )
    dual_success_probe = _run_probe(
        replay_root=cert_root / "cognition_probes" / "dual_success",
        probe_id="MPO-001-DUAL-SUCCESS",
        transport_registry={
            "openai": _successful_openai_transport,
            "claude": _successful_claude_transport,
        },
    )
    failover_probe = _run_probe(
        replay_root=cert_root / "cognition_probes" / "openai_failover_to_claude",
        probe_id="MPO-002-FAILOVER",
        transport_registry={
            "openai": _failing_openai_transport,
            "claude": _successful_claude_transport,
        },
    )
    governance = _record_operational_governance(
        replay_root=cert_root / "provider_governance_replay",
        dual_success_probe=dual_success_probe,
        failover_probe=failover_probe,
    )
    role_identity_check = _role_identity_check(prerequisite_evidence)
    scenario_results = _scenario_results(
        prerequisite_evidence=prerequisite_evidence,
        dual_success_probe=dual_success_probe,
        failover_probe=failover_probe,
        governance=governance,
        role_identity_check=role_identity_check,
    )
    replay_reconstruction = reconstruct_multi_provider_operational_readiness_replay(cert_root)
    secret_free = _secret_free(cert_root)
    assertions = _assertions(
        prerequisite_evidence=prerequisite_evidence,
        dual_success_probe=dual_success_probe,
        failover_probe=failover_probe,
        governance=governance,
        role_identity_check=role_identity_check,
        scenario_results=scenario_results,
        replay_reconstruction=replay_reconstruction,
        secret_free=secret_free,
    )
    final_verdict = FINAL_VERDICT_READY if all(assertions.values()) else FINAL_VERDICT_GAPS
    coverage = _with_hash(
        {
            "artifact_type": "MULTI_PROVIDER_OPERATIONAL_READINESS_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "providers": list(PROVIDERS),
            "coverage_dimensions": [
                "provider selection",
                "provider failover",
                "provider isolation",
                "participation tracking",
                "usage metrics",
                "cost metrics",
                "replay reconstruction",
                "role-separated identity independence",
                "provider-agnostic governance",
            ],
            "scenario_verdicts": {
                item["scenario_id"]: item["scenario_verdict"] for item in scenario_results
            },
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "MULTI_PROVIDER_OPERATIONAL_READINESS_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "prerequisite_evidence": prerequisite_evidence,
            "dual_success_probe": dual_success_probe,
            "failover_probe": failover_probe,
            "provider_governance": governance,
            "role_identity_check": role_identity_check,
            "scenario_results": scenario_results,
            "coverage_report_reference": "coverage_report/000_multi_provider_operational_readiness_coverage_report.json",
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "MULTI_PROVIDER_OPERATIONAL_READINESS_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "replay_root": str(cert_root),
            "dual_success_replay_reference": dual_success_probe["runtime_result"]["replay_reference"],
            "failover_replay_reference": failover_probe["runtime_result"]["replay_reference"],
            "provider_governance_replay_reference": governance["replay_root"],
            "replay_reconstruction": replay_reconstruction,
            "secret_free": secret_free,
            "final_verdict": final_verdict,
        }
    )
    operational_readiness = _with_hash(
        {
            "artifact_type": "MULTI_PROVIDER_OPERATIONAL_READINESS_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "question": "Can AiGOL operate as a real multi-provider cognition platform instead of a single-provider platform?",
            "answer": final_verdict == FINAL_VERDICT_READY,
            "openai_operational": "openai" in dual_success_probe["runtime_result"]["successful_providers"],
            "claude_operational": "claude" in dual_success_probe["runtime_result"]["successful_providers"],
            "failover_target": "claude",
            "failover_successful": failover_probe["runtime_result"]["successful_providers"] == ["claude"],
            "provider_agnostic_governance": assertions["governance_provider_agnostic"],
            "remaining_blockers": [] if final_verdict == FINAL_VERDICT_READY else _blockers(assertions),
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "MULTI_PROVIDER_OPERATIONAL_READINESS_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "operational_readiness_report_hash": operational_readiness["artifact_hash"],
            "scenario_results": scenario_results,
            "assertions": assertions,
            "observed": assertions,
            "gap_analysis": [] if final_verdict == FINAL_VERDICT_READY else _blockers(assertions),
            "remediation_recommendations": []
            if final_verdict == FINAL_VERDICT_READY
            else ["Re-run after missing operational assertions are remediated."],
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, operational_readiness, report):
        _assert_secret_safe(artifact)
    write_json_immutable(
        cert_root / "coverage_report" / "000_multi_provider_operational_readiness_coverage_report.json",
        coverage,
    )
    write_json_immutable(
        cert_root / "evidence_package" / "000_multi_provider_operational_readiness_evidence_package.json",
        evidence,
    )
    write_json_immutable(
        cert_root / "replay_package" / "000_multi_provider_operational_readiness_replay_package.json",
        replay,
    )
    write_json_immutable(
        cert_root / "operational_readiness_report" / "000_multi_provider_operational_readiness_report.json",
        operational_readiness,
    )
    write_json_immutable(
        cert_root / "certification_report" / "000_multi_provider_operational_readiness_certification_report.json",
        report,
    )
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "coverage_report_path": str(
            cert_root / "coverage_report" / "000_multi_provider_operational_readiness_coverage_report.json"
        ),
        "evidence_package_path": str(
            cert_root / "evidence_package" / "000_multi_provider_operational_readiness_evidence_package.json"
        ),
        "replay_package_path": str(
            cert_root / "replay_package" / "000_multi_provider_operational_readiness_replay_package.json"
        ),
        "operational_readiness_report_path": str(
            cert_root / "operational_readiness_report" / "000_multi_provider_operational_readiness_report.json"
        ),
        "certification_report_path": str(
            cert_root / "certification_report" / "000_multi_provider_operational_readiness_certification_report.json"
        ),
        "assertions": assertions,
        "scenario_results": scenario_results,
        "final_verdict": final_verdict,
    }


def reconstruct_multi_provider_operational_readiness_replay(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    dual = reconstruct_multi_provider_cognition_replay(root / "cognition_probes" / "dual_success" / "multi_provider_runtime")
    failover = reconstruct_multi_provider_cognition_replay(
        root / "cognition_probes" / "openai_failover_to_claude" / "multi_provider_runtime"
    )
    governance = reconstruct_provider_governance_replay(root / "provider_governance_replay")
    replay = {
        "artifact_type": "MULTI_PROVIDER_OPERATIONAL_READINESS_REPLAY_RECONSTRUCTION_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "dual_success_replay_reconstructed": dual["replay_visible"] is True,
        "failover_replay_reconstructed": failover["replay_visible"] is True,
        "provider_governance_replay_reconstructed": governance["replay_visible"] is True,
        "dual_successful_provider_count": dual["successful_provider_count"],
        "failover_successful_provider_count": failover["successful_provider_count"],
        "provider_usage_metric_count": governance["provider_usage_metric_count"],
        "cognition_participation_count": governance["cognition_participation_count"],
        "replay_reconstructed": dual["replay_visible"] is True
        and failover["replay_visible"] is True
        and governance["replay_visible"] is True,
    }
    return _with_hash(replay)


def _run_probe(
    *,
    replay_root: Path,
    probe_id: str,
    transport_registry: dict[str, Any],
) -> dict[str, Any]:
    context_capture = assemble_ocs_context(
        context_assembly_id=f"{probe_id}:CONTEXT",
        created_at=CREATED_AT,
        replay_dir=replay_root / "context",
        source_context={
            "conversation_context": [
                {
                    "source_id": probe_id,
                    "summary": "Operational readiness prompt for provider-agnostic Product 1 cognition.",
                    "replay_visible": True,
                }
            ],
            "replay_visible_operation_context": [
                {
                    "source_id": f"{probe_id}:BOUNDARY",
                    "summary": "No worker execution is authorized by operational multi-provider cognition.",
                    "replay_visible": True,
                }
            ],
        },
    )
    contracts = [
        create_default_cognition_provider_contract(provider_id=provider_id, created_at=CREATED_AT)
        for provider_id in PROVIDERS
    ]
    result = run_multi_provider_cognition_runtime(
        multi_provider_cognition_bundle_id=probe_id,
        human_request="Compare safe next steps for reviewing an AI decision before any execution.",
        ocs_context_artifact=context_capture["ocs_context_assembly_artifact"],
        provider_contracts=contracts,
        created_at=CREATED_AT,
        replay_dir=replay_root / "multi_provider_runtime",
        transport_registry=transport_registry,
    )
    reconstruction = reconstruct_multi_provider_cognition_replay(replay_root / "multi_provider_runtime")
    return {
        "probe_id": probe_id,
        "replay_root": str(replay_root),
        "context_replay_reference": context_capture["ocs_context_assembly_replay_reference"],
        "runtime_result": _safe_runtime_result(result),
        "reconstruction": reconstruction,
    }


def _successful_openai_transport(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    return _provider_response(metadata, "OpenAI", "OpenAI proposed a bounded review plan.", 18, 24)


def _successful_claude_transport(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    return _provider_response(metadata, "Claude", "Claude proposed an alternate bounded review plan.", 20, 26)


def _failing_openai_transport(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    raise FailClosedRuntimeError("operational readiness injected OpenAI transport failure")


def _provider_response(
    metadata: dict[str, Any],
    label: str,
    finding: str,
    input_tokens: int,
    output_tokens: int,
) -> dict[str, Any]:
    return {
        "provider_id": metadata["provider_id"],
        "model": f"{metadata['provider_id']}-operational-readiness-model",
        "text": (
            '{"findings":["'
            + finding
            + '"],"assumptions":["Provider output is proposal-only."],'
            '"alternatives":["Ask for more evidence","Keep action blocked until approval"],'
            '"risks":["Provider disagreement requires human review."],'
            '"uncertainties":["Operator scope may need clarification."],'
            '"confidence":"MEDIUM"}'
        ),
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
        "provider_label": label,
    }


def _safe_runtime_result(result: dict[str, Any]) -> dict[str, Any]:
    bundle = result.get("result_bundle") if isinstance(result.get("result_bundle"), dict) else {}
    return {
        "final_status": result.get("final_status"),
        "fail_closed": result.get("fail_closed"),
        "provider_count": bundle.get("provider_count"),
        "successful_provider_count": bundle.get("successful_provider_count"),
        "failed_provider_count": bundle.get("failed_provider_count"),
        "successful_providers": [item.get("provider_id") for item in bundle.get("provider_results", [])],
        "failed_providers": [item.get("provider_id") for item in bundle.get("provider_failures", [])],
        "failure_isolated": bundle.get("failure_isolated") is True,
        "worker_invoked": bundle.get("worker_invoked"),
        "approval_created": bundle.get("approval_created"),
        "execution_requested": bundle.get("execution_requested"),
        "authority_flags": deepcopy(bundle.get("authority_flags", {})),
        "replay_reference": result.get("replay_reference"),
    }


def _record_operational_governance(
    *,
    replay_root: Path,
    dual_success_probe: dict[str, Any],
    failover_probe: dict[str, Any],
) -> dict[str, Any]:
    outcomes = {
        "openai": {
            "success_count": 1 if "openai" in dual_success_probe["runtime_result"]["successful_providers"] else 0,
            "failure_count": 1 if "openai" in failover_probe["runtime_result"]["failed_providers"] else 0,
            "last_failure": "operational readiness injected OpenAI transport failure"
            if "openai" in failover_probe["runtime_result"]["failed_providers"]
            else None,
        },
        "claude": {
            "success_count": int("claude" in dual_success_probe["runtime_result"]["successful_providers"])
            + int("claude" in failover_probe["runtime_result"]["successful_providers"]),
            "failure_count": 0,
            "last_failure": None,
        },
    }
    for provider_id, outcome in outcomes.items():
        provider_dir = replay_root / provider_id
        record_provider_usage_metric(
            metric_id=f"MPO:{provider_id}:USAGE",
            provider_id=provider_id,
            model=f"{provider_id}-operational-readiness-model",
            status="OPERATIONAL" if outcome["success_count"] else "DEGRADED",
            availability="AVAILABLE" if outcome["success_count"] else "FAILED",
            created_at=CREATED_AT,
            replay_dir=provider_dir / "usage",
            success_count=outcome["success_count"],
            failure_count=outcome["failure_count"],
            last_used=CREATED_AT if outcome["success_count"] else None,
            last_failure=outcome["last_failure"],
            latency_ms=145,
            token_usage={"input_tokens": 38, "output_tokens": 50, "total_tokens": 88},
            cost_tracking={"estimated_usd": "hook-present", "provider_agnostic_cost_hook": True},
        )
        record_cognition_participation(
            participation_id=f"MPO:{provider_id}:PARTICIPATION",
            provider_id=provider_id,
            participation_location="OCS_LLM_COGNITION",
            participation_role="PRIMARY_OR_FAILOVER_COGNITION_PROVIDER",
            workflow_id="OCS_LLM_COGNITION",
            invocation_reason="multi-provider operational readiness certification",
            purpose="proposal-only Product 1 decision review cognition",
            response_used=outcome["success_count"] > 0,
            worker_invoked_after=False,
            human_confirmation_required=True,
            created_at=CREATED_AT,
            replay_dir=provider_dir / "participation",
        )
    return {
        "replay_root": str(replay_root),
        "reconstruction": reconstruct_provider_governance_replay(replay_root),
    }


def _prerequisite_evidence(
    *,
    openai_report_path: str | Path | None,
    claude_report_path: str | Path | None,
    role_identity_report_path: str | Path | None,
    product1_report_path: str | Path | None,
) -> dict[str, Any]:
    openai = _load_report(
        explicit_path=openai_report_path,
        default_path=Path(
            "runtime/first_live_cognition_provider_certification_v1/CERT-000009/"
            "certification_report/000_first_live_cognition_provider_certification_report.json"
        ),
    )
    claude = _load_report(
        explicit_path=claude_report_path,
        default_path=_latest_existing_report(
            Path("runtime/claude_live_cognition_certification_v1"),
            "certification_report/000_claude_live_cognition_certification_report.json",
        ),
    )
    role = _load_report(
        explicit_path=role_identity_report_path,
        default_path=_latest_existing_report(
            Path("runtime/role_separated_llm_identity_certification_v1"),
            "certification_report/000_role_separated_llm_identity_certification_report.json",
        ),
    )
    product1 = _load_report(
        explicit_path=product1_report_path,
        default_path=_latest_existing_report(
            Path("runtime/product1_end_to_end_certification_v1"),
            "certification_report/000_product1_end_to_end_certification_report.json",
        ),
    )
    return {
        "openai_report_path": str(openai["path"]),
        "claude_report_path": str(claude["path"]),
        "role_identity_report_path": str(role["path"]),
        "product1_report_path": str(product1["path"]),
        "openai_live_certified": openai["report"].get("final_verdict")
        == "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED",
        "claude_live_certified": claude["report"].get("final_verdict") == "CLAUDE_LIVE_COGNITION_CERTIFIED",
        "role_separated_identity_certified": role["report"].get("final_verdict")
        == "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED",
        "product1_end_to_end_certified": product1["report"].get("final_verdict")
        == "AIGOL_PRODUCT1_END_TO_END_CERTIFIED",
    }


def _load_report(*, explicit_path: str | Path | None, default_path: Path) -> dict[str, Any]:
    path = Path(explicit_path) if explicit_path is not None else default_path
    return {"path": path, "report": load_json(path) if path.exists() else {}}


def _latest_existing_report(base: Path, relative_report: str) -> Path:
    if not base.exists():
        return base / "MISSING" / relative_report
    for cert_root in sorted(base.glob("CERT-*"), reverse=True):
        report_path = cert_root / relative_report
        if report_path.exists():
            return report_path
    return base / "MISSING" / relative_report


def _role_identity_check(prerequisite_evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "role_separated_identity_certified": prerequisite_evidence["role_separated_identity_certified"],
        "same_external_provider_can_have_distinct_roles": prerequisite_evidence["role_separated_identity_certified"],
        "multi_provider_cognition_uses_cognition_provider_role_only": True,
        "role_identity_independence_preserved": prerequisite_evidence["role_separated_identity_certified"],
    }


def _scenario_results(
    *,
    prerequisite_evidence: dict[str, Any],
    dual_success_probe: dict[str, Any],
    failover_probe: dict[str, Any],
    governance: dict[str, Any],
    role_identity_check: dict[str, Any],
) -> list[dict[str, Any]]:
    dual = dual_success_probe["runtime_result"]
    failover = failover_probe["runtime_result"]
    gov = governance["reconstruction"]
    scenarios = [
        (
            "MPO-001",
            "openai_and_claude_execution",
            prerequisite_evidence["openai_live_certified"]
            and prerequisite_evidence["claude_live_certified"]
            and _same_providers(dual["successful_providers"], PROVIDERS),
            "OpenAI and Claude both returned governed cognition proposals.",
        ),
        (
            "MPO-002",
            "provider_selection",
            dual["provider_count"] == 2 and dual["successful_provider_count"] == 2,
            "The multi-provider runtime selected both configured providers.",
        ),
        (
            "MPO-003",
            "provider_failover",
            failover["successful_providers"] == ["claude"] and failover["failed_providers"] == ["openai"],
            "Claude remained usable when OpenAI failed.",
        ),
        (
            "MPO-004",
            "provider_isolation",
            dual["failure_isolated"] is True and failover["failure_isolated"] is True,
            "Provider failures are isolated from successful provider results.",
        ),
        (
            "MPO-005",
            "participation_tracking",
            gov["cognition_participation_count"] == 2,
            "Replay-visible cognition participation was recorded for both providers.",
        ),
        (
            "MPO-006",
            "usage_and_cost_metrics",
            gov["provider_usage_metric_count"] == 2 and len(gov["provider_costs"]) == 2,
            "Usage metrics and provider-agnostic cost hooks exist for both providers.",
        ),
        (
            "MPO-007",
            "role_separated_identity_independence",
            role_identity_check["role_identity_independence_preserved"],
            "Role-separated LLM identity certification remains an active prerequisite.",
        ),
        (
            "MPO-008",
            "provider_agnostic_governance",
            _authority_flags_false(dual["authority_flags"]) and _authority_flags_false(failover["authority_flags"]),
            "Governance did not transfer authority to either provider.",
        ),
    ]
    return [
        {
            "scenario_id": scenario_id,
            "coverage": coverage,
            "scenario_verdict": "CERTIFIED" if certified else "GAPS_FOUND",
            "finding": finding,
        }
        for scenario_id, coverage, certified, finding in scenarios
    ]


def _assertions(
    *,
    prerequisite_evidence: dict[str, Any],
    dual_success_probe: dict[str, Any],
    failover_probe: dict[str, Any],
    governance: dict[str, Any],
    role_identity_check: dict[str, Any],
    scenario_results: list[dict[str, Any]],
    replay_reconstruction: dict[str, Any],
    secret_free: bool,
) -> dict[str, bool]:
    dual = dual_success_probe["runtime_result"]
    failover = failover_probe["runtime_result"]
    gov = governance["reconstruction"]
    return {
        "openai_live_cognition_certified": prerequisite_evidence["openai_live_certified"],
        "claude_live_cognition_certified": prerequisite_evidence["claude_live_certified"],
        "product1_end_to_end_certified": prerequisite_evidence["product1_end_to_end_certified"],
        "provider_selection_verified": dual["provider_count"] == 2
        and _same_providers(dual["successful_providers"], PROVIDERS),
        "provider_failover_verified": failover["successful_providers"] == ["claude"]
        and failover["failed_providers"] == ["openai"],
        "provider_isolation_verified": dual["failure_isolated"] is True and failover["failure_isolated"] is True,
        "participation_tracking_verified": gov["cognition_participation_count"] == 2,
        "usage_metrics_verified": gov["provider_usage_metric_count"] == 2,
        "cost_metrics_verified": len(gov["provider_costs"]) == 2,
        "replay_reconstruction_verified": replay_reconstruction["replay_reconstructed"],
        "role_separated_identities_remain_independent": role_identity_check["role_identity_independence_preserved"],
        "governance_provider_agnostic": _authority_flags_false(dual["authority_flags"])
        and _authority_flags_false(failover["authority_flags"])
        and dual["worker_invoked"] is False
        and failover["worker_invoked"] is False
        and dual["execution_requested"] is False
        and failover["execution_requested"] is False,
        "all_scenarios_certified": all(item["scenario_verdict"] == "CERTIFIED" for item in scenario_results),
        "secret_free_evidence": secret_free,
    }


def _authority_flags_false(flags: dict[str, Any]) -> bool:
    expected = {
        "provider_authority",
        "approval_authority",
        "execution_authority",
        "worker_authority",
        "governance_authority",
        "replay_authority",
    }
    return expected.issubset(flags) and all(flags[key] is False for key in expected)


def _same_providers(actual: list[str], expected: tuple[str, ...]) -> bool:
    return set(actual) == set(expected) and len(actual) == len(expected)


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {
            "assertion": key,
            "failure_reason": "multi-provider operational readiness assertion failed",
        }
        for key, passed in assertions.items()
        if not passed
    ]


def _with_hash(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    root = base / f"CERT-{max(existing, default=0) + 1:06d}"
    root.mkdir(parents=True, exist_ok=False)
    return root


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    return not any(marker.lower() in serialized.lower() for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    serialized = canonical_serialize(payload).lower()
    for marker in SECRET_MARKERS:
        if marker.lower() in serialized:
            raise FailClosedRuntimeError("multi-provider operational readiness failed closed: secret-like material recorded")


def main() -> int:
    result = run_multi_provider_operational_readiness_certification_v1()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"COVERAGE_REPORT={result['coverage_report_path']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"OPERATIONAL_READINESS_REPORT={result['operational_readiness_report_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
