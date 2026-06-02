"""Replay-visible Improvement Proposal Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.result_evaluation_runtime import EVALUATED, RESULT_EVALUATION_ARTIFACT_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


IMPROVEMENT_PROPOSAL_RUNTIME_VERSION = "IMPROVEMENT_PROPOSAL_RUNTIME_V1"
IMPROVEMENT_PROPOSAL_ARTIFACT_V1 = "IMPROVEMENT_PROPOSAL_ARTIFACT_V1"
IMPROVEMENT_PROPOSED = "IMPROVEMENT_PROPOSED"
IMPROVEMENT_PROPOSAL_CREATED = "IMPROVEMENT_PROPOSAL_CREATED"
IMPROVEMENT_PROPOSAL_RETURNED = "IMPROVEMENT_PROPOSAL_RETURNED"

REPLAY_STEPS = ("improvement_proposal_created", "improvement_proposal_returned")
ALLOWED_PROPOSAL_SOURCES = frozenset(
    {
        "RESULT_EVALUATION",
        "AIGOL_DETERMINISTIC_REVIEW",
        "HUMAN_OBSERVATION_RECORDED",
        "WORKER_REPORT_RECORDED",
        "PROVIDER_ASSISTED_NON_AUTHORITATIVE",
        "COMBINED_EVIDENCE",
    }
)
FORBIDDEN_PROPOSAL_FIELDS = frozenset(
    {
        "automatic_approval",
        "approval_transition",
        "implementation_command",
        "execution_command",
        "execution_request",
        "worker_dispatch",
        "worker_invocation",
        "provider_command",
        "credentials",
        "api_key",
        "secret",
        "governance_mutation",
        "replay_repair",
        "self_improvement",
        "self_apply",
    }
)


def create_improvement_proposal(
    *,
    improvement_proposal_id: str,
    evaluation_artifact: dict[str, Any],
    canonical_chain_id: str,
    proposal_source: str,
    proposal_text: str,
    proposal_reason: str,
    proposal_scope: dict[str, Any],
    proposal_constraints: dict[str, Any],
    created_by: str,
    created_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create an improvement proposal from evaluation evidence only."""

    replay_path = Path(replay_dir)
    _ensure_proposal_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    evaluation = _validate_evaluation_artifact(evaluation_artifact, chain_id)
    scope = _validate_json_object(proposal_scope, "proposal_scope")
    constraints = _validate_json_object(proposal_constraints, "proposal_constraints")
    proposal = _proposal_artifact(
        improvement_proposal_id=improvement_proposal_id,
        evaluation=evaluation,
        canonical_chain_id=chain_id,
        proposal_source=proposal_source,
        proposal_text=proposal_text,
        proposal_reason=proposal_reason,
        proposal_scope=scope,
        proposal_constraints=constraints,
        created_by=created_by,
        created_at=created_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], proposal)
    returned = _proposal_returned(proposal)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(proposal, returned)


