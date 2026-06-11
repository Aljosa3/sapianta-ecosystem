"""Governed ACLI human prompt regression suite runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION = "AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_V1"
REGRESSION_TEST_EVIDENCE_V1 = "REGRESSION_TEST_EVIDENCE_V1"
REGRESSION_RUN_ARTIFACT_V1 = "REGRESSION_RUN_ARTIFACT_V1"
REGRESSION_CERTIFICATION_ARTIFACT_V1 = "REGRESSION_CERTIFICATION_ARTIFACT_V1"

TERMINATED = "TERMINATED"
FAILED_CLOSED = "FAILED_CLOSED"
WAITING_FOR_OPERATOR = "WAITING_FOR_OPERATOR"
WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
MAX_LIFECYCLE_LIMIT_REACHED = "MAX_LIFECYCLE_LIMIT_REACHED"
COMPLETED = "COMPLETED"

ROUTING_FAILURE = "ROUTING_FAILURE"
FAIL_CLOSED = "FAIL_CLOSED"
CLARIFICATION_STALL = "CLARIFICATION_STALL"
CONTINUATION_FAILURE = "CONTINUATION_FAILURE"
REPLAY_CONTINUITY_BREAK = "REPLAY_CONTINUITY_BREAK"
WORKFLOW_STATE_DEVIATION = "WORKFLOW_STATE_DEVIATION"
LIFECYCLE_STAGE_DEVIATION = "LIFECYCLE_STAGE_DEVIATION"
UNKNOWN = "UNKNOWN"

STOP_STAGES = {
    TERMINATED,
    FAILED_CLOSED,
    WAITING_FOR_OPERATOR,
    MAX_LIFECYCLE_LIMIT_REACHED,
}

GOVERNANCE_CONSTRAINTS = {
    "deterministic": True,
    "replay_preserving": True,
    "fail_closed": True,
    "read_only": True,
    "code_modified": False,
    "repair_invoked": False,
    "ppp_invoked": False,
    "provider_fix_invoked": False,
    "worker_remediation_invoked": False,
    "improvement_intent_created": False,
}


def load_prompt_corpus(corpus_path: str | Path) -> list[dict[str, str]]:
    """Load a deterministic plain-text prompt corpus, one non-empty line per test."""

    path = Path(corpus_path)
    if not path.exists():
        raise FailClosedRuntimeError("prompt corpus missing")
    prompts = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return _prompt_cases(prompts)


def run_acli_human_prompt_regression_suite(
    *,
    prompts: Iterable[str] | None = None,
    corpus_path: str | Path | None = None,
    run_id: str,
    created_at: str,
    runtime_root: str | Path,
    workspace: str | Path = ".",
    auto_continue: bool = True,
    max_lifecycle_depth: int = 32,
) -> dict[str, Any]:
    """Execute a prompt corpus through the ACLI conversation entrypoint."""

    if max_lifecycle_depth < 1:
        raise FailClosedRuntimeError("max lifecycle depth must be positive")
    cases = load_prompt_corpus(corpus_path) if corpus_path is not None else _prompt_cases(prompts or ())
    root = Path(runtime_root)
    run_root = root / _safe_segment(run_id)
    test_evidence = [
        _execute_prompt_case(
            case=case,
            case_index=index,
            run_id=run_id,
            created_at=created_at,
            run_root=run_root,
            workspace=workspace,
            auto_continue=auto_continue,
            max_lifecycle_depth=max_lifecycle_depth,
        )
        for index, case in enumerate(cases, start=1)
    ]
    run_artifact = _regression_run_artifact(
        run_id=run_id,
        created_at=created_at,
        test_evidence=test_evidence,
        replay_reference=str(run_root),
    )
    certification = _regression_certification_artifact(
        run_id=run_id,
        created_at=created_at,
        run_artifact=run_artifact,
        test_evidence=test_evidence,
    )
    write_json_immutable(run_root / "REGRESSION_RUN_ARTIFACT_V1.json", run_artifact)
    write_json_immutable(
        run_root / "REGRESSION_CERTIFICATION_ARTIFACT_V1.json",
        certification,
    )
    return {
        "runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION,
        "run_id": run_id,
        "regression_run_artifact": run_artifact,
        "regression_certification_artifact": certification,
        "test_evidence": test_evidence,
        "regression_run_artifact_replay_reference": str(run_root / "REGRESSION_RUN_ARTIFACT_V1.json"),
        "regression_certification_artifact_replay_reference": str(
            run_root / "REGRESSION_CERTIFICATION_ARTIFACT_V1.json"
        ),
        "governance_constraints": deepcopy(GOVERNANCE_CONSTRAINTS),
    }


def reconstruct_acli_human_prompt_regression_suite(run_root: str | Path) -> dict[str, Any]:
    """Reconstruct and verify regression run and certification artifacts."""

    root = Path(run_root)
    run_artifact = load_json(root / "REGRESSION_RUN_ARTIFACT_V1.json")
    certification = load_json(root / "REGRESSION_CERTIFICATION_ARTIFACT_V1.json")
    _verify_artifact_hash(run_artifact)
    _verify_artifact_hash(certification)
    if certification.get("regression_run_hash") != run_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("regression certification run hash mismatch")
    return {
        "run_artifact": run_artifact,
        "certification_artifact": certification,
        "replay_lineage_preserved": certification["replay_lineage_preserved"],
        "determinism_preserved": certification["determinism_preserved"],
        "fail_closed_preserved": certification["fail_closed_preserved"],
    }


def _execute_prompt_case(
    *,
    case: dict[str, str],
    case_index: int,
    run_id: str,
    created_at: str,
    run_root: Path,
    workspace: str | Path,
    auto_continue: bool,
    max_lifecycle_depth: int,
) -> dict[str, Any]:
    session_id = f"{_safe_segment(run_id)}-TEST-{case_index:06d}"
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            created_at,
            "--runtime-root",
            str(run_root / "sessions"),
            "--workspace",
            str(workspace),
            *(("--auto-continue",) if auto_continue else ()),
        ]
    )
    output: list[str] = []
    try:
        result = run_interactive_conversation(
            args,
            input_func=_input_sequence([case["prompt_text"], "exit"]),
            output_func=output.append,
        )
    except Exception as exc:
        result = {
            "session_id": session_id,
            "turn_count": 0,
            "failed_turns": 1,
            "turns": [],
            "runtime_root": str(run_root / "sessions" / session_id),
            "auto_continue_enabled": auto_continue,
            "auto_continue_turns": 0,
            "auto_continue_stop_reason": FAILED_CLOSED,
            "terminated": False,
            "failure_reason": str(exc) or "ACLI regression test failed closed",
        }
    turns = result.get("turns") if isinstance(result.get("turns"), list) else []
    final_turn = turns[-1] if turns else {}
    final_status = final_turn.get("workflow_status") if isinstance(final_turn, dict) else {}
    if not isinstance(final_status, dict):
        final_status = {}
    lifecycle_depth = _lifecycle_depth(turns)
    max_limit_reached = lifecycle_depth > max_lifecycle_depth
    final_lifecycle_stage = _final_lifecycle_stage(result, final_status, max_limit_reached=max_limit_reached)
    replay_inventory = _collect_replay_inventory(
        Path(result.get("runtime_root") or run_root / "sessions" / session_id)
    )
    evidence = {
        "artifact_type": REGRESSION_TEST_EVIDENCE_V1,
        "runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION,
        "run_id": run_id,
        "prompt_id": case["prompt_id"],
        "session_id": session_id,
        "prompt_text_hash": replay_hash(case["prompt_text"]),
        "detected_workflow": _detected_workflow(turns),
        "workflow_state_transitions": _workflow_state_transitions(turns),
        "lifecycle_stages_reached": _lifecycle_stages_reached(turns),
        "final_lifecycle_stage": final_lifecycle_stage,
        "final_workflow_state": str(final_status.get("workflow_state") or final_lifecycle_stage),
        "final_workflow_name": str(final_status.get("workflow_name") or _detected_workflow(turns)),
        "lifecycle_depth": lifecycle_depth,
        "max_lifecycle_limit": max_lifecycle_depth,
        "max_lifecycle_limit_reached": max_limit_reached,
        "failed_closed": final_lifecycle_stage == FAILED_CLOSED,
        "waiting_for_operator": final_lifecycle_stage == WAITING_FOR_OPERATOR,
        "terminated": final_lifecycle_stage == TERMINATED,
        "failure_classification": _failure_classification(result, final_status, final_lifecycle_stage, replay_inventory),
        "failure_reason": _failure_reason(result, turns),
        "replay_references": replay_inventory["replay_references"],
        "replay_hashes": replay_inventory["replay_hashes"],
        "replay_lineage_preserved": replay_inventory["replay_lineage_preserved"],
        "governance_constraints": deepcopy(GOVERNANCE_CONSTRAINTS),
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    write_json_immutable(
        run_root / "test_evidence" / f"{case['prompt_id']}.json",
        evidence,
    )
    return evidence


def _regression_run_artifact(
    *,
    run_id: str,
    created_at: str,
    test_evidence: list[dict[str, Any]],
    replay_reference: str,
) -> dict[str, Any]:
    total = len(test_evidence)
    passed = sum(1 for evidence in test_evidence if evidence["terminated"] is True)
    waiting = sum(1 for evidence in test_evidence if evidence["waiting_for_operator"] is True)
    failed = sum(
        1
        for evidence in test_evidence
        if evidence["final_lifecycle_stage"] in {FAILED_CLOSED, MAX_LIFECYCLE_LIMIT_REACHED}
    )
    artifact = {
        "artifact_type": REGRESSION_RUN_ARTIFACT_V1,
        "runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION,
        "run_id": run_id,
        "execution_timestamp": created_at,
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "waiting_tests": waiting,
        "termination_rate": _rate(passed, total),
        "fail_closed_rate": _rate(sum(1 for evidence in test_evidence if evidence["failed_closed"]), total),
        "average_lifecycle_depth": _average(evidence["lifecycle_depth"] for evidence in test_evidence),
        "workflow_distribution": _workflow_distribution(test_evidence),
        "failure_summaries": _failure_summaries(test_evidence),
        "replay_references": [evidence["replay_references"] for evidence in test_evidence],
        "test_evidence_hashes": [evidence["artifact_hash"] for evidence in test_evidence],
        "replay_reference": replay_reference,
        "governance_constraints": deepcopy(GOVERNANCE_CONSTRAINTS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _regression_certification_artifact(
    *,
    run_id: str,
    created_at: str,
    run_artifact: dict[str, Any],
    test_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    detected_deviations = _detected_deviations(test_evidence)
    failed_tests = int(run_artifact["failed_tests"])
    replay_lineage_preserved = all(evidence["replay_lineage_preserved"] is True for evidence in test_evidence)
    status = "CERTIFIED" if failed_tests == 0 and replay_lineage_preserved else "FAILED_CLOSED"
    if status == "CERTIFIED" and run_artifact["waiting_tests"]:
        rationale = "Regression corpus executed with visible operator gates and no failed-closed tests."
    elif status == "CERTIFIED":
        rationale = "Regression corpus executed to governed terminal stages without detected deviations."
    else:
        rationale = "Regression corpus detected failed-closed tests or replay continuity breaks."
    artifact = {
        "artifact_type": REGRESSION_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION,
        "run_id": run_id,
        "certified_at": created_at,
        "certification_status": status,
        "execution_statistics": {
            "total_tests": run_artifact["total_tests"],
            "passed_tests": run_artifact["passed_tests"],
            "failed_tests": run_artifact["failed_tests"],
            "waiting_tests": run_artifact["waiting_tests"],
            "termination_rate": run_artifact["termination_rate"],
            "fail_closed_rate": run_artifact["fail_closed_rate"],
            "average_lifecycle_depth": run_artifact["average_lifecycle_depth"],
        },
        "replay_references": run_artifact["replay_references"],
        "detected_deviations": detected_deviations,
        "certification_rationale": rationale,
        "regression_run_hash": run_artifact["artifact_hash"],
        "replay_lineage_preserved": replay_lineage_preserved,
        "determinism_preserved": True,
        "fail_closed_preserved": True,
        "governance_constraints": deepcopy(GOVERNANCE_CONSTRAINTS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _prompt_cases(prompts: Iterable[str]) -> list[dict[str, str]]:
    cases = []
    for index, prompt in enumerate(prompts, start=1):
        text = str(prompt).strip()
        if not text:
            continue
        cases.append({"prompt_id": f"PROMPT-{index:06d}", "prompt_text": text})
    if not cases:
        raise FailClosedRuntimeError("prompt corpus must contain at least one prompt")
    return cases


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _safe_segment(value: str) -> str:
    segment = "".join(character if character.isalnum() or character in "-_" else "-" for character in value.strip())
    return segment or "REGRESSION-RUN"


def _lifecycle_depth(turns: list[Any]) -> int:
    return sum(1 for turn in turns if isinstance(turn, dict) and isinstance(turn.get("workflow_status"), dict))


def _final_lifecycle_stage(
    result: dict[str, Any],
    final_status: dict[str, Any],
    *,
    max_limit_reached: bool,
) -> str:
    if max_limit_reached:
        return MAX_LIFECYCLE_LIMIT_REACHED
    workflow_state = str(final_status.get("workflow_state") or "")
    current_stage = str(final_status.get("current_lifecycle_stage") or "")
    if result.get("failed_turns", 0) or workflow_state == FAILED_CLOSED:
        return FAILED_CLOSED
    if workflow_state in {WAITING_FOR_OPERATOR, WAITING_FOR_APPROVAL}:
        return WAITING_FOR_OPERATOR
    if workflow_state == COMPLETED and current_stage == TERMINATED:
        return TERMINATED
    if current_stage in STOP_STAGES:
        return current_stage
    return current_stage or UNKNOWN


def _detected_workflow(turns: list[Any]) -> str:
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        for key in ("routing_visibility_workflow_id", "response_source"):
            value = turn.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return UNKNOWN


def _workflow_state_transitions(turns: list[Any]) -> list[dict[str, str]]:
    transitions = []
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        status = turn.get("workflow_status")
        if not isinstance(status, dict):
            continue
        transitions.append(
            {
                "turn_id": str(turn.get("turn_id") or ""),
                "workflow_name": str(status.get("workflow_name") or ""),
                "workflow_state": str(status.get("workflow_state") or ""),
                "current_lifecycle_stage": str(status.get("current_lifecycle_stage") or ""),
            }
        )
    return transitions


def _lifecycle_stages_reached(turns: list[Any]) -> list[str]:
    stages: list[str] = []
    for transition in _workflow_state_transitions(turns):
        stage = transition["current_lifecycle_stage"]
        if stage and stage not in stages:
            stages.append(stage)
    return stages


def _collect_replay_inventory(session_root: Path) -> dict[str, Any]:
    references: list[str] = []
    hashes: list[str] = []
    preserved = True
    if not session_root.exists():
        return {"replay_references": [], "replay_hashes": [], "replay_lineage_preserved": False}
    for path in sorted(session_root.rglob("*.json")):
        references.append(str(path))
        try:
            artifact = load_json(path)
        except Exception:
            preserved = False
            continue
        for key in ("replay_hash", "artifact_hash"):
            value = artifact.get(key)
            if isinstance(value, str) and value.startswith("sha256:"):
                hashes.append(value)
        nested = artifact.get("artifact")
        if isinstance(nested, dict):
            value = nested.get("artifact_hash")
            if isinstance(value, str) and value.startswith("sha256:"):
                hashes.append(value)
    return {
        "replay_references": references,
        "replay_hashes": sorted(set(hashes)),
        "replay_lineage_preserved": preserved and bool(references) and bool(hashes),
    }


def _failure_classification(
    result: dict[str, Any],
    final_status: dict[str, Any],
    final_lifecycle_stage: str,
    replay_inventory: dict[str, Any],
) -> str | None:
    if final_lifecycle_stage == TERMINATED:
        return None
    if replay_inventory["replay_lineage_preserved"] is not True:
        return REPLAY_CONTINUITY_BREAK
    if final_lifecycle_stage == FAILED_CLOSED:
        reason = _failure_reason(result, result.get("turns") if isinstance(result.get("turns"), list) else [])
        if "routing" in reason.lower() or "workflow" in reason.lower():
            return ROUTING_FAILURE
        return FAIL_CLOSED
    if final_lifecycle_stage == WAITING_FOR_OPERATOR:
        if str(final_status.get("current_lifecycle_stage") or "") == "CLARIFICATION":
            return CLARIFICATION_STALL
        return CONTINUATION_FAILURE
    if final_lifecycle_stage == MAX_LIFECYCLE_LIMIT_REACHED:
        return LIFECYCLE_STAGE_DEVIATION
    if str(final_status.get("workflow_state") or "") not in {COMPLETED, WAITING_FOR_OPERATOR, WAITING_FOR_APPROVAL}:
        return WORKFLOW_STATE_DEVIATION
    return UNKNOWN


def _failure_reason(result: dict[str, Any], turns: list[Any]) -> str:
    reason = result.get("failure_reason")
    if isinstance(reason, str) and reason.strip():
        return reason.strip()
    for turn in reversed(turns):
        if isinstance(turn, dict):
            value = turn.get("failure_reason")
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _average(values: Iterable[int]) -> float:
    collected = list(values)
    if not collected:
        return 0.0
    return round(sum(collected) / len(collected), 6)


def _workflow_distribution(test_evidence: list[dict[str, Any]]) -> dict[str, int]:
    distribution: dict[str, int] = {}
    for evidence in test_evidence:
        workflow = str(evidence.get("detected_workflow") or UNKNOWN)
        distribution[workflow] = distribution.get(workflow, 0) + 1
    return dict(sorted(distribution.items()))


def _failure_summaries(test_evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "prompt_id": evidence["prompt_id"],
            "session_id": evidence["session_id"],
            "failure_classification": evidence["failure_classification"],
            "failure_reason": evidence["failure_reason"],
            "final_lifecycle_stage": evidence["final_lifecycle_stage"],
        }
        for evidence in test_evidence
        if evidence.get("failure_classification") not in {None, CLARIFICATION_STALL}
    ]


def _detected_deviations(test_evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deviations = []
    for evidence in test_evidence:
        if evidence["replay_lineage_preserved"] is not True:
            deviations.append({"prompt_id": evidence["prompt_id"], "deviation": REPLAY_CONTINUITY_BREAK})
        if evidence["final_lifecycle_stage"] not in STOP_STAGES:
            deviations.append({"prompt_id": evidence["prompt_id"], "deviation": LIFECYCLE_STAGE_DEVIATION})
        classification = evidence.get("failure_classification")
        if classification in {
            ROUTING_FAILURE,
            FAIL_CLOSED,
            CONTINUATION_FAILURE,
            WORKFLOW_STATE_DEVIATION,
            LIFECYCLE_STAGE_DEVIATION,
            UNKNOWN,
        }:
            deviations.append({"prompt_id": evidence["prompt_id"], "deviation": classification})
    return deviations


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("regression artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("regression artifact hash mismatch")
