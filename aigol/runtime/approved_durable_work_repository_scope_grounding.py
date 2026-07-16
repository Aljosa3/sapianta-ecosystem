"""Ground approved durable-work Worker payloads in Repository Cognition evidence."""

from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

from aigol.runtime.approved_durable_work_worker_payload_binding import (
    WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED,
    reconstruct_approved_durable_work_worker_payload_binding,
    validate_approved_durable_work_worker_payload_binding,
)
from aigol.runtime.capability_audit_runtime import (
    AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION,
    detect_capabilities,
)
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    project_worker_request_repository_scope,
    validate_worker_request_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_change_impact_analysis_runtime import _constitutional_layer
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


REPOSITORY_SCOPE_GROUNDING_VERSION = (
    "G31_06_APPROVED_DURABLE_WORK_REPOSITORY_SCOPE_GROUNDING_V1"
)
CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1 = (
    "CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1"
)
REPOSITORY_SCOPE_GROUNDED = "CANONICAL_REPOSITORY_SCOPE_GROUNDED"
REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED = (
    "CANONICAL_REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED"
)
REPLAY_STEPS = (
    "approved_worker_payload_source_recorded",
    "canonical_repository_scope_grounding_recorded",
)

FALSE_BOUNDARIES = {
    "execution_authorized": False,
    "provider_invoked": False,
    "worker_selected": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "repository_mutated": False,
    "validation_executed": False,
    "certification_reached": False,
    "human_interface_authority": False,
    "human_interface_semantic_authority": False,
    "human_interface_repository_selection_authority": False,
    "human_interface_worker_authority": False,
    "human_interface_mutation_authority": False,
    "human_interface_authorization_authority": False,
    "human_interface_replay_authority": False,
}


