"""Deterministic token and operator economics runtime for governed AiGOL adoption."""

from __future__ import annotations

from copy import deepcopy
from math import ceil
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_VERSION = "AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_V1"
ECONOMICS_REPORT_V1 = "ECONOMICS_REPORT_V1"
ECONOMICS_MEASUREMENT_COMPLETED = "ECONOMICS_MEASUREMENT_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "economics_inputs_recorded",
    "economics_report_recorded",
    "economics_report_returned",
)


def generate_token_and_operator_economics_report(
    *,
    report_id: str,
    generated_at: str,
    human_prompts: list[str],
    aigol_governance_actions: list[str],
    codex_requests: list[str],
    replay_artifacts: list[str],
    certification_artifacts: list[str],
    approval_actions: list[str],
    baseline_chatgpt_actions: list[str],
    replay_dir: str | Path,
    validation_artifacts: list[str] | None = None,
    measurement_prompt_authorized: bool = False,
) -> dict[str, Any]:
    """Generate deterministic proxy economics evidence without provider or worker execution."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        inputs = _inputs_artifact(
            report_id=report_id,
            generated_at=generated_at,
            human_prompts=human_prompts,
            aigol_governance_actions=aigol_governance_actions,
            codex_requests=codex_requests,
            replay_artifacts=replay_artifacts,
            certification_artifacts=certification_artifacts,
            approval_actions=approval_actions,
            baseline_chatgpt_actions=baseline_chatgpt_actions,
            validation_artifacts=validation_artifacts or [],
            measurement_prompt_authorized=measurement_prompt_authorized,
            measurement_status=ECONOMICS_MEASUREMENT_COMPLETED,
            failure_reason=None,
        )
        report = _economics_report(inputs)
        returned = _returned_artifact(report)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], inputs)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], report)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(report, returned, replay_path)
    except Exception as exc:
        inputs = _failed_inputs_artifact(
            report_id=report_id,
            generated_at=generated_at,
            failure_reason=_failure_reason(exc),
        )
        report = _failed_report(inputs)
        returned = _returned_artifact(report)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], inputs)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], report)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(report, returned, replay_path)


def reconstruct_token_and_operator_economics_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct economics replay and verify wrapper and artifact hashes."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("economics replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("economics replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    inputs = wrappers[0]["artifact"]
    report = wrappers[1]["artifact"]
    returned = wrappers[2]["artifact"]
    if report.get("source_inputs_hash") != inputs["artifact_hash"]:
        raise FailClosedRuntimeError("economics source inputs hash mismatch")
    if returned.get("economics_report_hash") != report["artifact_hash"]:
        raise FailClosedRuntimeError("economics returned report hash mismatch")

    return {
        "report_id": report["report_id"],
        "measurement_status": report["measurement_status"],
        "token_impact_measured": report["final_outputs"]["TOKEN_IMPACT_MEASURED"],
        "operator_effort_measured": report["final_outputs"]["OPERATOR_EFFORT_MEASURED"],
        "governance_overhead_measured": report["final_outputs"]["GOVERNANCE_OVERHEAD_MEASURED"],
        "roi_estimate_available": report["final_outputs"]["ROI_ESTIMATE_AVAILABLE"],
        "billable_roi_available": report["roi_estimate"]["billable_roi_available"],
        "replay_lineage_preserved": report["replay_lineage_preserved"],
        "fail_closed_preserved": report["fail_closed_preserved"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _inputs_artifact(
    *,
    report_id: str,
    generated_at: str,
    human_prompts: list[str],
    aigol_governance_actions: list[str],
    codex_requests: list[str],
    replay_artifacts: list[str],
    certification_artifacts: list[str],
    approval_actions: list[str],
    baseline_chatgpt_actions: list[str],
    validation_artifacts: list[str],
    measurement_prompt_authorized: bool,
    measurement_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    prompts = _require_string_list(human_prompts, "human_prompts")
    governance_actions = _require_string_list(aigol_governance_actions, "aigol_governance_actions")
    requests = _require_string_list(codex_requests, "codex_requests")
    replays = _require_string_list(replay_artifacts, "replay_artifacts")
    certifications = _require_string_list(certification_artifacts, "certification_artifacts")
    approvals = _require_string_list(approval_actions, "approval_actions")
    baseline_actions = _require_string_list(baseline_chatgpt_actions, "baseline_chatgpt_actions")
    validations = _optional_string_list(validation_artifacts, "validation_artifacts")
    if not isinstance(measurement_prompt_authorized, bool):
        raise FailClosedRuntimeError(
            "economics measurement failed closed: measurement_prompt_authorized must be boolean"
        )

    artifact = {
        "artifact_type": "ECONOMICS_INPUTS_ARTIFACT_V1",
        "runtime_version": AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_VERSION,
        "report_id": _require_string(report_id, "report_id"),
        "generated_at": _require_string(generated_at, "generated_at"),
        "measurement_status": measurement_status,
        "recorded_inputs": {
            "human_prompts": _hashed_items(prompts),
            "aigol_governance_actions": _hashed_items(governance_actions),
            "codex_requests": _hashed_items(requests),
            "replay_artifacts": _hashed_items(replays),
            "certification_artifacts": _hashed_items(certifications),
            "approval_actions": _hashed_items(approvals),
            "baseline_chatgpt_actions": _hashed_items(baseline_actions),
            "validation_artifacts": _hashed_items(validations),
        },
        "raw_counts": {
            "human_prompts": len(prompts),
            "aigol_governance_actions": len(governance_actions),
            "codex_requests": len(requests),
            "replay_artifacts": len(replays),
            "certification_artifacts": len(certifications),
            "approval_actions": len(approvals),
            "baseline_chatgpt_actions": len(baseline_actions),
            "validation_artifacts": len(validations),
        },
        "measurement_method": {
            "token_estimation": "DETERMINISTIC_PROXY_TOKENS_FROM_CANONICAL_JSON_CHARS_DIVIDED_BY_4",
            "operator_effort": "COUNTED_HUMAN_PROMPTS_CODEX_REQUESTS_AND_APPROVAL_ACTIONS",
            "governance_overhead": "COUNTED_AIGOL_ACTIONS_REPLAY_ARTIFACTS_CERTIFICATION_ARTIFACTS_AND_APPROVALS",
            "validation_artifact_scope": "VALIDATION_ARTIFACTS_ARE_RECORDED_BUT_NOT_COUNTED_AS_REPLAY_OVERHEAD",
            "measurement_authorization": "EXPLICIT_HUMAN_PROMPT_CAN_AUTHORIZE_MEASUREMENT_WITHOUT_DUPLICATE_APPROVAL",
            "billable_provider_telemetry_available": False,
        },
        "measurement_prompt_authorized": measurement_prompt_authorized,
        "governance_constraints": {
            "read_only_measurement": True,
            "provider_invocation_allowed": False,
            "worker_invocation_allowed": False,
            "code_modification_allowed": False,
            "governance_modification_allowed": False,
        },
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _economics_report(inputs: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(inputs)
    recorded = inputs["recorded_inputs"]
    baseline_sections = {
        "human_prompts": recorded["human_prompts"],
        "baseline_chatgpt_actions": recorded["baseline_chatgpt_actions"],
        "codex_requests": recorded["codex_requests"],
    }
    aigol_sections = {
        "human_prompts": recorded["human_prompts"],
        "aigol_governance_actions": recorded["aigol_governance_actions"],
        "codex_requests": recorded["codex_requests"],
        "replay_artifacts": recorded["replay_artifacts"],
        "certification_artifacts": recorded["certification_artifacts"],
        "approval_actions": recorded["approval_actions"],
        "validation_artifacts": recorded.get("validation_artifacts", []),
    }
    baseline_tokens = _estimate_tokens(baseline_sections)
    aigol_tokens = _estimate_tokens(aigol_sections)
    token_delta = aigol_tokens - baseline_tokens
    token_delta_percent = _ratio(token_delta, baseline_tokens)

    counts = inputs["raw_counts"]
    baseline_operator_actions = counts["human_prompts"] + counts["baseline_chatgpt_actions"] + counts["codex_requests"]
    aigol_operator_actions = counts["human_prompts"] + counts["approval_actions"] + counts["codex_requests"]
    operator_delta = aigol_operator_actions - baseline_operator_actions
    overhead_actions = (
        counts["aigol_governance_actions"]
        + counts["replay_artifacts"]
        + counts["certification_artifacts"]
        + counts["approval_actions"]
    )
    overhead_tokens = aigol_tokens - _estimate_tokens(
        {
            "human_prompts": recorded["human_prompts"],
            "codex_requests": recorded["codex_requests"],
        }
    )

    report = {
        "artifact_type": ECONOMICS_REPORT_V1,
        "runtime_version": AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_VERSION,
        "report_id": inputs["report_id"],
        "generated_at": inputs["generated_at"],
        "measurement_status": ECONOMICS_MEASUREMENT_COMPLETED,
        "source_inputs_hash": inputs["artifact_hash"],
        "workflows_compared": {
            "baseline": "Human -> ChatGPT -> Codex",
            "aigol": "Human -> AiGOL -> Codex -> Replay",
        },
        "estimated_token_consumption": {
            "baseline_estimated_tokens": baseline_tokens,
            "aigol_estimated_tokens": aigol_tokens,
            "delta_estimated_tokens": token_delta,
            "delta_percent": token_delta_percent,
            "measurement_basis": inputs["measurement_method"]["token_estimation"],
            "billable_provider_telemetry_available": False,
        },
        "operator_effort": {
            "baseline_operator_actions": baseline_operator_actions,
            "aigol_operator_actions": aigol_operator_actions,
            "approval_actions": counts["approval_actions"],
            "delta_operator_actions": operator_delta,
            "delta_percent": _ratio(operator_delta, baseline_operator_actions),
        },
        "governance_overhead": {
            "aigol_governance_actions": counts["aigol_governance_actions"],
            "replay_artifacts": counts["replay_artifacts"],
            "certification_artifacts": counts["certification_artifacts"],
            "approval_actions": counts["approval_actions"],
            "overhead_actions": overhead_actions,
            "overhead_estimated_tokens": overhead_tokens,
            "overhead_classification": _overhead_classification(overhead_actions),
            "validation_artifacts_recorded_outside_replay_overhead": counts.get("validation_artifacts", 0),
            "measurement_prompt_authorized": inputs.get("measurement_prompt_authorized", False),
        },
        "comparison": {
            "token_impact": _impact_label(token_delta, "TOKEN"),
            "operator_effort_impact": _impact_label(operator_delta, "OPERATOR_EFFORT"),
            "governance_overhead_impact": "MEASURED",
            "replay_traceability_impact": "IMPROVED",
            "certification_traceability_impact": "IMPROVED",
        },
        "roi_estimate": {
            "roi_estimate_available": True,
            "roi_estimate_type": "DETERMINISTIC_PROXY_ESTIMATE",
            "billable_roi_available": False,
            "rationale": (
                "Local deterministic accounting now measures relative token, operator, and governance "
                "overhead impact. Billable ROI still requires provider-side token and labor-time ledgers."
            ),
        },
        "measurement_limits": [
            "Estimated tokens are deterministic proxy tokens, not provider billable tokens.",
            "Operator effort is measured as action counts, not wall-clock labor time.",
            "Baseline ChatGPT evidence is recorded locally and cannot reconstruct historical provider telemetry.",
        ],
        "replay_references": {
            "source_inputs_hash": inputs["artifact_hash"],
            "replay_artifact_hashes": [item["item_hash"] for item in recorded["replay_artifacts"]],
            "certification_artifact_hashes": [item["item_hash"] for item in recorded["certification_artifacts"]],
        },
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "determinism_preserved": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "final_outputs": {
            "TOKEN_IMPACT_MEASURED": True,
            "OPERATOR_EFFORT_MEASURED": True,
            "GOVERNANCE_OVERHEAD_MEASURED": True,
            "ROI_ESTIMATE_AVAILABLE": True,
        },
        "failure_reason": None,
    }
    report["artifact_hash"] = replay_hash(report)
    return report


def _failed_inputs_artifact(*, report_id: str, generated_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ECONOMICS_INPUTS_ARTIFACT_V1",
        "runtime_version": AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_VERSION,
        "report_id": report_id if isinstance(report_id, str) and report_id.strip() else "INVALID",
        "generated_at": generated_at if isinstance(generated_at, str) and generated_at.strip() else "INVALID",
        "measurement_status": FAILED_CLOSED,
        "recorded_inputs": {},
        "raw_counts": {},
        "measurement_method": {},
        "governance_constraints": {
            "read_only_measurement": True,
            "provider_invocation_allowed": False,
            "worker_invocation_allowed": False,
            "code_modification_allowed": False,
            "governance_modification_allowed": False,
        },
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_report(inputs: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(inputs)
    report = {
        "artifact_type": ECONOMICS_REPORT_V1,
        "runtime_version": AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_VERSION,
        "report_id": inputs["report_id"],
        "generated_at": inputs["generated_at"],
        "measurement_status": FAILED_CLOSED,
        "source_inputs_hash": inputs["artifact_hash"],
        "workflows_compared": {
            "baseline": "Human -> ChatGPT -> Codex",
            "aigol": "Human -> AiGOL -> Codex -> Replay",
        },
        "estimated_token_consumption": {
            "baseline_estimated_tokens": 0,
            "aigol_estimated_tokens": 0,
            "delta_estimated_tokens": 0,
            "delta_percent": None,
            "measurement_basis": "NOT_MEASURED",
            "billable_provider_telemetry_available": False,
        },
        "operator_effort": {
            "baseline_operator_actions": 0,
            "aigol_operator_actions": 0,
            "approval_actions": 0,
            "delta_operator_actions": 0,
            "delta_percent": None,
        },
        "governance_overhead": {
            "aigol_governance_actions": 0,
            "replay_artifacts": 0,
            "certification_artifacts": 0,
            "approval_actions": 0,
            "overhead_actions": 0,
            "overhead_estimated_tokens": 0,
            "overhead_classification": FAILED_CLOSED,
        },
        "comparison": {
            "token_impact": FAILED_CLOSED,
            "operator_effort_impact": FAILED_CLOSED,
            "governance_overhead_impact": FAILED_CLOSED,
            "replay_traceability_impact": FAILED_CLOSED,
            "certification_traceability_impact": FAILED_CLOSED,
        },
        "roi_estimate": {
            "roi_estimate_available": False,
            "roi_estimate_type": "UNAVAILABLE_FAILED_CLOSED",
            "billable_roi_available": False,
            "rationale": "Economics measurement failed closed before comparable local evidence was available.",
        },
        "measurement_limits": ["Economics measurement failed closed."],
        "replay_references": {"source_inputs_hash": inputs["artifact_hash"]},
        "replay_lineage_preserved": False,
        "fail_closed_preserved": True,
        "determinism_preserved": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "final_outputs": {
            "TOKEN_IMPACT_MEASURED": False,
            "OPERATOR_EFFORT_MEASURED": False,
            "GOVERNANCE_OVERHEAD_MEASURED": False,
            "ROI_ESTIMATE_AVAILABLE": False,
        },
        "failure_reason": inputs["failure_reason"],
    }
    report["artifact_hash"] = replay_hash(report)
    return report


def _returned_artifact(report: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(report)
    artifact = {
        "event_type": "ECONOMICS_REPORT_RETURNED",
        "report_id": report["report_id"],
        "economics_report_hash": report["artifact_hash"],
        "measurement_status": report["measurement_status"],
        "final_outputs": deepcopy(report["final_outputs"]),
        "replay_lineage_preserved": report["replay_lineage_preserved"],
        "fail_closed_preserved": report["fail_closed_preserved"],
        "provider_invoked": False,
        "worker_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "failure_reason": report["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(report: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_VERSION,
        "measurement_status": report["measurement_status"],
        "economics_report": deepcopy(report),
        "economics_returned_artifact": deepcopy(returned),
        "economics_replay_reference": str(replay_path),
        "token_impact_measured": report["final_outputs"]["TOKEN_IMPACT_MEASURED"],
        "operator_effort_measured": report["final_outputs"]["OPERATOR_EFFORT_MEASURED"],
        "governance_overhead_measured": report["final_outputs"]["GOVERNANCE_OVERHEAD_MEASURED"],
        "roi_estimate_available": report["final_outputs"]["ROI_ESTIMATE_AVAILABLE"],
        "billable_roi_available": report["roi_estimate"]["billable_roi_available"],
        "replay_lineage_preserved": report["replay_lineage_preserved"],
        "fail_closed_preserved": report["fail_closed_preserved"],
        "failure_reason": report["failure_reason"],
    }
    capture["economics_capture_hash"] = replay_hash(capture)
    return capture


def _estimate_tokens(value: Any) -> int:
    return max(1, ceil(len(canonical_serialize(value)) / 4))


def _ratio(delta: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(delta / denominator, 6)


def _impact_label(delta: int, metric: str) -> str:
    if delta > 0:
        return f"{metric}_INCREASED"
    if delta < 0:
        return f"{metric}_DECREASED"
    return f"{metric}_UNCHANGED"


def _overhead_classification(overhead_actions: int) -> str:
    if overhead_actions <= 3:
        return "LOW"
    if overhead_actions <= 10:
        return "MODERATE"
    return "HIGH"


def _hashed_items(items: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "item_index": index,
            "item_hash": replay_hash(item),
            "estimated_tokens": _estimate_tokens(item),
            "text": item,
        }
        for index, item in enumerate(items)
    ]


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("economics measurement failed closed: replay already exists")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("economics artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("economics artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("economics replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("economics replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"economics measurement failed closed: {field_name} is required")
    return value.strip()


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"economics measurement failed closed: {field_name} must be a list")
    items = [_require_string(item, field_name) for item in value]
    if not items:
        raise FailClosedRuntimeError(f"economics measurement failed closed: {field_name} requires at least one item")
    return items


def _optional_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"economics measurement failed closed: {field_name} must be a list")
    return [_require_string(item, field_name) for item in value]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "economics measurement failed closed"
