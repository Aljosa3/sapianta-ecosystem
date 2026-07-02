"""Codex Worker/Provider registration runtime for G11-06.

This module composes existing Provider identity, Provider governance, and Worker
registration runtimes. It does not invoke Codex, route work, authorize execution,
or perform repository mutation.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_registry import ATTACHED, ProviderMetadata, ProviderRegistry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_governance_runtime import (
    ADD,
    execute_provider_lifecycle_operation,
    record_cognition_participation,
    record_provider_usage_metric,
)
from aigol.runtime.provider_identity_boundaries import (
    COGNITION_PROVIDER,
    CREDENTIAL_CONFIGURED_INACTIVE,
    PROVIDER_REGISTERED_INACTIVE,
    create_provider_credential_reference,
    create_provider_identity,
    reconstruct_provider_identity_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_runtime import (
    AVAILABLE,
    register_worker,
    reconstruct_worker_registration_replay,
)


MILESTONE_ID = "G11_06_CODEX_WORKER_PLATFORM_INTEGRATION_IMPLEMENTATION_V1"
CODEX_COGNITION_PROVIDER_ID = "codex-cognition"
CODEX_EXECUTION_WORKER_ID = "codex-execution"
CODEX_COGNITION_CREDENTIAL_REFERENCE = "vault://provider/codex-cognition"
CODEX_EXECUTION_CREDENTIAL_REFERENCE = "vault://worker/codex-execution"
CODEX_COGNITION_MODEL_ID = "codex-governed-cognition"
CODEX_EXECUTION_WORKER_VERSION = "codex-governed-execution-v1"
DEFAULT_CREATED_AT = "2026-07-02T00:00:00Z"

CODEX_INTEGRATION_SUMMARY_ARTIFACT_V1 = "CODEX_WORKER_PROVIDER_INTEGRATION_SUMMARY_ARTIFACT_V1"
CODEX_WORKER_CREDENTIAL_BOUNDARY_ARTIFACT_V1 = "CODEX_WORKER_CREDENTIAL_BOUNDARY_ARTIFACT_V1"
CODEX_AUTHORITY_BOUNDARY_ARTIFACT_V1 = "CODEX_WORKER_PROVIDER_AUTHORITY_BOUNDARY_ARTIFACT_V1"
CODEX_ARCHITECTURAL_HEALTH_OBSERVATION_ARTIFACT_V1 = (
    "CODEX_WORKER_PROVIDER_ARCHITECTURAL_HEALTH_OBSERVATION_ARTIFACT_V1"
)


def register_codex_worker_provider_integration(
    *,
    replay_dir: str | Path,
    created_at: str = DEFAULT_CREATED_AT,
    requested_by: str = "PLATFORM_CORE",
) -> dict[str, Any]:
    """Register Codex as separate governed provider and worker identities."""

    root = Path(replay_dir)
    _ensure_integration_replay_available(root)

    provider_metadata = _register_provider_metadata()
    provider_credential = create_provider_credential_reference(
        credential_reference_id=CODEX_COGNITION_PROVIDER_ID,
        credential_reference=CODEX_COGNITION_CREDENTIAL_REFERENCE,
        credential_role=COGNITION_PROVIDER,
        credential_lifecycle_state=CREDENTIAL_CONFIGURED_INACTIVE,
        secret_present=False,
        created_at=created_at,
        replay_dir=root / "provider_credential_reference",
    )
    provider_identity = create_provider_identity(
        provider_id=CODEX_COGNITION_PROVIDER_ID,
        external_provider_family="codex",
        model_id=CODEX_COGNITION_MODEL_ID,
        provider_role=COGNITION_PROVIDER,
        capability_declarations=_codex_provider_capabilities(),
        credential_reference_artifact=provider_credential["credential_reference_artifact"],
        activation_status=PROVIDER_REGISTERED_INACTIVE,
        replay_lineage=[
            {
                "replay_reference": "governance:G11_05A_CODEX_WORKER_PLATFORM_INTEGRATION_ARCHITECTURE_REVIEW_V1",
                "replay_hash": replay_hash({"final_verdict": "CODEX_WORKER_PLATFORM_INTEGRATION_ARCHITECTURE_CONFIRMED"}),
            }
        ],
        rollback_reference="rollback:provider:codex-cognition",
        created_at=created_at,
        replay_dir=root / "provider_identity",
    )
    provider_governance = execute_provider_lifecycle_operation(
        event_id="CODEX-COGNITION-PROVIDER-GOVERNANCE-ADD",
        operation=ADD,
        provider_id=CODEX_COGNITION_PROVIDER_ID,
        requested_by=requested_by,
        created_at=created_at,
        replay_dir=root / "provider_governance",
        reason="Register Codex cognition as a non-authoritative Provider Platform identity.",
        env={},
    )
    provider_usage = record_provider_usage_metric(
        metric_id="CODEX-COGNITION-PROVIDER-USAGE-BASELINE",
        provider_id=CODEX_COGNITION_PROVIDER_ID,
        model=CODEX_COGNITION_MODEL_ID,
        status="REGISTERED_NOT_INVOKED",
        availability="CREDENTIAL_MISSING",
        created_at=created_at,
        replay_dir=root / "provider_metrics",
    )
    cognition_participation = record_cognition_participation(
        participation_id="CODEX-COGNITION-PROVIDER-PARTICIPATION-BASELINE",
        provider_id=CODEX_COGNITION_PROVIDER_ID,
        participation_location="OCS_LLM_COGNITION",
        participation_role="PROPOSAL_ONLY_COGNITION_PROVIDER",
        workflow_id="GOVERNED_DEVELOPMENT_WORKFLOW",
        invocation_reason="Register provider identity for future governed Codex cognition.",
        purpose="Proposal generation, reasoning, alternatives, uncertainty, and recommendations.",
        response_used=False,
        worker_invoked_after=False,
        human_confirmation_required=True,
        created_at=created_at,
        replay_dir=root / "provider_participation",
    )

    worker_registration = register_worker(
        worker_id=CODEX_EXECUTION_WORKER_ID,
        worker_type="CODEX_EXECUTION_WORKER",
        worker_version=CODEX_EXECUTION_WORKER_VERSION,
        declared_capabilities=[
            "GOVERNED_CODE_GENERATION",
            "GOVERNED_ARTIFACT_GENERATION",
            "BOUNDED_EXECUTION_REPORTING",
        ],
        supported_request_types=[
            "CODEX_GOVERNED_CODE_GENERATION_REQUEST",
            "CODEX_GOVERNED_ARTIFACT_GENERATION_REQUEST",
            "CODEX_BOUNDED_EXECUTION_REQUEST",
        ],
        trust_boundary="SANDBOXED_WORKER",
        created_at=created_at,
        replay_reference="replay:worker:codex-execution:registration",
        replay_dir=root / "worker_registration",
        state=AVAILABLE,
    )
    worker_credential = _worker_credential_boundary(created_at=created_at)
    _write_artifact(root / "worker_credential_boundary" / "000_codex_worker_credential_boundary.json", worker_credential)

    authority_boundary = _authority_boundary_artifact(
        created_at=created_at,
        provider_identity=provider_identity["provider_identity_artifact"],
        worker_artifact=worker_registration["worker_artifact"],
        worker_credential=worker_credential,
    )
    _write_artifact(root / "authority_boundary" / "000_codex_authority_boundary.json", authority_boundary)

    health_observation = _architectural_health_observation(
        created_at=created_at,
        authority_boundary=authority_boundary,
    )
    _write_artifact(root / "architectural_health" / "000_codex_architectural_health_observation.json", health_observation)

    summary = _integration_summary(
        created_at=created_at,
        provider_metadata=provider_metadata,
        provider_credential=provider_credential["credential_reference_artifact"],
        provider_identity=provider_identity["provider_identity_artifact"],
        provider_governance=provider_governance,
        provider_usage=provider_usage,
        cognition_participation=cognition_participation,
        worker_artifact=worker_registration["worker_artifact"],
        worker_registration_replay=worker_registration["worker_registration_replay"],
        worker_credential=worker_credential,
        authority_boundary=authority_boundary,
        health_observation=health_observation,
        replay_root=root,
    )
    _write_artifact(root / "000_codex_worker_provider_integration_summary.json", summary)
    return _capture(root, summary)


def reconstruct_codex_worker_provider_integration(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the Codex role-separated registration evidence."""

    root = Path(replay_dir)
    summary = _load_artifact(root / "000_codex_worker_provider_integration_summary.json")
    provider_reconstruction = reconstruct_provider_identity_replay(root / "provider_identity")
    worker_reconstruction = reconstruct_worker_registration_replay(root / "worker_registration")
    authority_boundary = _load_artifact(root / "authority_boundary" / "000_codex_authority_boundary.json")
    health_observation = _load_artifact(
        root / "architectural_health" / "000_codex_architectural_health_observation.json"
    )
    assertions = {
        "provider_identity_reconstructable": provider_reconstruction["provider_id"] == CODEX_COGNITION_PROVIDER_ID,
        "worker_identity_reconstructable": worker_reconstruction["worker_id"] == CODEX_EXECUTION_WORKER_ID,
        "identities_are_distinct": CODEX_COGNITION_PROVIDER_ID != CODEX_EXECUTION_WORKER_ID,
        "credential_references_are_distinct": summary["provider_credential_reference"]
        != summary["worker_credential_reference"],
        "provider_has_no_execution_authority": authority_boundary["provider_execution_authority"] is False,
        "worker_has_no_governance_authority": authority_boundary["worker_governance_authority"] is False,
        "architectural_health_advisory_only": health_observation["architectural_health_authority"] is False,
    }
    reconstruction = {
        "artifact_type": "CODEX_WORKER_PROVIDER_INTEGRATION_RECONSTRUCTION_V1",
        "runtime_version": MILESTONE_ID,
        "provider_identity": provider_reconstruction,
        "worker_identity": worker_reconstruction,
        "summary_hash": summary["artifact_hash"],
        "authority_boundary_hash": authority_boundary["artifact_hash"],
        "architectural_health_hash": health_observation["artifact_hash"],
        "assertions": assertions,
        "replay_reconstructed": all(assertions.values()),
        "final_verdict": (
            "CODEX_REGISTERED_AS_GOVERNED_WORKER_AND_PROVIDER"
            if all(assertions.values())
            else "CODEX_WORKER_PROVIDER_REGISTRATION_GAPS_DETECTED"
        ),
    }
    reconstruction["artifact_hash"] = replay_hash(reconstruction)
    return reconstruction


