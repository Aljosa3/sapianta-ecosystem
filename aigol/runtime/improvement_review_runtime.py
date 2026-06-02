"""Replay-visible Improvement Review Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.improvement_proposal_runtime import (
    IMPROVEMENT_PROPOSAL_ARTIFACT_V1,
    IMPROVEMENT_PROPOSED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


IMPROVEMENT_REVIEW_RUNTIME_VERSION = "IMPROVEMENT_REVIEW_RUNTIME_V1"
IMPROVEMENT_REVIEW_ARTIFACT_V1 = "IMPROVEMENT_REVIEW_ARTIFACT_V1"
IMPROVEMENT_REVIEWED = "IMPROVEMENT_REVIEWED"
IMPROVEMENT_REVIEW_RECORDED = "IMPROVEMENT_REVIEW_RECORDED"
IMPROVEMENT_REVIEW_RETURNED = "IMPROVEMENT_REVIEW_RETURNED"

REPLAY_STEPS = ("improvement_review_recorded", "improvement_review_returned")
ALLOWED_REVIEW_SOURCES = frozenset(
    {
        "AIGOL_DETERMINISTIC_REVIEW",
        "HUMAN_OBSERVATION_RECORDED",
        "WORKER_REPORT_RECORDED",
        "PROVIDER_ASSISTED_NON_AUTHORITATIVE",
        "GOVERNANCE_CONTEXT_REVIEW",
        "COMBINED_EVIDENCE",
    }
)
FORBIDDEN_REVIEW_FIELDS = frozenset(
    {
        "approval_transition",
        "rejection_transition",
        "approval_decision",
        "implementation_command",
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


def review_improvement_proposal(
    *,
    improvement_review_id: str,
    improvement_proposal_artifact: dict[str, Any],
    canonical_chain_id: str,
    review_source: str,
    review_method: str,
    review_criteria: dict[str, Any],
    review_findings: dict[str, Any],
    approval_recommended: bool,
    reviewed_by: str,
    reviewed_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Review an improvement proposal without approving, rejecting, or implementing it."""

    replay_path = Path(replay_dir)
    _ensure_review_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    proposal = _validate_proposal_artifact(improvement_proposal_artifact, chain_id)
    criteria = _validate_json_object(review_criteria, "review_criteria")
    findings = _validate_json_object(review_findings, "review_findings")
    review = _review_artifact(
        improvement_review_id=improvement_review_id,
        proposal=proposal,
        canonical_chain_id=chain_id,
        review_source=review_source,
        review_method=review_method,
        review_criteria=criteria,
        review_findings=findings,
        approval_recommended=approval_recommended,
        reviewed_by=reviewed_by,
        reviewed_at=reviewed_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], review)
    returned = _review_returned(review)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(review, returned)


