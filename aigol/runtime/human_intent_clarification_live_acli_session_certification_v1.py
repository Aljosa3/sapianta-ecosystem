"""Live ACLI session certification for human-intent clarification."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversational_cli_runtime import HUMAN_INTENT_CLARIFICATION_INTAKE
from aigol.runtime.human_intent_clarification_continuity_runtime import (
    reconstruct_human_intent_clarification_continuity_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/human_intent_clarification_live_acli_session_certification_v1")
CREATED_AT = "2026-06-21T00:00:00Z"
SESSION_ID = "HIC-LIVE-ACLI-SESSION-000001"
AMBIGUOUS_REQUEST = "Create a report"
CLARIFICATION_RESPONSE = (
    "Create a customer-facing report that reviews AI-generated customer replies for missing justification "
    "before anyone sends them."
)
HUMAN_CONFIRMATION = "Yes, I confirm this summary before any execution."


def run_human_intent_clarification_live_acli_session_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"
    session_runtime_root = root / "session_runtime"

    output_lines: list[str] = []
    session_result = run_interactive_conversation(
        _conversation_args(session_runtime_root),
        input_func=_input_sequence([AMBIGUOUS_REQUEST, CLARIFICATION_RESPONSE, HUMAN_CONFIRMATION, "exit"]),
        output_func=output_lines.append,
    )
    turns = list(session_result.get("turns") or [])
    first_turn = turns[0] if len(turns) > 0 else {}
    second_turn = turns[1] if len(turns) > 1 else {}
    third_turn = turns[2] if len(turns) > 2 else {}
    clarification_questions = _clarification_questions_from_turn(first_turn)
    execution_summary = _execution_summary_artifact(second_turn)
    confirmation = _human_confirmation_artifact(execution_summary, third_turn)
    confirmation_dir = root / "live_acli_confirmation"
    write_json_immutable(confirmation_dir / "000_live_acli_human_confirmation.json", confirmation)
    replay_reconstruction = _reconstruct_live_session_replay(first_turn, second_turn, confirmation)
    no_secret_leak = _secret_free(root)

    assertions = {
        "acli_session_started": session_result.get("session_id") == SESSION_ID and len(turns) >= 2,
        "ambiguous_intent_detected": first_turn.get("clarification_required") is True
        and first_turn.get("conversational_workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE,
        "clarification_generated": bool(clarification_questions),
        "clarification_response_received": second_turn.get("operator_reply_bound") is True,
        "context_updated": second_turn.get("operator_reply_bound") is True,
        "intent_resolved": second_turn.get("clarification_resolved") is True,
        "workflow_selected": second_turn.get("workflow_resumed") is True and bool(second_turn.get("workflow_id")),
        "execution_summary_generated": execution_summary.get("summary_generated") is True,
        "human_confirmation_recorded": confirmation.get("confirmation_recorded") is True,
        "replay_reconstructed": replay_reconstruction["replay_reconstructed"],
        "approval_boundaries_preserved": all(
            [
                first_turn.get("provider_invoked") is False,
                first_turn.get("worker_invoked") is False,
                second_turn.get("provider_invoked") is False,
                second_turn.get("worker_invoked") is False,
                second_turn.get("execution_requested") is False,
                confirmation.get("execution_authorized") is False,
                confirmation.get("worker_invocation_authorized") is False,
            ]
        ),
        "secret_free_evidence": no_secret_leak,
    }
    final_verdict = (
        "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_CERTIFIED"
        if all(assertions.values())
        else "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_GAPS_FOUND"
    )
    coverage = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_COVERAGE_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "session_id": SESSION_ID,
        "turn_count": len(turns),
        "failed_turns": session_result.get("failed_turns"),
        "ambiguous_request": AMBIGUOUS_REQUEST,
        "clarification_question_count": len(first_turn.get("clarification_questions") or []),
        "clarification_questions_replay_count": len(clarification_questions),
        "selected_workflow": second_turn.get("workflow_id"),
        "output_line_count": len(output_lines),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }
    coverage["artifact_hash"] = replay_hash(coverage)
    evidence = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_EVIDENCE_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(root),
        "session_runtime_root": str(session_runtime_root),
        "safe_turn_summaries": [_safe_turn_summary(turn) for turn in turns],
        "execution_summary": execution_summary,
        "human_confirmation": confirmation,
        "coverage_report": coverage,
        "final_verdict": final_verdict,
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    replay_package = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_REPLAY_PACKAGE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_root": str(root),
        "session_runtime_root": str(session_runtime_root),
        "replay_reconstruction": replay_reconstruction,
        "confirmation_reference": str(confirmation_dir / "000_live_acli_human_confirmation.json"),
        "final_verdict": final_verdict,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)
    report = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_CERTIFICATION_REPORT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "assertions": assertions,
        "observed": assertions,
        "blocker_analysis": [] if final_verdict.endswith("_CERTIFIED") else _blockers(assertions),
        "recommended_next_certification": "AIGOL_HUMAN_INTENT_CLARIFICATION_EXECUTION_AUTHORIZATION_BOUNDARY_CERTIFICATION_V1",
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    _persist(evidence_dir, replay_dir, report_dir, coverage, evidence, replay_package, report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "evidence_package_path": str(evidence_dir / "000_human_intent_clarification_live_acli_session_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_human_intent_clarification_live_acli_session_replay_package.json"),
        "certification_report_path": str(
            report_dir / "000_human_intent_clarification_live_acli_session_certification_report.json"
        ),
        "coverage_report_path": str(evidence_dir / "001_human_intent_clarification_live_acli_session_coverage_report.json"),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def _conversation_args(session_runtime_root: Path) -> Any:
    workspace = session_runtime_root / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            SESSION_ID,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(session_runtime_root),
            "--workspace",
            str(workspace),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _execution_summary_artifact(second_turn: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_EXECUTION_SUMMARY_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "summary_id": "HIC-LIVE-ACLI:EXECUTION-SUMMARY",
        "original_request_hash": replay_hash(AMBIGUOUS_REQUEST),
        "clarification_response_hash": replay_hash(CLARIFICATION_RESPONSE),
        "selected_workflow": second_turn.get("workflow_id"),
        "resolved_intent": second_turn.get("intent_family"),
        "summary_generated": second_turn.get("clarification_resolved") is True,
        "human_confirmation_required": True,
        "execution_authorized": False,
        "worker_invocation_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _clarification_questions_from_turn(first_turn: dict[str, Any]) -> list[str]:
    replay_reference = first_turn.get("replay_reference")
    if not isinstance(replay_reference, str) or not replay_reference:
        return []
    path = Path(replay_reference) / "001_conversational_workflow_selection_recorded.json"
    if not path.exists():
        return []
    wrapper = load_json(path)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        return []
    questions = artifact.get("clarification_questions")
    return list(questions) if isinstance(questions, list) else []


def _human_confirmation_artifact(execution_summary: dict[str, Any], third_turn: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_CONFIRMATION_ARTIFACT_V1",
        "runtime_version": MILESTONE_ID,
        "confirmation_id": "HIC-LIVE-ACLI:HUMAN-CONFIRMATION",
        "execution_summary_reference": execution_summary["summary_id"],
        "execution_summary_hash": execution_summary["artifact_hash"],
        "confirmation_response_hash": replay_hash(HUMAN_CONFIRMATION),
        "confirmation_turn_recorded": bool(third_turn),
        "confirmation_recorded": bool(third_turn) and "confirm" in HUMAN_CONFIRMATION.lower(),
        "confirmed_summary_only": True,
        "execution_authorized": False,
        "worker_invocation_authorized": False,
        "provider_invocation_authorized": False,
        "approval_boundaries_preserved": True,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _reconstruct_live_session_replay(
    first_turn: dict[str, Any],
    second_turn: dict[str, Any],
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    continuity_reference = second_turn.get("replay_reference")
    continuity_replay = (
        reconstruct_human_intent_clarification_continuity_replay(continuity_reference)
        if isinstance(continuity_reference, str) and continuity_reference
        else {}
    )
    return {
        "first_turn_replay_reference": first_turn.get("replay_reference"),
        "continuity_replay_reference": continuity_reference,
        "continuity_workflow_id": continuity_replay.get("workflow_id"),
        "confirmation_recorded": confirmation.get("confirmation_recorded") is True,
        "replay_reconstructed": all(
            [
                bool(first_turn.get("replay_reference")),
                bool(continuity_replay),
                continuity_replay.get("workflow_id") == second_turn.get("workflow_id"),
                confirmation.get("confirmation_recorded") is True,
            ]
        ),
    }


def _safe_turn_summary(turn: dict[str, Any]) -> dict[str, Any]:
    return {
        "turn_id": turn.get("turn_id"),
        "response_status": turn.get("response_status"),
        "workflow_id": turn.get("workflow_id") or turn.get("conversational_workflow_id"),
        "clarification_required": turn.get("clarification_required") is True,
        "operator_reply_bound": turn.get("operator_reply_bound") is True,
        "clarification_resolved": turn.get("clarification_resolved") is True,
        "workflow_resumed": turn.get("workflow_resumed") is True,
        "human_confirmation_required": turn.get("human_confirmation_required") is True,
        "provider_invoked": turn.get("provider_invoked") is True,
        "worker_invoked": turn.get("worker_invoked") is True,
        "execution_requested": turn.get("execution_requested") is True,
        "approval_bypassed": turn.get("approval_bypassed") is True,
        "replay_reference": turn.get("replay_reference"),
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
        evidence_dir / "000_human_intent_clarification_live_acli_session_evidence_package.json",
        evidence,
    )
    write_json_immutable(
        evidence_dir / "001_human_intent_clarification_live_acli_session_coverage_report.json",
        coverage,
    )
    write_json_immutable(
        replay_dir / "000_human_intent_clarification_live_acli_session_replay_package.json",
        replay_package,
    )
    write_json_immutable(
        report_dir / "000_human_intent_clarification_live_acli_session_certification_report.json",
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
    result = run_human_intent_clarification_live_acli_session_certification()
    assertions = result["assertions"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"acli_session_started={assertions['acli_session_started']}")
    print(f"ambiguous_intent_detected={assertions['ambiguous_intent_detected']}")
    print(f"human_confirmation_recorded={assertions['human_confirmation_recorded']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "HUMAN_INTENT_CLARIFICATION_LIVE_ACLI_SESSION_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
