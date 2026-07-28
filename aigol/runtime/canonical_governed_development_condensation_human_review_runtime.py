"""Exact human-review presentation for dormant canonical condensation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.canonical_governed_development_condensation_runtime import (
    G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT,
    G31_CODEX_SYNTHESIS_PREFIX,
    content_sha256,
    validate_canonical_condensation_artifact,
)
from aigol.runtime.canonical_governed_development_condensation_validation_runtime import (
    CANONICAL_CONDENSATION_VALIDATION_PASS,
    CANONICAL_CONDENSATION_VALIDATOR_VERSION,
    validate_canonical_condensation_validation_result,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CANONICAL_CONDENSATION_HUMAN_REVIEW_PRESENTATION_V1 = (
    "CANONICAL_CONDENSATION_HUMAN_REVIEW_PRESENTATION_V1"
)
CANONICAL_CONDENSATION_HUMAN_REVIEW_SCHEMA_VERSION = "1.0.0"
CANONICAL_CONDENSATION_SEMANTIC_REPRESENTATION_ONLY = (
    "SEMANTIC_REPRESENTATION_ONLY"
)
CANONICAL_CONDENSATION_REVIEW_WARNING = (
    "Approval concerns only the exact semantic representation displayed here. "
    "It creates no execution, Worker, mutation, CODEX synthesis, handoff, "
    "deployment, or authorization authority."
)
CANONICAL_CONDENSATION_DECISION_OUTCOMES = ("APPROVE", "REJECT")

REVIEW_AUTHORITY_BOUNDARIES = {
    "approval_created": False,
    "semantic_representation_approved": False,
    "approved_projection_created": False,
    "authorization_created": False,
    "execution_authorized": False,
    "worker_selected": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "execution_gate_reached": False,
    "repository_mutated": False,
    "g31_input_binding_created": False,
    "g31_preflight_invoked": False,
    "codex_synthesis_authorized": False,
    "handoff_authorized": False,
    "deployment_authorized": False,
    "capability_registered": False,
    "replay_visible": True,
}
_REVIEW_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_version",
        "review_id",
        "review_hash",
        "decision_scope",
        "valid_decision_outcomes",
        "reviewed_by",
        "presented_at",
        "review_warning",
        "source_request",
        "source_request_commitment",
        "source_bundle_hash",
        "condensation_proposal",
        "proposal_commitment",
        "deterministic_validation_result",
        "validation_commitment",
        "validation_id",
        "validation_version",
        "validation_status",
        "model_d_projection",
        "phase1_replay_reference",
        "explicit_human_action_required",
        "decision_pending",
        *REVIEW_AUTHORITY_BOUNDARIES.keys(),
    }
)


def create_canonical_condensation_human_review(
    *,
    proposal: dict[str, Any],
    validation_result: dict[str, Any],
    phase1_replay_dir: str | Path,
    reviewed_by: str,
    presented_at: str,
) -> dict[str, Any]:
    """Create the exact, non-authoritative object shown for human review."""

    phase1 = _phase1_reconstruction(phase1_replay_dir)
    canonical_proposal = validate_canonical_condensation_artifact(proposal)
    canonical_validation = validate_canonical_condensation_validation_result(
        validation_result,
        proposal=canonical_proposal,
    )
    if phase1["proposal"] != canonical_proposal:
        raise FailClosedRuntimeError(
            "canonical condensation review proposal Replay mismatch"
        )
    if phase1["validation_result"] != canonical_validation:
        raise FailClosedRuntimeError(
            "canonical condensation review validation Replay mismatch"
        )
    if (
        canonical_validation.get("validation_status")
        != CANONICAL_CONDENSATION_VALIDATION_PASS
    ):
        raise FailClosedRuntimeError(
            "canonical condensation review requires validation PASS"
        )
    actor = _required_exact_text(reviewed_by, "reviewed_by")
    timestamp = _required_exact_text(presented_at, "presented_at")
    source = canonical_proposal["source_lineage"]["original_request"]
    projection = _exact_projection(canonical_proposal)
    artifact = {
        "artifact_type": CANONICAL_CONDENSATION_HUMAN_REVIEW_PRESENTATION_V1,
        "schema_version": CANONICAL_CONDENSATION_HUMAN_REVIEW_SCHEMA_VERSION,
        "decision_scope": CANONICAL_CONDENSATION_SEMANTIC_REPRESENTATION_ONLY,
        "valid_decision_outcomes": list(
            CANONICAL_CONDENSATION_DECISION_OUTCOMES
        ),
        "reviewed_by": actor,
        "presented_at": timestamp,
        "review_warning": CANONICAL_CONDENSATION_REVIEW_WARNING,
        "source_request": deepcopy(source),
        "source_request_commitment": source["original_request_sha256"],
        "source_bundle_hash": canonical_proposal["source_lineage"][
            "source_bundle_hash"
        ],
        "condensation_proposal": deepcopy(canonical_proposal),
        "proposal_commitment": canonical_proposal["condensation_hash"],
        "deterministic_validation_result": deepcopy(canonical_validation),
        "validation_commitment": canonical_validation["validation_hash"],
        "validation_id": canonical_validation["validation_id"],
        "validation_version": canonical_validation["validator_version"],
        "validation_status": canonical_validation["validation_status"],
        "model_d_projection": projection,
        "phase1_replay_reference": {
            "replay_family": phase1["replay_family"],
            "replay_family_hash": phase1["replay_family_hash"],
            "record_hashes": deepcopy(phase1["record_hashes"]),
            "replay_location": str(Path(phase1_replay_dir)),
        },
        "explicit_human_action_required": True,
        "decision_pending": True,
        **deepcopy(REVIEW_AUTHORITY_BOUNDARIES),
    }
    identity_seed = deepcopy(artifact)
    review_hash = replay_hash(identity_seed)
    artifact["review_id"] = (
        "CANONICAL-CONDENSATION-REVIEW-"
        f"{review_hash.removeprefix('sha256:')[:24]}"
    )
    artifact["review_hash"] = review_hash
    validate_canonical_condensation_human_review(
        artifact,
        phase1_replay_dir=phase1_replay_dir,
    )
    return deepcopy(artifact)


def validate_canonical_condensation_human_review(
    review: dict[str, Any],
    *,
    phase1_replay_dir: str | Path | None = None,
    phase1_reconstruction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reconstruct the displayed object and reject any hidden substitution."""

    if not isinstance(review, dict):
        raise FailClosedRuntimeError(
            "canonical condensation human review artifact required"
        )
    candidate = deepcopy(review)
    if frozenset(candidate) != _REVIEW_FIELDS:
        raise FailClosedRuntimeError(
            "canonical condensation human review field set mismatch"
        )
    if (
        candidate.get("artifact_type")
        != CANONICAL_CONDENSATION_HUMAN_REVIEW_PRESENTATION_V1
        or candidate.get("schema_version")
        != CANONICAL_CONDENSATION_HUMAN_REVIEW_SCHEMA_VERSION
    ):
        raise FailClosedRuntimeError(
            "canonical condensation human review schema mismatch"
        )
    for field, expected in REVIEW_AUTHORITY_BOUNDARIES.items():
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(
                f"canonical condensation human review boundary mismatch: {field}"
            )
    identity_seed = deepcopy(candidate)
    actual_id = identity_seed.pop("review_id", None)
    actual_hash = identity_seed.pop("review_hash", None)
    expected_hash = replay_hash(identity_seed)
    expected_id = (
        "CANONICAL-CONDENSATION-REVIEW-"
        f"{expected_hash.removeprefix('sha256:')[:24]}"
    )
    if actual_hash != expected_hash or actual_id != expected_id:
        raise FailClosedRuntimeError(
            "canonical condensation human review identity mismatch"
        )

    phase1, replay_location = _review_phase1_context(
        candidate,
        phase1_replay_dir=phase1_replay_dir,
        phase1_reconstruction=phase1_reconstruction,
    )
    proposal = validate_canonical_condensation_artifact(
        candidate.get("condensation_proposal")
    )
    validation = validate_canonical_condensation_validation_result(
        candidate.get("deterministic_validation_result"),
        proposal=proposal,
    )
    if validation.get("validation_status") != CANONICAL_CONDENSATION_VALIDATION_PASS:
        raise FailClosedRuntimeError(
            "canonical condensation human review validation is not PASS"
        )
    if validation.get("validator_version") != CANONICAL_CONDENSATION_VALIDATOR_VERSION:
        raise FailClosedRuntimeError(
            "canonical condensation human review validator version unsupported"
        )
    source = proposal["source_lineage"]["original_request"]
    expected_replay_reference = {
        "replay_family": phase1["replay_family"],
        "replay_family_hash": phase1["replay_family_hash"],
        "record_hashes": deepcopy(phase1["record_hashes"]),
        "replay_location": replay_location,
    }
    checks = (
        candidate.get("decision_scope")
        == CANONICAL_CONDENSATION_SEMANTIC_REPRESENTATION_ONLY,
        candidate.get("valid_decision_outcomes")
        == list(CANONICAL_CONDENSATION_DECISION_OUTCOMES),
        candidate.get("review_warning") == CANONICAL_CONDENSATION_REVIEW_WARNING,
        candidate.get("source_request") == source,
        candidate.get("source_request_commitment")
        == source["original_request_sha256"],
        candidate.get("source_bundle_hash")
        == proposal["source_lineage"]["source_bundle_hash"],
        candidate.get("proposal_commitment") == proposal["condensation_hash"],
        candidate.get("validation_commitment") == validation["validation_hash"],
        candidate.get("validation_id") == validation["validation_id"],
        candidate.get("validation_version") == validation["validator_version"],
        candidate.get("validation_status") == validation["validation_status"],
        candidate.get("model_d_projection") == _exact_projection(proposal),
        candidate.get("phase1_replay_reference") == expected_replay_reference,
        phase1["proposal"] == proposal,
        phase1["validation_result"] == validation,
        candidate.get("explicit_human_action_required") is True,
        candidate.get("decision_pending") is True,
        isinstance(candidate.get("reviewed_by"), str)
        and bool(candidate.get("reviewed_by"))
        and candidate.get("reviewed_by")
        == candidate.get("reviewed_by").strip(),
        isinstance(candidate.get("presented_at"), str)
        and bool(candidate.get("presented_at"))
        and candidate.get("presented_at")
        == candidate.get("presented_at").strip(),
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "canonical condensation human review reconstruction mismatch"
        )
    return candidate