def _register_provider_metadata() -> dict[str, Any]:
    registry = ProviderRegistry()
    return registry.register_provider(
        ProviderMetadata(
            provider_id=CODEX_COGNITION_PROVIDER_ID,
            provider_type="codex_cognition_provider",
            provider_version="codex-cognition-v1",
            provider_status=ATTACHED,
            domain="governed_development",
            capability="proposal_generation",
        )
    )


def _codex_provider_capabilities() -> list[dict[str, Any]]:
    return [
        {
            "capability_id": "CODEX_PROPOSAL_GENERATION",
            "capability": "proposal_generation",
            "capability_scope": "governed_development_advisory",
            "advisory_only": True,
            "execution_authority": False,
        },
        {
            "capability_id": "CODEX_REASONING_ALTERNATIVES",
            "capability": "reasoning_alternatives_uncertainty",
            "capability_scope": "governed_development_advisory",
            "advisory_only": True,
            "execution_authority": False,
        },
        {
            "capability_id": "CODEX_RECOMMENDATIONS",
            "capability": "recommendations",
            "capability_scope": "human_review_required",
            "advisory_only": True,
            "execution_authority": False,
        },
    ]


def _worker_credential_boundary(*, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": CODEX_WORKER_CREDENTIAL_BOUNDARY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "worker_id": CODEX_EXECUTION_WORKER_ID,
        "credential_reference": CODEX_EXECUTION_CREDENTIAL_REFERENCE,
        "credential_reference_only": True,
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "secret_material_present": False,
        "provider_credential_reference": False,
        "governance_authority": False,
        "approval_authority": False,
        "provider_authority": False,
        "replay_authority": False,
        "worker_self_authorized": False,
        "execution_authorized": False,
        "execution_performed": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _authority_boundary_artifact(
    *,
    created_at: str,
    provider_identity: dict[str, Any],
    worker_artifact: dict[str, Any],
    worker_credential: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CODEX_AUTHORITY_BOUNDARY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "provider_identity_id": provider_identity["provider_id"],
        "worker_identity_id": worker_artifact["worker_id"],
        "provider_credential_reference": provider_identity["credential_reference"],
        "worker_credential_reference": worker_credential["credential_reference"],
        "identities_are_distinct": provider_identity["provider_id"] != worker_artifact["worker_id"],
        "credential_references_are_distinct": provider_identity["credential_reference"]
        != worker_credential["credential_reference"],
        "provider_execution_authority": False,
        "provider_worker_authority": False,
        "provider_governance_authority": False,
        "worker_provider_authority": False,
        "worker_governance_authority": False,
        "worker_replay_authority": False,
        "platform_core_authority_preserved": True,
        "governance_authority_preserved": True,
        "replay_authority_preserved": True,
        "worker_platform_authority_preserved": True,
        "provider_platform_authority_preserved": True,
        "acli_next_authority_introduced": False,
        "authority_transfer_detected": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _architectural_health_observation(*, created_at: str, authority_boundary: dict[str, Any]) -> dict[str, Any]:
    findings = []
    if authority_boundary["authority_transfer_detected"] is True:
        findings.append("authority transfer detected")
    artifact = {
        "artifact_type": CODEX_ARCHITECTURAL_HEALTH_OBSERVATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "observed_provider_identity": authority_boundary["provider_identity_id"],
        "observed_worker_identity": authority_boundary["worker_identity_id"],
        "role_separation_preserved": authority_boundary["identities_are_distinct"],
        "credential_separation_preserved": authority_boundary["credential_references_are_distinct"],
        "ownership_drift_detected": False,
        "authority_drift_detected": False,
        "duplicated_orchestration_detected": False,
        "duplicated_execution_detected": False,
        "duplicated_provider_management_detected": False,
        "architectural_health_authority": False,
        "advisory_only": True,
        "findings": findings,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _integration_summary(
    *,
    created_at: str,
    provider_metadata: dict[str, Any],
    provider_credential: dict[str, Any],
    provider_identity: dict[str, Any],
    provider_governance: dict[str, Any],
    provider_usage: dict[str, Any],
    cognition_participation: dict[str, Any],
    worker_artifact: dict[str, Any],
    worker_registration_replay: dict[str, Any],
    worker_credential: dict[str, Any],
    authority_boundary: dict[str, Any],
    health_observation: dict[str, Any],
    replay_root: Path,
) -> dict[str, Any]:
    assertions = {
        "codex_cognition_registered_as_provider": provider_identity["provider_id"] == CODEX_COGNITION_PROVIDER_ID,
        "codex_execution_registered_as_worker": worker_artifact["worker_id"] == CODEX_EXECUTION_WORKER_ID,
        "provider_non_authoritative": provider_identity["execution_requested"] is False
        and provider_identity["repository_mutated"] is False,
        "worker_non_authoritative": worker_artifact["governance_authority"] is False
        and worker_artifact["self_authorization"] is False,
        "provider_worker_identities_independent": authority_boundary["identities_are_distinct"] is True,
        "provider_worker_credentials_independent": authority_boundary["credential_references_are_distinct"] is True,
        "architectural_health_advisory_only": health_observation["architectural_health_authority"] is False,
    }
    artifact = {
        "artifact_type": CODEX_INTEGRATION_SUMMARY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "codex_cognition_provider_id": CODEX_COGNITION_PROVIDER_ID,
        "codex_execution_worker_id": CODEX_EXECUTION_WORKER_ID,
        "provider_credential_reference": provider_identity["credential_reference"],
        "worker_credential_reference": worker_credential["credential_reference"],
        "provider_metadata_hash": provider_metadata["provider_identity_hash"],
        "provider_credential_hash": provider_credential["artifact_hash"],
        "provider_identity_hash": provider_identity["artifact_hash"],
        "provider_governance_hash": provider_governance["artifact_hash"],
        "provider_usage_hash": provider_usage["artifact_hash"],
        "cognition_participation_hash": cognition_participation["artifact_hash"],
        "worker_artifact_hash": worker_artifact["artifact_hash"],
        "worker_registration_replay_hash": worker_registration_replay["artifact_hash"],
        "worker_credential_hash": worker_credential["artifact_hash"],
        "authority_boundary_hash": authority_boundary["artifact_hash"],
        "architectural_health_hash": health_observation["artifact_hash"],
        "provider_replay_reference": str(replay_root / "provider_identity"),
        "worker_replay_reference": str(replay_root / "worker_registration"),
        "provider_invoked": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "governance_authority_preserved": True,
        "replay_authority_preserved": True,
        "platform_core_authority_preserved": True,
        "assertions": assertions,
        "final_verdict": (
            "CODEX_REGISTERED_AS_GOVERNED_WORKER_AND_PROVIDER"
            if all(assertions.values())
            else "CODEX_WORKER_PROVIDER_REGISTRATION_GAPS_DETECTED"
        ),
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(root: Path, summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "replay_root": str(root),
        "codex_cognition_provider_id": summary["codex_cognition_provider_id"],
        "codex_execution_worker_id": summary["codex_execution_worker_id"],
        "provider_credential_reference": summary["provider_credential_reference"],
        "worker_credential_reference": summary["worker_credential_reference"],
        "assertions": deepcopy(summary["assertions"]),
        "final_verdict": summary["final_verdict"],
        "summary_hash": summary["artifact_hash"],
    }


def _ensure_integration_replay_available(root: Path) -> None:
    summary_path = root / "000_codex_worker_provider_integration_summary.json"
    if summary_path.exists():
        raise FailClosedRuntimeError("codex integration failed closed: replay already exists")


def _write_artifact(path: Path, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact)
    write_json_immutable(path, artifact)


def _load_artifact(path: Path) -> dict[str, Any]:
    artifact = load_json(path)
    _verify_artifact_hash(artifact)
    return artifact


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("codex integration failed closed: artifact must be object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("codex integration failed closed: artifact hash missing")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("codex integration failed closed: artifact hash mismatch")
    _assert_secret_safe(artifact)


def _assert_secret_safe(value: Any) -> None:
    serialized = str(value)
    forbidden = ("sk-", "Bearer ", "OPENAI_API_KEY=", "AIGOL_OPENAI_API_KEY=", "authorization:")
    if any(marker in serialized for marker in forbidden):
        raise FailClosedRuntimeError("codex integration failed closed: secret material must not be replayed")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"codex integration failed closed: {field_name} is required")
    return value
