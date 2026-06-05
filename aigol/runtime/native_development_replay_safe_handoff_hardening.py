"""Replay-safe native development handoff package hardening for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_VERSION = (
    "AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_V1"
)
HANDOFF_PACKAGE_ARTIFACT_V1 = "HANDOFF_PACKAGE"
HANDOFF_CREATED = "HANDOFF_CREATED"
HANDOFF_VALIDATED = "HANDOFF_VALIDATED"
HANDOFF_ACCEPTED = "HANDOFF_ACCEPTED"

STAGES = (
    "PROPOSAL",
    "VALIDATION",
    "APPROVAL",
    "AUTHORIZATION",
    "MATERIALIZATION",
    "CERTIFICATION",
)

ALLOWED_PARENT_STAGE = {
    "PROPOSAL": None,
    "VALIDATION": "PROPOSAL",
    "APPROVAL": "VALIDATION",
    "AUTHORIZATION": "APPROVAL",
    "MATERIALIZATION": "AUTHORIZATION",
    "CERTIFICATION": "MATERIALIZATION",
}

REPLAY_STEPS = (
    "handoff_created",
    "handoff_validated",
    "handoff_accepted",
)

EVENT_TYPES = (
    HANDOFF_CREATED,
    HANDOFF_VALIDATED,
    HANDOFF_ACCEPTED,
)


def create_handoff_package(
    *,
    stage_id: str,
    artifact_hashes: list[dict[str, Any]],
    manifest_hash: str,
    parent_replay_id: str | None,
    actor_id: str,
    timestamp: str,
    replay_dir: str | Path,
    parent_package: dict[str, Any] | None = None,
    authorized_actor_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Create, validate, accept, and persist a replay-safe stage handoff package."""

    package = build_handoff_package(
        stage_id=stage_id,
        artifact_hashes=artifact_hashes,
        manifest_hash=manifest_hash,
        parent_replay_id=parent_replay_id,
        actor_id=actor_id,
        timestamp=timestamp,
        parent_package=parent_package,
    )
    validation = validate_handoff_package(
        package,
        parent_package=parent_package,
        authorized_actor_ids=authorized_actor_ids,
    )
    accepted = _accepted_artifact(package, validation)
    replay_path = Path(replay_dir)
    _persist_step(replay_path, 0, package)
    _persist_step(replay_path, 1, validation)
    _persist_step(replay_path, 2, accepted)
    return {
        "handoff_package": deepcopy(package),
        "handoff_validation": deepcopy(validation),
        "handoff_acceptance": deepcopy(accepted),
        "stage_id": package["stage_id"],
        "handoff_status": accepted["acceptance_status"],
        "replay_id": package["replay_id"],
        "chain_hash": package["chain_hash"],
        "parent_replay_id": package["parent_replay_id"],
        "artifact_hashes": deepcopy(package["artifact_hashes"]),
        "manifest_hash": package["manifest_hash"],
        "actor_id": package["actor_id"],
        "timestamp": package["timestamp"],
        "replay_reference": str(replay_path),
        "lineage_continuity": validation["lineage_continuity"],
        "hash_continuity": validation["hash_continuity"],
        "replay_continuity": validation["replay_continuity"],
        "authorized_transition": validation["authorized_transition"],
        "orphan_artifacts_detected": validation["orphan_artifacts_detected"],
        "lineage_break_detected": validation["lineage_break_detected"],
        "replay_chain_break_detected": validation["replay_chain_break_detected"],
        "unauthorized_stage_transition_detected": validation["unauthorized_stage_transition_detected"],
        "replay_events": list(EVENT_TYPES),
        "replay_visible": True,
    }


