"""Dormant exact binding from approved condensation Replay to future G31 input."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.canonical_governed_development_condensation_human_decision_runtime import (
    CANONICAL_CONDENSATION_APPROVE,
    CANONICAL_CONDENSATION_HUMAN_DECISION_SCHEMA_VERSION,
    CANONICAL_CONDENSATION_HUMAN_DECISION_V1,
)
from aigol.runtime.canonical_governed_development_condensation_human_review_runtime import (
    CANONICAL_CONDENSATION_HUMAN_REVIEW_PRESENTATION_V1,
    CANONICAL_CONDENSATION_HUMAN_REVIEW_SCHEMA_VERSION,
)
from aigol.runtime.canonical_governed_development_condensation_replay import (
    CANONICAL_CONDENSATION_REPLAY_EXTENSION_SCHEMA_VERSION,
    CANONICAL_CONDENSATION_REPLAY_EXTENSION_V1,
    reconstruct_canonical_condensation_review_decision_replay,
)
from aigol.runtime.canonical_governed_development_condensation_runtime import (
    CANONICAL_CONDENSATION_ARTIFACT_V1,
    CANONICAL_CONDENSATION_ARTIFACT_VERSION,
    CANONICAL_CONDENSATION_SCHEMA_V1,
    CANONICAL_CONDENSATION_SCHEMA_VERSION,
    G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT,
    G31_CODEX_SYNTHESIS_PREFIX,
    content_sha256,
)
from aigol.runtime.canonical_governed_development_condensation_validation_runtime import (
    CANONICAL_CONDENSATION_VALIDATION_PASS,
    CANONICAL_CONDENSATION_VALIDATION_RESULT_V1,
    CANONICAL_CONDENSATION_VALIDATOR_VERSION,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CANONICAL_CONDENSATION_G31_INPUT_BINDING_V1 = (
    "CANONICAL_CONDENSATION_G31_INPUT_BINDING_V1"
)
CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_V1 = (
    "CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_V1"
)
CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_VERSION = "1.0.0"
CANONICAL_CONDENSATION_G31_INPUT_BINDING_RUNTIME_VERSION = "1.0.0"
CANONICAL_CONDENSATION_MODEL_D = "MODEL_D"
CANONICAL_CONDENSATION_G31_PREFLIGHT_TUPLE_V1 = (
    "CANONICAL_CONDENSATION_G31_PREFLIGHT_INPUT_TUPLE_V1"
)
ELIGIBLE_FOR_G31_PREFLIGHT = "ELIGIBLE_FOR_G31_PREFLIGHT"

BINDING_AUTHORITY_BOUNDARIES = {
    "g31_input_binding_created": True,
    "eligible_for_g31_preflight": True,
    "g31_preflight_invoked": False,
    "g31_preflight_passed": False,
    "codex_synthesis_authorized": False,
    "authorization_created": False,
    "execution_authorized": False,
    "worker_selected": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "execution_gate_reached": False,
    "handoff_authorized": False,
    "deployment_authorized": False,
    "repository_mutated": False,
    "capability_registered": False,
    "replay_written": False,
    "replay_visible": True,
}


def create_canonical_condensation_g31_input_binding(
    *,
    approved_replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct one approved chain and create a non-executing G31 binding."""

    reconstruction = reconstruct_canonical_condensation_review_decision_replay(
        approved_replay_dir
    )
    binding = _binding_from_reconstruction(reconstruction)
    validate_canonical_condensation_g31_input_binding(
        binding,
        approved_replay_dir=approved_replay_dir,
    )
    return deepcopy(binding)


def validate_canonical_condensation_g31_input_binding(
    binding: dict[str, Any],
    *,
    approved_replay_dir: str | Path,
) -> dict[str, Any]:
    """Reproduce the binding from Replay and require complete exact equality."""

    if not isinstance(binding, dict):
        raise FailClosedRuntimeError(
            "canonical condensation G31 input binding artifact required"
        )
    candidate = deepcopy(binding)
    if (
        candidate.get("artifact_type")
        != CANONICAL_CONDENSATION_G31_INPUT_BINDING_V1
        or candidate.get("schema_id")
        != CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_V1
        or candidate.get("schema_version")
        != CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_VERSION
        or candidate.get("runtime_version")
        != CANONICAL_CONDENSATION_G31_INPUT_BINDING_RUNTIME_VERSION
    ):
        raise FailClosedRuntimeError(
            "canonical condensation G31 input binding schema mismatch"
        )
    for field, expected in BINDING_AUTHORITY_BOUNDARIES.items():
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(
                f"canonical condensation G31 binding boundary mismatch: {field}"
            )
    reconstruction = reconstruct_canonical_condensation_review_decision_replay(
        approved_replay_dir
    )
    expected = _binding_from_reconstruction(reconstruction)
    if candidate != expected:
        raise FailClosedRuntimeError(
            "canonical condensation G31 input binding reconstruction mismatch"
        )
    return candidate


