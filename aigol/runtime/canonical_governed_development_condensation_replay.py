"""Immutable replay for standalone canonical condensation Phase 1.

This replay family records source lineage, a non-authoritative proposal, and
its deterministic validation.  It creates no approval, G31 input binding,
authorization, Worker lifecycle event, Provider invocation, or execution
permission.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.canonical_governed_development_condensation_runtime import (
    NO_AUTHORITY_EFFECT,
    validate_canonical_condensation_artifact,
)
from aigol.runtime.canonical_governed_development_condensation_validation_runtime import (
    validate_canonical_condensation_validation_result,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
    with_replay_hash,
    write_json_immutable,
)


CANONICAL_CONDENSATION_REPLAY_FAMILY_V1 = (
    "CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_REPLAY_FAMILY_V1"
)
CANONICAL_CONDENSATION_REPLAY_SCHEMA_VERSION = "1.0.0"
CANONICAL_CONDENSATION_REPLAY_STEPS = (
    "condensation_source_lineage_recorded",
    "condensation_proposal_recorded",
    "condensation_validation_recorded",
)
CANONICAL_CONDENSATION_REPLAY_EXTENSION_V1 = (
    "CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_REVIEW_DECISION_EXTENSION_V1"
)
CANONICAL_CONDENSATION_REPLAY_EXTENSION_SCHEMA_VERSION = "1.0.0"
CANONICAL_CONDENSATION_REPLAY_EXTENSION_STEPS = (
    "condensation_human_review_presented",
    "condensation_human_decision_recorded",
)

REPLAY_AUTHORITY_BOUNDARIES = {
    **NO_AUTHORITY_EFFECT,
    "replay_visible": True,
    "replay_authoritative_for_phase1_evidence": True,
    "replay_authoritative_for_approval": False,
    "replay_authoritative_for_execution": False,
}
REPLAY_EXTENSION_AUTHORITY_BOUNDARIES = {
    "semantic_representation_decision_recorded": True,
    "replay_authoritative_for_semantic_representation_decision": True,
    "replay_authoritative_for_execution": False,
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
_REPLAY_EXTENSION_WRAPPER_FIELDS = frozenset(
    {
        "replay_extension",
        "schema_version",
        "extends_replay_family",
        "phase1_replay_family_hash",
        "index",
        "step",
        "recorded_at",
        "previous_replay_hash",
        "artifact",
        "replay_hash",
        *REPLAY_EXTENSION_AUTHORITY_BOUNDARIES.keys(),
    }
)


def record_canonical_condensation_phase1_replay(
    *,
    proposal: dict[str, Any],
    validation_result: dict[str, Any],
    recorded_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Persist the exact three-record Phase 1 family append-only."""

    canonical_proposal = validate_canonical_condensation_artifact(proposal)
    canonical_validation = validate_canonical_condensation_validation_result(
        validation_result,
        proposal=canonical_proposal,
    )
    timestamp = _required_text(recorded_at, "recorded_at")
    path = Path(replay_dir)
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError(
            "canonical condensation replay directory must be absent or empty"
        )

    source_lineage = deepcopy(canonical_proposal["source_lineage"])
    artifacts = (
        {
            "artifact_type": "CANONICAL_CONDENSATION_SOURCE_LINEAGE_REPLAY_V1",
            "source_lineage": source_lineage,
            "source_bundle_hash": source_lineage["source_bundle_hash"],
            "condensation_id": canonical_proposal["condensation_id"],
            "condensation_hash": canonical_proposal["condensation_hash"],
        },
        canonical_proposal,
        canonical_validation,
    )
    previous_replay_hash: str | None = None
    written: list[str] = []
    record_hashes: list[str] = []
    for index, (step, artifact) in enumerate(
        zip(CANONICAL_CONDENSATION_REPLAY_STEPS, artifacts, strict=True)
    ):
        wrapper = with_replay_hash(
            {
                "replay_family": CANONICAL_CONDENSATION_REPLAY_FAMILY_V1,
                "schema_version": CANONICAL_CONDENSATION_REPLAY_SCHEMA_VERSION,
                "index": index,
                "step": step,
                "recorded_at": timestamp,
                "previous_replay_hash": previous_replay_hash,
                "artifact": deepcopy(artifact),
                **deepcopy(REPLAY_AUTHORITY_BOUNDARIES),
            }
        )
        filename = f"{index:03d}_{step}.json"
        write_json_immutable(path / filename, wrapper)
        written.append(filename)
        previous_replay_hash = wrapper["replay_hash"]
        record_hashes.append(wrapper["replay_hash"])

    reconstructed = reconstruct_canonical_condensation_phase1_replay(path)
    return {
        "replay_family": CANONICAL_CONDENSATION_REPLAY_FAMILY_V1,
        "replay_dir": str(path),
        "replay_files": written,
        "replay_record_hashes": record_hashes,
        "replay_family_hash": reconstructed["replay_family_hash"],
        "condensation_id": canonical_proposal["condensation_id"],
        "condensation_hash": canonical_proposal["condensation_hash"],
        "validation_id": canonical_validation["validation_id"],
        "validation_hash": canonical_validation["validation_hash"],
        "validation_status": canonical_validation["validation_status"],
        **deepcopy(REPLAY_AUTHORITY_BOUNDARIES),
    }