def render_canonical_condensation_human_review(
    review: dict[str, Any],
    *,
    phase1_replay_dir: str | Path,
) -> str:
    """Render every exact value the human would approve or reject."""

    candidate = validate_canonical_condensation_human_review(
        review,
        phase1_replay_dir=phase1_replay_dir,
    )
    projection = candidate["model_d_projection"]
    return "\n".join(
        (
            "Canonical Condensation Human Review",
            f"Review ID: {candidate['review_id']}",
            f"Decision Scope: {candidate['decision_scope']}",
            f"Valid Outcomes: {', '.join(candidate['valid_decision_outcomes'])}",
            "",
            "Exact Original Source Request:",
            candidate["source_request"]["original_request"],
            (
                "Source Request SHA-256: "
                f"{candidate['source_request_commitment']}"
            ),
            f"Source Bundle Hash: {candidate['source_bundle_hash']}",
            "",
            "Exact Condensation Proposal (canonical JSON):",
            canonical_serialize(candidate["condensation_proposal"]),
            f"Proposal Commitment: {candidate['proposal_commitment']}",
            "",
            "Exact Deterministic Validation (canonical JSON):",
            canonical_serialize(candidate["deterministic_validation_result"]),
            f"Validation ID: {candidate['validation_id']}",
            f"Validation Version: {candidate['validation_version']}",
            f"Validation Status: {candidate['validation_status']}",
            f"Validation Commitment: {candidate['validation_commitment']}",
            "",
            f"Exact Prefix: {projection['prefix']}",
            f"Prefix UTF-8 Bytes: {projection['prefix_utf8_byte_count']}",
            f"Prefix Code Points: {projection['prefix_code_point_count']}",
            f"Prefix SHA-256: {projection['prefix_sha256']}",
            f"Exact Proposed Synthesis Body: {projection['synthesis_body']}",
            (
                "Body UTF-8 Bytes: "
                f"{projection['synthesis_body_utf8_byte_count']}"
            ),
            (
                "Body Code Points: "
                f"{projection['synthesis_body_code_point_count']}"
            ),
            f"Body SHA-256: {projection['synthesis_body_sha256']}",
            f"Exact Complete Projection: {projection['complete_projection']}",
            (
                "Projection UTF-8 Bytes: "
                f"{projection['complete_projection_utf8_byte_count']}"
            ),
            (
                "Projection Code Points: "
                f"{projection['complete_projection_code_point_count']}"
            ),
            (
                "Projection SHA-256: "
                f"{projection['complete_projection_sha256']}"
            ),
            (
                "Phase 1 Replay Family Hash: "
                f"{candidate['phase1_replay_reference']['replay_family_hash']}"
            ),
            "",
            candidate["review_warning"],
            "An exact explicit APPROVE or REJECT decision is required.",
        )
    )


