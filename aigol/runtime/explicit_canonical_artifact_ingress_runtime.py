"""Bounded explicit canonical artifact ingress for Platform Core.

The runtime resolves only caller-supplied Replay wrapper references.  It does
not discover artifacts, interpret request text, select capabilities, or grant
execution authority.
"""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path, PurePath
from typing import Any

from aigol.runtime.certified_capability_invocation_binding_runtime import (
    certified_capability_invocation_adapters,
)
from aigol.runtime.implementation_manifest_runtime import (
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1,
    validate_platform_capability_composition_coverage_request,
)
from aigol.runtime.platform_change_impact_analysis_runtime import (
    PLATFORM_CHANGE_IMPACT_ARTIFACT_V1,
    validate_platform_change_impact_artifact,
)
from aigol.runtime.platform_change_normalization_runtime import (
    NORMALIZED_CHANGE_ARTIFACT_V1,
    validate_normalized_change_artifact,
)
from aigol.runtime.product1_decision_validation_packet_certification_v1 import (
    PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1,
    validate_product1_decision_validation_request,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


EXPLICIT_CANONICAL_ARTIFACT_INGRESS_VERSION = (
    "G29_08_EXPLICIT_CANONICAL_ARTIFACT_INGRESS_BINDING_V1"
)
EXPLICIT_CANONICAL_ARTIFACT_INGRESS_ARTIFACT_V1 = (
    "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_ARTIFACT_V1"
)
EXPLICIT_CANONICAL_ARTIFACT_INGRESS_LINK_ARTIFACT_V1 = (
    "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_LINK_ARTIFACT_V1"
)
INGRESS_COMPLETED = "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_COMPLETED"
INGRESS_FAILED_CLOSED = "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_FAILED_CLOSED"

REPLAY_STEPS = (
    "explicit_artifact_ingress_received",
    "explicit_artifact_ingress_resolved",
    "explicit_artifact_ingress_downstream_linked",
)

BOUNDARY_FLAGS = {
    "platform_core_validation_authority": True,
    "human_interface_authority": False,
    "semantic_selection_performed": False,
    "capability_invoked": False,
    "execution_authorized": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "repository_mutated": False,
    "replay_visible": True,
}


def run_explicit_canonical_artifact_ingress(
    *,
    ingress_id: str,
    session_id: str,
    opaque_artifact_references: list[Any] | tuple[Any, ...],
    runtime_root: str | Path,
    workspace: str | Path,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Resolve explicit Replay wrappers into validated canonical artifacts."""

    path = Path(replay_dir)
    received: dict[str, Any] | None = None
    try:
        ingress = _require_string(ingress_id, "ingress_id")
        session = _require_string(session_id, "session_id")
        timestamp = _require_string(created_at, "created_at")
        references = _normalized_reference_records(opaque_artifact_references)
        received = _received_artifact(
            ingress_id=ingress,
            session_id=session,
            references=references,
            created_at=timestamp,
        )
        _persist_step(path, 0, received)
        supplied_paths = [record["artifact_reference"] for record in references]
        if len(supplied_paths) != len(set(supplied_paths)):
            raise FailClosedRuntimeError(
                "explicit canonical artifact ingress duplicate reference"
            )

        roots = _allowed_roots(runtime_root=runtime_root, workspace=workspace)
        resolved_records: list[dict[str, Any]] = []
        artifacts: list[dict[str, Any]] = []
        resolved_paths: set[str] = set()
        for reference in references:
            resolved = _resolve_reference(reference, roots=roots, workspace=Path(workspace))
            resolved_path = resolved["resolved_reference"]
            if resolved_path in resolved_paths:
                raise FailClosedRuntimeError(
                    "explicit canonical artifact ingress duplicate or ambiguous reference"
                )
            resolved_paths.add(resolved_path)
            resolved_records.append(resolved)
            artifacts.append(deepcopy(resolved["validated_artifact"]))

        result = _resolution_artifact(
            ingress_id=ingress,
            session_id=session,
            received=received,
            status=INGRESS_COMPLETED,
            resolved_records=resolved_records,
            failure_reason=None,
            replay_reference=str(path),
        )
        _persist_step(path, 1, result)
        return _capture(result=result, artifacts=artifacts, replay_dir=path)
    except Exception as exc:
        result = _resolution_artifact(
            ingress_id=_safe_string(ingress_id),
            session_id=_safe_string(session_id),
            received=received,
            status=INGRESS_FAILED_CLOSED,
            resolved_records=[],
            failure_reason=str(exc) or "explicit canonical artifact ingress failed closed",
            replay_reference=str(path),
        )
        if received is None:
            fallback = _received_artifact(
                ingress_id=_safe_string(ingress_id),
                session_id=_safe_string(session_id),
                references=[],
                created_at=_safe_string(created_at),
            )
            _persist_failure_if_possible(path, 0, fallback)
            received = fallback
            result["ingress_request_hash"] = fallback["artifact_hash"]
            result["artifact_hash"] = replay_hash(
                {key: value for key, value in result.items() if key != "artifact_hash"}
            )
        _persist_failure_if_possible(path, 1, result)
        return _capture(result=result, artifacts=[], replay_dir=path)


def link_explicit_canonical_artifact_ingress(
    *,
    replay_dir: str | Path,
    project_context_reference: str,
    project_context_hash: str,
    downstream_route_reference: str | None,
    downstream_route_hash: str | None,
    downstream_route_status: str | None,
) -> dict[str, Any]:
    """Append the Project Context and G29-06 lineage link."""

    path = Path(replay_dir)
    resolution = _load_step(path, 1)
    artifact = {
        "artifact_type": EXPLICIT_CANONICAL_ARTIFACT_INGRESS_LINK_ARTIFACT_V1,
        "runtime_version": EXPLICIT_CANONICAL_ARTIFACT_INGRESS_VERSION,
        "ingress_id": resolution["ingress_id"],
        "session_id": resolution["session_id"],
        "ingress_status": resolution["ingress_status"],
        "ingress_resolution_hash": resolution["artifact_hash"],
        "project_context_reference": _require_string(
            project_context_reference, "project_context_reference"
        ),
        "project_context_hash": _require_hash(project_context_hash, "project_context_hash"),
        "downstream_route_reference": _optional_string(downstream_route_reference),
        "downstream_route_hash": _optional_hash(downstream_route_hash),
        "downstream_route_status": _optional_string(downstream_route_status),
        **BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(path, 2, artifact)
    return deepcopy(artifact)


def reconstruct_explicit_canonical_artifact_ingress(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct the complete ingress chain and reject tampering."""

    path = Path(replay_dir)
    received = _load_step(path, 0)
    resolution = _load_step(path, 1)
    linked = _load_step(path, 2)
    if resolution.get("ingress_request_hash") != received.get("artifact_hash"):
        raise FailClosedRuntimeError("explicit artifact ingress request lineage mismatch")
    if linked.get("ingress_resolution_hash") != resolution.get("artifact_hash"):
        raise FailClosedRuntimeError("explicit artifact ingress resolution lineage mismatch")
    if linked.get("ingress_id") != received.get("ingress_id"):
        raise FailClosedRuntimeError("explicit artifact ingress identity mismatch")
    project_context = load_json(Path(linked["project_context_reference"]))
    _verify_artifact_hash(project_context)
    if project_context["artifact_hash"] != linked.get("project_context_hash"):
        raise FailClosedRuntimeError("explicit artifact ingress Project Context mismatch")
    context_ingress = project_context.get("explicit_canonical_artifact_ingress")
    if not isinstance(context_ingress, dict):
        raise FailClosedRuntimeError("explicit artifact ingress Project Context linkage missing")
    if context_ingress.get("artifact_hash") != resolution.get("artifact_hash"):
        raise FailClosedRuntimeError("explicit artifact ingress Project Context lineage mismatch")
    if project_context.get("explicit_canonical_artifact_ingress_reference") != str(path):
        raise FailClosedRuntimeError("explicit artifact ingress Project Context reference mismatch")
    if linked.get("downstream_route_reference") is not None:
        from aigol.runtime.project_context_semantic_capability_route import (
            reconstruct_project_context_semantic_capability_route,
        )

        route = reconstruct_project_context_semantic_capability_route(
            linked["downstream_route_reference"]
        )
        if route.get("artifact_hash") != linked.get("downstream_route_hash"):
            raise FailClosedRuntimeError("explicit artifact ingress downstream route mismatch")
        if route.get("route_status") != linked.get("downstream_route_status"):
            raise FailClosedRuntimeError("explicit artifact ingress downstream status mismatch")
    records = resolution.get("resolved_artifacts")
    if not isinstance(records, list):
        raise FailClosedRuntimeError("explicit artifact ingress resolved records invalid")
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("validated_artifact"), dict):
            raise FailClosedRuntimeError("explicit artifact ingress artifact snapshot missing")
        artifact = _validate_supported_artifact(record["validated_artifact"])
        if artifact["artifact_hash"] != record.get("canonical_artifact_hash"):
            raise FailClosedRuntimeError("explicit artifact ingress snapshot hash mismatch")
    return {
        "ingress_id": resolution["ingress_id"],
        "session_id": resolution["session_id"],
        "ingress_status": resolution["ingress_status"],
        "ingress_request_hash": resolution["ingress_request_hash"],
        "ingress_resolution_hash": resolution["artifact_hash"],
        "validated_canonical_artifacts": [
            deepcopy(record["validated_artifact"]) for record in records
        ],
        "project_context_reference": linked["project_context_reference"],
        "project_context_hash": linked["project_context_hash"],
        "downstream_route_reference": linked["downstream_route_reference"],
        "downstream_route_hash": linked["downstream_route_hash"],
        "replay_artifact_count": 3,
        "replay_hash": replay_hash([received, resolution, linked]),
        "replay_reference": str(path),
    }


def validate_explicit_canonical_artifact_ingress_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one G29-08 ingress or downstream-link artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("explicit canonical artifact ingress artifact required")
    candidate = deepcopy(artifact)
    _verify_artifact_hash(candidate)
    if candidate.get("runtime_version") != EXPLICIT_CANONICAL_ARTIFACT_INGRESS_VERSION:
        raise FailClosedRuntimeError("explicit canonical artifact ingress version mismatch")
    if candidate.get("artifact_type") not in {
        EXPLICIT_CANONICAL_ARTIFACT_INGRESS_ARTIFACT_V1,
        EXPLICIT_CANONICAL_ARTIFACT_INGRESS_LINK_ARTIFACT_V1,
    }:
        raise FailClosedRuntimeError("explicit canonical artifact ingress type mismatch")
    for field, expected in BOUNDARY_FLAGS.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError("explicit canonical artifact ingress boundary mismatch")
    if candidate["artifact_type"] == EXPLICIT_CANONICAL_ARTIFACT_INGRESS_ARTIFACT_V1:
        event = candidate.get("ingress_event")
        if event == "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_RECEIVED":
            references = candidate.get("opaque_artifact_references")
            if not isinstance(references, list) or candidate.get(
                "opaque_artifact_reference_count"
            ) != len(references):
                raise FailClosedRuntimeError("explicit canonical artifact ingress request count mismatch")
        elif event == "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_RESOLVED":
            records = candidate.get("resolved_artifacts")
            if not isinstance(records, list) or candidate.get("resolved_artifact_count") != len(records):
                raise FailClosedRuntimeError("explicit canonical artifact ingress resolution count mismatch")
            if candidate.get("ingress_status") not in {
                INGRESS_COMPLETED,
                INGRESS_FAILED_CLOSED,
            }:
                raise FailClosedRuntimeError("explicit canonical artifact ingress status mismatch")
        else:
            raise FailClosedRuntimeError("explicit canonical artifact ingress event mismatch")
    return candidate


def _normalized_reference_records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, (list, tuple)) or not value:
        raise FailClosedRuntimeError("explicit canonical artifact references are required")
    records: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, str):
            record = {
                "artifact_reference": _require_string(item, "artifact_reference"),
                "expected_artifact_hash": None,
                "expected_wrapper_hash": None,
            }
        elif isinstance(item, dict):
            record = {
                "artifact_reference": _require_string(
                    item.get("artifact_reference"), "artifact_reference"
                ),
                "expected_artifact_hash": _optional_hash(
                    item.get("expected_artifact_hash")
                ),
                "expected_wrapper_hash": _optional_hash(
                    item.get("expected_wrapper_hash")
                ),
            }
        else:
            raise FailClosedRuntimeError("opaque artifact reference must be text or an object")
        records.append(record)
    return sorted(records, key=lambda record: record["artifact_reference"])


