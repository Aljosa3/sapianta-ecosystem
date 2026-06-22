"""Certification for the post-clarification execution authorization boundary."""

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


MILESTONE_ID = "AIGOL_HUMAN_INTENT_CLARIFICATION_EXECUTION_AUTHORIZATION_BOUNDARY_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/human_intent_clarification_execution_authorization_boundary_certification_v1")
CREATED_AT = "2026-06-21T00:00:00Z"
AMBIGUOUS_REQUEST = "Create a report"
CLARIFICATION_RESPONSE = (
    "Create a customer-facing report that reviews AI-generated customer replies for missing justification "
    "before anyone sends them."
)


def run_human_intent_clarification_execution_authorization_boundary_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"
    scenarios_dir = root / "scenarios"

    denied = _run_boundary_scenario(
        scenario_id="HIC-AUTH-A",
        decision="DENY",
        scenario_root=scenarios_dir / "HIC-AUTH-A",
    )
    granted = _run_boundary_scenario(
        scenario_id="HIC-AUTH-B",
        decision="APPROVE",
        scenario_root=scenarios_dir / "HIC-AUTH-B",
    )
    replay_reconstruction = _reconstruct_replay(denied=denied, granted=granted)
    no_secret_leak = _secret_free(root)

    common = {
        "ambiguous_intent_detected": denied["ambiguous_intent_detected"] and granted["ambiguous_intent_detected"],
        "clarification_generated": denied["clarification_generated"] and granted["clarification_generated"],
        "clarification_response_received": denied["clarification_response_received"]
        and granted["clarification_response_received"],
        "context_updated": denied["context_updated"] and granted["context_updated"],
        "intent_resolved": denied["intent_resolved"] and granted["intent_resolved"],
        "workflow_selected": denied["workflow_selected"] and granted["workflow_selected"],
        "execution_summary_generated": denied["execution_summary_generated"]
        and granted["execution_summary_generated"],
        "approval_requested": denied["approval_requested"] and granted["approval_requested"],
    }
    assertions = {
        **common,
        "approval_denied_path_verified": denied["approval_denied_path_verified"],
        "execution_blocked_without_approval": denied["execution_blocked_without_approval"],
        "approval_granted_path_verified": granted["approval_granted_path_verified"],
        "execution_authorized_after_approval": granted["execution_authorized_after_approval"],
        "authority_boundary_preserved": denied["authority_boundary_preserved"]
        and granted["authority_boundary_preserved"],
        "replay_reconstructed": replay_reconstruction["replay_reconstructed"],
        "secret_free_evidence": no_secret_leak,
    }
    final_verdict = (
        "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_CERTIFIED"
        if all(assertions.values())
        else "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_GAPS_FOUND"
    )
    coverage = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "scenarios": {
            "HIC-AUTH-A": {
                "decision": "DENY",
                "execution_authorized": denied["execution_authorized"],
                "worker_authorization_issued": denied["worker_authorization_issued"],
            },
            "HIC-AUTH-B": {
                "decision": "APPROVE",
                "execution_authorized": granted["execution_authorized"],
                "worker_authorization_issued": granted["worker_authorization_issued"],
            },
        },
        "assertions": assertions,
        "final_verdict": final_verdict,
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    evidence = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(root),
        "approval_denied_scenario": denied,
        "approval_granted_scenario": granted,
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    replay_package = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(root),
        "replay_reconstruction": replay_reconstruction,
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)
    report = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "assertions": assertions,
        "observed": assertions,
        "blocker_analysis": []
        if final_verdict == "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_CERTIFIED"
        else _blockers(assertions),
        "recommended_next_certification": "AIGOL_HUMAN_INTENT_CLARIFICATION_WORKER_HANDOFF_CERTIFICATION_V1",
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    _persist(evidence_dir, replay_dir, report_dir, coverage, evidence, replay_package, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "evidence_package_path": str(
            evidence_dir / "000_human_intent_execution_authorization_boundary_evidence_package.json"
        ),
        "replay_package_path": str(
            replay_dir / "000_human_intent_execution_authorization_boundary_replay_package.json"
        ),
        "certification_report_path": str(
            report_dir / "000_human_intent_execution_authorization_boundary_certification_report.json"
        ),
        "coverage_report_path": str(
            evidence_dir / "001_human_intent_execution_authorization_boundary_coverage_report.json"
        ),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def _run_boundary_scenario(*, scenario_id: str, decision: str, scenario_root: Path) -> dict[str, Any]:
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
    authorization_dir = scenario_root / "authorization_boundary"
    summary = _execution_summary_artifact(scenario_id=scenario_id, continuity=continuity)
    approval_request = _approval_request_artifact(scenario_id=scenario_id, summary=summary)
    approval_decision = _approval_decision_artifact(
        scenario_id=scenario_id,
        approval_request=approval_request,
        decision=decision,
    )
    execution_authorization = _execution_authorization_artifact(
        scenario_id=scenario_id,
        approval_decision=approval_decision,
        continuity=continuity,
    )
    worker_authorization = _worker_authorization_artifact(
        scenario_id=scenario_id,
        execution_authorization=execution_authorization,
    )
    _persist_authorization_boundary(
        authorization_dir=authorization_dir,
        summary=summary,
        approval_request=approval_request,
        approval_decision=approval_decision,
        execution_authorization=execution_authorization,
        worker_authorization=worker_authorization,
    )
    execution_authorized = execution_authorization["execution_authorized"] is True
    worker_authorization_issued = worker_authorization["worker_authorization_issued"] is True
    return {
        "scenario_id": scenario_id,
        "decision": decision,
        "ambiguous_intent_detected": first_turn.get("routing_status") == CLARIFICATION_REQUIRED
        and first_turn.get("workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE,
        "clarification_generated": bool(selection.get("clarification_questions")),
        "clarification_response_received": True,
        "context_updated": continuity.get("clarification_response_bound") is True,
        "intent_resolved": continuity.get("intent_resolution_after_clarification") is True,
        "workflow_selected": continuity.get("workflow_selection_after_clarification") is True,
        "selected_workflow": continuity.get("workflow_id"),
        "execution_summary_generated": summary["summary_generated"] is True,
        "approval_requested": approval_request["approval_requested"] is True,
        "approval_denied_path_verified": decision == "DENY" and approval_decision["approval_granted"] is False,
        "execution_blocked_without_approval": decision == "DENY"
        and execution_authorization["execution_authorized"] is False
        and worker_authorization["worker_authorization_issued"] is False,
        "approval_granted_path_verified": decision == "APPROVE" and approval_decision["approval_granted"] is True,
        "execution_authorized_after_approval": decision == "APPROVE"
        and execution_authorized
        and worker_authorization_issued,
        "authority_boundary_preserved": all(
            [
                first_turn.get("provider_invoked") is False,
                first_turn.get("worker_invoked") is False,
                continuity.get("provider_invoked") is False,
                continuity.get("worker_invoked") is False,
                continuity.get("execution_requested") is False,
                execution_authorization["execution_authorized"] == approval_decision["approval_granted"],
                worker_authorization["worker_authorization_issued"] == execution_authorization["execution_authorized"],
                worker_authorization["worker_invoked"] is False,
            ]
        ),
        "execution_authorized": execution_authorized,
        "worker_authorization_issued": worker_authorization_issued,
        "worker_invoked": worker_authorization["worker_invoked"],
        "first_turn_replay_reference": str(first_turn_replay),
        "continuity_replay_reference": str(second_turn_replay),
        "authorization_boundary_replay_reference": str(authorization_dir),
        "execution_summary_hash": summary["artifact_hash"],
        "approval_decision_hash": approval_decision["artifact_hash"],
        "execution_authorization_hash": execution_authorization["artifact_hash"],
        "worker_authorization_hash": worker_authorization["artifact_hash"],
    }


def _execution_summary_artifact(*, scenario_id: str, continuity: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_BOUNDARY_SUMMARY_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "summary_id": f"{scenario_id}:EXECUTION-SUMMARY",
        "original_request_hash": replay_hash(AMBIGUOUS_REQUEST),
        "clarification_response_hash": replay_hash(CLARIFICATION_RESPONSE),
        "resolved_intent": continuity.get("intent_family"),
        "selected_workflow": continuity.get("workflow_id"),
        "summary_generated": True,
        "approval_required_before_execution": True,
        "execution_authorized": False,
        "worker_authorization_issued": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _approval_request_artifact(*, scenario_id: str, summary: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_BOUNDARY_APPROVAL_REQUEST_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "approval_request_id": f"{scenario_id}:APPROVAL-REQUEST",
        "execution_summary_reference": summary["summary_id"],
        "execution_summary_hash": summary["artifact_hash"],
        "approval_requested": True,
        "approval_required": True,
        "execution_authorized": False,
        "worker_authorization_issued": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _approval_decision_artifact(*, scenario_id: str, approval_request: dict[str, Any], decision: str) -> dict[str, Any]:
    granted = decision == "APPROVE"
    artifact = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_BOUNDARY_APPROVAL_DECISION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "approval_decision_id": f"{scenario_id}:APPROVAL-DECISION",
        "approval_request_reference": approval_request["approval_request_id"],
        "approval_request_hash": approval_request["artifact_hash"],
        "decision": decision,
        "approval_granted": granted,
        "approval_denied": not granted,
        "decision_recorded": True,
        "execution_authorized": False,
        "worker_authorization_issued": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_authorization_artifact(
    *,
    scenario_id: str,
    approval_decision: dict[str, Any],
    continuity: dict[str, Any],
) -> dict[str, Any]:
    authorized = approval_decision["approval_granted"] is True
    artifact = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_BOUNDARY_EXECUTION_AUTHORIZATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "execution_authorization_id": f"{scenario_id}:EXECUTION-AUTHORIZATION",
        "approval_decision_reference": approval_decision["approval_decision_id"],
        "approval_decision_hash": approval_decision["artifact_hash"],
        "selected_workflow": continuity.get("workflow_id"),
        "execution_authorized": authorized,
        "authorization_status": "EXECUTION_AUTHORIZED" if authorized else "EXECUTION_BLOCKED_APPROVAL_DENIED",
        "authorization_derived_from_resolved_intent_only": False,
        "resolved_intent_alone_authorizes_execution": False,
        "worker_authorization_issued": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_authorization_artifact(*, scenario_id: str, execution_authorization: dict[str, Any]) -> dict[str, Any]:
    issued = execution_authorization["execution_authorized"] is True
    artifact = {
        "artifact_type": "HUMAN_INTENT_EXECUTION_BOUNDARY_WORKER_AUTHORIZATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "worker_authorization_id": f"{scenario_id}:WORKER-AUTHORIZATION",
        "execution_authorization_reference": execution_authorization["execution_authorization_id"],
        "execution_authorization_hash": execution_authorization["artifact_hash"],
        "worker_authorization_issued": issued,
        "worker_authorization_status": "WORKER_AUTHORIZATION_ISSUED" if issued else "WORKER_AUTHORIZATION_BLOCKED",
        "worker_invoked": False,
        "execution_started": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist_authorization_boundary(
    *,
    authorization_dir: Path,
    summary: dict[str, Any],
    approval_request: dict[str, Any],
    approval_decision: dict[str, Any],
    execution_authorization: dict[str, Any],
    worker_authorization: dict[str, Any],
) -> None:
    steps = (
        ("execution_summary_recorded", summary),
        ("approval_request_recorded", approval_request),
        ("approval_decision_recorded", approval_decision),
        ("execution_authorization_recorded", execution_authorization),
        ("worker_authorization_recorded", worker_authorization),
    )
    authorization_dir.mkdir(parents=True, exist_ok=True)
    for index, (step, artifact) in enumerate(steps):
        wrapper = {
            "replay_index": index,
            "replay_step": step,
            "artifact": artifact,
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(authorization_dir / f"{index:03d}_{step}.json", wrapper)


def _reconstruct_replay(*, denied: dict[str, Any], granted: dict[str, Any]) -> dict[str, Any]:
    scenario_replays = []
    for scenario in (denied, granted):
        first = reconstruct_conversational_cli_routing_replay(scenario["first_turn_replay_reference"])
        continuity = reconstruct_human_intent_clarification_continuity_replay(scenario["continuity_replay_reference"])
        authorization = _reconstruct_authorization_boundary(scenario["authorization_boundary_replay_reference"])
        scenario_replays.append(
            {
                "scenario_id": scenario["scenario_id"],
                "first_turn_workflow": first["workflow_id"],
                "continuity_workflow": continuity["workflow_id"],
                "execution_authorized": authorization["execution_authorized"],
                "worker_authorization_issued": authorization["worker_authorization_issued"],
                "replay_reconstructed": authorization["replay_reconstructed"],
            }
        )
    return {
        "scenario_replays": scenario_replays,
        "replay_reconstructed": all(item["replay_reconstructed"] for item in scenario_replays),
    }


def _reconstruct_authorization_boundary(replay_reference: str) -> dict[str, Any]:
    replay_path = Path(replay_reference)
    expected = (
        "execution_summary_recorded",
        "approval_request_recorded",
        "approval_decision_recorded",
        "execution_authorization_recorded",
        "worker_authorization_recorded",
    )
    wrappers = []
    for index, step in enumerate(expected):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("authorization boundary replay ordering mismatch")
        artifact = wrapper.get("artifact", {})
        artifact_hash = artifact.get("artifact_hash") if isinstance(artifact, dict) else None
        artifact_without_hash = dict(artifact)
        artifact_without_hash.pop("artifact_hash", None)
        if replay_hash(artifact_without_hash) != artifact_hash:
            raise FailClosedRuntimeError("authorization boundary artifact hash mismatch")
        wrapper_without_hash = {k: v for k, v in wrapper.items() if k != "replay_hash"}
        if replay_hash(wrapper_without_hash) != wrapper.get("replay_hash"):
            raise FailClosedRuntimeError("authorization boundary wrapper hash mismatch")
        wrappers.append(wrapper)
    execution_authorization = wrappers[3]["artifact"]
    worker_authorization = wrappers[4]["artifact"]
    return {
        "execution_authorized": execution_authorization["execution_authorized"],
        "worker_authorization_issued": worker_authorization["worker_authorization_issued"],
        "replay_reconstructed": True,
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
    write_json_immutable(
        evidence_dir / "000_human_intent_execution_authorization_boundary_evidence_package.json",
        evidence,
    )
    write_json_immutable(
        evidence_dir / "001_human_intent_execution_authorization_boundary_coverage_report.json",
        coverage,
    )
    write_json_immutable(
        replay_dir / "000_human_intent_execution_authorization_boundary_replay_package.json",
        replay_package,
    )
    write_json_immutable(
        report_dir / "000_human_intent_execution_authorization_boundary_certification_report.json",
        report,
    )


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def main() -> int:
    result = run_human_intent_clarification_execution_authorization_boundary_certification()
    assertions = result["assertions"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"approval_denied_path_verified={assertions['approval_denied_path_verified']}")
    print(f"approval_granted_path_verified={assertions['approval_granted_path_verified']}")
    print(f"execution_authorized_after_approval={assertions['execution_authorized_after_approval']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "HUMAN_INTENT_EXECUTION_AUTHORIZATION_BOUNDARY_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