def _exact_projection(proposal: dict[str, Any]) -> dict[str, Any]:
    prefix = proposal["projection_prefix"]
    body = proposal["proposed_synthesis_body"]
    complete = proposal["proposed_projection"]
    if (
        prefix != G31_CODEX_SYNTHESIS_PREFIX
        or complete != prefix + body
        or len(complete) > G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT
    ):
        raise FailClosedRuntimeError(
            "canonical condensation Model D projection mismatch"
        )
    projection = {
        "model": "MODEL_D",
        "prefix": prefix,
        "prefix_code_point_count": len(prefix),
        "prefix_utf8_byte_count": len(prefix.encode("utf-8")),
        "prefix_sha256": content_sha256(prefix),
        "synthesis_body": body,
        "synthesis_body_code_point_count": len(body),
        "synthesis_body_utf8_byte_count": len(body.encode("utf-8")),
        "synthesis_body_sha256": content_sha256(body),
        "complete_projection": complete,
        "complete_projection_code_point_count": len(complete),
        "complete_projection_utf8_byte_count": len(complete.encode("utf-8")),
        "complete_projection_sha256": content_sha256(complete),
    }
    projection["projection_commitment"] = replay_hash(projection)
    return projection


def _phase1_reconstruction(replay_dir: str | Path) -> dict[str, Any]:
    from aigol.runtime.canonical_governed_development_condensation_replay import (
        reconstruct_canonical_condensation_phase1_replay,
    )

    return reconstruct_canonical_condensation_phase1_replay(replay_dir)


def _review_phase1_context(
    review: dict[str, Any],
    *,
    phase1_replay_dir: str | Path | None,
    phase1_reconstruction: dict[str, Any] | None,
) -> tuple[dict[str, Any], str]:
    if (phase1_replay_dir is None) == (phase1_reconstruction is None):
        raise FailClosedRuntimeError(
            "exactly one canonical condensation Phase 1 Replay source is required"
        )
    if phase1_replay_dir is not None:
        return _phase1_reconstruction(phase1_replay_dir), str(
            Path(phase1_replay_dir)
        )
    if not isinstance(phase1_reconstruction, dict):
        raise FailClosedRuntimeError(
            "canonical condensation Phase 1 reconstruction required"
        )
    reference = review.get("phase1_replay_reference")
    if not isinstance(reference, dict):
        raise FailClosedRuntimeError(
            "canonical condensation Phase 1 Replay reference required"
        )
    location = reference.get("replay_location")
    if not isinstance(location, str) or not location:
        raise FailClosedRuntimeError(
            "canonical condensation Phase 1 Replay location required"
        )
    return deepcopy(phase1_reconstruction), location


def _required_exact_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise FailClosedRuntimeError(f"{field} must be exact non-empty text")
    return value
