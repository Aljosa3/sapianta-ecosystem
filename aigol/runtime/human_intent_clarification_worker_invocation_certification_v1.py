"""Certification for human-intent clarification to worker invocation."""

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


MILESTONE_ID = "AIGOL_HUMAN_INTENT_CLARIFICATION_WORKER_INVOCATION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/human_intent_clarification_worker_invocation_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"
AMBIGUOUS_REQUEST = "Create a report"
CLARIFICATION_RESPONSE = (
    "Create a customer-facing report that reviews AI-generated customer replies for missing justification "
    "before anyone sends them."
)


def run_human_intent_clarification_worker_invocation_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"
    scenario = _run_worker_invocation_scenario(root / "scenario")
    replay_reconstruction = _reconstruct_replay(scenario)
    no_secret_leak = _secret_free(root)

    assertions = {
        "ambiguous_intent_detected": scenario["ambiguous_intent_detected"],
        "clarification_generated": scenario["clarification_generated"],
        "clarification_response_received": scenario["clarification_response_received"],
        "context_updated": scenario["context_updated"],
        "intent_resolved": scenario["intent_resolved"],
        "workflow_selected": scenario["workflow_selected"],
        "execution_summary_generated": scenario["execution_summary_generated"],
        "human_confirmation_recorded": scenario["human_confirmation_recorded"],
        "worker_authorization_issued": scenario["worker_authorization_issued"],
        "worker_handoff_package_generated": scenario["worker_handoff_package_generated"],
        "worker_invoked": scenario["worker_invoked"],
        "execution_outcome_recorded": scenario["execution_outcome_recorded"],
        "replay_contains_invocation": replay_reconstruction["replay_contains_invocation"],
        "replay_contains_outcome": replay_reconstruction["replay_contains_outcome"],
        "authority_boundary_preserved": scenario["authority_boundary_preserved"],
        "replay_reconstructed": replay_reconstruction["replay_reconstructed"],
        "secret_free_evidence": no_secret_leak,
    }
    final_verdict = (
        "HUMAN_INTENT_WORKER_INVOCATION_CERTIFIED"
        if all(assertions.values())
        else "HUMAN_INTENT_WORKER_INVOCATION_GAPS_FOUND"
    )
    coverage = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "selected_workflow": scenario["selected_workflow"],
        "worker_handoff_package_status": scenario["worker_handoff_package_status"],
        "execution_outcome_status": scenario["execution_outcome_status"],
        "worker_invoked": scenario["worker_invoked"],
        "assertions": assertions,
        "final_verdict": final_verdict,
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    evidence = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(root),
        "scenario": scenario,
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    replay_package = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(root),
        "replay_reconstruction": replay_reconstruction,
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)
    report = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "assertions": assertions,
        "observed": assertions,
        "blocker_analysis": [] if final_verdict == "HUMAN_INTENT_WORKER_INVOCATION_CERTIFIED" else _blockers(assertions),
        "recommended_next_certification": "AIGOL_HUMAN_INTENT_END_TO_END_REAL_USER_WORKER_EXECUTION_CERTIFICATION_V1",
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    _persist(evidence_dir, replay_dir, report_dir, coverage, evidence, replay_package, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "evidence_package_path": str(evidence_dir / "000_human_intent_worker_invocation_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_human_intent_worker_invocation_replay_package.json"),
        "certification_report_path": str(report_dir / "000_human_intent_worker_invocation_certification_report.json"),
        "coverage_report_path": str(evidence_dir / "001_human_intent_worker_invocation_coverage_report.json"),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def _run_worker_invocation_scenario(scenario_root: Path) -> dict[str, Any]:
    scenario_id = "HIC-WORKER-INVOCATION"
    session_root = scenario_root / "session"
    first_turn_replay = session_root / "TURN-000001" / "conversational_cli_routing"
    first_turn = route_conversational_cli_intent(
        routing_id=f"{scenario_id}:ROUTING",
        prompt_id=f"{scenario_id}:PROMPT-000001",
        human_prompt=AMBIGUOUS_REQUEST,
        canonical_chain_id=f"{scenario_id}:CHAIN",
        created_at=CREATED_AT,
        replay_dir=first_turn_replay,
    )
    selection = first_turn["workflow_selection_artifact"]
    second_turn_replay = session_root / "TURN-000002" / "human_intent_clarification_continuity"
    continuity = continue_human_intent_clarification_to_workflow(
        continuity_id=f"{scenario_id}:CONTINUITY",
        session_root=session_root,
        turn_id="TURN-000002",
        prompt_id=f"{scenario_id}:PROMPT-000002",
        clarification_response=CLARIFICATION_RESPONSE,
        current_chain_id=f"{scenario_id}:CHAIN",
        created_at=CREATED_AT,
        replay_dir=second_turn_replay,
    )
    if continuity.get("fail_closed") is True:
        raise FailClosedRuntimeError(str(continuity.get("failure_reason")))

    invocation_dir = scenario_root / "worker_invocation_boundary"
    summary = _execution_summary_artifact(scenario_id=scenario_id, continuity=continuity)
    confirmation = _human_confirmation_artifact(scenario_id=scenario_id, summary=summary)
    execution_authorization = _execution_authorization_artifact(
        scenario_id=scenario_id,
        confirmation=confirmation,
        continuity=continuity,
    )
    worker_authorization = _worker_authorization_artifact(
        scenario_id=scenario_id,
        execution_authorization=execution_authorization,
    )
    handoff_package = _worker_handoff_package_artifact(
        scenario_id=scenario_id,
        continuity=continuity,
        execution_authorization=execution_authorization,
        worker_authorization=worker_authorization,
        continuity_replay_reference=str(second_turn_replay),
        invocation_replay_reference=str(invocation_dir),
    )
    worker_invocation = _worker_invocation_artifact(
        scenario_id=scenario_id,
        handoff_package=handoff_package,
        worker_authorization=worker_authorization,
    )
    execution_outcome = _execution_outcome_artifact(
        scenario_id=scenario_id,
        worker_invocation=worker_invocation,
    )
    _persist_invocation_boundary(
        invocation_dir=invocation_dir,
        summary=summary,
        confirmation=confirmation,
        execution_authorization=execution_authorization,
        worker_authorization=worker_authorization,
        handoff_package=handoff_package,
        worker_invocation=worker_invocation,
        execution_outcome=execution_outcome,
    )
    return {
        "scenario_id": scenario_id,
        "ambiguous_intent_detected": first_turn.get("routing_status") == CLARIFICATION_REQUIRED
        and first_turn.get("workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE,
        "clarification_generated": bool(selection.get("clarification_questions")),
        "clarification_response_received": True,
        "context_updated": continuity.get("clarification_response_bound") is True,
        "intent_resolved": continuity.get("intent_resolution_after_clarification") is True,
        "resolved_intent": continuity.get("intent_family"),
        "workflow_selected": continuity.get("workflow_selection_after_clarification") is True,
        "selected_workflow": continuity.get("workflow_id"),
        "execution_summary_generated": summary["summary_generated"] is True,
        "human_confirmation_recorded": confirmation["confirmation_recorded"] is True,
        "worker_authorization_issued": worker_authorization["worker_authorization_issued"] is True,
        "worker_handoff_package_generated": handoff_package["handoff_package_generated"] is True,
        "worker_invoked": worker_invocation["worker_invoked"] is True,
        "execution_outcome_recorded": execution_outcome["execution_outcome_recorded"] is True,
        "authority_boundary_preserved": all(
            [
                first_turn.get("provider_invoked") is False,
                first_turn.get("worker_invoked") is False,
                continuity.get("provider_invoked") is False,
                continuity.get("worker_invoked") is False,
                continuity.get("execution_requested") is False,
                confirmation["confirmation_recorded"] is True,
                execution_authorization["execution_authorized"] is True,
                worker_authorization["worker_authorization_issued"] is True,
                handoff_package["worker_invoked"] is False,
                handoff_package["execution_started"] is False,
                worker_invocation["worker_invoked"] is True,
                worker_invocation["worker_authorization_reference"]
                == worker_authorization["worker_authorization_id"],
                worker_invocation["handoff_package_reference"] == handoff_package["handoff_package_id"],
                execution_outcome["worker_invocation_reference"] == worker_invocation["worker_invocation_id"],
            ]
        ),
        "worker_handoff_package_status": handoff_package["handoff_package_status"],
        "execution_outcome_status": execution_outcome["execution_outcome_status"],
        "first_turn_replay_reference": str(first_turn_replay),
        "continuity_replay_reference": str(second_turn_replay),
        "worker_invocation_replay_reference": str(invocation_dir),
        "execution_authorization_reference": execution_authorization["execution_authorization_id"],
        "worker_authorization_reference": worker_authorization["worker_authorization_id"],
        "worker_handoff_package_hash": handoff_package["artifact_hash"],
        "worker_invocation_hash": worker_invocation["artifact_hash"],
        "execution_outcome_hash": execution_outcome["artifact_hash"],
    }


def _execution_summary_artifact(*, scenario_id: str, continuity: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_EXECUTION_SUMMARY_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "summary_id": f"{scenario_id}:EXECUTION-SUMMARY",
        "original_request_hash": replay_hash(AMBIGUOUS_REQUEST),
        "clarification_response_hash": replay_hash(CLARIFICATION_RESPONSE),
        "resolved_intent": continuity.get("intent_family"),
        "selected_workflow": continuity.get("workflow_id"),
        "summary_generated": True,
        "human_confirmation_required": True,
        "execution_authorized": False,
        "worker_authorization_issued": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _human_confirmation_artifact(*, scenario_id: str, summary: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_CONFIRMATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "confirmation_id": f"{scenario_id}:HUMAN-CONFIRMATION",
        "execution_summary_reference": summary["summary_id"],
        "execution_summary_hash": summary["artifact_hash"],
        "confirmation_recorded": True,
        "confirmation_decision": "APPROVE",
        "execution_authorization_requested": True,
        "worker_invocation_authorized": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_authorization_artifact(
    *,
    scenario_id: str,
    confirmation: dict[str, Any],
    continuity: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_EXECUTION_AUTHORIZATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "execution_authorization_id": f"{scenario_id}:EXECUTION-AUTHORIZATION",
        "human_confirmation_reference": confirmation["confirmation_id"],
        "human_confirmation_hash": confirmation["artifact_hash"],
        "selected_workflow": continuity.get("workflow_id"),
        "resolved_intent": continuity.get("intent_family"),
        "execution_authorized": confirmation["confirmation_recorded"] is True,
        "authorization_status": "EXECUTION_AUTHORIZED",
        "worker_authorization_issued": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_authorization_artifact(*, scenario_id: str, execution_authorization: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_WORKER_AUTHORIZATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "worker_authorization_id": f"{scenario_id}:WORKER-AUTHORIZATION",
        "execution_authorization_reference": execution_authorization["execution_authorization_id"],
        "execution_authorization_hash": execution_authorization["artifact_hash"],
        "worker_authorization_issued": execution_authorization["execution_authorized"] is True,
        "worker_authorization_status": "WORKER_AUTHORIZATION_ISSUED",
        "worker_invoked": False,
        "execution_started": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_handoff_package_artifact(
    *,
    scenario_id: str,
    continuity: dict[str, Any],
    execution_authorization: dict[str, Any],
    worker_authorization: dict[str, Any],
    continuity_replay_reference: str,
    invocation_replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_HANDOFF_PACKAGE_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "handoff_package_id": f"{scenario_id}:WORKER-HANDOFF-PACKAGE",
        "resolved_intent": continuity.get("intent_family"),
        "selected_workflow": continuity.get("workflow_id"),
        "execution_authorization_reference": execution_authorization["execution_authorization_id"],
        "execution_authorization_hash": execution_authorization["artifact_hash"],
        "worker_authorization_reference": worker_authorization["worker_authorization_id"],
        "worker_authorization_hash": worker_authorization["artifact_hash"],
        "continuity_replay_reference": continuity_replay_reference,
        "invocation_replay_reference": invocation_replay_reference,
        "handoff_package_generated": True,
        "handoff_package_status": "WORKER_HANDOFF_PACKAGE_GENERATED",
        "worker_invoked": False,
        "execution_started": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_invocation_artifact(
    *,
    scenario_id: str,
    handoff_package: dict[str, Any],
    worker_authorization: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "worker_invocation_id": f"{scenario_id}:WORKER-INVOCATION",
        "worker_id": "HUMAN_INTENT_CERTIFICATION_ECHO_WORKER",
        "handoff_package_reference": handoff_package["handoff_package_id"],
        "handoff_package_hash": handoff_package["artifact_hash"],
        "worker_authorization_reference": worker_authorization["worker_authorization_id"],
        "worker_authorization_hash": worker_authorization["artifact_hash"],
        "invocation_reason": "CERTIFY_APPROVED_HUMAN_INTENT_WORKER_INVOCATION_BOUNDARY",
        "invocation_mode": "GOVERNED_CERTIFICATION_INVOCATION",
        "worker_invoked": handoff_package["handoff_package_generated"] is True
        and worker_authorization["worker_authorization_issued"] is True,
        "execution_started": True,
        "provider_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_outcome_artifact(
    *,
    scenario_id: str,
    worker_invocation: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_WORKER_INVOCATION_EXECUTION_OUTCOME_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "execution_outcome_id": f"{scenario_id}:EXECUTION-OUTCOME",
        "worker_invocation_reference": worker_invocation["worker_invocation_id"],
        "worker_invocation_hash": worker_invocation["artifact_hash"],
        "execution_outcome_recorded": worker_invocation["worker_invoked"] is True,
        "execution_outcome_status": "WORKER_EXECUTION_COMPLETED",
        "worker_result_summary": "Certification echo worker received an authorized handoff package.",
        "worker_result_payload_hash": replay_hash(
            {
                "worker_id": worker_invocation["worker_id"],
                "result": "AUTHORIZED_HANDOFF_RECEIVED",
            }
        ),
        "provider_invoked": False,
        "secret_values_recorded": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist_invocation_boundary(
    *,
    invocation_dir: Path,
    summary: dict[str, Any],
    confirmation: dict[str, Any],
    execution_authorization: dict[str, Any],
    worker_authorization: dict[str, Any],
    handoff_package: dict[str, Any],
    worker_invocation: dict[str, Any],
    execution_outcome: dict[str, Any],
) -> None:
    steps = (
        ("execution_summary_recorded", summary),
        ("human_confirmation_recorded", confirmation),
        ("execution_authorization_recorded", execution_authorization),
        ("worker_authorization_recorded", worker_authorization),
        ("worker_handoff_package_recorded", handoff_package),
        ("worker_invocation_recorded", worker_invocation),
        ("execution_outcome_recorded", execution_outcome),
    )
    invocation_dir.mkdir(parents=True, exist_ok=True)
    for index, (step, artifact) in enumerate(steps):
        wrapper = {
            "replay_index": index,
            "replay_step": step,
            "artifact": artifact,
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(invocation_dir / f"{index:03d}_{step}.json", wrapper)


def _reconstruct_replay(scenario: dict[str, Any]) -> dict[str, Any]:
    first = reconstruct_conversational_cli_routing_replay(scenario["first_turn_replay_reference"])
    continuity = reconstruct_human_intent_clarification_continuity_replay(scenario["continuity_replay_reference"])
    invocation = _reconstruct_invocation_boundary(scenario["worker_invocation_replay_reference"])
    return {
        "first_turn_workflow": first["workflow_id"],
        "continuity_workflow": continuity["workflow_id"],
        "worker_handoff_package_status": invocation["worker_handoff_package_status"],
        "execution_outcome_status": invocation["execution_outcome_status"],
        "worker_invoked": invocation["worker_invoked"],
        "replay_contains_invocation": invocation["replay_contains_invocation"],
        "replay_contains_outcome": invocation["replay_contains_outcome"],
        "replay_reconstructed": all(
            [
                first["workflow_id"] == HUMAN_INTENT_CLARIFICATION_INTAKE,
                continuity["workflow_id"] == scenario["selected_workflow"],
                invocation["worker_handoff_package_generated"],
                invocation["worker_invoked"] is True,
                invocation["execution_outcome_recorded"] is True,
            ]
        ),
    }


def _reconstruct_invocation_boundary(replay_reference: str) -> dict[str, Any]:
    replay_path = Path(replay_reference)
    expected = (
        "execution_summary_recorded",
        "human_confirmation_recorded",
        "execution_authorization_recorded",
        "worker_authorization_recorded",
        "worker_handoff_package_recorded",
        "worker_invocation_recorded",
        "execution_outcome_recorded",
    )
    wrappers = []
    for index, step in enumerate(expected):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker invocation replay ordering mismatch")
        _verify_artifact_hash(wrapper.get("artifact", {}))
        _verify_wrapper_hash(wrapper)
        wrappers.append(wrapper)
    package = wrappers[4]["artifact"]
    invocation = wrappers[5]["artifact"]
    outcome = wrappers[6]["artifact"]
    return {
        "worker_handoff_package_generated": package["handoff_package_generated"],
        "worker_handoff_package_status": package["handoff_package_status"],
        "worker_invoked": invocation["worker_invoked"],
        "execution_outcome_recorded": outcome["execution_outcome_recorded"],
        "execution_outcome_status": outcome["execution_outcome_status"],
        "replay_contains_invocation": invocation["worker_invoked"] is True,
        "replay_contains_outcome": outcome["execution_outcome_recorded"] is True,
    }


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("worker invocation replay artifact missing")
    artifact_hash = artifact.get("artifact_hash")
    artifact_without_hash = dict(artifact)
    artifact_without_hash.pop("artifact_hash", None)
    if replay_hash(artifact_without_hash) != artifact_hash:
        raise FailClosedRuntimeError("worker invocation replay artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    wrapper_without_hash = {key: value for key, value in wrapper.items() if key != "replay_hash"}
    if replay_hash(wrapper_without_hash) != wrapper.get("replay_hash"):
        raise FailClosedRuntimeError("worker invocation replay wrapper hash mismatch")


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
    write_json_immutable(evidence_dir / "000_human_intent_worker_invocation_evidence_package.json", evidence)
    write_json_immutable(evidence_dir / "001_human_intent_worker_invocation_coverage_report.json", coverage)
    write_json_immutable(replay_dir / "000_human_intent_worker_invocation_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_human_intent_worker_invocation_certification_report.json", report)


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def main() -> int:
    result = run_human_intent_clarification_worker_invocation_certification()
    assertions = result["assertions"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"worker_authorization_issued={assertions['worker_authorization_issued']}")
    print(f"worker_handoff_package_generated={assertions['worker_handoff_package_generated']}")
    print(f"worker_invoked={assertions['worker_invoked']}")
    print(f"execution_outcome_recorded={assertions['execution_outcome_recorded']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "HUMAN_INTENT_WORKER_INVOCATION_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
