"""Bounded writable runtime state for Codex CLI execution."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_binding import stable_hash


DEFAULT_RUNTIME_STATE_ROOT = Path("/tmp/sapianta_codex_runtime")
SESSION_ID_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{7,96}$")


def runtime_state_session_id(*, provider_id: str, invocation_id: str, replay_identity: str) -> str:
    digest = stable_hash(
        {
            "invocation_id": invocation_id,
            "provider_id": provider_id,
            "replay_identity": replay_identity,
        }
    )
    return f"CODEX-RUNTIME-{digest[:24].upper()}"


def runtime_state_path_for(
    *,
    provider_id: str,
    invocation_id: str,
    replay_identity: str,
    runtime_state_root: str | Path = DEFAULT_RUNTIME_STATE_ROOT,
) -> Path:
    return Path(runtime_state_root) / runtime_state_session_id(
        provider_id=provider_id,
        invocation_id=invocation_id,
        replay_identity=replay_identity,
    )


@dataclass(frozen=True)
class BoundedRuntimeState:
    provider_id: str
    invocation_id: str
    replay_identity: str
    runtime_state_root: str
    runtime_state_dir: str
    session_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "invocation_id": self.invocation_id,
            "replay_identity": self.replay_identity,
            "runtime_state_root": self.runtime_state_root,
            "runtime_state_dir": self.runtime_state_dir,
            "session_id": self.session_id,
            "cleanup_policy": "CALLER_REMOVES_AFTER_EVIDENCE_IF_DESIRED",
            "home_directory_mutation_allowed": False,
            "repo_root_state_allowed": False,
            "global_state_mutation_allowed": False,
            "arbitrary_env_mutation_allowed": False,
            "replay_safe": True,
        }


def create_bounded_runtime_state(
    *,
    provider_id: str,
    invocation_id: str,
    replay_identity: str,
    runtime_state_root: str | Path = DEFAULT_RUNTIME_STATE_ROOT,
) -> BoundedRuntimeState:
    root = Path(runtime_state_root)
    session_id = runtime_state_session_id(
        provider_id=provider_id,
        invocation_id=invocation_id,
        replay_identity=replay_identity,
    )
    return BoundedRuntimeState(
        provider_id=provider_id,
        invocation_id=invocation_id,
        replay_identity=replay_identity,
        runtime_state_root=str(root),
        runtime_state_dir=str(root / session_id),
        session_id=session_id,
    )


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def validate_bounded_runtime_state(state: Any) -> dict[str, Any]:
    value = state.to_dict() if hasattr(state, "to_dict") else state
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "runtime_state", "reason": "must be an object"}]}
    for field in ("provider_id", "invocation_id", "replay_identity", "runtime_state_root", "runtime_state_dir", "session_id"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "runtime state field must be non-empty"})
    root = Path(value.get("runtime_state_root", ""))
    state_dir = Path(value.get("runtime_state_dir", ""))
    if ".." in root.parts or ".." in state_dir.parts:
        errors.append({"field": "runtime_state_dir", "reason": "runtime state path must not contain parent traversal"})
    if not state_dir.is_absolute() or not root.is_absolute():
        errors.append({"field": "runtime_state_dir", "reason": "runtime state paths must be absolute"})
    if not errors and not _is_relative_to(state_dir, root):
        errors.append({"field": "runtime_state_dir", "reason": "runtime state dir escapes approved root"})
    if not errors and state_dir == root:
        errors.append({"field": "runtime_state_dir", "reason": "runtime state must be session-isolated below root"})
    session_id = value.get("session_id", "")
    if isinstance(session_id, str) and SESSION_ID_PATTERN.match(session_id) is None:
        errors.append({"field": "session_id", "reason": "runtime state session id has invalid format"})
    if not errors:
        expected = runtime_state_path_for(
            provider_id=value["provider_id"],
            invocation_id=value["invocation_id"],
            replay_identity=value["replay_identity"],
            runtime_state_root=root,
        )
        if state_dir != expected:
            errors.append({"field": "runtime_state_dir", "reason": "runtime state path is not deterministic"})
    for field in (
        "home_directory_mutation_allowed",
        "repo_root_state_allowed",
        "global_state_mutation_allowed",
        "arbitrary_env_mutation_allowed",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "runtime state boundary violation"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "runtime state must be replay-safe"})
    return {"valid": not errors, "errors": errors, "runtime_state_bounded": not errors}


def ensure_bounded_runtime_state_dirs(state: dict[str, Any]) -> None:
    state_dir = Path(state["runtime_state_dir"])
    for child in (state_dir, state_dir / "cache", state_dir / "config", state_dir / "tmp"):
        child.mkdir(parents=True, exist_ok=True)


def bounded_runtime_state_env(state: dict[str, Any]) -> dict[str, str]:
    state_dir = Path(state["runtime_state_dir"])
    return {
        "HOME": str(state_dir),
        "XDG_CACHE_HOME": str(state_dir / "cache"),
        "XDG_CONFIG_HOME": str(state_dir / "config"),
        "TMPDIR": str(state_dir / "tmp"),
    }


def validate_bounded_runtime_state_env(env: Any, state: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(env, dict):
        return {"valid": False, "errors": [{"field": "runtime_state_env", "reason": "must be an object"}]}
    allowed = bounded_runtime_state_env(state)
    for key, expected in allowed.items():
        if env.get(key) != expected:
            errors.append({"field": key, "reason": "runtime state env path mismatch"})
    extra = sorted(set(env) - set(allowed))
    if extra:
        errors.append({"field": "runtime_state_env", "reason": f"unsupported runtime state env keys: {extra}"})
    state_dir = Path(state["runtime_state_dir"])
    for key, path in env.items():
        if ".." in Path(path).parts or not _is_relative_to(Path(path), state_dir):
            errors.append({"field": key, "reason": "runtime state env escapes state dir"})
    return {"valid": not errors, "errors": errors}
