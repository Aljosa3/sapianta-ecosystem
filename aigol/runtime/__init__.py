"""AiGOL mock-first runtime engine foundation."""

from .mock_provider import MockProvider
from .governed_contract_authorization_gate import (
    ContractAuthorizationResult,
    authorize_governed_execution_contract,
    reconstruct_authorization_lineage,
)
from .governed_execution_contract import GovernedExecutionContract, create_governed_execution_contract, reconstruct_contract_lineage
from .governed_execution_session import GovernedExecutionSession, create_governed_execution_session, reconstruct_session_lineage
from .models import FailClosedRuntimeError, GovernedReturnArtifact, ProviderResponse, RuntimePackage, replay_hash
from .provider_interface import ProviderInterface
from .runtime_engine import RuntimeEngine
from .session_lineage_replay_validator import validate_session_lineage_replay
from .worker_lifecycle import BLOCKED, CLOSED, CREATED, DISPATCHED, PREPARED, RETURNED, RUNNING, WorkerLifecycle

__all__ = [
    "BLOCKED",
    "CLOSED",
    "ContractAuthorizationResult",
    "CREATED",
    "DISPATCHED",
    "FailClosedRuntimeError",
    "GovernedReturnArtifact",
    "GovernedExecutionContract",
    "GovernedExecutionSession",
    "MockProvider",
    "PREPARED",
    "ProviderInterface",
    "ProviderResponse",
    "RETURNED",
    "RUNNING",
    "RuntimeEngine",
    "RuntimePackage",
    "WorkerLifecycle",
    "authorize_governed_execution_contract",
    "create_governed_execution_contract",
    "create_governed_execution_session",
    "reconstruct_authorization_lineage",
    "reconstruct_contract_lineage",
    "reconstruct_session_lineage",
    "replay_hash",
    "validate_session_lineage_replay",
]
