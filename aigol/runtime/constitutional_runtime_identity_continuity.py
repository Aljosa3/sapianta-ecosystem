"""Deterministic runtime identity continuity for bounded intelligence participation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.minimal_executable_real_llm_session import reconstruct_minimal_real_llm_session_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


OPEN = "OPEN"
TERMINATED = "TERMINATED"
AUTHORITY_SCOPE = "BOUNDED_NON_AUTHORITATIVE_RUNTIME"
IDENTITY_VIOLATION = "IDENTITY_VIOLATION"


def create_runtime_identity(
    *,
    session_id: str,
    replay_scope: str,
    authority_scope: str = AUTHORITY_SCOPE,
    created_at: str,
) -> dict[str, Any]:
    """Create explicit immutable runtime identity evidence."""

    artifact = {
        "session_id": _require_string(session_id, "session_id"),
        "replay_scope": _require_string(replay_scope, "replay_scope"),
        "authority_scope": _require_string(authority_scope, "authority_scope"),
        "created_at": _require_string(created_at, "created_at"),
        "state": OPEN,
        "lineage_parent": None,
        "governance_authority": False,
        "execution_authority": False,
        "hidden_continuity": False,
    }
    if artifact["authority_scope"] != AUTHORITY_SCOPE:
        raise FailClosedRuntimeError("runtime authority identity scope is not allowed")
    artifact["identity_hash"] = replay_hash(artifact)
    return artifact


def terminate_runtime_identity(identity: dict[str, Any], *, terminated_at: str) -> dict[str, Any]:
    """Create explicit terminated identity artifact without mutating the source identity."""

    _verify_identity_hash(identity)
    if identity["state"] != OPEN:
        raise FailClosedRuntimeError("runtime identity is not open")
    artifact = {
        "session_id": identity["session_id"],
        "replay_scope": identity["replay_scope"],
        "authority_scope": identity["authority_scope"],
        "created_at": identity["created_at"],
        "state": TERMINATED,
        "lineage_parent": identity["identity_hash"],
        "terminated_at": _require_string(terminated_at, "terminated_at"),
        "governance_authority": False,
        "execution_authority": False,
        "hidden_continuity": False,
    }
    artifact["identity_hash"] = replay_hash(artifact)
    return artifact


def validate_identity_immutability(identity: dict[str, Any]) -> dict[str, Any]:
    """Validate an identity artifact has not changed after creation."""

    _verify_identity_hash(identity)
    artifact = {
        "session_id": identity["session_id"],
        "identity_hash": identity["identity_hash"],
        "identity_immutable": True,
        "lineage_stable": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_session_not_resurrected(terminated_identity: dict[str, Any], candidate_identity: dict[str, Any]) -> dict[str, Any]:
    """Fail closed when a terminated session identity is reused or continued."""

    _verify_identity_hash(terminated_identity)
    _verify_identity_hash(candidate_identity)
    if terminated_identity["state"] != TERMINATED:
        raise FailClosedRuntimeError("terminated identity is required")
    if terminated_identity["session_id"] == candidate_identity["session_id"]:
        raise FailClosedRuntimeError("terminated runtime identity cannot continue")
    artifact = {
        "terminated_session_id": terminated_identity["session_id"],
        "candidate_session_id": candidate_identity["session_id"],
        "session_resurrected": False,
        "hidden_continuation_detected": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_runtime_identity_transition(previous_identity: dict[str, Any], next_identity: dict[str, Any]) -> dict[str, Any]:
    """Validate explicit identity transition without hidden carryover."""

    _verify_identity_hash(previous_identity)
    _verify_identity_hash(next_identity)
    if previous_identity["session_id"] == next_identity["session_id"]:
        raise FailClosedRuntimeError("runtime identity transition reuses session_id")
    if next_identity.get("lineage_parent") is not None:
        raise FailClosedRuntimeError("hidden identity carryover detected")
    if next_identity.get("authority_scope") != AUTHORITY_SCOPE:
        raise FailClosedRuntimeError("runtime authority identity drift detected")
    artifact = {
        "previous_session_id": previous_identity["session_id"],
        "next_session_id": next_identity["session_id"],
        "identity_transition_explicit": True,
        "hidden_carryover_detected": False,
        "authority_drift_detected": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_replay_identity_integrity(replay_dirs: list[str | Path]) -> dict[str, Any]:
    """Validate replay identity continuity and isolation across replay chains."""

    if not isinstance(replay_dirs, list) or not replay_dirs:
        raise FailClosedRuntimeError("replay identity integrity requires replay directories")
    session_ids: set[str] = set()
    replay_hashes: set[str] = set()
    replays = []
    for raw_dir in replay_dirs:
        replay_dir = Path(raw_dir)
        lineage = reconstruct_minimal_real_llm_session_replay(replay_dir)
        session_id = lineage["session_id"]
        replay_identity = lineage["replay_hash"]
        if session_id in session_ids:
            raise FailClosedRuntimeError("replay identity contamination detected")
        if replay_identity in replay_hashes:
            raise FailClosedRuntimeError("replay identity collision detected")
        session_ids.add(session_id)
        replay_hashes.add(replay_identity)
        replays.append(
            {
                "session_id": session_id,
                "replay_hash": replay_identity,
                "status": lineage["status"],
            }
        )
    artifact = {
        "replay_count": len(replays),
        "replays": replays,
        "replay_identity_integrity": True,
        "replay_identity_contamination_detected": False,
        "append_only_integrity_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_authority_identity_continuity(identity: dict[str, Any]) -> dict[str, Any]:
    """Validate authority identity remains non-transferable and non-escalated."""

    _verify_identity_hash(identity)
    if identity.get("authority_scope") != AUTHORITY_SCOPE:
        raise FailClosedRuntimeError("authority identity drift detected")
    if identity.get("governance_authority") is not False:
        raise FailClosedRuntimeError("governance authority identity escalation detected")
    if identity.get("execution_authority") is not False:
        raise FailClosedRuntimeError("execution authority identity escalation detected")
    artifact = {
        "session_id": identity["session_id"],
        "authority_scope": identity["authority_scope"],
        "authority_continuity_valid": True,
        "authority_drift_detected": False,
        "authority_escalation_detected": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_identity_violation_artifact(
    *,
    session_id: str,
    violation_type: str,
    reason: str,
) -> dict[str, Any]:
    """Create deterministic replay-visible identity violation evidence."""

    artifact = {
        "artifact_type": IDENTITY_VIOLATION,
        "session_id": _require_string(session_id, "session_id"),
        "violation_type": _require_string(violation_type, "violation_type"),
        "reason": _require_string(reason, "reason"),
        "identity_mutated": False,
        "authority_escalated": False,
        "hidden_continuity_created": False,
        "failed_closed": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def persist_identity_violation(*, violation_dir: str | Path, artifact: dict[str, Any]) -> None:
    """Persist identity violation evidence append-only."""

    _verify_artifact_hash(artifact)
    write_json_immutable(Path(violation_dir) / "000_identity_violation.json", artifact)


def _verify_identity_hash(identity: dict[str, Any]) -> None:
    if not isinstance(identity, dict):
        raise FailClosedRuntimeError("runtime identity must be a JSON object")
    canonical_serialize(identity)
    if "identity_hash" not in identity:
        raise FailClosedRuntimeError("runtime identity hash is required")
    expected = deepcopy(identity)
    actual = expected.pop("identity_hash")
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("runtime identity hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("identity artifact must be a JSON object")
    canonical_serialize(artifact)
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("identity artifact hash is required")
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash")
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("identity artifact hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