def ground_approved_durable_work_repository_scope(
    *,
    worker_payload_binding_artifact: dict[str, Any],
    workspace: str | Path,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Bind one unresolved G31-05 payload to exact existing repository evidence."""

    source = validate_approved_durable_work_worker_payload_binding(
        worker_payload_binding_artifact
    )
    if source.get("binding_status") != WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED:
        raise FailClosedRuntimeError(
            "repository grounding requires an unresolved approved Worker payload"
        )
    reconstructed = reconstruct_approved_durable_work_worker_payload_binding(
        source["replay_reference"]
    )
    if reconstructed["artifact_hash"] != source["artifact_hash"]:
        raise FailClosedRuntimeError("repository grounding source Replay mismatch")
    root = _existing_workspace_root(workspace)
    replay_root = Path(replay_dir)
    _ensure_replay_available(replay_root)
    _persist_step(replay_root, 0, REPLAY_STEPS[0], source)

    capability_key = _required_capability_key(source)
    git_repository = (root / ".git").exists()
    cognition_entries = detect_capabilities(root) if git_repository else {}
    matching = [
        deepcopy(entry)
        for key, entry in cognition_entries.items()
        if key == capability_key
        and entry.get("implementation")
        and entry.get("tests")
    ]
    materially_ambiguous = (
        len(matching) == 1
        and len(matching[0].get("implementation") or []) != 1
    )
    if len(matching) != 1 or materially_ambiguous:
        artifact = _grounding_artifact(
            source=source,
            workspace=root,
            capability_key=capability_key,
            cognition_entry=None,
            target_evidence=[],
            grounded_worker_request=None,
            created_at=created_at,
            replay_reference=str(replay_root),
            status=REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED,
            failure_reason=(
                "Repository Cognition requires a Git workspace with one exact compatible "
                "implementation-and-test evidence match"
                if not matching
                else "Repository Cognition found materially ambiguous capability evidence"
            ),
        )
    else:
        entry = matching[0]
        target_evidence = _target_evidence(root=root, cognition_entry=entry)
        snapshot_hash = _repository_cognition_snapshot_hash(
            capability_key=capability_key,
            cognition_entry=entry,
            target_evidence=target_evidence,
        )
        grounding_identity = (
            f"{source['source_durable_governed_work_id']}:REPOSITORY-SCOPE-GROUNDING"
        )
        grounding_evidence_hash = replay_hash(
            {
                "grounding_identity": grounding_identity,
                "source_worker_payload_binding_hash": source["artifact_hash"],
                "repository_cognition_snapshot_hash": snapshot_hash,
                "target_evidence_hashes": [
                    item["target_evidence_hash"] for item in target_evidence
                ],
            }
        )
        grounded_request = project_worker_request_repository_scope(
            worker_request_artifact=source[
                "worker_implementation_payload_artifact"
            ],
            repository_targets=[item["target_path"] for item in target_evidence],
            focused_test_targets=[
                item["target_path"]
                for item in target_evidence
                if item["target_role"] == "FOCUSED_TEST"
            ],
            repository_scope_grounding_identity=grounding_identity,
            repository_scope_grounding_hash=grounding_evidence_hash,
        )
        artifact = _grounding_artifact(
            source=source,
            workspace=root,
            capability_key=capability_key,
            cognition_entry=entry,
            target_evidence=target_evidence,
            grounded_worker_request=grounded_request,
            created_at=created_at,
            replay_reference=str(replay_root),
            status=REPOSITORY_SCOPE_GROUNDED,
            failure_reason=None,
            repository_cognition_snapshot_hash=snapshot_hash,
            grounding_identity=grounding_identity,
            grounding_evidence_hash=grounding_evidence_hash,
        )
    validate_approved_durable_work_repository_scope_grounding(
        artifact,
        workspace=root,
    )
    _persist_step(replay_root, 1, REPLAY_STEPS[1], artifact)
    return deepcopy(artifact)


def validate_approved_durable_work_repository_scope_grounding(
    artifact: dict[str, Any],
    *,
    workspace: str | Path | None = None,
) -> dict[str, Any]:
    """Validate grounding identity, target evidence, projection, and boundaries."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("repository-scope grounding must be a dict")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1:
        raise FailClosedRuntimeError("repository-scope grounding type is invalid")
    if candidate.get("runtime_version") != REPOSITORY_SCOPE_GROUNDING_VERSION:
        raise FailClosedRuntimeError("repository-scope grounding version is invalid")
    _verify_hash(candidate, "repository-scope grounding")
    source = validate_approved_durable_work_worker_payload_binding(
        candidate.get("source_worker_payload_binding_artifact")
    )
    expected_source = {
        "source_worker_payload_binding_hash": source["artifact_hash"],
        "source_implementation_turn_binding_hash": source[
            "source_implementation_turn_binding_hash"
        ],
        "source_approval_consumption_hash": source[
            "source_approval_consumption_hash"
        ],
        "source_development_composition_plan_hash": source[
            "source_development_composition_plan_hash"
        ],
        "source_durable_governed_work_hash": source[
            "source_durable_governed_work_hash"
        ],
        "source_proposal_preview_hash": source["source_proposal_preview_hash"],
        "source_approval_request_hash": source["source_approval_request_hash"],
        "source_ppp_task_package_hash": source["ppp_task_package_hash"],
        "source_implementation_request_hash": source[
            "implementation_request_hash"
        ],
        "source_worker_implementation_payload_hash": source[
            "worker_implementation_payload_hash"
        ],
    }
    for field, expected in expected_source.items():
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(
                f"repository-scope grounding upstream identity mismatch: {field}"
            )
    status = candidate.get("grounding_status")
    if status not in {
        REPOSITORY_SCOPE_GROUNDED,
        REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("repository-scope grounding status is invalid")
    for field, expected in FALSE_BOUNDARIES.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError(
                f"repository-scope grounding authority boundary mismatch: {field}"
            )
    evidence = candidate.get("target_evidence")
    if not isinstance(evidence, list):
        raise FailClosedRuntimeError("repository target evidence must be a list")
    if status == REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED:
        if evidence or candidate.get("grounded_repository_targets"):
            raise FailClosedRuntimeError("unresolved grounding cannot contain targets")
        if candidate.get("dispatch_blocked") is not True:
            raise FailClosedRuntimeError("unresolved grounding must block dispatch")
        if not candidate.get("failure_reason"):
            raise FailClosedRuntimeError("unresolved grounding requires a reason")
        return candidate

    if not evidence or candidate.get("fail_closed") is not False:
        raise FailClosedRuntimeError("grounded repository evidence is incomplete")
    _validate_target_evidence(
        evidence,
        workspace=(workspace if workspace is not None else None),
    )
    expected_targets = [item["target_path"] for item in evidence]
    if candidate.get("grounded_repository_targets") != expected_targets:
        raise FailClosedRuntimeError("grounded repository target order mismatch")
    focused_tests = [
        item["target_path"] for item in evidence if item["target_role"] == "FOCUSED_TEST"
    ]
    if candidate.get("grounded_focused_test_targets") != focused_tests:
        raise FailClosedRuntimeError("grounded focused-test targets mismatch")
    snapshot_hash = _repository_cognition_snapshot_hash(
        capability_key=candidate["canonical_capability_target"],
        cognition_entry=candidate["repository_cognition_entry"],
        target_evidence=evidence,
    )
    if candidate.get("repository_cognition_snapshot_hash") != snapshot_hash:
        raise FailClosedRuntimeError("Repository Cognition snapshot hash mismatch")
    expected_grounding_hash = replay_hash(
        {
            "grounding_identity": candidate["grounding_identity"],
            "source_worker_payload_binding_hash": source["artifact_hash"],
            "repository_cognition_snapshot_hash": snapshot_hash,
            "target_evidence_hashes": [item["target_evidence_hash"] for item in evidence],
        }
    )
    if candidate.get("grounding_evidence_hash") != expected_grounding_hash:
        raise FailClosedRuntimeError("repository grounding evidence hash mismatch")
    grounded_request = validate_worker_request_artifact(
        candidate.get("grounded_worker_request_artifact")
    )
    if candidate.get("grounded_worker_request_hash") != grounded_request["artifact_hash"]:
        raise FailClosedRuntimeError("grounded Worker request hash mismatch")
    if grounded_request.get("repository_targets") != expected_targets:
        raise FailClosedRuntimeError("grounded Worker request targets mismatch")
    if grounded_request.get("repository_scope_grounding_hash") != expected_grounding_hash:
        raise FailClosedRuntimeError("grounded Worker request evidence mismatch")
    _validate_projection_continuity(
        source_request=source["worker_implementation_payload_artifact"],
        grounded_request=grounded_request,
    )
    if candidate.get("dispatch_blocked") is not False:
        raise FailClosedRuntimeError("grounded repository scope dispatch boundary mismatch")
    return candidate


def reconstruct_approved_durable_work_repository_scope_grounding(
    replay_dir: str | Path,
    *,
    workspace: str | Path | None = None,
) -> dict[str, Any]:
    """Reconstruct ordered G31-05-to-repository-grounding Replay."""

    root = Path(replay_dir)
    wrappers = [
        load_json(root / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        _validate_wrapper(wrapper, index=index, step=step)
    source = validate_approved_durable_work_worker_payload_binding(
        wrappers[0]["artifact"]
    )
    reconstructed = reconstruct_approved_durable_work_worker_payload_binding(
        source["replay_reference"]
    )
    if reconstructed["artifact_hash"] != source["artifact_hash"]:
        raise FailClosedRuntimeError("repository grounding upstream Replay mismatch")
    grounding = validate_approved_durable_work_repository_scope_grounding(
        wrappers[1]["artifact"],
        workspace=workspace,
    )
    if grounding["source_worker_payload_binding_hash"] != source["artifact_hash"]:
        raise FailClosedRuntimeError("repository grounding Replay lineage mismatch")
    return grounding


def render_approved_durable_work_repository_scope_grounding(
    artifact: dict[str, Any],
) -> str:
    grounding = validate_approved_durable_work_repository_scope_grounding(artifact)
    return "\n".join(
        [
            "Canonical repository-scope grounding",
            f"grounding_status: {grounding['grounding_status']}",
            f"canonical_capability_target: {grounding['canonical_capability_target']}",
            f"repository_cognition_snapshot_hash: {grounding.get('repository_cognition_snapshot_hash')}",
            f"grounded_repository_targets: {grounding['grounded_repository_targets']}",
            f"grounded_focused_test_targets: {grounding['grounded_focused_test_targets']}",
            f"grounded_worker_request_hash: {grounding.get('grounded_worker_request_hash')}",
            f"dispatch_blocked: {grounding['dispatch_blocked']}",
            f"execution_authorized: {grounding['execution_authorized']}",
            f"provider_invoked: {grounding['provider_invoked']}",
            f"worker_invoked: {grounding['worker_invoked']}",
            f"repository_mutated: {grounding['repository_mutated']}",
            f"failure_reason: {grounding['failure_reason']}",
            f"replay_reference: {grounding['replay_reference']}",
        ]
    )


def _grounding_artifact(
    *,
    source: dict[str, Any],
    workspace: Path,
    capability_key: str,
    cognition_entry: dict[str, Any] | None,
    target_evidence: list[dict[str, Any]],
    grounded_worker_request: dict[str, Any] | None,
    created_at: str,
    replay_reference: str,
    status: str,
    failure_reason: str | None,
    repository_cognition_snapshot_hash: str | None = None,
    grounding_identity: str | None = None,
    grounding_evidence_hash: str | None = None,
) -> dict[str, Any]:
    grounded = status == REPOSITORY_SCOPE_GROUNDED
    targets = [item["target_path"] for item in target_evidence]
    tests = [
        item["target_path"] for item in target_evidence if item["target_role"] == "FOCUSED_TEST"
    ]
    artifact = {
        "artifact_type": CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1,
        "runtime_version": REPOSITORY_SCOPE_GROUNDING_VERSION,
        "grounding_status": status,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": replay_reference,
        "workspace_root": str(workspace),
        "repository_cognition_runtime_version": AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION,
        "repository_cognition_selection_rule": (
            "EXACT_CANONICAL_CAPABILITY_TARGET_TO_EXISTING_IMPLEMENTATION_AND_TEST_KEY"
        ),
        "canonical_capability_target": capability_key,
        "repository_cognition_entry": deepcopy(cognition_entry),
        "repository_cognition_snapshot_hash": repository_cognition_snapshot_hash,
        "target_evidence": deepcopy(target_evidence),
        "grounded_repository_targets": targets,
        "grounded_source_targets": [
            item["target_path"] for item in target_evidence if item["target_role"] == "SOURCE"
        ],
        "grounded_focused_test_targets": tests,
        "grounding_identity": grounding_identity,
        "grounding_evidence_hash": grounding_evidence_hash,
        "source_worker_payload_binding_artifact": deepcopy(source),
        "source_worker_payload_binding_hash": source["artifact_hash"],
        "source_implementation_turn_binding_hash": source[
            "source_implementation_turn_binding_hash"
        ],
        "source_approval_consumption_hash": source[
            "source_approval_consumption_hash"
        ],
        "source_development_composition_plan_hash": source[
            "source_development_composition_plan_hash"
        ],
        "source_durable_governed_work_hash": source[
            "source_durable_governed_work_hash"
        ],
        "source_proposal_preview_hash": source["source_proposal_preview_hash"],
        "source_approval_request_hash": source["source_approval_request_hash"],
        "source_ppp_task_package_hash": source["ppp_task_package_hash"],
        "source_implementation_request_hash": source["implementation_request_hash"],
        "source_worker_implementation_payload_hash": source[
            "worker_implementation_payload_hash"
        ],
        "grounded_worker_request_artifact": deepcopy(grounded_worker_request),
        "grounded_worker_request_hash": (
            grounded_worker_request.get("artifact_hash")
            if isinstance(grounded_worker_request, dict)
            else None
        ),
        "original_goal_preserved": True,
        "project_objective_preserved": True,
        "approved_plan_preserved": True,
        "durable_governed_work_preserved": True,
        "proposal_and_approval_preserved": True,
        "task_package_preserved": True,
        "worker_objective_preserved": True,
        "natural_language_target_inference_used": False,
        "placeholder_target_used": False,
        "repository_discovery_framework_created": False,
        "ready_for_separate_dispatch_governance": grounded,
        "dispatch_blocked": not grounded,
        "fail_closed": not grounded,
        "failure_reason": failure_reason,
        "replay_visible": True,
        **FALSE_BOUNDARIES,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _required_capability_key(source: dict[str, Any]) -> str:
    key = _require_string(
        source["ppp_task_package_artifact"].get("affected_domain"),
        "canonical capability target",
    ).lower()
    if key == "unresolved":
        return key
    return key


def _target_evidence(
    *,
    root: Path,
    cognition_entry: dict[str, Any],
) -> list[dict[str, Any]]:
    paths = [
        *(("SOURCE", path) for path in cognition_entry.get("implementation", [])),
        *(("FOCUSED_TEST", path) for path in cognition_entry.get("tests", [])),
    ]
    if not paths:
        raise FailClosedRuntimeError("Repository Cognition target evidence is empty")
    evidence = [
        _observe_target(root=root, relative_path=path, target_role=role)
        for role, path in paths
    ]
    return sorted(evidence, key=lambda item: (item["target_path"], item["target_role"]))


def _observe_target(
    *,
    root: Path,
    relative_path: str,
    target_role: str,
) -> dict[str, Any]:
    normalized = _relative_path(relative_path)
    path = (root / normalized).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise FailClosedRuntimeError("Repository Cognition target is outside workspace") from exc
    if not path.is_file():
        raise FailClosedRuntimeError("Repository Cognition target does not exist")
    content = path.read_bytes()
    content_hash = "sha256:" + sha256(content).hexdigest()
    try:
        text = content.decode("utf-8")
        tree = ast.parse(text, filename=normalized)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise FailClosedRuntimeError("Repository Cognition source evidence is not parseable") from exc
    symbols = [
        {
            "symbol_name": node.name,
            "symbol_kind": "CLASS" if isinstance(node, ast.ClassDef) else "FUNCTION",
            "line_number": node.lineno,
            "symbol_evidence_hash": replay_hash(
                {
                    "target_path": normalized,
                    "symbol_name": node.name,
                    "symbol_kind": "CLASS" if isinstance(node, ast.ClassDef) else "FUNCTION",
                    "line_number": node.lineno,
                    "file_content_hash": content_hash,
                }
            ),
        }
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    artifact_type = (
        "REPOSITORY_TEST_FILE" if target_role == "FOCUSED_TEST" else "REPOSITORY_SOURCE_FILE"
    )
    layer, mapping_rule = _constitutional_layer(normalized, artifact_type)
    if layer in {"L0", "L1"}:
        raise FailClosedRuntimeError("Repository Cognition target mutation layer is incompatible")
    evidence = {
        "target_path": normalized,
        "target_role": target_role,
        "repository_artifact_type": artifact_type,
        "source_evidence_identity": f"REPOSITORY_COGNITION:{normalized}",
        "source_content_hash": content_hash,
        "symbols": symbols,
        "symbol_count": len(symbols),
        "mutation_layer": layer,
        "mutation_layer_mapping_rule": mapping_rule,
        "mutation_layer_authority": "CANONICAL_LAYER_MODEL",
        "workspace_relative": True,
        "read_only_observation": True,
    }
    evidence["target_evidence_hash"] = replay_hash(evidence)
    return evidence


def _validate_target_evidence(
    evidence: list[dict[str, Any]],
    *,
    workspace: str | Path | None,
) -> None:
    expected_order = sorted(
        evidence, key=lambda item: (item.get("target_path"), item.get("target_role"))
    )
    if evidence != expected_order:
        raise FailClosedRuntimeError("repository target evidence ordering mismatch")
    paths: set[str] = set()
    root = _workspace_root(workspace) if workspace is not None else None
    for item in evidence:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("repository target evidence item is invalid")
        body = deepcopy(item)
        actual_hash = body.pop("target_evidence_hash", None)
        if replay_hash(body) != actual_hash:
            raise FailClosedRuntimeError("repository target evidence hash mismatch")
        path = _relative_path(item.get("target_path"))
        if path in paths:
            raise FailClosedRuntimeError("repository target evidence path is duplicated")
        paths.add(path)
        if item.get("target_role") not in {"SOURCE", "FOCUSED_TEST"}:
            raise FailClosedRuntimeError("repository target role is invalid")
        if item.get("mutation_layer") in {None, "L0", "L1"}:
            raise FailClosedRuntimeError("repository mutation layer is absent or incompatible")
        if item.get("mutation_layer_authority") != "CANONICAL_LAYER_MODEL":
            raise FailClosedRuntimeError("repository mutation layer authority mismatch")
        if root is not None:
            observed = _observe_target(
                root=root,
                relative_path=path,
                target_role=item["target_role"],
            )
            if observed != item:
                raise FailClosedRuntimeError("repository target evidence is stale or substituted")


def _repository_cognition_snapshot_hash(
    *,
    capability_key: str,
    cognition_entry: dict[str, Any],
    target_evidence: list[dict[str, Any]],
) -> str:
    return replay_hash(
        {
            "repository_cognition_runtime_version": AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION,
            "canonical_capability_target": capability_key,
            "capability_key": cognition_entry.get("key"),
            "capability_status": cognition_entry.get("status"),
            "implementation_paths": deepcopy(cognition_entry.get("implementation") or []),
            "focused_test_paths": deepcopy(cognition_entry.get("tests") or []),
            "target_evidence_hashes": [
                item["target_evidence_hash"] for item in target_evidence
            ],
        }
    )


def _validate_projection_continuity(
    *,
    source_request: dict[str, Any],
    grounded_request: dict[str, Any],
) -> None:
    allowed_outer = {
        "artifact_hash",
        "repository_scope_status",
        "repository_targets",
        "repository_scope_grounding_identity",
        "repository_scope_grounding_hash",
        "ready_for_worker_dispatch_governance",
        "dispatch_blocked_by_unresolved_repository_scope",
        "implementation_scope",
    }
    for field, value in source_request.items():
        if field not in allowed_outer and grounded_request.get(field) != value:
            raise FailClosedRuntimeError(
                f"grounded Worker request changed approved field: {field}"
            )
    source_scope = source_request["implementation_scope"]
    grounded_scope = grounded_request["implementation_scope"]
    allowed_scope = {
        "repository_scope_status",
        "repository_targets",
        "focused_test_requirements",
        "repository_scope_grounding_identity",
        "repository_scope_grounding_hash",
        "field_lineage",
    }
    for field, value in source_scope.items():
        if field not in allowed_scope and grounded_scope.get(field) != value:
            raise FailClosedRuntimeError(
                f"repository grounding changed approved scope field: {field}"
            )
    source_lineage = source_scope["field_lineage"]
    grounded_lineage = grounded_scope["field_lineage"]
    for field, value in source_lineage.items():
        if field != "repository_scope" and grounded_lineage.get(field) != value:
            raise FailClosedRuntimeError(
                f"repository grounding changed approved lineage field: {field}"
            )


def _workspace_root(value: str | Path) -> Path:
    root = Path(value).resolve()
    if not root.is_dir() or not (root / ".git").exists():
        raise FailClosedRuntimeError("repository grounding workspace must be a Git repository")
    return root


def _existing_workspace_root(value: str | Path) -> Path:
    root = Path(value).resolve()
    if not root.is_dir():
        raise FailClosedRuntimeError("repository grounding workspace must exist")
    return root


def _relative_path(value: Any) -> str:
    text = _require_string(value, "repository target path").replace("\\", "/")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or text in {"", "."}:
        raise FailClosedRuntimeError("repository target must be workspace-relative")
    return path.as_posix()


def _verify_hash(artifact: dict[str, Any], label: str) -> None:
    body = deepcopy(artifact)
    actual = body.pop("artifact_hash", None)
    if replay_hash(body) != actual:
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _ensure_replay_available(root: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (root / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("repository grounding Replay already exists")


def _persist_step(root: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(root / f"{index:03d}_{step}.json", wrapper)


def _validate_wrapper(wrapper: dict[str, Any], *, index: int, step: str) -> None:
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("repository grounding Replay ordering mismatch")
    body = deepcopy(wrapper)
    actual = body.pop("replay_hash", None)
    if replay_hash(body) != actual:
        raise FailClosedRuntimeError("repository grounding Replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
