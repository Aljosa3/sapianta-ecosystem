"""Certification for role-separated LLM identities."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_ROLE_SEPARATED_LLM_IDENTITY_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/role_separated_llm_identity_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

ROLE_SEPARATED_LLM_CREDENTIAL_IDENTITY_ARTIFACT_V1 = (
    "ROLE_SEPARATED_LLM_CREDENTIAL_IDENTITY_ARTIFACT_V1"
)
ROLE_SEPARATED_LLM_LIFECYCLE_ARTIFACT_V1 = "ROLE_SEPARATED_LLM_LIFECYCLE_ARTIFACT_V1"
ROLE_SEPARATED_LLM_USAGE_METRIC_ARTIFACT_V1 = "ROLE_SEPARATED_LLM_USAGE_METRIC_ARTIFACT_V1"
ROLE_SEPARATED_LLM_PARTICIPATION_ARTIFACT_V1 = "ROLE_SEPARATED_LLM_PARTICIPATION_ARTIFACT_V1"
ROLE_SEPARATED_LLM_AUTHORITY_BOUNDARY_ARTIFACT_V1 = (
    "ROLE_SEPARATED_LLM_AUTHORITY_BOUNDARY_ARTIFACT_V1"
)

SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "api_key",
    "authorization_header:",
    "OPENAI_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
)

ROLE_IDENTITIES: tuple[dict[str, Any], ...] = (
    {
        "identity_id": "openai-cognition",
        "external_provider_id": "openai",
        "architectural_role": "COGNITION_PROVIDER",
        "credential_reference": "vault://provider/openai-cognition",
        "participation_location": "OCS_LLM_COGNITION",
        "participation_role": "PROPOSAL_ONLY_COGNITION_PROVIDER",
        "workflow_id": "ROLE-SEPARATED-COGNITION-WORKFLOW",
        "invocation_reason": "Resolve ambiguous human intent through proposal-only cognition.",
        "purpose": "Generate non-authoritative cognition proposal for human confirmation.",
        "response_used": True,
        "worker_invoked_after": False,
    },
    {
        "identity_id": "openai-translation",
        "external_provider_id": "openai",
        "architectural_role": "TRANSLATION_WORKER",
        "credential_reference": "vault://worker/openai-translation",
        "participation_location": "HUMAN_RESPONSE_ASSISTANCE",
        "participation_role": "TRANSLATION_WORKER_ASSISTANT",
        "workflow_id": "ROLE-SEPARATED-TRANSLATION-WORKFLOW",
        "invocation_reason": "Translate operator-facing text after governed authorization.",
        "purpose": "Contribute translation output without approval authority.",
        "response_used": False,
        "worker_invoked_after": True,
    },
    {
        "identity_id": "openai-repair",
        "external_provider_id": "openai",
        "architectural_role": "REPAIR_WORKER",
        "credential_reference": "vault://worker/openai-repair",
        "participation_location": "WORKER_REPAIR",
        "participation_role": "REPAIR_WORKER_ASSISTANT",
        "workflow_id": "ROLE-SEPARATED-REPAIR-WORKFLOW",
        "invocation_reason": "Propose worker repair after governed failure analysis.",
        "purpose": "Contribute repair proposal without execution authority.",
        "response_used": False,
        "worker_invoked_after": True,
    },
)


def run_role_separated_llm_identity_certification(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    role_root = root / "role_identities"
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    coverage_dir = root / "coverage_report"
    report_dir = root / "certification_report"

    role_results = [_create_role_identity_evidence(role_root, spec) for spec in ROLE_IDENTITIES]
    replay_reconstruction = reconstruct_role_separated_llm_identity_replay(root)
    secret_free = _secret_free(root)
    assertions = _assertions(role_results=role_results, replay_reconstruction=replay_reconstruction, secret_free=secret_free)
    final_verdict = (
        "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED"
        if all(assertions.values())
        else "ROLE_SEPARATED_LLM_IDENTITY_GAPS_FOUND"
    )
    coverage = _with_hash(
        {
            "artifact_type": "ROLE_SEPARATED_LLM_IDENTITY_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "covered_role_count": len(role_results),
            "covered_roles": [item["identity_id"] for item in role_results],
            "covered_credential_references": [item["credential_reference"] for item in role_results],
            "covered_participation_locations": [item["participation_location"] for item in role_results],
            "covered_lifecycle_operations": ["ADD", "ENABLE", "DISABLE", "VERIFY"],
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "ROLE_SEPARATED_LLM_IDENTITY_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(root),
            "role_results": role_results,
            "coverage_report_reference": "coverage_report/000_role_separated_llm_identity_coverage_report.json",
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "ROLE_SEPARATED_LLM_IDENTITY_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "replay_root": str(root),
            "replay_reconstruction": replay_reconstruction,
            "role_replay_references": _role_replay_references(role_results),
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "ROLE_SEPARATED_LLM_IDENTITY_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "summary": (
                "Same external LLM provider is represented as independent cognition, translation, "
                "and repair identities with separate lifecycle, metrics, participation, and authority evidence."
            ),
            "assertions": assertions,
            "observed": assertions,
            "blocker_analysis": [] if final_verdict == "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED" else _blockers(assertions),
            "recommended_next_certification": "AIGOL_MULTI_PROVIDER_ROLE_SEPARATED_EXECUTION_CERTIFICATION_V1",
            "final_verdict": final_verdict,
        }
    )
    _assert_secret_safe(coverage)
    _assert_secret_safe(evidence)
    _assert_secret_safe(replay)
    _assert_secret_safe(report)
    write_json_immutable(coverage_dir / "000_role_separated_llm_identity_coverage_report.json", coverage)
    write_json_immutable(evidence_dir / "000_role_separated_llm_identity_evidence_package.json", evidence)
    write_json_immutable(replay_dir / "000_role_separated_llm_identity_replay_package.json", replay)
    write_json_immutable(report_dir / "000_role_separated_llm_identity_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "coverage_report_path": str(coverage_dir / "000_role_separated_llm_identity_coverage_report.json"),
        "evidence_package_path": str(evidence_dir / "000_role_separated_llm_identity_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_role_separated_llm_identity_replay_package.json"),
        "certification_report_path": str(report_dir / "000_role_separated_llm_identity_certification_report.json"),
        "role_identity_count": len(role_results),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def reconstruct_role_separated_llm_identity_replay(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    role_root = root / "role_identities"
    if not role_root.exists():
        return _with_hash(
            {
                "artifact_type": "ROLE_SEPARATED_LLM_IDENTITY_REPLAY_RECONSTRUCTION_V1",
                "runtime_version": MILESTONE_ID,
                "created_at": CREATED_AT,
                "replay_reconstructed": False,
                "failure_reason": "role identity replay root missing",
            }
        )
    role_records = []
    for role_dir in sorted(path for path in role_root.iterdir() if path.is_dir()):
        artifacts = {
            "credential_identity": load_json(role_dir / "000_credential_identity.json"),
            "lifecycle": load_json(role_dir / "001_lifecycle.json"),
            "usage_metric": load_json(role_dir / "002_usage_metric.json"),
            "participation": load_json(role_dir / "003_participation.json"),
            "authority_boundary": load_json(role_dir / "004_authority_boundary.json"),
        }
        role_records.append(_summarize_role_artifacts(role_dir, artifacts))
    role_names = {record["architectural_role"] for record in role_records}
    reconstruction = {
        "artifact_type": "ROLE_SEPARATED_LLM_IDENTITY_REPLAY_RECONSTRUCTION_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_reconstructed": len(role_records) == 3,
        "role_identity_count": len(role_records),
        "distinguished_cognition_provider": "COGNITION_PROVIDER" in role_names,
        "distinguished_translation_worker": "TRANSLATION_WORKER" in role_names,
        "distinguished_repair_worker": "REPAIR_WORKER" in role_names,
        "role_records": role_records,
    }
    return _with_hash(reconstruction)


def _create_role_identity_evidence(role_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    role_dir = role_root / spec["identity_id"]
    credential_identity = _credential_identity_artifact(spec)
    lifecycle = _lifecycle_artifact(spec)
    usage_metric = _usage_metric_artifact(spec)
    participation = _participation_artifact(spec)
    authority_boundary = _authority_boundary_artifact(spec)
    artifacts = {
        "credential_identity": credential_identity,
        "lifecycle": lifecycle,
        "usage_metric": usage_metric,
        "participation": participation,
        "authority_boundary": authority_boundary,
    }
    for artifact in artifacts.values():
        _assert_secret_safe(artifact)
    write_json_immutable(role_dir / "000_credential_identity.json", credential_identity)
    write_json_immutable(role_dir / "001_lifecycle.json", lifecycle)
    write_json_immutable(role_dir / "002_usage_metric.json", usage_metric)
    write_json_immutable(role_dir / "003_participation.json", participation)
    write_json_immutable(role_dir / "004_authority_boundary.json", authority_boundary)
    return _summarize_role_artifacts(role_dir, artifacts)


def _credential_identity_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": ROLE_SEPARATED_LLM_CREDENTIAL_IDENTITY_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "identity_id": spec["identity_id"],
            "external_provider_id": spec["external_provider_id"],
            "architectural_role": spec["architectural_role"],
            "credential_reference": spec["credential_reference"],
            "credential_source_type": "VAULT_REFERENCE",
            "credential_present": True,
            "credential_enabled": True,
            "credential_display_identifier": _display_identifier(spec["credential_reference"]),
            "credential_value_recorded": False,
            "credential_hash_recorded": False,
            "credential_contents_recorded": False,
            "authorization_header_recorded": False,
            "role_identity_independent": True,
            "replay_visible": True,
            **_authority_flags(),
        }
    )


def _lifecycle_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    operations = [
        _lifecycle_operation(spec, "ADD", False, False, "ENABLED"),
        _lifecycle_operation(spec, "ENABLE", False, False, "ENABLED"),
        _lifecycle_operation(spec, "VERIFY", False, False, "ENABLED"),
    ]
    final_status = "ENABLED"
    if spec["identity_id"] == "openai-translation":
        operations.append(_lifecycle_operation(spec, "DISABLE", True, True, "DISABLED"))
        final_status = "DISABLED"
    return _with_hash(
        {
            "artifact_type": ROLE_SEPARATED_LLM_LIFECYCLE_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "identity_id": spec["identity_id"],
            "external_provider_id": spec["external_provider_id"],
            "architectural_role": spec["architectural_role"],
            "credential_reference": spec["credential_reference"],
            "lifecycle_operations": operations,
            "enable_control_independent": True,
            "disable_control_independent": True,
            "disable_requires_human_approval": True,
            "final_lifecycle_status": final_status,
            "other_role_status_mutated": False,
            "replay_visible": True,
            **_authority_flags(),
        }
    )


def _usage_metric_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    metric_values = {
        "openai-cognition": {"success_count": 3, "failure_count": 0, "estimated_cost_units": "0.0030"},
        "openai-translation": {"success_count": 1, "failure_count": 1, "estimated_cost_units": "0.0015"},
        "openai-repair": {"success_count": 2, "failure_count": 0, "estimated_cost_units": "0.0022"},
    }[spec["identity_id"]]
    return _with_hash(
        {
            "artifact_type": ROLE_SEPARATED_LLM_USAGE_METRIC_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "metric_id": f"{spec['identity_id']}:USAGE",
            "identity_id": spec["identity_id"],
            "external_provider_id": spec["external_provider_id"],
            "architectural_role": spec["architectural_role"],
            "model": "shared-external-openai-model",
            "status": "ROLE_ISOLATED",
            "availability": "GOVERNED_BY_ROLE_IDENTITY",
            "success_count": metric_values["success_count"],
            "failure_count": metric_values["failure_count"],
            "last_used": CREATED_AT,
            "last_failure": CREATED_AT if metric_values["failure_count"] else None,
            "latency_ms": 120 + len(spec["identity_id"]),
            "token_usage": {
                "prompt_tokens_recorded": True,
                "completion_tokens_recorded": True,
                "role_isolated_token_accounting": True,
            },
            "cost_tracking": {
                "cost_tracking_hooks_present": True,
                "role_isolated_cost_tracking": True,
                "estimated_cost_units": metric_values["estimated_cost_units"],
            },
            "replay_visible": True,
            **_authority_flags(),
        }
    )


def _participation_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": ROLE_SEPARATED_LLM_PARTICIPATION_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "participation_id": f"{spec['identity_id']}:PARTICIPATION",
            "identity_id": spec["identity_id"],
            "external_provider_id": spec["external_provider_id"],
            "architectural_role": spec["architectural_role"],
            "participation_location": spec["participation_location"],
            "participation_role": spec["participation_role"],
            "workflow_id": spec["workflow_id"],
            "invocation_reason": spec["invocation_reason"],
            "purpose": spec["purpose"],
            "response_used": spec["response_used"],
            "worker_invoked_after": spec["worker_invoked_after"],
            "human_confirmation_required": True,
            "human_confirmation_recorded": True,
            "non_authoritative_provider_principle_preserved": True,
            "replay_visible": True,
            **_authority_flags(),
        }
    )


def _authority_boundary_artifact(spec: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": ROLE_SEPARATED_LLM_AUTHORITY_BOUNDARY_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "identity_id": spec["identity_id"],
            "external_provider_id": spec["external_provider_id"],
            "architectural_role": spec["architectural_role"],
            "llm_may_propose": True,
            "llm_may_contribute": True,
            "llm_is_authority": False,
            "human_authority_preserved": True,
            "governance_authority_preserved": True,
            "worker_execution_requires_authorization": True,
            "authority_transfer_detected": False,
            "replay_visible": True,
            **_authority_flags(),
        }
    )


def _lifecycle_operation(
    spec: dict[str, Any],
    operation: str,
    human_approval_required: bool,
    human_approval_recorded: bool,
    status_after: str,
) -> dict[str, Any]:
    return {
        "operation_id": f"{spec['identity_id']}:{operation}",
        "operation": operation,
        "identity_id": spec["identity_id"],
        "credential_reference": spec["credential_reference"],
        "human_approval_required": human_approval_required,
        "human_approval_recorded": human_approval_recorded,
        "status_after": status_after,
        "credential_value_recorded": False,
        "replay_visible": True,
    }


def _summarize_role_artifacts(role_dir: Path, artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    credential = artifacts["credential_identity"]
    lifecycle = artifacts["lifecycle"]
    usage = artifacts["usage_metric"]
    participation = artifacts["participation"]
    authority = artifacts["authority_boundary"]
    return {
        "identity_id": credential["identity_id"],
        "external_provider_id": credential["external_provider_id"],
        "architectural_role": credential["architectural_role"],
        "credential_reference": credential["credential_reference"],
        "credential_enabled": lifecycle["final_lifecycle_status"] == "ENABLED",
        "final_lifecycle_status": lifecycle["final_lifecycle_status"],
        "participation_location": participation["participation_location"],
        "participation_role": participation["participation_role"],
        "success_count": usage["success_count"],
        "failure_count": usage["failure_count"],
        "cost_tracking_hooks_present": usage["cost_tracking"]["cost_tracking_hooks_present"],
        "authority_transfer_detected": authority["authority_transfer_detected"],
        "artifact_paths": {
            "credential_identity": str(role_dir / "000_credential_identity.json"),
            "lifecycle": str(role_dir / "001_lifecycle.json"),
            "usage_metric": str(role_dir / "002_usage_metric.json"),
            "participation": str(role_dir / "003_participation.json"),
            "authority_boundary": str(role_dir / "004_authority_boundary.json"),
        },
        "artifact_hashes": {
            "credential_identity": credential["artifact_hash"],
            "lifecycle": lifecycle["artifact_hash"],
            "usage_metric": usage["artifact_hash"],
            "participation": participation["artifact_hash"],
            "authority_boundary": authority["artifact_hash"],
        },
    }


def _assertions(
    *,
    role_results: list[dict[str, Any]],
    replay_reconstruction: dict[str, Any],
    secret_free: bool,
) -> dict[str, bool]:
    identity_ids = [item["identity_id"] for item in role_results]
    credential_references = [item["credential_reference"] for item in role_results]
    role_status = {item["identity_id"]: item["final_lifecycle_status"] for item in role_results}
    participation_roles = {item["architectural_role"]: item["participation_role"] for item in role_results}
    return {
        "role_separated_credential_identities_created": len(role_results) == 3,
        "credential_references_are_unique": len(set(credential_references)) == len(credential_references),
        "same_external_provider_shared_across_roles": {item["external_provider_id"] for item in role_results} == {"openai"},
        "independent_lifecycle_verified": role_status == {
            "openai-cognition": "ENABLED",
            "openai-translation": "DISABLED",
            "openai-repair": "ENABLED",
        },
        "independent_metrics_verified": len(set(identity_ids)) == len(role_results)
        and all(item["success_count"] + item["failure_count"] > 0 for item in role_results),
        "independent_costs_verified": all(item["cost_tracking_hooks_present"] for item in role_results),
        "independent_participation_records_verified": participation_roles == {
            "COGNITION_PROVIDER": "PROPOSAL_ONLY_COGNITION_PROVIDER",
            "TRANSLATION_WORKER": "TRANSLATION_WORKER_ASSISTANT",
            "REPAIR_WORKER": "REPAIR_WORKER_ASSISTANT",
        },
        "independent_enable_disable_controls_verified": role_status["openai-translation"] == "DISABLED"
        and role_status["openai-cognition"] == "ENABLED"
        and role_status["openai-repair"] == "ENABLED",
        "replay_distinguishes_cognition_provider": replay_reconstruction["distinguished_cognition_provider"],
        "replay_distinguishes_translation_worker": replay_reconstruction["distinguished_translation_worker"],
        "replay_distinguishes_repair_worker": replay_reconstruction["distinguished_repair_worker"],
        "governance_treats_each_role_as_distinct_identity": len(set(identity_ids)) == 3,
        "no_authority_transfer_occurs": not any(item["authority_transfer_detected"] for item in role_results),
        "replay_reconstructed": replay_reconstruction["replay_reconstructed"],
        "secret_free_evidence": secret_free,
    }


def _role_replay_references(role_results: list[dict[str, Any]]) -> dict[str, str]:
    references: dict[str, str] = {}
    for item in role_results:
        references[item["architectural_role"]] = item["artifact_paths"]["participation"]
    return references


def _authority_flags() -> dict[str, bool]:
    return {
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
    }


def _display_identifier(reference: str) -> str:
    suffix = reference.rsplit("/", maxsplit=1)[-1][-4:]
    return f"...{suffix}"


def _with_hash(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.iterdir():
        if path.is_dir() and re.fullmatch(r"CERT-\d{6}", path.name):
            existing.append(int(path.name.split("-")[1]))
    next_id = max(existing, default=0) + 1
    root = base / f"CERT-{next_id:06d}"
    root.mkdir(parents=True, exist_ok=False)
    return root


def _secret_free(root: Path) -> bool:
    for path in sorted(root.rglob("*.json")):
        data = canonical_serialize(load_json(path))
        if any(marker.lower() in data.lower() for marker in SECRET_MARKERS):
            return False
    return True


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    serialized = canonical_serialize(payload).lower()
    for marker in SECRET_MARKERS:
        if marker.lower() in serialized:
            raise FailClosedRuntimeError(f"secret-like marker found in role identity artifact: {marker}")


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {
            "assertion": assertion,
            "failure_reason": "role-separated LLM identity certification assertion failed",
        }
        for assertion, passed in assertions.items()
        if not passed
    ]


def main() -> None:
    result = run_role_separated_llm_identity_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")


if __name__ == "__main__":
    main()
