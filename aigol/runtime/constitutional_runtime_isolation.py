"""Constitutional runtime isolation checks for bounded intelligence participation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.minimal_executable_real_llm_session import reconstruct_minimal_real_llm_session_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


ISOLATION_VIOLATION = "ISOLATION_VIOLATION"
CONSTITUTIONAL_SUBSTRATE = "CONSTITUTIONAL_SUBSTRATE"
OPERATIONAL_COGNITION_RUNTIME = "OPERATIONAL_COGNITION_RUNTIME"
READ_ONLY = "READ_ONLY"


def read_constitutional_substrate_references(paths: list[str | Path]) -> dict[str, Any]:
    """Read constitutional substrate files as deterministic readonly references."""

    if not isinstance(paths, list) or not paths:
        raise FailClosedRuntimeError("constitutional substrate paths must be explicit")
    references = []
    seen_paths: set[str] = set()
    for raw_path in paths:
        path = Path(raw_path)
        path_key = path.as_posix()
        if path_key in seen_paths:
            raise FailClosedRuntimeError("constitutional substrate reference is duplicated")
        if not path.exists() or not path.is_file():
            raise FailClosedRuntimeError("constitutional substrate reference is missing")
        content = path.read_text(encoding="utf-8")
        references.append(
            {
                "path": path_key,
                "mode": READ_ONLY,
                "content_hash": replay_hash({"path": path_key, "content": content}),
            }
        )
        seen_paths.add(path_key)
    substrate = {
        "substrate_type": CONSTITUTIONAL_SUBSTRATE,
        "runtime_access": READ_ONLY,
        "reference_count": len(references),
        "references": references,
        "runtime_may_write": False,
        "replay_authoritative": True,
    }
    substrate["artifact_hash"] = replay_hash(substrate)
    return substrate


def block_constitutional_mutation(
    *,
    session_id: str,
    attempted_target: str,
    attempted_action: str,
    violation_dir: str | Path,
) -> None:
    """Persist a replay-visible isolation violation and fail closed."""

    artifact = create_isolation_violation_artifact(
        session_id=session_id,
        violation_type="CONSTITUTIONAL_MUTATION_ATTEMPT",
        attempted_target=attempted_target,
        attempted_action=attempted_action,
        reason="bounded cognition runtime cannot mutate constitutional substrate",
    )
    persist_isolation_violation(violation_dir=violation_dir, artifact=artifact)
    raise FailClosedRuntimeError("constitutional mutation attempt blocked")


def create_isolation_violation_artifact(
    *,
    session_id: str,
    violation_type: str,
    attempted_target: str,
    attempted_action: str,
    reason: str,
) -> dict[str, Any]:
    """Create deterministic replay-visible isolation violation evidence."""

    artifact = {
        "artifact_type": ISOLATION_VIOLATION,
        "session_id": _require_string(session_id, "session_id"),
        "violation_type": _require_string(violation_type, "violation_type"),
        "attempted_target": _require_string(attempted_target, "attempted_target"),
        "attempted_action": _require_string(attempted_action, "attempted_action"),
        "reason": _require_string(reason, "reason"),
        "constitutional_substrate_mutated": False,
        "runtime_state_leaked": False,
        "authority_escalated": False,
        "failed_closed": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def persist_isolation_violation(*, violation_dir: str | Path, artifact: dict[str, Any]) -> None:
    """Persist isolation violation evidence append-only."""

    _verify_artifact_hash(artifact)
    write_json_immutable(Path(violation_dir) / "000_isolation_violation.json", artifact)


def validate_runtime_sandbox_containment(capture: dict[str, Any]) -> dict[str, Any]:
    """Validate a bounded session capture remains userspace-like and non-authoritative."""

    if not isinstance(capture, dict):
        raise FailClosedRuntimeError("runtime capture must be a JSON object")
    egress = capture.get("egress")
    validation = capture.get("validation")
    if not isinstance(egress, dict) or not isinstance(validation, dict):
        raise FailClosedRuntimeError("runtime capture is missing isolation evidence")
    if egress.get("governance_authority_delegated") is not False:
        raise FailClosedRuntimeError("runtime sandbox authority escalation detected")
    if egress.get("execution_authority_activated") is not False:
        raise FailClosedRuntimeError("runtime sandbox execution authority detected")
    if validation.get("hidden_state_transition_detected") is not False:
        raise FailClosedRuntimeError("runtime sandbox hidden state transition detected")
    containment = {
        "session_id": egress["session_id"],
        "runtime_layer": OPERATIONAL_COGNITION_RUNTIME,
        "constitution_layer": CONSTITUTIONAL_SUBSTRATE,
        "sandbox_contained": True,
        "governance_authority_delegated": False,
        "execution_authority_activated": False,
        "hidden_state_persisted": False,
    }
    containment["artifact_hash"] = replay_hash(containment)
    return containment


def validate_cross_session_isolation(captures: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate bounded sessions do not leak hidden state across sessions."""

    if not isinstance(captures, list) or not captures:
        raise FailClosedRuntimeError("cross-session isolation requires captures")
    session_ids: set[str] = set()
    session_hashes: set[str] = set()
    for capture in captures:
        if not isinstance(capture, dict):
            raise FailClosedRuntimeError("cross-session capture is invalid")
        ingress = capture.get("ingress")
        egress = capture.get("egress")
        if not isinstance(ingress, dict) or not isinstance(egress, dict):
            raise FailClosedRuntimeError("cross-session capture is missing boundary artifacts")
        session_id = egress.get("session_id")
        if session_id in session_ids:
            raise FailClosedRuntimeError("cross-session isolation contains duplicate session_id")
        if ingress.get("lineage_parent") is not None:
            raise FailClosedRuntimeError("cross-session hidden lineage carryover detected")
        session_hash = capture.get("session_hash")
        if session_hash in session_hashes:
            raise FailClosedRuntimeError("cross-session replay identity collision detected")
        if egress.get("governance_authority_delegated") is not False:
            raise FailClosedRuntimeError("cross-session governance authority escalation detected")
        session_ids.add(session_id)
        session_hashes.add(session_hash)
    isolation = {
        "session_count": len(captures),
        "unique_session_ids": len(session_ids),
        "cross_session_isolated": True,
        "hidden_continuity_detected": False,
        "replay_contamination_detected": False,
        "authority_escalation_detected": False,
    }
    isolation["artifact_hash"] = replay_hash(isolation)
    return isolation


