"""Import-only structural validation for ChatGPT ingress artifacts.

This module stops at semantic proposal/contract candidates and a governance
acceptance report. It performs no Codex dispatch, provider invocation,
orchestration, autonomous continuation, durable replay write, or runtime
execution.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from .chatgpt_ingress_validator import validate_chatgpt_ingress_artifact

ACCEPTED_FOR_STRUCTURAL_IMPORT = "ACCEPTED_FOR_STRUCTURAL_IMPORT"
REJECTED = "REJECTED"


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_without(value: dict, field: str) -> str:
    value_copy = _canonical_copy(value)
    value_copy.pop(field, None)
    return canonical_hash(value_copy)


def _lineage_from_artifact(artifact: dict) -> dict:
    hashes = artifact.get("hashes", {})
    return {
        "artifact_type": artifact.get("artifact_type", "UNKNOWN"),
        "schema_version": artifact.get("schema_version", "UNKNOWN"),
        "session_id": artifact.get("session_id", "UNKNOWN"),
        "replay_identity": artifact.get("replay_identity", "UNKNOWN"),
        "ingress_artifact_hash": hashes.get("artifact_hash", "UNKNOWN"),
        "human_request_hash": hashes.get("human_request_hash", "UNKNOWN"),
        "semantic_output_hash": hashes.get("semantic_output_hash", "UNKNOWN"),
        "provenance": _canonical_copy(artifact.get("provenance", {})),
    }


def derive_semantic_proposal_candidate(artifact: dict) -> dict:
    """Derive a structural semantic proposal candidate from ingress input."""

    lineage = _lineage_from_artifact(artifact)
    candidate = {
        "candidate_type": "CHATGPT_INGRESS_SEMANTIC_PROPOSAL_CANDIDATE_V1",
        "proposal_candidate_only": True,
        "classification": "STRUCTURAL_ONLY",
        "normalized_intent": artifact.get("normalized_intent", ""),
        "expected_artifacts": _canonical_copy(artifact.get("expected_artifacts", [])),
        "constraints": _canonical_copy(artifact.get("constraints", [])),
        "forbidden_operations": _canonical_copy(artifact.get("forbidden_operations", [])),
        "provenance_references": lineage,
        "replay_identity": artifact.get("replay_identity", "UNKNOWN"),
        "hashes": {
            "ingress_artifact_hash": lineage["ingress_artifact_hash"],
            "human_request_hash": lineage["human_request_hash"],
            "semantic_output_hash": lineage["semantic_output_hash"],
        },
        "execution_authority": False,
        "governance_authority": False,
        "codex_dispatch_allowed": False,
        "autonomous_continuation_allowed": False,
    }
    candidate["proposal_candidate_hash"] = _hash_without(candidate, "proposal_candidate_hash")
    return candidate


def derive_semantic_contract_candidate(*, artifact: dict, proposal_candidate: dict) -> dict:
    """Derive a structural semantic contract candidate.

    This is not a live semantic contract and does not verify semantic
    correctness.
    """

    candidate = {
        "candidate_type": "CHATGPT_INGRESS_SEMANTIC_CONTRACT_CANDIDATE_V1",
        "contract_candidate_only": True,
        "classification": "STRUCTURAL_ONLY",
        "source_proposal_candidate_hash": proposal_candidate.get("proposal_candidate_hash", "UNKNOWN"),
        "normalized_intent": proposal_candidate.get("normalized_intent", ""),
        "human_request": artifact.get("human_request", ""),
        "chatgpt_semantic_output": artifact.get("chatgpt_semantic_output", ""),
        "expected_artifacts": _canonical_copy(proposal_candidate.get("expected_artifacts", [])),
        "constraints": _canonical_copy(proposal_candidate.get("constraints", [])),
        "forbidden_operations": _canonical_copy(proposal_candidate.get("forbidden_operations", [])),
        "provenance_references": _canonical_copy(proposal_candidate.get("provenance_references", {})),
        "replay_identity": artifact.get("replay_identity", "UNKNOWN"),
        "hashes": _canonical_copy(proposal_candidate.get("hashes", {})),
        "semantic_correctness_verified": False,
        "governance_approved": False,
        "execution_authorized": False,
        "provider_dispatch_authorized": False,
    }
    candidate["contract_candidate_hash"] = _hash_without(candidate, "contract_candidate_hash")
    return candidate


def generate_governance_acceptance_report(
    *,
    artifact: dict,
    ingress_validation: dict,
    proposal_candidate: dict | None = None,
    contract_candidate: dict | None = None,
) -> dict:
    """Generate the import-only governance acceptance/rejection report."""

    valid = ingress_validation.get("valid") is True
    lineage = _lineage_from_artifact(artifact) if isinstance(artifact, dict) else {}
    report = {
        "report_type": "CHATGPT_INGRESS_IMPORT_VALIDATION_REPORT_V1",
        "status": ACCEPTED_FOR_STRUCTURAL_IMPORT if valid else REJECTED,
        "import_only": True,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "autonomous_continuation_performed": False,
        "semantic_correctness_verified": False,
        "ingress_validation": _canonical_copy(ingress_validation),
        "replay_identity": lineage.get("replay_identity", "UNKNOWN"),
        "preserved_hashes": {
            "ingress_artifact_hash": lineage.get("ingress_artifact_hash", "UNKNOWN"),
            "human_request_hash": lineage.get("human_request_hash", "UNKNOWN"),
            "semantic_output_hash": lineage.get("semantic_output_hash", "UNKNOWN"),
            "proposal_candidate_hash": (proposal_candidate or {}).get("proposal_candidate_hash", "NONE"),
            "contract_candidate_hash": (contract_candidate or {}).get("contract_candidate_hash", "NONE"),
        },
        "provenance_lineage": lineage.get("provenance", {}),
        "structural_continuity": {
            "ingress_artifact_validated": valid,
            "proposal_candidate_created": proposal_candidate is not None,
            "contract_candidate_created": contract_candidate is not None,
            "downstream_runtime_connected": False,
            "provider_invoked": False,
            "governance_mutated": False,
        },
        "authority_boundary": {
            "chatgpt_authority": False,
            "execution_authority": False,
            "governance_authority": False,
            "approval_authority": False,
            "provider_dispatch_authority": False,
            "autonomous_continuation_authority": False,
        },
    }
    report["governance_report_hash"] = _hash_without(report, "governance_report_hash")
    return report


def import_chatgpt_ingress_artifact(artifact: Any) -> dict:
    """Validate and structurally import an ingress artifact, then stop."""

    ingress_validation = validate_chatgpt_ingress_artifact(artifact)
    if ingress_validation.get("valid") is not True:
        return {
            "status": REJECTED,
            "ingress_validation": ingress_validation,
            "semantic_proposal_candidate": {},
            "semantic_contract_candidate": {},
            "governance_acceptance_report": generate_governance_acceptance_report(
                artifact=artifact if isinstance(artifact, dict) else {},
                ingress_validation=ingress_validation,
            ),
            "import_only": True,
            "execution_performed": False,
            "codex_dispatch_performed": False,
            "autonomous_continuation_performed": False,
            "semantic_correctness_verified": False,
        }

    safe_artifact = _canonical_copy(artifact)
    proposal_candidate = derive_semantic_proposal_candidate(safe_artifact)
    contract_candidate = derive_semantic_contract_candidate(
        artifact=safe_artifact,
        proposal_candidate=proposal_candidate,
    )
    report = generate_governance_acceptance_report(
        artifact=safe_artifact,
        ingress_validation=ingress_validation,
        proposal_candidate=proposal_candidate,
        contract_candidate=contract_candidate,
    )
    return {
        "status": ACCEPTED_FOR_STRUCTURAL_IMPORT,
        "ingress_validation": ingress_validation,
        "semantic_proposal_candidate": proposal_candidate,
        "semantic_contract_candidate": contract_candidate,
        "governance_acceptance_report": report,
        "import_only": True,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "autonomous_continuation_performed": False,
        "semantic_correctness_verified": False,
    }


__all__ = [
    "ACCEPTED_FOR_STRUCTURAL_IMPORT",
    "REJECTED",
    "derive_semantic_contract_candidate",
    "derive_semantic_proposal_candidate",
    "generate_governance_acceptance_report",
    "import_chatgpt_ingress_artifact",
]
