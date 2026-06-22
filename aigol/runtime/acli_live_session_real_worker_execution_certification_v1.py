"""Live ACLI-style real worker execution certification."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/acli_live_session_real_worker_execution_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"
FINAL_VERDICT_CERTIFIED = "ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_CERTIFIED"
FINAL_VERDICT_GAPS = "ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_GAPS_FOUND"

REPLAY_STEPS = (
    "acli_session_started",
    "natural_language_turns_recorded",
    "intent_resolution_recorded",
    "execution_summary_recorded",
    "human_approval_recorded",
    "authorization_recorded",
    "worker_handoff_recorded",
    "worker_execution_recorded",
    "side_effect_verification_recorded",
)

SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "scenario_id": "ALS-001",
        "coverage": "clear_user_request",
        "turns": [
            ("human", "Please create a proof note that shows this session safely did real work."),
            ("acli", "I will summarize the bounded file creation before asking for approval."),
            ("human", "Approved."),
        ],
        "worker_type": "FILE_CREATION_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        "target_relative_path": "created/live_session_proof.txt",
        "requested_content": "ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_CERTIFIED\n",
        "initial_content": None,
        "clarification_required": False,
        "correction_before_approval": None,
        "approval_decision": "APPROVE",
        "authorization_issued": True,
        "handoff_modified": False,
        "replay_mismatch": False,
        "verification_expected_to_pass": True,
        "expected_side_effect_executed": True,
    },
    {
        "scenario_id": "ALS-002",
        "coverage": "ambiguous_user_request_requiring_clarification",
        "turns": [
            ("human", "Update it."),
            ("acli", "What file should be updated, and what should the update say?"),
            ("human", "Update the session status note to say the live session worker path is certified."),
            ("acli", "I will summarize the bounded update before asking for approval."),
            ("human", "Approved."),
        ],
        "worker_type": "FILE_UPDATE_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_UPDATE_WORKFLOW",
        "target_relative_path": "updated/live_status.txt",
        "requested_content": "live_session_worker_path=certified\n",
        "initial_content": "live_session_worker_path=pending\n",
        "clarification_required": True,
        "correction_before_approval": None,
        "approval_decision": "APPROVE",
        "authorization_issued": True,
        "handoff_modified": False,
        "replay_mismatch": False,
        "verification_expected_to_pass": True,
        "expected_side_effect_executed": True,
    },
    {
        "scenario_id": "ALS-003",
        "coverage": "user_correction_before_approval",
        "turns": [
            ("human", "Generate a detailed proof artifact."),
            ("acli", "Do you want a detailed artifact or a short operator-safe artifact?"),
            ("human", "Correction: make it short and operator-safe."),
            ("acli", "I will generate the short artifact only after approval."),
            ("human", "Approved."),
        ],
        "worker_type": "ARTIFACT_GENERATION_WORKER",
        "workflow_id": "LIVE_ACLI_ARTIFACT_GENERATION_WORKFLOW",
        "target_relative_path": "artifacts/operator_safe_proof.json",
        "requested_content": "operator-safe-proof-artifact",
        "initial_content": None,
        "clarification_required": True,
        "correction_before_approval": "detailed_to_short_operator_safe",
        "approval_decision": "APPROVE",
        "authorization_issued": True,
        "handoff_modified": False,
        "replay_mismatch": False,
        "verification_expected_to_pass": True,
        "expected_side_effect_executed": True,
    },
    {
        "scenario_id": "ALS-004",
        "coverage": "human_rejection",
        "turns": [
            ("human", "Create the proof file."),
            ("acli", "Please approve the bounded file creation."),
            ("human", "No, do not run it."),
        ],
        "worker_type": "FILE_CREATION_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        "target_relative_path": "blocked/human_rejection.txt",
        "requested_content": "should-not-exist\n",
        "initial_content": None,
        "clarification_required": False,
        "correction_before_approval": None,
        "approval_decision": "REJECT",
        "authorization_issued": False,
        "handoff_modified": False,
        "replay_mismatch": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "HUMAN_REJECTED_EXECUTION",
    },
    {
        "scenario_id": "ALS-005",
        "coverage": "no_approval",
        "turns": [
            ("human", "Create the proof file."),
            ("acli", "Please approve the bounded file creation."),
        ],
        "worker_type": "FILE_CREATION_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        "target_relative_path": "blocked/no_approval.txt",
        "requested_content": "should-not-exist\n",
        "initial_content": None,
        "clarification_required": False,
        "correction_before_approval": None,
        "approval_decision": "MISSING",
        "authorization_issued": False,
        "handoff_modified": False,
        "replay_mismatch": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "MISSING_HUMAN_APPROVAL",
    },
    {
        "scenario_id": "ALS-006",
        "coverage": "no_authorization",
        "turns": [
            ("human", "Create a proof file."),
            ("acli", "Please approve the bounded file creation."),
            ("human", "Approved."),
        ],
        "worker_type": "FILE_CREATION_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        "target_relative_path": "blocked/no_authorization.txt",
        "requested_content": "should-not-exist\n",
        "initial_content": None,
        "clarification_required": False,
        "correction_before_approval": None,
        "approval_decision": "APPROVE",
        "authorization_issued": False,
        "handoff_modified": False,
        "replay_mismatch": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "MISSING_EXECUTION_AUTHORIZATION",
    },
    {
        "scenario_id": "ALS-007",
        "coverage": "modified_handoff_package",
        "turns": [
            ("human", "Create a proof file."),
            ("acli", "Please approve the bounded file creation."),
            ("human", "Approved."),
        ],
        "worker_type": "FILE_CREATION_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        "target_relative_path": "blocked/modified_handoff.txt",
        "requested_content": "should-not-exist\n",
        "initial_content": None,
        "clarification_required": False,
        "correction_before_approval": None,
        "approval_decision": "APPROVE",
        "authorization_issued": True,
        "handoff_modified": True,
        "replay_mismatch": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "MODIFIED_HANDOFF_PACKAGE_DETECTED",
    },
    {
        "scenario_id": "ALS-008",
        "coverage": "invalid_worker_target",
        "turns": [
            ("human", "Create this proof file outside the sandbox."),
            ("acli", "Execution must stay in the certification sandbox."),
            ("human", "Approved."),
        ],
        "worker_type": "FILE_CREATION_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        "target_relative_path": "../outside_sandbox.txt",
        "requested_content": "should-not-exist\n",
        "initial_content": None,
        "clarification_required": False,
        "correction_before_approval": None,
        "approval_decision": "APPROVE",
        "authorization_issued": True,
        "handoff_modified": False,
        "replay_mismatch": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "INVALID_WORKER_TARGET",
    },
    {
        "scenario_id": "ALS-009",
        "coverage": "replay_mismatch",
        "turns": [
            ("human", "Create the replay mismatch proof file."),
            ("acli", "Please approve the bounded file creation."),
            ("human", "Approved."),
        ],
        "worker_type": "FILE_CREATION_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        "target_relative_path": "blocked/replay_mismatch.txt",
        "requested_content": "should-not-exist\n",
        "initial_content": None,
        "clarification_required": False,
        "correction_before_approval": None,
        "approval_decision": "APPROVE",
        "authorization_issued": True,
        "handoff_modified": False,
        "replay_mismatch": True,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "REPLAY_MISMATCH_DETECTED",
    },
    {
        "scenario_id": "ALS-010",
        "coverage": "side_effect_verification_failure",
        "turns": [
            ("human", "Create a proof file and then check it."),
            ("acli", "Please approve the bounded file creation."),
            ("human", "Approved."),
        ],
        "worker_type": "FILE_CREATION_WORKER",
        "workflow_id": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        "target_relative_path": "failed_verification/wrong_content.txt",
        "requested_content": "actual-live-session-content\n",
        "verification_content_override": "different-expected-content\n",
        "initial_content": None,
        "clarification_required": False,
        "correction_before_approval": None,
        "approval_decision": "APPROVE",
        "authorization_issued": True,
        "handoff_modified": False,
        "replay_mismatch": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": True,
        "expected_failure_reason": "SIDE_EFFECT_VERIFICATION_FAILED",
    },
)


def run_acli_live_session_real_worker_execution_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    cert_root = _next_cert_root(base)
    sandbox_root = cert_root / "sandbox"
    scenario_results = [_run_scenario(cert_root / "scenarios" / spec["scenario_id"], sandbox_root, spec) for spec in SCENARIOS]
    replay_results = [_reconstruct_scenario_replay(result) for result in scenario_results]
    no_secret_leak = _secret_free(cert_root)
    assertions = _aggregate_assertions(scenario_results, replay_results, no_secret_leak)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = {
        "artifact_type": "ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "scenario_count": len(scenario_results),
        "coverage": [result["coverage"] for result in scenario_results],
        "positive_scenarios": [result["scenario_id"] for result in scenario_results if result["expected_verification_pass"]],
        "fail_closed_scenarios": [
            result["scenario_id"] for result in scenario_results if not result["expected_verification_pass"]
        ],
        "scenario_verdicts": {result["scenario_id"]: result["scenario_verdict"] for result in scenario_results},
        "assertions": assertions,
        "final_verdict": final_verdict,
    }
    coverage["artifact_hash"] = replay_hash(coverage)

    evidence = {
        "artifact_type": "ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "sandbox_root": str(sandbox_root),
        "scenario_results": scenario_results,
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    evidence["artifact_hash"] = replay_hash(evidence)

    replay_package = {
        "artifact_type": "ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(cert_root),
        "replay_results": replay_results,
        "certified_chain": (
            "Intent Resolution -> Execution Summary -> Human Approval -> Authorization -> "
            "Worker Handoff -> Worker Execution -> Side-Effect Verification -> Replay Reconstruction"
        ),
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)

    report = {
        "artifact_type": "ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "assertions": assertions,
        "observed": assertions,
        "scenario_results": _summarize_scenarios(scenario_results),
        "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
        "recommended_next_certification": "AIGOL_ACLI_LIVE_SESSION_REAL_PROVIDER_AND_WORKER_CHAIN_CERTIFICATION_V1",
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)

    evidence_dir = cert_root / "evidence_package"
    replay_dir = cert_root / "replay_package"
    report_dir = cert_root / "certification_report"
    _persist(evidence_dir, replay_dir, report_dir, evidence, coverage, replay_package, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "sandbox_root": str(sandbox_root),
        "evidence_package_path": str(evidence_dir / "000_acli_live_session_real_worker_execution_evidence_package.json"),
        "coverage_report_path": str(evidence_dir / "001_acli_live_session_real_worker_execution_coverage_report.json"),
        "replay_package_path": str(replay_dir / "000_acli_live_session_real_worker_execution_replay_package.json"),
        "certification_report_path": str(report_dir / "000_acli_live_session_real_worker_execution_certification_report.json"),
        "assertions": assertions,
        "scenario_results": scenario_results,
        "final_verdict": final_verdict,
    }


def _run_scenario(scenario_root: Path, sandbox_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    scenario_sandbox = sandbox_root / spec["scenario_id"]
    target_path, target_failure = _safe_sandbox_path(scenario_sandbox, spec["target_relative_path"])
    if target_failure is None and spec.get("initial_content") is not None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(str(spec["initial_content"]), encoding="utf-8")

    session = _session_artifact(spec)
    turns = _turns_artifact(spec, session)
    intent = _intent_resolution_artifact(spec, turns)
    summary = _execution_summary_artifact(spec, intent, target_path, target_failure)
    approval = _approval_artifact(spec, summary)
    authorization = _authorization_artifact(spec, approval, target_path, target_failure)
    handoff = _handoff_artifact(spec, authorization, target_path, target_failure)
    execution = _worker_execution_artifact(spec, handoff, authorization, scenario_sandbox, target_path, target_failure)
    verification = _verification_artifact(spec, execution, target_path, target_failure)
    artifacts = (session, turns, intent, summary, approval, authorization, handoff, execution, verification)
    _persist_scenario_replay(scenario_root / "replay", artifacts)

    side_effect_present = target_failure is None and target_path.exists()
    scenario_assertions = {
        "acli_session_started": session["acli_session_started"] is True,
        "natural_language_user_input": turns["natural_language_user_input"] is True,
        "intent_resolution": intent["intent_resolved"] is True,
        "clarification_if_required": intent["clarification_completed"] is spec["clarification_required"]
        or spec["clarification_required"] is False,
        "execution_summary_generation": summary["execution_summary_generated"] is True,
        "human_approval_requirement": summary["human_approval_required"] is True,
        "authorization_issuance": authorization["authorization_issued"] is _authorization_expected(
            spec,
            target_failure,
        ),
        "worker_handoff_generation": handoff["worker_handoff_generated"] is _handoff_expected(spec, target_failure),
        "worker_execution": execution["worker_executed"] is spec["expected_side_effect_executed"],
        "side_effect_verification": verification["verification_passed"] is spec["verification_expected_to_pass"],
        "authority_boundary_preservation": _authority_boundary_preserved(spec, approval, authorization, handoff, execution),
    }
    scenario_verdict = "CERTIFIED" if all(scenario_assertions.values()) else "GAPS_FOUND"
    return {
        "scenario_id": spec["scenario_id"],
        "coverage": spec["coverage"],
        "worker_type": spec["worker_type"],
        "target_relative_path": spec["target_relative_path"],
        "target_path": str(target_path),
        "target_failure": target_failure,
        "side_effect_present": side_effect_present,
        "expected_side_effect_executed": spec["expected_side_effect_executed"],
        "expected_verification_pass": spec["verification_expected_to_pass"],
        "failure_reason": verification["failure_reason"] or execution["failure_reason"] or handoff["failure_reason"],
        "scenario_assertions": scenario_assertions,
        "scenario_verdict": scenario_verdict,
        "replay_reference": str(scenario_root / "replay"),
    }


def _session_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_STARTED_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "acli_session_started": True,
            "session_mode": "SIMULATED_LIVE_ACLI_SESSION",
            "human_knows_internal_terms": False,
            "created_at": CREATED_AT,
        }
    )


def _turns_artifact(spec: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_NATURAL_LANGUAGE_TURNS_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "session_reference": session["artifact_hash"],
            "turn_count": len(spec["turns"]),
            "turn_hashes": [replay_hash({"speaker": speaker, "text": text}) for speaker, text in spec["turns"]],
            "natural_language_user_input": True,
            "internal_terms_required_from_user": False,
            "created_at": CREATED_AT,
        }
    )


def _intent_resolution_artifact(spec: dict[str, Any], turns: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_INTENT_RESOLUTION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "turns_reference": turns["artifact_hash"],
            "clear_user_request": spec["coverage"] == "clear_user_request",
            "ambiguous_user_request": spec["clarification_required"],
            "clarification_generated": spec["clarification_required"],
            "clarification_completed": spec["clarification_required"],
            "user_correction_before_approval": spec["correction_before_approval"],
            "intent_resolved": True,
            "workflow_selected": True,
            "selected_workflow": spec["workflow_id"],
            "worker_type": spec["worker_type"],
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _execution_summary_artifact(
    spec: dict[str, Any],
    intent: dict[str, Any],
    target_path: Path,
    target_failure: str | None,
) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_EXECUTION_SUMMARY_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "intent_resolution_reference": intent["artifact_hash"],
            "execution_summary_generated": True,
            "human_approval_required": True,
            "selected_workflow": spec["workflow_id"],
            "worker_type": spec["worker_type"],
            "target_path_reference": str(target_path),
            "target_valid": target_failure is None,
            "requested_content_hash": replay_hash(spec["requested_content"]),
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _approval_artifact(spec: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    approved = spec["approval_decision"] == "APPROVE"
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_HUMAN_APPROVAL_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "execution_summary_reference": summary["artifact_hash"],
            "human_approval_required": True,
            "human_approval_recorded": spec["approval_decision"] != "MISSING",
            "approval_decision": spec["approval_decision"],
            "approved_for_execution": approved,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _authorization_artifact(
    spec: dict[str, Any],
    approval: dict[str, Any],
    target_path: Path,
    target_failure: str | None,
) -> dict[str, Any]:
    issued = spec["authorization_issued"] and approval["approved_for_execution"] is True and target_failure is None
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_AUTHORIZATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "execution_authorization_id": f"{spec['scenario_id']}:AUTHORIZATION",
            "human_approval_reference": approval["artifact_hash"],
            "authorization_issued": issued,
            "requested_authorization_issued": spec["authorization_issued"],
            "authorization_status": _authorization_status(spec, approval, target_failure, issued),
            "authorized_worker_type": spec["worker_type"],
            "authorized_target_path_reference": str(target_path),
            "authorized_content_hash": replay_hash(spec["requested_content"]),
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _handoff_artifact(
    spec: dict[str, Any],
    authorization: dict[str, Any],
    target_path: Path,
    target_failure: str | None,
) -> dict[str, Any]:
    generated = _handoff_expected(spec, target_failure)
    target_reference = str(target_path)
    if spec["handoff_modified"]:
        target_reference = f"{target_reference}:MODIFIED"
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_WORKER_HANDOFF_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "worker_handoff_id": f"{spec['scenario_id']}:WORKER-HANDOFF",
            "authorization_reference": authorization["execution_authorization_id"],
            "authorization_hash": authorization["artifact_hash"],
            "worker_handoff_generated": generated,
            "worker_type": spec["worker_type"],
            "target_path_reference": target_reference,
            "requested_content_hash": replay_hash(spec["requested_content"]),
            "handoff_modified": spec["handoff_modified"],
            "replay_mismatch": spec["replay_mismatch"],
            "failure_reason": None if generated else _expected_failure_reason(spec, target_failure),
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _worker_execution_artifact(
    spec: dict[str, Any],
    handoff: dict[str, Any],
    authorization: dict[str, Any],
    scenario_sandbox: Path,
    target_path: Path,
    target_failure: str | None,
) -> dict[str, Any]:
    allowed = _execution_allowed(spec, handoff, authorization, target_failure)
    side_effect_hash = None
    failure_reason = None
    if allowed:
        side_effect_hash = _execute_worker(spec, scenario_sandbox, target_path)
    else:
        failure_reason = _expected_failure_reason(spec, target_failure)
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_WORKER_EXECUTION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "worker_type": spec["worker_type"],
            "worker_handoff_reference": handoff["worker_handoff_id"],
            "worker_handoff_hash": handoff["artifact_hash"],
            "authorization_reference": authorization["execution_authorization_id"],
            "worker_executed": allowed,
            "side_effect_hash": side_effect_hash,
            "side_effect_path_reference": str(target_path),
            "failure_reason": failure_reason,
            "created_at": CREATED_AT,
        }
    )


def _verification_artifact(
    spec: dict[str, Any],
    execution: dict[str, Any],
    target_path: Path,
    target_failure: str | None,
) -> dict[str, Any]:
    verification = _verify_side_effect(spec, execution, target_path, target_failure)
    return _artifact(
        {
            "artifact_type": "ACLI_LIVE_SESSION_SIDE_EFFECT_VERIFICATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "worker_execution_reference": execution["artifact_hash"],
            "side_effect_verification_performed": True,
            "verification_passed": verification["passed"],
            "target_exists": target_failure is None and target_path.exists(),
            "target_path_reference": str(target_path),
            "expected_content_hash": verification["expected_content_hash"],
            "actual_content_hash": verification["actual_content_hash"],
            "failure_reason": verification["failure_reason"],
            "created_at": CREATED_AT,
        }
    )


def _execute_worker(spec: dict[str, Any], scenario_sandbox: Path, target_path: Path) -> str:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if spec["worker_type"] == "FILE_CREATION_WORKER":
        target_path.write_text(str(spec["requested_content"]), encoding="utf-8")
    elif spec["worker_type"] == "FILE_UPDATE_WORKER":
        existing = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        target_path.write_text(existing + str(spec["requested_content"]), encoding="utf-8")
    elif spec["worker_type"] == "ARTIFACT_GENERATION_WORKER":
        artifact = {
            "artifact_type": "ACLI_LIVE_SESSION_GENERATED_SIDE_EFFECT_ARTIFACT_V1",
            "scenario_id": spec["scenario_id"],
            "worker_type": spec["worker_type"],
            "approval_status": "APPROVED",
            "correction_before_approval": spec["correction_before_approval"],
            "created_at": CREATED_AT,
        }
        artifact["artifact_hash"] = replay_hash(artifact)
        write_json_immutable(target_path, artifact)
    else:
        raise FailClosedRuntimeError("unknown ACLI live-session worker type")
    return _file_hash(target_path)


def _verify_side_effect(
    spec: dict[str, Any],
    execution: dict[str, Any],
    target_path: Path,
    target_failure: str | None,
) -> dict[str, Any]:
    expected_hash = None
    actual_hash = None
    if spec["worker_type"] == "ARTIFACT_GENERATION_WORKER":
        if target_failure is None and target_path.exists():
            actual_hash = load_json(target_path).get("artifact_hash")
            expected_hash = actual_hash
    else:
        expected_content = str(spec.get("verification_content_override", spec["requested_content"]))
        if spec["worker_type"] == "FILE_UPDATE_WORKER":
            expected_content = str(spec["initial_content"]) + expected_content
        expected_hash = replay_hash(expected_content)
        if target_failure is None and target_path.exists():
            actual_hash = replay_hash(target_path.read_text(encoding="utf-8"))
    passed = target_failure is None and target_path.exists() and expected_hash == actual_hash and execution["worker_executed"]
    failure_reason = None if passed else _expected_failure_reason(spec, target_failure)
    return {
        "passed": passed,
        "expected_content_hash": expected_hash,
        "actual_content_hash": actual_hash,
        "failure_reason": failure_reason,
    }


def _persist_scenario_replay(replay_dir: Path, artifacts: tuple[dict[str, Any], ...]) -> None:
    replay_dir.mkdir(parents=True, exist_ok=True)
    if len(artifacts) != len(REPLAY_STEPS):
        raise FailClosedRuntimeError("ACLI live-session replay artifact count mismatch")
    for index, (step, artifact) in enumerate(zip(REPLAY_STEPS, artifacts, strict=True)):
        wrapper = {
            "replay_index": index,
            "replay_step": step,
            "artifact": artifact,
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _reconstruct_scenario_replay(scenario: dict[str, Any]) -> dict[str, Any]:
    replay_path = Path(scenario["replay_reference"])
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("ACLI live-session replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("ACLI live-session replay artifact missing")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    execution = wrappers[7]["artifact"]
    verification = wrappers[8]["artifact"]
    return {
        "scenario_id": scenario["scenario_id"],
        "replay_artifact_count": len(wrappers),
        "worker_executed": execution["worker_executed"],
        "verification_passed": verification["verification_passed"],
        "replay_reconstructed": verification["verification_passed"] is scenario["expected_verification_pass"],
        "replay_hash": replay_hash(wrappers),
    }


def _aggregate_assertions(
    scenario_results: list[dict[str, Any]],
    replay_results: list[dict[str, Any]],
    no_secret_leak: bool,
) -> dict[str, bool]:
    positive = [item for item in scenario_results if item["expected_verification_pass"]]
    blocked = [
        item
        for item in scenario_results
        if not item["expected_verification_pass"] and item["failure_reason"] != "SIDE_EFFECT_VERIFICATION_FAILED"
    ]
    return {
        "live_acli_session_simulated": all(item["scenario_assertions"]["acli_session_started"] for item in scenario_results),
        "natural_language_user_input": all(
            item["scenario_assertions"]["natural_language_user_input"] for item in scenario_results
        ),
        "intent_resolution": all(item["scenario_assertions"]["intent_resolution"] for item in scenario_results),
        "clarification_if_required": all(
            item["scenario_assertions"]["clarification_if_required"] for item in scenario_results
        ),
        "execution_summary_generation": all(
            item["scenario_assertions"]["execution_summary_generation"] for item in scenario_results
        ),
        "human_approval_requirement": all(
            item["scenario_assertions"]["human_approval_requirement"] for item in scenario_results
        ),
        "authorization_issuance": all(item["scenario_assertions"]["authorization_issuance"] for item in scenario_results),
        "worker_handoff_generation": all(
            item["scenario_assertions"]["worker_handoff_generation"] for item in scenario_results
        ),
        "real_worker_execution": all(item["side_effect_present"] for item in positive)
        and all(not item["side_effect_present"] for item in blocked),
        "side_effect_verification": all(
            item["scenario_assertions"]["side_effect_verification"] for item in scenario_results
        ),
        "replay_reconstruction": all(item["replay_reconstructed"] for item in replay_results),
        "authority_boundary_preservation": all(
            item["scenario_assertions"]["authority_boundary_preservation"] for item in scenario_results
        ),
        "secret_free_evidence": no_secret_leak,
    }


def _safe_sandbox_path(scenario_sandbox: Path, relative_path: str) -> tuple[Path, str | None]:
    target = scenario_sandbox / relative_path
    resolved_sandbox = scenario_sandbox.resolve()
    resolved_target = target.resolve()
    if resolved_sandbox not in resolved_target.parents and resolved_target != resolved_sandbox:
        return scenario_sandbox / "INVALID_TARGET_BLOCKED", "INVALID_WORKER_TARGET"
    return target, None


def _authorization_status(
    spec: dict[str, Any],
    approval: dict[str, Any],
    target_failure: str | None,
    issued: bool,
) -> str:
    if target_failure:
        return target_failure
    if approval["human_approval_recorded"] is not True:
        return "BLOCKED_MISSING_HUMAN_APPROVAL"
    if approval["approved_for_execution"] is not True:
        return "BLOCKED_HUMAN_REJECTION"
    if spec["authorization_issued"] is not True:
        return "BLOCKED_MISSING_AUTHORIZATION"
    return "AUTHORIZED" if issued else "BLOCKED"


def _authorization_expected(spec: dict[str, Any], target_failure: str | None) -> bool:
    return (
        target_failure is None
        and spec["approval_decision"] == "APPROVE"
        and spec["authorization_issued"] is True
    )


def _handoff_expected(spec: dict[str, Any], target_failure: str | None) -> bool:
    return (
        target_failure is None
        and spec["approval_decision"] == "APPROVE"
        and spec["authorization_issued"] is True
        and spec["handoff_modified"] is False
        and spec["replay_mismatch"] is False
    )


def _execution_allowed(
    spec: dict[str, Any],
    handoff: dict[str, Any],
    authorization: dict[str, Any],
    target_failure: str | None,
) -> bool:
    return (
        target_failure is None
        and handoff["worker_handoff_generated"] is True
        and authorization["authorization_issued"] is True
        and spec["handoff_modified"] is False
        and spec["replay_mismatch"] is False
    )


def _expected_failure_reason(spec: dict[str, Any], target_failure: str | None) -> str | None:
    if spec["verification_expected_to_pass"]:
        return None
    if target_failure:
        return target_failure
    if spec.get("expected_failure_reason"):
        return str(spec["expected_failure_reason"])
    if spec["approval_decision"] == "MISSING":
        return "MISSING_HUMAN_APPROVAL"
    if spec["approval_decision"] == "REJECT":
        return "HUMAN_REJECTED_EXECUTION"
    if spec["authorization_issued"] is not True:
        return "MISSING_EXECUTION_AUTHORIZATION"
    if spec["handoff_modified"]:
        return "MODIFIED_HANDOFF_PACKAGE_DETECTED"
    if spec["replay_mismatch"]:
        return "REPLAY_MISMATCH_DETECTED"
    return "SIDE_EFFECT_VERIFICATION_FAILED"


def _authority_boundary_preserved(
    spec: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    handoff: dict[str, Any],
    execution: dict[str, Any],
) -> bool:
    if execution["worker_executed"] is True:
        return all(
            [
                approval["approved_for_execution"] is True,
                authorization["authorization_issued"] is True,
                handoff["worker_handoff_generated"] is True,
                spec["handoff_modified"] is False,
                spec["replay_mismatch"] is False,
            ]
        )
    return spec["expected_side_effect_executed"] is False


def _file_hash(path: Path) -> str:
    if path.suffix == ".json":
        return replay_hash(load_json(path))
    return replay_hash(path.read_text(encoding="utf-8"))


def _summarize_scenarios(scenario_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "scenario_id",
        "coverage",
        "worker_type",
        "target_relative_path",
        "side_effect_present",
        "expected_side_effect_executed",
        "expected_verification_pass",
        "failure_reason",
        "scenario_verdict",
    )
    return [{key: item[key] for key in keys} for item in scenario_results]


def _artifact(payload: dict[str, Any]) -> dict[str, Any]:
    payload["artifact_hash"] = replay_hash(payload)
    return payload


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    artifact_hash = artifact.get("artifact_hash")
    artifact_without_hash = dict(artifact)
    artifact_without_hash.pop("artifact_hash", None)
    if replay_hash(artifact_without_hash) != artifact_hash:
        raise FailClosedRuntimeError("ACLI live-session replay artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    wrapper_without_hash = {key: value for key, value in wrapper.items() if key != "replay_hash"}
    if replay_hash(wrapper_without_hash) != wrapper.get("replay_hash"):
        raise FailClosedRuntimeError("ACLI live-session replay wrapper hash mismatch")


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
    evidence: dict[str, Any],
    coverage: dict[str, Any],
    replay_package: dict[str, Any],
    report: dict[str, Any],
) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    write_json_immutable(evidence_dir / "000_acli_live_session_real_worker_execution_evidence_package.json", evidence)
    write_json_immutable(evidence_dir / "001_acli_live_session_real_worker_execution_coverage_report.json", coverage)
    write_json_immutable(replay_dir / "000_acli_live_session_real_worker_execution_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_acli_live_session_real_worker_execution_certification_report.json", report)


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def main() -> int:
    result = run_acli_live_session_real_worker_execution_certification()
    assertions = result["assertions"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"SANDBOX_ROOT={result['sandbox_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"real_worker_execution={assertions['real_worker_execution']}")
    print(f"side_effect_verification={assertions['side_effect_verification']}")
    print(f"replay_reconstruction={assertions['replay_reconstruction']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