def reconstruct_canonical_condensation_g31_input_binding(
    *,
    approved_replay_dir: str | Path,
) -> dict[str, Any]:
    """Recreate the same deterministic binding from immutable Replay."""

    return create_canonical_condensation_g31_input_binding(
        approved_replay_dir=approved_replay_dir
    )


def _binding_from_reconstruction(
    reconstruction: dict[str, Any],
) -> dict[str, Any]:
    proposal = reconstruction.get("proposal")
    validation = reconstruction.get("validation_result")
    review = reconstruction.get("review")
    decision = reconstruction.get("decision_artifact")
    approved = reconstruction.get("approved_projection")
    if not all(
        isinstance(value, dict)
        for value in (proposal, validation, review, decision, approved)
    ):
        raise FailClosedRuntimeError(
            "approved canonical condensation chain is incomplete"
        )
    if validation.get("validation_status") != CANONICAL_CONDENSATION_VALIDATION_PASS:
        raise FailClosedRuntimeError(
            "canonical condensation G31 binding requires validation PASS"
        )
    if (
        decision.get("decision") != CANONICAL_CONDENSATION_APPROVE
        or decision.get("explicit_human_action") is not True
        or decision.get("semantic_representation_approved") is not True
        or decision.get("approved_projection_created") is not True
        or reconstruction.get("approved_projection_created") is not True
    ):
        raise FailClosedRuntimeError(
            "canonical condensation G31 binding requires explicit approval"
        )

    source = proposal.get("source_lineage", {}).get("original_request")
    if not isinstance(source, dict):
        raise FailClosedRuntimeError(
            "canonical condensation G31 binding source request missing"
        )
    original = _exact_text(source.get("original_request"), "original source request")
    prefix = _exact_text(approved.get("prefix"), "approved projection prefix")
    body = _exact_text(
        approved.get("approved_synthesis_body"),
        "approved synthesis body",
    )
    complete = _exact_text(
        approved.get("approved_projection"),
        "approved complete projection",
    )
    if prefix != G31_CODEX_SYNTHESIS_PREFIX or complete != prefix + body:
        raise FailClosedRuntimeError(
            "canonical condensation G31 binding Model D mismatch"
        )
    if len(complete) > G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT:
        raise FailClosedRuntimeError(
            "canonical condensation G31 binding exceeds preflight bound"
        )

    source_commitment = _value_commitment(original)
    prefix_commitment = _value_commitment(prefix)
    body_commitment = _value_commitment(body)
    projection_commitment = _value_commitment(complete)
    _verify_approved_value(
        approved,
        role="prefix",
        value=prefix,
        commitment=prefix_commitment,
    )
    _verify_approved_value(
        approved,
        role="approved_synthesis_body",
        value=body,
        commitment=body_commitment,
    )
    _verify_approved_value(
        approved,
        role="approved_projection",
        value=complete,
        commitment=projection_commitment,
    )
    preflight_tuple = {
        "tuple_contract": CANONICAL_CONDENSATION_G31_PREFLIGHT_TUPLE_V1,
        "binding_schema_id": CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_V1,
        "binding_schema_version": (
            CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_VERSION
        ),
        "g31_function_argument": {
            "value": body,
            **deepcopy(body_commitment),
        },
        "g31_final_measured_request": {
            "value": complete,
            **deepcopy(projection_commitment),
        },
    }
    preflight_tuple_hash = replay_hash(preflight_tuple)
    artifact_versions = {
        "proposal_artifact_type": proposal.get("artifact_type"),
        "proposal_schema_id": proposal.get("schema_id"),
        "proposal_schema_version": proposal.get("schema_version"),
        "proposal_artifact_version": proposal.get("artifact_version"),
        "validation_artifact_type": validation.get("artifact_type"),
        "validation_schema_version": validation.get("schema_version"),
        "validator_version": validation.get("validator_version"),
        "review_artifact_type": review.get("artifact_type"),
        "review_schema_version": review.get("schema_version"),
        "decision_artifact_type": decision.get("artifact_type"),
        "decision_schema_version": decision.get("schema_version"),
        "approved_projection_artifact_type": approved.get("artifact_type"),
        "replay_extension": reconstruction.get("replay_extension"),
        "replay_extension_schema_version": (
            CANONICAL_CONDENSATION_REPLAY_EXTENSION_SCHEMA_VERSION
        ),
    }
    _verify_supported_versions(artifact_versions)

    artifact = {
        "artifact_type": CANONICAL_CONDENSATION_G31_INPUT_BINDING_V1,
        "schema_id": CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_V1,
        "schema_version": CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_VERSION,
        "runtime_version": (
            CANONICAL_CONDENSATION_G31_INPUT_BINDING_RUNTIME_VERSION
        ),
        "binding_model": CANONICAL_CONDENSATION_MODEL_D,
        "binding_status": ELIGIBLE_FOR_G31_PREFLIGHT,
        "binding_meaning": (
            "This exact approved condensation is eligible to be presented "
            "to the unchanged G31 preflight."
        ),
        "maximum_g31_final_measured_request_code_point_count": (
            G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT
        ),
        "character_counting_contract": "PYTHON_UNICODE_CODE_POINTS",
        "encoding_contract": "UTF-8_STRICT",
        "original_source_request": original,
        "original_source_request_commitment": source_commitment,
        "approved_projection": complete,
        "approved_projection_commitment": projection_commitment,
        "approved_projection_prefix": prefix,
        "approved_projection_prefix_commitment": prefix_commitment,
        "approved_synthesis_body": body,
        "approved_synthesis_body_commitment": body_commitment,
        "g31_function_argument": body,
        "g31_function_argument_commitment": deepcopy(body_commitment),
        "g31_final_measured_request": complete,
        "g31_final_measured_request_commitment": deepcopy(
            projection_commitment
        ),
        "authorized_task": body,
        "authorized_task_commitment": deepcopy(body_commitment),
        "authorized_task_semantic_role": (
            "FUTURE_G31_AUTHORIZED_TASK_VALUE_ONLY"
        ),
        "preflight_input_tuple": preflight_tuple,
        "preflight_input_tuple_hash": preflight_tuple_hash,
        "source_request_hash": source.get("original_request_sha256"),
        "source_bundle_hash": proposal["source_lineage"]["source_bundle_hash"],
        "proposal_hash": proposal.get("condensation_hash"),
        "validation_hash": validation.get("validation_hash"),
        "review_hash": review.get("review_hash"),
        "decision_hash": decision.get("human_decision_hash"),
        "approval_hash": approved.get("approved_projection_artifact_hash"),
        "prefix_hash": prefix_commitment["sha256"],
        "body_hash": body_commitment["sha256"],
        "complete_projection_hash": projection_commitment["sha256"],
        "phase1_replay_family_hash": reconstruction.get(
            "phase1_replay_family_hash"
        ),
        "approved_chain_replay_hash": reconstruction.get(
            "replay_extension_hash"
        ),
        "approved_chain_record_hashes": deepcopy(
            reconstruction.get("extension_record_hashes")
        ),
        "artifact_versions": artifact_versions,
        "post_approval_transformation_allowed": False,
        **deepcopy(BINDING_AUTHORITY_BOUNDARIES),
    }
    _verify_cross_commitments(
        artifact=artifact,
        source=source,
        proposal=proposal,
        validation=validation,
        review=review,
        decision=decision,
        approved=approved,
        reconstruction=reconstruction,
    )
    identity_seed = deepcopy(artifact)
    binding_hash = replay_hash(identity_seed)
    artifact["binding_id"] = (
        "CANONICAL-CONDENSATION-G31-BINDING-"
        f"{binding_hash.removeprefix('sha256:')[:24]}"
    )
    artifact["binding_hash"] = binding_hash
    return artifact


