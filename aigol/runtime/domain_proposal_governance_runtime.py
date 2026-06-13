"""Replay-visible governance for new domain proposals."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION = "AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_V1"
DOMAIN_PROPOSAL_ARTIFACT_V1 = "DOMAIN_PROPOSAL_ARTIFACT_V1"
DOMAIN_REVIEW_DECISION_ARTIFACT_V1 = "DOMAIN_REVIEW_DECISION_ARTIFACT_V1"
DOMAIN_CANDIDATE_ARTIFACT_V1 = "DOMAIN_CANDIDATE_ARTIFACT_V1"
DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1 = "DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1"

DOMAIN_PROPOSAL_CREATED = "DOMAIN_PROPOSAL_CREATED"
DOMAIN_CANDIDATE_CREATED = "DOMAIN_CANDIDATE_CREATED"
DOMAIN_PROPOSAL_ARCHIVED = "DOMAIN_PROPOSAL_ARCHIVED"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
FAILED_CLOSED = "FAILED_CLOSED"

PROPOSAL_REPLAY_STEPS = (
    "domain_proposal_recorded",
    "domain_proposal_returned",
)
REVIEW_REPLAY_STEPS = (
    "domain_review_decision_recorded",
    "domain_candidate_or_archive_recorded",
    "domain_review_returned",
)

VALID_SOURCE_TYPES = frozenset({"HUMAN_REQUEST", "REPLAY_DERIVED_IMPROVEMENT"})
VALID_REVIEW_DECISIONS = frozenset({APPROVED, REJECTED})


AUTHORITY_FLAGS = {
    "proposal_authoritative": False,
    "approval_required": True,
    "domain_created": False,
    "domain_registered": False,
    "domain_activated": False,
    "live_registry_mutated": False,
    "ppp_invoked": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "worker_dispatched": False,
    "execution_started": False,
    "authorization_created": False,
    "governance_mutated": False,
    "replay_mutated": False,
    "self_authorized": False,
}


def create_domain_proposal(
    *,
    proposal_id: str,
    source_type: str,
    proposed_domain: str,
    need_summary: str,
    requested_by: str,
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
    source_replay_references: list[str] | None = None,
    source_replay_hashes: list[str] | None = None,
) -> dict[str, Any]:
    """Create a non-authoritative proposal for a new domain."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, PROPOSAL_REPLAY_STEPS)
        proposal = _proposal_artifact(
            proposal_id=proposal_id,
            source_type=source_type,
            proposed_domain=proposed_domain,
            need_summary=need_summary,
            requested_by=requested_by,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            source_replay_references=source_replay_references or [],
            source_replay_hashes=source_replay_hashes or [],
            proposal_status=DOMAIN_PROPOSAL_CREATED,
            failure_reason=None,
        )
        returned = _proposal_returned_artifact(proposal)
        _persist_step(replay_path, 0, PROPOSAL_REPLAY_STEPS[0], proposal)
        _persist_step(replay_path, 1, PROPOSAL_REPLAY_STEPS[1], returned)
        return _proposal_capture(proposal, returned, replay_path)
    except Exception as exc:
        proposal = _failed_proposal_artifact(
            proposal_id=proposal_id,
            source_type=source_type,
            proposed_domain=proposed_domain,
            need_summary=need_summary,
            requested_by=requested_by,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _proposal_returned_artifact(proposal)
        _persist_failure_if_possible(replay_path, 0, PROPOSAL_REPLAY_STEPS[0], proposal)
        _persist_failure_if_possible(replay_path, 1, PROPOSAL_REPLAY_STEPS[1], returned)
        return _proposal_capture(proposal, returned, replay_path)


def review_domain_proposal(
    *,
    review_id: str,
    domain_proposal_artifact: dict[str, Any],
    decision: str,
    decision_reason: str,
    reviewed_by: str,
    reviewed_at: str,
    human_approval_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Approve or reject a domain proposal without creating a live domain."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, REVIEW_REPLAY_STEPS)
        proposal = deepcopy(domain_proposal_artifact)
        _validate_proposal(proposal)
        review = _review_artifact(
            review_id=review_id,
            proposal=proposal,
            decision=decision,
            decision_reason=decision_reason,
            reviewed_by=reviewed_by,
            reviewed_at=reviewed_at,
            human_approval_reference=human_approval_reference,
            review_status=_normalize_decision(decision),
            failure_reason=None,
        )
        outcome = (
            _domain_candidate_artifact(review=review, proposal=proposal, reviewed_at=reviewed_at)
            if review["review_status"] == APPROVED
            else _domain_archive_artifact(review=review, proposal=proposal, reviewed_at=reviewed_at)
        )
        returned = _review_returned_artifact(review, outcome)
        _persist_step(replay_path, 0, REVIEW_REPLAY_STEPS[0], review)
        _persist_step(replay_path, 1, REVIEW_REPLAY_STEPS[1], outcome)
        _persist_step(replay_path, 2, REVIEW_REPLAY_STEPS[2], returned)
        return _review_capture(review, outcome, returned, replay_path)
    except Exception as exc:
        review = _failed_review_artifact(
            review_id=review_id,
            domain_proposal_artifact=domain_proposal_artifact,
            decision=decision,
            reviewed_by=reviewed_by,
            reviewed_at=reviewed_at,
            human_approval_reference=human_approval_reference,
            failure_reason=_failure_reason(exc),
        )
        outcome = _failed_archive_artifact(review=review, reviewed_at=reviewed_at)
        returned = _review_returned_artifact(review, outcome)
        _persist_failure_if_possible(replay_path, 0, REVIEW_REPLAY_STEPS[0], review)
        _persist_failure_if_possible(replay_path, 1, REVIEW_REPLAY_STEPS[1], outcome)
        _persist_failure_if_possible(replay_path, 2, REVIEW_REPLAY_STEPS[2], returned)
        return _review_capture(review, outcome, returned, replay_path)


def reconstruct_domain_proposal_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct domain proposal replay evidence."""

    wrappers = _load_wrappers(Path(replay_dir), PROPOSAL_REPLAY_STEPS, "domain proposal")
    proposal = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("domain_proposal_reference") != proposal["domain_proposal_id"]:
        raise FailClosedRuntimeError("domain proposal replay reference mismatch")
    if returned.get("domain_proposal_hash") != proposal["artifact_hash"]:
        raise FailClosedRuntimeError("domain proposal replay hash mismatch")
    return {
        "domain_proposal_id": proposal["domain_proposal_id"],
        "proposal_status": proposal["proposal_status"],
        "source_type": proposal["source_type"],
        "proposed_domain": proposal["proposed_domain"],
        "canonical_chain_id": proposal["canonical_chain_id"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": proposal["failure_reason"],
        "replay_hash": replay_hash(wrappers),
    }


def reconstruct_domain_proposal_review_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct domain proposal review replay evidence."""

    wrappers = _load_wrappers(Path(replay_dir), REVIEW_REPLAY_STEPS, "domain proposal review")
    review = wrappers[0]["artifact"]
    outcome = wrappers[1]["artifact"]
    returned = wrappers[2]["artifact"]
    if returned.get("domain_review_reference") != review["domain_review_id"]:
        raise FailClosedRuntimeError("domain proposal review returned reference mismatch")
    if returned.get("domain_review_hash") != review["artifact_hash"]:
        raise FailClosedRuntimeError("domain proposal review returned hash mismatch")
    if outcome.get("domain_review_hash") != review["artifact_hash"]:
        raise FailClosedRuntimeError("domain proposal review outcome lineage mismatch")
    return {
        "domain_review_id": review["domain_review_id"],
        "review_status": review["review_status"],
        "proposed_domain": review["proposed_domain"],
        "outcome_artifact_type": outcome["artifact_type"],
        "outcome_status": outcome["outcome_status"],
        "domain_candidate_created": outcome["artifact_type"] == DOMAIN_CANDIDATE_ARTIFACT_V1
        and outcome["outcome_status"] == DOMAIN_CANDIDATE_CREATED,
        "proposal_archived": outcome["artifact_type"] == DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1
        and outcome["outcome_status"] == DOMAIN_PROPOSAL_ARCHIVED,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": review["failure_reason"],
        "replay_hash": replay_hash(wrappers),
    }


def _proposal_artifact(
    *,
    proposal_id: str,
    source_type: str,
    proposed_domain: str,
    need_summary: str,
    requested_by: str,
    canonical_chain_id: str,
    created_at: str,
    source_replay_references: list[str],
    source_replay_hashes: list[str],
    proposal_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    normalized_source = _normalize_source(source_type)
    if normalized_source == "REPLAY_DERIVED_IMPROVEMENT":
        if not _string_list(source_replay_references) or not _hash_list(source_replay_hashes):
            raise FailClosedRuntimeError("domain proposal failed closed: replay-derived source lineage required")
    artifact = {
        "artifact_type": DOMAIN_PROPOSAL_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "domain_proposal_id": _require_string(proposal_id, "proposal_id"),
        "proposal_status": proposal_status,
        "source_type": normalized_source,
        "proposed_domain": _normalize_domain(proposed_domain),
        "need_summary": _require_string(need_summary, "need_summary"),
        "requested_by": _require_string(requested_by, "requested_by"),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "source_replay_references": deepcopy(source_replay_references),
        "source_replay_hashes": deepcopy(source_replay_hashes),
        "required_next_step": "HUMAN_REVIEW",
        "proposal_created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["proposal_hash"] = replay_hash(
        {
            "domain_proposal_id": artifact["domain_proposal_id"],
            "source_type": artifact["source_type"],
            "proposed_domain": artifact["proposed_domain"],
            "need_summary": artifact["need_summary"],
            "canonical_chain_id": artifact["canonical_chain_id"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_proposal_artifact(
    *,
    proposal_id: Any,
    source_type: Any,
    proposed_domain: Any,
    need_summary: Any,
    requested_by: Any,
    canonical_chain_id: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_PROPOSAL_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "domain_proposal_id": proposal_id if isinstance(proposal_id, str) and proposal_id.strip() else "INVALID",
        "proposal_status": FAILED_CLOSED,
        "source_type": source_type if isinstance(source_type, str) else None,
        "proposed_domain": proposed_domain if isinstance(proposed_domain, str) else None,
        "need_summary": need_summary if isinstance(need_summary, str) else None,
        "requested_by": requested_by if isinstance(requested_by, str) else None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "source_replay_references": [],
        "source_replay_hashes": [],
        "required_next_step": "HUMAN_REVIEW",
        "proposal_created_at": created_at if isinstance(created_at, str) else None,
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["proposal_hash"] = replay_hash(
        {
            "domain_proposal_id": artifact["domain_proposal_id"],
            "source_type": artifact["source_type"],
            "proposed_domain": artifact["proposed_domain"],
            "need_summary": artifact["need_summary"],
            "canonical_chain_id": artifact["canonical_chain_id"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _proposal_returned_artifact(proposal: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(proposal, "domain proposal artifact")
    artifact = {
        "event_type": "DOMAIN_PROPOSAL_RETURNED",
        "domain_proposal_reference": proposal["domain_proposal_id"],
        "domain_proposal_hash": proposal["artifact_hash"],
        "proposal_status": proposal["proposal_status"],
        "source_type": proposal["source_type"],
        "proposed_domain": proposal["proposed_domain"],
        "required_next_step": proposal["required_next_step"],
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": proposal["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _review_artifact(
    *,
    review_id: str,
    proposal: dict[str, Any],
    decision: str,
    decision_reason: str,
    reviewed_by: str,
    reviewed_at: str,
    human_approval_reference: str,
    review_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_REVIEW_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "domain_review_id": _require_string(review_id, "review_id"),
        "review_status": review_status,
        "domain_proposal_reference": proposal["domain_proposal_id"],
        "domain_proposal_hash": proposal["artifact_hash"],
        "source_type": proposal["source_type"],
        "proposed_domain": proposal["proposed_domain"],
        "canonical_chain_id": proposal["canonical_chain_id"],
        "decision": _normalize_decision(decision),
        "decision_reason": _require_string(decision_reason, "decision_reason"),
        "reviewed_by": _require_string(reviewed_by, "reviewed_by"),
        "reviewed_at": _require_string(reviewed_at, "reviewed_at"),
        "human_approval_reference": _require_string(human_approval_reference, "human_approval_reference"),
        "decision_authority": "HUMAN",
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_review_artifact(
    *,
    review_id: Any,
    domain_proposal_artifact: Any,
    decision: Any,
    reviewed_by: Any,
    reviewed_at: Any,
    human_approval_reference: Any,
    failure_reason: str,
) -> dict[str, Any]:
    proposal = domain_proposal_artifact if isinstance(domain_proposal_artifact, dict) else {}
    artifact = {
        "artifact_type": DOMAIN_REVIEW_DECISION_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "domain_review_id": review_id if isinstance(review_id, str) and review_id.strip() else "INVALID",
        "review_status": FAILED_CLOSED,
        "domain_proposal_reference": proposal.get("domain_proposal_id"),
        "domain_proposal_hash": proposal.get("artifact_hash"),
        "source_type": proposal.get("source_type"),
        "proposed_domain": proposal.get("proposed_domain"),
        "canonical_chain_id": proposal.get("canonical_chain_id"),
        "decision": decision if isinstance(decision, str) else None,
        "decision_reason": None,
        "reviewed_by": reviewed_by if isinstance(reviewed_by, str) else None,
        "reviewed_at": reviewed_at if isinstance(reviewed_at, str) else None,
        "human_approval_reference": human_approval_reference if isinstance(human_approval_reference, str) else None,
        "decision_authority": "HUMAN",
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _domain_candidate_artifact(*, review: dict[str, Any], proposal: dict[str, Any], reviewed_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "domain_candidate_id": f"{review['domain_review_id']}:DOMAIN-CANDIDATE",
        "outcome_status": DOMAIN_CANDIDATE_CREATED,
        "domain_review_reference": review["domain_review_id"],
        "domain_review_hash": review["artifact_hash"],
        "domain_proposal_reference": proposal["domain_proposal_id"],
        "domain_proposal_hash": proposal["artifact_hash"],
        "proposed_domain": proposal["proposed_domain"],
        "canonical_chain_id": proposal["canonical_chain_id"],
        "candidate_scope": "DOMAIN_CANDIDATE_ONLY",
        "required_next_step": "SEPARATE_DOMAIN_CREATION_AUTHORIZATION",
        "created_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _domain_archive_artifact(*, review: dict[str, Any], proposal: dict[str, Any], reviewed_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "domain_archive_id": f"{review['domain_review_id']}:DOMAIN-PROPOSAL-ARCHIVE",
        "outcome_status": DOMAIN_PROPOSAL_ARCHIVED,
        "domain_review_reference": review["domain_review_id"],
        "domain_review_hash": review["artifact_hash"],
        "domain_proposal_reference": proposal["domain_proposal_id"],
        "domain_proposal_hash": proposal["artifact_hash"],
        "proposed_domain": proposal["proposed_domain"],
        "canonical_chain_id": proposal["canonical_chain_id"],
        "archive_reason": review["decision_reason"],
        "archived_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_archive_artifact(*, review: dict[str, Any], reviewed_at: Any) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "domain_archive_id": f"{review['domain_review_id']}:DOMAIN-PROPOSAL-ARCHIVE",
        "outcome_status": FAILED_CLOSED,
        "domain_review_reference": review["domain_review_id"],
        "domain_review_hash": review["artifact_hash"],
        "domain_proposal_reference": review.get("domain_proposal_reference"),
        "domain_proposal_hash": review.get("domain_proposal_hash"),
        "proposed_domain": review.get("proposed_domain"),
        "canonical_chain_id": review.get("canonical_chain_id"),
        "archive_reason": review["failure_reason"],
        "archived_at": reviewed_at if isinstance(reviewed_at, str) else None,
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": review["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _review_returned_artifact(review: dict[str, Any], outcome: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(review, "domain review artifact")
    _verify_artifact_hash(outcome, "domain review outcome artifact")
    artifact = {
        "event_type": "DOMAIN_REVIEW_RETURNED",
        "domain_review_reference": review["domain_review_id"],
        "domain_review_hash": review["artifact_hash"],
        "outcome_reference": outcome.get("domain_candidate_id") or outcome.get("domain_archive_id"),
        "outcome_hash": outcome["artifact_hash"],
        "outcome_artifact_type": outcome["artifact_type"],
        "outcome_status": outcome["outcome_status"],
        "review_status": review["review_status"],
        "proposed_domain": review["proposed_domain"],
        "replay_visible": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": review["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _proposal_capture(proposal: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "proposal_status": proposal["proposal_status"],
        "domain_proposal_artifact": deepcopy(proposal),
        "domain_proposal_returned_artifact": deepcopy(returned),
        "domain_proposal_replay_reference": str(replay_path),
        "domain_proposal_created": proposal["proposal_status"] == DOMAIN_PROPOSAL_CREATED,
        "replay_lineage_preserved": True,
        "approval_required": proposal["approval_required"],
        "domain_created": False,
        "failure_reason": proposal["failure_reason"],
    }
    capture["domain_proposal_capture_hash"] = replay_hash(capture)
    return capture


def _review_capture(
    review: dict[str, Any],
    outcome: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME_VERSION,
        "review_status": review["review_status"],
        "domain_review_decision_artifact": deepcopy(review),
        "domain_review_outcome_artifact": deepcopy(outcome),
        "domain_review_returned_artifact": deepcopy(returned),
        "domain_review_replay_reference": str(replay_path),
        "domain_candidate_created": outcome["artifact_type"] == DOMAIN_CANDIDATE_ARTIFACT_V1
        and outcome["outcome_status"] == DOMAIN_CANDIDATE_CREATED,
        "proposal_archived": outcome["artifact_type"] == DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1
        and outcome["outcome_status"] == DOMAIN_PROPOSAL_ARCHIVED,
        "approval_required": review["approval_required"],
        "domain_created": False,
        "replay_lineage_preserved": True,
        "failure_reason": review["failure_reason"],
    }
    capture["domain_proposal_review_capture_hash"] = replay_hash(capture)
    return capture


def _validate_proposal(proposal: dict[str, Any]) -> None:
    _validate_artifact(proposal, "domain proposal artifact")
    if proposal.get("artifact_type") != DOMAIN_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain proposal review failed closed: invalid proposal artifact")
    if proposal.get("proposal_status") != DOMAIN_PROPOSAL_CREATED:
        raise FailClosedRuntimeError("domain proposal review failed closed: created proposal required")
    if proposal.get("proposal_authoritative") is not False:
        raise FailClosedRuntimeError("domain proposal review failed closed: proposal authority invalid")
    if proposal.get("approval_required") is not True:
        raise FailClosedRuntimeError("domain proposal review failed closed: approval requirement missing")
    for flag in (
        "domain_created",
        "domain_registered",
        "domain_activated",
        "live_registry_mutated",
        "ppp_invoked",
        "provider_invoked",
        "worker_invoked",
        "execution_started",
        "authorization_created",
    ):
        if proposal.get(flag) is not False:
            raise FailClosedRuntimeError(f"domain proposal review failed closed: proposal {flag} must be false")


def _load_wrappers(replay_path: Path, steps: tuple[str, ...], label: str) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError(f"{label} replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(f"{label} replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"{label} artifact")
        wrappers.append(wrapper)
    return wrappers


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "domain proposal governance artifact")
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path, steps: tuple[str, ...]) -> None:
    for index, step in enumerate(steps):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("domain proposal governance failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} missing")
    _verify_artifact_hash(artifact, label)


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("domain proposal governance replay hash is required")
    candidate = deepcopy(wrapper)
    candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("domain proposal governance replay hash mismatch")


def _normalize_source(value: Any) -> str:
    normalized = _require_string(value, "source_type").upper()
    if normalized not in VALID_SOURCE_TYPES:
        raise FailClosedRuntimeError("domain proposal failed closed: unsupported source type")
    return normalized


def _normalize_decision(value: Any) -> str:
    normalized = _require_string(value, "decision").upper()
    if normalized not in VALID_REVIEW_DECISIONS:
        raise FailClosedRuntimeError("domain proposal review failed closed: invalid decision")
    return normalized


def _normalize_domain(value: Any) -> str:
    domain = _require_string(value, "proposed_domain").strip()
    if not domain.replace("_", "").replace("-", "").isalnum():
        raise FailClosedRuntimeError("domain proposal failed closed: invalid proposed domain")
    return domain


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"domain proposal governance failed closed: {field_name} is required")
    return value.strip()


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _hash_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.startswith("sha256:") for item in value
    )


def _failure_reason(exc: Exception) -> str:
    message = str(exc).strip()
    return message or "domain proposal governance failed closed"
