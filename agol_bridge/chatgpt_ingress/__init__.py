"""Canonical non-authoritative ChatGPT ingress artifacts."""

from .chatgpt_ingress_artifact import (
    ARTIFACT_TYPE,
    BOUNDARY_STATEMENT,
    SCHEMA_VERSION,
    create_chatgpt_ingress_artifact,
    replay_identity_for,
)
from .chatgpt_ingress_validator import (
    ACCEPTED_AS_SEMANTIC_INPUT,
    REJECTED,
    validate_chatgpt_ingress_artifact,
)
from .ingress_import_validation import (
    ACCEPTED_FOR_STRUCTURAL_IMPORT,
    derive_semantic_contract_candidate,
    derive_semantic_proposal_candidate,
    generate_governance_acceptance_report,
    import_chatgpt_ingress_artifact,
)
from .ingress_acceptance_gate import (
    ACCEPTED_FOR_GOVERNED_PREVIEW,
    ALLOWED_GATE_STATUSES,
    REJECTED_BY_GOVERNANCE_GATE,
    evaluate_chatgpt_ingress_acceptance_gate,
    evaluate_import_acceptance_gate,
)

__all__ = [
    "ACCEPTED_AS_SEMANTIC_INPUT",
    "ACCEPTED_FOR_GOVERNED_PREVIEW",
    "ACCEPTED_FOR_STRUCTURAL_IMPORT",
    "ALLOWED_GATE_STATUSES",
    "ARTIFACT_TYPE",
    "BOUNDARY_STATEMENT",
    "REJECTED",
    "REJECTED_BY_GOVERNANCE_GATE",
    "SCHEMA_VERSION",
    "create_chatgpt_ingress_artifact",
    "derive_semantic_contract_candidate",
    "derive_semantic_proposal_candidate",
    "generate_governance_acceptance_report",
    "import_chatgpt_ingress_artifact",
    "evaluate_chatgpt_ingress_acceptance_gate",
    "evaluate_import_acceptance_gate",
    "replay_identity_for",
    "validate_chatgpt_ingress_artifact",
]
