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

REPLAY_AUTHORITY_BOUNDARIES = {
    **NO_AUTHORITY_EFFECT,
    "replay_visible": True,
    "replay_authoritative_for_phase1_evidence": True,
    "replay_authoritative_for_approval": False,
    "replay_authoritative_for_execution": False,
}


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

    wrappers: list[dict[str, Any]] = []
    previous_replay_hash: str | None = None
    recorded_at: str | None = None
    for index, (step, filename) in enumerate(
        zip(CANONICAL_CONDENSATION_REPLAY_STEPS, expected_files, strict=True)
    ):
        wrapper = load_json(path / filename)
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
                "canonical condensation replay sequence mismatch"
            )
        for field, expected in REPLAY_AUTHORITY_BOUNDARIES.items():
            if wrapper.get(field) != expected:
                raise FailClosedRuntimeError(
                    f"canonical condensation replay boundary mismatch: {field}"
                )
        if recorded_at is None:
            recorded_at = wrapper["recorded_at"]
        elif wrapper["recorded_at"] != recorded_at:
            raise FailClosedRuntimeError(
                "canonical condensation replay timestamp continuity mismatch"
            )
        wrappers.append(wrapper)
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
