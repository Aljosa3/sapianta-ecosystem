"""Compose semantic selection into certified capability invocation and presentation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.certified_capability_invocation_binding_runtime import (
    CERTIFIED_CAPABILITY_INVOCATION_COMPLETED,
    invoke_certified_capability,
    reconstruct_certified_capability_invocation_replay,
    validate_certified_capability_invocation_result_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_knowledge_runtime import validate_platform_knowledge_response
from aigol.runtime.platform_presentation_layer import (
    present_platform_response,
    validate_platform_presentation,
)
from aigol.runtime.semantic_capability_selection_runtime import (
    CAPABILITY_CLARIFICATION_REQUIRED,
    CAPABILITY_SELECTED,
    NO_ADMISSIBLE_CAPABILITY,
    validate_semantic_capability_selection_artifact,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RUNTIME_VERSION = (
    "G29_04_SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RUNTIME_V1"
)
SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RESULT_ARTIFACT_V1 = (
    "SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RESULT_ARTIFACT_V1"
)

LIFECYCLE_COMPLETED = "SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_COMPLETED"
LIFECYCLE_CLARIFICATION_REQUIRED = (
    "SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_CLARIFICATION_REQUIRED"
)
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "semantic_selection_handoff_recorded",
    "g28_invocation_request_recorded",
    "g28_invocation_result_recorded",
    "canonical_presentation_recorded",
    "semantic_invocation_lifecycle_returned",
)

AUTHORITY_FLAGS = {
    "platform_core_authority": True,
    "human_interface_authority": False,
    "selection_treated_as_authorization": False,
    "authorizes_execution": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_repository_mutation": False,
    "invokes_workers": False,
    "invokes_providers": False,
    "mutates_repository": False,
    "uses_dynamic_imports": False,
    "creates_capability_inputs": False,
    "g29_selection_modified": False,
    "g28_invocation_modified": False,
}


def run_semantic_capability_invocation_lifecycle(
    *,
    invocation_id: str,
    session_id: str,
    semantic_selection_artifact: dict[str, Any],
    platform_knowledge_response: dict[str, Any],
    platform_knowledge_response_reference: str,
    capability_inputs: dict[str, Any],
    invoked_by: str,
    invoked_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Bind one valid G29 selection to unchanged G28 and canonical presentation."""

    path = Path(replay_dir)
    selection: dict[str, Any] | None = None
    try:
        _ensure_replay_available(path)
        identifier = _require_string(invocation_id, "invocation_id")
        session = _require_string(session_id, "session_id")
        knowledge_reference = _require_string(
            platform_knowledge_response_reference,
            "platform_knowledge_response_reference",
        )
        actor = _require_string(invoked_by, "invoked_by")
        timestamp = _require_string(invoked_at, "invoked_at")
        selection = validate_semantic_capability_selection_artifact(
            semantic_selection_artifact
        )
        if selection.get("session_id") != session:
            raise FailClosedRuntimeError(
                "semantic invocation lifecycle failed closed: selection session mismatch"
            )
        clarification = _clarification_outcome_if_required(
            invocation_id=identifier,
            session_id=session,
            selection=selection,
            replay_path=path,
        )
        if clarification is not None:
            return clarification
        selected = _validated_selected_capability(selection)
        knowledge = validate_platform_knowledge_response(platform_knowledge_response)
        if knowledge.get("canonical_capability_identifier") != selected:
            raise FailClosedRuntimeError(
                "semantic invocation lifecycle failed closed: Platform Knowledge capability mismatch"
            )
        inputs, input_field_hashes = _validated_capability_inputs(selection, capability_inputs)

        selection_record = _record_artifact(
            "SEMANTIC_CAPABILITY_SELECTION_HANDOFF_ARTIFACT_V1",
            {
                "invocation_id": identifier,
                "session_id": session,
                "selection_reference": selection["selection_id"],
                "selection_hash": selection["artifact_hash"],
                "selected_capability_identifier": selected,
                "semantic_selection_artifact": selection,
            },
        )
        request_record = _record_artifact(
            "CERTIFIED_CAPABILITY_INVOCATION_REQUEST_ARTIFACT_V1",
            {
                "invocation_id": identifier,
                "session_id": session,
                "selection_handoff_hash": selection_record["artifact_hash"],
                "selected_capability_identifier": selected,
                "platform_knowledge_response_reference": knowledge_reference,
                "platform_knowledge_response_hash": knowledge["artifact_hash"],
                "platform_knowledge_response": knowledge,
                "capability_inputs": inputs,
                "capability_inputs_hash": replay_hash(inputs),
                "capability_input_field_hashes": input_field_hashes,
                "required_capability_input_fields": selection[
                    "required_canonical_input_fields"
                ],
                "invoked_by": actor,
                "invoked_at": timestamp,
                "g28_replay_reference": str(path / "g28_invocation"),
            },
        )
        _persist_step(path, 0, REPLAY_STEPS[0], selection_record)
        _persist_step(path, 1, REPLAY_STEPS[1], request_record)

        invocation = invoke_certified_capability(
            invocation_id=identifier,
            session_id=session,
            platform_knowledge_response=knowledge,
            platform_knowledge_response_reference=knowledge_reference,
            discovered_capability_identifier=selected,
            capability_inputs=inputs,
            invoked_by=actor,
            invoked_at=timestamp,
            replay_dir=path / "g28_invocation",
        )
        g28_result = validate_certified_capability_invocation_result_artifact(
            invocation["certified_capability_invocation_result_artifact"]
        )
        if g28_result.get("capability_identifier") != selected:
            raise FailClosedRuntimeError(
                "semantic invocation lifecycle failed closed: selected identifier substitution"
            )
        result_record = _record_artifact(
            "SEMANTIC_SELECTION_BOUND_INVOCATION_RESULT_ARTIFACT_V1",
            {
                "invocation_id": identifier,
                "invocation_request_hash": request_record["artifact_hash"],
                "selected_capability_identifier": selected,
                "g28_invocation_result_reference": g28_result["invocation_id"],
                "g28_invocation_result_hash": g28_result["artifact_hash"],
                "g28_invocation_result": g28_result,
            },
        )
        _persist_step(path, 2, REPLAY_STEPS[2], result_record)

        presentation = validate_platform_presentation(
            present_platform_response(g28_result, created_at=timestamp)
        )
        presentation_record = _record_artifact(
            "CERTIFIED_CAPABILITY_INVOCATION_PRESENTATION_LINEAGE_ARTIFACT_V1",
            {
                "invocation_id": identifier,
                "invocation_result_record_hash": result_record["artifact_hash"],
                "selected_capability_identifier": selected,
                "presentation_reference": presentation["presentation_hash"],
                "presentation_hash": presentation["presentation_hash"],
                "canonical_presentation": presentation,
            },
        )
        _persist_step(path, 3, REPLAY_STEPS[3], presentation_record)

        completed = g28_result["invocation_status"] == CERTIFIED_CAPABILITY_INVOCATION_COMPLETED
        lifecycle = _lifecycle_result(
            invocation_id=identifier,
            session_id=session,
            selection=selection,
            knowledge=knowledge,
            knowledge_reference=knowledge_reference,
            inputs_hash=request_record["capability_inputs_hash"],
            input_field_hashes=input_field_hashes,
            request_hash=request_record["artifact_hash"],
            g28_result=g28_result,
            presentation=presentation,
            status=LIFECYCLE_COMPLETED if completed else FAILED_CLOSED,
            failure_reason=g28_result.get("failure_reason"),
        )
        _persist_step(path, 4, REPLAY_STEPS[4], lifecycle)
        return _capture(lifecycle, presentation, path)
    except Exception as exc:
        failure = _failed_lifecycle_result(
            invocation_id=invocation_id,
            session_id=session_id,
            selection=selection or semantic_selection_artifact,
            knowledge=platform_knowledge_response,
            knowledge_reference=platform_knowledge_response_reference,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(path, failure)
        return _capture(failure, None, path)


def validate_semantic_capability_invocation_lifecycle_result(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one lifecycle result artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("semantic invocation lifecycle result must be an object")
    candidate = deepcopy(artifact)
    _verify_artifact_hash(candidate, "semantic invocation lifecycle result")
    if candidate.get("artifact_type") != (
        SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RESULT_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError("semantic invocation lifecycle result type mismatch")
    if candidate.get("runtime_version") != (
        SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RUNTIME_VERSION
    ):
        raise FailClosedRuntimeError("semantic invocation lifecycle version mismatch")
    if candidate.get("lifecycle_status") not in {
        LIFECYCLE_COMPLETED,
        LIFECYCLE_CLARIFICATION_REQUIRED,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("semantic invocation lifecycle status invalid")
    if candidate.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("semantic invocation lifecycle authority invalid")
    if candidate.get("replay_visible") is not True:
        raise FailClosedRuntimeError("semantic invocation lifecycle must be replay-visible")
    if candidate["lifecycle_status"] == LIFECYCLE_COMPLETED:
        if candidate.get("capability_invoked") is not True:
            raise FailClosedRuntimeError("completed lifecycle must record capability invocation")
        for field in (
            "selection_hash",
            "platform_knowledge_response_hash",
            "capability_inputs_hash",
            "g28_invocation_request_hash",
            "g28_invocation_result_hash",
            "presentation_hash",
        ):
            _require_hash(candidate.get(field), field)
    elif candidate.get("capability_invoked") is not False:
        raise FailClosedRuntimeError("non-completed lifecycle cannot claim capability invocation")
    return candidate


def reconstruct_semantic_capability_invocation_lifecycle_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct and cross-check one completed selection-to-invocation lifecycle."""

    path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("semantic invocation lifecycle replay ordering mismatch")
        _verify_named_hash(wrapper, "replay_hash", "semantic invocation lifecycle replay hash mismatch")
        artifact = wrapper.get("artifact")
        _verify_artifact_hash(artifact, "semantic invocation lifecycle replay artifact")
        wrappers.append(wrapper)
        artifacts.append(artifact)

    selection_record, request, result_record, presentation_record, lifecycle = artifacts
    selection = validate_semantic_capability_selection_artifact(
        selection_record.get("semantic_selection_artifact")
    )
    knowledge = validate_platform_knowledge_response(request.get("platform_knowledge_response"))
    g28_result = validate_certified_capability_invocation_result_artifact(
        result_record.get("g28_invocation_result")
    )
    presentation = validate_platform_presentation(
        presentation_record.get("canonical_presentation")
    )
    validated = validate_semantic_capability_invocation_lifecycle_result(lifecycle)
    selected = selection.get("selected_capability_identifier")
    capability_ids = {
        selected,
        selection_record.get("selected_capability_identifier"),
        request.get("selected_capability_identifier"),
        knowledge.get("canonical_capability_identifier"),
        result_record.get("selected_capability_identifier"),
        g28_result.get("capability_identifier"),
        presentation_record.get("selected_capability_identifier"),
        validated.get("selected_capability_identifier"),
    }
    if len(capability_ids) != 1 or None in capability_ids:
        raise FailClosedRuntimeError("semantic invocation lifecycle capability lineage mismatch")
    if selection_record.get("selection_hash") != selection["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle selection linkage mismatch")
    if request.get("selection_handoff_hash") != selection_record["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle request lineage mismatch")
    if request.get("platform_knowledge_response_hash") != knowledge["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle knowledge linkage mismatch")
    inputs = request.get("capability_inputs")
    if not isinstance(inputs, dict) or request.get("capability_inputs_hash") != replay_hash(inputs):
        raise FailClosedRuntimeError("semantic invocation lifecycle input hash mismatch")
    if request.get("capability_input_field_hashes") != _input_field_hashes(inputs):
        raise FailClosedRuntimeError("semantic invocation lifecycle input evidence mismatch")
    if result_record.get("invocation_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle invocation lineage mismatch")
    if result_record.get("g28_invocation_result_hash") != g28_result["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle G28 result mismatch")
    if g28_result.get("invocation_id") != request.get("invocation_id"):
        raise FailClosedRuntimeError("semantic invocation lifecycle invocation identity mismatch")
    if g28_result.get("session_id") != request.get("session_id"):
        raise FailClosedRuntimeError("semantic invocation lifecycle session lineage mismatch")
    if g28_result.get("platform_knowledge_response_reference") != request.get(
        "platform_knowledge_response_reference"
    ):
        raise FailClosedRuntimeError("semantic invocation lifecycle knowledge reference mismatch")
    if g28_result.get("platform_knowledge_response_hash") != knowledge["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle G28 knowledge mismatch")
    if presentation_record.get("invocation_result_record_hash") != result_record["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle presentation lineage mismatch")
    if presentation_record.get("presentation_hash") != presentation["presentation_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle presentation hash mismatch")
    if presentation.get("source_response_hash") != g28_result["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle presentation source mismatch")
    if presentation.get("answer", {}).get("selected_capability_identifier") != selected:
        raise FailClosedRuntimeError("semantic invocation lifecycle presentation capability mismatch")
    expected = {
        "selection_hash": selection["artifact_hash"],
        "platform_knowledge_response_hash": knowledge["artifact_hash"],
        "capability_inputs_hash": request["capability_inputs_hash"],
        "g28_invocation_request_hash": request["artifact_hash"],
        "g28_invocation_result_hash": g28_result["artifact_hash"],
        "presentation_hash": presentation["presentation_hash"],
    }
    if any(validated.get(field) != value for field, value in expected.items()):
        raise FailClosedRuntimeError("semantic invocation lifecycle returned lineage mismatch")
    reconstructed_g28 = reconstruct_certified_capability_invocation_replay(
        path / "g28_invocation"
    )
    if reconstructed_g28.get("artifact_hash") != g28_result["artifact_hash"]:
        raise FailClosedRuntimeError("semantic invocation lifecycle G28 replay mismatch")
    return {
        "invocation_id": validated["invocation_id"],
        "session_id": validated["session_id"],
        "lifecycle_status": validated["lifecycle_status"],
        "selected_capability_identifier": selected,
        "selection_hash": selection["artifact_hash"],
        "g28_invocation_result_hash": g28_result["artifact_hash"],
        "presentation_hash": presentation["presentation_hash"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "replay_visible": True,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "human_interface_authority": False,
    }


def _clarification_outcome_if_required(
    *,
    invocation_id: str,
    session_id: str,
    selection: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any] | None:
    if selection.get("selection_status") not in {
        CAPABILITY_CLARIFICATION_REQUIRED,
        NO_ADMISSIBLE_CAPABILITY,
    }:
        return None
    lifecycle = _failed_lifecycle_result(
        invocation_id=invocation_id,
        session_id=session_id,
        selection=selection,
        knowledge={},
        knowledge_reference=None,
        failure_reason=str(
            selection.get("fail_closed_reason") or "semantic capability clarification required"
        ),
        status=LIFECYCLE_CLARIFICATION_REQUIRED,
    )
    _persist_failure_if_possible(replay_path, lifecycle)
    return _capture(lifecycle, None, replay_path)


def _validated_selected_capability(selection: dict[str, Any]) -> str:
    if selection.get("selection_status") != CAPABILITY_SELECTED:
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: selected capability required"
        )
    if selection.get("invocation_eligible") is not True:
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: invocation eligibility required"
        )
    if selection.get("clarification_required") is not False:
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: clarification cannot invoke"
        )
    if selection.get("ready_for_g28_invocation") is not True:
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: G28 readiness required"
        )
    _require_string(selection.get("selection_id"), "selection_id")
    _require_string(
        selection.get("project_objective_reference"),
        "project_objective_reference",
    )
    for field in (
        "project_objective_hash",
        "certification_registry_fingerprint",
        "invocation_adapter_metadata_fingerprint",
        "semantic_descriptor_fingerprint",
        "objective_source_record_hash",
        "candidate_set_record_hash",
        "scoring_evidence_record_hash",
        "classification_record_hash",
    ):
        _require_hash(selection.get(field), field)
    discovery_reference = selection.get("candidate_discovery_reference")
    discovery_hash = selection.get("candidate_discovery_hash")
    if discovery_reference is not None or discovery_hash is not None:
        _require_string(discovery_reference, "candidate_discovery_reference")
        _require_hash(discovery_hash, "candidate_discovery_hash")
    selected = _require_string(
        selection.get("selected_capability_identifier"),
        "selected_capability_identifier",
    )
    candidates = selection.get("ordered_candidate_records")
    if not isinstance(candidates, list):
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: candidate evidence required"
        )
    matching = [
        item
        for item in candidates
        if isinstance(item, dict)
        and item.get("capability_identifier") == selected
        and item.get("admissible") is True
        and item.get("invocation_eligible") is True
    ]
    if len(matching) != 1:
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: exactly one selected candidate required"
        )
    fields = selection.get("required_canonical_input_fields")
    if not isinstance(fields, list) or not fields or any(
        not isinstance(field, str) or not field.strip() for field in fields
    ):
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: G28 input schema required"
        )
    if len(fields) != len(set(fields)) or fields != matching[0].get(
        "required_canonical_input_fields"
    ):
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: G28 input schema mismatch"
        )
    return selected


def _validated_capability_inputs(
    selection: dict[str, Any], inputs: Any
) -> tuple[dict[str, Any], dict[str, str]]:
    if not isinstance(inputs, dict):
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: concrete capability inputs required"
        )
    concrete = deepcopy(inputs)
    required = set(selection["required_canonical_input_fields"])
    missing = sorted(required - set(concrete))
    extra = sorted(set(concrete) - required)
    if missing:
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: missing concrete input: "
            + ", ".join(missing)
        )
    if extra:
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: undeclared concrete input: "
            + ", ".join(extra)
        )
    artifact_fields = [field for field in concrete if field.endswith("_artifact") or field == "source_artifact"]
    if len(artifact_fields) != 1 or not isinstance(concrete[artifact_fields[0]], dict):
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: one concrete canonical artifact required"
        )
    artifact_type = concrete[artifact_fields[0]].get("artifact_type")
    if artifact_type not in selection.get("required_canonical_input_artifact_types", []):
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: concrete artifact type mismatch"
        )
    return concrete, _input_field_hashes(concrete)


def _input_field_hashes(inputs: dict[str, Any]) -> dict[str, str]:
    return {field: replay_hash(inputs[field]) for field in sorted(inputs)}


def _lifecycle_result(
    *,
    invocation_id: str,
    session_id: str,
    selection: dict[str, Any],
    knowledge: dict[str, Any],
    knowledge_reference: str,
    inputs_hash: str,
    input_field_hashes: dict[str, str],
    request_hash: str,
    g28_result: dict[str, Any],
    presentation: dict[str, Any],
    status: str,
    failure_reason: Any,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RESULT_ARTIFACT_V1,
        "runtime_version": SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RUNTIME_VERSION,
        "invocation_id": invocation_id,
        "session_id": session_id,
        "lifecycle_status": status,
        "selection_reference": selection["selection_id"],
        "selection_hash": selection["artifact_hash"],
        "selected_capability_identifier": selection["selected_capability_identifier"],
        "platform_knowledge_response_reference": knowledge_reference,
        "platform_knowledge_response_hash": knowledge["artifact_hash"],
        "capability_inputs_hash": inputs_hash,
        "capability_input_field_hashes": deepcopy(input_field_hashes),
        "g28_invocation_request_reference": invocation_id,
        "g28_invocation_request_hash": request_hash,
        "g28_invocation_result_reference": g28_result["invocation_id"],
        "g28_invocation_result_hash": g28_result["artifact_hash"],
        "presentation_reference": presentation["presentation_hash"],
        "presentation_hash": presentation["presentation_hash"],
        "invocation_status": g28_result["invocation_status"],
        "capability_invoked": g28_result["capability_invoked"],
        "clarification_required": False,
        "clarification_artifact": None,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "human_interface_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_semantic_capability_invocation_lifecycle_result(artifact)


def _failed_lifecycle_result(
    *,
    invocation_id: Any,
    session_id: Any,
    selection: Any,
    knowledge: Any,
    knowledge_reference: Any,
    failure_reason: str,
    status: str = FAILED_CLOSED,
) -> dict[str, Any]:
    selected = selection if isinstance(selection, dict) else {}
    discovery = knowledge if isinstance(knowledge, dict) else {}
    clarification = selected.get("clarification_artifact")
    artifact = {
        "artifact_type": SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RESULT_ARTIFACT_V1,
        "runtime_version": SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RUNTIME_VERSION,
        "invocation_id": _safe_string(invocation_id),
        "session_id": _safe_string(session_id),
        "lifecycle_status": status,
        "selection_reference": selected.get("selection_id"),
        "selection_hash": _safe_hash(selected.get("artifact_hash")),
        "selected_capability_identifier": selected.get("selected_capability_identifier"),
        "platform_knowledge_response_reference": _safe_optional_string(knowledge_reference),
        "platform_knowledge_response_hash": _safe_hash(discovery.get("artifact_hash")),
        "capability_inputs_hash": None,
        "capability_input_field_hashes": {},
        "g28_invocation_request_reference": None,
        "g28_invocation_request_hash": None,
        "g28_invocation_result_reference": None,
        "g28_invocation_result_hash": None,
        "presentation_reference": None,
        "presentation_hash": None,
        "invocation_status": None,
        "capability_invoked": False,
        "clarification_required": status == LIFECYCLE_CLARIFICATION_REQUIRED,
        "clarification_artifact": deepcopy(clarification) if isinstance(clarification, dict) else None,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "human_interface_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_semantic_capability_invocation_lifecycle_result(artifact)


def _record_artifact(artifact_type: str, fields: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": artifact_type,
        "runtime_version": SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RUNTIME_VERSION,
        **deepcopy(fields),
        "replay_visible": True,
        "human_interface_authority": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    result: dict[str, Any],
    presentation: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RUNTIME_VERSION,
        "invocation_id": result["invocation_id"],
        "session_id": result["session_id"],
        "lifecycle_status": result["lifecycle_status"],
        "selected_capability_identifier": result["selected_capability_identifier"],
        "semantic_capability_invocation_lifecycle_result_artifact": deepcopy(result),
        "canonical_platform_presentation": deepcopy(presentation),
        "lifecycle_replay_reference": str(replay_path),
        "capability_invoked": result["capability_invoked"],
        "clarification_required": result["clarification_required"],
        "fail_closed": result["lifecycle_status"] != LIFECYCLE_COMPLETED,
        "failure_reason": result["failure_reason"],
        "replay_visible": True,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "human_interface_authority": False,
        "dynamic_import_used": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(path: Path, result: dict[str, Any]) -> None:
    try:
        _persist_step(path, 4, REPLAY_STEPS[4], result)
    except Exception:
        return


def _ensure_replay_available(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError(
            "semantic invocation lifecycle failed closed: replay directory is not empty"
        )


def _verify_artifact_hash(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be an object")
    _verify_named_hash(artifact, "artifact_hash", f"{label} hash mismatch")


def _verify_named_hash(artifact: dict[str, Any], field: str, message: str) -> None:
    actual = _require_hash(artifact.get(field), field)
    body = deepcopy(artifact)
    body.pop(field, None)
    if replay_hash(body) != actual:
        raise FailClosedRuntimeError(message)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"semantic invocation lifecycle requires {field}")
    return value.strip()


def _require_hash(value: Any, field: str) -> str:
    token = _require_string(value, field)
    if not token.startswith("sha256:"):
        raise FailClosedRuntimeError(f"semantic invocation lifecycle requires valid {field}")
    return token


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "INVALID"


def _safe_optional_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _safe_hash(value: Any) -> str | None:
    return value if isinstance(value, str) and value.startswith("sha256:") else None


def _failure_reason(exc: Exception) -> str:
    return str(exc) if isinstance(exc, FailClosedRuntimeError) else f"unexpected failure: {exc}"


__all__ = [
    "FAILED_CLOSED",
    "LIFECYCLE_CLARIFICATION_REQUIRED",
    "LIFECYCLE_COMPLETED",
    "SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RESULT_ARTIFACT_V1",
    "SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_RUNTIME_VERSION",
    "reconstruct_semantic_capability_invocation_lifecycle_replay",
    "run_semantic_capability_invocation_lifecycle",
    "validate_semantic_capability_invocation_lifecycle_result",
]
