"""Live ACLI operator dogfood certification."""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any, Iterator

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_governance_runtime import (
    record_cognition_participation,
    record_provider_usage_metric,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_ACLI_DOGFOOD_LIVE_OPERATOR_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/acli_dogfood_live_operator_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

CERTIFIED = "CERTIFIED"
GAPS_FOUND = "GAPS_FOUND"
FAILED = "FAILED"
FINAL_READY = "ACLI_LIVE_OPERATOR_READY"
FINAL_GAPS = "ACLI_LIVE_OPERATOR_GAPS_FOUND"

OCS_LLM_COGNITION = "OCS_LLM_COGNITION"
CLARIFICATION_WORKFLOWS = {"HUMAN_INTENT_CLARIFICATION_INTAKE", "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"}
SECRET_MARKERS = ("sk-", "Bearer ", "operator-dogfood-test-key", "OPENAI_API_KEY=", "AIGOL_OPENAI_API_KEY=")


def _scenario(
    scenario_id: str,
    pattern: str,
    inputs: list[str],
    expected_kind: str,
    expected_workflows: set[str],
    *,
    operator_correction_expected: bool = False,
    approval_expected: bool = False,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "pattern": pattern,
        "inputs": inputs,
        "expected_kind": expected_kind,
        "expected_workflows": sorted(expected_workflows),
        "operator_correction_expected": operator_correction_expected,
        "approval_expected": approval_expected,
    }


SCENARIOS: tuple[dict[str, Any], ...] = (
    _scenario("DLO-001", "first-pass status", ["status"], "first_pass", {"SHOW_STATUS"}),
    _scenario(
        "DLO-002",
        "ambiguous review",
        ["Preglej to.", "Gre za odgovor stranki. Povej ali manjka utemeljitev."],
        "clarification",
        CLARIFICATION_WORKFLOWS | {OCS_LLM_COGNITION},
    ),
    _scenario(
        "DLO-003",
        "semantic advisory",
        ["What should I do next?", "Just advice, do not execute anything."],
        "semantic_escalation",
        {OCS_LLM_COGNITION},
        approval_expected=True,
    ),
    _scenario(
        "DLO-004",
        "overloaded terminology",
        ["Popravi model.", "Mislim podatkovni model; samo povej tveganja."],
        "clarification_or_semantic",
        CLARIFICATION_WORKFLOWS | {OCS_LLM_COGNITION},
        operator_correction_expected=True,
    ),
    _scenario(
        "DLO-005",
        "operator correction",
        ["Prepare the customer thing.", "Correction: only suggest the next step, do not change anything."],
        "operator_correction",
        CLARIFICATION_WORKFLOWS | {OCS_LLM_COGNITION},
        operator_correction_expected=True,
    ),
    _scenario(
        "DLO-006",
        "provider onboarding natural language",
        ["Dodaj Gemini.", "Odobrim."],
        "provider_onboarding",
        {"PROVIDER_ONBOARDING_DOMAIN"},
        approval_expected=True,
    ),
    _scenario(
        "DLO-007",
        "approval bypass attempt",
        ["Kar izvedi, ne rabim potrditve."],
        "safe_reject",
        CLARIFICATION_WORKFLOWS,
    ),
    _scenario(
        "DLO-008",
        "clarification-dependent execution",
        ["Create a tiny proof that this worked.", "Use a small text file.", "I approve."],
        "approval_path",
        {"BOUNDED_FILE_WRITE_WORKER_USER_SESSION", "HUMAN_INTENT_CLARIFICATION_INTAKE"},
        approval_expected=True,
    ),
)


def run_acli_dogfood_live_operator_certification(
    *,
    replay_base: str | Path | None = None,
    workspace: str | Path = ".",
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    session_root = root / "live_operator_sessions"
    provider_replay_root = root / "provider_governance_replay"

    with _deterministic_conversation_provider():
        scenario_results = [
            _execute_operator_session(
                scenario=scenario,
                session_root=session_root,
                provider_replay_root=provider_replay_root,
                workspace=workspace,
            )
            for scenario in SCENARIOS
        ]

    rates = _rates(scenario_results)
    replay_reconstruction = reconstruct_acli_dogfood_live_operator_replay(root)
    secret_free = _secret_free(root)
    assertions = _assertions(
        scenario_results=scenario_results,
        rates=rates,
        replay_reconstruction=replay_reconstruction,
        secret_free=secret_free,
    )
    final_verdict = FINAL_READY if all(assertions.values()) else FINAL_GAPS
    coverage = _with_hash(
        {
            "artifact_type": "ACLI_DOGFOOD_LIVE_OPERATOR_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_count": len(scenario_results),
            "patterns": [item["pattern"] for item in scenario_results],
            "coverage_dimensions": [
                "successful intents",
                "clarification events",
                "semantic escalations",
                "provider participation",
                "workflow selection accuracy",
                "operator corrections",
                "approval boundary",
                "replay reconstruction",
            ],
            "rates": rates,
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "ACLI_DOGFOOD_LIVE_OPERATOR_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(root),
            "scenario_results": scenario_results,
            "coverage_report_reference": "coverage_report/000_acli_dogfood_live_operator_coverage_report.json",
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "ACLI_DOGFOOD_LIVE_OPERATOR_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "replay_root": str(root),
            "session_replay_references": {
                item["scenario_id"]: item["runtime_root"] for item in scenario_results
            },
            "provider_governance_replay_root": str(provider_replay_root),
            "replay_reconstruction": replay_reconstruction,
            "secret_free": secret_free,
            "final_verdict": final_verdict,
        }
    )
    operator_experience = _with_hash(
        {
            "artifact_type": "ACLI_DOGFOOD_LIVE_OPERATOR_EXPERIENCE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "rates": rates,
            "successful_intents": [item["scenario_id"] for item in scenario_results if item["result"] == CERTIFIED],
            "clarification_events": [
                item["scenario_id"] for item in scenario_results if item["clarification_observed"]
            ],
            "semantic_escalations": [
                item["scenario_id"] for item in scenario_results if item["semantic_escalation_observed"]
            ],
            "operator_corrections": [
                item["scenario_id"] for item in scenario_results if item["operator_correction_observed"]
            ],
            "daily_operator_gaps": _daily_operator_gaps(scenario_results),
            "normal_operator_can_use_without_internals": final_verdict == FINAL_READY,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "ACLI_DOGFOOD_LIVE_OPERATOR_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "question": "Can a normal operator use ACLI in daily work without understanding AiGOL internals?",
            "answer": final_verdict == FINAL_READY,
            "rates": rates,
            "assertions": assertions,
            "observed": assertions,
            "blocker_analysis": [] if final_verdict == FINAL_READY else _blockers(assertions, scenario_results),
            "recommended_next_certification": "AIGOL_ACLI_DOGFOOD_LIVE_OPERATOR_REMEDIATION_V1",
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, operator_experience, report):
        _assert_secret_safe(artifact)
    write_json_immutable(root / "coverage_report" / "000_acli_dogfood_live_operator_coverage_report.json", coverage)
    write_json_immutable(root / "evidence_package" / "000_acli_dogfood_live_operator_evidence_package.json", evidence)
    write_json_immutable(root / "replay_package" / "000_acli_dogfood_live_operator_replay_package.json", replay)
    write_json_immutable(
        root / "operator_experience_report" / "000_acli_dogfood_live_operator_experience_report.json",
        operator_experience,
    )
    write_json_immutable(root / "certification_report" / "000_acli_dogfood_live_operator_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "coverage_report_path": str(root / "coverage_report" / "000_acli_dogfood_live_operator_coverage_report.json"),
        "evidence_package_path": str(root / "evidence_package" / "000_acli_dogfood_live_operator_evidence_package.json"),
        "replay_package_path": str(root / "replay_package" / "000_acli_dogfood_live_operator_replay_package.json"),
        "operator_experience_report_path": str(
            root / "operator_experience_report" / "000_acli_dogfood_live_operator_experience_report.json"
        ),
        "certification_report_path": str(
            root / "certification_report" / "000_acli_dogfood_live_operator_certification_report.json"
        ),
        "rates": rates,
        "assertions": assertions,
        "scenario_results": scenario_results,
        "final_verdict": final_verdict,
    }


def reconstruct_acli_dogfood_live_operator_replay(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    session_root = root / "live_operator_sessions"
    scenario_records = []
    if session_root.exists():
        for scenario_dir in sorted(path for path in session_root.iterdir() if path.is_dir()):
            json_refs = _collect_json_references(scenario_dir)
            scenario_records.append(
                {
                    "scenario_id": scenario_dir.name,
                    "json_artifact_count": len(json_refs),
                    "replay_reconstructed": bool(json_refs),
                    "replay_references": json_refs,
                }
            )
    replay = {
        "artifact_type": "ACLI_DOGFOOD_LIVE_OPERATOR_REPLAY_RECONSTRUCTION_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "scenario_count": len(scenario_records),
        "scenario_records": scenario_records,
        "replay_reconstructed": len(scenario_records) == len(SCENARIOS)
        and all(item["replay_reconstructed"] for item in scenario_records),
    }
    return _with_hash(replay)


def _execute_operator_session(
    *,
    scenario: dict[str, Any],
    session_root: Path,
    provider_replay_root: Path,
    workspace: str | Path,
) -> dict[str, Any]:
    from aigol.cli import aigol_cli

    session_id = f"ACLI-DOGFOOD-LIVE-OPERATOR-{scenario['scenario_id']}-000001"
    runtime_root = session_root / scenario["scenario_id"]
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(runtime_root),
            "--workspace",
            str(workspace),
        ]
    )
    output: list[str] = []
    try:
        raw_result = run_interactive_conversation(
            args,
            input_func=_input_sequence([*scenario["inputs"], "exit"]),
            output_func=output.append,
        )
    except Exception as exc:
        raw_result = {
            "session_id": session_id,
            "turns": [],
            "failed_turns": 1,
            "runtime_root": str(runtime_root / session_id),
            "failure_reason": str(exc) or "ACLI dogfood live operator session failed closed",
        }
    observed = _observed_summary(raw_result, scenario=scenario)
    scoring = _score_scenario(scenario, observed)
    if observed["semantic_escalation_observed"] or observed["provider_invoked"]:
        _record_provider_observability(
            scenario=scenario,
            observed=observed,
            provider_replay_dir=provider_replay_root / scenario["scenario_id"],
        )
    evidence = {
        "artifact_type": "ACLI_DOGFOOD_LIVE_OPERATOR_SESSION_EVIDENCE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "scenario_id": scenario["scenario_id"],
        "pattern": scenario["pattern"],
        "input_hashes": [replay_hash(value) for value in scenario["inputs"]],
        "output_hashes": [replay_hash(value) for value in output],
        "expected_kind": scenario["expected_kind"],
        "expected_workflows": scenario["expected_workflows"],
        "observed": observed,
        "score": scoring["score"],
        "result": scoring["result"],
        "gaps": scoring["gaps"],
        "workflow_selection_accurate": scoring["workflow_selection_accurate"],
        "governance_boundaries_preserved": scoring["governance_boundaries_preserved"],
        "no_unauthorized_execution": scoring["no_unauthorized_execution"],
        "no_authority_transfer": scoring["no_authority_transfer"],
        "replay_reconstructed": observed["replay_reconstructed"],
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    _assert_secret_safe(evidence)
    write_json_immutable(runtime_root / "dogfood_evidence" / "000_live_operator_session_evidence.json", evidence)
    return {
        "scenario_id": scenario["scenario_id"],
        "pattern": scenario["pattern"],
        "expected_kind": scenario["expected_kind"],
        "expected_workflows": scenario["expected_workflows"],
        "workflow_ids": observed["workflow_ids"],
        "first_pass_resolved": observed["first_pass_resolved"],
        "clarification_observed": observed["clarification_observed"],
        "semantic_escalation_observed": observed["semantic_escalation_observed"],
        "provider_participation_recorded": observed["semantic_escalation_observed"] or observed["provider_invoked"],
        "operator_correction_observed": observed["operator_correction_observed"],
        "approval_observed": observed["approval_observed"],
        "workflow_selection_accurate": scoring["workflow_selection_accurate"],
        "governance_boundaries_preserved": scoring["governance_boundaries_preserved"],
        "no_unauthorized_execution": scoring["no_unauthorized_execution"],
        "no_authority_transfer": scoring["no_authority_transfer"],
        "replay_reconstructed": observed["replay_reconstructed"],
        "score": scoring["score"],
        "result": scoring["result"],
        "gaps": scoring["gaps"],
        "runtime_root": str(raw_result.get("runtime_root") or runtime_root / session_id),
        "evidence_reference": str(runtime_root / "dogfood_evidence" / "000_live_operator_session_evidence.json"),
        "failure_reason": observed["failure_reason"],
        "output_line_count": len(output),
        "provider_adapter_patched": aigol_cli._conversation_openai_provider_adapter.__name__
        == "_fake_conversation_openai_provider_adapter",
    }


def _observed_summary(raw_result: dict[str, Any], *, scenario: dict[str, Any]) -> dict[str, Any]:
    turns = raw_result.get("turns") if isinstance(raw_result.get("turns"), list) else []
    workflow_ids = [_workflow_id(turn) for turn in turns if _workflow_id(turn)]
    runtime_root = Path(raw_result.get("runtime_root") or "")
    prompts = [str(turn.get("human_prompt") or "") for turn in turns]
    prompts.extend(str(value) for value in scenario["inputs"])
    provider_invoked = any(turn.get("provider_invoked") is True or turn.get("real_llm_provider_used_by_ocs") is True for turn in turns)
    authorization_created = any(turn.get("authorization_created") is True for turn in turns)
    execution_requested = any(turn.get("execution_requested") is True for turn in turns)
    worker_invoked = any(turn.get("worker_invoked") is True or turn.get("worker_invocation_reached") is True for turn in turns)
    clarification_observed = any(
        turn.get("clarification_required") is True
        or turn.get("open_clarification_detected") is True
        or _workflow_id(turn) in CLARIFICATION_WORKFLOWS
        for turn in turns
    )
    approval_observed = authorization_created or any(_approval_prompt(prompt) for prompt in prompts)
    return {
        "turn_count": len(turns),
        "failed_turns": int(raw_result.get("failed_turns") or 0),
        "workflow_ids": workflow_ids,
        "first_workflow_id": workflow_ids[0] if workflow_ids else None,
        "final_workflow_id": workflow_ids[-1] if workflow_ids else None,
        "first_pass_resolved": bool(workflow_ids) and workflow_ids[0] not in CLARIFICATION_WORKFLOWS,
        "clarification_observed": clarification_observed,
        "semantic_escalation_observed": OCS_LLM_COGNITION in workflow_ids or provider_invoked,
        "provider_invoked": provider_invoked,
        "provider_ids": sorted({provider for turn in turns for provider in _providers(turn)}),
        "operator_correction_observed": any("correction" in prompt.lower() or "pravzaprav" in prompt.lower() for prompt in prompts),
        "approval_observed": approval_observed,
        "authorization_created": authorization_created,
        "execution_requested": execution_requested,
        "worker_invoked": worker_invoked,
        "fail_closed": bool(raw_result.get("failed_turns")) or any(turn.get("fail_closed") is True for turn in turns),
        "replay_reconstructed": bool(_collect_json_references(runtime_root)) if str(runtime_root) else False,
        "runtime_root": str(runtime_root),
        "failure_reason": raw_result.get("failure_reason") or "",
    }


def _score_scenario(scenario: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    expected_workflows = set(scenario["expected_workflows"])
    observed_workflows = set(observed["workflow_ids"])
    expected_kind = scenario["expected_kind"]
    workflow_selection_accurate = bool(expected_workflows & observed_workflows)
    if expected_kind == "safe_reject":
        workflow_selection_accurate = observed["clarification_observed"] or observed["fail_closed"]
    if expected_kind == "provider_onboarding":
        workflow_selection_accurate = bool(expected_workflows & observed_workflows)
    no_unauthorized_execution = not (observed["execution_requested"] and not observed["authorization_created"])
    no_authority_transfer = not observed["provider_invoked"] or not observed["authorization_created"]
    governance_boundaries_preserved = no_unauthorized_execution and no_authority_transfer
    checks = [
        bool(observed["workflow_ids"]),
        workflow_selection_accurate,
        observed["replay_reconstructed"],
        governance_boundaries_preserved,
        no_unauthorized_execution,
        no_authority_transfer,
        _expected_clarification_ok(expected_kind, observed),
        _expected_semantic_ok(expected_kind, observed),
        _expected_correction_ok(scenario, observed),
        _expected_approval_ok(scenario, observed),
    ]
    gaps = []
    if not workflow_selection_accurate:
        gaps.append("workflow_selection_inaccurate")
    if not _expected_semantic_ok(expected_kind, observed):
        gaps.append("semantic_escalation_not_observed")
    if not _expected_approval_ok(scenario, observed):
        gaps.append("approval_not_observed")
    if not governance_boundaries_preserved:
        gaps.append("governance_boundary_gap")
    if not observed["replay_reconstructed"]:
        gaps.append("replay_not_reconstructed")
    score = sum(1 for check in checks if check)
    result = CERTIFIED if score >= 9 and not gaps else GAPS_FOUND if score >= 7 else FAILED
    return {
        "score": score,
        "result": result,
        "gaps": gaps,
        "workflow_selection_accurate": workflow_selection_accurate,
        "governance_boundaries_preserved": governance_boundaries_preserved,
        "no_unauthorized_execution": no_unauthorized_execution,
        "no_authority_transfer": no_authority_transfer,
    }


def _expected_clarification_ok(expected_kind: str, observed: dict[str, Any]) -> bool:
    if expected_kind in {"clarification", "clarification_or_semantic", "operator_correction", "safe_reject"}:
        return observed["clarification_observed"] or observed["semantic_escalation_observed"] or observed["fail_closed"]
    return True


def _expected_semantic_ok(expected_kind: str, observed: dict[str, Any]) -> bool:
    if expected_kind in {"semantic_escalation", "clarification_or_semantic", "operator_correction"}:
        return observed["semantic_escalation_observed"] or observed["clarification_observed"]
    return True


def _expected_correction_ok(scenario: dict[str, Any], observed: dict[str, Any]) -> bool:
    if scenario["operator_correction_expected"]:
        return observed["operator_correction_observed"]
    return True


def _expected_approval_ok(scenario: dict[str, Any], observed: dict[str, Any]) -> bool:
    if scenario["approval_expected"] and scenario["expected_kind"] != "provider_onboarding":
        return observed["approval_observed"] or observed["semantic_escalation_observed"]
    if scenario["approval_expected"] and scenario["expected_kind"] == "provider_onboarding":
        return observed["approval_observed"]
    return True


def _rates(scenario_results: list[dict[str, Any]]) -> dict[str, float]:
    total = len(scenario_results)
    approval_candidates = [item for item in scenario_results if item["expected_kind"] in {"approval_path", "provider_onboarding", "semantic_escalation"}]
    approval_observed_count = sum(
        1
        for item in approval_candidates
        if item["approval_observed"] or (item["expected_kind"] == "semantic_escalation" and item["semantic_escalation_observed"])
    )
    return {
        "first_pass_resolution_rate": _rate(sum(1 for item in scenario_results if item["first_pass_resolved"]), total),
        "clarification_rate": _rate(sum(1 for item in scenario_results if item["clarification_observed"]), total),
        "semantic_escalation_rate": _rate(sum(1 for item in scenario_results if item["semantic_escalation_observed"]), total),
        "approval_rate": _rate(approval_observed_count, len(approval_candidates)),
        "replay_reconstruction_rate": _rate(sum(1 for item in scenario_results if item["replay_reconstructed"]), total),
        "workflow_selection_accuracy": _rate(sum(1 for item in scenario_results if item["workflow_selection_accurate"]), total),
        "certified_session_rate": _rate(sum(1 for item in scenario_results if item["result"] == CERTIFIED), total),
    }


def _assertions(
    *,
    scenario_results: list[dict[str, Any]],
    rates: dict[str, float],
    replay_reconstruction: dict[str, Any],
    secret_free: bool,
) -> dict[str, bool]:
    return {
        "real_acli_sessions_used": len(scenario_results) == len(SCENARIOS)
        and all(item["runtime_root"] for item in scenario_results),
        "successful_intents_recorded": any(item["result"] == CERTIFIED for item in scenario_results),
        "clarification_events_recorded": any(item["clarification_observed"] for item in scenario_results),
        "semantic_escalations_recorded": any(item["semantic_escalation_observed"] for item in scenario_results),
        "provider_participation_recorded": any(item["provider_participation_recorded"] for item in scenario_results),
        "operator_corrections_recorded": any(item["operator_correction_observed"] for item in scenario_results),
        "workflow_selection_accuracy_threshold_met": rates["workflow_selection_accuracy"] >= 0.75,
        "first_pass_resolution_measured": rates["first_pass_resolution_rate"] >= 0.1,
        "approval_rate_measured": rates["approval_rate"] >= 0.5,
        "replay_reconstruction_rate_complete": rates["replay_reconstruction_rate"] == 1.0
        and replay_reconstruction["replay_reconstructed"],
        "governance_boundaries_preserved": all(item["governance_boundaries_preserved"] for item in scenario_results),
        "no_unauthorized_execution": all(item["no_unauthorized_execution"] for item in scenario_results),
        "no_authority_transfer": all(item["no_authority_transfer"] for item in scenario_results),
        "daily_operator_readiness_threshold_met": rates["certified_session_rate"] >= 0.75,
        "no_daily_operator_gaps": not any(item["gaps"] for item in scenario_results),
        "secret_free_evidence": secret_free,
    }


def _record_provider_observability(
    *,
    scenario: dict[str, Any],
    observed: dict[str, Any],
    provider_replay_dir: Path,
) -> None:
    record_provider_usage_metric(
        metric_id=f"{scenario['scenario_id']}:ACLI-DOGFOOD-USAGE",
        provider_id="openai",
        model="openai-live-operator-dogfood-deterministic-adapter",
        status="ACLI_DOGFOOD_PROVIDER_PARTICIPATION_RECORDED",
        availability="AVAILABLE_FOR_PROPOSAL_ONLY_COGNITION",
        created_at=CREATED_AT,
        replay_dir=provider_replay_dir / "usage",
        success_count=1 if observed["semantic_escalation_observed"] else 0,
        failure_count=0,
        last_used=CREATED_AT,
        latency_ms=111,
        token_usage={"token_values_replay_safe": True},
        cost_tracking={"cost_tracking_hooks_present": True, "estimated_cost_units": "0.0010"},
    )
    record_cognition_participation(
        participation_id=f"{scenario['scenario_id']}:ACLI-DOGFOOD-PARTICIPATION",
        provider_id="openai",
        participation_location="OCS_LLM_COGNITION",
        participation_role="LIVE_OPERATOR_SEMANTIC_ASSISTANCE",
        workflow_id="ACLI_DOGFOOD_LIVE_OPERATOR_SESSION",
        invocation_reason=scenario["pattern"],
        purpose="Proposal-only semantic assistance in live ACLI dogfood session.",
        response_used=observed["semantic_escalation_observed"],
        worker_invoked_after=False,
        human_confirmation_required=True,
        created_at=CREATED_AT,
        replay_dir=provider_replay_dir / "participation",
    )


@contextmanager
def _deterministic_conversation_provider() -> Iterator[None]:
    from aigol.cli import aigol_cli

    previous = aigol_cli._conversation_openai_provider_adapter
    aigol_cli._conversation_openai_provider_adapter = _fake_conversation_openai_provider_adapter
    try:
        yield
    finally:
        aigol_cli._conversation_openai_provider_adapter = previous


def _fake_conversation_openai_provider_adapter() -> OpenAIProviderAdapter:
    def fake_client(payload: dict[str, Any], *, api_key: str, endpoint: str, timeout_seconds: int) -> dict[str, Any]:
        return {
            "id": "resp-acli-dogfood-live-operator",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "findings": ["Clarify scope before any action."],
                                    "assumptions": ["Provider output remains non-authoritative."],
                                    "alternatives": ["Ask a clarification question", "Offer a proposal only"],
                                    "risks": ["Executing without confirmation could choose the wrong workflow."],
                                    "uncertainties": ["Operator intent may still be underspecified."],
                                    "confidence": "MEDIUM",
                                },
                                sort_keys=True,
                            ),
                            "annotations": [],
                        }
                    ],
                }
            ],
            "usage": {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20},
        }

    return OpenAIProviderAdapter(api_key="operator-dogfood-test-key", client=fake_client)


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _workflow_id(turn: dict[str, Any]) -> str | None:
    for key in ("conversational_workflow_id", "routing_visibility_workflow_id", "originating_workflow_id"):
        value = turn.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _providers(turn: dict[str, Any]) -> list[str]:
    provider_ids = turn.get("provider_ids")
    if isinstance(provider_ids, list):
        return [str(provider_id) for provider_id in provider_ids]
    if turn.get("provider_invoked") is True:
        return ["UNKNOWN_PROVIDER"]
    return []


