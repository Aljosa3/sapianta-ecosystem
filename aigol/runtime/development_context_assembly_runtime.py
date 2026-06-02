"""Deterministic development context assembly runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_task_intake_runtime import (
    AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_ARTIFACT_V1,
    NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME_VERSION = "AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME_V1"
DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1 = "DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1"
CONTEXT_ASSEMBLED = "CONTEXT_ASSEMBLED"
FAILED_CLOSED_MISSING_CONTEXT = "FAILED_CLOSED_MISSING_CONTEXT"
FAILED_CLOSED_AMBIGUOUS_CONTEXT = "FAILED_CLOSED_AMBIGUOUS_CONTEXT"
FAILED_CLOSED_INVALID_INTAKE = "FAILED_CLOSED_INVALID_INTAKE"
FAILED_CLOSED_AUTHORITY_RISK = "FAILED_CLOSED_AUTHORITY_RISK"
PROVIDER_NOT_REQUIRED = "PROVIDER_NOT_REQUIRED"
PROVIDER_REQUIRED_FOR_PROPOSAL = "PROVIDER_REQUIRED_FOR_PROPOSAL"

REPLAY_STEPS = (
    "development_context_assembly_started",
    "development_context_artifacts_resolved",
    "development_context_assembly_validated",
    "development_context_assembly_recorded",
    "development_context_assembly_returned",
)

CORE_CONTEXT_FILES = (
    ("core_governance_context", "AIGOL_CORE_FREEZE_CERTIFICATION.json", True),
    ("core_governance_context", "AIGOL_CORE_FREEZE_V1.md", True),
    ("core_governance_context", "AIGOL_CLI_PRIMARY_INTERFACE_CERTIFICATION.json", True),
    ("native_development_context", "AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_AND_SESSION_RESUME_CERTIFICATION.json", True),
    ("native_development_context", "AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_CERTIFICATION.json", True),
    ("native_development_context", "AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_MODEL_V1.md", True),
    ("native_development_context", "AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_BOUNDARY_GUARANTEES_V1.md", True),
    ("native_development_context", "AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_REPLAY_MODEL_V1.md", True),
    ("cognition_context", "COGNITION_RUNTIME_CERTIFICATION.json", True),
    ("cognition_context", "COGNITION_RUNTIME_COVERAGE_CERTIFICATION.json", True),
    ("cognition_context", "COGNITION_RUNTIME_COVERAGE_GAP_ANALYSIS_V1.md", True),
)

TRADING_CONTEXT_FILES = (
    ("domain_foundation_context", "TRADING_DOMAIN_CERTIFICATION.json", True),
    ("domain_foundation_context", "TRADING_DOMAIN_FOUNDATION_V1.md", True),
    ("domain_foundation_context", "TRADING_DOMAIN_MODEL_V1.md", True),
    ("worker_taxonomy_context", "TRADING_DOMAIN_WORKER_MODEL_V1.md", True),
    ("domain_decision_model_context", "TRADING_DOMAIN_DECISION_VALIDATION_CERTIFICATION.json", True),
    ("domain_decision_model_context", "TRADING_DOMAIN_DECISION_VALIDATION_MODEL_V1.md", True),
    ("domain_decision_model_context", "TRADING_DECISION_ARTIFACT_MODEL_V1.md", True),
    ("policy_and_acceptance_context", "TRADING_DECISION_VALIDATION_ACCEPTANCE_CERTIFICATION.json", True),
    ("policy_and_acceptance_context", "TRADING_DECISION_VALIDATION_ACCEPTANCE_CRITERIA_V1.md", True),
    ("policy_and_acceptance_context", "TRADING_DECISION_POLICY_CONSTRAINT_CERTIFICATION.json", True),
    ("policy_and_acceptance_context", "TRADING_DECISION_VALIDATION_POLICY_CONSTRAINTS_V1.md", True),
    ("policy_and_acceptance_context", "TRADING_POLICY_CONSTRAINT_MODEL_V1.md", True),
    ("fixture_and_test_scenario_context", "TRADING_DECISION_VALIDATION_TEST_FIXTURES_CERTIFICATION.json", True),
    ("fixture_and_test_scenario_context", "TRADING_DECISION_VALIDATION_TEST_FIXTURES_V1.md", True),
    ("fixture_and_test_scenario_context", "TRADING_DECISION_FIXTURE_MODEL_V1.md", True),
    ("fixture_and_test_scenario_context", "TRADING_DECISION_FIXTURE_COVERAGE_V1.md", True),
)

DOMAIN_CONTEXT_FILES = {
    "TRADING": TRADING_CONTEXT_FILES,
}

REQUIRED_CONTEXT_CATEGORIES = (
    "core_governance_context",
    "native_development_context",
    "cognition_context",
    "domain_foundation_context",
    "domain_decision_model_context",
    "policy_and_acceptance_context",
    "fixture_and_test_scenario_context",
    "worker_taxonomy_context",
    "known_gap_context",
    "certification_context",
)

PROHIBITED_INTAKE_FLAGS = (
    "authority",
    "approval_created",
    "execution_requested",
    "dispatch_requested",
    "worker_invoked",
    "domain_created",
    "governance_modified",
    "replay_modified",
)


def assemble_development_context(
    *,
    context_assembly_id: str,
    development_task_intake_artifact: dict[str, Any],
    governance_root: str | Path,
    replay_dir: str | Path,
    created_at: str,
    expected_reference_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Assemble a deterministic context bundle from an accepted native development intake artifact."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        intake = deepcopy(development_task_intake_artifact)
        _validate_intake(intake)
        started = _started_artifact(
            context_assembly_id=context_assembly_id,
            intake=intake,
            governance_root=governance_root,
            created_at=created_at,
        )
        resolved = _resolved_artifact(
            context_assembly_id=context_assembly_id,
            intake=intake,
            governance_root=Path(governance_root),
            created_at=created_at,
            expected_reference_hashes=expected_reference_hashes or {},
        )
        validated = _validated_artifact(
            context_assembly_id=context_assembly_id,
            intake=intake,
            resolved=resolved,
            created_at=created_at,
        )
        context_artifact = _context_artifact(
            context_assembly_id=context_assembly_id,
            intake=intake,
            resolved=resolved,
            validated=validated,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        returned = _returned_artifact(context_artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], started)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], resolved)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], validated)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], context_artifact)
        _persist_step(replay_path, 4, REPLAY_STEPS[4], returned)
        return _capture(started, resolved, validated, context_artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        intake = development_task_intake_artifact if isinstance(development_task_intake_artifact, dict) else {}
        failed = _failed_context_artifact(
            context_assembly_id=context_assembly_id,
            intake=intake,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(failed)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], failed)
        _persist_failure_if_possible(replay_path, 4, REPLAY_STEPS[4], returned)
        return _capture(None, None, None, failed, returned, replay_path)


def reconstruct_development_context_assembly_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct development context assembly replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if not path.exists() and index < 3:
            continue
        wrapper = load_json(path)
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("development context assembly replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("development context assembly replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    if len(wrappers) < 2:
        raise FailClosedRuntimeError("development context assembly replay evidence missing")
    recorded = wrappers[-2]["artifact"]
    returned = wrappers[-1]["artifact"]
    if returned.get("context_assembly_reference") != recorded["context_assembly_id"]:
        raise FailClosedRuntimeError("development context assembly replay reference mismatch")
    if returned.get("context_assembly_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("development context assembly replay hash mismatch")
    return {
        "context_assembly_id": recorded["context_assembly_id"],
        "context_status": recorded["context_status"],
        "requested_milestone_id": recorded["requested_milestone_id"],
        "requested_domain": recorded["requested_domain"],
        "requested_worker_family": recorded["requested_worker_family"],
        "artifact_references": deepcopy(recorded["artifact_references"]),
        "missing_context": deepcopy(recorded["missing_context"]),
        "ambiguous_context": deepcopy(recorded["ambiguous_context"]),
        "known_assumptions": deepcopy(recorded["known_assumptions"]),
        "known_gaps": deepcopy(recorded["known_gaps"]),
        "provider_necessity_classification": recorded["provider_necessity_classification"],
        "context_hash": recorded["context_hash"],
        "replay_visible": True,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_intake(intake: dict[str, Any]) -> None:
    if intake.get("artifact_type") != AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_ARTIFACT_V1:
        raise FailClosedRuntimeError("development context assembly failed closed: invalid intake artifact")
    _verify_artifact_hash(intake)
    if intake.get("intake_status") != NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED:
        raise FailClosedRuntimeError("development context assembly failed closed: intake not accepted")
    if intake.get("safe_for_native_development") is not True:
        raise FailClosedRuntimeError("development context assembly failed closed: intake not safe for native development")
    _require_string(intake.get("requested_milestone_id"), "requested_milestone_id")
    _require_string(intake.get("requested_domain"), "requested_domain")
    for flag in PROHIBITED_INTAKE_FLAGS:
        if intake.get(flag) is True:
            raise FailClosedRuntimeError("development context assembly failed closed: intake carries authority")


def _started_artifact(
    *,
    context_assembly_id: str,
    intake: dict[str, Any],
    governance_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "DEVELOPMENT_CONTEXT_ASSEMBLY_STARTED",
        "runtime_version": AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME_VERSION,
        "context_assembly_id": _require_string(context_assembly_id, "context_assembly_id"),
        "development_task_intake_reference": intake["intake_id"],
        "development_task_intake_hash": intake["artifact_hash"],
        "requested_milestone_id": intake["requested_milestone_id"],
        "requested_domain": intake["requested_domain"],
        "requested_worker_family": intake.get("requested_worker_family"),
        "governance_root": str(Path(governance_root)),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _resolved_artifact(
    *,
    context_assembly_id: str,
    intake: dict[str, Any],
    governance_root: Path,
    created_at: str,
    expected_reference_hashes: dict[str, str],
) -> dict[str, Any]:
    references: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for category, filename, required in _required_context_files(intake):
        path = governance_root / filename
        if not path.exists():
            missing.append(_missing_context(category=category, filename=filename, required=required, reason="artifact does not exist"))
            continue
        if not path.is_file():
            missing.append(_missing_context(category=category, filename=filename, required=required, reason="artifact is not a file"))
            continue
        ref = _artifact_reference(category=category, path=path, governance_root=governance_root, required=required)
        expected_hash = expected_reference_hashes.get(ref["artifact_id"]) or expected_reference_hashes.get(ref["artifact_path"])
        if expected_hash is not None and expected_hash != ref["artifact_hash"]:
            raise FailClosedRuntimeError("development context assembly failed closed: reference hash mismatch")
        references.append(ref)
    duplicate_ids = sorted({ref["artifact_id"] for ref in references if _count_reference_id(references, ref["artifact_id"]) > 1})
    for artifact_id in duplicate_ids:
        ambiguous.append(
            {
                "category": "artifact_reference",
                "candidate_references": [ref["artifact_path"] for ref in references if ref["artifact_id"] == artifact_id],
                "ambiguity_reason": "duplicate artifact id",
                "fail_closed_impact": True,
            }
        )
    references = sorted(references, key=lambda ref: (ref["category"], ref["artifact_id"], ref["artifact_path"], ref["artifact_hash"]))
    artifact = {
        "artifact_type": "DEVELOPMENT_CONTEXT_ARTIFACTS_RESOLVED",
        "runtime_version": AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME_VERSION,
        "context_assembly_id": _require_string(context_assembly_id, "context_assembly_id"),
        "development_task_intake_reference": intake["intake_id"],
        "development_task_intake_hash": intake["artifact_hash"],
        "artifact_references": references,
        "missing_context": missing,
        "ambiguous_context": ambiguous,
        "resolved_reference_count": len(references),
        "missing_context_count": len(missing),
        "ambiguous_context_count": len(ambiguous),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validated_artifact(
    *,
    context_assembly_id: str,
    intake: dict[str, Any],
    resolved: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    missing_required = [entry for entry in resolved["missing_context"] if entry["required"] is True]
    ambiguous = list(resolved["ambiguous_context"])
    if missing_required:
        context_status = FAILED_CLOSED_MISSING_CONTEXT
        failure_reason = "development context assembly failed closed: required context is missing"
    elif ambiguous:
        context_status = FAILED_CLOSED_AMBIGUOUS_CONTEXT
        failure_reason = "development context assembly failed closed: ambiguous context"
    else:
        context_status = CONTEXT_ASSEMBLED
        failure_reason = None
    provider_necessity = _provider_necessity_classification(intake, context_status)
    artifact = {
        "artifact_type": "DEVELOPMENT_CONTEXT_ASSEMBLY_VALIDATED",
        "runtime_version": AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME_VERSION,
        "context_assembly_id": _require_string(context_assembly_id, "context_assembly_id"),
        "development_task_intake_reference": intake["intake_id"],
        "development_task_intake_hash": intake["artifact_hash"],
        "context_status": context_status,
        "missing_context_status": "MISSING_REQUIRED_CONTEXT" if missing_required else "NO_MISSING_REQUIRED_CONTEXT",
        "ambiguity_status": "AMBIGUOUS_CONTEXT" if ambiguous else "UNAMBIGUOUS_CONTEXT",
        "provider_necessity_classification": provider_necessity,
        "provider_context_allowed": context_status == CONTEXT_ASSEMBLED,
        "proposal_generation_allowed": False,
        "failure_reason": failure_reason,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _context_artifact(
    *,
    context_assembly_id: str,
    intake: dict[str, Any],
    resolved: dict[str, Any],
    validated: dict[str, Any],
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    known_gaps = _known_gaps()
    known_assumptions = _known_assumptions(intake)
    known_constraints = sorted(set(intake.get("explicit_constraints", [])))
    context_hash_input = {
        "development_task_intake_hash": intake["artifact_hash"],
        "artifact_references": resolved["artifact_references"],
        "required_context_categories": list(REQUIRED_CONTEXT_CATEGORIES),
        "missing_context": resolved["missing_context"],
        "ambiguous_context": resolved["ambiguous_context"],
        "known_gaps": known_gaps,
        "provider_necessity_classification": validated["provider_necessity_classification"],
        "context_status": validated["context_status"],
    }
    artifact = {
        "artifact_type": DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
        "runtime_version": AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME_VERSION,
        "context_assembly_id": _require_string(context_assembly_id, "context_assembly_id"),
        "development_task_intake_reference": intake["intake_id"],
        "development_task_intake_hash": intake["artifact_hash"],
        "requested_milestone_id": intake["requested_milestone_id"],
        "requested_domain": intake["requested_domain"],
        "requested_worker_family": intake.get("requested_worker_family"),
        "requested_output_scope": deepcopy(intake.get("requested_output_scope", [])),
        "task_kind": intake["task_kind"],
        "context_status": validated["context_status"],
        "artifact_references": deepcopy(resolved["artifact_references"]),
        "required_context_categories": list(REQUIRED_CONTEXT_CATEGORIES),
        "missing_context": deepcopy(resolved["missing_context"]),
        "ambiguous_context": deepcopy(resolved["ambiguous_context"]),
        "known_constraints": known_constraints,
        "known_assumptions": known_assumptions,
        "known_gaps": known_gaps,
        "provider_necessity_classification": validated["provider_necessity_classification"],
        "provider_context_allowed": validated["provider_context_allowed"],
        "proposal_generation_allowed": False,
        "context_hash": replay_hash(context_hash_input),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "provider_invoked": False,
        "failure_reason": validated["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_context_artifact(
    *,
    context_assembly_id: str,
    intake: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    status = FAILED_CLOSED_INVALID_INTAKE
    if "authority" in failure_reason:
        status = FAILED_CLOSED_AUTHORITY_RISK
    artifact = {
        "artifact_type": DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
        "runtime_version": AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME_VERSION,
        "context_assembly_id": _require_string(context_assembly_id, "context_assembly_id"),
        "development_task_intake_reference": intake.get("intake_id"),
        "development_task_intake_hash": intake.get("artifact_hash"),
        "requested_milestone_id": intake.get("requested_milestone_id"),
        "requested_domain": intake.get("requested_domain"),
        "requested_worker_family": intake.get("requested_worker_family"),
        "requested_output_scope": deepcopy(intake.get("requested_output_scope", [])),
        "task_kind": intake.get("task_kind"),
        "context_status": status,
        "artifact_references": [],
        "required_context_categories": list(REQUIRED_CONTEXT_CATEGORIES),
        "missing_context": [],
        "ambiguous_context": [],
        "known_constraints": deepcopy(intake.get("explicit_constraints", [])),
        "known_assumptions": [],
        "known_gaps": _known_gaps(),
        "provider_necessity_classification": PROVIDER_NOT_REQUIRED,
        "provider_context_allowed": False,
        "proposal_generation_allowed": False,
        "context_hash": replay_hash({"failure_reason": failure_reason, "intake_hash": intake.get("artifact_hash")}),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "provider_invoked": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(context_artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(context_artifact)
    returned = {
        "event_type": "DEVELOPMENT_CONTEXT_ASSEMBLY_RETURNED",
        "context_assembly_reference": context_artifact["context_assembly_id"],
        "context_assembly_hash": context_artifact["artifact_hash"],
        "context_status": context_artifact["context_status"],
        "context_hash": context_artifact["context_hash"],
        "missing_context_status": "MISSING_CONTEXT" if context_artifact["missing_context"] else "NO_MISSING_CONTEXT",
        "ambiguity_status": "AMBIGUOUS_CONTEXT" if context_artifact["ambiguous_context"] else "UNAMBIGUOUS_CONTEXT",
        "provider_necessity_classification": context_artifact["provider_necessity_classification"],
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "failure_reason": context_artifact["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(
    started: dict[str, Any] | None,
    resolved: dict[str, Any] | None,
    validated: dict[str, Any] | None,
    context_artifact: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "development_context_assembly_started": deepcopy(started),
        "development_context_artifacts_resolved": deepcopy(resolved),
        "development_context_assembly_validated": deepcopy(validated),
        "development_context_assembly_artifact": deepcopy(context_artifact),
        "development_context_assembly_returned": deepcopy(returned),
        "development_context_assembly_replay_reference": str(replay_path),
        "context_status": context_artifact["context_status"],
        "requested_milestone_id": context_artifact["requested_milestone_id"],
        "requested_domain": context_artifact["requested_domain"],
        "requested_worker_family": context_artifact["requested_worker_family"],
        "artifact_references": deepcopy(context_artifact["artifact_references"]),
        "reference_hashes": {
            reference["artifact_id"]: reference["artifact_hash"] for reference in context_artifact["artifact_references"]
        },
        "context_hash": context_artifact["context_hash"],
        "missing_context": deepcopy(context_artifact["missing_context"]),
        "ambiguous_context": deepcopy(context_artifact["ambiguous_context"]),
        "known_assumptions": deepcopy(context_artifact["known_assumptions"]),
        "known_gaps": deepcopy(context_artifact["known_gaps"]),
        "provider_necessity_classification": context_artifact["provider_necessity_classification"],
        "fail_closed": context_artifact["context_status"] != CONTEXT_ASSEMBLED,
        "failure_reason": context_artifact["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["development_context_assembly_capture_hash"] = replay_hash(capture)
    return capture


def _required_context_files(intake: dict[str, Any]) -> tuple[tuple[str, str, bool], ...]:
    domain = _require_string(intake.get("requested_domain"), "requested_domain").upper()
    if domain not in DOMAIN_CONTEXT_FILES:
        raise FailClosedRuntimeError("development context assembly failed closed: unsupported domain context")
    return tuple(CORE_CONTEXT_FILES) + tuple(DOMAIN_CONTEXT_FILES[domain])


def _artifact_reference(*, category: str, path: Path, governance_root: Path, required: bool) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    rel_path = path.relative_to(governance_root).as_posix()
    artifact_id = path.stem
    return {
        "category": category,
        "artifact_id": artifact_id,
        "artifact_path": rel_path,
        "artifact_hash": replay_hash({"artifact_path": rel_path, "content": content}),
        "required": required,
        "content_length": len(content),
    }


def _missing_context(*, category: str, filename: str, required: bool, reason: str) -> dict[str, Any]:
    return {
        "category": category,
        "expected_artifact": filename,
        "required": required,
        "fail_closed_impact": required,
        "reason_missing": reason,
    }


def _provider_necessity_classification(intake: dict[str, Any], context_status: str) -> str:
    if context_status != CONTEXT_ASSEMBLED:
        return PROVIDER_NOT_REQUIRED
    task_kind = _require_string(intake.get("task_kind"), "task_kind")
    if "WORKER" in task_kind or "RUNTIME" in task_kind or "CLI" in task_kind:
        return PROVIDER_REQUIRED_FOR_PROPOSAL
    return PROVIDER_NOT_REQUIRED


def _known_assumptions(intake: dict[str, Any]) -> list[str]:
    assumptions = [
        f"target milestone is {intake['requested_milestone_id']}",
        f"target domain is {intake['requested_domain']}",
    ]
    worker_family = intake.get("requested_worker_family")
    if worker_family:
        assumptions.append(f"target worker family is {worker_family}")
    task_kind = intake.get("task_kind")
    if task_kind:
        assumptions.append(f"task kind is {task_kind}")
    return assumptions


def _known_gaps() -> list[str]:
    return [
        "domain and worker resolution registry runtime remains missing",
        "provider necessity policy runtime remains missing",
        "development proposal contract remains missing",
        "conversation-to-implementation governed handoff remains missing",
    ]


def _count_reference_id(references: list[dict[str, Any]], artifact_id: str) -> int:
    return sum(1 for reference in references if reference["artifact_id"] == artifact_id)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("development context assembly replay step ordering mismatch")
    _verify_artifact_hash(artifact)
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


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("development context assembly artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("development context assembly artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("development context assembly replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("development context assembly replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "development context assembly failed closed"
