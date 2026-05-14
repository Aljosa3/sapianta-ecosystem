"""Canonical bounded execution envelope model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .envelope_constraints import default_constraints
from .replay_binding import compute_replay_binding
from .workspace_scope import workspace_scope as build_workspace_scope


@dataclass(frozen=True)
class ExecutionEnvelope:
    envelope_id: str
    provider_id: str
    workspace_scope: dict[str, Any]
    authority_scope: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    timeout_seconds: int
    replay_identity: str
    validation_requirements: tuple[str, ...]
    human_approval_required: bool = False
    replay_safe: bool = True
    constraints: tuple[str, ...] = field(default_factory=lambda: tuple(default_constraints()))
    replay_binding_sha256: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = {
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "workspace_scope": self.workspace_scope,
            "authority_scope": list(self.authority_scope),
            "allowed_actions": list(self.allowed_actions),
            "forbidden_actions": list(self.forbidden_actions),
            "timeout_seconds": self.timeout_seconds,
            "replay_identity": self.replay_identity,
            "validation_requirements": list(self.validation_requirements),
            "human_approval_required": self.human_approval_required,
            "replay_safe": self.replay_safe,
            "constraints": list(self.constraints),
        }
        value["replay_binding_sha256"] = self.replay_binding_sha256 or compute_replay_binding(value)
        return value


def create_execution_envelope(
    *,
    envelope_id: str,
    provider_id: str,
    allowed_roots: list[str],
    authority_scope: list[str],
    allowed_actions: list[str],
    forbidden_actions: list[str],
    replay_identity: str,
    validation_requirements: list[str],
    timeout_seconds: int = 300,
    human_approval_required: bool = False,
) -> ExecutionEnvelope:
    return ExecutionEnvelope(
        envelope_id=envelope_id,
        provider_id=provider_id,
        workspace_scope=build_workspace_scope(
            allowed_roots,
            forbidden_roots=[".git", "sapianta_system/venv"],
            generated_artifact_roots=["sapianta_bridge/runtime/processing"],
        ),
        authority_scope=tuple(authority_scope),
        allowed_actions=tuple(sorted(allowed_actions)),
        forbidden_actions=tuple(sorted(forbidden_actions)),
        timeout_seconds=timeout_seconds,
        replay_identity=replay_identity,
        validation_requirements=tuple(sorted(validation_requirements)),
        human_approval_required=human_approval_required,
    )
