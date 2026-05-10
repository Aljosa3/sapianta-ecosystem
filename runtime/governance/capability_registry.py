"""Static governed capability registry.

The registry is intentionally read-only and deterministic. It does not start
processes, launch preview servers, grant shell access, or persist background
services. It only evaluates whether a requested capability shape fits a
governance-approved scope.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from .capability_models import (
    CapabilityDecision,
    CapabilityEvaluation,
    CapabilityScope,
    CapabilityStatus,
    GovernedCapability,
)


LOCALHOST_PREVIEW_RUNTIME_V1 = GovernedCapability(
    capability_id="LOCALHOST_PREVIEW_RUNTIME_V1",
    status=CapabilityStatus.ACTIVE,
    allowed_scope=CapabilityScope(
        host="127.0.0.1",
        port=8010,
        runtime="uvicorn",
        lifecycle=("start", "validate", "stop"),
        temporary=True,
        visual_validation=True,
    ),
    forbidden_scope=(
        "deployment",
        "systemd changes",
        "daemon persistence",
        "firewall changes",
        "remote or public binding",
        "background permanent services",
        "autonomous runtime orchestration",
        "production runtime mutation",
        "unrestricted shell execution",
        "arbitrary subprocess execution",
    ),
    approval_semantics=(
        "approved only for temporary localhost preview",
        "approval is scoped to host 127.0.0.1",
        "approval is scoped to uvicorn preview runtime",
        "approval is scoped to start -> validate -> stop lifecycle",
        "approval does not imply deployment authority",
    ),
    replay_visibility=(
        "capability id is stable",
        "allowed scope is deterministic",
        "evaluation output is hashable",
        "approval and escalation decisions are reportable",
    ),
    revocation_semantics=(
        "revoked capability must reject all requests",
        "revocation must remain visible in registry state",
        "revocation does not mutate historical evidence",
    ),
    escalation_conditions=(
        "port changes",
        "host changes",
        "runtime becomes persistent",
        "deployment semantics appear",
        "background execution appears",
        "mutation scope expands",
        "public network exposure appears",
    ),
    lineage_references=(
        "AGENTS.md",
        "docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md",
        "docs/governance/GOVERNED_CAPABILITY_MEMORY_V1.md",
    ),
)


CAPABILITY_REGISTRY = {
    LOCALHOST_PREVIEW_RUNTIME_V1.capability_id: LOCALHOST_PREVIEW_RUNTIME_V1,
}


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def get_capability_registry() -> dict[str, dict[str, object]]:
    return {
        capability_id: capability.to_dict()
        for capability_id, capability in sorted(CAPABILITY_REGISTRY.items())
    }


def evaluate_capability_request(
    capability_id: str,
    *,
    host: str,
    port: int,
    runtime: str,
    lifecycle: tuple[str, ...],
    temporary: bool,
    visual_validation: bool,
    deployment: bool = False,
    persistent: bool = False,
    background_execution: bool = False,
    public_network_exposure: bool = False,
    mutation_scope_expands: bool = False,
    revoked: bool = False,
) -> CapabilityEvaluation:
    capability = CAPABILITY_REGISTRY.get(capability_id)
    if capability is None:
        return _evaluation(
            capability_id=capability_id,
            decision=CapabilityDecision.REJECTED,
            reason="unknown capability",
            scope_locked=False,
            escalation_required=True,
        )

    if revoked:
        capability = replace(capability, status=CapabilityStatus.REVOKED)

    if capability.status is CapabilityStatus.REVOKED:
        return _evaluation(
            capability_id=capability_id,
            decision=CapabilityDecision.REJECTED,
            reason="capability revoked",
            scope_locked=False,
            escalation_required=False,
        )

    if deployment:
        return _escalated(capability_id, "deployment semantics require renewed approval")
    if persistent:
        return _escalated(capability_id, "persistent runtime requires renewed approval")
    if background_execution:
        return _escalated(capability_id, "background execution requires renewed approval")
    if public_network_exposure:
        return _escalated(capability_id, "public network exposure requires renewed approval")
    if mutation_scope_expands:
        return _escalated(capability_id, "expanded mutation scope requires renewed approval")

    allowed = capability.allowed_scope
    if host != allowed.host:
        return _escalated(capability_id, "host change requires renewed approval")
    if port != allowed.port:
        return _escalated(capability_id, "port change requires renewed approval")
    if runtime != allowed.runtime:
        return _escalated(capability_id, "runtime change requires renewed approval")
    if tuple(lifecycle) != allowed.lifecycle:
        return _escalated(capability_id, "lifecycle change requires renewed approval")
    if temporary is not allowed.temporary:
        return _escalated(capability_id, "temporary lifecycle change requires renewed approval")
    if visual_validation is not allowed.visual_validation:
        return _escalated(capability_id, "visual validation scope change requires renewed approval")

    return _evaluation(
        capability_id=capability_id,
        decision=CapabilityDecision.APPROVED,
        reason="scope matches governed localhost preview capability",
        scope_locked=True,
        escalation_required=False,
    )


def _escalated(capability_id: str, reason: str) -> CapabilityEvaluation:
    return _evaluation(
        capability_id=capability_id,
        decision=CapabilityDecision.ESCALATED,
        reason=reason,
        scope_locked=False,
        escalation_required=True,
    )


def _evaluation(
    *,
    capability_id: str,
    decision: CapabilityDecision,
    reason: str,
    scope_locked: bool,
    escalation_required: bool,
) -> CapabilityEvaluation:
    base = {
        "capability_id": capability_id,
        "decision": decision.value,
        "escalation_required": escalation_required,
        "reason": reason,
        "replay_visible": True,
        "scope_locked": scope_locked,
    }
    return CapabilityEvaluation(
        capability_id=capability_id,
        decision=decision,
        reason=reason,
        replay_visible=True,
        scope_locked=scope_locked,
        escalation_required=escalation_required,
        deterministic_hash=stable_hash(base),
    )

