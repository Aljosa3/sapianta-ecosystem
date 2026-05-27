"""Minimal CLI surface for live cognition rejection analysis."""

from __future__ import annotations

import argparse
from typing import Any

from aigol.runtime.live_cognition_rejection_analysis import (
    ANALYSIS_MODE,
    LiveCognitionRejectionAnalysisEvidence,
    analyze_live_cognition_rejection,
    render_rejection_analysis_summary,
)
from aigol.runtime.live_runtime_usage_validation import validate_live_runtime_usage
from aigol.runtime.models import FailClosedRuntimeError


DEFAULT_CREATED_AT = "1970-01-01T00:00:00+00:00"
DEFAULT_ANALYSIS_ID = "LIVE-COGNITION-REJECTION-ANALYSIS-1"
DEFAULT_OPERATOR_PROMPT_LIMIT_SECONDS = 20


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def run_live_cognition_rejection_analysis_cli(
    *,
    analysis_id: str,
    operator_prompt: str,
    created_at: str,
    timeout_seconds: int = DEFAULT_OPERATOR_PROMPT_LIMIT_SECONDS,
) -> dict[str, Any]:
    """Drive one prompt through the live runtime validator and inspect the rejection."""

    try:
        _require_string(analysis_id, "analysis_id")
        normalized_prompt = " ".join(_require_string(operator_prompt, "operator_prompt").split())
        _require_string(created_at, "created_at")
        usage_validation = validate_live_runtime_usage(
            validation_id=f"{analysis_id}:USAGE_VALIDATION",
            human_prompts=[normalized_prompt],
            created_at=created_at,
            timeout_seconds=timeout_seconds,
        )
        usage_records = usage_validation.get("usage_records", [])
        usage_record = usage_records[0] if usage_records else None
        analysis = analyze_live_cognition_rejection(
            analysis_id=analysis_id,
            usage_record=usage_record,
            created_at=created_at,
        )
        evidence = analysis["analysis_evidence"]
        return {
            "analysis": analysis,
            "rendered_output": render_rejection_analysis_summary(evidence),
            "exit_code": 0 if evidence.rejection_stage == "NONE" else 1,
            "analysis_mode": ANALYSIS_MODE,
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        analysis = analyze_live_cognition_rejection(
            analysis_id=analysis_id if isinstance(analysis_id, str) and analysis_id else "ANALYSIS-INVALID",
            usage_record=None,
            created_at=created_at if isinstance(created_at, str) and created_at else DEFAULT_CREATED_AT,
        )
        evidence = analysis["analysis_evidence"]
        return {
            "analysis": analysis,
            "rendered_output": render_rejection_analysis_summary(evidence),
            "exit_code": 1,
            "analysis_mode": ANALYSIS_MODE,
            "governance_authority_separated": True,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m aigol.runtime.live_cognition_rejection_analysis_cli",
        description="Readonly inspection of why a live governed cognition request was rejected.",
    )
    parser.add_argument("prompt")
    parser.add_argument("--analysis-id", default=DEFAULT_ANALYSIS_ID)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_OPERATOR_PROMPT_LIMIT_SECONDS)
    args = parser.parse_args(argv)
    result = run_live_cognition_rejection_analysis_cli(
        analysis_id=args.analysis_id,
        operator_prompt=args.prompt,
        created_at=args.created_at,
        timeout_seconds=args.timeout_seconds,
    )
    print(result["rendered_output"])
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
