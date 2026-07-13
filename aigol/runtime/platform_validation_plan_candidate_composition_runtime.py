"""Deterministic Platform Validation Plan-to-Candidate composition."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_allowlist import get_validation_command_spec
from aigol.runtime.platform_core_validation_candidate import (
    VALIDATION_CANDIDATE_ARTIFACT_V1,
    create_governed_validation_candidate,
    validate_governed_validation_candidate,
)
from aigol.runtime.platform_core_validation_suite_candidate import (
    VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1,
    create_governed_validation_suite_candidate,
    validate_governed_validation_suite_candidate,
)
from aigol.runtime.platform_validation_planning_runtime import (
    FAILED_CLOSED as PLAN_FAILED_CLOSED,
    PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
    validate_platform_validation_plan_artifact,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PLATFORM_VALIDATION_PLAN_CANDIDATE_COMPOSITION_RUNTIME_VERSION = (
    "G27_09_PLATFORM_VALIDATION_PLAN_CANDIDATE_COMPOSITION_RUNTIME_V1"
)
PLATFORM_VALIDATION_CANDIDATE_COMPOSITION_ARTIFACT_V1 = (
    "PLATFORM_VALIDATION_CANDIDATE_COMPOSITION_ARTIFACT_V1"
)
SINGLE_VALIDATION_CANDIDATE_COMPOSED = "SINGLE_VALIDATION_CANDIDATE_COMPOSED"
VALIDATION_SUITE_CANDIDATE_COMPOSED = "VALIDATION_SUITE_CANDIDATE_COMPOSED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEP = "platform_validation_candidate_composition_recorded"

AUTHORITY_FLAGS = {
    "executes_validation": False,
    "invokes_workers": False,
    "invokes_providers": False,
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_mutation": False,
    "certifies_results": False,
    "synthesizes_commands": False,
    "expands_validation_allowlist": False,
}


def compose_platform_validation_candidate(
    *,
    composition_id: str,
    session_id: str,
    validation_plan_artifact: dict[str, Any],
    validation_plan_reference: str,
    validation_plan_artifact_hash: str,
    validation_plan_hash: str,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Compose exactly one existing candidate artifact from one validation plan."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        composition = _require_string(composition_id, "composition_id")
        session = _require_string(session_id, "session_id")
        source_reference = _require_string(validation_plan_reference, "validation_plan_reference")
        source_artifact_hash = _require_hash(validation_plan_artifact_hash, "validation_plan_artifact_hash")
        source_plan_hash = _require_hash(validation_plan_hash, "validation_plan_hash")
        plan = validate_platform_validation_plan_artifact(validation_plan_artifact)
        _validate_plan_binding(plan, source_reference, source_artifact_hash, source_plan_hash)
        commands = _validated_command_references(plan)
        requirements = _mandatory_requirements(plan)
        if not commands:
            raise FailClosedRuntimeError(
                "platform validation candidate composition failed closed: mandatory requirements lack exact allowlisted command mappings"
            )
        lineage = _plan_lineage(plan, source_artifact_hash, source_plan_hash, requirements)
        creator = _require_string(created_by, "created_by")
        timestamp = _require_string(created_at, "created_at")
        candidate, status = _compose_existing_candidate(
            composition_id=composition,
            session_id=session,
            commands=commands,
            lineage=lineage,
            requirements=requirements,
            created_by=creator,
            created_at=timestamp,
        )
        artifact = _composition_artifact(
            composition_id=composition,
            session_id=session,
            plan_reference=source_reference,
            plan_artifact_hash=source_artifact_hash,
            plan_hash=source_plan_hash,
            command_references=commands,
            requirement_references=requirements,
            candidate=candidate,
            composition_status=status,
            created_by=creator,
            created_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_artifact(
            composition_id=composition_id,
            session_id=session_id,
            validation_plan_artifact=validation_plan_artifact,
            validation_plan_reference=validation_plan_reference,
            validation_plan_artifact_hash=validation_plan_artifact_hash,
            validation_plan_hash=validation_plan_hash,
            created_by=created_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_if_possible(replay_path, artifact)
    return _capture(artifact, replay_path)


def validate_platform_validation_candidate_composition_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one canonical plan-to-candidate composition artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("platform validation candidate composition artifact must be a JSON object")
    candidate = deepcopy(artifact)
    _verify_composition_artifact(candidate)
    return candidate


def reconstruct_platform_validation_candidate_composition_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct and verify one plan-to-candidate composition replay."""

    wrapper = load_json(Path(replay_dir) / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("platform validation candidate composition replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "platform validation candidate composition replay hash mismatch")
    artifact = validate_platform_validation_candidate_composition_artifact(wrapper.get("artifact"))
    return {
        "composition_id": artifact["composition_id"],
        "composition_status": artifact["composition_status"],
        "validation_plan_reference": artifact["validation_plan_reference"],
        "validation_plan_hash": artifact["validation_plan_hash"],
        "candidate_artifact_type": artifact["candidate_artifact_type"],
        "candidate_artifact_hash": artifact["candidate_artifact_hash"],
        "candidate_artifact": deepcopy(artifact["candidate_artifact"]),
        "composition_hash": artifact["composition_hash"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "fail_closed": artifact["composition_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "replay_hash": wrapper["replay_hash"],
    }


def _validate_plan_binding(plan: dict[str, Any], reference: str, artifact_hash: str, plan_hash: str) -> None:
    if plan.get("artifact_type") != PLATFORM_VALIDATION_PLAN_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform validation candidate composition failed closed: validation plan required")
    if plan.get("planning_status") == PLAN_FAILED_CLOSED:
        raise FailClosedRuntimeError("platform validation candidate composition failed closed: source plan failed closed")
    if plan.get("validation_plan_id") != reference:
        raise FailClosedRuntimeError("platform validation candidate composition failed closed: plan reference mismatch")
    if plan.get("artifact_hash") != artifact_hash:
        raise FailClosedRuntimeError("platform validation candidate composition failed closed: plan artifact hash mismatch")
    if plan.get("platform_validation_plan_hash") != plan_hash:
        raise FailClosedRuntimeError("platform validation candidate composition failed closed: plan hash mismatch")


def _mandatory_requirements(plan: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = plan.get("validation_requirements")
    if not isinstance(requirements, list) or not requirements:
        raise FailClosedRuntimeError("platform validation candidate composition failed closed: mandatory requirements required")
    mandatory = []
    for requirement in requirements:
        if not isinstance(requirement, dict) or requirement.get("required") is not True:
            raise FailClosedRuntimeError("platform validation candidate composition failed closed: requirement is not mandatory")
        mandatory.append(
            {
                "requirement_id": _require_string(requirement.get("requirement_id"), "requirement_id"),
                "requirement_hash": _require_hash(requirement.get("requirement_hash"), "requirement_hash"),
                "requirement_type": _require_string(requirement.get("requirement_type"), "requirement_type"),
            }
        )
    return mandatory


def _validated_command_references(plan: dict[str, Any]) -> list[dict[str, Any]]:
    references = plan.get("allowlisted_command_references")
    if not isinstance(references, list):
        raise FailClosedRuntimeError("platform validation candidate composition failed closed: command references required")
    validated = []
    seen: set[tuple[str, str]] = set()
    for index, reference in enumerate(references):
        if not isinstance(reference, dict):
            raise FailClosedRuntimeError("platform validation candidate composition failed closed: command reference invalid")
        command_id = _require_string(reference.get("command_id"), "command_id")
        spec = get_validation_command_spec(command_id)
        if reference.get("command_spec_hash") != spec["spec_hash"]:
            raise FailClosedRuntimeError("platform validation candidate composition failed closed: command spec hash mismatch")
        if reference.get("allowlist_version") != spec["allowlist_version"]:
            raise FailClosedRuntimeError("platform validation candidate composition failed closed: allowlist version mismatch")
        if reference.get("exact_mapping_basis") != "DECLARED_COMMAND_TARGET_SET_EQUALS_AFFECTED_PATH_SET":
            raise FailClosedRuntimeError("platform validation candidate composition failed closed: exact command mapping required")
        reference_hash = replay_hash(reference)
        identity = (command_id, reference_hash)
        if identity in seen:
            raise FailClosedRuntimeError("platform validation candidate composition failed closed: duplicate command reference")
        seen.add(identity)
        validated.append(
            {
                "command_index": index,
                "command_id": command_id,
                "command_spec_hash": spec["spec_hash"],
                "allowlist_version": spec["allowlist_version"],
                "exact_mapping_basis": reference["exact_mapping_basis"],
                "affected_paths": deepcopy(reference.get("affected_paths") or []),
                "source_command_reference_hash": reference_hash,
            }
        )
    return validated


def _plan_lineage(plan: dict[str, Any], artifact_hash: str, plan_hash: str, requirements: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source_artifact_type": PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
        "validation_plan_id": plan["validation_plan_id"],
        "validation_plan_artifact_hash": artifact_hash,
        "validation_plan_hash": plan_hash,
        "platform_change_impact_reference": plan["platform_change_impact_reference"],
        "platform_change_impact_hash": plan["platform_change_impact_hash"],
        "requirement_ids": [item["requirement_id"] for item in requirements],
        "requirement_hashes": [item["requirement_hash"] for item in requirements],
        "replay_visible": True,
    }


def _compose_existing_candidate(*, composition_id: str, session_id: str, commands: list[dict[str, Any]], lineage: dict[str, Any], requirements: list[dict[str, Any]], created_by: str, created_at: str) -> tuple[dict[str, Any], str]:
    if len(commands) == 1:
        command = commands[0]
        candidate = create_governed_validation_candidate(
            candidate_id=f"{composition_id}:CANDIDATE",
            session_id=session_id,
            command_id=command["command_id"],
            validation_purpose=_validation_purpose(command, requirements),
            created_by=created_by,
            created_at=created_at,
            associated_reference={**deepcopy(lineage), "command_reference": deepcopy(command)},
        )
        return validate_governed_validation_candidate(candidate), SINGLE_VALIDATION_CANDIDATE_COMPOSED
    suite_commands = [
        {
            "command_id": command["command_id"],
            "validation_purpose": _validation_purpose(command, requirements),
            "associated_reference": {**deepcopy(lineage), "command_reference": deepcopy(command)},
        }
        for command in commands
    ]
    candidate = create_governed_validation_suite_candidate(
        candidate_id=f"{composition_id}:SUITE-CANDIDATE",
        session_id=session_id,
        commands=suite_commands,
        created_by=created_by,
        created_at=created_at,
        associated_reference=deepcopy(lineage),
    )
    return validate_governed_validation_suite_candidate(candidate), VALIDATION_SUITE_CANDIDATE_COMPOSED


def _validation_purpose(command: dict[str, Any], requirements: list[dict[str, Any]]) -> str:
    requirement_ids = ",".join(item["requirement_id"] for item in requirements)
    return f"{command['command_id']} exact validation for {requirement_ids}"


def _composition_artifact(*, composition_id: str, session_id: str, plan_reference: str, plan_artifact_hash: str, plan_hash: str, command_references: list[dict[str, Any]], requirement_references: list[dict[str, Any]], candidate: dict[str, Any] | None, composition_status: str, created_by: str, created_at: str, failure_reason: str | None) -> dict[str, Any]:
    artifact = {
        "artifact_type": PLATFORM_VALIDATION_CANDIDATE_COMPOSITION_ARTIFACT_V1,
        "runtime_version": PLATFORM_VALIDATION_PLAN_CANDIDATE_COMPOSITION_RUNTIME_VERSION,
        "composition_id": composition_id,
        "session_id": session_id,
        "composition_status": composition_status,
        "source_artifact_type": PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
        "validation_plan_reference": plan_reference,
        "validation_plan_artifact_hash": plan_artifact_hash,
        "validation_plan_hash": plan_hash,
        "ordered_command_references": deepcopy(command_references),
        "command_reference_count": len(command_references),
        "mandatory_requirement_references": deepcopy(requirement_references),
        "mandatory_requirement_count": len(requirement_references),
        "candidate_artifact_type": candidate.get("artifact_type") if isinstance(candidate, dict) else None,
        "candidate_artifact_hash": candidate.get("artifact_hash") if isinstance(candidate, dict) else None,
        "candidate_artifact": deepcopy(candidate),
        "candidate_count": 1 if isinstance(candidate, dict) else 0,
        "deterministic_ordering_preserved": True,
        "plan_lineage_bound": isinstance(candidate, dict),
        "replay_visible": True,
        "read_only_composition": True,
        "validation_executed": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "certification_performed": False,
        "commands_synthesized": False,
        "validation_allowlist_expanded": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "created_by": created_by,
        "created_at": created_at,
        "failure_reason": failure_reason,
    }
    artifact["composition_hash"] = _composition_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(*, composition_id: Any, session_id: Any, validation_plan_artifact: Any, validation_plan_reference: Any, validation_plan_artifact_hash: Any, validation_plan_hash: Any, created_by: Any, created_at: Any, failure_reason: str) -> dict[str, Any]:
    source = validation_plan_artifact if isinstance(validation_plan_artifact, dict) else {}
    return _composition_artifact(
        composition_id=_safe_string(composition_id),
        session_id=_safe_string(session_id),
        plan_reference=_safe_string(validation_plan_reference),
        plan_artifact_hash=_safe_hash(validation_plan_artifact_hash or source.get("artifact_hash")),
        plan_hash=_safe_hash(validation_plan_hash or source.get("platform_validation_plan_hash")),
        command_references=[],
        requirement_references=[],
        candidate=None,
        composition_status=FAILED_CLOSED,
        created_by=_safe_string(created_by),
        created_at=_safe_string(created_at),
        failure_reason=failure_reason,
    )


def _verify_composition_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != PLATFORM_VALIDATION_CANDIDATE_COMPOSITION_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform validation candidate composition artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "platform validation candidate composition artifact hash mismatch")
    if artifact.get("composition_hash") != _composition_hash(artifact):
        raise FailClosedRuntimeError("platform validation candidate composition hash mismatch")
    if artifact.get("replay_visible") is not True or artifact.get("read_only_composition") is not True:
        raise FailClosedRuntimeError("platform validation candidate composition must be replay-visible and read-only")
    if any(value is not False for value in artifact.get("authority_flags", {}).values()):
        raise FailClosedRuntimeError("platform validation candidate composition cannot grant authority")
    status = artifact.get("composition_status")
    if status not in {SINGLE_VALIDATION_CANDIDATE_COMPOSED, VALIDATION_SUITE_CANDIDATE_COMPOSED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("platform validation candidate composition status invalid")
    commands = artifact.get("ordered_command_references")
    requirements = artifact.get("mandatory_requirement_references")
    if not isinstance(commands, list) or artifact.get("command_reference_count") != len(commands):
        raise FailClosedRuntimeError("platform validation candidate composition command reference count mismatch")
    if not isinstance(requirements, list) or artifact.get("mandatory_requirement_count") != len(requirements):
        raise FailClosedRuntimeError("platform validation candidate composition requirement count mismatch")
    candidate = artifact.get("candidate_artifact")
    if status == FAILED_CLOSED:
        if candidate is not None or artifact.get("candidate_count") != 0 or commands or requirements:
            raise FailClosedRuntimeError("failed candidate composition cannot contain a candidate")
        return
    if not isinstance(candidate, dict) or artifact.get("candidate_count") != 1:
        raise FailClosedRuntimeError("successful candidate composition requires exactly one candidate")
    if status == SINGLE_VALIDATION_CANDIDATE_COMPOSED:
        validated = validate_governed_validation_candidate(candidate)
        expected_type = VALIDATION_CANDIDATE_ARTIFACT_V1
        expected_commands = 1
    else:
        validated = validate_governed_validation_suite_candidate(candidate)
        expected_type = VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1
        expected_commands = artifact.get("command_reference_count")
    if artifact.get("candidate_artifact_type") != expected_type:
        raise FailClosedRuntimeError("platform validation candidate composition candidate type mismatch")
    if artifact.get("candidate_artifact_hash") != validated["artifact_hash"]:
        raise FailClosedRuntimeError("platform validation candidate composition candidate hash mismatch")
    if artifact.get("command_reference_count") != expected_commands:
        raise FailClosedRuntimeError("platform validation candidate composition command count mismatch")
    expected_command_ids = [item.get("command_id") for item in commands]
    actual_command_ids = (
        [validated["command_id"]]
        if status == SINGLE_VALIDATION_CANDIDATE_COMPOSED
        else validated["command_ids"]
    )
    if actual_command_ids != expected_command_ids:
        raise FailClosedRuntimeError("platform validation candidate composition command ordering mismatch")
    lineage = validated.get("associated_reference")
    if not isinstance(lineage, dict):
        raise FailClosedRuntimeError("platform validation candidate composition plan lineage missing")
    if lineage.get("validation_plan_id") != artifact.get("validation_plan_reference"):
        raise FailClosedRuntimeError("platform validation candidate composition plan lineage reference mismatch")
    if lineage.get("validation_plan_artifact_hash") != artifact.get("validation_plan_artifact_hash"):
        raise FailClosedRuntimeError("platform validation candidate composition plan lineage artifact hash mismatch")
    if lineage.get("validation_plan_hash") != artifact.get("validation_plan_hash"):
        raise FailClosedRuntimeError("platform validation candidate composition plan lineage hash mismatch")
    if lineage.get("requirement_ids") != [item.get("requirement_id") for item in requirements]:
        raise FailClosedRuntimeError("platform validation candidate composition requirement lineage mismatch")


def _composition_hash(artifact: dict[str, Any]) -> str:
    return replay_hash({key: deepcopy(artifact[key]) for key in (
        "source_artifact_type", "validation_plan_reference", "validation_plan_artifact_hash", "validation_plan_hash",
        "ordered_command_references", "mandatory_requirement_references", "candidate_artifact_type",
        "candidate_artifact_hash", "candidate_artifact", "composition_status", "deterministic_ordering_preserved",
        "plan_lineage_bound", "authority_flags", "failure_reason",
    )})


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": PLATFORM_VALIDATION_PLAN_CANDIDATE_COMPOSITION_RUNTIME_VERSION,
        "platform_validation_candidate_composition_artifact": deepcopy(artifact),
        "composition_id": artifact["composition_id"],
        "composition_status": artifact["composition_status"],
        "candidate_artifact": deepcopy(artifact["candidate_artifact"]),
        "candidate_artifact_type": artifact["candidate_artifact_type"],
        "candidate_artifact_hash": artifact["candidate_artifact_hash"],
        "composition_hash": artifact["composition_hash"],
        "composition_replay_reference": str(replay_path),
        "fail_closed": artifact["composition_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "validation_executed": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "certification_performed": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _persist_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        wrapper = {"replay_index": 0, "replay_step": REPLAY_STEP, "artifact": deepcopy(artifact)}
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    except Exception:
        return


def _ensure_replay_available(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError("platform validation candidate composition replay directory must be empty")


def _verify_hash(value: dict[str, Any], field: str, message: str) -> None:
    actual = _require_hash(value.get(field), field)
    expected = deepcopy(value)
    expected.pop(field)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(f"platform validation candidate composition requires canonical {field}")
    return text


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"platform validation candidate composition requires {field}")
    return value.strip()


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "UNAVAILABLE"


def _safe_hash(value: Any) -> str:
    return value if isinstance(value, str) and value.startswith("sha256:") else replay_hash({"unavailable": True})


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__
