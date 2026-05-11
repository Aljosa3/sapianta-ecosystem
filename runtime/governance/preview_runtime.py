"""Governed local preview runtime command preparation.

This module validates and prepares the bounded localhost preview command for
LOCALHOST_PREVIEW_RUNTIME_V1. It never starts a server and never executes shell
commands.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .capability_models import CapabilityDecision
from .capability_registry import (
    LOCALHOST_PREVIEW_RUNTIME_V1,
    evaluate_capability_request,
)
from .primitive_replay import build_deterministic_result_hash, build_replay_identity


PREVIEW_APP_TARGET = "sapianta_system.sapianta_product.main:app"
PRIMITIVE_ID = "GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1"
SCOPE_ID = "LOCALHOST_UVICORN_PREVIEW_ONLY"
PREVIEW_COMMAND = (
    "uvicorn",
    PREVIEW_APP_TARGET,
    "--host",
    "127.0.0.1",
    "--port",
    "8010",
)
PREVIEW_LIFECYCLE = ("start", "validate", "stop")
REPLAY_LINEAGE = (
    "AGENTS.md",
    "docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md",
    "docs/governance/GOVERNED_CAPABILITY_MEMORY_V1.md",
    "docs/governance/GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1.md",
    "runtime/governance/capability_registry.py",
    "runtime/governance/preview_runtime.py",
    "tests/test_governed_preview_runtime.py",
)


@dataclass(frozen=True)
class PreviewRuntimeRequest:
    capability_id: str = "LOCALHOST_PREVIEW_RUNTIME_V1"
    host: str = "127.0.0.1"
    port: int = 8010
    runtime: str = "uvicorn"
    app_target: str = PREVIEW_APP_TARGET
    lifecycle: tuple[str, ...] = PREVIEW_LIFECYCLE
    temporary: bool = True
    visual_validation: bool = True
    deployment: bool = False
    persistent: bool = False
    background_execution: bool = False
    public_network_exposure: bool = False
    mutation_scope_expands: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_target": self.app_target,
            "background_execution": self.background_execution,
            "capability_id": self.capability_id,
            "deployment": self.deployment,
            "host": self.host,
            "lifecycle": list(self.lifecycle),
            "mutation_scope_expands": self.mutation_scope_expands,
            "persistent": self.persistent,
            "port": self.port,
            "public_network_exposure": self.public_network_exposure,
            "runtime": self.runtime,
            "temporary": self.temporary,
            "visual_validation": self.visual_validation,
        }


@dataclass(frozen=True)
class PreviewRuntimeResult:
    primitive_id: str
    capability_id: str
    decision: str
    approved: bool
    escalation_required: bool
    rejected: bool
    command: tuple[str, ...]
    reason: str
    forbidden_boundary_checks: tuple[str, ...]
    lifecycle: tuple[str, ...]
    request_hash: str
    command_hash: str
    scope_hash: str
    replay_lineage: tuple[str, ...]
    deterministic_hash: str
    server_started: bool = False

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "approved": self.approved,
            "capability_id": self.capability_id,
            "command": list(self.command),
            "command_hash": self.command_hash,
            "decision": self.decision,
            "escalation_required": self.escalation_required,
            "forbidden_boundary_checks": list(self.forbidden_boundary_checks),
            "lifecycle": list(self.lifecycle),
            "primitive_id": self.primitive_id,
            "reason": self.reason,
            "rejected": self.rejected,
            "replay_lineage": list(self.replay_lineage),
            "request_hash": self.request_hash,
            "server_started": self.server_started,
            "scope_hash": self.scope_hash,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data


def describe_preview_lifecycle() -> dict[str, object]:
    return {
        "capability_id": LOCALHOST_PREVIEW_RUNTIME_V1.capability_id,
        "lifecycle": list(PREVIEW_LIFECYCLE),
        "meaning": {
            "start": "prepare a temporary localhost preview command",
            "validate": "use the preview for bounded visual/runtime verification",
            "stop": "terminate the temporary preview process",
        },
        "primitive_id": PRIMITIVE_ID,
        "replay_lineage": list(REPLAY_LINEAGE),
        "server_started_by_helper": False,
        "scope_hash": _scope_hash(),
        "scope_id": SCOPE_ID,
    }


def build_preview_command(request: PreviewRuntimeRequest | None = None) -> tuple[str, ...]:
    request = request or PreviewRuntimeRequest()
    if (
        request.capability_id != LOCALHOST_PREVIEW_RUNTIME_V1.capability_id
        or request.host != "127.0.0.1"
        or request.port != 8010
        or request.runtime != "uvicorn"
        or request.app_target != PREVIEW_APP_TARGET
        or tuple(request.lifecycle) != PREVIEW_LIFECYCLE
        or not request.temporary
    ):
        return ()
    return PREVIEW_COMMAND


def validate_preview_request(request: PreviewRuntimeRequest) -> PreviewRuntimeResult:
    forbidden = _forbidden_boundary_checks(request)

    capability_evaluation = evaluate_capability_request(
        capability_id=request.capability_id,
        host=request.host,
        port=request.port,
        runtime=request.runtime,
        lifecycle=tuple(request.lifecycle),
        temporary=request.temporary,
        visual_validation=request.visual_validation,
        deployment=request.deployment,
        persistent=request.persistent,
        background_execution=request.background_execution,
        public_network_exposure=request.public_network_exposure,
        mutation_scope_expands=request.mutation_scope_expands,
    )

    if request.app_target != PREVIEW_APP_TARGET:
        decision = CapabilityDecision.ESCALATED.value
        reason = "app target change requires renewed approval"
        approved = False
        escalation_required = True
        rejected = False
        command: tuple[str, ...] = ()
    else:
        decision = capability_evaluation.decision.value
        reason = capability_evaluation.reason
        approved = capability_evaluation.decision is CapabilityDecision.APPROVED
        escalation_required = capability_evaluation.escalation_required
        rejected = capability_evaluation.decision is CapabilityDecision.REJECTED
        command = build_preview_command(request) if approved else ()

    base = {
        "approved": approved,
        "capability_id": request.capability_id,
        "command": list(command),
        "decision": decision,
        "escalation_required": escalation_required,
        "forbidden_boundary_checks": list(forbidden),
        "lifecycle": list(request.lifecycle),
        "reason": reason,
        "rejected": rejected,
        "server_started": False,
    }
    replay_identity = build_replay_identity(
        primitive_id=PRIMITIVE_ID,
        request_payload=request.to_dict(),
        command=command,
        scope_payload=_scope_payload(),
        replay_lineage=REPLAY_LINEAGE,
    )
    hash_payload = {
        **base,
        "command_hash": replay_identity["command_hash"],
        "primitive_id": replay_identity["primitive_id"],
        "replay_lineage": list(REPLAY_LINEAGE),
        "request_hash": replay_identity["request_hash"],
        "scope_hash": replay_identity["scope_hash"],
    }
    return PreviewRuntimeResult(
        primitive_id=str(replay_identity["primitive_id"]),
        capability_id=request.capability_id,
        decision=decision,
        approved=approved,
        escalation_required=escalation_required,
        rejected=rejected,
        command=command,
        reason=reason,
        forbidden_boundary_checks=forbidden,
        lifecycle=tuple(request.lifecycle),
        request_hash=str(replay_identity["request_hash"]),
        command_hash=str(replay_identity["command_hash"]),
        scope_hash=str(replay_identity["scope_hash"]),
        replay_lineage=REPLAY_LINEAGE,
        deterministic_hash=build_deterministic_result_hash(hash_payload),
    )


def _forbidden_boundary_checks(request: PreviewRuntimeRequest) -> tuple[str, ...]:
    checks: list[str] = []
    if request.host == "0.0.0.0" or request.public_network_exposure:
        checks.append("public_binding_forbidden")
    if request.deployment:
        checks.append("deployment_forbidden")
    if request.persistent:
        checks.append("daemon_persistence_forbidden")
    if request.background_execution:
        checks.append("background_permanent_service_forbidden")
    if request.mutation_scope_expands:
        checks.append("production_runtime_mutation_forbidden")
    if request.runtime != "uvicorn":
        checks.append("arbitrary_runtime_forbidden")
    if request.app_target != PREVIEW_APP_TARGET:
        checks.append("unapproved_app_target_forbidden")
    return tuple(sorted(checks))


def _scope_hash() -> str:
    return str(
        build_replay_identity(
            primitive_id=PRIMITIVE_ID,
            request_payload={},
            command=PREVIEW_COMMAND,
            scope_payload=_scope_payload(),
            replay_lineage=REPLAY_LINEAGE,
        )["scope_hash"]
    )


def _scope_payload() -> dict[str, object]:
    return {
        "allowed_command": list(PREVIEW_COMMAND),
        "app_target": PREVIEW_APP_TARGET,
        "capability_id": LOCALHOST_PREVIEW_RUNTIME_V1.capability_id,
        "host": "127.0.0.1",
        "lifecycle": list(PREVIEW_LIFECYCLE),
        "port": 8010,
        "primitive_id": PRIMITIVE_ID,
        "runtime": "uvicorn",
        "scope_id": SCOPE_ID,
    }
