"""Explicit semantic-representation decisions for canonical condensation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.canonical_governed_development_condensation_human_review_runtime import (
    CANONICAL_CONDENSATION_HUMAN_REVIEW_PRESENTATION_V1,
    CANONICAL_CONDENSATION_SEMANTIC_REPRESENTATION_ONLY,
    validate_canonical_condensation_human_review,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CANONICAL_CONDENSATION_HUMAN_DECISION_V1 = (
    "CANONICAL_CONDENSATION_HUMAN_DECISION_V1"
)
CANONICAL_CONDENSATION_HUMAN_DECISION_SCHEMA_VERSION = "1.0.0"
CANONICAL_CONDENSATION_APPROVE = "APPROVE"
CANONICAL_CONDENSATION_REJECT = "REJECT"
CANONICAL_CONDENSATION_VALID_DECISIONS = frozenset(
    {CANONICAL_CONDENSATION_APPROVE, CANONICAL_CONDENSATION_REJECT}
)

DECISION_NO_EXECUTION_BOUNDARIES = {
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


def create_canonical_condensation_human_decision(
    *,
    review: dict[str, Any],
    phase1_replay_dir: str | Path,
    decision: str,
    decided_by: str,
    decided_at: str,
) -> dict[str, Any]:
    """Record one exact explicit APPROVE or REJECT decision artifact."""

    canonical_review = validate_canonical_condensation_human_review(
        review,
        phase1_replay_dir=phase1_replay_dir,
    )
    if decision not in CANONICAL_CONDENSATION_VALID_DECISIONS:
        raise FailClosedRuntimeError(
            "canonical condensation decision must be explicit APPROVE or REJECT"
        )
    actor = _required_exact_text(decided_by, "decided_by")
    timestamp = _required_exact_text(decided_at, "decided_at")
    if actor != canonical_review["reviewed_by"]:
        raise FailClosedRuntimeError(
            "canonical condensation decision actor did not receive review"
        )
    artifact = _decision_artifact(
        review=canonical_review,
        decision=decision,
        decided_by=actor,
        decided_at=timestamp,
    )
    validate_canonical_condensation_human_decision(
        artifact,
        review=canonical_review,
        phase1_replay_dir=phase1_replay_dir,
    )
    return deepcopy(artifact)


def validate_canonical_condensation_human_decision(
    decision_artifact: dict[str, Any],
    *,
    review: dict[str, Any],
    phase1_replay_dir: str | Path | None = None,
    phase1_reconstruction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Recompute one decision and its exact approval or rejection semantics."""

    if not isinstance(decision_artifact, dict):
        raise FailClosedRuntimeError(
            "canonical condensation human decision artifact required"
        )
    candidate = deepcopy(decision_artifact)
    canonical_review = validate_canonical_condensation_human_review(
        review,
        phase1_replay_dir=phase1_replay_dir,
        phase1_reconstruction=phase1_reconstruction,
    )
    if (
        candidate.get("artifact_type")
        != CANONICAL_CONDENSATION_HUMAN_DECISION_V1
        or candidate.get("schema_version")
        != CANONICAL_CONDENSATION_HUMAN_DECISION_SCHEMA_VERSION
    ):
        raise FailClosedRuntimeError(
            "canonical condensation human decision schema mismatch"
        )
    decision = candidate.get("decision")
    if decision not in CANONICAL_CONDENSATION_VALID_DECISIONS:
        raise FailClosedRuntimeError(
            "canonical condensation human decision is malformed or ambiguous"
        )
    for field, expected in DECISION_NO_EXECUTION_BOUNDARIES.items():
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(
                f"canonical condensation decision boundary mismatch: {field}"
            )
    expected = _decision_artifact(
        review=canonical_review,
        decision=decision,
        decided_by=candidate.get("decided_by"),
        decided_at=candidate.get("decided_at"),
    )
    if candidate != expected:
        raise FailClosedRuntimeError(
            "canonical condensation human decision reconstruction mismatch"
        )
    return candidate


