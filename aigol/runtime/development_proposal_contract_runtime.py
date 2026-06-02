"""Deterministic development proposal contract runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.development_context_assembly_runtime import (
    CONTEXT_ASSEMBLED,
    DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.domain_and_worker_resolution_registry import (
    DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
    RESOLUTION_SUCCEEDED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME_VERSION = "AIGOL_DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME_V1"
DEVELOPMENT_PROPOSAL_ARTIFACT_V1 = "DEVELOPMENT_PROPOSAL_ARTIFACT_V1"
DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATION_ARTIFACT_V1 = (
    "DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATION_ARTIFACT_V1"
)
DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED = "DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "development_proposal_contract_validated",
    "development_proposal_contract_returned",
)

REQUIRED_PROPOSAL_FIELDS = (
    "artifact_type",
    "proposal_id",
    "task_reference",
    "context_reference",
    "context_hash",
    "domain_reference",
    "worker_reference",
    "milestone_reference",
    "proposal_summary",
    "proposed_outputs",
    "constraints_acknowledged",
    "assumptions",
    "known_gaps",
    "proposal_only",
    "artifact_hash",
)

FORBIDDEN_AUTHORITY_FIELDS = (
    "execution_authority",
    "dispatch_authority",
    "governance_authority",
    "replay_authority",
    "provider_authority",
    "execution_requested",
    "dispatch_requested",
    "worker_created",
    "domain_created",
    "governance_modified",
    "replay_modified",
)


def validate_development_proposal_contract(
    *,
    contract_validation_id: str,
    proposal_artifact: dict[str, Any],
    context_assembly_artifact: dict[str, Any],
    registry_resolution_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Validate that a development proposal satisfies the proposal-only contract."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        proposal = deepcopy(proposal_artifact)
        context = deepcopy(context_assembly_artifact)
        registry = deepcopy(registry_resolution_artifact)
        _validate_context(context)
        _validate_registry_resolution(registry)
        _validate_proposal(proposal)
        _validate_cross_references(proposal=proposal, context=context, registry=registry)
        validation = _validation_artifact(
            contract_validation_id=contract_validation_id,
            proposal=proposal,
            context=context,
            registry=registry,
            validation_status=DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED,
            validation_reason="development proposal satisfies proposal-only contract",
            created_at=created_at,
            failure_reason=None,
        )
        returned = _returned_artifact(validation)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], validation)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(validation, returned, replay_path)
    except Exception as exc:
        validation = _failed_validation_artifact(
            contract_validation_id=contract_validation_id,
            proposal=proposal_artifact if isinstance(proposal_artifact, dict) else {},
            context=context_assembly_artifact if isinstance(context_assembly_artifact, dict) else {},
            registry=registry_resolution_artifact if isinstance(registry_resolution_artifact, dict) else {},
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(validation)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], validation)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(validation, returned, replay_path)


def reconstruct_development_proposal_contract_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct development proposal contract validation replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("development proposal contract replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("development proposal contract replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "development proposal contract validation")
        wrappers.append(wrapper)
    validation = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("contract_validation_reference") != validation["contract_validation_id"]:
        raise FailClosedRuntimeError("development proposal contract replay reference mismatch")
    if returned.get("contract_validation_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("development proposal contract replay hash mismatch")
    return {
        "contract_validation_id": validation["contract_validation_id"],
        "validation_status": validation["validation_status"],
        "proposal_id": validation["proposal_id"],
        "proposal_hash": validation["proposal_hash"],
        "context_reference": validation["context_reference"],
        "context_hash": validation["context_hash"],
        "domain_reference": validation["domain_reference"],
        "worker_reference": validation["worker_reference"],
        "milestone_reference": validation["milestone_reference"],
        "registry_resolution_reference": validation["registry_resolution_reference"],
        "registry_resolution_hash": validation["registry_resolution_hash"],
        "failure_reason": validation["failure_reason"],
        "proposal_only": True,
        "provider_invoked": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_context(context: dict[str, Any]) -> None:
    if context.get("artifact_type") != DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("development proposal contract failed closed: invalid context artifact")
    _verify_artifact_hash(context, "development context assembly")
    if context.get("context_status") != CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("development proposal contract failed closed: context is not assembled")
    _require_string(context.get("context_assembly_id"), "context_assembly_id")
    _require_string(context.get("context_hash"), "context_hash")
    _require_string(context.get("development_task_intake_reference"), "development_task_intake_reference")


def _validate_registry_resolution(registry: dict[str, Any]) -> None:
    if registry.get("artifact_type") != DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("development proposal contract failed closed: invalid registry resolution")
    _verify_artifact_hash(registry, "domain worker resolution")
    if registry.get("resolution_status") != RESOLUTION_SUCCEEDED:
        raise FailClosedRuntimeError("development proposal contract failed closed: registry resolution not successful")
    _require_string(registry.get("resolution_id"), "resolution_id")
    _require_string(registry.get("domain_id"), "domain_id")
    _require_string(registry.get("worker_family_id"), "worker_family_id")
    _require_string(registry.get("milestone_type"), "milestone_type")


def _validate_proposal(proposal: dict[str, Any]) -> None:
    for field in REQUIRED_PROPOSAL_FIELDS:
        if field not in proposal:
            raise FailClosedRuntimeError("development proposal contract failed closed: proposal is incomplete")
    if proposal.get("artifact_type") != DEVELOPMENT_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("development proposal contract failed closed: invalid proposal artifact")
    _verify_artifact_hash(proposal, "development proposal")
    for field in (
        "proposal_id",
        "task_reference",
        "context_reference",
        "context_hash",
        "domain_reference",
        "worker_reference",
        "milestone_reference",
        "proposal_summary",
    ):
        _require_string(proposal.get(field), field)
    if proposal.get("proposal_only") is not True:
        raise FailClosedRuntimeError("development proposal contract failed closed: proposal-only boundary missing")
    for field in FORBIDDEN_AUTHORITY_FIELDS:
        if proposal.get(field) is True:
            raise FailClosedRuntimeError("development proposal contract failed closed: proposal violates authority boundary")
    _require_nonempty_string_list(proposal.get("proposed_outputs"), "proposed_outputs")
    _require_string_list(proposal.get("constraints_acknowledged"), "constraints_acknowledged")
    _require_string_list(proposal.get("assumptions"), "assumptions")
    _require_string_list(proposal.get("known_gaps"), "known_gaps")
    if len(set(proposal["proposed_outputs"])) != len(proposal["proposed_outputs"]):
        raise FailClosedRuntimeError("development proposal contract failed closed: proposal is ambiguous")


def _validate_cross_references(
    *,
    proposal: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
) -> None:
    expected = {
        "task_reference": context["development_task_intake_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": registry["domain_id"],
        "worker_reference": registry["worker_family_id"],
        "milestone_reference": registry["milestone_type"],
    }
    for field, expected_value in expected.items():
        if proposal.get(field) != expected_value:
            raise FailClosedRuntimeError("development proposal contract failed closed: proposal references unknown entities")
    if context.get("requested_domain") != registry["domain_id"]:
        raise FailClosedRuntimeError("development proposal contract failed closed: context and registry domain mismatch")
    if context.get("requested_worker_family") != registry["worker_family_id"]:
        raise FailClosedRuntimeError("development proposal contract failed closed: context and registry worker mismatch")


def _validation_artifact(
    *,
    contract_validation_id: str,
    proposal: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
    validation_status: str,
    validation_reason: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME_VERSION,
        "contract_validation_id": _require_string(contract_validation_id, "contract_validation_id"),
        "proposal_id": proposal.get("proposal_id"),
        "proposal_hash": proposal.get("artifact_hash"),
        "context_reference": proposal.get("context_reference"),
        "context_hash": proposal.get("context_hash") or context.get("context_hash"),
        "domain_reference": proposal.get("domain_reference"),
        "worker_reference": proposal.get("worker_reference"),
        "milestone_reference": proposal.get("milestone_reference"),
        "registry_resolution_reference": registry.get("resolution_id"),
        "registry_resolution_hash": registry.get("artifact_hash"),
        "validation_status": validation_status,
        "validation_reason": _require_string(validation_reason, "validation_reason"),
        "proposal_only": True,
        "provider_invoked": False,
        "provider_authority": False,
        "proposal_generated": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_validation_artifact(
    *,
    contract_validation_id: str,
    proposal: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    return _validation_artifact(
        contract_validation_id=contract_validation_id,
        proposal=proposal,
        context=context,
        registry=registry,
        validation_status=FAILED_CLOSED,
        validation_reason="development proposal contract failed closed",
        created_at=created_at,
        failure_reason=failure_reason,
    )


def _returned_artifact(validation: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(validation, "development proposal contract validation")
    returned = {
        "event_type": "DEVELOPMENT_PROPOSAL_CONTRACT_RETURNED",
        "contract_validation_reference": validation["contract_validation_id"],
        "contract_validation_hash": validation["artifact_hash"],
        "validation_status": validation["validation_status"],
        "proposal_id": validation["proposal_id"],
        "proposal_hash": validation["proposal_hash"],
        "context_hash": validation["context_hash"],
        "domain_reference": validation["domain_reference"],
        "worker_reference": validation["worker_reference"],
        "milestone_reference": validation["milestone_reference"],
        "proposal_only": True,
        "provider_invoked": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": validation["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(validation: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "development_proposal_contract_validation_artifact": deepcopy(validation),
        "development_proposal_contract_replay": deepcopy(returned),
        "development_proposal_contract_replay_reference": str(replay_path),
        "validation_status": validation["validation_status"],
        "proposal_id": validation["proposal_id"],
        "proposal_hash": validation["proposal_hash"],
        "context_hash": validation["context_hash"],
        "domain_reference": validation["domain_reference"],
        "worker_reference": validation["worker_reference"],
        "milestone_reference": validation["milestone_reference"],
        "registry_resolution_reference": validation["registry_resolution_reference"],
        "registry_resolution_hash": validation["registry_resolution_hash"],
        "proposal_only": True,
        "fail_closed": validation["validation_status"] == FAILED_CLOSED,
        "failure_reason": validation["failure_reason"],
        "provider_invoked": False,
        "proposal_generated": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["development_proposal_contract_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("development proposal contract replay step ordering mismatch")
    _verify_artifact_hash(artifact, "development proposal contract artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("development proposal contract replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("development proposal contract replay hash mismatch")


def _require_nonempty_string_list(value: Any, field_name: str) -> list[str]:
    items = _require_string_list(value, field_name)
    if not items:
        raise FailClosedRuntimeError("development proposal contract failed closed: proposal is incomplete")
    return items


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError("development proposal contract failed closed: proposal is incomplete")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise FailClosedRuntimeError(f"{field_name} must contain strings")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "development proposal contract failed closed"

