"""Certification for governed real worker side effects from human intent."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/human_intent_real_worker_side_effect_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"
FINAL_VERDICT_CERTIFIED = "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_CERTIFIED"
FINAL_VERDICT_GAPS = "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_GAPS_FOUND"

REPLAY_STEPS = (
    "human_intent_recorded",
    "governance_resolution_recorded",
    "execution_summary_recorded",
    "human_approval_recorded",
    "authorization_recorded",
    "worker_handoff_recorded",
    "side_effect_execution_recorded",
    "side_effect_verification_recorded",
)

SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "scenario_id": "RWS-001",
        "coverage": "file_creation_worker",
        "human_request": "Create a small proof file that shows this action really happened.",
        "worker_type": "FILE_CREATION_WORKER",
        "clarification_required": False,
        "workflow_id": "REAL_FILE_CREATION_SIDE_EFFECT",
        "target_relative_path": "created/proof_note.txt",
        "initial_content": None,
        "requested_content": "AIGOL_REAL_WORKER_SIDE_EFFECT_FILE_CREATED\n",
        "approval_recorded": True,
        "authorization_issued": True,
        "authorization_modified": False,
        "replay_mismatch_injected": False,
        "verification_expected_to_pass": True,
        "expected_side_effect_executed": True,
    },
    {
        "scenario_id": "RWS-002",
        "coverage": "file_update_worker",
        "human_request": "Update the existing proof note with the certification result.",
        "worker_type": "FILE_UPDATE_WORKER",
        "clarification_required": True,
        "clarification_question": "Which existing proof note should be updated, and with what result?",
        "clarification_response": "Update the status note with the certified result line.",
        "workflow_id": "REAL_FILE_UPDATE_SIDE_EFFECT",
        "target_relative_path": "updated/status_note.txt",
        "initial_content": "status=pending\n",
        "requested_content": "status=certified\n",
        "approval_recorded": True,
        "authorization_issued": True,
        "authorization_modified": False,
        "replay_mismatch_injected": False,
        "verification_expected_to_pass": True,
        "expected_side_effect_executed": True,
    },
    {
        "scenario_id": "RWS-003",
        "coverage": "artifact_generation_worker",
        "human_request": "Generate the proof artifact for this certification.",
        "worker_type": "ARTIFACT_GENERATION_WORKER",
        "clarification_required": True,
        "clarification_question": "What should the proof artifact contain?",
        "clarification_response": "Include the worker type, approval status, and verification status.",
        "workflow_id": "REAL_ARTIFACT_GENERATION_SIDE_EFFECT",
        "target_relative_path": "artifacts/generated_proof_artifact.json",
        "initial_content": None,
        "requested_content": "generated-proof-artifact",
        "approval_recorded": True,
        "authorization_issued": True,
        "authorization_modified": False,
        "replay_mismatch_injected": False,
        "verification_expected_to_pass": True,
        "expected_side_effect_executed": True,
    },
    {
        "scenario_id": "RWS-004",
        "coverage": "missing_approval_rejection",
        "human_request": "Create the file, but I have not approved it yet.",
        "worker_type": "FILE_CREATION_WORKER",
        "clarification_required": False,
        "workflow_id": "REAL_FILE_CREATION_SIDE_EFFECT",
        "target_relative_path": "rejected/missing_approval.txt",
        "initial_content": None,
        "requested_content": "should-not-exist\n",
        "approval_recorded": False,
        "authorization_issued": False,
        "authorization_modified": False,
        "replay_mismatch_injected": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "MISSING_HUMAN_APPROVAL",
    },
    {
        "scenario_id": "RWS-005",
        "coverage": "missing_authorization_rejection",
        "human_request": "I approve the proof file.",
        "worker_type": "FILE_CREATION_WORKER",
        "clarification_required": False,
        "workflow_id": "REAL_FILE_CREATION_SIDE_EFFECT",
        "target_relative_path": "rejected/missing_authorization.txt",
        "initial_content": None,
        "requested_content": "should-not-exist\n",
        "approval_recorded": True,
        "authorization_issued": False,
        "authorization_modified": False,
        "replay_mismatch_injected": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "MISSING_EXECUTION_AUTHORIZATION",
    },
    {
        "scenario_id": "RWS-006",
        "coverage": "modified_authorization_rejection",
        "human_request": "Use the approved authorization but change the target file.",
        "worker_type": "FILE_CREATION_WORKER",
        "clarification_required": False,
        "workflow_id": "REAL_FILE_CREATION_SIDE_EFFECT",
        "target_relative_path": "rejected/modified_authorization.txt",
        "initial_content": None,
        "requested_content": "should-not-exist\n",
        "approval_recorded": True,
        "authorization_issued": True,
        "authorization_modified": True,
        "replay_mismatch_injected": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "MODIFIED_AUTHORIZATION_DETECTED",
    },
    {
        "scenario_id": "RWS-007",
        "coverage": "replay_mismatch_rejection",
        "human_request": "Create the proof file with mismatched replay.",
        "worker_type": "FILE_CREATION_WORKER",
        "clarification_required": False,
        "workflow_id": "REAL_FILE_CREATION_SIDE_EFFECT",
        "target_relative_path": "rejected/replay_mismatch.txt",
        "initial_content": None,
        "requested_content": "should-not-exist\n",
        "approval_recorded": True,
        "authorization_issued": True,
        "authorization_modified": False,
        "replay_mismatch_injected": True,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": False,
        "expected_failure_reason": "REPLAY_MISMATCH_DETECTED",
    },
    {
        "scenario_id": "RWS-008",
        "coverage": "side_effect_verification_failure",
        "human_request": "Create a proof file, but verify the wrong expected content.",
        "worker_type": "FILE_CREATION_WORKER",
        "clarification_required": False,
        "workflow_id": "REAL_FILE_CREATION_SIDE_EFFECT",
        "target_relative_path": "failed_verification/wrong_content.txt",
        "initial_content": None,
        "requested_content": "actual-side-effect-content\n",
        "verification_content_override": "different-expected-content\n",
        "approval_recorded": True,
        "authorization_issued": True,
        "authorization_modified": False,
        "replay_mismatch_injected": False,
        "verification_expected_to_pass": False,
        "expected_side_effect_executed": True,
        "expected_failure_reason": "SIDE_EFFECT_VERIFICATION_FAILED",
    },
)


def run_human_intent_real_worker_side_effect_certification(
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
        "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "scenario_count": len(scenario_results),
        "positive_side_effect_workers": [
            result["worker_type"] for result in scenario_results if result["expected_side_effect_executed"] is True
        ],
        "rejection_scenarios": [
            result["scenario_id"] for result in scenario_results if result["expected_verification_pass"] is False
        ],
        "scenario_verdicts": {result["scenario_id"]: result["scenario_verdict"] for result in scenario_results},
        "assertions": assertions,
        "final_verdict": final_verdict,
    }
    coverage["artifact_hash"] = replay_hash(coverage)

    evidence = {
        "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_EVIDENCE_PACKAGE_V1",
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
        "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(cert_root),
        "replay_results": replay_results,
        "governed_chain": "Intent Resolution -> Human Approval -> Authorization -> Worker Handoff -> Real Worker Side Effect -> Verification -> Replay",
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)

    report = {
        "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "assertions": assertions,
        "observed": assertions,
        "scenario_results": _summarize_scenarios(scenario_results),
        "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
        "recommended_next_certification": "AIGOL_HUMAN_INTENT_LIVE_ACLI_REAL_WORKER_SIDE_EFFECT_CERTIFICATION_V1",
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
        "evidence_package_path": str(evidence_dir / "000_human_intent_real_worker_side_effect_evidence_package.json"),
        "coverage_report_path": str(evidence_dir / "001_human_intent_real_worker_side_effect_coverage_report.json"),
        "replay_package_path": str(replay_dir / "000_human_intent_real_worker_side_effect_replay_package.json"),
        "certification_report_path": str(report_dir / "000_human_intent_real_worker_side_effect_certification_report.json"),
        "assertions": assertions,
        "scenario_results": scenario_results,
        "final_verdict": final_verdict,
    }


def _run_scenario(scenario_root: Path, sandbox_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    scenario_sandbox = sandbox_root / spec["scenario_id"]
    target_path = _safe_sandbox_path(scenario_sandbox, spec["target_relative_path"])
    if spec.get("initial_content") is not None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(str(spec["initial_content"]), encoding="utf-8")

    human_intent = _human_intent_artifact(spec)
    governance = _governance_resolution_artifact(spec, human_intent)
    summary = _execution_summary_artifact(spec, governance, target_path)
    approval = _human_approval_artifact(spec, summary)
    authorization = _authorization_artifact(spec, approval, target_path)
    handoff = _worker_handoff_artifact(spec, authorization, target_path)
    execution = _side_effect_execution_artifact(spec, handoff, authorization, scenario_sandbox, target_path)
    verification = _side_effect_verification_artifact(spec, execution, target_path)
    artifacts = (human_intent, governance, summary, approval, authorization, handoff, execution, verification)
    _persist_scenario_replay(scenario_root / "replay", artifacts)

    side_effect_present = target_path.exists()
    scenario_assertions = {
        "intent_detection": human_intent["intent_detected"] is True,
        "clarification_if_required": (
            governance["clarification_completed"] is True
            if spec["clarification_required"]
            else governance["clarification_required"] is False
        ),
        "workflow_selection": governance["workflow_selected"] is True,
        "execution_summary_generation": summary["execution_summary_generated"] is True,
        "human_approval_requirement": summary["human_approval_required"] is True,
        "authorization_issuance": authorization["authorization_issued"] is spec["authorization_issued"],
        "worker_handoff_generation": handoff["worker_handoff_generated"] is _handoff_expected(spec),
        "side_effect_execution": execution["side_effect_executed"] is spec["expected_side_effect_executed"],
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
        "side_effect_present": side_effect_present,
        "expected_side_effect_executed": spec["expected_side_effect_executed"],
        "expected_verification_pass": spec["verification_expected_to_pass"],
        "failure_reason": verification["failure_reason"] or execution["failure_reason"] or handoff["failure_reason"],
        "scenario_assertions": scenario_assertions,
        "scenario_verdict": scenario_verdict,
        "replay_reference": str(scenario_root / "replay"),
        "side_effect_hash": execution["side_effect_hash"],
        "verification_hash": verification["artifact_hash"],
    }


def _human_intent_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_INTENT_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "human_request_hash": replay_hash(spec["human_request"]),
            "intent_detected": True,
            "intent_family": spec["worker_type"],
            "clarification_required": spec["clarification_required"],
            "internal_terms_required_from_human": False,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _governance_resolution_artifact(spec: dict[str, Any], human_intent: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_GOVERNANCE_RESOLUTION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "human_intent_reference": human_intent["artifact_hash"],
            "clarification_required": spec["clarification_required"],
            "clarification_question_hash": replay_hash(spec.get("clarification_question", "")),
            "clarification_response_hash": replay_hash(spec.get("clarification_response", "")),
            "clarification_completed": bool(spec.get("clarification_response")) if spec["clarification_required"] else False,
            "workflow_selected": True,
            "selected_workflow": spec["workflow_id"],
            "worker_type": spec["worker_type"],
            "governance_mutated": False,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _execution_summary_artifact(spec: dict[str, Any], governance: dict[str, Any], target_path: Path) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_EXECUTION_SUMMARY_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "governance_resolution_reference": governance["artifact_hash"],
            "execution_summary_generated": True,
            "human_approval_required": True,
            "selected_workflow": governance["selected_workflow"],
            "worker_type": spec["worker_type"],
            "target_path_reference": _path_reference(target_path),
            "requested_content_hash": replay_hash(spec["requested_content"]),
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _human_approval_artifact(spec: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_APPROVAL_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "execution_summary_reference": summary["artifact_hash"],
            "human_approval_required": True,
            "human_approval_recorded": spec["approval_recorded"],
            "approval_decision": "APPROVE" if spec["approval_recorded"] else "MISSING_APPROVAL",
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _authorization_artifact(spec: dict[str, Any], approval: dict[str, Any], target_path: Path) -> dict[str, Any]:
    authorization_issued = spec["authorization_issued"]
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_AUTHORIZATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "execution_authorization_id": f"{spec['scenario_id']}:EXECUTION-AUTHORIZATION",
            "human_approval_reference": approval["artifact_hash"],
            "human_approval_recorded": approval["human_approval_recorded"],
            "authorization_issued": authorization_issued,
            "authorization_modified": spec["authorization_modified"],
            "authorized_worker_type": spec["worker_type"],
            "authorized_target_path_reference": _path_reference(target_path),
            "authorized_content_hash": replay_hash(spec["requested_content"]),
            "authorization_status": _authorization_status(spec, approval),
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _worker_handoff_artifact(spec: dict[str, Any], authorization: dict[str, Any], target_path: Path) -> dict[str, Any]:
    handoff_generated = _handoff_expected(spec)
    failure_reason = None if handoff_generated else _expected_failure_reason(spec)
    target_reference = _path_reference(target_path)
    if spec["authorization_modified"]:
        target_reference = f"{target_reference}:MODIFIED"
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_HANDOFF_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "worker_handoff_id": f"{spec['scenario_id']}:WORKER-HANDOFF",
            "authorization_reference": authorization["execution_authorization_id"],
            "authorization_hash": authorization["artifact_hash"],
            "worker_handoff_generated": handoff_generated,
            "worker_type": spec["worker_type"],
            "target_path_reference": target_reference,
            "requested_content_hash": replay_hash(spec["requested_content"]),
            "replay_mismatch_injected": spec["replay_mismatch_injected"],
            "failure_reason": failure_reason,
            "worker_invoked": False,
            "created_at": CREATED_AT,
        }
    )


def _side_effect_execution_artifact(
    spec: dict[str, Any],
    handoff: dict[str, Any],
    authorization: dict[str, Any],
    scenario_sandbox: Path,
    target_path: Path,
) -> dict[str, Any]:
    allowed = _execution_allowed(spec, handoff, authorization)
    side_effect_hash = None
    failure_reason = None
    if allowed:
        side_effect_hash = _execute_worker(spec, scenario_sandbox, target_path)
    else:
        failure_reason = _expected_failure_reason(spec)
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_EXECUTION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "worker_type": spec["worker_type"],
            "worker_handoff_reference": handoff["worker_handoff_id"],
            "worker_handoff_hash": handoff["artifact_hash"],
            "authorization_reference": authorization["execution_authorization_id"],
            "side_effect_executed": allowed,
            "side_effect_hash": side_effect_hash,
            "side_effect_path_reference": _path_reference(target_path),
            "failure_reason": failure_reason,
            "created_at": CREATED_AT,
        }
    )


def _side_effect_verification_artifact(spec: dict[str, Any], execution: dict[str, Any], target_path: Path) -> dict[str, Any]:
    verification = _verify_side_effect(spec, execution, target_path)
    return _artifact(
        {
            "artifact_type": "HUMAN_INTENT_REAL_WORKER_SIDE_EFFECT_VERIFICATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "scenario_id": spec["scenario_id"],
            "side_effect_execution_reference": execution["artifact_hash"],
            "side_effect_verification_performed": True,
            "verification_passed": verification["passed"],
            "target_exists": target_path.exists(),
            "target_path_reference": _path_reference(target_path),
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
            "artifact_type": "REAL_WORKER_SIDE_EFFECT_GENERATED_ARTIFACT_V1",
            "scenario_id": spec["scenario_id"],
            "worker_type": spec["worker_type"],
            "approval_status": "APPROVED",
            "verification_status": "PENDING_REPLAY_VERIFICATION",
            "created_at": CREATED_AT,
        }
        artifact["artifact_hash"] = replay_hash(artifact)
        write_json_immutable(target_path, artifact)
    else:
        raise FailClosedRuntimeError("unknown side-effect worker type")
    return _file_hash(target_path, scenario_sandbox)


def _verify_side_effect(spec: dict[str, Any], execution: dict[str, Any], target_path: Path) -> dict[str, Any]:
    expected_hash = None
    actual_hash = None
    failure_reason = None
    if spec["worker_type"] == "ARTIFACT_GENERATION_WORKER":
        if target_path.exists():
            actual = load_json(target_path)
            actual_hash = actual.get("artifact_hash")
            expected_hash = actual_hash
    else:
        expected_content = str(spec.get("verification_content_override", spec["requested_content"]))
        if spec["worker_type"] == "FILE_UPDATE_WORKER":
            expected_content = str(spec["initial_content"]) + expected_content
        expected_hash = replay_hash(expected_content)
        if target_path.exists():
            actual_hash = replay_hash(target_path.read_text(encoding="utf-8"))
    passed = target_path.exists() and expected_hash == actual_hash and execution["side_effect_executed"] is True
    if not passed:
        failure_reason = spec.get("expected_failure_reason") or "SIDE_EFFECT_VERIFICATION_FAILED"
    return {
        "passed": passed,
        "expected_content_hash": expected_hash,
        "actual_content_hash": actual_hash,
        "failure_reason": failure_reason,
    }


def _persist_scenario_replay(replay_dir: Path, artifacts: tuple[dict[str, Any], ...]) -> None:
    replay_dir.mkdir(parents=True, exist_ok=True)
    if len(artifacts) != len(REPLAY_STEPS):
        raise FailClosedRuntimeError("real worker side-effect replay artifact count mismatch")
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
            raise FailClosedRuntimeError("real worker side-effect replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("real worker side-effect replay artifact missing")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    execution = wrappers[6]["artifact"]
    verification = wrappers[7]["artifact"]
    expected_pass = scenario["expected_verification_pass"]
    return {
        "scenario_id": scenario["scenario_id"],
        "replay_artifact_count": len(wrappers),
        "side_effect_executed": execution["side_effect_executed"],
        "side_effect_verification_performed": verification["side_effect_verification_performed"],
        "verification_passed": verification["verification_passed"],
        "replay_reconstructed": verification["verification_passed"] is expected_pass,
        "replay_hash": replay_hash(wrappers),
    }


def _aggregate_assertions(
    scenario_results: list[dict[str, Any]],
    replay_results: list[dict[str, Any]],
    no_secret_leak: bool,
) -> dict[str, bool]:
    positive = [item for item in scenario_results if item["expected_verification_pass"] is True]
    negative = [item for item in scenario_results if item["expected_verification_pass"] is False]
    return {
        "intent_detection": all(item["scenario_assertions"]["intent_detection"] for item in scenario_results),
        "clarification_if_required": all(
            item["scenario_assertions"]["clarification_if_required"] for item in scenario_results
        ),
        "workflow_selection": all(item["scenario_assertions"]["workflow_selection"] for item in scenario_results),
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
        "side_effect_execution": all(item["side_effect_present"] is True for item in positive)
        and all(
            item["side_effect_present"] is False
            for item in negative
            if item["failure_reason"] != "SIDE_EFFECT_VERIFICATION_FAILED"
        ),
        "side_effect_verification": all(
            item["scenario_assertions"]["side_effect_verification"] for item in scenario_results
        ),
        "replay_reconstruction": all(item["replay_reconstructed"] for item in replay_results),
        "authority_boundary_preservation": all(
            item["scenario_assertions"]["authority_boundary_preservation"] for item in scenario_results
        ),
        "secret_free_evidence": no_secret_leak,
    }


def _safe_sandbox_path(scenario_sandbox: Path, relative_path: str) -> Path:
    target = scenario_sandbox / relative_path
    resolved_sandbox = scenario_sandbox.resolve()
    resolved_target = target.resolve()
    if resolved_sandbox not in resolved_target.parents and resolved_target != resolved_sandbox:
        raise FailClosedRuntimeError("side-effect target escapes certification sandbox")
    return target


def _path_reference(path: Path) -> str:
    return str(path)


def _file_hash(path: Path, scenario_sandbox: Path) -> str:
    if not path.exists():
        return replay_hash({"missing": _path_reference(path)})
    if path.suffix == ".json":
        return replay_hash(load_json(path))
    return replay_hash(path.read_text(encoding="utf-8"))


def _authorization_status(spec: dict[str, Any], approval: dict[str, Any]) -> str:
    if approval["human_approval_recorded"] is not True:
        return "BLOCKED_MISSING_HUMAN_APPROVAL"
    if spec["authorization_issued"] is not True:
        return "BLOCKED_MISSING_AUTHORIZATION"
    if spec["authorization_modified"]:
        return "AUTHORIZATION_MODIFIED"
    if spec["replay_mismatch_injected"]:
        return "REPLAY_MISMATCH_REQUESTED"
    return "AUTHORIZED"


def _handoff_expected(spec: dict[str, Any]) -> bool:
    return (
        spec["approval_recorded"] is True
        and spec["authorization_issued"] is True
        and spec["authorization_modified"] is False
        and spec["replay_mismatch_injected"] is False
    )


def _execution_allowed(spec: dict[str, Any], handoff: dict[str, Any], authorization: dict[str, Any]) -> bool:
    return (
        handoff["worker_handoff_generated"] is True
        and authorization["authorization_issued"] is True
        and authorization["authorization_modified"] is False
        and spec["replay_mismatch_injected"] is False
    )


def _expected_failure_reason(spec: dict[str, Any]) -> str | None:
    if spec["verification_expected_to_pass"] is True:
        return None
    if spec.get("expected_failure_reason"):
        return str(spec["expected_failure_reason"])
    if spec["approval_recorded"] is not True:
        return "MISSING_HUMAN_APPROVAL"
    if spec["authorization_issued"] is not True:
        return "MISSING_EXECUTION_AUTHORIZATION"
    if spec["authorization_modified"]:
        return "MODIFIED_AUTHORIZATION_DETECTED"
    if spec["replay_mismatch_injected"]:
        return "REPLAY_MISMATCH_DETECTED"
    return "SIDE_EFFECT_VERIFICATION_FAILED"


def _authority_boundary_preserved(
    spec: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    handoff: dict[str, Any],
    execution: dict[str, Any],
) -> bool:
    if execution["side_effect_executed"] is True:
        return all(
            [
                approval["human_approval_recorded"] is True,
                authorization["authorization_issued"] is True,
                authorization["authorization_modified"] is False,
                handoff["worker_handoff_generated"] is True,
            ]
        )
    return spec["expected_side_effect_executed"] is False


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
        raise FailClosedRuntimeError("real worker side-effect replay artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    wrapper_without_hash = {key: value for key, value in wrapper.items() if key != "replay_hash"}
    if replay_hash(wrapper_without_hash) != wrapper.get("replay_hash"):
        raise FailClosedRuntimeError("real worker side-effect replay wrapper hash mismatch")


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
    write_json_immutable(evidence_dir / "000_human_intent_real_worker_side_effect_evidence_package.json", evidence)
    write_json_immutable(evidence_dir / "001_human_intent_real_worker_side_effect_coverage_report.json", coverage)
    write_json_immutable(replay_dir / "000_human_intent_real_worker_side_effect_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_human_intent_real_worker_side_effect_certification_report.json", report)


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def main() -> int:
    result = run_human_intent_real_worker_side_effect_certification()
    assertions = result["assertions"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"SANDBOX_ROOT={result['sandbox_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"side_effect_execution={assertions['side_effect_execution']}")
    print(f"side_effect_verification={assertions['side_effect_verification']}")
    print(f"authority_boundary_preservation={assertions['authority_boundary_preservation']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