def _verify_supported_versions(versions: dict[str, Any]) -> None:
    expected = {
        "proposal_artifact_type": CANONICAL_CONDENSATION_ARTIFACT_V1,
        "proposal_schema_id": CANONICAL_CONDENSATION_SCHEMA_V1,
        "proposal_schema_version": CANONICAL_CONDENSATION_SCHEMA_VERSION,
        "proposal_artifact_version": CANONICAL_CONDENSATION_ARTIFACT_VERSION,
        "validation_artifact_type": CANONICAL_CONDENSATION_VALIDATION_RESULT_V1,
        "validation_schema_version": "1.0.0",
        "validator_version": CANONICAL_CONDENSATION_VALIDATOR_VERSION,
        "review_artifact_type": (
            CANONICAL_CONDENSATION_HUMAN_REVIEW_PRESENTATION_V1
        ),
        "review_schema_version": (
            CANONICAL_CONDENSATION_HUMAN_REVIEW_SCHEMA_VERSION
        ),
        "decision_artifact_type": CANONICAL_CONDENSATION_HUMAN_DECISION_V1,
        "decision_schema_version": (
            CANONICAL_CONDENSATION_HUMAN_DECISION_SCHEMA_VERSION
        ),
        "approved_projection_artifact_type": (
            "CANONICAL_CONDENSATION_APPROVED_PROJECTION_V1"
        ),
        "replay_extension": CANONICAL_CONDENSATION_REPLAY_EXTENSION_V1,
        "replay_extension_schema_version": (
            CANONICAL_CONDENSATION_REPLAY_EXTENSION_SCHEMA_VERSION
        ),
    }
    if versions != expected:
        raise FailClosedRuntimeError(
            "canonical condensation G31 binding artifact version unsupported"
        )


