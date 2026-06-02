"""Deterministic conversation-to-implementation handoff runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.development_context_assembly_runtime import (
    CONTEXT_ASSEMBLED,
    DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED,
    DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATION_ARTIFACT_V1,
)
from aigol.runtime.domain_and_worker_resolution_registry import (
    DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
    RESOLUTION_SUCCEEDED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import (
    PROVIDER_NECESSITY_CLASSIFIED,
    PROVIDER_NECESSITY_POLICY_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CONVERSATION_TO_IMPLEMENTATION_HANDOFF_RUNTIME_VERSION = (
    "AIGOL_CONVERSATION_TO_IMPLEMENTATION_HANDOFF_RUNTIME_V1"
)
IMPLEMENTATION_HANDOFF_ARTIFACT_V1 = "IMPLEMENTATION_HANDOFF_ARTIFACT_V1"
IMPLEMENTATION_HANDOFF_CREATED = "IMPLEMENTATION_HANDOFF_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "implementation_handoff_created",
    "implementation_handoff_returned",
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


def create_conversation_to_implementation_handoff(
    *,
    handoff_id: str,
    proposal_artifact: dict[str, Any],
    proposal_contract_validation_artifact: dict[str, Any],
    context_assembly_artifact: dict[str, Any],
    registry_resolution_artifact: dict[str, Any],
    provider_necessity_policy_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a governed implementation handoff packet from already-validated evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        proposal = deepcopy(proposal_artifact)
        validation = deepcopy(proposal_contract_validation_artifact)
        context = deepcopy(context_assembly_artifact)
        registry = deepcopy(registry_resolution_artifact)
        provider_policy = deepcopy(provider_necessity_policy_artifact)
        _validate_proposal(proposal)
        _validate_contract_validation(validation)
        _validate_context(context)
        _validate_registry(registry)
        _validate_provider_policy(provider_policy)
        _validate_cross_references(
            proposal=proposal,
            validation=validation,
            context=context,
            registry=registry,
        )
        handoff = _handoff_artifact(
            handoff_id=handoff_id,
            proposal=proposal,
            validation=validation,
            context=context,
            registry=registry,
            provider_policy=provider_policy,
            handoff_status=IMPLEMENTATION_HANDOFF_CREATED,
            created_at=created_at,
            failure_reason=None,
        )
        returned = _returned_artifact(handoff)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], handoff)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(handoff, returned, replay_path)
    except Exception as exc:
        handoff = _failed_handoff_artifact(
            handoff_id=handoff_id,
            proposal=proposal_artifact if isinstance(proposal_artifact, dict) else {},
            validation=proposal_contract_validation_artifact
            if isinstance(proposal_contract_validation_artifact, dict)
            else {},
            context=context_assembly_artifact if isinstance(context_assembly_artifact, dict) else {},
            registry=registry_resolution_artifact if isinstance(registry_resolution_artifact, dict) else {},
            provider_policy=provider_necessity_policy_artifact
            if isinstance(provider_necessity_policy_artifact, dict)
            else {},
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(handoff)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], handoff)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(handoff, returned, replay_path)


def reconstruct_conversation_to_implementation_handoff_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct conversation-to-implementation handoff replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("implementation handoff replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("implementation handoff replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "implementation handoff")
        wrappers.append(wrapper)
    handoff = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("handoff_reference") != handoff["handoff_id"]:
        raise FailClosedRuntimeError("implementation handoff replay reference mismatch")
    if returned.get("handoff_hash") != handoff["artifact_hash"]:
        raise FailClosedRuntimeError("implementation handoff replay hash mismatch")
    return {
        "handoff_id": handoff["handoff_id"],
        "handoff_status": handoff["handoff_status"],
        "task_reference": handoff["task_reference"],
        "proposal_reference": handoff["proposal_reference"],
        "proposal_hash": handoff["proposal_hash"],
        "context_reference": handoff["context_reference"],
        "context_hash": handoff["context_hash"],
        "domain_reference": handoff["domain_reference"],
        "worker_reference": handoff["worker_reference"],
        "milestone_reference": handoff["milestone_reference"],
        "output_targets": deepcopy(handoff["output_targets"]),
        "validation_references": deepcopy(handoff["validation_references"]),
        "replay_references": deepcopy(handoff["replay_references"]),
        "failure_reason": handoff["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_proposal(proposal: dict[str, Any]) -> None:
    if proposal.get("artifact_type") != DEVELOPMENT_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation handoff failed closed: invalid proposal artifact")
    _verify_artifact_hash(proposal, "development proposal")
    if proposal.get("proposal_only") is not True:
        raise FailClosedRuntimeError("implementation handoff failed closed: proposal-only boundary missing")
    for field in FORBIDDEN_AUTHORITY_FIELDS:
        if proposal.get(field) is True:
            raise FailClosedRuntimeError("implementation handoff failed closed: authority violation detected")
    _require_string(proposal.get("proposal_id"), "proposal_id")
    _require_string(proposal.get("task_reference"), "task_reference")
    _require_string(proposal.get("context_reference"), "context_reference")
    _require_string(proposal.get("context_hash"), "context_hash")
    _require_string(proposal.get("domain_reference"), "domain_reference")
    _require_string(proposal.get("worker_reference"), "worker_reference")
    _require_string(proposal.get("milestone_reference"), "milestone_reference")
    _require_nonempty_string_list(proposal.get("proposed_outputs"), "proposed_outputs")
    _require_string_list(proposal.get("constraints_acknowledged"), "constraints_acknowledged")
    _require_string_list(proposal.get("assumptions"), "assumptions")
    _require_string_list(proposal.get("known_gaps"), "known_gaps")


def _validate_contract_validation(validation: dict[str, Any]) -> None:
    if validation.get("artifact_type") != DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation handoff failed closed: invalid proposal validation")
    _verify_artifact_hash(validation, "development proposal contract validation")
    if validation.get("validation_status") != DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED:
        raise FailClosedRuntimeError("implementation handoff failed closed: proposal validation failed")
    _require_string(validation.get("contract_validation_id"), "contract_validation_id")
    _require_string(validation.get("proposal_hash"), "proposal_hash")
    _require_string(validation.get("context_hash"), "context_hash")


def _validate_context(context: dict[str, Any]) -> None:
    if context.get("artifact_type") != DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation handoff failed closed: invalid context artifact")
    _verify_artifact_hash(context, "development context assembly")
    if context.get("context_status") != CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("implementation handoff failed closed: context is not assembled")
    _require_string(context.get("context_assembly_id"), "context_assembly_id")
    _require_string(context.get("context_hash"), "context_hash")


def _validate_registry(registry: dict[str, Any]) -> None:
    if registry.get("artifact_type") != DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation handoff failed closed: invalid registry resolution")
    _verify_artifact_hash(registry, "domain worker resolution")
    if registry.get("resolution_status") != RESOLUTION_SUCCEEDED:
        raise FailClosedRuntimeError("implementation handoff failed closed: registry resolution failed")
    _require_string(registry.get("resolution_id"), "resolution_id")
    _require_string(registry.get("domain_id"), "domain_id")
    _require_string(registry.get("worker_family_id"), "worker_family_id")
    _require_string(registry.get("milestone_type"), "milestone_type")


def _validate_provider_policy(provider_policy: dict[str, Any]) -> None:
    if provider_policy.get("artifact_type") != PROVIDER_NECESSITY_POLICY_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation handoff failed closed: invalid provider necessity policy")
    _verify_artifact_hash(provider_policy, "provider necessity policy")
    if provider_policy.get("policy_status") != PROVIDER_NECESSITY_CLASSIFIED:
        raise FailClosedRuntimeError("implementation handoff failed closed: provider necessity policy failed")
    _require_string(provider_policy.get("policy_decision_id"), "policy_decision_id")
    _require_string(provider_policy.get("necessity_classification"), "necessity_classification")
    _require_string(provider_policy.get("policy_hash"), "policy_hash")


def _validate_cross_references(
    *,
    proposal: dict[str, Any],
    validation: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
) -> None:
    expected = {
        "proposal_hash": proposal["artifact_hash"],
        "context_hash": context["context_hash"],
        "domain_reference": registry["domain_id"],
        "worker_reference": registry["worker_family_id"],
        "milestone_reference": registry["milestone_type"],
    }
    for field, expected_value in expected.items():
        if validation.get(field) != expected_value:
            raise FailClosedRuntimeError("implementation handoff failed closed: hashes mismatch")
    proposal_expected = {
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": registry["domain_id"],
        "worker_reference": registry["worker_family_id"],
        "milestone_reference": registry["milestone_type"],
    }
    for field, expected_value in proposal_expected.items():
        if proposal.get(field) != expected_value:
            raise FailClosedRuntimeError("implementation handoff failed closed: references are missing")


def _handoff_artifact(
    *,
    handoff_id: str,
    proposal: dict[str, Any],
    validation: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
    provider_policy: dict[str, Any],
    handoff_status: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPLEMENTATION_HANDOFF_ARTIFACT_V1,
        "runtime_version": AIGOL_CONVERSATION_TO_IMPLEMENTATION_HANDOFF_RUNTIME_VERSION,
        "handoff_id": _require_string(handoff_id, "handoff_id"),
        "handoff_status": handoff_status,
        "task_reference": proposal.get("task_reference"),
        "proposal_reference": proposal.get("proposal_id"),
        "proposal_hash": proposal.get("artifact_hash"),
        "context_reference": proposal.get("context_reference"),
        "context_hash": proposal.get("context_hash") or context.get("context_hash"),
        "domain_reference": proposal.get("domain_reference"),
        "worker_reference": proposal.get("worker_reference"),
        "milestone_reference": proposal.get("milestone_reference"),
        "output_targets": deepcopy(proposal.get("proposed_outputs", [])),
        "validation_references": {
            "proposal_contract_validation_reference": validation.get("contract_validation_id"),
            "proposal_contract_validation_hash": validation.get("artifact_hash"),
            "provider_necessity_policy_reference": provider_policy.get("policy_decision_id"),
            "provider_necessity_policy_hash": provider_policy.get("artifact_hash"),
            "registry_resolution_reference": registry.get("resolution_id"),
            "registry_resolution_hash": registry.get("artifact_hash"),
        },
        "replay_references": {
            "context_replay_reference": context.get("replay_reference"),
            "proposal_contract_replay_reference": validation.get("replay_reference"),
            "registry_resolution_replay_reference": registry.get("replay_reference"),
        },
        "constraints": deepcopy(proposal.get("constraints_acknowledged", [])),
        "assumptions": deepcopy(proposal.get("assumptions", [])),
        "known_gaps": deepcopy(proposal.get("known_gaps", [])),
        "provider_necessity_classification": provider_policy.get("necessity_classification"),
        "implementation_authorized": False,
        "proposal_only": True,
        "provider_invoked": False,
        "worker_invoked": False,
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
    artifact["handoff_hash"] = replay_hash(
        {
            "task_reference": artifact["task_reference"],
            "proposal_hash": artifact["proposal_hash"],
            "context_hash": artifact["context_hash"],
            "registry_resolution_hash": artifact["validation_references"]["registry_resolution_hash"],
            "output_targets": artifact["output_targets"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_handoff_artifact(
    *,
    handoff_id: str,
    proposal: dict[str, Any],
    validation: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
    provider_policy: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    return _handoff_artifact(
        handoff_id=handoff_id,
        proposal=proposal,
        validation=validation,
        context=context,
        registry=registry,
        provider_policy=provider_policy,
        handoff_status=FAILED_CLOSED,
        created_at=created_at,
        failure_reason=failure_reason,
    )


def _returned_artifact(handoff: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(handoff, "implementation handoff")
    returned = {
        "event_type": "IMPLEMENTATION_HANDOFF_RETURNED",
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "handoff_status": handoff["handoff_status"],
        "proposal_hash": handoff["proposal_hash"],
        "context_hash": handoff["context_hash"],
        "domain_reference": handoff["domain_reference"],
        "worker_reference": handoff["worker_reference"],
        "milestone_reference": handoff["milestone_reference"],
        "implementation_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": handoff["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(handoff: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "implementation_handoff_artifact": deepcopy(handoff),
        "implementation_handoff_replay": deepcopy(returned),
        "implementation_handoff_replay_reference": str(replay_path),
        "handoff_status": handoff["handoff_status"],
        "handoff_hash": handoff["handoff_hash"],
        "task_reference": handoff["task_reference"],
        "proposal_reference": handoff["proposal_reference"],
        "proposal_hash": handoff["proposal_hash"],
        "context_reference": handoff["context_reference"],
        "context_hash": handoff["context_hash"],
        "domain_reference": handoff["domain_reference"],
        "worker_reference": handoff["worker_reference"],
        "milestone_reference": handoff["milestone_reference"],
        "output_targets": deepcopy(handoff["output_targets"]),
        "validation_references": deepcopy(handoff["validation_references"]),
        "replay_references": deepcopy(handoff["replay_references"]),
        "constraints": deepcopy(handoff["constraints"]),
        "assumptions": deepcopy(handoff["assumptions"]),
        "known_gaps": deepcopy(handoff["known_gaps"]),
        "fail_closed": handoff["handoff_status"] == FAILED_CLOSED,
        "failure_reason": handoff["failure_reason"],
        "implementation_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["conversation_to_implementation_handoff_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("implementation handoff replay step ordering mismatch")
    _verify_artifact_hash(artifact, "implementation handoff")
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
        raise FailClosedRuntimeError("implementation handoff replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("implementation handoff replay hash mismatch")


def _require_nonempty_string_list(value: Any, field_name: str) -> list[str]:
    items = _require_string_list(value, field_name)
    if not items:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return items


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"{field_name} is required")
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
    return "implementation handoff failed closed"

