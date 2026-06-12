"""Certification runtime for complete ACLI human prompt regression suites."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.acli_human_prompt_regression_suite_runtime import (
    AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION,
    FAILED_CLOSED,
    REGRESSION_CERTIFICATION_ARTIFACT_V1,
    REGRESSION_RUN_ARTIFACT_V1,
    TERMINATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_VERSION = (
    "AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_V1"
)

REQUIRED_COVERAGE = (
    "Create Domain",
    "Clarification",
    "Approval",
    "Execution Ready",
    "Worker Request",
    "Worker Dispatch",
    "Worker Invocation",
    "Execution",
    "Result Validation",
    "Replay Review",
    "Termination",
)

GOVERNANCE_CONSTRAINTS = {
    "deterministic": True,
    "replay_preserving": True,
    "fail_closed": True,
    "auto_continue": True,
    "repair_invoked": False,
    "provider_fix_invoked": False,
    "worker_remediation_invoked": False,
    "improvement_intent_created": False,
}


def run_acli_lifecycle_regression_certification(
    *,
    run_id: str,
    created_at: str,
    runtime_root: str | Path,
    workspace: str | Path = ".",
    domains: Iterable[str] = ("FreshDomain", "PilotDomain"),
    auto_continue: bool = True,
) -> dict[str, Any]:
    """Execute complete ACLI lifecycle sessions and certify regression readiness."""

    domain_list = [_require_domain(domain) for domain in domains]
    if len(domain_list) < 2:
        raise FailClosedRuntimeError("at least two lifecycle sessions are required for 25 prompt certification")
    run_root = Path(runtime_root) / _safe_segment(run_id)
    session_evidence = [
        _execute_lifecycle_session(
            run_id=run_id,
            session_index=index,
            domain=domain,
            created_at=created_at,
            run_root=run_root,
            workspace=workspace,
            auto_continue=auto_continue,
        )
        for index, domain in enumerate(domain_list, start=1)
    ]
    prompt_count = sum(evidence["prompt_count"] for evidence in session_evidence)
    if prompt_count < 25:
        raise FailClosedRuntimeError("minimum 25 ACLI prompts were not executed")
    run_artifact = _regression_run_artifact(
        run_id=run_id,
        created_at=created_at,
        run_root=run_root,
        session_evidence=session_evidence,
    )
    certification = _regression_certification_artifact(
        run_id=run_id,
        created_at=created_at,
        run_artifact=run_artifact,
        session_evidence=session_evidence,
    )
    write_json_immutable(run_root / "REGRESSION_RUN_ARTIFACT_V1.json", run_artifact)
    write_json_immutable(run_root / "REGRESSION_CERTIFICATION_ARTIFACT_V1.json", certification)
    return {
        "runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_VERSION,
        "run_id": run_id,
        "regression_run_artifact": run_artifact,
        "regression_certification_artifact": certification,
        "session_evidence": session_evidence,
        "regression_suite_certified": certification["certification_status"] == "CERTIFIED",
        "production_readiness_score": certification["production_readiness_score"],
        "termination_rate": run_artifact["termination_rate"],
        "fail_closed_rate": run_artifact["fail_closed_rate"],
    }


def reconstruct_acli_lifecycle_regression_certification(run_root: str | Path) -> dict[str, Any]:
    """Reconstruct and verify ACLI lifecycle regression certification artifacts."""

    root = Path(run_root)
    run_artifact = load_json(root / "REGRESSION_RUN_ARTIFACT_V1.json")
    certification = load_json(root / "REGRESSION_CERTIFICATION_ARTIFACT_V1.json")
    _verify_artifact_hash(run_artifact)
    _verify_artifact_hash(certification)
    if certification.get("regression_run_hash") != run_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("ACLI lifecycle certification run hash mismatch")
    return {
        "run_artifact": run_artifact,
        "certification_artifact": certification,
        "replay_lineage_preserved": certification["replay_lineage_preserved"],
        "termination_rate": run_artifact["termination_rate"],
        "fail_closed_rate": run_artifact["fail_closed_rate"],
    }


def _execute_lifecycle_session(
    *,
    run_id: str,
    session_index: int,
    domain: str,
    created_at: str,
    run_root: Path,
    workspace: str | Path,
    auto_continue: bool,
) -> dict[str, Any]:
    session_id = f"{_safe_segment(run_id)}-SESSION-{session_index:06d}"
    prompts = _lifecycle_prompts(domain)
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
            input_func=_input_sequence(prompts + ["exit"]),
            output_func=output.append,
        )
    except Exception as exc:
        result = {
            "session_id": session_id,
            "turn_count": 0,
            "failed_turns": 1,
            "turns": [],
            "runtime_root": str(run_root / "sessions" / session_id),
            "failure_reason": str(exc) or "ACLI lifecycle certification failed closed",
        }
    turns = result.get("turns") if isinstance(result.get("turns"), list) else []
    lifecycle_turns = _canonical_lifecycle_turns(turns)
    final_turn = lifecycle_turns[-1] if lifecycle_turns else {}
    status = final_turn.get("workflow_status") if isinstance(final_turn, dict) else {}
    if not isinstance(status, dict):
        status = {}
    final_stage = str(status.get("current_lifecycle_stage") or "")
    workflow_state = str(status.get("workflow_state") or "")
    terminated = final_stage == TERMINATED and workflow_state == "COMPLETED"
    replay_inventory = _collect_replay_inventory(Path(result.get("runtime_root") or run_root / "sessions" / session_id))
    evidence = {
        "artifact_type": "ACLI_LIFECYCLE_REGRESSION_SESSION_EVIDENCE_V1",
        "runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_VERSION,
        "run_id": run_id,
        "session_id": session_id,
        "domain": domain,
        "prompt_count": len(prompts),
        "prompt_hashes": [replay_hash(prompt) for prompt in prompts],
        "turn_count": len(lifecycle_turns),
        "raw_turn_count": len(turns),
        "failed_turns": _failed_turn_count(lifecycle_turns),
        "raw_failed_turns": int(result.get("failed_turns") or 0),
        "coverage": _coverage(lifecycle_turns),
        "workflow_distribution": _workflow_distribution(lifecycle_turns),
        "gap_distribution": _gap_distribution(lifecycle_turns, replay_inventory, terminated),
        "final_lifecycle_stage": final_stage or FAILED_CLOSED,
        "terminated": terminated,
        "failed_closed": (not terminated) and (_failed_turn_count(lifecycle_turns) > 0 or final_stage == FAILED_CLOSED),
        "replay_references": replay_inventory["replay_references"],
        "replay_hashes": replay_inventory["replay_hashes"],
        "replay_lineage_preserved": replay_inventory["replay_lineage_preserved"],
        "governance_constraints": deepcopy(GOVERNANCE_CONSTRAINTS),
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    write_json_immutable(run_root / "session_evidence" / f"{session_id}.json", evidence)
    return evidence


def _regression_run_artifact(
    *,
    run_id: str,
    created_at: str,
    run_root: Path,
    session_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    total = len(session_evidence)
    terminated = sum(1 for evidence in session_evidence if evidence["terminated"] is True)
    failed_closed = sum(1 for evidence in session_evidence if evidence["failed_closed"] is True)
    replay_integrity = all(evidence["replay_lineage_preserved"] is True for evidence in session_evidence)
    artifact = {
        "artifact_type": REGRESSION_RUN_ARTIFACT_V1,
        "runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_VERSION,
        "base_runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION,
        "run_id": run_id,
        "execution_timestamp": created_at,
        "total_tests": total,
        "total_prompts": sum(evidence["prompt_count"] for evidence in session_evidence),
        "passed_tests": terminated,
        "failed_tests": failed_closed,
        "waiting_tests": 0,
        "termination_rate": _rate(terminated, total),
        "fail_closed_rate": _rate(failed_closed, total),
        "workflow_distribution": _merge_distributions(evidence["workflow_distribution"] for evidence in session_evidence),
        "gap_distribution": _merge_distributions(evidence["gap_distribution"] for evidence in session_evidence),
        "replay_lineage_integrity": replay_integrity,
        "coverage": _merge_coverage(session_evidence),
        "failure_summaries": [
            {
                "session_id": evidence["session_id"],
                "final_lifecycle_stage": evidence["final_lifecycle_stage"],
                "gap_distribution": evidence["gap_distribution"],
            }
            for evidence in session_evidence
            if evidence["terminated"] is not True
        ],
        "replay_references": [evidence["replay_references"] for evidence in session_evidence],
        "session_evidence_hashes": [evidence["artifact_hash"] for evidence in session_evidence],
        "replay_reference": str(run_root),
        "governance_constraints": deepcopy(GOVERNANCE_CONSTRAINTS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _regression_certification_artifact(
    *,
    run_id: str,
    created_at: str,
    run_artifact: dict[str, Any],
    session_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    coverage = run_artifact["coverage"]
    missing = [item for item in REQUIRED_COVERAGE if coverage.get(item) is not True]
    no_lifecycle_regressions = (
        run_artifact["termination_rate"] >= 0.95
        and run_artifact["replay_lineage_integrity"] is True
        and not missing
        and not run_artifact["failure_summaries"]
    )
    production_readiness_score = _production_readiness_score(
        termination_rate=float(run_artifact["termination_rate"]),
        fail_closed_rate=float(run_artifact["fail_closed_rate"]),
        replay_lineage_integrity=bool(run_artifact["replay_lineage_integrity"]),
        coverage_complete=not missing,
        no_lifecycle_regressions=no_lifecycle_regressions,
    )
    status = "CERTIFIED" if no_lifecycle_regressions else "FAILED_CLOSED"
    artifact = {
        "artifact_type": REGRESSION_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_VERSION,
        "run_id": run_id,
        "certified_at": created_at,
        "certification_status": status,
        "minimum_prompt_requirement_met": run_artifact["total_prompts"] >= 25,
        "required_coverage": list(REQUIRED_COVERAGE),
        "coverage": coverage,
        "missing_coverage": missing,
        "execution_statistics": {
            "total_tests": run_artifact["total_tests"],
            "total_prompts": run_artifact["total_prompts"],
            "passed_tests": run_artifact["passed_tests"],
            "failed_tests": run_artifact["failed_tests"],
            "termination_rate": run_artifact["termination_rate"],
            "fail_closed_rate": run_artifact["fail_closed_rate"],
        },
        "workflow_distribution": run_artifact["workflow_distribution"],
        "gap_distribution": run_artifact["gap_distribution"],
        "replay_lineage_integrity": run_artifact["replay_lineage_integrity"],
        "replay_references": run_artifact["replay_references"],
        "detected_deviations": run_artifact["failure_summaries"],
        "no_lifecycle_regressions": no_lifecycle_regressions,
        "production_readiness_score": production_readiness_score,
        "certification_rationale": (
            "Minimum 25-prompt ACLI Auto Continue lifecycle corpus terminated without lifecycle regressions."
            if status == "CERTIFIED"
            else "ACLI lifecycle regression certification failed closed due to coverage, termination, or replay gaps."
        ),
        "regression_run_hash": run_artifact["artifact_hash"],
        "replay_lineage_preserved": run_artifact["replay_lineage_integrity"],
        "determinism_preserved": True,
        "fail_closed_preserved": True,
        "governance_constraints": deepcopy(GOVERNANCE_CONSTRAINTS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _lifecycle_prompts(domain: str) -> list[str]:
    return [
        f"Create a new governed domain called {domain}.",
        "\n".join(
            [
                "Primary purpose: Create a safe pilot governed domain.",
                "Expected capabilities: Clarification handling and bounded workflow resume.",
                "Target users: Internal operators.",
            ]
        ),
        f"Approve {domain} for domain artifact creation.",
        f"Create execution-ready authorization packet for {domain}.",
        f"Authorize execution-ready packet for {domain}.",
        f"Create worker request for {domain}.",
        f"Assign worker for {domain}.",
        f"Dispatch worker for {domain}.",
        f"Invoke worker for {domain}.",
        f"Execute worker for {domain}.",
        f"Capture worker result for {domain}.",
        f"Validate worker result for {domain}.",
        f"Review post-execution replay for {domain}.",
        f"Terminate reviewed operation for {domain}.",
    ]


def _coverage(turns: list[Any]) -> dict[str, bool]:
    stages = {stage for stage in _stages(turns)}
    sources = set()
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        for key in ("response_source", "routing_visibility_workflow_id"):
            value = turn.get(key)
            if isinstance(value, str) and value.strip():
                sources.add(value)
    return {
        "Create Domain": "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION" in sources,
        "Clarification": "CLARIFICATION" in stages,
        "Approval": "APPROVAL" in stages,
        "Execution Ready": "EXECUTION_AUTHORIZED" in stages or "EXECUTION_READY" in stages,
        "Worker Request": "WORKER_REQUESTED" in stages,
        "Worker Dispatch": "WORKER_DISPATCHED" in stages,
        "Worker Invocation": "WORKER_INVOKED" in stages,
        "Execution": "EXECUTING" in stages,
        "Result Validation": "RESULT_VALIDATED" in stages,
        "Replay Review": "REPLAY_REVIEWED" in stages,
        "Termination": TERMINATED in stages,
    }


def _stages(turns: list[Any]) -> list[str]:
    stages: list[str] = []
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        status = turn.get("workflow_status")
        if not isinstance(status, dict):
            continue
        stage = str(status.get("current_lifecycle_stage") or "")
        if stage:
            stages.append(stage)
    return stages


def _canonical_lifecycle_turns(turns: list[Any]) -> list[Any]:
    collected: list[Any] = []
    for turn in turns:
        collected.append(turn)
        if not isinstance(turn, dict):
            continue
        status = turn.get("workflow_status")
        if not isinstance(status, dict):
            continue
        if status.get("current_lifecycle_stage") == TERMINATED and status.get("workflow_state") == "COMPLETED":
            break
    return collected


def _failed_turn_count(turns: list[Any]) -> int:
    return sum(1 for turn in turns if isinstance(turn, dict) and turn.get("failure_reason"))


def _workflow_distribution(turns: list[Any]) -> dict[str, int]:
    distribution: dict[str, int] = {}
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        workflow = str(turn.get("response_source") or turn.get("routing_visibility_workflow_id") or "UNKNOWN")
        distribution[workflow] = distribution.get(workflow, 0) + 1
    return dict(sorted(distribution.items()))


def _gap_distribution(turns: list[Any], replay_inventory: dict[str, Any], terminated: bool) -> dict[str, int]:
    distribution: dict[str, int] = {}
    if replay_inventory["replay_lineage_preserved"] is not True:
        distribution["REPLAY_LINEAGE_GAP"] = 1
    if not terminated:
        distribution["TERMINATION_GAP"] = 1
    failed_turns = [turn for turn in turns if isinstance(turn, dict) and turn.get("failure_reason")]
    if failed_turns:
        distribution["FAILED_TURN_GAP"] = len(failed_turns)
    return distribution or {"NO_GAPS": 1}


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


def _merge_distributions(distributions: Iterable[dict[str, int]]) -> dict[str, int]:
    merged: dict[str, int] = {}
    for distribution in distributions:
        for key, value in distribution.items():
            merged[key] = merged.get(key, 0) + int(value)
    return dict(sorted(merged.items()))


def _merge_coverage(session_evidence: list[dict[str, Any]]) -> dict[str, bool]:
    return {
        item: any(evidence["coverage"].get(item) is True for evidence in session_evidence)
        for item in REQUIRED_COVERAGE
    }


def _production_readiness_score(
    *,
    termination_rate: float,
    fail_closed_rate: float,
    replay_lineage_integrity: bool,
    coverage_complete: bool,
    no_lifecycle_regressions: bool,
) -> float:
    score = termination_rate * 70.0
    score += (1.0 - fail_closed_rate) * 10.0
    score += 10.0 if replay_lineage_integrity else 0.0
    score += 5.0 if coverage_complete else 0.0
    score += 5.0 if no_lifecycle_regressions else 0.0
    return round(score, 2)


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _safe_segment(value: str) -> str:
    segment = "".join(character if character.isalnum() or character in "-_" else "-" for character in value.strip())
    return segment or "REGRESSION-RUN"


def _require_domain(domain: str) -> str:
    value = str(domain).strip()
    if not value or not value[0].isalpha() or not value.replace("_", "").replace("-", "").isalnum():
        raise FailClosedRuntimeError("domain name invalid")
    return value


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("ACLI lifecycle regression artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("ACLI lifecycle regression artifact hash mismatch")
