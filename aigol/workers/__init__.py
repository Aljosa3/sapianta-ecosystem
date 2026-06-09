"""Governed worker attachments for AiGOL."""

from .domain_artifact_worker import (
    AUTHORIZED_SCOPE as DOMAIN_ARTIFACT_AUTHORIZED_SCOPE,
    DOMAIN_ARTIFACT_WORKER_ID,
    DOMAIN_ARTIFACT_WORKER_VERSION,
    DOMAIN_DEFINITION_ARTIFACT_V1,
    DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1,
    DOMAIN_METADATA_ARTIFACT_V1,
    DOMAIN_REGISTRATION_ARTIFACT_V1,
    OPERATION_AUTHOR_DOMAIN_ARTIFACTS,
    create_domain_artifact_request,
    execute_domain_artifact_request,
    reconstruct_domain_artifact_worker_replay,
    validate_domain_artifact_request,
)

__all__ = [
    "DOMAIN_ARTIFACT_AUTHORIZED_SCOPE",
    "DOMAIN_ARTIFACT_WORKER_ID",
    "DOMAIN_ARTIFACT_WORKER_VERSION",
    "DOMAIN_DEFINITION_ARTIFACT_V1",
    "DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1",
    "DOMAIN_METADATA_ARTIFACT_V1",
    "DOMAIN_REGISTRATION_ARTIFACT_V1",
    "OPERATION_AUTHOR_DOMAIN_ARTIFACTS",
    "create_domain_artifact_request",
    "execute_domain_artifact_request",
    "reconstruct_domain_artifact_worker_replay",
    "validate_domain_artifact_request",
]