def build_handoff_package(
    *,
    stage_id: str,
    artifact_hashes: list[dict[str, Any]],
    manifest_hash: str,
    parent_replay_id: str | None,
    actor_id: str,
    timestamp: str,
    parent_package: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a handoff package and bind it to deterministic chain identity."""

    stage = _require_stage(stage_id)
    artifacts = _normalize_artifact_hashes(artifact_hashes)
    parent_chain_hash = _parent_chain_hash(parent_package)
    package = {
        "artifact_type": HANDOFF_PACKAGE_ARTIFACT_V1,
        "runtime_version": AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_VERSION,
        "stage_id": stage,
        "artifact_hashes": artifacts,
        "manifest_hash": _require_hash(manifest_hash, "manifest_hash"),
        "parent_replay_id": parent_replay_id,
        "parent_stage_id": parent_package.get("stage_id") if isinstance(parent_package, dict) else None,
        "parent_chain_hash": parent_chain_hash,
        "actor_id": _require_string(actor_id, "actor_id"),
        "timestamp": _require_string(timestamp, "timestamp"),
        "replay_visible": True,
    }
    package["chain_hash"] = _compute_chain_hash(package)
    package["replay_id"] = "HANDOFF-REPLAY-" + package["chain_hash"].removeprefix("sha256:")[:24].upper()
    package["package_hash"] = _compute_package_hash(package)
    return package


def validate_handoff_package(
    package: dict[str, Any],
    *,
    parent_package: dict[str, Any] | None = None,
    authorized_actor_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Validate lineage, hash, replay, and authorization continuity for a package."""

    violations = _handoff_violations(
        package,
        parent_package=parent_package,
        authorized_actor_ids=authorized_actor_ids,
    )
    validation = {
        "event_type": HANDOFF_VALIDATED,
        "artifact_type": "HANDOFF_PACKAGE_VALIDATION",
        "runtime_version": AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_VERSION,
        "stage_id": package.get("stage_id"),
        "replay_id": package.get("replay_id"),
        "package_hash": package.get("package_hash"),
        "chain_hash": package.get("chain_hash"),
        "lineage_continuity": not _has_violation(violations, "LINEAGE_BREAK"),
        "hash_continuity": not _has_violation(violations, "HASH_BREAK"),
        "replay_continuity": not _has_violation(violations, "REPLAY_CHAIN_BREAK"),
        "authorized_transition": not _has_violation(violations, "UNAUTHORIZED_STAGE_TRANSITION"),
        "orphan_artifacts_detected": _has_violation(violations, "ORPHAN_ARTIFACT"),
        "lineage_break_detected": _has_violation(violations, "LINEAGE_BREAK"),
        "replay_chain_break_detected": _has_violation(violations, "REPLAY_CHAIN_BREAK"),
        "unauthorized_stage_transition_detected": _has_violation(violations, "UNAUTHORIZED_STAGE_TRANSITION"),
        "violations": violations,
        "validation_status": "HANDOFF_VALIDATION_PASSED" if not violations else "FAILED_CLOSED",
        "replay_visible": True,
    }
    validation["artifact_hash"] = replay_hash(validation)
    if violations:
        raise FailClosedRuntimeError(_violation_message(violations))
    return validation


def reconstruct_handoff_package_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct a persisted handoff package replay and verify all three events."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("handoff replay ordering mismatch")
        if wrapper.get("event_type") != EVENT_TYPES[index]:
            raise FailClosedRuntimeError("handoff replay event type mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("handoff replay artifact must be a JSON object")
        wrappers.append(wrapper)

    package = wrappers[0]["artifact"]
    _verify_package_hash(package)
    validation = wrappers[1]["artifact"]
    acceptance = wrappers[2]["artifact"]
    _verify_artifact_hash(validation)
    _verify_artifact_hash(acceptance)
    if validation.get("replay_id") != package["replay_id"]:
        raise FailClosedRuntimeError("handoff validation replay reference mismatch")
    if acceptance.get("replay_id") != package["replay_id"]:
        raise FailClosedRuntimeError("handoff acceptance replay reference mismatch")
    if acceptance.get("package_hash") != package["package_hash"]:
        raise FailClosedRuntimeError("handoff acceptance package hash mismatch")
    return {
        "stage_id": package["stage_id"],
        "replay_id": package["replay_id"],
        "parent_replay_id": package["parent_replay_id"],
        "chain_hash": package["chain_hash"],
        "package_hash": package["package_hash"],
        "manifest_hash": package["manifest_hash"],
        "artifact_hashes": deepcopy(package["artifact_hashes"]),
        "actor_id": package["actor_id"],
        "timestamp": package["timestamp"],
        "handoff_status": acceptance["acceptance_status"],
        "lineage_continuity": validation["lineage_continuity"],
        "hash_continuity": validation["hash_continuity"],
        "replay_continuity": validation["replay_continuity"],
        "authorized_transition": validation["authorized_transition"],
        "replay_events": [wrapper["event_type"] for wrapper in wrappers],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "replay_visible": True,
    }


def reconstruct_handoff_chain(replay_dirs: list[str | Path]) -> dict[str, Any]:
    """Reconstruct a sequence of handoff package replays and validate chain continuity."""

    packages: list[dict[str, Any]] = []
    for path in replay_dirs:
        reconstruct_handoff_package_replay(path)
        packages.append(load_json(Path(path) / "000_handoff_created.json")["artifact"])
    parent: dict[str, Any] | None = None
    for package in packages:
        validate_handoff_package(package, parent_package=parent)
        parent = package
    return {
        "chain_status": "HANDOFF_CHAIN_VERIFIED",
        "stage_ids": [package["stage_id"] for package in packages],
        "final_replay_id": packages[-1]["replay_id"] if packages else None,
        "final_chain_hash": packages[-1]["chain_hash"] if packages else None,
        "handoff_count": len(packages),
        "replay_visible": True,
    }


def _handoff_violations(
    package: dict[str, Any],
    *,
    parent_package: dict[str, Any] | None,
    authorized_actor_ids: list[str] | None,
) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    if not isinstance(package, dict):
        return [{"code": "HASH_BREAK", "message": "handoff package must be a JSON object"}]
    stage = package.get("stage_id")
    expected_parent_stage = ALLOWED_PARENT_STAGE.get(stage)
    parent_stage = parent_package.get("stage_id") if isinstance(parent_package, dict) else None
    if package.get("artifact_type") != HANDOFF_PACKAGE_ARTIFACT_V1:
        violations.append({"code": "HASH_BREAK", "message": "handoff package type mismatch"})
    if stage not in STAGES:
        violations.append({"code": "UNAUTHORIZED_STAGE_TRANSITION", "message": "unknown stage id"})
    if expected_parent_stage != parent_stage:
        violations.append({"code": "UNAUTHORIZED_STAGE_TRANSITION", "message": "stage transition is not allowed"})
    if expected_parent_stage is not None and not isinstance(parent_package, dict):
        violations.append({"code": "LINEAGE_BREAK", "message": "parent handoff package is required"})
    if expected_parent_stage is None and package.get("parent_replay_id") is not None:
        violations.append({"code": "LINEAGE_BREAK", "message": "initial stage cannot have parent replay id"})
    if isinstance(parent_package, dict):
        if package.get("parent_replay_id") != parent_package.get("replay_id"):
            violations.append({"code": "REPLAY_CHAIN_BREAK", "message": "parent replay id mismatch"})
        if package.get("parent_chain_hash") != parent_package.get("chain_hash"):
            violations.append({"code": "LINEAGE_BREAK", "message": "parent chain hash mismatch"})
    try:
        _normalize_artifact_hashes(package.get("artifact_hashes"))
    except FailClosedRuntimeError as exc:
        violations.append({"code": "HASH_BREAK", "message": str(exc)})
    if _has_orphan_artifact(package, parent_package):
        violations.append({"code": "ORPHAN_ARTIFACT", "message": "artifact parent replay id is missing or mismatched"})
    try:
        _require_hash(package.get("manifest_hash"), "manifest_hash")
    except FailClosedRuntimeError as exc:
        violations.append({"code": "HASH_BREAK", "message": str(exc)})
    try:
        _verify_package_hash(package)
    except FailClosedRuntimeError as exc:
        violations.append({"code": "HASH_BREAK", "message": str(exc)})
    expected_actors = authorized_actor_ids or ["AIGOL_GOVERNANCE", "HUMAN_OPERATOR", "CODEX_ASSISTED_OPERATOR"]
    if package.get("actor_id") not in expected_actors:
        violations.append({"code": "UNAUTHORIZED_STAGE_TRANSITION", "message": "actor is not authorized for handoff"})
    return violations


def _accepted_artifact(package: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    accepted = {
        "event_type": HANDOFF_ACCEPTED,
        "artifact_type": "HANDOFF_PACKAGE_ACCEPTANCE",
        "runtime_version": AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_VERSION,
        "stage_id": package["stage_id"],
        "replay_id": package["replay_id"],
        "package_hash": package["package_hash"],
        "chain_hash": package["chain_hash"],
        "validation_hash": validation["artifact_hash"],
        "acceptance_status": "HANDOFF_ACCEPTED",
        "lineage_continuity": validation["lineage_continuity"],
        "hash_continuity": validation["hash_continuity"],
        "replay_continuity": validation["replay_continuity"],
        "authorized_transition": validation["authorized_transition"],
        "replay_visible": True,
    }
    accepted["artifact_hash"] = replay_hash(accepted)
    return accepted


def _persist_step(replay_dir: Path, index: int, artifact: dict[str, Any]) -> None:
    step = REPLAY_STEPS[index]
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": EVENT_TYPES[index],
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _compute_chain_hash(package: dict[str, Any]) -> str:
    return replay_hash(
        {
            "stage_id": package.get("stage_id"),
            "artifact_hashes": package.get("artifact_hashes"),
            "manifest_hash": package.get("manifest_hash"),
            "parent_replay_id": package.get("parent_replay_id"),
            "parent_stage_id": package.get("parent_stage_id"),
            "parent_chain_hash": package.get("parent_chain_hash"),
            "actor_id": package.get("actor_id"),
            "timestamp": package.get("timestamp"),
        }
    )


def _compute_package_hash(package: dict[str, Any]) -> str:
    safe = deepcopy(package)
    safe.pop("package_hash", None)
    return replay_hash(safe)


def _verify_package_hash(package: dict[str, Any]) -> None:
    if package.get("chain_hash") != _compute_chain_hash(package):
        raise FailClosedRuntimeError("handoff chain hash mismatch")
    expected_replay_id = "HANDOFF-REPLAY-" + package["chain_hash"].removeprefix("sha256:")[:24].upper()
    if package.get("replay_id") != expected_replay_id:
        raise FailClosedRuntimeError("handoff replay id mismatch")
    if package.get("package_hash") != _compute_package_hash(package):
        raise FailClosedRuntimeError("handoff package hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("handoff artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("handoff replay hash mismatch")


def _normalize_artifact_hashes(value: Any) -> list[dict[str, str | None]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("artifact hashes are required")
    normalized: list[dict[str, str | None]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("artifact hash entry must be a JSON object")
        artifact_id = _require_string(item.get("artifact_id"), "artifact_id")
        artifact_hash = _require_hash(item.get("artifact_hash"), "artifact_hash")
        if artifact_id in seen:
            raise FailClosedRuntimeError("duplicate artifact id")
        seen.add(artifact_id)
        normalized.append(
            {
                "artifact_id": artifact_id,
                "artifact_hash": artifact_hash,
                "parent_replay_id": item.get("parent_replay_id") if item.get("parent_replay_id") is not None else None,
            }
        )
    return normalized


def _has_orphan_artifact(package: dict[str, Any], parent_package: dict[str, Any] | None) -> bool:
    stage = package.get("stage_id")
    if stage == "PROPOSAL":
        return False
    expected_parent = parent_package.get("replay_id") if isinstance(parent_package, dict) else package.get("parent_replay_id")
    for artifact in package.get("artifact_hashes", []):
        if not isinstance(artifact, dict) or artifact.get("parent_replay_id") != expected_parent:
            return True
    return False


def _parent_chain_hash(parent_package: dict[str, Any] | None) -> str | None:
    if parent_package is None:
        return None
    chain_hash = parent_package.get("chain_hash")
    return _require_hash(chain_hash, "parent_chain_hash")


def _require_stage(value: Any) -> str:
    stage = _require_string(value, "stage_id")
    if stage not in STAGES:
        raise FailClosedRuntimeError("unknown handoff stage")
    return stage


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(f"{field_name} must be a sha256 hash")
    return text


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _has_violation(violations: list[dict[str, str]], code: str) -> bool:
    return any(violation.get("code") == code for violation in violations)


def _violation_message(violations: list[dict[str, str]]) -> str:
    if not violations:
        return "handoff validation failed closed"
    return "handoff validation failed closed: " + "; ".join(
        f"{violation['code']}: {violation['message']}" for violation in violations
    )


__all__ = [
    "AIGOL_NATIVE_DEVELOPMENT_REPLAY_SAFE_HANDOFF_HARDENING_VERSION",
    "HANDOFF_ACCEPTED",
    "HANDOFF_CREATED",
    "HANDOFF_PACKAGE_ARTIFACT_V1",
    "HANDOFF_VALIDATED",
    "STAGES",
    "build_handoff_package",
    "create_handoff_package",
    "reconstruct_handoff_chain",
    "reconstruct_handoff_package_replay",
    "validate_handoff_package",
]
