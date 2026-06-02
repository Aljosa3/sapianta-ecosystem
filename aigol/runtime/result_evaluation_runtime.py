"""Replay-visible Result Evaluation Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.result_runtime import RESULT_ARTIFACT_V1, RESULT_CAPTURED
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


RESULT_EVALUATION_RUNTIME_VERSION = "RESULT_EVALUATION_RUNTIME_V1"
RESULT_EVALUATION_ARTIFACT_V1 = "RESULT_EVALUATION_ARTIFACT_V1"
EVALUATED = "EVALUATED"
RESULT_EVALUATION_RECORDED = "RESULT_EVALUATION_RECORDED"
RESULT_EVALUATION_RETURNED = "RESULT_EVALUATION_RETURNED"

REPLAY_STEPS = ("result_evaluation_recorded", "result_evaluation_returned")
ALLOWED_EVALUATION_SOURCES = frozenset(
    {
        "AIGOL_DETERMINISTIC",
        "HUMAN_OBSERVATION",
        "WORKER_REPORT",
        "PROVIDER_ASSISTED_NON_AUTHORITATIVE",
        "COMBINED_NON_AUTHORITATIVE",
    }
)
FORBIDDEN_OBSERVATION_FIELDS = frozenset(
    {
        "approval_transition",
        "result_approval",
        "result_certification",
        "governance_mutation",
        "direct_worker_dispatch",
        "direct_execution_request",
        "replay_repair",
        "self_improvement",
        "implementation_plan",
        "self_apply",
        "provider_command",
        "credentials",
        "api_key",
        "secret",
    }
)


def evaluate_result(
    *,
    evaluation_id: str,
    result_artifact: dict[str, Any],
    canonical_chain_id: str,
    evaluator_reference: str,
    evaluation_source: str,
    evaluation_method: str,
    evaluation_observations: dict[str, Any],
    improvement_recommended: bool,
    improvement_proposal_reference: str | None,
    evaluated_by: str,
    evaluated_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Evaluate a captured result without approving or applying improvements."""

    replay_path = Path(replay_dir)
    _ensure_evaluation_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    result = _validate_result_artifact(result_artifact, chain_id)
    observations = _validate_observations(evaluation_observations)
    evaluation = _evaluation_artifact(
        evaluation_id=evaluation_id,
        result=result,
        canonical_chain_id=chain_id,
        evaluator_reference=evaluator_reference,
        evaluation_source=evaluation_source,
        evaluation_method=evaluation_method,
        evaluation_observations=observations,
        improvement_recommended=improvement_recommended,
        improvement_proposal_reference=improvement_proposal_reference,
        evaluated_by=evaluated_by,
        evaluated_at=evaluated_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], evaluation)
    returned = _evaluation_returned(evaluation)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(evaluation, returned)


