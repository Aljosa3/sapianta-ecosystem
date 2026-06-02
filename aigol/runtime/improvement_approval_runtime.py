"""Replay-visible Improvement Approval Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.improvement_proposal_runtime import (
    IMPROVEMENT_PROPOSAL_ARTIFACT_V1,
    IMPROVEMENT_PROPOSED,
)
from aigol.runtime.improvement_review_runtime import IMPROVEMENT_REVIEW_ARTIFACT_V1, IMPROVEMENT_REVIEWED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


IMPROVEMENT_APPROVAL_RUNTIME_VERSION = "IMPROVEMENT_APPROVAL_RUNTIME_V1"
IMPROVEMENT_APPROVAL_ARTIFACT_V1 = "IMPROVEMENT_APPROVAL_ARTIFACT_V1"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
IMPROVEMENT_APPROVAL_RECORDED = "IMPROVEMENT_APPROVAL_RECORDED"
IMPROVEMENT_APPROVAL_RETURNED = "IMPROVEMENT_APPROVAL_RETURNED"

VALID_DECISIONS = frozenset({APPROVED, REJECTED})
REPLAY_STEPS = ("improvement_approval_recorded", "improvement_approval_returned")


def decide_improvement_approval(
    *,
    improvement_approval_id: str,
    improvement_review_artifact: dict[str, Any],
    improvement_proposal_artifact: dict[str, Any],
    canonical_chain_id: str,
    decision: str,
    decision_reason: str,
    human_authorization_reference: str,
    recorded_by: str,
    recorded_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record a human-authorized improvement approval decision without implementation."""

    replay_path = Path(replay_dir)
    _ensure_approval_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    proposal = _validate_proposal_artifact(improvement_proposal_artifact, chain_id)
    review = _validate_review_artifact(improvement_review_artifact, proposal, chain_id)
    approval = _approval_artifact(
        improvement_approval_id=improvement_approval_id,
        review=review,
        proposal=proposal,
        canonical_chain_id=chain_id,
        decision=decision,
        decision_reason=decision_reason,
        human_authorization_reference=human_authorization_reference,
        recorded_by=recorded_by,
        recorded_at=recorded_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], approval)
    returned = _approval_returned(approval)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(approval, returned)


