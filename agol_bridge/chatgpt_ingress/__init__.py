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

__all__ = [
    "ACCEPTED_AS_SEMANTIC_INPUT",
    "ACCEPTED_FOR_STRUCTURAL_IMPORT",
    "ARTIFACT_TYPE",
    "BOUNDARY_STATEMENT",
    "REJECTED",
    "SCHEMA_VERSION",
    "create_chatgpt_ingress_artifact",
    "derive_semantic_contract_candidate",
    "derive_semantic_proposal_candidate",
    "generate_governance_acceptance_report",
    "import_chatgpt_ingress_artifact",
    "replay_identity_for",
    "validate_chatgpt_ingress_artifact",
]
