"""Bind validated Project Context evidence to the certified semantic lifecycle.

This runtime composes existing Platform Core responsibilities.  It does not
rank capabilities, create canonical capability inputs, invoke G28 directly,
or grant execution authority.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.certified_capability_invocation_binding_runtime import (
    PLATFORM_CHANGE_IMPACT_ANALYSIS,
    PLATFORM_CHANGE_NORMALIZATION,
    PLATFORM_VALIDATION_PLANNING,
    certified_capability_invocation_adapters,
    certified_capability_semantic_descriptors,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    platform_capability_certification_registry,
)
from aigol.runtime.platform_knowledge_runtime import (
    query_platform_knowledge,
    validate_platform_knowledge_response,
)
from aigol.runtime.platform_project_objective_inference import (
    OBJECTIVE_SUFFICIENT,
    validate_platform_project_objective,
)
from aigol.runtime.semantic_capability_invocation_lifecycle_runtime import (
    LIFECYCLE_COMPLETED,
    reconstruct_semantic_capability_invocation_lifecycle_replay,
    run_semantic_capability_invocation_lifecycle,
)
from aigol.runtime.semantic_capability_selection_runtime import (
    CAPABILITY_SELECTED,
    reconstruct_semantic_capability_selection_replay,
    select_semantic_capability,
    validate_semantic_capability_selection_artifact,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_VERSION = (
    "G29_06_CANONICAL_PROJECT_CONTEXT_TO_SEMANTIC_CAPABILITY_RUNTIME_ROUTE_V1"
)
PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_ARTIFACT_V1 = (
    "PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_ARTIFACT_V1"
)

ROUTE_NOT_ELIGIBLE = "SEMANTIC_CAPABILITY_ROUTE_NOT_ELIGIBLE"
ROUTE_CLARIFICATION_REQUIRED = "SEMANTIC_CAPABILITY_ROUTE_CLARIFICATION_REQUIRED"
ROUTE_COMPLETED = "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
ROUTE_FAILED_CLOSED = "SEMANTIC_CAPABILITY_ROUTE_FAILED_CLOSED"

NON_MUTATING_WORK_TYPES = frozenset({
    "AUDIT_ONLY",
    "ANALYSIS",
    "CERTIFICATION",
    "REVIEW",
})

ROUTE_BOUNDARY_FLAGS = {
    "platform_core_authority": True,
    "human_interface_authority": False,
    "selection_treated_as_authorization": False,
    "authorizes_execution": False,
    "invokes_g28_directly": False,
    "creates_capability_inputs": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "repository_mutated": False,
    "replay_visible": True,
}


def semantic_capability_route_eligible(
    project_objective_artifact: dict[str, Any],
) -> bool:
    """Return whether objective evidence belongs to the bounded G29 adapter scope."""

    objective = validate_platform_project_objective(project_objective_artifact)
    if objective.get("objective_status") != OBJECTIVE_SUFFICIENT:
        return False
    if str(objective.get("requested_work_type") or "") not in NON_MUTATING_WORK_TYPES:
        return False
    text = " ".join(str(objective.get("source_request") or "").lower().split())
    clauses = [clause.strip() for clause in re.split(r"[.!?;\n]+", text) if clause.strip()]
    for capability_id, descriptor in sorted(
        certified_capability_semantic_descriptors().items()
    ):
        exact_identifier = capability_id.lower().replace("_", " ")
        objective_match = any(
            str(phrase).lower() in text for phrase in descriptor["objective_terms"]
        )
        specific_actions = {
            "analyze",
            "analyse",
            "assess",
            "canonicalize",
            "evaluate",
            "normalize",
            "plan",
        }
        action_subject_match = any(
            any(
                str(action).lower() in clause
                for action in descriptor["supported_actions"]
                if str(action).lower() in specific_actions
            )
            and any(
                str(subject).lower() in clause
                for subject in descriptor["supported_subjects"]
            )
            for clause in clauses
        )
        if exact_identifier in text or objective_match or action_subject_match:
            return True
    return False


def run_project_context_semantic_capability_route(
    *,
    session_id: str,
    message: str,
    project_objective_artifact: dict[str, Any],
    project_objective_reference: str,
    explicit_canonical_artifacts: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    created_at: str,
    replay_dir: str | Path,
    workspace_state: dict[str, Any] | None = None,
    candidate_discovery_evidence: dict[str, Any] | None = None,
    invoked_by: str = "PLATFORM_CORE",
) -> dict[str, Any]:
    """Compose G29 selection, explicit input binding, knowledge, and G29-04."""

    path = Path(replay_dir)
    objective: dict[str, Any] | None = None
    selection: dict[str, Any] | None = None
    try:
        session = _require_string(session_id, "session_id")
        query = _require_string(message, "message")
        objective_reference = _require_string(
            project_objective_reference, "project_objective_reference"
        )
        timestamp = _require_string(created_at, "created_at")
        actor = _require_string(invoked_by, "invoked_by")
        objective = validate_platform_project_objective(project_objective_artifact)
        if not semantic_capability_route_eligible(objective):
            return _route_artifact(
                status=ROUTE_NOT_ELIGIBLE,
                session_id=session,
                objective=objective,
                objective_reference=objective_reference,
                selection=None,
                selection_replay_reference=None,
                bound_artifact=None,
                knowledge=None,
                knowledge_reference=None,
                lifecycle=None,
                lifecycle_replay_reference=None,
                presentation=None,
                clarification=None,
                failure_reason=None,
                replay_reference=str(path),
            )

        artifacts = _normalized_explicit_artifacts(explicit_canonical_artifacts)
        registry = platform_capability_certification_registry()
        adapters = certified_capability_invocation_adapters()
        objective_hash = objective["artifact_hash"]
        route_key = objective_hash.split(":", 1)[-1][:20]
        selection_id = f"G29-06-SELECTION-{session}-{route_key}"
        discovery = (
            deepcopy(candidate_discovery_evidence)
            if isinstance(candidate_discovery_evidence, dict)
            else None
        )
        selection_capture = select_semantic_capability(
            selection_id=selection_id,
            session_id=session,
            project_objective_artifact=objective,
            project_objective_reference=objective_reference,
            project_objective_hash=objective_hash,
            certification_registry_state=registry,
            certification_registry_fingerprint=replay_hash(registry),
            invocation_adapter_metadata=adapters,
            invocation_adapter_metadata_fingerprint=replay_hash(adapters),
            available_input_artifact_types=[
                str(artifact.get("artifact_type")) for artifact in artifacts
            ],
            replay_dir=path / "g29_selection",
            candidate_discovery_evidence=discovery,
            candidate_discovery_reference=(
                f"{objective_reference}/candidate-discovery" if discovery else None
            ),
            candidate_discovery_hash=(
                discovery.get("artifact_hash") if discovery else None
            ),
            created_at=timestamp,
        )
        selection = validate_semantic_capability_selection_artifact(
            selection_capture["semantic_capability_selection_artifact"]
        )
        if selection.get("selection_status") != CAPABILITY_SELECTED:
            clarification = selection.get("clarification_artifact")
            route = _route_artifact(
                status=ROUTE_CLARIFICATION_REQUIRED,
                session_id=session,
                objective=objective,
                objective_reference=objective_reference,
                selection=selection,
                selection_replay_reference=str(path / "g29_selection"),
                bound_artifact=None,
                knowledge=None,
                knowledge_reference=None,
                lifecycle=None,
                lifecycle_replay_reference=None,
                presentation=None,
                clarification=clarification,
                failure_reason=selection.get("fail_closed_reason"),
                replay_reference=str(path),
            )
            return _persist_route(path, route)

        compatible = _compatible_artifacts(selection, artifacts)
        if len(compatible) != 1:
            clarification = _artifact_binding_clarification(
                selection=selection,
                compatible_count=len(compatible),
            )
            route = _route_artifact(
                status=ROUTE_CLARIFICATION_REQUIRED,
                session_id=session,
                objective=objective,
                objective_reference=objective_reference,
                selection=selection,
                selection_replay_reference=str(path / "g29_selection"),
                bound_artifact=None,
                knowledge=None,
                knowledge_reference=None,
                lifecycle=None,
                lifecycle_replay_reference=None,
                presentation=None,
                clarification=clarification,
                failure_reason=(
                    "NO_EXPLICIT_COMPATIBLE_CANONICAL_ARTIFACT"
                    if not compatible
                    else "MULTIPLE_EXPLICIT_COMPATIBLE_CANONICAL_ARTIFACTS"
                ),
                replay_reference=str(path),
            )
            return _persist_route(path, route)

        selected = _require_string(
            selection.get("selected_capability_identifier"),
            "selected_capability_identifier",
        )
        bound = compatible[0]
        capability_inputs = _capability_inputs(selected, bound)
        knowledge = validate_platform_knowledge_response(
            query_platform_knowledge(
                query=query,
                capability_identifier=selected,
                workspace_state=workspace_state,
            )
        )
        knowledge_path = path / "platform_knowledge_response.json"
        write_json_immutable(knowledge_path, knowledge)
        knowledge_reference = str(knowledge_path)
        invocation_id = f"G29-06-INVOCATION-{session}-{route_key}"
        lifecycle_capture = run_semantic_capability_invocation_lifecycle(
            invocation_id=invocation_id,
            session_id=session,
            semantic_selection_artifact=selection,
            platform_knowledge_response=knowledge,
            platform_knowledge_response_reference=knowledge_reference,
            capability_inputs=capability_inputs,
            invoked_by=actor,
            invoked_at=timestamp,
            replay_dir=path / "g29_04_lifecycle",
        )
        lifecycle = lifecycle_capture[
            "semantic_capability_invocation_lifecycle_result_artifact"
        ]
        presentation = lifecycle_capture.get("canonical_platform_presentation")
        status = (
            ROUTE_COMPLETED
            if lifecycle_capture.get("lifecycle_status") == LIFECYCLE_COMPLETED
            else ROUTE_FAILED_CLOSED
        )
        route = _route_artifact(
            status=status,
            session_id=session,
            objective=objective,
            objective_reference=objective_reference,
            selection=selection,
            selection_replay_reference=str(path / "g29_selection"),
            bound_artifact=bound,
            knowledge=knowledge,
            knowledge_reference=knowledge_reference,
            lifecycle=lifecycle,
            lifecycle_replay_reference=str(path / "g29_04_lifecycle"),
            presentation=presentation,
            clarification=lifecycle.get("clarification_artifact"),
            failure_reason=lifecycle_capture.get("failure_reason"),
            replay_reference=str(path),
        )
        return _persist_route(path, route)
    except Exception as exc:
        route = _route_artifact(
            status=ROUTE_FAILED_CLOSED,
            session_id=str(session_id or "UNAVAILABLE"),
            objective=objective,
            objective_reference=str(project_objective_reference or "UNAVAILABLE"),
            selection=selection,
            selection_replay_reference=(str(path / "g29_selection") if selection else None),
            bound_artifact=None,
            knowledge=None,
            knowledge_reference=None,
            lifecycle=None,
            lifecycle_replay_reference=None,
            presentation=None,
            clarification=None,
            failure_reason=str(exc),
            replay_reference=str(path),
        )
        return _persist_route(path, route)


def validate_project_context_semantic_capability_route(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("semantic capability route artifact must be an object")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_ARTIFACT_V1:
        raise FailClosedRuntimeError("semantic capability route artifact type mismatch")
    if candidate.get("runtime_version") != PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_VERSION:
        raise FailClosedRuntimeError("semantic capability route version mismatch")
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("semantic capability route artifact hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    if candidate.get("route_status") not in {
        ROUTE_NOT_ELIGIBLE,
        ROUTE_CLARIFICATION_REQUIRED,
        ROUTE_COMPLETED,
        ROUTE_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("semantic capability route status invalid")
    for field, expected in ROUTE_BOUNDARY_FLAGS.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError("semantic capability route boundary invalid")
    if candidate["route_status"] == ROUTE_COMPLETED:
        for field in (
            "project_objective_hash",
            "selection_hash",
            "bound_canonical_artifact_hash",
            "platform_knowledge_response_hash",
            "lifecycle_result_hash",
            "canonical_presentation_hash",
        ):
            _require_hash(candidate.get(field), field)
    if candidate["route_status"] == ROUTE_CLARIFICATION_REQUIRED:
        clarification = candidate.get("clarification_artifact")
        if not isinstance(clarification, dict):
            raise FailClosedRuntimeError("semantic capability route clarification missing")
        questions = clarification.get("clarification_questions")
        if not isinstance(questions, list) or len(questions) != 1:
            raise FailClosedRuntimeError("semantic capability route must ask one question")
    return candidate


def reconstruct_project_context_semantic_capability_route(
    replay_dir: str | Path,
) -> dict[str, Any]:
    path = Path(replay_dir)
    route = validate_project_context_semantic_capability_route(
        load_json(path / "project_context_semantic_capability_route.json")
    )
    if route.get("selection_replay_reference"):
        reconstructed = reconstruct_semantic_capability_selection_replay(
            route["selection_replay_reference"]
        )
        if reconstructed.get("artifact_hash") != route.get("selection_hash"):
            raise FailClosedRuntimeError("semantic capability route selection lineage mismatch")
    if route.get("route_status") == ROUTE_COMPLETED:
        knowledge = validate_platform_knowledge_response(
            load_json(Path(route["platform_knowledge_response_reference"]))
        )
        if knowledge.get("artifact_hash") != route.get("platform_knowledge_response_hash"):
            raise FailClosedRuntimeError("semantic capability route knowledge lineage mismatch")
        if knowledge.get("canonical_capability_identifier") != route.get(
            "selected_capability_identifier"
        ):
            raise FailClosedRuntimeError("semantic capability route knowledge identity mismatch")
        reconstructed = reconstruct_semantic_capability_invocation_lifecycle_replay(
            route["lifecycle_replay_reference"]
        )
        returned = load_json(
            Path(route["lifecycle_replay_reference"])
            / "004_semantic_invocation_lifecycle_returned.json"
        ).get("artifact")
        if not isinstance(returned, dict) or returned.get("artifact_hash") != route.get(
            "lifecycle_result_hash"
        ):
            raise FailClosedRuntimeError("semantic capability route lifecycle lineage mismatch")
        if reconstructed.get("presentation_hash") != route.get("canonical_presentation_hash"):
            raise FailClosedRuntimeError("semantic capability route presentation lineage mismatch")
    return route


def _normalized_explicit_artifacts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError("explicit canonical artifacts must be a sequence")
    artifacts: dict[str, dict[str, Any]] = {}
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("explicit canonical artifact must be an object")
        artifact = deepcopy(item)
        artifact_type = _require_string(artifact.get("artifact_type"), "artifact_type")
        key = str(artifact.get("artifact_hash") or replay_hash(artifact))
        artifacts[f"{artifact_type}:{key}"] = artifact
    return [artifacts[key] for key in sorted(artifacts)]


def _compatible_artifacts(
    selection: dict[str, Any], artifacts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    accepted = set(selection.get("required_canonical_input_artifact_types") or [])
    return [artifact for artifact in artifacts if artifact.get("artifact_type") in accepted]


def _capability_inputs(capability_id: str, artifact: dict[str, Any]) -> dict[str, Any]:
    if capability_id == PLATFORM_CHANGE_NORMALIZATION:
        reference_field = (
            "manifest_id"
            if artifact.get("artifact_type") == "IMPLEMENTATION_MANIFEST_ARTIFACT_V1"
            else "proposal_id"
        )
        return {
            "source_artifact": deepcopy(artifact),
            "source_reference": artifact.get(reference_field),
            "source_hash": artifact.get("artifact_hash"),
        }
    if capability_id == PLATFORM_CHANGE_IMPACT_ANALYSIS:
        return {
            "normalized_change_artifact": deepcopy(artifact),
            "normalized_change_reference": artifact.get("normalization_id"),
            "normalized_change_hash": artifact.get("normalized_change_hash"),
        }
    if capability_id == PLATFORM_VALIDATION_PLANNING:
        return {
            "platform_change_impact_artifact": deepcopy(artifact),
            "platform_change_impact_reference": artifact.get("impact_analysis_id"),
            "platform_change_impact_hash": artifact.get("platform_change_impact_hash"),
        }
    raise FailClosedRuntimeError("selected capability is outside G29-06 scope")


def _artifact_binding_clarification(
    *, selection: dict[str, Any], compatible_count: int
) -> dict[str, Any]:
    if compatible_count == 0:
        question = (
            "Which explicit canonical input artifact should Platform Core bind to the "
            f"selected {selection.get('selected_capability_identifier')} capability?"
        )
        reason = "NO_EXPLICIT_COMPATIBLE_CANONICAL_ARTIFACT"
    else:
        question = (
            "Which one of the compatible canonical input artifacts should Platform Core "
            f"bind to the selected {selection.get('selected_capability_identifier')} capability?"
        )
        reason = "MULTIPLE_EXPLICIT_COMPATIBLE_CANONICAL_ARTIFACTS"
    artifact = {
        "artifact_type": "SEMANTIC_CAPABILITY_ARTIFACT_BINDING_CLARIFICATION_ARTIFACT_V1",
        "runtime_version": PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_VERSION,
        "selection_reference": selection.get("selection_id"),
        "selection_hash": selection.get("artifact_hash"),
        "clarification_authority": "PLATFORM_CORE",
        "clarification_reason": reason,
        "clarification_questions": [question],
        "clarification_question_count": 1,
        "asks_exactly_one_question": True,
        "human_interface_authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _route_artifact(
    *,
    status: str,
    session_id: str,
    objective: dict[str, Any] | None,
    objective_reference: str,
    selection: dict[str, Any] | None,
    selection_replay_reference: str | None,
    bound_artifact: dict[str, Any] | None,
    knowledge: dict[str, Any] | None,
    knowledge_reference: str | None,
    lifecycle: dict[str, Any] | None,
    lifecycle_replay_reference: str | None,
    presentation: dict[str, Any] | None,
    clarification: dict[str, Any] | None,
    failure_reason: Any,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_ARTIFACT_V1,
        "runtime_version": PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_VERSION,
        "route_status": status,
        "session_id": session_id,
        "project_objective_reference": objective_reference,
        "project_objective_hash": objective.get("artifact_hash") if objective else None,
        "selection_reference": selection.get("selection_id") if selection else None,
        "selection_hash": selection.get("artifact_hash") if selection else None,
        "selection_status": selection.get("selection_status") if selection else None,
        "selected_capability_identifier": (
            selection.get("selected_capability_identifier") if selection else None
        ),
        "selection_replay_reference": selection_replay_reference,
        "bound_canonical_artifact_type": (
            bound_artifact.get("artifact_type") if bound_artifact else None
        ),
        "bound_canonical_artifact_hash": (
            bound_artifact.get("artifact_hash") if bound_artifact else None
        ),
        "platform_knowledge_response_reference": knowledge_reference,
        "platform_knowledge_response_hash": (
            knowledge.get("artifact_hash") if knowledge else None
        ),
        "lifecycle_result_hash": lifecycle.get("artifact_hash") if lifecycle else None,
        "lifecycle_status": lifecycle.get("lifecycle_status") if lifecycle else None,
        "lifecycle_replay_reference": lifecycle_replay_reference,
        "canonical_presentation_hash": (
            presentation.get("presentation_hash") if presentation else None
        ),
        "canonical_platform_presentation": deepcopy(presentation),
        "clarification_required": status == ROUTE_CLARIFICATION_REQUIRED,
        "clarification_artifact": deepcopy(clarification),
        "failure_reason": str(failure_reason) if failure_reason else None,
        "replay_reference": replay_reference,
        **ROUTE_BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_project_context_semantic_capability_route(artifact)


def _persist_route(path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    write_json_immutable(
        path / "project_context_semantic_capability_route.json", artifact
    )
    return artifact


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{field_name} must be a sha256 hash")
    return text


__all__ = [
    "PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_ARTIFACT_V1",
    "PROJECT_CONTEXT_SEMANTIC_CAPABILITY_ROUTE_VERSION",
    "ROUTE_CLARIFICATION_REQUIRED",
    "ROUTE_COMPLETED",
    "ROUTE_FAILED_CLOSED",
    "ROUTE_NOT_ELIGIBLE",
    "reconstruct_project_context_semantic_capability_route",
    "run_project_context_semantic_capability_route",
    "semantic_capability_route_eligible",
    "validate_project_context_semantic_capability_route",
]