def reconstruct_improvement_approval_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Improvement Approval Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("improvement approval replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("improvement approval replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "improvement approval artifact")
        wrappers.append(wrapper)

    approval = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("improvement_approval_reference") != approval["improvement_approval_id"]:
        raise FailClosedRuntimeError("improvement approval replay reference mismatch")
    if returned.get("improvement_approval_hash") != approval["artifact_hash"]:
        raise FailClosedRuntimeError("improvement approval replay hash mismatch")
    if returned.get("canonical_chain_id") != approval["canonical_chain_id"]:
        raise FailClosedRuntimeError("improvement approval replay chain mismatch")
    if returned.get("improvement_review_reference") != approval["improvement_review_reference"]:
        raise FailClosedRuntimeError("improvement approval replay review reference mismatch")
    if returned.get("improvement_review_hash") != approval["improvement_review_hash"]:
        raise FailClosedRuntimeError("improvement approval replay review hash mismatch")
    if returned.get("improvement_proposal_reference") != approval["improvement_proposal_reference"]:
        raise FailClosedRuntimeError("improvement approval replay proposal reference mismatch")
    if returned.get("improvement_proposal_hash") != approval["improvement_proposal_hash"]:
        raise FailClosedRuntimeError("improvement approval replay proposal hash mismatch")
    _validate_approval_artifact(approval)
    return {
        "improvement_approval_id": approval["improvement_approval_id"],
        "canonical_chain_id": approval["canonical_chain_id"],
        "improvement_review_reference": approval["improvement_review_reference"],
        "improvement_proposal_reference": approval["improvement_proposal_reference"],
        "decision": approval["decision"],
        "approval_status": approval["approval_status"],
        "implementation_authorized": approval["implementation_authorized"],
        "recorded_at": approval["recorded_at"],
        "implementation_performed": False,
        "execution_requested": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_improvement_performed": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _approval_artifact(
    *,
    improvement_approval_id: str,
    review: dict[str, Any],
    proposal: dict[str, Any],
    canonical_chain_id: str,
    decision: str,
    decision_reason: str,
    human_authorization_reference: str,
    recorded_by: str,
    recorded_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    normalized_decision = _normalize_token(decision, "decision")
    if normalized_decision not in VALID_DECISIONS:
        raise FailClosedRuntimeError("improvement approval failed closed: invalid decision")
    implementation_authorized = normalized_decision == APPROVED
    artifact = {
        "artifact_type": IMPROVEMENT_APPROVAL_ARTIFACT_V1,
        "improvement_approval_version": IMPROVEMENT_APPROVAL_RUNTIME_VERSION,
        "improvement_approval_id": _require_string(improvement_approval_id, "improvement_approval_id"),
        "canonical_chain_id": canonical_chain_id,
        "improvement_review_reference": review["improvement_review_id"],
        "improvement_review_hash": review["artifact_hash"],
        "improvement_proposal_reference": proposal["improvement_proposal_id"],
        "improvement_proposal_hash": proposal["artifact_hash"],
        "evaluation_reference": review["evaluation_reference"],
        "evaluation_hash": review["evaluation_hash"],
        "result_reference": review["result_reference"],
        "result_hash": review["result_hash"],
        "worker_reference": review["worker_reference"],
        "decision": normalized_decision,
        "decision_reason": _require_string(decision_reason, "decision_reason"),
        "decision_reason_hash": replay_hash(decision_reason),
        "decision_authority": "HUMAN",
        "human_authorization_reference": _require_string(
            human_authorization_reference,
            "human_authorization_reference",
        ),
        "approval_status": normalized_decision,
        "implementation_authorized": implementation_authorized,
        "implementation_reference": None,
        "recorded_by": _normalize_token(recorded_by, "recorded_by"),
        "recorded_at": _require_string(recorded_at, "recorded_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "worker_authority": False,
        "aigol_autonomous_approval": False,
        "implementation_authority": False,
        "self_improvement_authority": False,
        "governance_mutation_authority": False,
        "implementation_performed": False,
        "execution_requested": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "proposal_mutated": False,
        "review_mutated": False,
        "evaluation_mutated": False,
        "result_mutated": False,
        "execution_history_modified": False,
        "self_modification_performed": False,
        "self_improvement_performed": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_approval_artifact(artifact)
    return artifact


def _approval_returned(approval: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(approval, "improvement approval artifact")
    returned = {
        "event_type": IMPROVEMENT_APPROVAL_RETURNED,
        "improvement_approval_reference": approval["improvement_approval_id"],
        "improvement_approval_hash": approval["artifact_hash"],
        "canonical_chain_id": approval["canonical_chain_id"],
        "improvement_review_reference": approval["improvement_review_reference"],
        "improvement_review_hash": approval["improvement_review_hash"],
        "improvement_proposal_reference": approval["improvement_proposal_reference"],
        "improvement_proposal_hash": approval["improvement_proposal_hash"],
        "evaluation_reference": approval["evaluation_reference"],
        "evaluation_hash": approval["evaluation_hash"],
        "result_reference": approval["result_reference"],
        "result_hash": approval["result_hash"],
        "worker_reference": approval["worker_reference"],
        "decision": approval["decision"],
        "approval_status": approval["approval_status"],
        "decision_authority": "HUMAN",
        "human_authorization_reference": approval["human_authorization_reference"],
        "implementation_authorized": approval["implementation_authorized"],
        "implementation_reference": None,
        "recorded_at": approval["recorded_at"],
        "replay_reference": approval["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "worker_authority": False,
        "aigol_autonomous_approval": False,
        "implementation_authority": False,
        "self_improvement_authority": False,
        "governance_mutation_authority": False,
        "implementation_performed": False,
        "execution_requested": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_modification_performed": False,
        "self_improvement_performed": False,
        "reconstruction_metadata": {
            "approval_reconstructable": True,
            "review_reconstructable": True,
            "proposal_reconstructable": True,
            "canonical_chain_continuous": True,
            "implementation_performed": False,
            "execution_requested": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(approval: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "improvement_approval_artifact": deepcopy(approval),
        "improvement_approval_replay": deepcopy(returned),
    }
    capture["improvement_approval_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_approval_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("improvement approval replay step ordering mismatch")
    _verify_artifact_hash(artifact, "improvement approval artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": IMPROVEMENT_APPROVAL_RECORDED if index == 0 else IMPROVEMENT_APPROVAL_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_review_artifact(
    review: dict[str, Any],
    proposal: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(review, dict):
        raise FailClosedRuntimeError("improvement approval failed closed: review artifact is required")
    _verify_artifact_hash(review, "improvement review artifact")
    if review.get("artifact_type") != IMPROVEMENT_REVIEW_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement approval failed closed: invalid review")
    if review.get("review_status") != IMPROVEMENT_REVIEWED:
        raise FailClosedRuntimeError("improvement approval failed closed: invalid review")
    if review.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("improvement approval failed closed: chain mismatch")
    if review.get("improvement_proposal_reference") != proposal["improvement_proposal_id"]:
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if review.get("improvement_proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if review.get("evaluation_reference") != proposal["evaluation_reference"]:
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if review.get("evaluation_hash") != proposal["evaluation_hash"]:
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if review.get("result_reference") != proposal["result_reference"]:
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if review.get("result_hash") != proposal["result_hash"]:
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if review.get("worker_reference") != proposal["worker_reference"]:
        raise FailClosedRuntimeError("improvement approval failed closed: worker mismatch")
    if review.get("review_criteria_hash") != replay_hash(review.get("review_criteria")):
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if review.get("review_findings_hash") != replay_hash(review.get("review_findings")):
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if review.get("replay_visible") is not True:
        raise FailClosedRuntimeError("improvement approval failed closed: review replay visibility missing")
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
            raise FailClosedRuntimeError("improvement approval failed closed: invalid review authority")
    _require_string(review.get("improvement_review_id"), "improvement_review_id")
    _require_string(review.get("improvement_proposal_reference"), "improvement_proposal_reference")
    _require_string(review.get("improvement_proposal_hash"), "improvement_proposal_hash")
    _require_string(review.get("evaluation_reference"), "evaluation_reference")
    _require_string(review.get("evaluation_hash"), "evaluation_hash")
    _require_string(review.get("result_reference"), "result_reference")
    _require_string(review.get("result_hash"), "result_hash")
    _require_string(review.get("worker_reference"), "worker_reference")
    return deepcopy(review)


def _validate_proposal_artifact(proposal: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError("improvement approval failed closed: proposal artifact is required")
    _verify_artifact_hash(proposal, "improvement proposal artifact")
    if proposal.get("artifact_type") != IMPROVEMENT_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement approval failed closed: invalid proposal")
    if proposal.get("proposal_status") != IMPROVEMENT_PROPOSED:
        raise FailClosedRuntimeError("improvement approval failed closed: invalid proposal")
    if proposal.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("improvement approval failed closed: chain mismatch")
    if proposal.get("approval_required") is not True:
        raise FailClosedRuntimeError("improvement approval failed closed: proposal must require approval")
    if proposal.get("approval_reference") is not None:
        raise FailClosedRuntimeError("improvement approval failed closed: proposal already approved")
    if proposal.get("implementation_reference") is not None:
        raise FailClosedRuntimeError("improvement approval failed closed: implementation is out of scope")
    if proposal.get("proposal_text_hash") != replay_hash(proposal.get("proposal_text")):
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if proposal.get("proposal_scope_hash") != replay_hash(proposal.get("proposal_scope")):
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
    if proposal.get("proposal_constraints_hash") != replay_hash(proposal.get("proposal_constraints")):
        raise FailClosedRuntimeError("improvement approval failed closed: corrupt references")
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
            raise FailClosedRuntimeError("improvement approval failed closed: invalid proposal authority")
    return deepcopy(proposal)


def _validate_approval_artifact(approval: dict[str, Any]) -> None:
    if approval.get("artifact_type") != IMPROVEMENT_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement approval failed closed: invalid approval artifact")
    if approval.get("recorded_by") != "AIGOL":
        raise FailClosedRuntimeError("improvement approval failed closed: recorded_by must be AIGOL")
    if approval.get("decision_authority") != "HUMAN":
        raise FailClosedRuntimeError("improvement approval failed closed: decision authority must be HUMAN")
    if approval.get("decision") not in VALID_DECISIONS:
        raise FailClosedRuntimeError("improvement approval failed closed: invalid decision")
    if approval.get("approval_status") != approval.get("decision"):
        raise FailClosedRuntimeError("improvement approval failed closed: approval status mismatch")
    if approval.get("decision") == APPROVED and approval.get("implementation_authorized") is not True:
        raise FailClosedRuntimeError("improvement approval failed closed: implementation authorization mismatch")
    if approval.get("decision") == REJECTED and approval.get("implementation_authorized") is not False:
        raise FailClosedRuntimeError("improvement approval failed closed: implementation authorization mismatch")
    if approval.get("implementation_reference") is not None:
        raise FailClosedRuntimeError("improvement approval failed closed: implementation is out of scope")
    if approval.get("decision_reason_hash") != replay_hash(approval.get("decision_reason")):
        raise FailClosedRuntimeError("improvement approval failed closed: decision reason hash mismatch")
    if approval.get("replay_visible") is not True:
        raise FailClosedRuntimeError("improvement approval failed closed: replay visibility missing")
    for field in (
        "provider_authority",
        "worker_authority",
        "aigol_autonomous_approval",
        "implementation_authority",
        "self_improvement_authority",
        "governance_mutation_authority",
        "implementation_performed",
        "execution_requested",
        "worker_dispatched",
        "worker_invoked",
        "governance_mutated",
        "replay_mutated",
        "proposal_mutated",
        "review_mutated",
        "evaluation_mutated",
        "result_mutated",
        "execution_history_modified",
        "self_modification_performed",
        "self_improvement_performed",
    ):
        if approval.get(field) is not False:
            raise FailClosedRuntimeError("improvement approval failed closed: forbidden approval authority introduced")
    _require_string(approval.get("improvement_approval_id"), "improvement_approval_id")
    _require_string(approval.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(approval.get("improvement_review_reference"), "improvement_review_reference")
    _require_string(approval.get("improvement_review_hash"), "improvement_review_hash")
    _require_string(approval.get("improvement_proposal_reference"), "improvement_proposal_reference")
    _require_string(approval.get("improvement_proposal_hash"), "improvement_proposal_hash")
    _require_string(approval.get("evaluation_reference"), "evaluation_reference")
    _require_string(approval.get("evaluation_hash"), "evaluation_hash")
    _require_string(approval.get("result_reference"), "result_reference")
    _require_string(approval.get("result_hash"), "result_hash")
    _require_string(approval.get("decision_reason"), "decision_reason")
    _require_string(approval.get("human_authorization_reference"), "human_authorization_reference")
    _require_string(approval.get("recorded_at"), "recorded_at")
    _require_string(approval.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("improvement approval replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("improvement approval replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
