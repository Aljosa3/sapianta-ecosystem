"""AiGOL mock-first runtime engine foundation."""

from .mock_provider import MockProvider
from .bounded_llm_attachment_architecture import BoundedCognitionProposal, create_bounded_cognition_proposal, reconstruct_cognition_lineage
from .governed_contract_authorization_gate import (
    ContractAuthorizationResult,
    authorize_governed_execution_contract,
    reconstruct_authorization_lineage,
)
from .governed_contract_router import ContractRoutingResult, reconstruct_routing_lineage, route_authorized_contract
from .governed_execution_contract import GovernedExecutionContract, create_governed_execution_contract, reconstruct_contract_lineage
from .governed_execution_session import GovernedExecutionSession, create_governed_execution_session, reconstruct_session_lineage
from .governed_cognition_review_gate import (
    GovernedCognitionReviewResult,
    reconstruct_cognition_review_lineage,
    review_translated_cognition_candidate,
)
from .governed_proposal_translation_layer import (
    GovernedProposalTranslationResult,
    reconstruct_translation_lineage,
    translate_bounded_proposal,
)
from .governance_failure_semantics import GovernanceFailureEvidence, classify_governance_failure, reconstruct_failure_lineage
from .governance_promotion_discipline import GovernancePromotionResult, evaluate_governance_promotion, reconstruct_promotion_lineage
from .governance_resilience_certification_gate import (
    GovernanceResilienceCertificationResult,
    certify_governance_resilience,
    reconstruct_certification_lineage,
)
from .governed_return_interpretation import (
    GovernedReturnInterpretationArtifact,
    interpret_governed_execution_return,
    reconstruct_governed_return_lineage,
)
from .first_readonly_domain_experiment import (
    ReadonlyDomainExperimentEvidence,
    reconstruct_readonly_domain_experiment_lineage,
    run_governance_runtime_inspector_experiment,
)
from .first_real_operator_usage import (
    FirstRealOperatorUsageEvidence,
    reconstruct_first_real_operator_usage_lineage,
    run_first_real_operator_usage,
)
from .live_external_llm_provider import (
    LiveExternalLLMInferenceEvidence,
    invoke_live_external_llm_provider,
    reconstruct_live_external_llm_inference_lineage,
)
from .live_openai_runtime_connector import (
    LiveOpenAIRuntimeConnectorEvidence,
    invoke_live_openai_runtime_connector,
    reconstruct_live_openai_runtime_lineage,
)
from .live_runtime_observation_phase import (
    LiveRuntimeObservationArtifact,
    observe_ambiguity_telemetry,
    observe_cognition_drift,
    observe_governance_pressure,
    observe_replay_continuity,
    reconstruct_live_runtime_observation_lineage,
)
from .live_runtime_usage_validation import (
    LiveRuntimeUsageValidationEvidence,
    reconstruct_live_runtime_usage_validation_lineage,
    validate_live_runtime_usage,
)
from .live_semantic_pressure_validation import (
    LiveSemanticPressureValidationEvidence,
    reconstruct_live_semantic_pressure_lineage,
    validate_live_semantic_pressure,
)
from .models import FailClosedRuntimeError, GovernedReturnArtifact, ProviderResponse, RuntimePackage, replay_hash
from .minimal_real_llm_proposal_flow import normalize_real_llm_proposal_input, reconstruct_real_llm_proposal_lineage
from .minimal_governed_execution_path import (
    MinimalGovernedExecutionPathResult,
    execute_minimal_governed_path,
    reconstruct_minimal_governed_execution_lineage,
)
from .minimal_real_runtime_demo import (
    MinimalRealRuntimeDemoEvidence,
    reconstruct_minimal_real_runtime_demo_lineage,
    run_minimal_real_runtime_demo,
)
from .operator_interaction_loop import (
    OperatorInteractionLoopEvidence,
    reconstruct_operator_interaction_loop_lineage,
    run_operator_interaction_loop,
)
from .operator_cli import (
    RuntimeOperatorCLIEvidence,
    reconstruct_runtime_operator_cli_lineage,
    run_runtime_operator_cli,
)
from .production_isolation_foundation import (
    ProductionIsolationEvidence,
    reconstruct_production_isolation_lineage,
    validate_production_isolation,
)
from .provider_interface import ProviderInterface
from .real_external_llm_attachment import (
    attach_external_llm_response,
    external_model_response_hash,
    reconstruct_external_llm_proposal_lineage,
)
from .real_openai_api_invocation import (
    RealOpenAIAPIInvocationEvidence,
    invoke_real_openai_api,
    reconstruct_real_openai_api_invocation_lineage,
)
from .real_runtime_activation import (
    RealRuntimeActivationEvidence,
    activate_real_runtime,
    reconstruct_real_runtime_activation_lineage,
)
from .real_governed_execution_resilience_suite import (
    RealGovernedExecutionResilienceEvidence,
    reconstruct_real_governed_execution_resilience_lineage,
    run_real_governed_execution_resilience_suite,
)
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
    "BoundedCognitionProposal",
    "CLOSED",
    "ContractAuthorizationResult",
    "ContractRoutingResult",
    "CREATED",
    "DISPATCHED",
    "FailClosedRuntimeError",
    "FirstRealOperatorUsageEvidence",
    "GovernedReturnArtifact",
    "GovernedExecutionContract",
    "GovernedExecutionSession",
    "GovernedCognitionReviewResult",
    "GovernedProposalTranslationResult",
    "GovernedReturnInterpretationArtifact",
    "GovernanceFailureEvidence",
    "GovernancePromotionResult",
    "GovernanceResilienceCertificationResult",
    "LiveExternalLLMInferenceEvidence",
    "LiveOpenAIRuntimeConnectorEvidence",
    "LiveRuntimeObservationArtifact",
    "LiveRuntimeUsageValidationEvidence",
    "LiveSemanticPressureValidationEvidence",
    "MockProvider",
    "MinimalGovernedExecutionPathResult",
    "MinimalRealRuntimeDemoEvidence",
    "OperatorInteractionLoopEvidence",
    "PREPARED",
    "ProviderInterface",
    "ProviderResponse",
    "ProductionIsolationEvidence",
    "ReadonlyDomainExperimentEvidence",
    "RealGovernedExecutionResilienceEvidence",
    "RealRuntimeActivationEvidence",
    "RETURNED",
    "RUNNING",
    "RuntimeEngine",
    "RuntimePackage",
    "RuntimeOperatorCLIEvidence",
    "RealOpenAIAPIInvocationEvidence",
    "SyntheticCognitionPressureArtifact",
    "WorkerLifecycle",
    "attach_external_llm_response",
    "activate_real_runtime",
    "authorize_governed_execution_contract",
    "classify_governance_failure",
    "certify_governance_resilience",
    "create_bounded_cognition_proposal",
    "create_governed_execution_contract",
    "create_governed_execution_session",
    "evaluate_governance_promotion",
    "execute_minimal_governed_path",
    "external_model_response_hash",
    "generate_ambiguous_contract",
    "generate_authority_drift_attempt",
    "generate_long_chain_entropy_sequence",
    "generate_provider_escalation_attempt",
    "generate_replay_corruption_attempt",
    "interpret_governed_execution_return",
    "invoke_live_external_llm_provider",
    "invoke_live_openai_runtime_connector",
    "invoke_real_openai_api",
    "normalize_real_llm_proposal_input",
    "observe_ambiguity_telemetry",
    "observe_cognition_drift",
    "observe_governance_pressure",
    "observe_replay_continuity",
    "reconstruct_authorization_lineage",
    "reconstruct_certification_lineage",
    "reconstruct_cognition_lineage",
    "reconstruct_cognition_review_lineage",
    "reconstruct_external_llm_proposal_lineage",
    "reconstruct_first_real_operator_usage_lineage",
    "reconstruct_contract_lineage",
    "reconstruct_failure_lineage",
    "reconstruct_governed_return_lineage",
    "reconstruct_live_external_llm_inference_lineage",
    "reconstruct_live_openai_runtime_lineage",
    "reconstruct_live_runtime_observation_lineage",
    "reconstruct_live_runtime_usage_validation_lineage",
    "reconstruct_live_semantic_pressure_lineage",
    "reconstruct_promotion_lineage",
    "reconstruct_real_llm_proposal_lineage",
    "reconstruct_real_openai_api_invocation_lineage",
    "reconstruct_real_runtime_activation_lineage",
    "reconstruct_minimal_governed_execution_lineage",
    "reconstruct_minimal_real_runtime_demo_lineage",
    "reconstruct_operator_interaction_loop_lineage",
    "reconstruct_production_isolation_lineage",
    "reconstruct_real_governed_execution_resilience_lineage",
    "reconstruct_readonly_domain_experiment_lineage",
    "reconstruct_routing_lineage",
    "reconstruct_runtime_operator_cli_lineage",
    "reconstruct_session_lineage",
    "reconstruct_simulation_lineage",
    "reconstruct_translation_lineage",
    "replay_hash",
    "route_authorized_contract",
    "review_translated_cognition_candidate",
    "run_real_governed_execution_resilience_suite",
    "run_minimal_real_runtime_demo",
    "run_governance_runtime_inspector_experiment",
    "run_first_real_operator_usage",
    "run_operator_interaction_loop",
    "run_runtime_operator_cli",
    "translate_bounded_proposal",
    "validate_production_isolation",
    "validate_live_semantic_pressure",
    "validate_live_runtime_usage",
    "validate_session_lineage_replay",
]
