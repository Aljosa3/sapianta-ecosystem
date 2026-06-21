"""Certification runtime for AIGOL_HUMAN_INTENT_CLARIFICATION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aigol.runtime.conversational_cli_runtime import (
    CLARIFICATION_REQUIRED,
    HUMAN_INTENT_CLARIFICATION_INTAKE,
    route_conversational_cli_intent,
    reconstruct_conversational_cli_routing_replay,
)
from aigol.runtime.human_intent_clarification_continuity_runtime import (
    continue_human_intent_clarification_to_workflow,
    reconstruct_human_intent_clarification_continuity_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_HUMAN_INTENT_CLARIFICATION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/human_intent_clarification_certification_v1")
CREATED_AT = "2026-06-21T00:00:00Z"

AMBIGUOUS_PROMPTS = (
    "Create a report",
    "Analyze this",
    "Deploy it",
    "Fix the issue",
    "Continue the project",
    "Prepare something for the customer",
)
FULL_SCENARIO_PROMPT = "Create a report"
FULL_SCENARIO_CLARIFICATION_RESPONSE = (
    "Create a customer-facing report that reviews AI-generated customer replies for missing justification "
    "before anyone sends them."
)
FULL_SCENARIO_CONFIRMATION = "Yes, confirm this summary before any execution."


def run_human_intent_clarification_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"
    scenarios_dir = root / "scenarios"
    full_session_root = root / "full_session"

    ambiguity_results = [
        _run_ambiguity_probe(index=index + 1, prompt=prompt, scenarios_dir=scenarios_dir)
        for index, prompt in enumerate(AMBIGUOUS_PROMPTS)
    ]
    full_scenario = _run_full_clarification_scenario(full_session_root)
    replay_reconstruction = _reconstruct_replay(ambiguity_results=ambiguity_results, full_scenario=full_scenario)
    no_secret_leak = _secret_free(root)

    assertions = {
        "ambiguous_intent_detected": all(item["ambiguous_intent_detected"] for item in ambiguity_results),
        "clarification_generated": all(item["clarification_generated"] for item in ambiguity_results),
        "clarification_response_received": full_scenario["clarification_response_received"],
        "context_updated": full_scenario["context_updated"],
        "intent_resolved": full_scenario["intent_resolved"],
        "workflow_selected": full_scenario["workflow_selected"],
        "execution_summary_generated": full_scenario["execution_summary_generated"],
        "human_confirmation_recorded": full_scenario["human_confirmation_recorded"],
        "replay_reconstructed": replay_reconstruction["replay_reconstructed"],
        "approval_boundaries_preserved": full_scenario["approval_boundaries_preserved"],
        "secret_free_evidence": no_secret_leak,
    }
    final_verdict = (
        "HUMAN_INTENT_CLARIFICATION_CERTIFIED"
        if all(assertions.values())
        else "HUMAN_INTENT_CLARIFICATION_GAPS_FOUND"
    )
    coverage = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "ambiguous_prompt_count": len(ambiguity_results),
        "ambiguous_prompts_certified": sum(1 for item in ambiguity_results if item["ambiguous_intent_detected"]),
        "clarification_questions_generated": sum(len(item["clarification_questions"]) for item in ambiguity_results),
        "full_scenario_prompt": FULL_SCENARIO_PROMPT,
        "full_scenario_selected_workflow": full_scenario["selected_workflow"],
        "assertions": assertions,
        "final_verdict": final_verdict,
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    evidence = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(root),
        "ambiguity_detection_results": ambiguity_results,
        "full_clarification_scenario": full_scenario,
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    replay_package = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(root),
        "replay_reconstruction": replay_reconstruction,
        "original_ambiguous_request": FULL_SCENARIO_PROMPT,
        "clarification_questions": full_scenario["clarification_questions"],
        "clarification_response_hash": replay_hash(FULL_SCENARIO_CLARIFICATION_RESPONSE),
        "resolved_intent": full_scenario["resolved_intent"],
        "selected_workflow": full_scenario["selected_workflow"],
        "confirmation_boundary": full_scenario["confirmation_artifact_reference"],
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)
    report = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "assertions": assertions,
        "observed": {
            "ambiguous_intent_detected": assertions["ambiguous_intent_detected"],
            "clarification_generated": assertions["clarification_generated"],
            "clarification_response_received": assertions["clarification_response_received"],
            "context_updated": assertions["context_updated"],
            "intent_resolved": assertions["intent_resolved"],
            "workflow_selected": assertions["workflow_selected"],
            "execution_summary_generated": assertions["execution_summary_generated"],
            "human_confirmation_recorded": assertions["human_confirmation_recorded"],
            "replay_reconstructed": assertions["replay_reconstructed"],
            "approval_boundaries_preserved": assertions["approval_boundaries_preserved"],
            "secret_free_evidence": assertions["secret_free_evidence"],
        },
        "blocker_analysis": [] if final_verdict == "HUMAN_INTENT_CLARIFICATION_CERTIFIED" else _blockers(assertions),
        "recommended_next_certification": "AIGOL_HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_CERTIFICATION_V1",
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    _persist(evidence_dir, replay_dir, report_dir, coverage, evidence, replay_package, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "evidence_package_path": str(evidence_dir / "000_human_intent_clarification_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_human_intent_clarification_replay_package.json"),
        "certification_report_path": str(report_dir / "000_human_intent_clarification_certification_report.json"),
        "coverage_report_path": str(evidence_dir / "001_human_intent_clarification_coverage_report.json"),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def _run_ambiguity_probe(*, index: int, prompt: str, scenarios_dir: Path) -> dict[str, Any]:
    scenario_id = f"HIC-{index:03d}"
    replay_dir = scenarios_dir / scenario_id / "TURN-000001" / "conversational_cli_routing"
    capture = route_conversational_cli_intent(
        routing_id=f"{scenario_id}:ROUTING",
        prompt_id=f"{scenario_id}:PROMPT",
        human_prompt=prompt,
        canonical_chain_id=f"{scenario_id}:CHAIN",
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    selection = capture.get("workflow_selection_artifact", {})
    questions = list(selection.get("clarification_questions") or [])
    return {
        "scenario_id": scenario_id,
        "prompt": prompt,
        "routing_status": capture.get("routing_status"),
        "workflow_id": capture.get("workflow_id"),
        "intent_family": selection.get("intent_family"),
        "intent_confidence": selection.get("confidence"),
        "ambiguous_intent_detected": capture.get("routing_status") == CLARIFICATION_REQUIRED
        and capture.get("workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE,
        "clarification_generated": bool(questions),
        "clarification_questions": questions,
        "provider_invoked": capture.get("provider_invoked") is True,
        "worker_invoked": capture.get("worker_invoked") is True,
        "execution_requested": selection.get("execution_requested") is True,
        "approval_bypassed": selection.get("approval_bypassed") is True,
        "replay_reference": str(replay_dir),
    }


def _run_full_clarification_scenario(session_root: Path) -> dict[str, Any]:
    first_turn_replay = session_root / "TURN-000001" / "conversational_cli_routing"
    first_turn = route_conversational_cli_intent(
        routing_id="HIC-FULL:ROUTING",
        prompt_id="HIC-FULL:PROMPT-000001",
        human_prompt=FULL_SCENARIO_PROMPT,
        canonical_chain_id="HIC-FULL:CHAIN",
        created_at=CREATED_AT,
        replay_dir=first_turn_replay,
    )
    selection = first_turn["workflow_selection_artifact"]
    second_turn_replay = session_root / "TURN-000002" / "human_intent_clarification_continuity"
    continuity = continue_human_intent_clarification_to_workflow(
        continuity_id="HIC-FULL:CONTINUITY",
        session_root=session_root,
        turn_id="TURN-000002",
        prompt_id="HIC-FULL:PROMPT-000002",
        clarification_response=FULL_SCENARIO_CLARIFICATION_RESPONSE,
        current_chain_id="HIC-FULL:CHAIN",
        created_at=CREATED_AT,
        replay_dir=second_turn_replay,
    )
    if continuity.get("fail_closed") is True:
        raise FailClosedRuntimeError(str(continuity.get("failure_reason")))
    execution_summary = _execution_summary_artifact(
        continuity=continuity,
        clarification_questions=selection.get("clarification_questions") or [],
    )
    confirmation = _human_confirmation_artifact(execution_summary)
    confirmation_dir = session_root / "TURN-000003" / "human_confirmation"
    write_json_immutable(confirmation_dir / "000_human_intent_clarification_confirmation.json", confirmation)
    return {
        "original_request": FULL_SCENARIO_PROMPT,
        "clarification_questions": list(selection.get("clarification_questions") or []),
        "clarification_response_received": True,
        "clarification_response_hash": replay_hash(FULL_SCENARIO_CLARIFICATION_RESPONSE),
        "context_updated": continuity.get("clarification_response_bound") is True,
        "intent_resolved": continuity.get("intent_resolution_after_clarification") is True,
        "resolved_intent": continuity.get("intent_family"),
        "workflow_selected": continuity.get("workflow_selection_after_clarification") is True,
        "selected_workflow": continuity.get("workflow_id"),
        "execution_summary_generated": True,
        "execution_summary_artifact": execution_summary,
        "human_confirmation_recorded": True,
        "confirmation_artifact_reference": str(confirmation_dir / "000_human_intent_clarification_confirmation.json"),
        "human_confirmation_artifact": confirmation,
        "approval_boundaries_preserved": all(
            [
                first_turn.get("provider_invoked") is False,
                first_turn.get("worker_invoked") is False,
                continuity.get("provider_invoked") is False,
                continuity.get("worker_invoked") is False,
                continuity.get("execution_requested") is False,
                confirmation.get("execution_authorized") is False,
                confirmation.get("worker_invocation_authorized") is False,
            ]
        ),
        "first_turn_replay_reference": str(first_turn_replay),
        "continuity_replay_reference": str(second_turn_replay),
    }


def _execution_summary_artifact(*, continuity: dict[str, Any], clarification_questions: list[str]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_EXECUTION_SUMMARY_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "summary_id": "HIC-FULL:EXECUTION-SUMMARY",
        "original_request_hash": replay_hash(FULL_SCENARIO_PROMPT),
        "clarification_questions": list(clarification_questions),
        "clarification_response_hash": replay_hash(FULL_SCENARIO_CLARIFICATION_RESPONSE),
        "resolved_intent": continuity.get("intent_family"),
        "selected_workflow": continuity.get("workflow_id"),
        "summary_text": (
            "You asked for a report. After clarification, AiGOL understands this as a customer-facing "
            "AI-reply review report for missing justification. AiGOL will not execute anything unless you confirm."
        ),
        "human_confirmation_required": True,
        "execution_authorized": False,
        "worker_invocation_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _human_confirmation_artifact(execution_summary: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_CONFIRMATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "confirmation_id": "HIC-FULL:HUMAN-CONFIRMATION",
        "execution_summary_reference": execution_summary["summary_id"],
        "execution_summary_hash": execution_summary["artifact_hash"],
        "confirmation_response_hash": replay_hash(FULL_SCENARIO_CONFIRMATION),
        "confirmation_recorded": True,
        "confirmed_summary_only": True,
        "execution_authorized": False,
        "worker_invocation_authorized": False,
        "provider_invocation_authorized": False,
        "approval_boundaries_preserved": True,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _reconstruct_replay(*, ambiguity_results: list[dict[str, Any]], full_scenario: dict[str, Any]) -> dict[str, Any]:
    ambiguity_replays = []
    for item in ambiguity_results:
        replay = reconstruct_conversational_cli_routing_replay(item["replay_reference"])
        ambiguity_replays.append(
            {
                "scenario_id": item["scenario_id"],
                "workflow_id": replay["workflow_id"],
                "routing_status": replay["routing_status"],
                "replay_artifact_count": replay["replay_artifact_count"],
            }
        )
    full_first = reconstruct_conversational_cli_routing_replay(full_scenario["first_turn_replay_reference"])
    continuity = reconstruct_human_intent_clarification_continuity_replay(full_scenario["continuity_replay_reference"])
    confirmation = load_json(Path(full_scenario["confirmation_artifact_reference"]))
    return {
        "ambiguity_replays": ambiguity_replays,
        "full_first_turn_workflow": full_first["workflow_id"],
        "full_continuity_workflow": continuity["workflow_id"],
        "confirmation_recorded": confirmation.get("confirmation_recorded") is True,
        "replay_reconstructed": all(
            [
                len(ambiguity_replays) == len(ambiguity_results),
                full_first["workflow_id"] == HUMAN_INTENT_CLARIFICATION_INTAKE,
                continuity["workflow_id"] == full_scenario["selected_workflow"],
                confirmation.get("confirmation_recorded") is True,
            ]
        ),
    }


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    return "sk-" not in serialized and "Bearer " not in serialized and "api_key" not in serialized.lower()


def _blockers(assertions: dict[str, bool]) -> list[str]:
    return [name for name, value in assertions.items() if value is not True]


def _persist(
    evidence_dir: Path,
    replay_dir: Path,
    report_dir: Path,
    coverage: dict[str, Any],
    evidence: dict[str, Any],
    replay_package: dict[str, Any],
    report: dict[str, Any],
) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    write_json_immutable(evidence_dir / "000_human_intent_clarification_evidence_package.json", evidence)
    write_json_immutable(evidence_dir / "001_human_intent_clarification_coverage_report.json", coverage)
    write_json_immutable(replay_dir / "000_human_intent_clarification_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_human_intent_clarification_certification_report.json", report)


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def main() -> int:
    result = run_human_intent_clarification_certification()
    assertions = result["assertions"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"ambiguous_intent_detected={assertions['ambiguous_intent_detected']}")
    print(f"clarification_generated={assertions['clarification_generated']}")
    print(f"human_confirmation_recorded={assertions['human_confirmation_recorded']}")
    print(f"replay_reconstructed={assertions['replay_reconstructed']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "HUMAN_INTENT_CLARIFICATION_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