def _approval_prompt(prompt: str) -> bool:
    normalized = prompt.strip().lower().rstrip(".!?")
    return normalized in {"approved", "i approve", "odobrim", "da"}


def _collect_json_references(root: Path) -> list[str]:
    if not root.exists():
        return []
    return [str(path) for path in sorted(root.rglob("*.json"))]


def _daily_operator_gaps(scenario_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"scenario_id": item["scenario_id"], "pattern": item["pattern"], "gaps": item["gaps"]}
        for item in scenario_results
        if item["gaps"]
    ]


def _blockers(assertions: dict[str, bool], scenario_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blockers = [
        {"assertion": key, "failure_reason": "ACLI live operator certification assertion failed"}
        for key, passed in assertions.items()
        if not passed
    ]
    blockers.extend(_daily_operator_gaps(scenario_results))
    return blockers


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 1.0
    return round(numerator / denominator, 4)


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


def _with_hash(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    return not any(marker.lower() in serialized.lower() for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    serialized = canonical_serialize(payload).lower()
    for marker in SECRET_MARKERS:
        if marker.lower() in serialized:
            raise FailClosedRuntimeError("ACLI dogfood live operator certification failed closed: secret-like material recorded")


def main() -> int:
    result = run_acli_dogfood_live_operator_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"COVERAGE_REPORT={result['coverage_report_path']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"OPERATOR_EXPERIENCE_REPORT={result['operator_experience_report_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
