"""Platform Core Cognition Layer foundation.

G16-01 registers PCCL as a first-class Platform Core service boundary. G16-02
adds deterministic session state. G16-03 adds a canonical context envelope that
aggregates certified Platform Core references only. G16-04 adds a canonical
policy envelope that aggregates governance boundary references only. G16-08
adds reference binding for existing Platform Core services; it does not execute
those services, generate prompts, evaluate policy, authorize execution, invoke
providers, generate proposals, or run cognitive loops.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, NoReturn

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PCCL_SERVICE_VERSION = "G16_01_PLATFORM_CORE_COGNITION_LAYER_FOUNDATION_V1"
PCCL_SESSION_RUNTIME_VERSION = "G16_02_PCCL_SESSION_RUNTIME_V1"
PCCL_CONTEXT_ENVELOPE_VERSION = "G16_03_CANONICAL_CONTEXT_ENVELOPE_V1"
PCCL_POLICY_ENVELOPE_VERSION = "G16_04_CANONICAL_POLICY_ENVELOPE_V1"
PCCL_REFERENCE_BINDING_VERSION = "G16_08_PCCL_REFERENCE_BINDING_V1"
PCCL_SERVICE_NAME = "PlatformCoreCognitionLayer"
PCCL_FOUNDATION_STATUS = "PCCL_FOUNDATION_REGISTERED"
PCCL_SESSION_DECLARED = "PCCL_SESSION_DECLARED"
PCCL_RESERVED_FOR_FUTURE_MILESTONE = "PCCL_RESERVED_FOR_FUTURE_MILESTONE"

PCCL_SESSION_RUNTIME_ARTIFACT_V1 = "PCCL_SESSION_RUNTIME_ARTIFACT_V1"
CANONICAL_CONTEXT_ENVELOPE_ARTIFACT_V1 = "CANONICAL_CONTEXT_ENVELOPE_ARTIFACT_V1"
CANONICAL_POLICY_ENVELOPE_ARTIFACT_V1 = "CANONICAL_POLICY_ENVELOPE_ARTIFACT_V1"
PCCL_REFERENCE_BINDING_ARTIFACT_V1 = "PCCL_REFERENCE_BINDING_ARTIFACT_V1"
PCCL_SESSION_CREATED = "PCCL_SESSION_CREATED"
PCCL_SESSION_ACTIVE = "PCCL_SESSION_ACTIVE"
PCCL_SESSION_WAITING = "PCCL_SESSION_WAITING"
PCCL_SESSION_COMPLETED = "PCCL_SESSION_COMPLETED"
PCCL_SESSION_ESCALATED = "PCCL_SESSION_ESCALATED"
PCCL_SESSION_CLOSED = "PCCL_SESSION_CLOSED"

PCCL_TERMINAL_SESSION_STATUSES = frozenset(
    {
        PCCL_SESSION_COMPLETED,
        PCCL_SESSION_ESCALATED,
        PCCL_SESSION_CLOSED,
    }
)
PCCL_ALLOWED_SESSION_STATUSES = frozenset(
    {
        PCCL_SESSION_CREATED,
        PCCL_SESSION_ACTIVE,
        PCCL_SESSION_WAITING,
        PCCL_SESSION_COMPLETED,
        PCCL_SESSION_ESCALATED,
        PCCL_SESSION_CLOSED,
    }
)

PCCL_RESPONSIBILITIES = (
    "cognition orchestration",
    "cognitive session lifecycle",
    "provider orchestration future contract",
    "proposal lifecycle future contract",
)

PCCL_NON_RESPONSIBILITIES = (
    "semantic interpretation",
    "Human Intent Resolution",
    "clarification",
    "governance",
    "runtime entry",
    "runtime continuation",
    "replay",
    "worker execution",
    "certification",
)

PCCL_INTEGRATION_POINTS = (
    "Human Intent Resolution",
    "Clarification Planning",
    "Clarification Satisfaction Verification",
    "Clarification Decision Explainability",
    "Canonical Semantic Artifact",
    "Knowledge Reuse",
    "Governance",
    "Runtime Entry",
    "Runtime Continuation",
    "Replay Observation",
    "Replay Certification",
    "Certification Registry",
    "Provider Registry",
    "Worker Infrastructure",
)

PCCL_LIFECYCLE = (
    "Human Goal",
    "Platform Core",
    "PlatformCoreCognitionLayer",
    "existing Platform Core services",
    "Runtime",
    "Replay",
    "Certification",
)

PCCL_AUTHORITY_FLAGS = {
    "semantic_interpretation_authority": False,
    "human_intent_resolution_authority": False,
    "clarification_authority": False,
    "governance_authority": False,
    "runtime_authority": False,
    "replay_authority": False,
    "certification_authority": False,
    "provider_execution_authority": False,
    "proposal_generation_authority": False,
    "worker_execution_authority": False,
}

CANONICAL_CONTEXT_REFERENCE_TYPES = frozenset(
    {
        "HUMAN_GOAL",
        "PCCL_SESSION",
        "CANONICAL_SEMANTIC_ARTIFACT",
        "KNOWLEDGE_REUSE",
        "CLARIFICATION_RESULT",
        "RUNTIME_REFERENCE",
        "REPLAY_REFERENCE",
        "GOVERNANCE_REFERENCE",
        "CERTIFICATION_REFERENCE",
    }
)

CONTEXT_REFERENCE_OWNER_BY_TYPE = {
    "HUMAN_GOAL": "PLATFORM_CORE_HUMAN_INTENT_RESOLUTION",
    "PCCL_SESSION": "PLATFORM_CORE_COGNITION_LAYER",
    "CANONICAL_SEMANTIC_ARTIFACT": "PLATFORM_CORE_SEMANTICS",
    "KNOWLEDGE_REUSE": "PLATFORM_CORE_KNOWLEDGE_REUSE",
    "CLARIFICATION_RESULT": "PLATFORM_CORE_CLARIFICATION",
    "RUNTIME_REFERENCE": "PLATFORM_CORE_RUNTIME",
    "REPLAY_REFERENCE": "PLATFORM_CORE_REPLAY",
    "GOVERNANCE_REFERENCE": "PLATFORM_CORE_GOVERNANCE",
    "CERTIFICATION_REFERENCE": "PLATFORM_CORE_CERTIFICATION",
}

CANONICAL_POLICY_REFERENCE_TYPES = frozenset(
    {
        "PCCL_SESSION",
        "CONTEXT_ENVELOPE",
        "GOVERNANCE_POLICY",
        "CONSTITUTIONAL_CONSTRAINT",
        "REPLAY_REQUIREMENT",
        "HUMAN_APPROVAL_REQUIREMENT",
        "PROVIDER_PERMISSION",
        "WORKER_BOUNDARY",
        "CERTIFICATION_REQUIREMENT",
    }
)

POLICY_REFERENCE_OWNER_BY_TYPE = {
    "PCCL_SESSION": "PLATFORM_CORE_COGNITION_LAYER",
    "CONTEXT_ENVELOPE": "PLATFORM_CORE_COGNITION_LAYER",
    "GOVERNANCE_POLICY": "PLATFORM_CORE_GOVERNANCE",
    "CONSTITUTIONAL_CONSTRAINT": "PLATFORM_CORE_GOVERNANCE",
    "REPLAY_REQUIREMENT": "PLATFORM_CORE_REPLAY",
    "HUMAN_APPROVAL_REQUIREMENT": "HUMAN_AUTHORITY",
    "PROVIDER_PERMISSION": "PROVIDER_PLATFORM",
    "WORKER_BOUNDARY": "WORKER_PLATFORM",
    "CERTIFICATION_REQUIREMENT": "PLATFORM_CORE_CERTIFICATION",
}

PCCL_BINDING_REFERENCE_TYPES = frozenset(
    {
        "PCCL_SESSION",
        "CONTEXT_ENVELOPE",
        "POLICY_ENVELOPE",
        "HUMAN_INTENT_RESOLUTION",
        "DEVELOPMENT_INTENT_RESOLUTION",
        "CAPABILITY_DISCOVERY",
        "KNOWLEDGE_REUSE",
        "CLARIFICATION",
        "CANONICAL_SEMANTIC_ARTIFACT",
        "RUNTIME",
        "GOVERNANCE",
        "REPLAY",
        "CERTIFICATION_REGISTRY",
        "PROVIDER_PLATFORM",
        "WORKER_RESOLUTION",
    }
)

BINDING_REFERENCE_OWNER_BY_TYPE = {
    "PCCL_SESSION": "PLATFORM_CORE_COGNITION_LAYER",
    "CONTEXT_ENVELOPE": "PLATFORM_CORE_COGNITION_LAYER",
    "POLICY_ENVELOPE": "PLATFORM_CORE_COGNITION_LAYER",
    "HUMAN_INTENT_RESOLUTION": "PLATFORM_CORE_HUMAN_INTENT_RESOLUTION",
    "DEVELOPMENT_INTENT_RESOLUTION": "PLATFORM_CORE_HUMAN_INTENT_RESOLUTION",
    "CAPABILITY_DISCOVERY": "PLATFORM_CORE_HUMAN_INTENT_RESOLUTION",
    "KNOWLEDGE_REUSE": "PLATFORM_CORE_KNOWLEDGE_REUSE",
    "CLARIFICATION": "PLATFORM_CORE_CLARIFICATION",
    "CANONICAL_SEMANTIC_ARTIFACT": "PLATFORM_CORE_SEMANTICS",
    "RUNTIME": "PLATFORM_CORE_RUNTIME",
    "GOVERNANCE": "PLATFORM_CORE_GOVERNANCE",
    "REPLAY": "PLATFORM_CORE_REPLAY",
    "CERTIFICATION_REGISTRY": "PLATFORM_CORE_CERTIFICATION",
    "PROVIDER_PLATFORM": "PROVIDER_PLATFORM",
    "WORKER_RESOLUTION": "WORKER_PLATFORM",
}


@dataclass(frozen=True)
class PCCLSession:
    """Deterministic declaration of a future PCCL cognitive session lifecycle."""

    session_id: str
    human_goal_reference: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "artifact_type": "PCCL_SESSION_V1",
            "pccl_service_version": PCCL_SERVICE_VERSION,
            "session_id": _require_string(self.session_id, "session_id"),
            "human_goal_reference": _require_string(
                self.human_goal_reference,
                "human_goal_reference",
            ),
            "created_at": _require_string(self.created_at, "created_at"),
            "lifecycle_status": PCCL_SESSION_DECLARED,
            "cognition_loop_started": False,
            "context_assembled": False,
            "policy_evaluated": False,
            "provider_invoked": False,
            "proposal_generated": False,
            "worker_invoked": False,
            "replay_certified": False,
            "authority_flags": deepcopy(PCCL_AUTHORITY_FLAGS),
        }
        artifact["artifact_hash"] = replay_hash(artifact)
        return artifact


@dataclass(frozen=True)
class PCCLContractDescriptor:
    """Descriptor for a future PCCL contract without implementing behavior."""

    contract_name: str
    future_capability: str

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "artifact_type": "PCCL_CONTRACT_DESCRIPTOR_V1",
            "pccl_service_version": PCCL_SERVICE_VERSION,
            "contract_name": _require_string(self.contract_name, "contract_name"),
            "future_capability": _require_string(
                self.future_capability,
                "future_capability",
            ),
            "contract_status": PCCL_RESERVED_FOR_FUTURE_MILESTONE,
            "behavior_implemented": False,
            "provider_invocation_implemented": False,
            "context_assembly_implemented": False,
            "policy_evaluation_implemented": False,
            "proposal_generation_implemented": False,
            "cognitive_loop_implemented": False,
            "authority_flags": deepcopy(PCCL_AUTHORITY_FLAGS),
        }
        artifact["artifact_hash"] = replay_hash(artifact)
        return artifact


class ContextAssembler:
    """Future PCCL context assembly contract."""

    contract_name = "ContextAssembler"

    def assemble_context(self, *_args: Any, **_kwargs: Any) -> NoReturn:
        _reserved("context assembly")


class PolicyEnvelope:
    """Future PCCL policy envelope contract."""

    contract_name = "PolicyEnvelope"

    def evaluate_policy(self, *_args: Any, **_kwargs: Any) -> NoReturn:
        _reserved("policy evaluation")


class ProviderRuntime:
    """Future PCCL provider orchestration contract."""

    contract_name = "ProviderRuntime"

    def invoke_provider(self, *_args: Any, **_kwargs: Any) -> NoReturn:
        _reserved("provider invocation")


class ProposalPipeline:
    """Future PCCL proposal lifecycle contract."""

    contract_name = "ProposalPipeline"

    def create_proposal(self, *_args: Any, **_kwargs: Any) -> NoReturn:
        _reserved("proposal generation")


class CognitiveLoopController:
    """Future PCCL cognitive loop controller contract."""

    contract_name = "CognitiveLoopController"

    def run_loop(self, *_args: Any, **_kwargs: Any) -> NoReturn:
        _reserved("cognitive loop")


class PlatformCoreCognitionLayer:
    """First-class PCCL service boundary for future governed cognition."""

    def service_manifest(self) -> dict[str, Any]:
        return platform_core_cognition_layer_manifest()

    def declare_session(
        self,
        *,
        session_id: str,
        human_goal_reference: str,
        created_at: str,
    ) -> dict[str, Any]:
        return PCCLSession(
            session_id=session_id,
            human_goal_reference=human_goal_reference,
            created_at=created_at,
        ).to_dict()

    def contract_descriptors(self) -> tuple[dict[str, Any], ...]:
        return platform_core_cognition_layer_contract_descriptors()

    def create_session(
        self,
        *,
        session_id: str,
        creation_timestamp: str,
        originating_human_goal_reference: str,
        replay_reference: str = "",
        runtime_reference: str = "",
        certification_reference: str = "",
        provider_budget: int = 0,
    ) -> dict[str, Any]:
        return create_pccl_session(
            session_id=session_id,
            creation_timestamp=creation_timestamp,
            originating_human_goal_reference=originating_human_goal_reference,
            replay_reference=replay_reference,
            runtime_reference=runtime_reference,
            certification_reference=certification_reference,
            provider_budget=provider_budget,
        )

    def start_session(self, *, session: dict[str, Any], updated_at: str) -> dict[str, Any]:
        return start_pccl_session(session=session, updated_at=updated_at)

    def mark_session_waiting(
        self,
        *,
        session: dict[str, Any],
        waiting_reason: str,
        updated_at: str,
    ) -> dict[str, Any]:
        return mark_pccl_session_waiting(
            session=session,
            waiting_reason=waiting_reason,
            updated_at=updated_at,
        )

    def mark_session_completed(
        self,
        *,
        session: dict[str, Any],
        completion_reference: str,
        updated_at: str,
    ) -> dict[str, Any]:
        return mark_pccl_session_completed(
            session=session,
            completion_reference=completion_reference,
            updated_at=updated_at,
        )

    def mark_session_escalated(
        self,
        *,
        session: dict[str, Any],
        escalation_reference: str,
        termination_reason: str,
        updated_at: str,
    ) -> dict[str, Any]:
        return mark_pccl_session_escalated(
            session=session,
            escalation_reference=escalation_reference,
            termination_reason=termination_reason,
            updated_at=updated_at,
        )

    def close_session(
        self,
        *,
        session: dict[str, Any],
        termination_reason: str,
        updated_at: str,
    ) -> dict[str, Any]:
        return close_pccl_session(
            session=session,
            termination_reason=termination_reason,
            updated_at=updated_at,
        )

    def create_context_envelope(
        self,
        *,
        envelope_id: str,
        created_at: str,
        pccl_session: dict[str, Any],
        context_references: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    ) -> dict[str, Any]:
        return create_canonical_context_envelope(
            envelope_id=envelope_id,
            created_at=created_at,
            pccl_session=pccl_session,
            context_references=context_references,
        )

    def create_policy_envelope(
        self,
        *,
        policy_envelope_id: str,
        created_at: str,
        pccl_session: dict[str, Any],
        context_envelope: dict[str, Any],
        policy_references: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    ) -> dict[str, Any]:
        return create_canonical_policy_envelope(
            policy_envelope_id=policy_envelope_id,
            created_at=created_at,
            pccl_session=pccl_session,
            context_envelope=context_envelope,
            policy_references=policy_references,
        )

    def create_reference_binding(
        self,
        *,
        binding_id: str,
        created_at: str,
        pccl_session: dict[str, Any],
        context_envelope: dict[str, Any],
        policy_envelope: dict[str, Any],
        service_references: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    ) -> dict[str, Any]:
        return create_pccl_reference_binding(
            binding_id=binding_id,
            created_at=created_at,
            pccl_session=pccl_session,
            context_envelope=context_envelope,
            policy_envelope=policy_envelope,
            service_references=service_references,
        )


def platform_core_cognition_layer_manifest() -> dict[str, Any]:
    """Return deterministic PCCL ownership, lifecycle, and boundary metadata."""

    manifest = {
        "artifact_type": "PLATFORM_CORE_COGNITION_LAYER_MANIFEST_V1",
        "service_name": PCCL_SERVICE_NAME,
        "service_version": PCCL_SERVICE_VERSION,
        "foundation_status": PCCL_FOUNDATION_STATUS,
        "platform_core_service": True,
        "architectural_owner": "PLATFORM_CORE",
        "implementation_owner": "aigol.runtime.platform_core_cognition_layer",
        "responsibilities": list(PCCL_RESPONSIBILITIES),
        "non_responsibilities": list(PCCL_NON_RESPONSIBILITIES),
        "integration_points": list(PCCL_INTEGRATION_POINTS),
        "deterministic_lifecycle": list(PCCL_LIFECYCLE),
        "contracts": [descriptor["contract_name"] for descriptor in _contract_descriptor_dicts()],
        "canonical_context_envelope_implemented": True,
        "canonical_policy_envelope_implemented": True,
        "pccl_reference_binding_implemented": True,
        "cognition_loop_implemented": False,
        "provider_invocation_implemented": False,
        "context_assembly_implemented": False,
        "policy_evaluation_implemented": False,
        "proposal_generation_implemented": False,
        "runtime_behavior_modified": False,
        "governance_behavior_modified": False,
        "replay_behavior_modified": False,
        "human_interface_behavior_modified": False,
        "authority_flags": deepcopy(PCCL_AUTHORITY_FLAGS),
    }
    manifest["artifact_hash"] = replay_hash(manifest)
    return manifest


def platform_core_cognition_layer_contract_descriptors() -> tuple[dict[str, Any], ...]:
    """Return deterministic descriptors for future PCCL contracts."""

    return tuple(deepcopy(descriptor) for descriptor in _contract_descriptor_dicts())


def create_pccl_session(
    *,
    session_id: str,
    creation_timestamp: str,
    originating_human_goal_reference: str,
    replay_reference: str = "",
    runtime_reference: str = "",
    certification_reference: str = "",
    provider_budget: int = 0,
) -> dict[str, Any]:
    """Create a deterministic PCCL session runtime artifact.

    The session is state only: it does not assemble context, evaluate policy,
    invoke providers, generate proposals, persist replay, or certify anything.
    """

    budget = _require_nonnegative_int(provider_budget, "provider_budget")
    artifact = _session_artifact(
        session_id=session_id,
        creation_timestamp=creation_timestamp,
        updated_at=creation_timestamp,
        session_status=PCCL_SESSION_CREATED,
        iteration_counter=0,
        replay_reference=replay_reference,
        originating_human_goal_reference=originating_human_goal_reference,
        runtime_reference=runtime_reference,
        certification_reference=certification_reference,
        provider_budget=budget,
        provider_budget_remaining=budget,
        termination_reason=None,
        lifecycle_events=[],
        waiting_reason=None,
        completion_reference=None,
        escalation_reference=None,
    )
    event = _session_event(
        event_index=0,
        event_type="pccl_session_created",
        occurred_at=creation_timestamp,
        previous_event_hash="",
        event_payload={
            "session_id": artifact["session_id"],
            "originating_human_goal_reference": artifact["originating_human_goal_reference"],
            "provider_budget": budget,
        },
    )
    return _with_events(artifact, [event])


def start_pccl_session(*, session: dict[str, Any], updated_at: str) -> dict[str, Any]:
    """Mark a created or waiting PCCL session active."""

    current = _validated_session(session)
    _require_mutable_session(current)
    if current["session_status"] not in {PCCL_SESSION_CREATED, PCCL_SESSION_WAITING}:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: session cannot be started")
    return _transition(
        current,
        session_status=PCCL_SESSION_ACTIVE,
        updated_at=updated_at,
        event_type="pccl_session_started",
        event_payload={"session_status": PCCL_SESSION_ACTIVE},
        waiting_reason=None,
    )


def mark_pccl_session_waiting(
    *,
    session: dict[str, Any],
    waiting_reason: str,
    updated_at: str,
) -> dict[str, Any]:
    """Mark a PCCL session waiting on a future Platform Core service."""

    current = _validated_session(session)
    _require_mutable_session(current)
    if current["session_status"] not in {PCCL_SESSION_CREATED, PCCL_SESSION_ACTIVE}:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: session cannot wait")
    reason = _require_string(waiting_reason, "waiting_reason")
    return _transition(
        current,
        session_status=PCCL_SESSION_WAITING,
        updated_at=updated_at,
        event_type="pccl_session_waiting",
        event_payload={"waiting_reason": reason},
        waiting_reason=reason,
    )


def mark_pccl_session_completed(
    *,
    session: dict[str, Any],
    completion_reference: str,
    updated_at: str,
) -> dict[str, Any]:
    """Mark a PCCL session complete without approving or certifying work."""

    current = _validated_session(session)
    _require_mutable_session(current)
    reference = _require_string(completion_reference, "completion_reference")
    return _transition(
        current,
        session_status=PCCL_SESSION_COMPLETED,
        updated_at=updated_at,
        event_type="pccl_session_completed",
        event_payload={"completion_reference": reference},
        completion_reference=reference,
        termination_reason="completed",
    )


def mark_pccl_session_escalated(
    *,
    session: dict[str, Any],
    escalation_reference: str,
    termination_reason: str,
    updated_at: str,
) -> dict[str, Any]:
    """Mark a PCCL session escalated to existing Platform Core governance/human review."""

    current = _validated_session(session)
    _require_mutable_session(current)
    reference = _require_string(escalation_reference, "escalation_reference")
    reason = _require_string(termination_reason, "termination_reason")
    return _transition(
        current,
        session_status=PCCL_SESSION_ESCALATED,
        updated_at=updated_at,
        event_type="pccl_session_escalated",
        event_payload={
            "escalation_reference": reference,
            "termination_reason": reason,
        },
        escalation_reference=reference,
        termination_reason=reason,
    )


def close_pccl_session(
    *,
    session: dict[str, Any],
    termination_reason: str,
    updated_at: str,
) -> dict[str, Any]:
    """Close a PCCL session fail-closed or administratively."""

    current = _validated_session(session)
    _require_mutable_session(current)
    reason = _require_string(termination_reason, "termination_reason")
    return _transition(
        current,
        session_status=PCCL_SESSION_CLOSED,
        updated_at=updated_at,
        event_type="pccl_session_closed",
        event_payload={"termination_reason": reason},
        termination_reason=reason,
    )


def create_canonical_context_envelope(
    *,
    envelope_id: str,
    created_at: str,
    pccl_session: dict[str, Any],
    context_references: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    """Create a deterministic PCCL context envelope of references only.

    The envelope aggregates certified Platform Core references for future
    providers. It does not inspect referenced content, derive semantics,
    generate prompts, invoke providers, modify governance, or persist replay.
    """

    session = _validated_session(pccl_session)
    references = _canonical_context_references(session=session, context_references=context_references)
    artifact = {
        "artifact_type": CANONICAL_CONTEXT_ENVELOPE_ARTIFACT_V1,
        "pccl_service_version": PCCL_SERVICE_VERSION,
        "pccl_session_runtime_version": PCCL_SESSION_RUNTIME_VERSION,
        "pccl_context_envelope_version": PCCL_CONTEXT_ENVELOPE_VERSION,
        "envelope_id": _require_string(envelope_id, "envelope_id"),
        "created_at": _require_string(created_at, "created_at"),
        "pccl_session_id": session["session_id"],
        "pccl_session_status": session["session_status"],
        "pccl_session_hash": session["artifact_hash"],
        "human_goal_reference": session["originating_human_goal_reference"],
        "context_references": references,
        "context_reference_count": len(references),
        "included_reference_types": sorted({reference["reference_type"] for reference in references}),
        "source_owners": {
            reference_type: CONTEXT_REFERENCE_OWNER_BY_TYPE[reference_type]
            for reference_type in sorted({reference["reference_type"] for reference in references})
        },
        "context_references_aggregated": True,
        "reference_only_envelope": True,
        "certified_artifact_payload_embedded": False,
        "semantic_interpretation_performed": False,
        "prompt_generated": False,
        "provider_invoked": False,
        "policy_evaluated": False,
        "proposal_generated": False,
        "clarification_requested": False,
        "governance_modified": False,
        "runtime_invoked": False,
        "worker_invoked": False,
        "replay_modified": False,
        "replay_certified": False,
        "certification_performed": False,
        "provider_specific": False,
        "authority_flags": deepcopy(PCCL_AUTHORITY_FLAGS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_canonical_context_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    """Fail-closed validation for a canonical PCCL context envelope."""

    return _validated_context_envelope(envelope)


def create_canonical_policy_envelope(
    *,
    policy_envelope_id: str,
    created_at: str,
    pccl_session: dict[str, Any],
    context_envelope: dict[str, Any],
    policy_references: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    """Create a deterministic PCCL policy envelope of references only.

    The envelope carries canonical governance and execution-boundary references
    for future providers. It does not execute policy, evaluate policy, grant
    authorization, invoke governance, invoke providers, or invoke workers.
    """

    session = _validated_session(pccl_session)
    context = _validated_context_envelope(context_envelope)
    if context["pccl_session_id"] != session["session_id"] or context["pccl_session_hash"] != session["artifact_hash"]:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: context session mismatch")
    references = _canonical_policy_references(
        session=session,
        context_envelope=context,
        policy_references=policy_references,
    )
    artifact = {
        "artifact_type": CANONICAL_POLICY_ENVELOPE_ARTIFACT_V1,
        "pccl_service_version": PCCL_SERVICE_VERSION,
        "pccl_session_runtime_version": PCCL_SESSION_RUNTIME_VERSION,
        "pccl_context_envelope_version": PCCL_CONTEXT_ENVELOPE_VERSION,
        "pccl_policy_envelope_version": PCCL_POLICY_ENVELOPE_VERSION,
        "policy_envelope_id": _require_string(policy_envelope_id, "policy_envelope_id"),
        "created_at": _require_string(created_at, "created_at"),
        "pccl_session_id": session["session_id"],
        "pccl_session_status": session["session_status"],
        "pccl_session_hash": session["artifact_hash"],
        "context_envelope_id": context["envelope_id"],
        "context_envelope_hash": context["artifact_hash"],
        "human_goal_reference": session["originating_human_goal_reference"],
        "policy_references": references,
        "policy_reference_count": len(references),
        "included_policy_reference_types": sorted({reference["reference_type"] for reference in references}),
        "source_owners": {
            reference_type: POLICY_REFERENCE_OWNER_BY_TYPE[reference_type]
            for reference_type in sorted({reference["reference_type"] for reference in references})
        },
        "policy_references_aggregated": True,
        "reference_only_envelope": True,
        "governance_policy_payload_embedded": False,
        "policy_executed": False,
        "policy_evaluated": False,
        "authorization_granted": False,
        "governance_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "runtime_invoked": False,
        "prompt_generated": False,
        "proposal_generated": False,
        "replay_modified": False,
        "replay_certified": False,
        "certification_performed": False,
        "provider_specific": False,
        "authority_flags": deepcopy(PCCL_AUTHORITY_FLAGS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_canonical_policy_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    """Fail-closed validation for a canonical PCCL policy envelope."""

    return _validated_policy_envelope(envelope)


def create_pccl_reference_binding(
    *,
    binding_id: str,
    created_at: str,
    pccl_session: dict[str, Any],
    context_envelope: dict[str, Any],
    policy_envelope: dict[str, Any],
    service_references: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    """Create a deterministic binding from PCCL artifacts to existing services.

    The binding is reference-only. It validates PCCL-owned wrappers and records
    owner-bound service references, but it never executes, resolves, governs,
    invokes, certifies, or dereferences those services.
    """

    session = _validated_session(pccl_session)
    context = _validated_context_envelope(context_envelope)
    policy = _validated_policy_envelope(policy_envelope)
    if context["pccl_session_id"] != session["session_id"] or context["pccl_session_hash"] != session["artifact_hash"]:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: context session mismatch")
    if policy["pccl_session_id"] != session["session_id"] or policy["pccl_session_hash"] != session["artifact_hash"]:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: policy session mismatch")
    if policy["context_envelope_id"] != context["envelope_id"] or policy["context_envelope_hash"] != context["artifact_hash"]:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: policy context mismatch")
    references = _canonical_binding_references(
        session=session,
        context_envelope=context,
        policy_envelope=policy,
        service_references=service_references,
    )
    artifact = {
        "artifact_type": PCCL_REFERENCE_BINDING_ARTIFACT_V1,
        "pccl_service_version": PCCL_SERVICE_VERSION,
        "pccl_session_runtime_version": PCCL_SESSION_RUNTIME_VERSION,
        "pccl_context_envelope_version": PCCL_CONTEXT_ENVELOPE_VERSION,
        "pccl_policy_envelope_version": PCCL_POLICY_ENVELOPE_VERSION,
        "pccl_reference_binding_version": PCCL_REFERENCE_BINDING_VERSION,
        "binding_id": _require_string(binding_id, "binding_id"),
        "created_at": _require_string(created_at, "created_at"),
        "pccl_session_id": session["session_id"],
        "pccl_session_status": session["session_status"],
        "pccl_session_hash": session["artifact_hash"],
        "context_envelope_id": context["envelope_id"],
        "context_envelope_hash": context["artifact_hash"],
        "policy_envelope_id": policy["policy_envelope_id"],
        "policy_envelope_hash": policy["artifact_hash"],
        "binding_references": references,
        "binding_reference_count": len(references),
        "included_binding_reference_types": sorted({reference["reference_type"] for reference in references}),
        "source_owners": {
            reference_type: BINDING_REFERENCE_OWNER_BY_TYPE[reference_type]
            for reference_type in sorted({reference["reference_type"] for reference in references})
        },
        "platform_core_services_bound": True,
        "reference_only_binding": True,
        "reference_payload_embedded": False,
        "platform_core_service_invoked": False,
        "provider_runtime_created": False,
        "capability_resolver_created": False,
        "capability_resolution_performed": False,
        "governance_logic_duplicated": False,
        "governance_invoked": False,
        "runtime_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_modified": False,
        "replay_certified": False,
        "certification_performed": False,
        "proposal_pipeline_implemented": False,
        "cognitive_loop_implemented": False,
        "prompt_generated": False,
        "new_runtime_behavior_introduced": False,
        "authority_flags": deepcopy(PCCL_AUTHORITY_FLAGS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_pccl_reference_binding(binding: dict[str, Any]) -> dict[str, Any]:
    """Fail-closed validation for a PCCL reference binding artifact."""

    return _validated_reference_binding(binding)


def _contract_descriptor_dicts() -> tuple[dict[str, Any], ...]:
    descriptors = (
        PCCLContractDescriptor("PCCLSession", "cognitive session lifecycle"),
        PCCLContractDescriptor("ContextAssembler", "canonical cognition context envelope"),
        PCCLContractDescriptor("PolicyEnvelope", "deterministic cognition policy envelope"),
        PCCLContractDescriptor("ProviderRuntime", "certified cognition provider orchestration"),
        PCCLContractDescriptor("ProposalPipeline", "non-authoritative proposal lifecycle"),
        PCCLContractDescriptor("CognitiveLoopController", "future governed cognitive loop control"),
    )
    return tuple(descriptor.to_dict() for descriptor in descriptors)


def _canonical_context_references(
    *,
    session: dict[str, Any],
    context_references: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    if not isinstance(context_references, (list, tuple)):
        raise FailClosedRuntimeError("canonical context envelope failed closed: context_references must be a sequence")
    references = [
        _context_reference_entry(
            reference_type="HUMAN_GOAL",
            reference=session["originating_human_goal_reference"],
            artifact_hash="",
            certification_reference=session["certification_reference"],
        ),
        _context_reference_entry(
            reference_type="PCCL_SESSION",
            reference=session["session_id"],
            artifact_hash=session["artifact_hash"],
            certification_reference=session["certification_reference"],
        ),
    ]
    references.extend(_context_reference_entry_from_dict(reference) for reference in context_references)
    unique: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for reference in references:
        key = (
            reference["reference_type"],
            reference["reference"],
            reference["artifact_hash"],
            reference["certification_reference"],
        )
        unique[key] = reference
    return [
        deepcopy(unique[key])
        for key in sorted(unique, key=lambda item: (item[0], item[1], item[2], item[3]))
    ]


def _context_reference_entry_from_dict(reference: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(reference, dict):
        raise FailClosedRuntimeError("canonical context envelope failed closed: context reference must be object")
    return _context_reference_entry(
        reference_type=reference.get("reference_type"),
        reference=reference.get("reference"),
        artifact_hash=reference.get("artifact_hash", ""),
        certification_reference=reference.get("certification_reference", ""),
    )


def _context_reference_entry(
    *,
    reference_type: Any,
    reference: Any,
    artifact_hash: Any,
    certification_reference: Any,
) -> dict[str, Any]:
    normalized_type = _normalize_context_reference_type(reference_type)
    entry = {
        "reference_type": normalized_type,
        "reference_owner": CONTEXT_REFERENCE_OWNER_BY_TYPE[normalized_type],
        "reference": _require_string(reference, "context reference"),
        "artifact_hash": _optional_artifact_hash(artifact_hash),
        "certification_reference": _optional_string(certification_reference),
        "reference_payload_embedded": False,
        "semantic_interpretation_performed": False,
        "prompt_generated": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    entry["reference_hash"] = replay_hash(entry)
    return entry


def _canonical_policy_references(
    *,
    session: dict[str, Any],
    context_envelope: dict[str, Any],
    policy_references: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    if not isinstance(policy_references, (list, tuple)):
        raise FailClosedRuntimeError("canonical policy envelope failed closed: policy_references must be a sequence")
    references = [
        _policy_reference_entry(
            reference_type="PCCL_SESSION",
            reference=session["session_id"],
            artifact_hash=session["artifact_hash"],
            certification_reference=session["certification_reference"],
        ),
        _policy_reference_entry(
            reference_type="CONTEXT_ENVELOPE",
            reference=context_envelope["envelope_id"],
            artifact_hash=context_envelope["artifact_hash"],
            certification_reference=session["certification_reference"],
        ),
    ]
    references.extend(_policy_reference_entry_from_dict(reference) for reference in policy_references)
    unique: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for reference in references:
        key = (
            reference["reference_type"],
            reference["reference"],
            reference["artifact_hash"],
            reference["certification_reference"],
        )
        unique[key] = reference
    return [
        deepcopy(unique[key])
        for key in sorted(unique, key=lambda item: (item[0], item[1], item[2], item[3]))
    ]


def _canonical_binding_references(
    *,
    session: dict[str, Any],
    context_envelope: dict[str, Any],
    policy_envelope: dict[str, Any],
    service_references: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    if not isinstance(service_references, (list, tuple)):
        raise FailClosedRuntimeError("PCCL reference binding failed closed: service_references must be a sequence")
    references = [
        _binding_reference_entry(
            reference_type="PCCL_SESSION",
            reference=session["session_id"],
            artifact_hash=session["artifact_hash"],
            certification_reference=session["certification_reference"],
        ),
        _binding_reference_entry(
            reference_type="CONTEXT_ENVELOPE",
            reference=context_envelope["envelope_id"],
            artifact_hash=context_envelope["artifact_hash"],
            certification_reference=session["certification_reference"],
        ),
        _binding_reference_entry(
            reference_type="POLICY_ENVELOPE",
            reference=policy_envelope["policy_envelope_id"],
            artifact_hash=policy_envelope["artifact_hash"],
            certification_reference=session["certification_reference"],
        ),
    ]
    references.extend(_binding_reference_entry_from_dict(reference) for reference in service_references)
    unique: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for reference in references:
        key = (
            reference["reference_type"],
            reference["reference"],
            reference["artifact_hash"],
            reference["certification_reference"],
        )
        unique[key] = reference
    return [
        deepcopy(unique[key])
        for key in sorted(unique, key=lambda item: (item[0], item[1], item[2], item[3]))
    ]


def _binding_reference_entry_from_dict(reference: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(reference, dict):
        raise FailClosedRuntimeError("PCCL reference binding failed closed: service reference must be object")
    return _binding_reference_entry(
        reference_type=reference.get("reference_type"),
        reference=reference.get("reference"),
        artifact_hash=reference.get("artifact_hash", ""),
        certification_reference=reference.get("certification_reference", ""),
    )


def _binding_reference_entry(
    *,
    reference_type: Any,
    reference: Any,
    artifact_hash: Any,
    certification_reference: Any,
) -> dict[str, Any]:
    normalized_type = _normalize_binding_reference_type(reference_type)
    entry = {
        "reference_type": normalized_type,
        "reference_owner": BINDING_REFERENCE_OWNER_BY_TYPE[normalized_type],
        "reference": _require_string(reference, "binding reference"),
        "artifact_hash": _optional_artifact_hash(artifact_hash),
        "certification_reference": _optional_string(certification_reference),
        "reference_payload_embedded": False,
        "service_invoked": False,
        "logic_duplicated": False,
        "semantic_interpretation_performed": False,
        "capability_resolution_performed": False,
        "governance_invoked": False,
        "runtime_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_modified": False,
        "replay_certified": False,
        "certification_performed": False,
        "prompt_generated": False,
    }
    entry["reference_hash"] = replay_hash(entry)
    return entry


def _policy_reference_entry_from_dict(reference: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(reference, dict):
        raise FailClosedRuntimeError("canonical policy envelope failed closed: policy reference must be object")
    return _policy_reference_entry(
        reference_type=reference.get("reference_type"),
        reference=reference.get("reference"),
        artifact_hash=reference.get("artifact_hash", ""),
        certification_reference=reference.get("certification_reference", ""),
    )


def _policy_reference_entry(
    *,
    reference_type: Any,
    reference: Any,
    artifact_hash: Any,
    certification_reference: Any,
) -> dict[str, Any]:
    normalized_type = _normalize_policy_reference_type(reference_type)
    entry = {
        "reference_type": normalized_type,
        "reference_owner": POLICY_REFERENCE_OWNER_BY_TYPE[normalized_type],
        "reference": _require_string(reference, "policy reference"),
        "artifact_hash": _optional_artifact_hash(artifact_hash),
        "certification_reference": _optional_string(certification_reference),
        "reference_payload_embedded": False,
        "policy_executed": False,
        "policy_evaluated": False,
        "authorization_granted": False,
        "governance_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_modified": False,
    }
    entry["reference_hash"] = replay_hash(entry)
    return entry


def _transition(
    session: dict[str, Any],
    *,
    session_status: str,
    updated_at: str,
    event_type: str,
    event_payload: dict[str, Any],
    waiting_reason: str | None = None,
    completion_reference: str | None = None,
    escalation_reference: str | None = None,
    termination_reason: str | None = None,
) -> dict[str, Any]:
    event = _session_event(
        event_index=len(session["lifecycle_events"]),
        event_type=event_type,
        occurred_at=updated_at,
        previous_event_hash=session["lifecycle_events"][-1]["event_hash"],
        event_payload=event_payload,
    )
    artifact = _session_artifact(
        session_id=session["session_id"],
        creation_timestamp=session["creation_timestamp"],
        updated_at=updated_at,
        session_status=session_status,
        iteration_counter=session["iteration_counter"],
        replay_reference=session["replay_reference"],
        originating_human_goal_reference=session["originating_human_goal_reference"],
        runtime_reference=session["runtime_reference"],
        certification_reference=session["certification_reference"],
        provider_budget=session["provider_budget"],
        provider_budget_remaining=session["provider_budget_remaining"],
        termination_reason=termination_reason if termination_reason is not None else session["termination_reason"],
        lifecycle_events=session["lifecycle_events"],
        waiting_reason=waiting_reason,
        completion_reference=completion_reference or session["completion_reference"],
        escalation_reference=escalation_reference or session["escalation_reference"],
    )
    return _with_events(artifact, session["lifecycle_events"] + [event])


def _session_artifact(
    *,
    session_id: str,
    creation_timestamp: str,
    updated_at: str,
    session_status: str,
    iteration_counter: int,
    replay_reference: str,
    originating_human_goal_reference: str,
    runtime_reference: str,
    certification_reference: str,
    provider_budget: int,
    provider_budget_remaining: int,
    termination_reason: str | None,
    lifecycle_events: list[dict[str, Any]],
    waiting_reason: str | None,
    completion_reference: str | None,
    escalation_reference: str | None,
) -> dict[str, Any]:
    if session_status not in PCCL_ALLOWED_SESSION_STATUSES:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: unsupported session status")
    budget = _require_nonnegative_int(provider_budget, "provider_budget")
    budget_remaining = _require_nonnegative_int(provider_budget_remaining, "provider_budget_remaining")
    if budget_remaining > budget:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: remaining budget exceeds budget")
    artifact = {
        "artifact_type": PCCL_SESSION_RUNTIME_ARTIFACT_V1,
        "pccl_service_version": PCCL_SERVICE_VERSION,
        "pccl_session_runtime_version": PCCL_SESSION_RUNTIME_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "creation_timestamp": _require_string(creation_timestamp, "creation_timestamp"),
        "updated_at": _require_string(updated_at, "updated_at"),
        "session_status": session_status,
        "iteration_counter": _require_nonnegative_int(iteration_counter, "iteration_counter"),
        "replay_reference": _optional_string(replay_reference),
        "originating_human_goal_reference": _require_string(
            originating_human_goal_reference,
            "originating_human_goal_reference",
        ),
        "runtime_reference": _optional_string(runtime_reference),
        "certification_reference": _optional_string(certification_reference),
        "provider_budget": budget,
        "provider_budget_remaining": budget_remaining,
        "termination_reason": termination_reason if isinstance(termination_reason, str) and termination_reason else None,
        "waiting_reason": waiting_reason if isinstance(waiting_reason, str) and waiting_reason else None,
        "completion_reference": completion_reference
        if isinstance(completion_reference, str) and completion_reference
        else None,
        "escalation_reference": escalation_reference
        if isinstance(escalation_reference, str) and escalation_reference
        else None,
        "lifecycle_events": deepcopy(lifecycle_events),
        "cognition_loop_started": False,
        "context_assembled": False,
        "policy_evaluated": False,
        "provider_invoked": False,
        "proposal_generated": False,
        "clarification_requested": False,
        "governance_performed": False,
        "worker_invoked": False,
        "replay_implemented": False,
        "replay_certified": False,
        "certification_performed": False,
        "authority_flags": deepcopy(PCCL_AUTHORITY_FLAGS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _with_events(artifact: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    updated = deepcopy(artifact)
    updated["lifecycle_events"] = deepcopy(events)
    updated["artifact_hash"] = replay_hash({key: value for key, value in updated.items() if key != "artifact_hash"})
    return updated


def _session_event(
    *,
    event_index: int,
    event_type: str,
    occurred_at: str,
    previous_event_hash: str,
    event_payload: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "event_index": _require_nonnegative_int(event_index, "event_index"),
        "event_type": _require_string(event_type, "event_type"),
        "occurred_at": _require_string(occurred_at, "occurred_at"),
        "previous_event_hash": previous_event_hash,
        "event_payload": deepcopy(event_payload),
        "provider_invoked": False,
        "proposal_generated": False,
        "worker_invoked": False,
        "governance_performed": False,
        "replay_certified": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _validated_session(session: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(session, dict):
        raise FailClosedRuntimeError("PCCL session runtime failed closed: session must be object")
    if session.get("artifact_type") != PCCL_SESSION_RUNTIME_ARTIFACT_V1:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: invalid artifact type")
    expected = deepcopy(session)
    actual_hash = expected.pop("artifact_hash", None)
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("PCCL session runtime failed closed: artifact hash mismatch")
    if session.get("pccl_session_runtime_version") != PCCL_SESSION_RUNTIME_VERSION:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: invalid runtime version")
    if session.get("session_status") not in PCCL_ALLOWED_SESSION_STATUSES:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: invalid session status")
    if session.get("provider_budget_remaining") > session.get("provider_budget"):
        raise FailClosedRuntimeError("PCCL session runtime failed closed: invalid provider budget")
    for flag in (
        "cognition_loop_started",
        "context_assembled",
        "policy_evaluated",
        "provider_invoked",
        "proposal_generated",
        "clarification_requested",
        "governance_performed",
        "worker_invoked",
        "replay_implemented",
        "replay_certified",
        "certification_performed",
    ):
        if session.get(flag) is not False:
            raise FailClosedRuntimeError(f"PCCL session runtime failed closed: {flag} must be false")
    events = session.get("lifecycle_events")
    if not isinstance(events, list) or not events:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: lifecycle events required")
    for index, event in enumerate(events):
        _validated_event(event, index)
        expected_previous = "" if index == 0 else events[index - 1]["event_hash"]
        if event["previous_event_hash"] != expected_previous:
            raise FailClosedRuntimeError("PCCL session runtime failed closed: event lineage mismatch")
    return deepcopy(session)


def _validated_context_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, dict):
        raise FailClosedRuntimeError("canonical context envelope failed closed: envelope must be object")
    if envelope.get("artifact_type") != CANONICAL_CONTEXT_ENVELOPE_ARTIFACT_V1:
        raise FailClosedRuntimeError("canonical context envelope failed closed: invalid artifact type")
    expected = deepcopy(envelope)
    actual_hash = expected.pop("artifact_hash", None)
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("canonical context envelope failed closed: artifact hash mismatch")
    if envelope.get("pccl_context_envelope_version") != PCCL_CONTEXT_ENVELOPE_VERSION:
        raise FailClosedRuntimeError("canonical context envelope failed closed: invalid version")
    references = envelope.get("context_references")
    if not isinstance(references, list) or not references:
        raise FailClosedRuntimeError("canonical context envelope failed closed: references required")
    recalculated_types = sorted({reference.get("reference_type") for reference in references})
    if envelope.get("included_reference_types") != recalculated_types:
        raise FailClosedRuntimeError("canonical context envelope failed closed: reference type index mismatch")
    if envelope.get("context_reference_count") != len(references):
        raise FailClosedRuntimeError("canonical context envelope failed closed: reference count mismatch")
    if "HUMAN_GOAL" not in recalculated_types or "PCCL_SESSION" not in recalculated_types:
        raise FailClosedRuntimeError("canonical context envelope failed closed: required references missing")
    if envelope.get("context_references_aggregated") is not True or envelope.get("reference_only_envelope") is not True:
        raise FailClosedRuntimeError("canonical context envelope failed closed: reference-only invariants invalid")
    expected_source_owners = {
        reference_type: CONTEXT_REFERENCE_OWNER_BY_TYPE[reference_type]
        for reference_type in recalculated_types
    }
    if envelope.get("source_owners") != expected_source_owners:
        raise FailClosedRuntimeError("canonical context envelope failed closed: source owner index mismatch")
    if envelope.get("authority_flags") != PCCL_AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("canonical context envelope failed closed: authority flags invalid")
    for flag in (
        "certified_artifact_payload_embedded",
        "semantic_interpretation_performed",
        "prompt_generated",
        "provider_invoked",
        "policy_evaluated",
        "proposal_generated",
        "clarification_requested",
        "governance_modified",
        "runtime_invoked",
        "worker_invoked",
        "replay_modified",
        "replay_certified",
        "certification_performed",
        "provider_specific",
    ):
        if envelope.get(flag) is not False:
            raise FailClosedRuntimeError(f"canonical context envelope failed closed: {flag} must be false")
    for reference in references:
        _validated_context_reference(reference)
    return deepcopy(envelope)


def _validated_context_reference(reference: Any) -> None:
    if not isinstance(reference, dict):
        raise FailClosedRuntimeError("canonical context envelope failed closed: reference must be object")
    expected = deepcopy(reference)
    actual_hash = expected.pop("reference_hash", None)
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("canonical context envelope failed closed: reference hash mismatch")
    _normalize_context_reference_type(reference.get("reference_type"))
    if reference.get("reference_owner") != CONTEXT_REFERENCE_OWNER_BY_TYPE[reference["reference_type"]]:
        raise FailClosedRuntimeError("canonical context envelope failed closed: reference owner mismatch")
    _require_string(reference.get("reference"), "context reference")
    _optional_artifact_hash(reference.get("artifact_hash", ""))
    for flag in (
        "reference_payload_embedded",
        "semantic_interpretation_performed",
        "prompt_generated",
        "provider_invoked",
        "governance_modified",
        "replay_modified",
    ):
        if reference.get(flag) is not False:
            raise FailClosedRuntimeError(f"canonical context envelope failed closed: reference {flag} must be false")


def _validated_policy_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, dict):
        raise FailClosedRuntimeError("canonical policy envelope failed closed: envelope must be object")
    if envelope.get("artifact_type") != CANONICAL_POLICY_ENVELOPE_ARTIFACT_V1:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: invalid artifact type")
    expected = deepcopy(envelope)
    actual_hash = expected.pop("artifact_hash", None)
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("canonical policy envelope failed closed: artifact hash mismatch")
    if envelope.get("pccl_policy_envelope_version") != PCCL_POLICY_ENVELOPE_VERSION:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: invalid version")
    references = envelope.get("policy_references")
    if not isinstance(references, list) or not references:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: references required")
    recalculated_types = sorted({reference.get("reference_type") for reference in references})
    if envelope.get("included_policy_reference_types") != recalculated_types:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: reference type index mismatch")
    if envelope.get("policy_reference_count") != len(references):
        raise FailClosedRuntimeError("canonical policy envelope failed closed: reference count mismatch")
    if "PCCL_SESSION" not in recalculated_types or "CONTEXT_ENVELOPE" not in recalculated_types:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: required references missing")
    if envelope.get("policy_references_aggregated") is not True or envelope.get("reference_only_envelope") is not True:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: reference-only invariants invalid")
    expected_source_owners = {
        reference_type: POLICY_REFERENCE_OWNER_BY_TYPE[reference_type]
        for reference_type in recalculated_types
    }
    if envelope.get("source_owners") != expected_source_owners:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: source owner index mismatch")
    if envelope.get("authority_flags") != PCCL_AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: authority flags invalid")
    for flag in (
        "governance_policy_payload_embedded",
        "policy_executed",
        "policy_evaluated",
        "authorization_granted",
        "governance_invoked",
        "provider_invoked",
        "worker_invoked",
        "runtime_invoked",
        "prompt_generated",
        "proposal_generated",
        "replay_modified",
        "replay_certified",
        "certification_performed",
        "provider_specific",
    ):
        if envelope.get(flag) is not False:
            raise FailClosedRuntimeError(f"canonical policy envelope failed closed: {flag} must be false")
    for reference in references:
        _validated_policy_reference(reference)
    return deepcopy(envelope)


def _validated_policy_reference(reference: Any) -> None:
    if not isinstance(reference, dict):
        raise FailClosedRuntimeError("canonical policy envelope failed closed: reference must be object")
    expected = deepcopy(reference)
    actual_hash = expected.pop("reference_hash", None)
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("canonical policy envelope failed closed: reference hash mismatch")
    _normalize_policy_reference_type(reference.get("reference_type"))
    if reference.get("reference_owner") != POLICY_REFERENCE_OWNER_BY_TYPE[reference["reference_type"]]:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: reference owner mismatch")
    _require_string(reference.get("reference"), "policy reference")
    _optional_artifact_hash(reference.get("artifact_hash", ""))
    for flag in (
        "reference_payload_embedded",
        "policy_executed",
        "policy_evaluated",
        "authorization_granted",
        "governance_invoked",
        "provider_invoked",
        "worker_invoked",
        "replay_modified",
    ):
        if reference.get(flag) is not False:
            raise FailClosedRuntimeError(f"canonical policy envelope failed closed: reference {flag} must be false")


def _validated_reference_binding(binding: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(binding, dict):
        raise FailClosedRuntimeError("PCCL reference binding failed closed: binding must be object")
    if binding.get("artifact_type") != PCCL_REFERENCE_BINDING_ARTIFACT_V1:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: invalid artifact type")
    expected = deepcopy(binding)
    actual_hash = expected.pop("artifact_hash", None)
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("PCCL reference binding failed closed: artifact hash mismatch")
    if binding.get("pccl_reference_binding_version") != PCCL_REFERENCE_BINDING_VERSION:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: invalid version")
    references = binding.get("binding_references")
    if not isinstance(references, list) or not references:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: references required")
    recalculated_types = sorted({reference.get("reference_type") for reference in references})
    if binding.get("included_binding_reference_types") != recalculated_types:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: reference type index mismatch")
    if binding.get("binding_reference_count") != len(references):
        raise FailClosedRuntimeError("PCCL reference binding failed closed: reference count mismatch")
    if not {"PCCL_SESSION", "CONTEXT_ENVELOPE", "POLICY_ENVELOPE"}.issubset(set(recalculated_types)):
        raise FailClosedRuntimeError("PCCL reference binding failed closed: required references missing")
    if binding.get("platform_core_services_bound") is not True or binding.get("reference_only_binding") is not True:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: reference-only invariants invalid")
    expected_source_owners = {
        reference_type: BINDING_REFERENCE_OWNER_BY_TYPE[reference_type]
        for reference_type in recalculated_types
    }
    if binding.get("source_owners") != expected_source_owners:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: source owner index mismatch")
    if binding.get("authority_flags") != PCCL_AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: authority flags invalid")
    for flag in (
        "reference_payload_embedded",
        "platform_core_service_invoked",
        "provider_runtime_created",
        "capability_resolver_created",
        "capability_resolution_performed",
        "governance_logic_duplicated",
        "governance_invoked",
        "runtime_invoked",
        "provider_invoked",
        "worker_invoked",
        "replay_modified",
        "replay_certified",
        "certification_performed",
        "proposal_pipeline_implemented",
        "cognitive_loop_implemented",
        "prompt_generated",
        "new_runtime_behavior_introduced",
    ):
        if binding.get(flag) is not False:
            raise FailClosedRuntimeError(f"PCCL reference binding failed closed: {flag} must be false")
    for reference in references:
        _validated_binding_reference(reference)
    return deepcopy(binding)


def _validated_binding_reference(reference: Any) -> None:
    if not isinstance(reference, dict):
        raise FailClosedRuntimeError("PCCL reference binding failed closed: reference must be object")
    expected = deepcopy(reference)
    actual_hash = expected.pop("reference_hash", None)
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("PCCL reference binding failed closed: reference hash mismatch")
    _normalize_binding_reference_type(reference.get("reference_type"))
    if reference.get("reference_owner") != BINDING_REFERENCE_OWNER_BY_TYPE[reference["reference_type"]]:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: reference owner mismatch")
    _require_string(reference.get("reference"), "binding reference")
    _optional_artifact_hash(reference.get("artifact_hash", ""))
    for flag in (
        "reference_payload_embedded",
        "service_invoked",
        "logic_duplicated",
        "semantic_interpretation_performed",
        "capability_resolution_performed",
        "governance_invoked",
        "runtime_invoked",
        "provider_invoked",
        "worker_invoked",
        "replay_modified",
        "replay_certified",
        "certification_performed",
        "prompt_generated",
    ):
        if reference.get(flag) is not False:
            raise FailClosedRuntimeError(f"PCCL reference binding failed closed: reference {flag} must be false")


def _validated_event(event: Any, expected_index: int) -> None:
    if not isinstance(event, dict):
        raise FailClosedRuntimeError("PCCL session runtime failed closed: event must be object")
    if event.get("event_index") != expected_index:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: event order mismatch")
    expected = deepcopy(event)
    actual_hash = expected.pop("event_hash", None)
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("PCCL session runtime failed closed: event hash mismatch")
    for flag in (
        "provider_invoked",
        "proposal_generated",
        "worker_invoked",
        "governance_performed",
        "replay_certified",
    ):
        if event.get(flag) is not False:
            raise FailClosedRuntimeError(f"PCCL session runtime failed closed: event {flag} must be false")


def _require_mutable_session(session: dict[str, Any]) -> None:
    if session["session_status"] in PCCL_TERMINAL_SESSION_STATUSES:
        raise FailClosedRuntimeError("PCCL session runtime failed closed: terminal session cannot transition")


def _reserved(capability_name: str) -> NoReturn:
    raise FailClosedRuntimeError(f"PCCL {capability_name} is reserved for a future governed milestone")


def _require_nonnegative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise FailClosedRuntimeError(f"{field_name} must be a nonnegative integer")
    return value


def _optional_string(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise FailClosedRuntimeError("optional PCCL reference must be string")
    return value.strip()


def _optional_artifact_hash(value: Any) -> str:
    artifact_hash = _optional_string(value)
    if artifact_hash and not artifact_hash.startswith("sha256:"):
        raise FailClosedRuntimeError("canonical context envelope failed closed: artifact_hash must be sha256 reference")
    return artifact_hash


def _normalize_context_reference_type(value: Any) -> str:
    reference_type = _require_string(value, "reference_type").upper().replace("-", "_").replace(" ", "_")
    if reference_type not in CANONICAL_CONTEXT_REFERENCE_TYPES:
        raise FailClosedRuntimeError("canonical context envelope failed closed: unsupported reference type")
    return reference_type


def _normalize_policy_reference_type(value: Any) -> str:
    reference_type = _require_string(value, "reference_type").upper().replace("-", "_").replace(" ", "_")
    if reference_type not in CANONICAL_POLICY_REFERENCE_TYPES:
        raise FailClosedRuntimeError("canonical policy envelope failed closed: unsupported reference type")
    return reference_type


def _normalize_binding_reference_type(value: Any) -> str:
    reference_type = _require_string(value, "reference_type").upper().replace("-", "_").replace(" ", "_")
    if reference_type not in PCCL_BINDING_REFERENCE_TYPES:
        raise FailClosedRuntimeError("PCCL reference binding failed closed: unsupported reference type")
    return reference_type


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