def _decision_artifact(
    *,
    review: dict[str, Any],
    decision: str,
    decided_by: Any,
    decided_at: Any,
) -> dict[str, Any]:
    actor = _required_exact_text(decided_by, "decided_by")
    timestamp = _required_exact_text(decided_at, "decided_at")
    if actor != review["reviewed_by"]:
        raise FailClosedRuntimeError(
            "canonical condensation decision actor mismatch"
        )
    projection = deepcopy(review["model_d_projection"])
    approved_projection = None
    approved_projection_hash = None
    if decision == CANONICAL_CONDENSATION_APPROVE:
        approved_projection = {
            "artifact_type": "CANONICAL_CONDENSATION_APPROVED_PROJECTION_V1",
            "approval_scope": (
                CANONICAL_CONDENSATION_SEMANTIC_REPRESENTATION_ONLY
            ),
            "prefix": projection["prefix"],
            "prefix_code_point_count": projection["prefix_code_point_count"],
            "prefix_utf8_byte_count": projection["prefix_utf8_byte_count"],
            "prefix_sha256": projection["prefix_sha256"],
            "approved_synthesis_body": projection["synthesis_body"],
            "approved_synthesis_body_code_point_count": projection[
                "synthesis_body_code_point_count"
            ],
            "approved_synthesis_body_utf8_byte_count": projection[
                "synthesis_body_utf8_byte_count"
            ],
            "approved_synthesis_body_sha256": projection[
                "synthesis_body_sha256"
            ],
            "approved_projection": projection["complete_projection"],
            "approved_projection_code_point_count": projection[
                "complete_projection_code_point_count"
            ],
            "approved_projection_utf8_byte_count": projection[
                "complete_projection_utf8_byte_count"
            ],
            "approved_projection_sha256": projection[
                "complete_projection_sha256"
            ],
            "proposal_commitment": review["proposal_commitment"],
            "validation_commitment": review["validation_commitment"],
            "review_commitment": review["review_hash"],
            "phase1_replay_family_hash": review["phase1_replay_reference"][
                "replay_family_hash"
            ],
            "execution_authorized": False,
            "g31_input_binding_created": False,
        }
        approved_projection_hash = replay_hash(approved_projection)
        approved_projection["approved_projection_artifact_hash"] = (
            approved_projection_hash
        )

    artifact = {
        "artifact_type": CANONICAL_CONDENSATION_HUMAN_DECISION_V1,
        "schema_version": CANONICAL_CONDENSATION_HUMAN_DECISION_SCHEMA_VERSION,
        "decision_scope": CANONICAL_CONDENSATION_SEMANTIC_REPRESENTATION_ONLY,
        "decision": decision,
        "explicit_human_action": True,
        "decided_by": actor,
        "decided_at": timestamp,
        "review_id": review["review_id"],
        "review_commitment": review["review_hash"],
        "source_request_commitment": review["source_request_commitment"],
        "source_bundle_hash": review["source_bundle_hash"],
        "proposal_commitment": review["proposal_commitment"],
        "validation_commitment": review["validation_commitment"],
        "phase1_replay_family_hash": review["phase1_replay_reference"][
            "replay_family_hash"
        ],
        "exact_prefix": projection["prefix"],
        "exact_prefix_sha256": projection["prefix_sha256"],
        "exact_synthesis_body": projection["synthesis_body"],
        "exact_synthesis_body_sha256": projection["synthesis_body_sha256"],
        "exact_complete_projection": projection["complete_projection"],
        "exact_complete_projection_sha256": projection[
            "complete_projection_sha256"
        ],
        "projection_commitment": projection["projection_commitment"],
        "approval_created": decision == CANONICAL_CONDENSATION_APPROVE,
        "semantic_representation_approved": (
            decision == CANONICAL_CONDENSATION_APPROVE
        ),
        "approved_projection_created": (
            decision == CANONICAL_CONDENSATION_APPROVE
        ),
        "approved_projection": approved_projection,
        "approved_projection_artifact_hash": approved_projection_hash,
        "rejection_final_for_review": decision == CANONICAL_CONDENSATION_REJECT,
        **deepcopy(DECISION_NO_EXECUTION_BOUNDARIES),
    }
    identity_seed = deepcopy(artifact)
    decision_hash = replay_hash(identity_seed)
    artifact["human_decision_id"] = (
        "CANONICAL-CONDENSATION-DECISION-"
        f"{decision_hash.removeprefix('sha256:')[:24]}"
    )
    artifact["human_decision_hash"] = decision_hash
    return artifact


def _required_exact_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise FailClosedRuntimeError(f"{field} must be exact non-empty text")
    return value