def reconstruct_improvement_review_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Improvement Review Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("improvement review replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("improvement review replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "improvement review artifact")
        wrappers.append(wrapper)

    review = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("improvement_review_reference") != review["improvement_review_id"]:
        raise FailClosedRuntimeError("improvement review replay reference mismatch")
    if returned.get("improvement_review_hash") != review["artifact_hash"]:
        raise FailClosedRuntimeError("improvement review replay hash mismatch")
    if returned.get("canonical_chain_id") != review["canonical_chain_id"]:
        raise FailClosedRuntimeError("improvement review replay chain mismatch")
    if returned.get("improvement_proposal_reference") != review["improvement_proposal_reference"]:
        raise FailClosedRuntimeError("improvement review replay proposal reference mismatch")
    if returned.get("improvement_proposal_hash") != review["improvement_proposal_hash"]:
        raise FailClosedRuntimeError("improvement review replay proposal hash mismatch")
    _validate_review_artifact(review)
    return {
        "improvement_review_id": review["improvement_review_id"],
        "canonical_chain_id": review["canonical_chain_id"],
        "improvement_proposal_reference": review["improvement_proposal_reference"],
        "evaluation_reference": review["evaluation_reference"],
        "result_reference": review["result_reference"],
        "worker_reference": review["worker_reference"],
        "review_status": review["review_status"],
        "approval_recommended": review["approval_recommended"],
        "implementation_authorized": review["implementation_authorized"],
        "reviewed_at": review["reviewed_at"],
        "proposal_approved": False,
        "proposal_rejected": False,
        "implementation_applied": False,
        "execution_requested": False,
        "self_improvement_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _review_artifact(
    *,
    improvement_review_id: str,
    proposal: dict[str, Any],
    canonical_chain_id: str,
    review_source: str,
    review_method: str,
    review_criteria: dict[str, Any],
    review_findings: dict[str, Any],
    approval_recommended: bool,
    reviewed_by: str,
    reviewed_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    source = _normalize_token(review_source, "review_source")
    if source not in ALLOWED_REVIEW_SOURCES:
        raise FailClosedRuntimeError("improvement review failed closed: invalid review source")
    if not isinstance(approval_recommended, bool):
        raise FailClosedRuntimeError("improvement review failed closed: approval recommendation must be boolean")
    artifact = {
        "artifact_type": IMPROVEMENT_REVIEW_ARTIFACT_V1,
        "improvement_review_version": IMPROVEMENT_REVIEW_RUNTIME_VERSION,
        "improvement_review_id": _require_string(improvement_review_id, "improvement_review_id"),
        "canonical_chain_id": canonical_chain_id,
        "improvement_proposal_reference": proposal["improvement_proposal_id"],
        "improvement_proposal_hash": proposal["artifact_hash"],
        "evaluation_reference": proposal["evaluation_reference"],
        "evaluation_hash": proposal["evaluation_hash"],
        "result_reference": proposal["result_reference"],
        "result_hash": proposal["result_hash"],
        "execution_reference": proposal["execution_reference"],
        "completion_reference": proposal["completion_reference"],
        "worker_reference": proposal["worker_reference"],
        "worker_hash": proposal["worker_hash"],
        "review_source": source,
        "review_method": _require_string(review_method, "review_method"),
        "review_criteria": deepcopy(review_criteria),
        "review_criteria_hash": replay_hash(review_criteria),
        "review_findings": deepcopy(review_findings),
        "review_findings_hash": replay_hash(review_findings),
        "review_status": IMPROVEMENT_REVIEWED,
        "approval_recommended": approval_recommended,
        "approval_reference": None,
        "implementation_authorized": False,
        "implementation_reference": None,
        "reviewed_by": _normalize_token(reviewed_by, "reviewed_by"),
        "reviewed_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "approval_authority": False,
        "implementation_authority": False,
        "self_improvement_authority": False,
        "proposal_approved": False,
        "proposal_rejected": False,
        "implementation_applied": False,
        "execution_requested": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_improvement_performed": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_review_artifact(artifact)
    return artifact


def _review_returned(review: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(review, "improvement review artifact")
    returned = {
        "event_type": IMPROVEMENT_REVIEW_RETURNED,
        "improvement_review_reference": review["improvement_review_id"],
        "improvement_review_hash": review["artifact_hash"],
        "canonical_chain_id": review["canonical_chain_id"],
        "improvement_proposal_reference": review["improvement_proposal_reference"],
        "improvement_proposal_hash": review["improvement_proposal_hash"],
        "evaluation_reference": review["evaluation_reference"],
        "evaluation_hash": review["evaluation_hash"],
        "result_reference": review["result_reference"],
        "result_hash": review["result_hash"],
        "worker_reference": review["worker_reference"],
        "review_status": review["review_status"],
        "approval_recommended": review["approval_recommended"],
        "approval_reference": None,
        "implementation_authorized": False,
        "implementation_reference": None,
        "reviewed_at": review["reviewed_at"],
        "replay_reference": review["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "approval_authority": False,
        "implementation_authority": False,
        "self_improvement_authority": False,
        "proposal_approved": False,
        "proposal_rejected": False,
        "implementation_applied": False,
        "execution_requested": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_improvement_performed": False,
        "reconstruction_metadata": {
            "review_reconstructable": True,
            "proposal_reconstructable": True,
            "canonical_chain_continuous": True,
            "approval_performed": False,
            "implementation_performed": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(review: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "improvement_review_artifact": deepcopy(review),
        "improvement_review_replay": deepcopy(returned),
    }
    capture["improvement_review_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_review_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("improvement review replay step ordering mismatch")
    _verify_artifact_hash(artifact, "improvement review artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": IMPROVEMENT_REVIEW_RECORDED if index == 0 else IMPROVEMENT_REVIEW_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_proposal_artifact(proposal: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError("improvement review failed closed: proposal artifact is required")
    _verify_artifact_hash(proposal, "improvement proposal artifact")
    if proposal.get("artifact_type") != IMPROVEMENT_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement review failed closed: invalid proposal")
    if proposal.get("proposal_status") != IMPROVEMENT_PROPOSED:
        raise FailClosedRuntimeError("improvement review failed closed: invalid proposal")
    if proposal.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("improvement review failed closed: chain mismatch")
    if proposal.get("approval_required") is not True:
        raise FailClosedRuntimeError("improvement review failed closed: proposal must require approval")
    if proposal.get("approval_reference") is not None:
        raise FailClosedRuntimeError("improvement review failed closed: approval is out of scope")
    if proposal.get("implementation_reference") is not None:
        raise FailClosedRuntimeError("improvement review failed closed: implementation is out of scope")
    if proposal.get("proposal_text_hash") != replay_hash(proposal.get("proposal_text")):
        raise FailClosedRuntimeError("improvement review failed closed: corrupt references")
    if proposal.get("proposal_scope_hash") != replay_hash(proposal.get("proposal_scope")):
        raise FailClosedRuntimeError("improvement review failed closed: corrupt references")
    if proposal.get("proposal_constraints_hash") != replay_hash(proposal.get("proposal_constraints")):
        raise FailClosedRuntimeError("improvement review failed closed: corrupt references")
    if proposal.get("replay_visible") is not True:
        raise FailClosedRuntimeError("improvement review failed closed: proposal replay visibility missing")
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
            raise FailClosedRuntimeError("improvement review failed closed: invalid proposal authority")
    _require_string(proposal.get("improvement_proposal_id"), "improvement_proposal_id")
    _require_string(proposal.get("evaluation_reference"), "evaluation_reference")
    _require_string(proposal.get("evaluation_hash"), "evaluation_hash")
    _require_string(proposal.get("result_reference"), "result_reference")
    _require_string(proposal.get("result_hash"), "result_hash")
    _require_string(proposal.get("execution_reference"), "execution_reference")
    _require_string(proposal.get("completion_reference"), "completion_reference")
    _require_string(proposal.get("worker_reference"), "worker_reference")
    _require_string(proposal.get("worker_hash"), "worker_hash")
    return deepcopy(proposal)


def _validate_json_object(value: dict[str, Any], field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"improvement review failed closed: {field_name} must be a JSON object")
    if FORBIDDEN_REVIEW_FIELDS.intersection(value):
        raise FailClosedRuntimeError("improvement review failed closed: authority-bearing review content")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "approval_authority",
        "implementation_authority",
        "self_improvement_authority",
        "proposal_approved",
        "proposal_rejected",
        "implementation_authorized",
        "implementation_applied",
        "execution_requested",
        "worker_dispatched",
        "worker_invoked",
        "governance_mutated",
        "replay_mutated",
    ):
        if field in value and value.get(field) is not False:
            raise FailClosedRuntimeError("improvement review failed closed: authority-bearing review content")
    replay_hash(value)
    return deepcopy(value)


def _validate_review_artifact(review: dict[str, Any]) -> None:
    if review.get("artifact_type") != IMPROVEMENT_REVIEW_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement review failed closed: invalid review artifact")
    if review.get("reviewed_by") != "AIGOL":
        raise FailClosedRuntimeError("improvement review failed closed: reviewed_by must be AIGOL")
    if review.get("review_status") != IMPROVEMENT_REVIEWED:
        raise FailClosedRuntimeError("improvement review failed closed: invalid review status")
    if review.get("review_source") not in ALLOWED_REVIEW_SOURCES:
        raise FailClosedRuntimeError("improvement review failed closed: invalid review source")
    if not isinstance(review.get("approval_recommended"), bool):
        raise FailClosedRuntimeError("improvement review failed closed: approval recommendation must be boolean")
    if review.get("approval_reference") is not None:
        raise FailClosedRuntimeError("improvement review failed closed: approval is out of scope")
    if review.get("implementation_reference") is not None:
        raise FailClosedRuntimeError("improvement review failed closed: implementation is out of scope")
    if review.get("review_criteria_hash") != replay_hash(review.get("review_criteria")):
        raise FailClosedRuntimeError("improvement review failed closed: review criteria hash mismatch")
    if review.get("review_findings_hash") != replay_hash(review.get("review_findings")):
        raise FailClosedRuntimeError("improvement review failed closed: review findings hash mismatch")
    if review.get("replay_visible") is not True:
        raise FailClosedRuntimeError("improvement review failed closed: replay visibility missing")
    for field in (
        "provider_authority",
        "governance_authority",
        "worker_authority",
        "approval_authority",
        "implementation_authority",
        "self_improvement_authority",
        "proposal_approved",
        "proposal_rejected",
        "implementation_authorized",
        "implementation_applied",
        "execution_requested",
        "worker_dispatched",
        "worker_invoked",
        "governance_mutated",
        "replay_mutated",
        "self_improvement_performed",
    ):
        if review.get(field) is not False:
            raise FailClosedRuntimeError("improvement review failed closed: forbidden review authority introduced")
    _require_string(review.get("improvement_review_id"), "improvement_review_id")
    _require_string(review.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(review.get("improvement_proposal_reference"), "improvement_proposal_reference")
    _require_string(review.get("improvement_proposal_hash"), "improvement_proposal_hash")
    _require_string(review.get("evaluation_reference"), "evaluation_reference")
    _require_string(review.get("evaluation_hash"), "evaluation_hash")
    _require_string(review.get("result_reference"), "result_reference")
    _require_string(review.get("result_hash"), "result_hash")
    _require_string(review.get("worker_reference"), "worker_reference")
    _require_string(review.get("review_method"), "review_method")
    _require_string(review.get("reviewed_at"), "reviewed_at")
    _require_string(review.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("improvement review replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("improvement review replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