def _verify_cross_commitments(
    *,
    artifact: dict[str, Any],
    source: dict[str, Any],
    proposal: dict[str, Any],
    validation: dict[str, Any],
    review: dict[str, Any],
    decision: dict[str, Any],
    approved: dict[str, Any],
    reconstruction: dict[str, Any],
) -> None:
    checks = (
        artifact["source_request_hash"] == content_sha256(
            artifact["original_source_request"]
        ),
        artifact["source_request_hash"] == source["original_request_sha256"],
        artifact["source_bundle_hash"]
        == proposal["source_lineage"]["source_bundle_hash"],
        artifact["proposal_hash"] == proposal["condensation_hash"],
        artifact["proposal_hash"] == review["proposal_commitment"],
        artifact["proposal_hash"] == decision["proposal_commitment"],
        artifact["validation_hash"] == validation["validation_hash"],
        artifact["validation_hash"] == review["validation_commitment"],
        artifact["validation_hash"] == decision["validation_commitment"],
        artifact["review_hash"] == review["review_hash"],
        artifact["review_hash"] == decision["review_commitment"],
        artifact["decision_hash"] == decision["human_decision_hash"],
        artifact["approval_hash"]
        == approved["approved_projection_artifact_hash"],
        artifact["prefix_hash"] == decision["exact_prefix_sha256"],
        artifact["body_hash"] == decision["exact_synthesis_body_sha256"],
        artifact["complete_projection_hash"]
        == decision["exact_complete_projection_sha256"],
        artifact["phase1_replay_family_hash"]
        == reconstruction["phase1_replay_family_hash"],
        artifact["phase1_replay_family_hash"]
        == decision["phase1_replay_family_hash"],
        artifact["approved_chain_replay_hash"]
        == reconstruction["replay_extension_hash"],
        artifact["approved_chain_record_hashes"]
        == reconstruction["extension_record_hashes"],
        artifact["approved_projection_prefix"] + artifact[
            "approved_synthesis_body"
        ]
        == artifact["approved_projection"],
        artifact["g31_function_argument"]
        == artifact["approved_synthesis_body"],
        artifact["g31_final_measured_request"]
        == artifact["approved_projection"],
        artifact["authorized_task"] == artifact["approved_synthesis_body"],
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "canonical condensation G31 binding commitment mismatch"
        )


def _verify_approved_value(
    approved: dict[str, Any],
    *,
    role: str,
    value: str,
    commitment: dict[str, Any],
) -> None:
    if role == "prefix":
        prefix = "prefix"
    else:
        prefix = role
    if any(
        (
            approved.get(prefix) != value,
            approved.get(f"{prefix}_sha256") != commitment["sha256"],
            approved.get(f"{prefix}_code_point_count")
            != commitment["code_point_count"],
            approved.get(f"{prefix}_utf8_byte_count")
            != commitment["utf8_byte_count"],
        )
    ):
        raise FailClosedRuntimeError(
            f"canonical condensation G31 binding {role} commitment mismatch"
        )


def _value_commitment(value: str) -> dict[str, Any]:
    return {
        "sha256": content_sha256(value),
        "code_point_count": len(value),
        "utf8_byte_count": len(value.encode("utf-8", errors="strict")),
        "character_counting_contract": "PYTHON_UNICODE_CODE_POINTS",
        "encoding_contract": "UTF-8_STRICT",
    }


def _exact_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise FailClosedRuntimeError(f"{field} is required")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise FailClosedRuntimeError(f"{field} must be strict UTF-8") from exc
    return value