def validate_replay_isolation(replay_dirs: list[str | Path]) -> dict[str, Any]:
    """Validate replay chains remain scoped to isolated session directories."""

    if not isinstance(replay_dirs, list) or not replay_dirs:
        raise FailClosedRuntimeError("replay isolation requires replay directories")
    seen_session_ids: set[str] = set()
    lineages = []
    for raw_dir in replay_dirs:
        replay_dir = Path(raw_dir)
        lineage = reconstruct_minimal_real_llm_session_replay(replay_dir)
        session_id = lineage["session_id"]
        if session_id in seen_session_ids:
            raise FailClosedRuntimeError("replay isolation contains duplicate session lineage")
        if lineage.get("governance_authority_delegated") is not False:
            raise FailClosedRuntimeError("replay isolation authority escalation detected")
        seen_session_ids.add(session_id)
        lineages.append(
            {
                "replay_dir": replay_dir.as_posix(),
                "session_id": session_id,
                "status": lineage["status"],
                "replay_hash": lineage["replay_hash"],
            }
        )
    isolation = {
        "replay_chain_count": len(lineages),
        "isolated_replay_chains": True,
        "lineages": lineages,
        "replay_contamination_detected": False,
        "append_only_replay_integrity": True,
    }
    isolation["artifact_hash"] = replay_hash(isolation)
    return isolation


def validate_no_constitutional_drift(
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    """Validate readonly constitutional substrate references did not drift."""

    _verify_artifact_hash(before)
    _verify_artifact_hash(after)
    if before != after:
        raise FailClosedRuntimeError("constitutional substrate drift detected")
    artifact = {
        "constitutional_substrate_immutable": True,
        "runtime_access": READ_ONLY,
        "substrate_hash": before["artifact_hash"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("isolation artifact must be a JSON object")
    canonical_serialize(artifact)
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("isolation artifact hash is required")
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash")
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError("isolation artifact hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
