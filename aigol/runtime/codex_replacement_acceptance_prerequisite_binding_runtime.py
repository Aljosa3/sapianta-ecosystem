"""Bind one successful G31 disposable replacement to canonical acceptance prerequisites."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import stat
from typing import Any

from aigol.runtime.codex_satisfied_outcome_disposable_validation_binding_runtime import (
    COMPLETED,
    CRITERIA_VERSION,
    reconstruct_disposable_patch_validation_outcome,
    reconstruct_disposable_patch_validation_review,
)
from aigol.runtime.generated_content_acceptance_runtime import (
    ACCEPTANCE_PREREQUISITES_SATISFIED,
    bind_generated_content_acceptance_prerequisites,
    verify_generated_content_acceptance_prerequisite_artifact,
)
from aigol.runtime.generated_content_validation_runtime import (
    GENERATED_CONTENT_VALIDATED,
    validate_generated_content,
    verify_generated_content_validation_artifact,
)
from aigol.runtime.generated_test_validation_runtime import (
    GENERATED_TEST_VALIDATED,
    validate_generated_tests,
    verify_generated_test_validation_artifact,
)
from aigol.runtime.human_decision_runtime import reconstruct_human_decision_replay
from aigol.runtime.implementation_manifest_runtime import (
    IMPLEMENTATION_MANIFEST_CREATED,
    REPLACE_CONTENT,
    create_replacement_implementation_manifest,
    reconstruct_implementation_manifest_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
    write_json_immutable,
)
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    reconstruct_validation_command_replay,
)


RUNTIME_VERSION = "AIGOL_CODEX_REPLACEMENT_ACCEPTANCE_PREREQUISITE_BINDING_RUNTIME_V1"
BINDING_ARTIFACT_V1 = "CODEX_REPLACEMENT_ACCEPTANCE_PREREQUISITE_BINDING_ARTIFACT_V1"
BINDING_COMPLETED = "REPLACEMENT_ACCEPTANCE_PREREQUISITES_BOUND"
REPLAY_STEP = "replacement_acceptance_prerequisites_bound"


def bind_codex_replacement_acceptance_prerequisites(
    *,
    disposable_validation_outcome_capture: dict[str, Any],
    disposable_validation_review_capture: dict[str, Any],
    application_decision_capture: dict[str, Any],
    task_outcome_decision_capture: dict[str, Any],
    task_outcome_review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    governance_validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    source_workspace: str | Path,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create V2 manifest and validation prerequisites without acceptance or mutation."""

    root = Path(session_root).resolve()
    replay_path = Path(replay_dir).resolve()
    source = Path(source_workspace).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("replacement prerequisite binding is cross-session")
    _ensure_destination_available(replay_path)
    review = reconstruct_disposable_patch_validation_review(
        review_binding_capture=disposable_validation_review_capture,
        task_outcome_decision_capture=task_outcome_decision_capture,
        review_capture=task_outcome_review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=governance_validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        source_workspace=source,
    )
    reconstructed_outcome = reconstruct_disposable_patch_validation_outcome(
        outcome_capture=disposable_validation_outcome_capture,
        review_binding_capture=disposable_validation_review_capture,
        application_decision_capture=application_decision_capture,
        task_outcome_decision_capture=task_outcome_decision_capture,
        review_capture=task_outcome_review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=governance_validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        source_workspace=source,
    )
    plan = review["plan"]
    outcome = deepcopy(disposable_validation_outcome_capture.get("outcome_artifact"))
    _require_successful_disposable_outcome(outcome, reconstructed_outcome, plan)
    _reject_repeated_consumption(root, outcome["artifact_hash"])

    application_replay = reconstruct_human_decision_replay(
        application_decision_capture["human_decision_replay_reference"]
    )
    task_decision_replay = reconstruct_human_decision_replay(
        task_outcome_decision_capture["human_decision_replay_reference"]
    )
    test_capture = disposable_validation_outcome_capture.get("grounded_test_validation_capture")
    if not isinstance(test_capture, dict):
        raise FailClosedRuntimeError("replacement prerequisite binding requires focused test evidence")
    test_result = deepcopy(test_capture.get("validation_command_result_artifact"))
    test_replay = reconstruct_validation_command_replay(
        test_capture.get("validation_command_replay_reference", "")
    )
    if not isinstance(test_result, dict) or test_result.get("artifact_hash") != outcome.get(
        "test_validation_result_hash"
    ):
        raise FailClosedRuntimeError("replacement prerequisite test result identity mismatch")

    source_snapshot = _repository_file_hashes(source)
    if source_snapshot != plan.get("source_repository_snapshot_sha256"):
        raise FailClosedRuntimeError("replacement prerequisite source repository drift")
    disposable = Path(plan["disposable_workspace"]).resolve()
    replacements = _replacement_entries(source, disposable, plan)
    focused_test = _focused_test_evidence(
        source,
        disposable,
        plan,
        test_result,
        test_replay,
        test_capture["validation_command_replay_reference"],
    )

    identity = replay_hash({
        "disposable_validation_outcome_hash": outcome["artifact_hash"],
        "application_decision_hash": outcome["application_decision_hash"],
        "task_outcome_decision_hash": plan["task_outcome_decision_hash"],
        "patch_sha256": plan["patch_sha256"],
        "preimage_sha256": plan["preimage_sha256"],
        "postimage_sha256": plan["postimage_sha256"],
        "disposable_workspace": plan["disposable_workspace"],
    })
    manifest_capture = create_replacement_implementation_manifest(
        manifest_id=f"G31-REPLACEMENT-MANIFEST-{identity[-24:]}",
        canonical_chain_id=identity,
        implementation_bundle_id=f"G31-REPLACEMENT-BUNDLE-{identity[-24:]}",
        canonical_session_id=root.name,
        source_review_reference=review["sources"]["review"]["review_packet"]["review_id"],
        source_review_hash=review["sources"]["review"]["review_packet"]["artifact_hash"],
        source_review_replay_reference=review["sources"]["review"]["review_replay_reference"],
        source_review_replay_hash=review["sources"]["review"]["review_replay_hash"],
        source_decision_reference=task_outcome_decision_capture["human_decision_capture"][
            "human_decision_artifact"
        ]["human_decision_id"],
        source_decision_hash=plan["task_outcome_decision_hash"],
        source_decision_replay_reference=plan["task_outcome_decision_replay_reference"],
        source_decision_replay_hash=task_decision_replay["replay_hash"],
        application_decision_reference=outcome["application_decision_id"],
        application_decision_hash=outcome["application_decision_hash"],
        application_decision_replay_reference=application_decision_capture[
            "human_decision_replay_reference"
        ],
        application_decision_replay_hash=application_replay["replay_hash"],
        disposable_validation_reference=outcome["outcome_id"],
        disposable_validation_hash=outcome["artifact_hash"],
        disposable_validation_replay_reference=disposable_validation_outcome_capture[
            "outcome_replay_reference"
        ],
        disposable_validation_replay_hash=reconstructed_outcome["replay_hash"],
        source_workspace=str(source),
        disposable_workspace=str(disposable),
        exact_patch=plan["patch_text"],
        patch_sha256=plan["patch_sha256"],
        replacement_files=replacements,
        focused_test_evidence=focused_test,
        validation_requirements=[
            "EXACT_PREIMAGE_AND_POSTIMAGE_SHA256",
            "UNCHANGED_REGULAR_FILE_TYPE_AND_MODE",
            "SUCCESSFUL_DISPOSABLE_CONTENT_VALIDATION",
            "SUCCESSFUL_FIXED_GROUNDED_TEST_VALIDATION",
        ],
        known_gaps=["human generated-content acceptance not yet performed"],
        created_at=_required(created_at, "created_at"),
        replay_dir=replay_path / "implementation_manifest",
    )
    if manifest_capture["manifest_status"] != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError(manifest_capture.get("failure_reason") or "replacement manifest failed closed")
    manifest = manifest_capture["implementation_manifest_artifact"]
    manifest_replay = reconstruct_implementation_manifest_replay(
        manifest_capture["implementation_manifest_replay_reference"]
    )
    content_capture = validate_generated_content(
        validation_id=f"G31-REPLACEMENT-CONTENT-VALIDATION-{identity[-24:]}",
        implementation_manifest_artifact=manifest,
        created_at=created_at,
    )
    if content_capture["validation_status"] != GENERATED_CONTENT_VALIDATED:
        raise FailClosedRuntimeError(content_capture.get("failure_reason") or "replacement content validation failed")
    content_artifact = content_capture["generated_content_validation_artifact"]
    verify_generated_content_validation_artifact(content_artifact)
    test_validation_capture = validate_generated_tests(
        validation_id=f"G31-REPLACEMENT-TEST-VALIDATION-{identity[-24:]}",
        implementation_manifest_artifact=manifest,
        generated_test_bundle=deepcopy(manifest["test_entries"]),
        created_at=created_at,
    )
    if test_validation_capture["validation_status"] != GENERATED_TEST_VALIDATED:
        raise FailClosedRuntimeError(
            test_validation_capture.get("failure_reason") or "replacement test validation failed"
        )
    test_artifact = test_validation_capture["generated_test_validation_artifact"]
    verify_generated_test_validation_artifact(test_artifact)
    prerequisites = bind_generated_content_acceptance_prerequisites(
        prerequisite_id=f"G31-REPLACEMENT-ACCEPTANCE-PREREQUISITES-{identity[-24:]}",
        implementation_manifest_artifact=manifest,
        generated_content_validation_artifact=content_artifact,
        generated_test_validation_artifact=test_artifact,
        created_at=created_at,
    )
    if prerequisites["prerequisite_status"] != ACCEPTANCE_PREREQUISITES_SATISFIED:
        raise FailClosedRuntimeError(prerequisites.get("failure_reason") or "acceptance prerequisites failed closed")
    prerequisite_artifact = prerequisites["acceptance_prerequisite_artifact"]
    verify_generated_content_acceptance_prerequisite_artifact(prerequisite_artifact)
    binding = _binding_artifact(
        identity=identity,
        outcome=outcome,
        manifest=manifest,
        manifest_replay=manifest_replay,
        content=content_artifact,
        tests=test_artifact,
        prerequisites=prerequisite_artifact,
        disposable_workspace=str(disposable),
        created_at=created_at,
    )
    _persist_binding(replay_path, binding)
    capture = {
        "runtime_version": RUNTIME_VERSION,
        "binding_status": BINDING_COMPLETED,
        "binding_artifact": deepcopy(binding),
        "implementation_manifest_capture": deepcopy(manifest_capture),
        "generated_content_validation_capture": deepcopy(content_capture),
        "generated_test_validation_capture": deepcopy(test_validation_capture),
        "acceptance_prerequisite_capture": deepcopy(prerequisites),
        "binding_replay_reference": str(replay_path),
        "replacement_manifest_created": True,
        "content_validation_passed": True,
        "test_validation_passed": True,
        "acceptance_prerequisites_satisfied": True,
        "ready_for_acceptance": True,
        "result_accepted": False,
        "main_repository_mutated": False,
        "mutation_authorized": False,
        "commit_created": False,
        "provider_invoked": False,
        "codex_process_started": False,
        "deployed": False,
        "released": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def reconstruct_codex_replacement_acceptance_prerequisite_binding(
    *, binding_capture: dict[str, Any], session_root: str | Path,
) -> dict[str, Any]:
    root = Path(session_root).resolve()
    replay_path = Path(binding_capture.get("binding_replay_reference", "")).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("replacement prerequisite Replay is cross-session")
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    verify_replay_hash(wrapper)
    artifact = wrapper.get("artifact")
    _verify_artifact(artifact, "replacement prerequisite binding")
    if binding_capture.get("binding_artifact") != artifact:
        raise FailClosedRuntimeError("replacement prerequisite binding capture mismatch")
    manifest_capture = binding_capture["implementation_manifest_capture"]
    manifest = manifest_capture["implementation_manifest_artifact"]
    _verify_artifact(manifest, "replacement implementation manifest")
    manifest_replay = reconstruct_implementation_manifest_replay(
        manifest_capture["implementation_manifest_replay_reference"]
    )
    content = binding_capture["generated_content_validation_capture"][
        "generated_content_validation_artifact"
    ]
    tests = binding_capture["generated_test_validation_capture"]["generated_test_validation_artifact"]
    prerequisite = binding_capture["acceptance_prerequisite_capture"]["acceptance_prerequisite_artifact"]
    verify_generated_content_validation_artifact(content)
    verify_generated_test_validation_artifact(tests)
    verify_generated_content_acceptance_prerequisite_artifact(prerequisite)
    if not all((
        artifact["implementation_manifest_hash"] == manifest_replay["implementation_manifest_hash"],
        artifact["implementation_manifest_hash"] == manifest["implementation_manifest_hash"],
        artifact["generated_content_validation_hash"] == content["generated_content_validation_hash"],
        artifact["generated_test_validation_hash"] == tests["generated_test_validation_hash"],
        artifact["acceptance_prerequisite_hash"] == prerequisite["prerequisite_hash"],
    )):
        raise FailClosedRuntimeError("replacement prerequisite reconstructed identity mismatch")
    return {
        "binding_status": artifact["binding_status"],
        "binding_id": artifact["binding_id"],
        "binding_hash": artifact["artifact_hash"],
        "replay_hash": replay_hash(wrapper),
        "replay_artifact_count": 1,
        "replacement_manifest_created": True,
        "content_validation_passed": True,
        "test_validation_passed": True,
        "acceptance_prerequisites_satisfied": True,
        "ready_for_acceptance": True,
        "result_accepted": False,
        "main_repository_mutated": False,
        "mutation_authorized": False,
    }


def render_codex_replacement_acceptance_prerequisites(
    binding_capture: dict[str, Any], reconstruction: dict[str, Any],
) -> str:
    """Render ready-for-human-acceptance evidence without accepting content."""

    binding = binding_capture.get("binding_artifact") or {}
    manifest = (binding_capture.get("implementation_manifest_capture") or {}).get(
        "implementation_manifest_artifact"
    ) or {}
    _verify_artifact(binding, "replacement prerequisite binding")
    _verify_artifact(manifest, "replacement implementation manifest")
    if reconstruction.get("binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("replacement prerequisite presentation identity mismatch")
    files = []
    for entry in manifest["file_entries"]:
        files.extend((
            f"Target Relative Path: {entry['target_path']}",
            f"Original File SHA-256: {entry['preimage_sha256']}",
            f"Replacement Content SHA-256: {entry['postimage_sha256']}",
        ))
    return "\n".join((
        "Captured Replacement Acceptance Prerequisites",
        f"Operation: {manifest['operation_mode']}",
        *files,
        f"Disposable Execution Result: {COMPLETED}",
        f"Content Validation Passed: {binding['content_validation_passed']}",
        f"Focused Test Validation Passed: {binding['test_validation_passed']}",
        f"Acceptance Prerequisites Satisfied: {binding['acceptance_prerequisites_satisfied']}",
        f"Result Identity: {binding['binding_id']}",
        f"Result Hash: {binding['artifact_hash']}",
        f"Replay Reference: {binding_capture['binding_replay_reference']}",
        f"Replay Hash: {reconstruction['replay_hash']}",
        "Ready For Human Acceptance: True",
        "Result Accepted: False",
        "Mutation Authorized: False",
        "Main Repository Mutated: False",
    ))


def _require_successful_disposable_outcome(
    outcome: Any, reconstructed: dict[str, Any], plan: dict[str, Any],
) -> None:
    if not isinstance(outcome, dict):
        raise FailClosedRuntimeError("replacement prerequisite disposable outcome missing")
    _verify_artifact(outcome, "disposable validation outcome")
    if not all((
        reconstructed.get("execution_status") == COMPLETED,
        outcome.get("execution_status") == COMPLETED,
        outcome.get("task_outcome_satisfied") is True,
        outcome.get("task_outcome_criteria_version") == CRITERIA_VERSION,
        outcome.get("disposable_patch_application_attempted") is True,
        outcome.get("disposable_patch_applied") is True,
        outcome.get("content_validation_passed") is True,
        outcome.get("grounded_test_execution_performed") is True,
        outcome.get("grounded_test_validation_passed") is True,
        outcome.get("source_repository_unchanged") is True,
        outcome.get("main_repository_mutated") is False,
        outcome.get("result_accepted") is False,
        outcome.get("repository_mutation_authorized") is False,
        outcome.get("patch_sha256") == plan.get("patch_sha256"),
        outcome.get("preimage_sha256") == plan.get("preimage_sha256"),
        outcome.get("postimage_sha256") == plan.get("postimage_sha256"),
        outcome.get("changed_paths") == plan.get("changed_paths"),
    )):
        raise FailClosedRuntimeError("replacement prerequisite requires one successful G31-23A outcome")


def _replacement_entries(source: Path, disposable: Path, plan: dict[str, Any]) -> list[dict[str, Any]]:
    entries = []
    for index, relative in enumerate(plan["changed_paths"]):
        source_path = _regular_file(source, relative, "source preimage")
        post_path = _regular_file(disposable, relative, "disposable postimage")
        preimage = _utf8(source_path, "replacement preimage")
        postimage = _utf8(post_path, "replacement postimage")
        pre_hash = _byte_sha256(preimage)
        post_hash = _byte_sha256(postimage)
        if pre_hash != plan["preimage_sha256"].get(relative) or post_hash != plan["postimage_sha256"].get(relative):
            raise FailClosedRuntimeError("replacement prerequisite preimage or postimage substitution")
        source_mode = stat.S_IMODE(source_path.stat().st_mode)
        post_mode = stat.S_IMODE(post_path.stat().st_mode)
        if source_mode != post_mode:
            raise FailClosedRuntimeError("replacement prerequisite file mode changed")
        entries.append({
            "file_entry_id": f"REPLACEMENT-FILE-{index + 1:06d}",
            "target_path": relative,
            "artifact_type": _artifact_type(relative),
            "preimage_content": preimage,
            "preimage_sha256": pre_hash,
            "postimage_content": postimage,
            "postimage_sha256": post_hash,
            "patch_sha256": plan["patch_sha256"],
            "file_mode": source_mode,
            "postimage_file_mode": post_mode,
        })
    return entries


def _focused_test_evidence(
    source: Path, disposable: Path, plan: dict[str, Any], result: dict[str, Any],
    replay: dict[str, Any], replay_reference: str,
) -> dict[str, Any]:
    relative = plan["grounded_test_target"]
    source_path = _regular_file(source, relative, "source focused test")
    disposable_path = _regular_file(disposable, relative, "disposable focused test")
    source_bytes = source_path.read_bytes()
    if source_bytes != disposable_path.read_bytes():
        raise FailClosedRuntimeError("replacement prerequisite focused test content changed")
    if stat.S_IMODE(source_path.stat().st_mode) != stat.S_IMODE(disposable_path.stat().st_mode):
        raise FailClosedRuntimeError("replacement prerequisite focused test mode changed")
    try:
        content = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError("replacement prerequisite focused test must be UTF-8") from exc
    if not all((
        result.get("command_status") == VALIDATION_COMMAND_COMPLETED,
        result.get("exit_code") == 0,
        result.get("command") == plan["grounded_test_command"],
        result.get("cwd") == str(disposable),
        result.get("shell_execution_used") is False,
        result.get("provider_invoked") is False,
        result.get("worker_invoked") is False,
    )):
        raise FailClosedRuntimeError("replacement prerequisite focused test receipt mismatch")
    return {
        "test_entry_id": "EXISTING-FOCUSED-TEST-000001",
        "target_path": relative,
        "content": content,
        "content_sha256": _byte_sha256(content),
        "file_mode": stat.S_IMODE(source_path.stat().st_mode),
        "validation_command": deepcopy(plan["grounded_test_command"]),
        "validation_result_artifact": deepcopy(result),
        "validation_replay_reference": replay_reference,
        "validation_replay_hash": replay["replay_hash"],
    }


def _binding_artifact(
    *, identity: str, outcome: dict[str, Any], manifest: dict[str, Any],
    manifest_replay: dict[str, Any], content: dict[str, Any], tests: dict[str, Any],
    prerequisites: dict[str, Any], disposable_workspace: str, created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": BINDING_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "binding_id": f"G31-REPLACEMENT-PREREQUISITE-BINDING-{identity[-24:]}",
        "binding_identity": identity,
        "binding_status": BINDING_COMPLETED,
        "source_disposable_validation_reference": outcome["outcome_id"],
        "source_disposable_validation_hash": outcome["artifact_hash"],
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "implementation_manifest_replay_hash": manifest_replay["replay_hash"],
        "generated_content_validation_reference": content["validation_id"],
        "generated_content_validation_hash": content["generated_content_validation_hash"],
        "generated_test_validation_reference": tests["validation_id"],
        "generated_test_validation_hash": tests["generated_test_validation_hash"],
        "acceptance_prerequisite_reference": prerequisites["prerequisite_id"],
        "acceptance_prerequisite_hash": prerequisites["prerequisite_hash"],
        "operation": REPLACE_CONTENT,
        "patch_sha256": manifest["patch_sha256"],
        "preimage_sha256": {entry["target_path"]: entry["preimage_sha256"] for entry in manifest["file_entries"]},
        "postimage_sha256": {entry["target_path"]: entry["postimage_sha256"] for entry in manifest["file_entries"]},
        "disposable_workspace": disposable_workspace,
        "replacement_manifest_created": True,
        "content_validation_passed": True,
        "test_validation_passed": True,
        "acceptance_prerequisites_satisfied": True,
        "ready_for_acceptance": True,
        "result_accepted": False,
        "main_repository_mutated": False,
        "mutation_authorized": False,
        "acceptance_owner_called": False,
        "main_repository_mutation_owner_called": False,
        "commit_created": False,
        "provider_invoked": False,
        "codex_process_started": False,
        "deployed": False,
        "released": False,
        "created_at": _required(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _regular_file(root: Path, relative: str, label: str) -> Path:
    candidate = root / relative
    path = candidate.resolve()
    if candidate.is_symlink() or not path.is_relative_to(root.resolve()) or not path.is_file():
        raise FailClosedRuntimeError(f"replacement prerequisite {label} must be a grounded regular file")
    if stat.S_ISREG(path.stat().st_mode) is not True:
        raise FailClosedRuntimeError(f"replacement prerequisite {label} file type invalid")
    return path


def _utf8(path: Path, label: str) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError(f"{label} must be UTF-8") from exc


def _repository_file_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(root.resolve().rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root.resolve())
        if relative.parts and relative.parts[0] == ".git":
            continue
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        hashes[relative.as_posix()] = "sha256:" + sha256(path.read_bytes()).hexdigest()
    return hashes


def _artifact_type(path: str) -> str:
    if path.startswith("tests/") and path.endswith(".py"):
        return "PYTEST_TEST"
    if path.endswith(".py"):
        return "PYTHON_RUNTIME_MODULE"
    if path.endswith(".md"):
        return "GOVERNANCE_DOCUMENT_MARKDOWN"
    if path.endswith(".json"):
        return "JSON_GOVERNANCE_ARTIFACT"
    raise FailClosedRuntimeError("replacement prerequisite target artifact type is not canonical")


def _byte_sha256(value: str) -> str:
    return "sha256:" + sha256(value.encode("utf-8")).hexdigest()


def _ensure_destination_available(path: Path) -> None:
    if (path / f"000_{REPLAY_STEP}.json").exists() or (path / "implementation_manifest").exists():
        raise FailClosedRuntimeError("replacement prerequisite destination already exists")


def _reject_repeated_consumption(root: Path, outcome_hash: str) -> None:
    for path in root.rglob(f"000_{REPLAY_STEP}.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        if (wrapper.get("artifact") or {}).get("source_disposable_validation_hash") == outcome_hash:
            raise FailClosedRuntimeError("replacement prerequisite disposable outcome already consumed")


def _persist_binding(path: Path, artifact: dict[str, Any]) -> None:
    wrapper = {
        "event_type": REPLAY_STEP.upper(),
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"000_{REPLAY_STEP}.json", wrapper)


def _verify_artifact(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{label} missing")
    candidate = deepcopy(value)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _required(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"replacement prerequisite {label} required")
    return value.strip()


__all__ = [
    "BINDING_COMPLETED",
    "REPLACE_CONTENT",
    "bind_codex_replacement_acceptance_prerequisites",
    "reconstruct_codex_replacement_acceptance_prerequisite_binding",
    "render_codex_replacement_acceptance_prerequisites",
]
