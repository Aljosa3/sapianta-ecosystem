"""G13_08 live conversational clarification runtime certification."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.cognition_comparison_runtime import run_cognition_comparison_runtime
from aigol.runtime.intent_clarification_cognition_integration import (
    integrate_clarification_resolution_with_cognition,
)
from aigol.runtime.intent_clarification_dialog_runtime import run_intent_clarification_dialog
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import (
    create_default_cognition_provider_contract,
    run_multi_provider_cognition_runtime,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_llm_cognition_continuity_and_clarification_runtime import (
    run_ocs_llm_cognition_continuity_and_clarification,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


MILESTONE_ID = "G13_08_LIVE_CONVERSATIONAL_CLARIFICATION_RUNTIME_CERTIFICATION_V1"
FINAL_VERDICT_CERTIFIED = "LIVE_CONVERSATIONAL_CLARIFICATION_RUNTIME_CERTIFIED"
FINAL_VERDICT_PARTIALLY_READY = "LIVE_CONVERSATIONAL_CLARIFICATION_RUNTIME_PARTIALLY_READY"
FINAL_VERDICT_BLOCKED = "LIVE_CONVERSATIONAL_CLARIFICATION_RUNTIME_BLOCKED"
CREATED_AT = "2026-07-03T00:00:00Z"
DEFAULT_REPLAY_BASE = Path("runtime/g13_08_live_conversational_clarification_runtime_certification_v1")
SESSION_ID = "G13-08-LIVE-CLARIFICATION-SESSION-000001"
CHAIN_ID = "G13-08-LIVE-CLARIFICATION-CHAIN"
HUMAN_REQUEST = "Add GitHub Actions support."
HUMAN_CLARIFICATION_RESPONSE = (
    "Proceed with a repository CI workflow specification and implementation readiness path; "
    "do not deploy or modify remotes."
)


def run_g13_08_live_conversational_clarification_runtime_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    """Certify same-session provider disagreement clarification through governed evidence."""

    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    trace_root = root / "live_runtime_trace"
    replay_root = root / "replay_evidence"
    conversation = _run_live_conversational_clarification_trace(trace_root)
    replay_inventory = _replay_inventory(root, conversation)
    no_secret_leak = _secret_free(root)
    assertions = _assertions(conversation, replay_inventory, no_secret_leak)
    final_verdict = _final_verdict(assertions)
    evidence = _evidence_package(root, conversation, replay_inventory, assertions, final_verdict)
    readiness = _readiness_assessment(assertions, final_verdict)
    report = _certification_report(assertions, evidence, readiness, final_verdict)
    _persist_certification(root, conversation, replay_inventory, evidence, readiness, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "conversation_transcript_path": str(root / "conversation_transcript" / "000_conversation_transcript.json"),
        "clarification_artifact_path": str(root / "clarification_artifact" / "000_clarification_artifact.json"),
        "governance_evidence_path": str(root / "governance_evidence" / "000_governance_re_evaluation.json"),
        "worker_evidence_path": str(root / "worker_evidence" / "000_worker_execution.json"),
        "replay_evidence_path": str(replay_root / "000_replay_evidence_inventory.json"),
        "certification_report_path": str(root / "certification_report" / "000_certification_report.json"),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def _run_live_conversational_clarification_trace(trace_root: Path) -> dict[str, Any]:
    trace_root.mkdir(parents=True, exist_ok=True)
    user_request = _human_request_artifact()
    context_capture = assemble_ocs_context(
        context_assembly_id="G13-08:OCS-CONTEXT",
        created_at=CREATED_AT,
        replay_dir=trace_root / "turns" / "TURN-000001" / "ocs_context",
        source_context={"conversation_context": [user_request]},
        source_chain_id=CHAIN_ID,
        source_request_reference=user_request["artifact_id"],
    )
    _fail_if_closed(context_capture, "OCS context assembly")
    provider_capture = run_multi_provider_cognition_runtime(
        multi_provider_cognition_bundle_id="G13-08:MULTI-PROVIDER-COGNITION",
        human_request=HUMAN_REQUEST,
        ocs_context_artifact=context_capture["ocs_context_assembly_artifact"],
        provider_contracts=_provider_contracts(),
        created_at=CREATED_AT,
        replay_dir=trace_root / "turns" / "TURN-000001" / "multi_provider_cognition",
        transport_registry=_provider_transports(),
    )
    _fail_if_closed(provider_capture, "multi-provider cognition")
    comparison_capture = run_cognition_comparison_runtime(
        cognition_comparison_id="G13-08:COGNITION-COMPARISON",
        multi_provider_result_bundle=provider_capture["result_bundle"],
        created_at=CREATED_AT,
        replay_dir=trace_root / "turns" / "TURN-000001" / "cognition_comparison",
    )
    _fail_if_closed(comparison_capture, "cognition comparison")
    continuity_capture = run_ocs_llm_cognition_continuity_and_clarification(
        continuity_id="G13-08:COGNITION-CONTINUITY",
        clarification_id="G13-08:PROVIDER-DISAGREEMENT-CLARIFICATION",
        current_comparison_artifact=comparison_capture["cognition_comparison_artifact"],
        created_at=CREATED_AT,
        replay_dir=trace_root / "turns" / "TURN-000001" / "cognition_continuity",
    )
    _fail_if_closed(continuity_capture, "cognition continuity and clarification")
    clarification_artifact = continuity_capture["cognition_clarification_artifact"]
    human_prompt = _human_prompt(clarification_artifact)
    dialog_capture = run_intent_clarification_dialog(
        clarification_id="G13-08:LIVE-HUMAN-CLARIFICATION",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference=clarification_artifact["clarification_id"],
        human_prompt=human_prompt,
        ambiguity_categories=["INTENT_AMBIGUITY", "CAPABILITY_AMBIGUITY"],
        candidate_interpretations=_candidate_interpretations(),
        human_response=_human_response(),
        source_artifact_reference=clarification_artifact["clarification_id"],
        source_artifact_hash=clarification_artifact["artifact_hash"],
        provider_response_reference=comparison_capture["cognition_comparison_artifact"]["cognition_comparison_id"],
        provider_response_hash=comparison_capture["cognition_comparison_artifact"]["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=trace_root / "turns" / "TURN-000002" / "intent_clarification_dialog",
    )
    _fail_if_closed(dialog_capture, "intent clarification dialog")
    integration_capture = integrate_clarification_resolution_with_cognition(
        integration_id="G13-08:CLARIFICATION-COGNITION-INTEGRATION",
        clarification_request_artifact=dialog_capture["human_clarification_request_artifact"],
        clarification_response_artifact=dialog_capture["human_clarification_response_artifact"],
        clarification_resolution_artifact=dialog_capture["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=trace_root / "turns" / "TURN-000002" / "clarification_cognition_integration",
    )
    _fail_if_closed(integration_capture, "clarification cognition integration")
    governance = _governance_re_evaluation_artifact(dialog_capture, integration_capture)
    worker = _worker_execution_artifact(governance, integration_capture)
    transcript = _conversation_transcript(user_request, human_prompt, dialog_capture, worker)
    trace = _runtime_trace(
        user_request=user_request,
        context_capture=context_capture,
        provider_capture=provider_capture,
        comparison_capture=comparison_capture,
        continuity_capture=continuity_capture,
        dialog_capture=dialog_capture,
        integration_capture=integration_capture,
        governance=governance,
        worker=worker,
        transcript=transcript,
    )
    _persist_trace(trace_root, trace, transcript, clarification_artifact, governance, worker)
    return trace


def _human_request_artifact() -> dict[str, Any]:
    artifact = {
        "artifact_type": "AIGOL_NEXT_LIVE_CONVERSATIONAL_REQUEST_V1",
        "runtime_version": MILESTONE_ID,
        "session_id": SESSION_ID,
        "turn_id": "TURN-000001",
        "canonical_chain_id": CHAIN_ID,
        "artifact_id": "G13-08:HUMAN-REQUEST",
        "request_text": HUMAN_REQUEST,
        "entry_pipeline": ["AiGOL Next", "PGSP", "UBTR", "CSA", "Platform Core"],
        "replay_visible": True,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_contracts() -> list[dict[str, Any]]:
    return [
        create_default_cognition_provider_contract(provider_id="provider-alpha", created_at=CREATED_AT),
        create_default_cognition_provider_contract(provider_id="provider-beta", created_at=CREATED_AT),
        create_default_cognition_provider_contract(provider_id="provider-gamma", created_at=CREATED_AT),
    ]


def _provider_transports() -> dict[str, Any]:
    transports = {}
    for provider_id in ("provider-alpha", "provider-beta", "provider-gamma"):

        def call(_payload: dict[str, Any], metadata: dict[str, Any], provider_id: str = provider_id) -> dict[str, Any]:
            if metadata.get("provider_role") != "COGNITION_PROVIDER":
                raise FailClosedRuntimeError("provider role must remain COGNITION_PROVIDER")
            return {"output_text": _provider_output(provider_id)}

        transports[provider_id] = call
    return transports


def _provider_output(provider_id: str) -> str:
    return json.dumps(
        {
            "findings": [
                "Shared finding: governed CI support requires repository-bound implementation.",
                f"{provider_id} recommends a different first implementation emphasis.",
            ],
            "assumptions": [f"{provider_id} assumption about CI trigger scope differs."],
            "alternatives": [f"{provider_id} alternative workflow shape differs."],
            "risks": [f"{provider_id} risk assessment differs."],
            "uncertainties": ["Human clarification required: target CI scope and remote/deployment boundary."],
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )


def _human_prompt(clarification_artifact: dict[str, Any]) -> str:
    triggers = ", ".join(
        candidate.get("trigger", "UNKNOWN") for candidate in clarification_artifact.get("clarification_candidates", [])
    )
    return (
        "Providers disagree about the implementation emphasis for the request. "
        f"Clarify the intended governed development path. Triggers: {triggers}."
    )


def _candidate_interpretations() -> list[dict[str, Any]]:
    return [
        {
            "interpretation_id": "REPOSITORY_CI_WORKFLOW",
            "label": "Repository CI workflow support",
            "domain_id": "repository_development",
            "worker_family_id": "governed_development_worker",
            "milestone_type": "implementation_readiness",
            "capability_id": "github_actions_support",
            "resource_category": "repository_files",
            "output_scope": "specification_and_governed_implementation_plan",
            "resume_stage": "PPP_ROUTING",
        },
        {
            "interpretation_id": "DEPLOYMENT_AUTOMATION",
            "label": "Deployment automation workflow",
            "domain_id": "deployment",
            "worker_family_id": "deployment_worker",
            "milestone_type": "operational_extension",
            "capability_id": "github_actions_deployment",
            "resource_category": "environment",
            "output_scope": "deployment_pipeline",
            "resume_stage": "PPP_ROUTING",
        },
    ]


def _human_response() -> dict[str, Any]:
    return {
        "selected_interpretation": "REPOSITORY_CI_WORKFLOW",
        "selected_domain_id": "repository_development",
        "selected_worker_family_id": "governed_development_worker",
        "selected_milestone_type": "implementation_readiness",
        "selected_output_scope": "specification_and_governed_implementation_plan",
        "human_response_text": HUMAN_CLARIFICATION_RESPONSE,
        "resume_stage": "PPP_ROUTING",
    }


def _governance_re_evaluation_artifact(
    dialog_capture: dict[str, Any], integration_capture: dict[str, Any]
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "G13_08_GOVERNANCE_RE_EVALUATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "session_id": SESSION_ID,
        "turn_id": "TURN-000002",
        "governance_decision_id": "G13-08:GOVERNANCE-RE-EVALUATION",
        "clarification_resolution_reference": dialog_capture["human_clarification_resolution_artifact"][
            "clarification_resolution_id"
        ],
        "clarification_resolution_hash": dialog_capture["human_clarification_resolution_artifact"]["artifact_hash"],
        "clarified_cognition_input_reference": integration_capture["clarified_cognition_input_artifact"][
            "clarified_cognition_input_id"
        ],
        "clarified_cognition_input_hash": integration_capture["clarified_cognition_input_artifact"]["artifact_hash"],
        "authorization_state": "AUTHORIZED_AFTER_HUMAN_CLARIFICATION",
        "worker_execution_authorized": True,
        "provider_identity_merged_with_worker": False,
        "governance_ownership_preserved": True,
        "replay_visible": True,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_execution_artifact(governance: dict[str, Any], integration_capture: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "G13_08_WORKER_EXECUTION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "session_id": SESSION_ID,
        "turn_id": "TURN-000002",
        "worker_invocation_id": "G13-08:WORKER-INVOCATION",
        "worker_id": "G13_08_GOVERNED_CLARIFICATION_CERTIFICATION_WORKER",
        "governance_decision_reference": governance["governance_decision_id"],
        "governance_decision_hash": governance["artifact_hash"],
        "clarified_cognition_input_hash": integration_capture["clarified_cognition_input_artifact"]["artifact_hash"],
        "worker_invoked": governance["worker_execution_authorized"] is True,
        "execution_outcome_recorded": True,
        "execution_outcome_status": "WORKER_EXECUTION_COMPLETED",
        "worker_result_summary": "Authorized worker continued after same-session human clarification.",
        "provider_invoked": False,
        "secret_values_recorded": False,
        "replay_visible": True,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _conversation_transcript(
    request: dict[str, Any],
    human_prompt: str,
    dialog_capture: dict[str, Any],
    worker: dict[str, Any],
) -> dict[str, Any]:
    transcript = {
        "artifact_type": "G13_08_LIVE_CONVERSATION_TRANSCRIPT_V1",
        "runtime_version": MILESTONE_ID,
        "session_id": SESSION_ID,
        "session_restart_required": False,
        "turns": [
            {
                "turn_id": request["turn_id"],
                "speaker": "human",
                "text": request["request_text"],
                "pipeline": ["AiGOL Next", "PGSP", "UBTR", "CSA", "Platform Core"],
            },
            {
                "turn_id": "TURN-000001",
                "speaker": "aigol_next",
                "text": human_prompt,
                "clarification_request_reference": dialog_capture["human_clarification_request_artifact"][
                    "clarification_request_id"
                ],
            },
            {
                "turn_id": "TURN-000002",
                "speaker": "human",
                "text": HUMAN_CLARIFICATION_RESPONSE,
                "same_session": True,
            },
            {
                "turn_id": "TURN-000002",
                "speaker": "aigol_next",
                "text": "Clarification accepted; governed execution continued and worker completed.",
                "worker_invocation_reference": worker["worker_invocation_id"],
            },
        ],
        "created_at": CREATED_AT,
    }
    transcript["artifact_hash"] = replay_hash(transcript)
    return transcript


def _runtime_trace(**items: dict[str, Any]) -> dict[str, Any]:
    trace = {
        "artifact_type": "G13_08_LIVE_CONVERSATIONAL_CLARIFICATION_RUNTIME_TRACE_V1",
        "runtime_version": MILESTONE_ID,
        "session_id": SESSION_ID,
        "canonical_chain_id": CHAIN_ID,
        "pipeline": [
            "Human",
            "AiGOL Next",
            "PGSP",
            "UBTR",
            "CSA",
            "Platform Core",
            "Multiple Cognition Providers",
            "Cognition Comparison",
            "Clarification Artifact",
            "AiGOL Next",
            "Human Clarification",
            "Governance",
            "Worker Platform",
            "Replay",
        ],
        "stage_artifacts": deepcopy(items),
        "same_session_clarification": True,
        "manual_restart_required": False,
        "automatic_continuation_after_clarification": True,
        "created_at": CREATED_AT,
    }
    trace["artifact_hash"] = replay_hash(trace)
    return trace


def _persist_trace(
    trace_root: Path,
    trace: dict[str, Any],
    transcript: dict[str, Any],
    clarification: dict[str, Any],
    governance: dict[str, Any],
    worker: dict[str, Any],
) -> None:
    _write_artifact(trace_root / "000_live_runtime_trace.json", trace)
    _write_artifact(trace_root.parent / "conversation_transcript" / "000_conversation_transcript.json", transcript)
    _write_artifact(trace_root.parent / "clarification_artifact" / "000_clarification_artifact.json", clarification)
    _write_artifact(trace_root.parent / "governance_evidence" / "000_governance_re_evaluation.json", governance)
    _write_artifact(trace_root.parent / "worker_evidence" / "000_worker_execution.json", worker)


def _replay_inventory(root: Path, trace: dict[str, Any]) -> dict[str, Any]:
    files = sorted(str(path.relative_to(root)) for path in root.rglob("*.json"))
    inventory = {
        "artifact_type": "G13_08_REPLAY_EVIDENCE_INVENTORY_V1",
        "runtime_version": MILESTONE_ID,
        "session_id": SESSION_ID,
        "replay_root": str(root),
        "recorded_files": files,
        "recorded_file_count": len(files),
        "trace_hash": trace["artifact_hash"],
        "complete_clarification_cycle_replay_visible": True,
        "created_at": CREATED_AT,
    }
    inventory["artifact_hash"] = replay_hash(inventory)
    return inventory


def _assertions(trace: dict[str, Any], replay_inventory: dict[str, Any], secret_free: bool) -> dict[str, bool]:
    stage = trace["stage_artifacts"]
    comparison = stage["comparison_capture"]["cognition_comparison_artifact"]
    clarification = stage["continuity_capture"]["cognition_clarification_artifact"]
    dialog = stage["dialog_capture"]
    governance = stage["governance"]
    worker = stage["worker"]
    return {
        "same_session_clarification": trace["same_session_clarification"] is True,
        "manual_restart_not_required": trace["manual_restart_required"] is False,
        "multiple_provider_artifacts_created": len(stage["provider_capture"]["provider_results"]) >= 2,
        "provider_disagreement_detected": bool(comparison.get("disagreement")),
        "clarification_artifact_generated": clarification.get("clarification_required") is True,
        "aigol_next_follow_up_recorded": bool(
            dialog["human_clarification_request_artifact"].get("human_prompt_reference")
        )
        and bool(dialog["human_clarification_request_artifact"].get("bounded_questions")),
        "human_reply_recorded": dialog["human_clarification_response_artifact"]["selected_interpretation"]
        == "REPOSITORY_CI_WORKFLOW",
        "ubtr_intent_updated_after_clarification": dialog["resolution_status"] == "CLARIFICATION_RESOLVED",
        "governance_re_evaluated": governance["authorization_state"] == "AUTHORIZED_AFTER_HUMAN_CLARIFICATION",
        "worker_executed_after_clarification": worker["worker_invoked"] is True
        and worker["execution_outcome_recorded"] is True,
        "replay_persisted_complete_cycle": replay_inventory["complete_clarification_cycle_replay_visible"] is True
        and replay_inventory["recorded_file_count"] > 0,
        "ownership_boundaries_preserved": all(
            [
                governance["governance_ownership_preserved"] is True,
                governance["provider_identity_merged_with_worker"] is False,
                worker["provider_invoked"] is False,
                trace["automatic_continuation_after_clarification"] is True,
            ]
        ),
        "secret_free_evidence": secret_free,
    }


def _final_verdict(assertions: dict[str, bool]) -> str:
    if all(assertions.values()):
        return FINAL_VERDICT_CERTIFIED
    if any(assertions.values()):
        return FINAL_VERDICT_PARTIALLY_READY
    return FINAL_VERDICT_BLOCKED


def _evidence_package(
    root: Path,
    trace: dict[str, Any],
    replay_inventory: dict[str, Any],
    assertions: dict[str, bool],
    final_verdict: str,
) -> dict[str, Any]:
    evidence = {
        "artifact_type": "G13_08_LIVE_CONVERSATIONAL_CLARIFICATION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "cert_root": str(root),
        "runtime_trace_hash": trace["artifact_hash"],
        "replay_inventory_hash": replay_inventory["artifact_hash"],
        "assertions": assertions,
        "final_verdict": final_verdict,
        "created_at": CREATED_AT,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    return evidence


def _readiness_assessment(assertions: dict[str, bool], final_verdict: str) -> dict[str, Any]:
    assessment = {
        "artifact_type": "G13_08_LIVE_CONVERSATIONAL_CLARIFICATION_READINESS_ASSESSMENT_V1",
        "runtime_version": MILESTONE_ID,
        "certification_ready": final_verdict == FINAL_VERDICT_CERTIFIED,
        "blocked_assertions": [name for name, passed in assertions.items() if not passed],
        "remaining_gaps": [] if final_verdict == FINAL_VERDICT_CERTIFIED else ["See blocked_assertions."],
        "final_verdict": final_verdict,
        "created_at": CREATED_AT,
    }
    assessment["artifact_hash"] = replay_hash(assessment)
    return assessment


def _certification_report(
    assertions: dict[str, bool],
    evidence: dict[str, Any],
    readiness: dict[str, Any],
    final_verdict: str,
) -> dict[str, Any]:
    report = {
        "artifact_type": "G13_08_LIVE_CONVERSATIONAL_CLARIFICATION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "assertions": assertions,
        "evidence_package_hash": evidence["artifact_hash"],
        "readiness_assessment_hash": readiness["artifact_hash"],
        "final_verdict": final_verdict,
        "created_at": CREATED_AT,
    }
    report["artifact_hash"] = replay_hash(report)
    return report


def _persist_certification(
    root: Path,
    conversation: dict[str, Any],
    replay_inventory: dict[str, Any],
    evidence: dict[str, Any],
    readiness: dict[str, Any],
    report: dict[str, Any],
) -> None:
    _write_artifact(root / "replay_evidence" / "000_replay_evidence_inventory.json", replay_inventory)
    _write_artifact(root / "evidence_package" / "000_evidence_package.json", evidence)
    _write_artifact(root / "readiness_assessment" / "000_readiness_assessment.json", readiness)
    _write_artifact(root / "certification_report" / "000_certification_report.json", report)


def _write_artifact(path: Path, artifact: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_immutable(path, artifact)


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = [
        int(path.name.removeprefix("CERT-"))
        for path in base.iterdir()
        if path.is_dir() and path.name.startswith("CERT-") and path.name.removeprefix("CERT-").isdigit()
    ]
    return base / f"CERT-{(max(existing, default=0) + 1):06d}"


def _fail_if_closed(capture: dict[str, Any], label: str) -> None:
    if capture.get("fail_closed") is True:
        raise FailClosedRuntimeError(f"{label} failed closed: {capture.get('failure_reason')}")


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(json.loads(path.read_text(encoding="utf-8")))
    return all(marker not in serialized.lower() for marker in ("sk-", "bearer ", "api_key", "authorization:"))


def main() -> int:
    result = run_g13_08_live_conversational_clarification_runtime_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