def _allowed_roots(*, runtime_root: str | Path, workspace: str | Path) -> tuple[Path, ...]:
    roots = {Path(runtime_root).resolve(strict=False), Path(workspace).resolve(strict=False)}
    return tuple(sorted(roots, key=str))


def _resolve_reference(
    reference: dict[str, Any], *, roots: tuple[Path, ...], workspace: Path
) -> dict[str, Any]:
    supplied = reference["artifact_reference"]
    raw = Path(supplied)
    if ".." in PurePath(supplied).parts:
        raise FailClosedRuntimeError("explicit canonical artifact ingress path traversal rejected")
    candidate = raw if raw.is_absolute() else workspace / raw
    resolved = candidate.resolve(strict=False)
    root = next((allowed for allowed in roots if _is_relative_to(resolved, allowed)), None)
    if root is None:
        raise FailClosedRuntimeError("explicit canonical artifact ingress reference outside allowed roots")
    _reject_symlinks(candidate=candidate, root=root)
    if not candidate.exists() or not candidate.is_file():
        raise FailClosedRuntimeError("explicit canonical artifact ingress reference missing")
    before = candidate.stat()
    if not os.path.isfile(candidate):
        raise FailClosedRuntimeError("explicit canonical artifact ingress source must be a regular file")
    wrapper = load_json(candidate)
    after = candidate.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise FailClosedRuntimeError("explicit canonical artifact ingress mutable source rejected")
    wrapper_hash_field, wrapper_hash = _verify_wrapper(wrapper)
    expected_wrapper_hash = reference.get("expected_wrapper_hash")
    if expected_wrapper_hash is not None and expected_wrapper_hash != wrapper_hash:
        raise FailClosedRuntimeError("explicit canonical artifact ingress wrapper hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("explicit canonical artifact ingress malformed wrapper")
    validated = _validate_supported_artifact(artifact)
    expected_artifact_hash = reference.get("expected_artifact_hash")
    if expected_artifact_hash is not None and expected_artifact_hash != validated["artifact_hash"]:
        raise FailClosedRuntimeError("explicit canonical artifact ingress artifact hash mismatch")
    return {
        "supplied_reference": supplied,
        "resolved_reference": str(resolved),
        "source_root": str(root),
        "wrapper_hash_field": wrapper_hash_field,
        "wrapper_hash": wrapper_hash,
        "wrapper_replay_index": wrapper.get("replay_index"),
        "wrapper_replay_step": wrapper.get("replay_step"),
        "canonical_artifact_type": validated["artifact_type"],
        "canonical_artifact_reference": _artifact_identity(validated),
        "canonical_artifact_hash": validated["artifact_hash"],
        "validated_artifact": deepcopy(validated),
        "source_stability_verified": True,
        "canonical_validation_completed": True,
    }


def _reject_symlinks(*, candidate: Path, root: Path) -> None:
    absolute = candidate.absolute()
    if not _is_relative_to(absolute, root):
        return
    current = root
    for part in absolute.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise FailClosedRuntimeError("explicit canonical artifact ingress symlink rejected")


def _verify_wrapper(wrapper: dict[str, Any]) -> tuple[str, str]:
    if not isinstance(wrapper.get("replay_index"), int):
        raise FailClosedRuntimeError("explicit canonical artifact ingress malformed wrapper index")
    _require_string(wrapper.get("replay_step"), "replay_step")
    fields = [field for field in ("replay_hash", "wrapper_hash") if field in wrapper]
    if len(fields) != 1:
        raise FailClosedRuntimeError("explicit canonical artifact ingress malformed wrapper hash")
    field = fields[0]
    body = deepcopy(wrapper)
    supplied = _require_hash(body.pop(field), field)
    if replay_hash(body) != supplied:
        raise FailClosedRuntimeError("explicit canonical artifact ingress wrapper hash mismatch")
    return field, supplied


def _validate_supported_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(artifact)
    artifact_type = _require_string(candidate.get("artifact_type"), "artifact_type")
    supported = {
        artifact_type
        for adapter in certified_capability_invocation_adapters().values()
        for artifact_type in adapter["accepted_input_artifact_types"]
    }
    if artifact_type not in supported:
        raise FailClosedRuntimeError("explicit canonical artifact ingress unsupported artifact type")
    _verify_artifact_hash(candidate)
    if candidate.get("replay_visible") is not True:
        raise FailClosedRuntimeError("explicit canonical artifact ingress artifact is not replay-visible")
    if artifact_type == NORMALIZED_CHANGE_ARTIFACT_V1:
        return validate_normalized_change_artifact(candidate)
    if artifact_type == PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1:
        return validate_platform_capability_composition_coverage_request(candidate)
    if artifact_type == PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1:
        return validate_product1_decision_validation_request(candidate)
    if artifact_type == PLATFORM_CHANGE_IMPACT_ARTIFACT_V1:
        return validate_platform_change_impact_artifact(candidate)
    if artifact_type == IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
        _validate_manifest(candidate)
    else:
        _validate_mutation_proposal(candidate)
    return candidate


def _validate_manifest(artifact: dict[str, Any]) -> None:
    if artifact.get("manifest_status") != "IMPLEMENTATION_MANIFEST_CREATED":
        raise FailClosedRuntimeError("explicit canonical artifact ingress manifest is not created")
    if artifact.get("read_only") is not True or artifact.get("content_bearing_manifest") is not True:
        raise FailClosedRuntimeError("explicit canonical artifact ingress mutable manifest rejected")
    if artifact.get("filesystem_mutated") is not False:
        raise FailClosedRuntimeError("explicit canonical artifact ingress manifest mutation mismatch")
    _require_string(artifact.get("manifest_id"), "manifest_id")
    manifest_hash = _require_hash(
        artifact.get("implementation_manifest_hash"), "implementation_manifest_hash"
    )
    if manifest_hash != _implementation_manifest_hash(artifact):
        raise FailClosedRuntimeError(
            "explicit canonical artifact ingress implementation manifest hash mismatch"
        )
    if not isinstance(artifact.get("file_entries"), list) or not artifact["file_entries"]:
        raise FailClosedRuntimeError("explicit canonical artifact ingress manifest files missing")
    if artifact.get("file_count") != len(artifact["file_entries"]):
        raise FailClosedRuntimeError("explicit canonical artifact ingress manifest count mismatch")


def _implementation_manifest_hash(artifact: dict[str, Any]) -> str:
    fields = (
        "manifest_id",
        "canonical_chain_id",
        "implementation_bundle_id",
        "source_candidate_reference",
        "source_candidate_hash",
        "implementation_handoff_reference",
        "implementation_handoff_hash",
        "provider_generation_authorization_reference",
        "provider_generation_authorization_hash",
        "provider_response_reference",
        "provider_response_hash",
        "target_domain",
        "target_resource",
        "target_worker",
        "operation_mode",
        "file_entries",
        "test_entries",
        "validation_requirements",
        "forbidden_operations",
        "known_gaps",
        "manifest_status",
        "read_only",
        "content_bearing_manifest",
        "filesystem_mutated",
        "execution_authorized",
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authority_flags",
        "failure_reason",
    )
    try:
        return replay_hash({field: artifact[field] for field in fields})
    except KeyError as exc:
        raise FailClosedRuntimeError(
            "explicit canonical artifact ingress implementation manifest field missing"
        ) from exc


def _validate_mutation_proposal(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != "GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1":
        raise FailClosedRuntimeError("explicit canonical artifact ingress artifact family invalid")
    _require_string(artifact.get("proposal_id"), "proposal_id")
    if artifact.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("explicit canonical artifact ingress proposal approval boundary invalid")
    if artifact.get("mutation_allowed_before_approval") is not False:
        raise FailClosedRuntimeError("explicit canonical artifact ingress mutable proposal rejected")
    mutations = artifact.get("file_mutations")
    if not isinstance(mutations, list) or not mutations:
        raise FailClosedRuntimeError("explicit canonical artifact ingress proposal mutations missing")
    if artifact.get("file_mutation_count") != len(mutations):
        raise FailClosedRuntimeError("explicit canonical artifact ingress proposal count mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    body = deepcopy(artifact)
    supplied = _require_hash(body.pop("artifact_hash", None), "artifact_hash")
    if replay_hash(body) != supplied:
        raise FailClosedRuntimeError("explicit canonical artifact ingress artifact hash mismatch")


def _artifact_identity(artifact: dict[str, Any]) -> str:
    for field in (
        "manifest_id",
        "proposal_id",
        "normalization_id",
        "impact_analysis_id",
        "request_id",
    ):
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise FailClosedRuntimeError("explicit canonical artifact ingress immutable identity missing")


def _received_artifact(
    *, ingress_id: str, session_id: str, references: list[dict[str, Any]], created_at: str
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXPLICIT_CANONICAL_ARTIFACT_INGRESS_ARTIFACT_V1,
        "runtime_version": EXPLICIT_CANONICAL_ARTIFACT_INGRESS_VERSION,
        "ingress_event": "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_RECEIVED",
        "ingress_id": ingress_id,
        "session_id": session_id,
        "created_at": created_at,
        "opaque_artifact_references": deepcopy(references),
        "opaque_artifact_reference_count": len(references),
        **BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _resolution_artifact(
    *,
    ingress_id: str,
    session_id: str,
    received: dict[str, Any] | None,
    status: str,
    resolved_records: list[dict[str, Any]],
    failure_reason: str | None,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXPLICIT_CANONICAL_ARTIFACT_INGRESS_ARTIFACT_V1,
        "runtime_version": EXPLICIT_CANONICAL_ARTIFACT_INGRESS_VERSION,
        "ingress_event": "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_RESOLVED",
        "ingress_id": ingress_id,
        "session_id": session_id,
        "ingress_request_hash": received.get("artifact_hash") if received else None,
        "ingress_status": status,
        "resolved_artifacts": deepcopy(resolved_records),
        "resolved_artifact_count": len(resolved_records),
        "failure_reason": failure_reason,
        "replay_reference": replay_reference,
        **BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(*, result: dict[str, Any], artifacts: list[dict[str, Any]], replay_dir: Path) -> dict[str, Any]:
    return {
        "ingress_status": result["ingress_status"],
        "explicit_canonical_artifact_ingress_artifact": deepcopy(result),
        "validated_canonical_artifacts": deepcopy(artifacts),
        "failure_reason": result.get("failure_reason"),
        "replay_reference": str(replay_dir),
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
    }


def _persist_step(path: Path, index: int, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": REPLAY_STEPS[index],
        "artifact": deepcopy(artifact),
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"{index:03d}_{REPLAY_STEPS[index]}.json", wrapper)


def _persist_failure_if_possible(path: Path, index: int, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(path, index, artifact)
    except Exception:
        return


def _load_step(path: Path, index: int) -> dict[str, Any]:
    wrapper = load_json(path / f"{index:03d}_{REPLAY_STEPS[index]}.json")
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != REPLAY_STEPS[index]:
        raise FailClosedRuntimeError("explicit canonical artifact ingress replay ordering mismatch")
    body = deepcopy(wrapper)
    supplied = body.pop("wrapper_hash", None)
    if supplied != replay_hash(body):
        raise FailClosedRuntimeError("explicit canonical artifact ingress Replay wrapper mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("explicit canonical artifact ingress Replay artifact missing")
    return validate_explicit_canonical_artifact_ingress_artifact(artifact)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "UNAVAILABLE"


def _optional_string(value: Any) -> str | None:
    return None if value is None else _require_string(value, "optional string")


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{field_name} must be a sha256 hash")
    return text


def _optional_hash(value: Any) -> str | None:
    return None if value is None else _require_hash(value, "optional hash")


__all__ = [
    "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_ARTIFACT_V1",
    "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_LINK_ARTIFACT_V1",
    "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_VERSION",
    "INGRESS_COMPLETED",
    "INGRESS_FAILED_CLOSED",
    "link_explicit_canonical_artifact_ingress",
    "reconstruct_explicit_canonical_artifact_ingress",
    "run_explicit_canonical_artifact_ingress",
    "validate_explicit_canonical_artifact_ingress_artifact",
]
