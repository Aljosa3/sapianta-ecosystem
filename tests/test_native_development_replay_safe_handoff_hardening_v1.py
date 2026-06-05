"""Tests for AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_V1."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_replay_safe_handoff_hardening import (
    HANDOFF_ACCEPTED,
    HANDOFF_CREATED,
    HANDOFF_PACKAGE_ARTIFACT_V1,
    HANDOFF_VALIDATED,
    build_handoff_package,
    create_handoff_package,
    reconstruct_handoff_chain,
    reconstruct_handoff_package_replay,
    validate_handoff_package,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T12:00:00+00:00"


def _hash(label: str) -> str:
    return replay_hash({"fixture": label})


def _artifact(stage: str, parent_replay_id: str | None = None) -> list[dict[str, str | None]]:
    return [
        {
            "artifact_id": f"{stage.lower()}-artifact",
            "artifact_hash": _hash(stage),
            "parent_replay_id": parent_replay_id,
        }
    ]


def _create_stage(
    tmp_path: Path,
    stage: str,
    parent_capture: dict | None,
    actor_id: str = "AIGOL_GOVERNANCE",
) -> dict:
    parent_package = parent_capture["handoff_package"] if parent_capture else None
    parent_replay_id = parent_capture["replay_id"] if parent_capture else None
    return create_handoff_package(
        stage_id=stage,
        artifact_hashes=_artifact(stage, parent_replay_id),
        manifest_hash=_hash(f"{stage}-manifest"),
        parent_replay_id=parent_replay_id,
        actor_id=actor_id,
        timestamp=CREATED_AT,
        replay_dir=tmp_path / stage.lower(),
        parent_package=parent_package,
    )


def test_valid_handoff_chain_is_replay_safe_and_lineage_verifiable(tmp_path) -> None:
    proposal = _create_stage(tmp_path, "PROPOSAL", None)
    validation = _create_stage(tmp_path, "VALIDATION", proposal)
    approval = _create_stage(tmp_path, "APPROVAL", validation)
    authorization = _create_stage(tmp_path, "AUTHORIZATION", approval)
    materialization = _create_stage(tmp_path, "MATERIALIZATION", authorization)
    certification = _create_stage(tmp_path, "CERTIFICATION", materialization)

    reconstructed = reconstruct_handoff_package_replay(tmp_path / "certification")
    chain = reconstruct_handoff_chain(
        [
            tmp_path / "proposal",
            tmp_path / "validation",
            tmp_path / "approval",
            tmp_path / "authorization",
            tmp_path / "materialization",
            tmp_path / "certification",
        ]
    )

    assert proposal["handoff_package"]["artifact_type"] == HANDOFF_PACKAGE_ARTIFACT_V1
    assert certification["handoff_status"] == HANDOFF_ACCEPTED
    assert certification["lineage_continuity"] is True
    assert certification["hash_continuity"] is True
    assert certification["replay_continuity"] is True
    assert certification["authorized_transition"] is True
    assert reconstructed["replay_events"] == [HANDOFF_CREATED, HANDOFF_VALIDATED, HANDOFF_ACCEPTED]
    assert reconstructed["replay_artifact_count"] == 3
    assert chain["chain_status"] == "HANDOFF_CHAIN_VERIFIED"
    assert chain["stage_ids"] == [
        "PROPOSAL",
        "VALIDATION",
        "APPROVAL",
        "AUTHORIZATION",
        "MATERIALIZATION",
        "CERTIFICATION",
    ]


def test_lineage_break_is_detected(tmp_path) -> None:
    proposal = _create_stage(tmp_path, "PROPOSAL", None)
    broken_parent = dict(proposal["handoff_package"])
    broken_parent["chain_hash"] = _hash("wrong-parent-chain")
    package = build_handoff_package(
        stage_id="VALIDATION",
        artifact_hashes=_artifact("VALIDATION", proposal["replay_id"]),
        manifest_hash=_hash("validation-manifest"),
        parent_replay_id=proposal["replay_id"],
        actor_id="AIGOL_GOVERNANCE",
        timestamp=CREATED_AT,
        parent_package=proposal["handoff_package"],
    )

    with pytest.raises(FailClosedRuntimeError, match="LINEAGE_BREAK"):
        validate_handoff_package(package, parent_package=broken_parent)


def test_replay_break_is_detected(tmp_path) -> None:
    proposal = _create_stage(tmp_path, "PROPOSAL", None)
    package = build_handoff_package(
        stage_id="VALIDATION",
        artifact_hashes=_artifact("VALIDATION", proposal["replay_id"]),
        manifest_hash=_hash("validation-manifest"),
        parent_replay_id=proposal["replay_id"],
        actor_id="AIGOL_GOVERNANCE",
        timestamp=CREATED_AT,
        parent_package=proposal["handoff_package"],
    )
    package["parent_replay_id"] = "HANDOFF-REPLAY-BROKEN"
    package["chain_hash"] = replay_hash(
        {
            "stage_id": package["stage_id"],
            "artifact_hashes": package["artifact_hashes"],
            "manifest_hash": package["manifest_hash"],
            "parent_replay_id": package["parent_replay_id"],
            "parent_stage_id": package["parent_stage_id"],
            "parent_chain_hash": package["parent_chain_hash"],
            "actor_id": package["actor_id"],
            "timestamp": package["timestamp"],
        }
    )
    package["package_hash"] = replay_hash({key: value for key, value in package.items() if key != "package_hash"})

    with pytest.raises(FailClosedRuntimeError, match="REPLAY_CHAIN_BREAK"):
        validate_handoff_package(package, parent_package=proposal["handoff_package"])


def test_unauthorized_transition_is_detected(tmp_path) -> None:
    proposal = _create_stage(tmp_path, "PROPOSAL", None)

    with pytest.raises(FailClosedRuntimeError, match="UNAUTHORIZED_STAGE_TRANSITION"):
        create_handoff_package(
            stage_id="MATERIALIZATION",
            artifact_hashes=_artifact("MATERIALIZATION", proposal["replay_id"]),
            manifest_hash=_hash("materialization-manifest"),
            parent_replay_id=proposal["replay_id"],
            actor_id="AIGOL_GOVERNANCE",
            timestamp=CREATED_AT,
            replay_dir=tmp_path / "unauthorized_transition",
            parent_package=proposal["handoff_package"],
        )


def test_orphan_artifact_is_detected(tmp_path) -> None:
    proposal = _create_stage(tmp_path, "PROPOSAL", None)

    with pytest.raises(FailClosedRuntimeError, match="ORPHAN_ARTIFACT"):
        create_handoff_package(
            stage_id="VALIDATION",
            artifact_hashes=_artifact("VALIDATION", None),
            manifest_hash=_hash("validation-manifest"),
            parent_replay_id=proposal["replay_id"],
            actor_id="AIGOL_GOVERNANCE",
            timestamp=CREATED_AT,
            replay_dir=tmp_path / "orphan",
            parent_package=proposal["handoff_package"],
        )


def test_unauthorized_actor_is_detected(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="UNAUTHORIZED_STAGE_TRANSITION"):
        create_handoff_package(
            stage_id="PROPOSAL",
            artifact_hashes=_artifact("PROPOSAL", None),
            manifest_hash=_hash("proposal-manifest"),
            parent_replay_id=None,
            actor_id="UNKNOWN_ACTOR",
            timestamp=CREATED_AT,
            replay_dir=tmp_path / "unauthorized_actor",
            parent_package=None,
        )