def reconstruct_improvement_proposal_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Improvement Proposal Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("improvement proposal replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("improvement proposal replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "improvement proposal artifact")
        wrappers.append(wrapper)

    proposal = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("improvement_proposal_reference") != proposal["improvement_proposal_id"]:
        raise FailClosedRuntimeError("improvement proposal replay reference mismatch")
    if returned.get("improvement_proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("improvement proposal replay hash mismatch")
    if returned.get("canonical_chain_id") != proposal["canonical_chain_id"]:
        raise FailClosedRuntimeError("improvement proposal replay chain mismatch")
    if returned.get("evaluation_reference") != proposal["evaluation_reference"]:
        raise FailClosedRuntimeError("improvement proposal replay evaluation reference mismatch")
    if returned.get("evaluation_hash") != proposal["evaluation_hash"]:
        raise FailClosedRuntimeError("improvement proposal replay evaluation hash mismatch")
    _validate_proposal_artifact(proposal)
    return {
        "improvement_proposal_id": proposal["improvement_proposal_id"],
        "canonical_chain_id": proposal["canonical_chain_id"],
        "evaluation_reference": proposal["evaluation_reference"],
        "result_reference": proposal["result_reference"],
        "worker_reference": proposal["worker_reference"],
        "proposal_status": proposal["proposal_status"],
        "approval_required": proposal["approval_required"],
        "implementation_authorized": proposal["implementation_authorized"],
        "created_at": proposal["created_at"],
        "proposal_approved": False,
        "review_performed": False,
        "implementation_applied": False,
        "execution_requested": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _proposal_artifact(
    *,
    improvement_proposal_id: str,
    evaluation: dict[str, Any],
    canonical_chain_id: str,
    proposal_source: str,
    proposal_text: str,
    proposal_reason: str,
    proposal_scope: dict[str, Any],
    proposal_constraints: dict[str, Any],
    created_by: str,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    source = _normalize_token(proposal_source, "proposal_source")
    if source not in ALLOWED_PROPOSAL_SOURCES:
        raise FailClosedRuntimeError("improvement proposal failed closed: invalid proposal source")
    text = _validate_bounded_text(proposal_text, "proposal_text")
    reason = _validate_bounded_text(proposal_reason, "proposal_reason")
    artifact = {
        "artifact_type": IMPROVEMENT_PROPOSAL_ARTIFACT_V1,
        "improvement_proposal_version": IMPROVEMENT_PROPOSAL_RUNTIME_VERSION,
        "improvement_proposal_id": _require_string(improvement_proposal_id, "improvement_proposal_id"),
        "canonical_chain_id": canonical_chain_id,
        "evaluation_reference": evaluation["evaluation_id"],
        "evaluation_hash": evaluation["artifact_hash"],
        "result_reference": evaluation["result_reference"],
        "result_hash": evaluation["result_hash"],
        "execution_reference": evaluation["execution_reference"],
        "completion_reference": evaluation["completion_reference"],
        "worker_reference": evaluation["worker_reference"],
        "worker_hash": evaluation["worker_hash"],
        "proposal_source": source,
        "proposal_text": text,
        "proposal_text_hash": replay_hash(text),
        "proposal_reason": reason,
        "proposal_scope": deepcopy(proposal_scope),
        "proposal_scope_hash": replay_hash(proposal_scope),
        "proposal_constraints": deepcopy(proposal_constraints),
        "proposal_constraints_hash": replay_hash(proposal_constraints),
        "proposal_status": IMPROVEMENT_PROPOSED,
        "approval_required": True,
        "approval_reference": None,
        "implementation_authorized": False,
        "implementation_reference": None,
        "created_by": _normalize_token(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "approval_authority": False,
        "implementation_authority": False,
        "self_improvement_authority": False,
        "proposal_approved": False,
        "review_performed": False,
        "implementation_applied": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_improvement_performed": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_proposal_artifact(artifact)
    return artifact


def _proposal_returned(proposal: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(proposal, "improvement proposal artifact")
    returned = {
        "event_type": IMPROVEMENT_PROPOSAL_RETURNED,
        "improvement_proposal_reference": proposal["improvement_proposal_id"],
        "improvement_proposal_hash": proposal["artifact_hash"],
        "canonical_chain_id": proposal["canonical_chain_id"],
        "evaluation_reference": proposal["evaluation_reference"],
        "evaluation_hash": proposal["evaluation_hash"],
        "result_reference": proposal["result_reference"],
        "result_hash": proposal["result_hash"],
        "worker_reference": proposal["worker_reference"],
        "proposal_status": proposal["proposal_status"],
        "approval_required": proposal["approval_required"],
        "approval_reference": None,
        "implementation_authorized": False,
        "implementation_reference": None,
        "created_at": proposal["created_at"],
        "replay_reference": proposal["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "approval_authority": False,
        "implementation_authority": False,
        "self_improvement_authority": False,
        "proposal_approved": False,
        "review_performed": False,
        "implementation_applied": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_improvement_performed": False,
        "reconstruction_metadata": {
            "proposal_reconstructable": True,
            "evaluation_reconstructable": True,
            "canonical_chain_continuous": True,
            "approval_performed": False,
            "review_performed": False,
            "implementation_performed": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(proposal: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "improvement_proposal_artifact": deepcopy(proposal),
        "improvement_proposal_replay": deepcopy(returned),
    }
    capture["improvement_proposal_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_proposal_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("improvement proposal replay step ordering mismatch")
    _verify_artifact_hash(artifact, "improvement proposal artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": IMPROVEMENT_PROPOSAL_CREATED if index == 0 else IMPROVEMENT_PROPOSAL_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_evaluation_artifact(evaluation: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(evaluation, dict):
        raise FailClosedRuntimeError("improvement proposal failed closed: evaluation artifact is required")
    _verify_artifact_hash(evaluation, "result evaluation artifact")
    if evaluation.get("artifact_type") != RESULT_EVALUATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement proposal failed closed: invalid evaluation")
    if evaluation.get("evaluation_status") != EVALUATED:
        raise FailClosedRuntimeError("improvement proposal failed closed: invalid evaluation")
    if evaluation.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("improvement proposal failed closed: chain mismatch")
    if evaluation.get("improvement_recommended") is not True:
        raise FailClosedRuntimeError("improvement proposal failed closed: improvement was not recommended")
    if evaluation.get("improvement_proposal_reference") is not None:
        raise FailClosedRuntimeError("improvement proposal failed closed: evaluation already references proposal")
    if evaluation.get("evaluation_observations_hash") != replay_hash(evaluation.get("evaluation_observations")):
        raise FailClosedRuntimeError("improvement proposal failed closed: corrupt references")
    if evaluation.get("replay_visible") is not True:
        raise FailClosedRuntimeError("improvement proposal failed closed: evaluation replay visibility missing")
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
            raise FailClosedRuntimeError("improvement proposal failed closed: invalid evaluation authority")
    _require_string(evaluation.get("evaluation_id"), "evaluation_id")
    _require_string(evaluation.get("result_reference"), "result_reference")
    _require_string(evaluation.get("result_hash"), "result_hash")
    _require_string(evaluation.get("execution_reference"), "execution_reference")
    _require_string(evaluation.get("completion_reference"), "completion_reference")
    _require_string(evaluation.get("worker_reference"), "worker_reference")
    _require_string(evaluation.get("worker_hash"), "worker_hash")
    return deepcopy(evaluation)


def _validate_json_object(value: dict[str, Any], field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"improvement proposal failed closed: {field_name} must be a JSON object")
    if FORBIDDEN_PROPOSAL_FIELDS.intersection(value):
        raise FailClosedRuntimeError("improvement proposal failed closed: authority-bearing proposal content")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "approval_authority",
        "implementation_authority",
        "self_improvement_authority",
        "proposal_approved",
        "implementation_authorized",
        "implementation_applied",
        "worker_dispatched",
        "worker_invoked",
        "execution_requested",
        "governance_mutated",
        "replay_mutated",
    ):
        if field in value and value.get(field) is not False:
            raise FailClosedRuntimeError("improvement proposal failed closed: authority-bearing proposal content")
    replay_hash(value)
    return deepcopy(value)


def _validate_bounded_text(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    lowered = text.lower()
    for forbidden in (
        "approve automatically",
        "execute now",
        "dispatch worker",
        "invoke worker",
        "mutate governance",
        "repair replay",
        "self-improve",
        "self improve",
        "apply this change now",
    ):
        if forbidden in lowered:
            raise FailClosedRuntimeError("improvement proposal failed closed: authority-bearing proposal text")
    return text


def _validate_proposal_artifact(proposal: dict[str, Any]) -> None:
    if proposal.get("artifact_type") != IMPROVEMENT_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement proposal failed closed: invalid proposal artifact")
    if proposal.get("created_by") != "AIGOL":
        raise FailClosedRuntimeError("improvement proposal failed closed: created_by must be AIGOL")
    if proposal.get("proposal_status") != IMPROVEMENT_PROPOSED:
        raise FailClosedRuntimeError("improvement proposal failed closed: invalid proposal status")
    if proposal.get("proposal_source") not in ALLOWED_PROPOSAL_SOURCES:
        raise FailClosedRuntimeError("improvement proposal failed closed: invalid proposal source")
    if proposal.get("approval_required") is not True:
        raise FailClosedRuntimeError("improvement proposal failed closed: approval must be required")
    if proposal.get("approval_reference") is not None:
        raise FailClosedRuntimeError("improvement proposal failed closed: approval is out of scope")
    if proposal.get("implementation_reference") is not None:
        raise FailClosedRuntimeError("improvement proposal failed closed: implementation is out of scope")
    if proposal.get("proposal_text_hash") != replay_hash(proposal.get("proposal_text")):
        raise FailClosedRuntimeError("improvement proposal failed closed: proposal text hash mismatch")
    if proposal.get("proposal_scope_hash") != replay_hash(proposal.get("proposal_scope")):
        raise FailClosedRuntimeError("improvement proposal failed closed: proposal scope hash mismatch")
    if proposal.get("proposal_constraints_hash") != replay_hash(proposal.get("proposal_constraints")):
        raise FailClosedRuntimeError("improvement proposal failed closed: proposal constraints hash mismatch")
    if proposal.get("replay_visible") is not True:
        raise FailClosedRuntimeError("improvement proposal failed closed: replay visibility missing")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "approval_authority",
        "implementation_authority",
        "self_improvement_authority",
        "proposal_approved",
        "implementation_authorized",
        "implementation_applied",
        "worker_dispatched",
        "worker_invoked",
        "execution_requested",
        "governance_mutated",
        "replay_mutated",
        "self_improvement_performed",
    ):
        if proposal.get(field) is not False:
            raise FailClosedRuntimeError("improvement proposal failed closed: forbidden proposal authority introduced")
    _require_string(proposal.get("improvement_proposal_id"), "improvement_proposal_id")
    _require_string(proposal.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(proposal.get("evaluation_reference"), "evaluation_reference")
    _require_string(proposal.get("evaluation_hash"), "evaluation_hash")
    _require_string(proposal.get("result_reference"), "result_reference")
    _require_string(proposal.get("result_hash"), "result_hash")
    _require_string(proposal.get("execution_reference"), "execution_reference")
    _require_string(proposal.get("completion_reference"), "completion_reference")
    _require_string(proposal.get("worker_reference"), "worker_reference")
    _require_string(proposal.get("proposal_text"), "proposal_text")
    _require_string(proposal.get("proposal_reason"), "proposal_reason")
    _require_string(proposal.get("created_at"), "created_at")
    _require_string(proposal.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("improvement proposal replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("improvement proposal replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
