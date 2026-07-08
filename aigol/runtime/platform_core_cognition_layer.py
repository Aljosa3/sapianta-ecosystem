"""Platform Core Cognition Layer foundation.

G16-01 registers PCCL as a first-class Platform Core service boundary. The
module intentionally defines ownership, lifecycle, and future contracts only;
it does not assemble context, evaluate policy, invoke providers, generate
proposals, or run cognitive loops.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, NoReturn

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PCCL_SERVICE_VERSION = "G16_01_PLATFORM_CORE_COGNITION_LAYER_FOUNDATION_V1"
PCCL_SERVICE_NAME = "PlatformCoreCognitionLayer"
PCCL_FOUNDATION_STATUS = "PCCL_FOUNDATION_REGISTERED"
PCCL_SESSION_DECLARED = "PCCL_SESSION_DECLARED"
PCCL_RESERVED_FOR_FUTURE_MILESTONE = "PCCL_RESERVED_FOR_FUTURE_MILESTONE"

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


def _reserved(capability_name: str) -> NoReturn:
    raise FailClosedRuntimeError(f"PCCL {capability_name} is reserved for a future governed milestone")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