def reconstruct_result_evaluation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Result Evaluation Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("result evaluation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("result evaluation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "result evaluation artifact")
        wrappers.append(wrapper)

    evaluation = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("evaluation_reference") != evaluation["evaluation_id"]:
        raise FailClosedRuntimeError("result evaluation replay reference mismatch")
    if returned.get("evaluation_hash") != evaluation["artifact_hash"]:
        raise FailClosedRuntimeError("result evaluation replay hash mismatch")
    if returned.get("canonical_chain_id") != evaluation["canonical_chain_id"]:
        raise FailClosedRuntimeError("result evaluation replay chain mismatch")
    if returned.get("result_reference") != evaluation["result_reference"]:
        raise FailClosedRuntimeError("result evaluation replay result reference mismatch")
    if returned.get("result_hash") != evaluation["result_hash"]:
        raise FailClosedRuntimeError("result evaluation replay result hash mismatch")
    _validate_evaluation_artifact(evaluation)
    return {
        "evaluation_id": evaluation["evaluation_id"],
        "canonical_chain_id": evaluation["canonical_chain_id"],
        "result_reference": evaluation["result_reference"],
        "result_hash": evaluation["result_hash"],
        "worker_reference": evaluation["worker_reference"],
        "evaluation_source": evaluation["evaluation_source"],
        "evaluation_method": evaluation["evaluation_method"],
        "evaluation_status": evaluation["evaluation_status"],
        "improvement_recommended": evaluation["improvement_recommended"],
        "improvement_proposal_reference": evaluation["improvement_proposal_reference"],
        "evaluated_at": evaluation["evaluated_at"],
        "approval_authority": False,
        "result_approved": False,
        "result_certified": False,
        "implementation_plan_created": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _evaluation_artifact(
    *,
    evaluation_id: str,
    result: dict[str, Any],
    canonical_chain_id: str,
    evaluator_reference: str,
    evaluation_source: str,
    evaluation_method: str,
    evaluation_observations: dict[str, Any],
    improvement_recommended: bool,
    improvement_proposal_reference: str | None,
    evaluated_by: str,
    evaluated_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    source = _normalize_token(evaluation_source, "evaluation_source")
    if source not in ALLOWED_EVALUATION_SOURCES:
        raise FailClosedRuntimeError("result evaluation failed closed: invalid evaluation source")
    if not isinstance(improvement_recommended, bool):
        raise FailClosedRuntimeError("result evaluation failed closed: improvement recommendation must be boolean")
    if improvement_proposal_reference is not None:
        raise FailClosedRuntimeError("result evaluation failed closed: proposal creation is out of scope")
    artifact = {
        "artifact_type": RESULT_EVALUATION_ARTIFACT_V1,
        "result_evaluation_version": RESULT_EVALUATION_RUNTIME_VERSION,
        "evaluation_id": _require_string(evaluation_id, "evaluation_id"),
        "canonical_chain_id": canonical_chain_id,
        "result_reference": result["result_id"],
        "result_hash": result["artifact_hash"],
        "execution_reference": result["execution_reference"],
        "completion_reference": result["completion_reference"],
        "worker_reference": result["worker_reference"],
        "worker_hash": result["worker_hash"],
        "worker_output_reference": result["worker_output_reference"],
        "worker_output_hash": result["worker_output_hash"],
        "result_payload_hash": result["result_payload_hash"],
        "evaluator_reference": _require_string(evaluator_reference, "evaluator_reference"),
        "evaluation_source": source,
        "evaluation_method": _require_string(evaluation_method, "evaluation_method"),
        "evaluation_observations": deepcopy(evaluation_observations),
        "evaluation_observations_hash": replay_hash(evaluation_observations),
        "evaluation_status": EVALUATED,
        "improvement_recommended": improvement_recommended,
        "improvement_proposal_reference": None,
        "evaluated_by": _normalize_token(evaluated_by, "evaluated_by"),
        "evaluated_at": _require_string(evaluated_at, "evaluated_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "approval_authority": False,
        "result_approved": False,
        "result_certified": False,
        "implementation_plan_created": False,
        "implementation_applied": False,
        "reflection_performed": False,
        "self_improvement_performed": False,
        "self_application_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "execution_history_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_evaluation_artifact(artifact)
    return artifact


def _evaluation_returned(evaluation: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(evaluation, "result evaluation artifact")
    returned = {
        "event_type": RESULT_EVALUATION_RETURNED,
        "evaluation_reference": evaluation["evaluation_id"],
        "evaluation_hash": evaluation["artifact_hash"],
        "canonical_chain_id": evaluation["canonical_chain_id"],
        "result_reference": evaluation["result_reference"],
        "result_hash": evaluation["result_hash"],
        "worker_reference": evaluation["worker_reference"],
        "evaluation_source": evaluation["evaluation_source"],
        "evaluation_method": evaluation["evaluation_method"],
        "evaluation_status": evaluation["evaluation_status"],
        "improvement_recommended": evaluation["improvement_recommended"],
        "improvement_proposal_reference": None,
        "evaluated_at": evaluation["evaluated_at"],
        "replay_reference": evaluation["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "approval_authority": False,
        "result_approved": False,
        "result_certified": False,
        "implementation_plan_created": False,
        "implementation_applied": False,
        "reflection_performed": False,
        "self_improvement_performed": False,
        "self_application_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "execution_history_modified": False,
        "reconstruction_metadata": {
            "evaluation_reconstructable": True,
            "result_reconstructable": True,
            "canonical_chain_continuous": True,
            "approval_performed": False,
            "implementation_plan_created": False,
            "self_improvement_performed": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(evaluation: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "result_evaluation_artifact": deepcopy(evaluation),
        "result_evaluation_replay": deepcopy(returned),
    }
    capture["result_evaluation_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_evaluation_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("result evaluation replay step ordering mismatch")
    _verify_artifact_hash(artifact, "result evaluation artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": RESULT_EVALUATION_RECORDED if index == 0 else RESULT_EVALUATION_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_result_artifact(result: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise FailClosedRuntimeError("result evaluation failed closed: result artifact is required")
    _verify_artifact_hash(result, "result artifact")
    if result.get("artifact_type") != RESULT_ARTIFACT_V1:
        raise FailClosedRuntimeError("result evaluation failed closed: invalid result")
    if result.get("result_status") != RESULT_CAPTURED:
        raise FailClosedRuntimeError("result evaluation failed closed: invalid result")
    if result.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("result evaluation failed closed: chain mismatch")
    if result.get("worker_output_hash") != result.get("result_payload", {}).get("artifact_hash"):
        raise FailClosedRuntimeError("result evaluation failed closed: corrupt references")
    if result.get("result_payload_hash") != replay_hash(result.get("result_payload")):
        raise FailClosedRuntimeError("result evaluation failed closed: corrupt references")
    if result.get("replay_visible") is not True:
        raise FailClosedRuntimeError("result evaluation failed closed: result replay visibility missing")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "worker_self_certified",
        "result_approved",
        "result_certified",
        "failure_analysis_performed",
        "reflection_performed",
        "self_improvement_performed",
        "governance_mutated",
        "replay_mutated",
        "execution_history_modified",
    ):
        if result.get(field) is not False:
            raise FailClosedRuntimeError("result evaluation failed closed: invalid result authority")
    _require_string(result.get("result_id"), "result_id")
    _require_string(result.get("execution_reference"), "execution_reference")
    _require_string(result.get("completion_reference"), "completion_reference")
    _require_string(result.get("worker_reference"), "worker_reference")
    _require_string(result.get("worker_hash"), "worker_hash")
    _require_string(result.get("worker_output_reference"), "worker_output_reference")
    _require_string(result.get("worker_output_hash"), "worker_output_hash")
    _require_string(result.get("result_payload_hash"), "result_payload_hash")
    return deepcopy(result)


def _validate_observations(observations: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(observations, dict):
        raise FailClosedRuntimeError("result evaluation failed closed: evaluation observations must be a JSON object")
    if FORBIDDEN_OBSERVATION_FIELDS.intersection(observations):
        raise FailClosedRuntimeError("result evaluation failed closed: authority-bearing observations")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "approval_authority",
        "result_approved",
        "result_certified",
        "implementation_plan_created",
        "implementation_applied",
        "reflection_performed",
        "self_improvement_performed",
        "self_application_performed",
        "governance_mutated",
        "replay_mutated",
        "execution_history_modified",
    ):
        if field in observations and observations.get(field) is not False:
            raise FailClosedRuntimeError("result evaluation failed closed: authority-bearing observations")
    replay_hash(observations)
    return deepcopy(observations)


def _validate_evaluation_artifact(evaluation: dict[str, Any]) -> None:
    if evaluation.get("artifact_type") != RESULT_EVALUATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("result evaluation failed closed: invalid evaluation artifact")
    if evaluation.get("evaluated_by") != "AIGOL":
        raise FailClosedRuntimeError("result evaluation failed closed: evaluated_by must be AIGOL")
    if evaluation.get("evaluation_status") != EVALUATED:
        raise FailClosedRuntimeError("result evaluation failed closed: invalid evaluation status")
    if evaluation.get("evaluation_source") not in ALLOWED_EVALUATION_SOURCES:
        raise FailClosedRuntimeError("result evaluation failed closed: invalid evaluation source")
    if not isinstance(evaluation.get("improvement_recommended"), bool):
        raise FailClosedRuntimeError("result evaluation failed closed: improvement recommendation must be boolean")
    if evaluation.get("improvement_proposal_reference") is not None:
        raise FailClosedRuntimeError("result evaluation failed closed: proposal creation is out of scope")
    if evaluation.get("evaluation_observations_hash") != replay_hash(evaluation.get("evaluation_observations")):
        raise FailClosedRuntimeError("result evaluation failed closed: observation hash mismatch")
    if evaluation.get("replay_visible") is not True:
        raise FailClosedRuntimeError("result evaluation failed closed: replay visibility missing")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "approval_authority",
        "result_approved",
        "result_certified",
        "implementation_plan_created",
        "implementation_applied",
        "reflection_performed",
        "self_improvement_performed",
        "self_application_performed",
        "governance_mutated",
        "replay_mutated",
        "execution_history_modified",
    ):
        if evaluation.get(field) is not False:
            raise FailClosedRuntimeError("result evaluation failed closed: forbidden evaluation authority introduced")
    _require_string(evaluation.get("evaluation_id"), "evaluation_id")
    _require_string(evaluation.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(evaluation.get("result_reference"), "result_reference")
    _require_string(evaluation.get("result_hash"), "result_hash")
    _require_string(evaluation.get("execution_reference"), "execution_reference")
    _require_string(evaluation.get("completion_reference"), "completion_reference")
    _require_string(evaluation.get("worker_reference"), "worker_reference")
    _require_string(evaluation.get("evaluator_reference"), "evaluator_reference")
    _require_string(evaluation.get("evaluation_method"), "evaluation_method")
    _require_string(evaluation.get("evaluated_at"), "evaluated_at")
    _require_string(evaluation.get("replay_reference"), "replay_reference")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("result evaluation replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("result evaluation replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