def reconstruct_canonical_condensation_phase1_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Fail closed unless the exact replay family reconstructs deterministically."""

    path = Path(replay_dir)
    if not path.exists() or not path.is_dir():
        raise FailClosedRuntimeError(
            "canonical condensation replay directory is required"
        )
    expected_files = [
        f"{index:03d}_{step}.json"
        for index, step in enumerate(CANONICAL_CONDENSATION_REPLAY_STEPS)
    ]
    actual_files = sorted(item.name for item in path.iterdir())
    if actual_files != expected_files:
        raise FailClosedRuntimeError(
            "canonical condensation replay file set or order mismatch"
        )

    wrappers = [load_json(path / filename) for filename in expected_files]
    return _reconstruct_phase1_wrappers(wrappers)


def record_canonical_condensation_review_decision_replay(
    *,
    phase1_replay_dir: str | Path,
    review: dict[str, Any],
    decision: dict[str, Any],
    recorded_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Copy the immutable Phase 1 prefix and append review and decision."""

    from aigol.runtime.canonical_governed_development_condensation_human_decision_runtime import (
        validate_canonical_condensation_human_decision,
    )
    from aigol.runtime.canonical_governed_development_condensation_human_review_runtime import (
        validate_canonical_condensation_human_review,
    )

    source_path = Path(phase1_replay_dir)
    phase1 = reconstruct_canonical_condensation_phase1_replay(source_path)
    canonical_review = validate_canonical_condensation_human_review(
        review,
        phase1_replay_dir=source_path,
    )
    canonical_decision = validate_canonical_condensation_human_decision(
        decision,
        review=canonical_review,
        phase1_replay_dir=source_path,
    )
    timestamp = _required_text(recorded_at, "recorded_at")
    path = Path(replay_dir)
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError(
            "canonical condensation review-decision Replay must be absent or empty"
        )

    phase1_files = [
        f"{index:03d}_{step}.json"
        for index, step in enumerate(CANONICAL_CONDENSATION_REPLAY_STEPS)
    ]
    written: list[str] = []
    record_hashes: list[str] = []
    for filename in phase1_files:
        wrapper = load_json(source_path / filename)
        verify_replay_hash(wrapper)
        write_json_immutable(path / filename, wrapper)
        written.append(filename)
        record_hashes.append(wrapper["replay_hash"])

    previous_replay_hash = record_hashes[-1]
    for offset, (step, artifact) in enumerate(
        zip(
            CANONICAL_CONDENSATION_REPLAY_EXTENSION_STEPS,
            (canonical_review, canonical_decision),
            strict=True,
        ),
        start=len(CANONICAL_CONDENSATION_REPLAY_STEPS),
    ):
        wrapper = with_replay_hash(
            {
                "replay_extension": CANONICAL_CONDENSATION_REPLAY_EXTENSION_V1,
                "schema_version": (
                    CANONICAL_CONDENSATION_REPLAY_EXTENSION_SCHEMA_VERSION
                ),
                "extends_replay_family": CANONICAL_CONDENSATION_REPLAY_FAMILY_V1,
                "phase1_replay_family_hash": phase1["replay_family_hash"],
                "index": offset,
                "step": step,
                "recorded_at": timestamp,
                "previous_replay_hash": previous_replay_hash,
                "artifact": deepcopy(artifact),
                **deepcopy(REPLAY_EXTENSION_AUTHORITY_BOUNDARIES),
            }
        )
        filename = f"{offset:03d}_{step}.json"
        write_json_immutable(path / filename, wrapper)
        written.append(filename)
        previous_replay_hash = wrapper["replay_hash"]
        record_hashes.append(wrapper["replay_hash"])

    reconstructed = reconstruct_canonical_condensation_review_decision_replay(
        path
    )
    return {
        "replay_extension": CANONICAL_CONDENSATION_REPLAY_EXTENSION_V1,
        "replay_dir": str(path),
        "replay_files": written,
        "record_hashes": record_hashes,
        "phase1_replay_family_hash": phase1["replay_family_hash"],
        "review_id": canonical_review["review_id"],
        "review_hash": canonical_review["review_hash"],
        "human_decision_id": canonical_decision["human_decision_id"],
        "human_decision_hash": canonical_decision["human_decision_hash"],
        "decision": canonical_decision["decision"],
        "approved_projection": deepcopy(
            reconstructed["approved_projection"]
        ),
        "replay_extension_hash": reconstructed["replay_extension_hash"],
        **deepcopy(REPLAY_EXTENSION_AUTHORITY_BOUNDARIES),
    }


