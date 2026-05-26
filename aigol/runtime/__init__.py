"""AiGOL mock-first runtime engine foundation."""

from .mock_provider import MockProvider
from .governed_contract_authorization_gate import (
    ContractAuthorizationResult,
    authorize_governed_execution_contract,
    reconstruct_authorization_lineage,
)
from .governed_contract_router import ContractRoutingResult, reconstruct_routing_lineage, route_authorized_contract
from .governed_execution_contract import GovernedExecutionContract, create_governed_execution_contract, reconstruct_contract_lineage
from .governed_execution_session import GovernedExecutionSession, create_governed_execution_session, reconstruct_session_lineage
from .governance_failure_semantics import GovernanceFailureEvidence, classify_governance_failure, reconstruct_failure_lineage
from .models import FailClosedRuntimeError, GovernedReturnArtifact, ProviderResponse, RuntimePackage, replay_hash
from .provider_interface import ProviderInterface
from .runtime_engine import RuntimeEngine
from .session_lineage_replay_validator import validate_session_lineage_replay
from .synthetic_cognition_pressure_simulator import (
    SyntheticCognitionPressureArtifact,
    generate_ambiguous_contract,
    generate_authority_drift_attempt,
    generate_long_chain_entropy_sequence,
    generate_provider_escalation_attempt,
    generate_replay_corruption_attempt,
    reconstruct_simulation_lineage,
)
from .worker_lifecycle import BLOCKED, CLOSED, CREATED, DISPATCHED, PREPARED, RETURNED, RUNNING, WorkerLifecycle

__all__ = [
    "BLOCKED",
    "CLOSED",
    "ContractAuthorizationResult",
    "ContractRoutingResult",
    "CREATED",
    "DISPATCHED",
    "FailClosedRuntimeError",
    "GovernedReturnArtifact",
    "GovernedExecutionContract",
    "GovernedExecutionSession",
    "GovernanceFailureEvidence",
    "MockProvider",
    "PREPARED",
    "ProviderInterface",
    "ProviderResponse",
    "RETURNED",
    "RUNNING",
    "RuntimeEngine",
    "RuntimePackage",
    "SyntheticCognitionPressureArtifact",
    "WorkerLifecycle",
    "authorize_governed_execution_contract",
    "classify_governance_failure",
    "create_governed_execution_contract",
    "create_governed_execution_session",
    "generate_ambiguous_contract",
    "generate_authority_drift_attempt",
    "generate_long_chain_entropy_sequence",
    "generate_provider_escalation_attempt",
    "generate_replay_corruption_attempt",
    "reconstruct_authorization_lineage",
    "reconstruct_contract_lineage",
    "reconstruct_failure_lineage",
    "reconstruct_routing_lineage",
    "reconstruct_session_lineage",
    "reconstruct_simulation_lineage",
    "replay_hash",
    "route_authorized_contract",
    "validate_session_lineage_replay",
]