def reconstruct_canonical_condensation_review_decision_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct source through explicit review decision without execution."""

    from aigol.runtime.canonical_governed_development_condensation_human_decision_runtime import (
        validate_canonical_condensation_human_decision,
    )
    from aigol.runtime.canonical_governed_development_condensation_human_review_runtime import (
        validate_canonical_condensation_human_review,
    )

    path = Path(replay_dir)
    if not path.exists() or not path.is_dir():
        raise FailClosedRuntimeError(
            "canonical condensation review-decision Replay directory required"
        )
    phase1_files = [
        f"{index:03d}_{step}.json"
        for index, step in enumerate(CANONICAL_CONDENSATION_REPLAY_STEPS)
    ]
    extension_files = [
        f"{index:03d}_{step}.json"
        for index, step in enumerate(
            CANONICAL_CONDENSATION_REPLAY_EXTENSION_STEPS,
            start=len(CANONICAL_CONDENSATION_REPLAY_STEPS),
        )
    ]
    expected_files = phase1_files + extension_files
    if sorted(item.name for item in path.iterdir()) != expected_files:
        raise FailClosedRuntimeError(
            "canonical condensation review-decision Replay file set mismatch"
        )

    phase1_wrappers = [load_json(path / filename) for filename in phase1_files]
    phase1 = _reconstruct_phase1_wrappers(phase1_wrappers)
    extension_wrappers: list[dict[str, Any]] = []
    previous_replay_hash = phase1_wrappers[-1]["replay_hash"]
    recorded_at: str | None = None
    for index, (step, filename) in enumerate(
        zip(
            CANONICAL_CONDENSATION_REPLAY_EXTENSION_STEPS,
            extension_files,
            strict=True,
        ),
        start=len(CANONICAL_CONDENSATION_REPLAY_STEPS),
    ):
        wrapper = load_json(path / filename)
        verify_replay_hash(wrapper)
        if frozenset(wrapper) != _REPLAY_EXTENSION_WRAPPER_FIELDS:
            raise FailClosedRuntimeError(
                "canonical condensation review-decision Replay field set mismatch"
            )
        if any(
            (
                wrapper.get("replay_extension")
                != CANONICAL_CONDENSATION_REPLAY_EXTENSION_V1,
                wrapper.get("schema_version")
                != CANONICAL_CONDENSATION_REPLAY_EXTENSION_SCHEMA_VERSION,
                wrapper.get("extends_replay_family")
                != CANONICAL_CONDENSATION_REPLAY_FAMILY_V1,
                wrapper.get("phase1_replay_family_hash")
                != phase1["replay_family_hash"],
                wrapper.get("index") != index,
                wrapper.get("step") != step,
                wrapper.get("previous_replay_hash") != previous_replay_hash,
                not isinstance(wrapper.get("recorded_at"), str),
                not wrapper.get("recorded_at"),
                not isinstance(wrapper.get("artifact"), dict),
            )
        ):
            raise FailClosedRuntimeError(
                "canonical condensation review-decision Replay sequence mismatch"
            )
        for field, expected in REPLAY_EXTENSION_AUTHORITY_BOUNDARIES.items():
            if wrapper.get(field) != expected:
                raise FailClosedRuntimeError(
                    "canonical condensation review-decision Replay "
                    f"boundary mismatch: {field}"
                )
        if recorded_at is None:
            recorded_at = wrapper["recorded_at"]
        elif wrapper["recorded_at"] != recorded_at:
            raise FailClosedRuntimeError(
                "canonical condensation review-decision Replay time mismatch"
            )
        extension_wrappers.append(wrapper)
        previous_replay_hash = wrapper["replay_hash"]

    review = validate_canonical_condensation_human_review(
        extension_wrappers[0]["artifact"],
        phase1_reconstruction=phase1,
    )
    decision = validate_canonical_condensation_human_decision(
        extension_wrappers[1]["artifact"],
        review=review,
        phase1_reconstruction=phase1,
    )
    if any(
        (
            decision["review_id"] != review["review_id"],
            decision["review_commitment"] != review["review_hash"],
            decision["phase1_replay_family_hash"]
            != phase1["replay_family_hash"],
        )
    ):
        raise FailClosedRuntimeError(
            "canonical condensation review-decision Replay lineage mismatch"
        )
    extension_seed = {
        "replay_extension": CANONICAL_CONDENSATION_REPLAY_EXTENSION_V1,
        "phase1_replay_family_hash": phase1["replay_family_hash"],
        "extension_record_hashes": [
            wrapper["replay_hash"] for wrapper in extension_wrappers
        ],
        "review_hash": review["review_hash"],
        "human_decision_hash": decision["human_decision_hash"],
    }
    return {
        **extension_seed,
        "replay_extension_hash": replay_hash(extension_seed),
        "recorded_at": recorded_at,
        "source_lineage": deepcopy(phase1["source_lineage"]),
        "proposal": deepcopy(phase1["proposal"]),
        "validation_result": deepcopy(phase1["validation_result"]),
        "review": deepcopy(review),
        "decision_artifact": deepcopy(decision),
        "decision": decision["decision"],
        "approved_projection": deepcopy(decision["approved_projection"]),
        "approved_projection_created": decision[
            "approved_projection_created"
        ],
        **deepcopy(REPLAY_EXTENSION_AUTHORITY_BOUNDARIES),
    }


def _reconstruct_phase1_wrappers(
    wrappers: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(wrappers) != len(CANONICAL_CONDENSATION_REPLAY_STEPS):
        raise FailClosedRuntimeError(
            "canonical condensation Phase 1 Replay wrapper count mismatch"
        )
    previous_replay_hash: str | None = None
    recorded_at: str | None = None
    for index, (step, wrapper) in enumerate(
        zip(CANONICAL_CONDENSATION_REPLAY_STEPS, wrappers, strict=True)
    ):
        verify_replay_hash(wrapper)
        if any(
            (
                wrapper.get("replay_family")
                != CANONICAL_CONDENSATION_REPLAY_FAMILY_V1,
                wrapper.get("schema_version")
                != CANONICAL_CONDENSATION_REPLAY_SCHEMA_VERSION,
                wrapper.get("index") != index,
                wrapper.get("step") != step,
                wrapper.get("previous_replay_hash") != previous_replay_hash,
                not isinstance(wrapper.get("recorded_at"), str),
                not wrapper.get("recorded_at"),
                not isinstance(wrapper.get("artifact"), dict),
            )
        ):
            raise FailClosedRuntimeError(
                "canonical condensation Replay sequence mismatch"
            )
        for field, expected in REPLAY_AUTHORITY_BOUNDARIES.items():
            if wrapper.get(field) != expected:
                raise FailClosedRuntimeError(
                    f"canonical condensation Replay boundary mismatch: {field}"
                )
        if recorded_at is None:
            recorded_at = wrapper["recorded_at"]
        elif wrapper["recorded_at"] != recorded_at:
            raise FailClosedRuntimeError(
                "canonical condensation Replay timestamp continuity mismatch"
            )
        previous_replay_hash = wrapper["replay_hash"]

    source_record = wrappers[0]["artifact"]
    proposal = validate_canonical_condensation_artifact(wrappers[1]["artifact"])
    validation = validate_canonical_condensation_validation_result(
        wrappers[2]["artifact"],
        proposal=proposal,
    )
    if any(
        (
            source_record.get("artifact_type")
            != "CANONICAL_CONDENSATION_SOURCE_LINEAGE_REPLAY_V1",
            source_record.get("source_lineage") != proposal["source_lineage"],
            source_record.get("source_bundle_hash")
            != proposal["source_lineage"]["source_bundle_hash"],
            source_record.get("condensation_id") != proposal["condensation_id"],
            source_record.get("condensation_hash") != proposal["condensation_hash"],
            validation.get("condensation_id") != proposal["condensation_id"],
            validation.get("condensation_hash") != proposal["condensation_hash"],
        )
    ):
        raise FailClosedRuntimeError(
            "canonical condensation replay cross-record lineage mismatch"
        )

    family_seed = {
        "replay_family": CANONICAL_CONDENSATION_REPLAY_FAMILY_V1,
        "record_hashes": [wrapper["replay_hash"] for wrapper in wrappers],
        "condensation_hash": proposal["condensation_hash"],
        "validation_hash": validation["validation_hash"],
    }
    return {
        **family_seed,
        "replay_family_hash": replay_hash(family_seed),
        "recorded_at": recorded_at,
        "source_lineage": deepcopy(source_record["source_lineage"]),
        "proposal": deepcopy(proposal),
        "validation_result": deepcopy(validation),
        "validation_status": validation["validation_status"],
        **deepcopy(REPLAY_AUTHORITY_BOUNDARIES),
    }


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field} is required")
    return value.strip()
