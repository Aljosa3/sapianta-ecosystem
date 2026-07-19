"""Human acceptance gate for validated generated implementation content."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.generated_content_validation_runtime import (
    GENERATED_CONTENT_VALIDATED,
    GENERATED_CONTENT_VALIDATION_ARTIFACT_V1,
    GENERATED_CONTENT_VALIDATION_ARTIFACT_V2,
    verify_generated_content_validation_artifact,
)
from aigol.runtime.generated_test_validation_runtime import (
    GENERATED_TEST_VALIDATED,
    GENERATED_TEST_VALIDATION_ARTIFACT_V1,
    GENERATED_TEST_VALIDATION_ARTIFACT_V2,
    verify_generated_test_validation_artifact,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V2,
    IMPLEMENTATION_MANIFEST_CREATED,
    REPLACE_CONTENT,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_VERSION = "AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_V1"
GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1 = "GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1"
GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_ARTIFACT_V2 = (
    "GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_ARTIFACT_V2"
)
ACCEPTANCE_PREREQUISITES_SATISFIED = "ACCEPTANCE_PREREQUISITES_SATISFIED"
AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_STATUS = "CERTIFIED"
GENERATED_CONTENT_ACCEPTED = "GENERATED_CONTENT_ACCEPTED"
FAILED_CLOSED = "FAILED_CLOSED"
CONTENT_ACCEPTANCE_REPLAY_STEP = "generated_content_acceptance_from_decision_recorded"

ACCEPTANCE_DECISION = "ACCEPTED"
ACCEPTANCE_SCOPE = "CONTENT_ACCEPTANCE_ONLY"
ACCEPTANCE_STATEMENT = (
    "I accept this generated content for the bound implementation manifest and validation evidence."
)

FORBIDDEN_OPERATIONS = (
    "FILESYSTEM_MUTATION",
    "PROVIDER_INVOCATION",
    "WORKER_INVOCATION",
    "EXECUTION_AUTHORIZATION",
    "DISPATCH",
    "AUTOMATIC_APPROVAL_INFERENCE",
    "APPROVAL_CREATION",
    "GOVERNANCE_MUTATION",
    "REPLAY_MUTATION",
)

AUTHORITY_FLAGS = {
    "authorizes_filesystem_mutation": False,
    "authorizes_provider_invocation": False,
    "authorizes_worker_invocation": False,
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "infers_approval_automatically": False,
    "creates_approval": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
}


def bind_generated_content_acceptance_prerequisites(
    *,
    prerequisite_id: str,
    implementation_manifest_artifact: dict[str, Any],
    generated_content_validation_artifact: dict[str, Any],
    generated_test_validation_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Bind V2 replacement prerequisites without performing human acceptance."""

    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        if manifest.get("artifact_type") != IMPLEMENTATION_MANIFEST_ARTIFACT_V2:
            raise FailClosedRuntimeError(
                "generated content acceptance prerequisites failed closed: V2 replacement manifest required"
            )
        content = _validate_content_validation(generated_content_validation_artifact, manifest)
        tests = _validate_test_validation(generated_test_validation_artifact, manifest)
        status = ACCEPTANCE_PREREQUISITES_SATISFIED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        content = _validation_stub(generated_content_validation_artifact, "generated_content_validation_hash")
        tests = _validation_stub(generated_test_validation_artifact, "generated_test_validation_hash")
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)
    artifact = {
        "artifact_type": GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_ARTIFACT_V2,
        "runtime_version": "AIGOL_GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_RUNTIME_V2",
        "prerequisite_id": _safe_string(prerequisite_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "prerequisite_status": status,
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "generated_content_validation_reference": content["validation_id"],
        "generated_content_validation_artifact_hash": content["artifact_hash"],
        "generated_content_validation_hash": content["generated_content_validation_hash"],
        "generated_test_validation_reference": tests["validation_id"],
        "generated_test_validation_artifact_hash": tests["artifact_hash"],
        "generated_test_validation_hash": tests["generated_test_validation_hash"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "operation_mode": manifest["operation_mode"],
        "replacement_manifest_created": status == ACCEPTANCE_PREREQUISITES_SATISFIED,
        "content_validation_passed": status == ACCEPTANCE_PREREQUISITES_SATISFIED,
        "test_validation_passed": status == ACCEPTANCE_PREREQUISITES_SATISFIED,
        "acceptance_prerequisites_satisfied": status == ACCEPTANCE_PREREQUISITES_SATISFIED,
        "ready_for_acceptance": status == ACCEPTANCE_PREREQUISITES_SATISFIED,
        "result_accepted": False,
        "main_repository_mutated": False,
        "mutation_authorized": False,
        "commit_created": False,
        "deployed": False,
        "released": False,
        "acceptance_owner_called": False,
        "read_only": True,
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["prerequisite_hash"] = _compute_prerequisite_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "acceptance_prerequisite_artifact": deepcopy(artifact),
        "prerequisite_status": status,
        "acceptance_prerequisites_satisfied": artifact["acceptance_prerequisites_satisfied"],
        "ready_for_acceptance": artifact["ready_for_acceptance"],
        "result_accepted": False,
        "main_repository_mutated": False,
        "mutation_authorized": False,
        "failure_reason": failure_reason,
    }


def verify_generated_content_acceptance_prerequisite_artifact(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != (
        GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_ARTIFACT_V2
    ):
        raise FailClosedRuntimeError("generated content acceptance prerequisite artifact type mismatch")
    if artifact.get("prerequisite_hash") != _compute_prerequisite_hash(artifact):
        raise FailClosedRuntimeError("generated content acceptance prerequisite hash mismatch")
    actual = artifact.get("artifact_hash")
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    if actual != replay_hash(value):
        raise FailClosedRuntimeError("generated content acceptance prerequisite artifact hash mismatch")


def accept_generated_content(
    *,
    acceptance_id: str,
    implementation_manifest_artifact: dict[str, Any],
    generated_content_validation_artifact: dict[str, Any],
    generated_test_validation_artifact: dict[str, Any],
    human_acceptance_evidence: dict[str, Any],
    created_at: str,
    prior_acceptance_lineage_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Create a non-authorizing human acceptance artifact for validated generated content."""

    try:
        manifest = _validate_manifest(implementation_manifest_artifact)
        content_validation = _validate_content_validation(generated_content_validation_artifact, manifest)
        test_validation = _validate_test_validation(generated_test_validation_artifact, manifest)
        human = _validate_human_acceptance(human_acceptance_evidence)
        acceptance_lineage_key = _acceptance_lineage_key(manifest, content_validation, test_validation)
        if acceptance_lineage_key in _string_list(
            prior_acceptance_lineage_keys or [],
            "prior_acceptance_lineage_keys",
            allow_empty=True,
        ):
            raise FailClosedRuntimeError("generated content acceptance failed closed: acceptance lineage already used")
        checks = _validation_checks()
        status = GENERATED_CONTENT_ACCEPTED
        failure_reason = None
    except Exception as exc:
        manifest = _manifest_stub(implementation_manifest_artifact)
        content_validation = _validation_stub(generated_content_validation_artifact, "generated_content_validation_hash")
        test_validation = _validation_stub(generated_test_validation_artifact, "generated_test_validation_hash")
        human = _human_stub(human_acceptance_evidence)
        acceptance_lineage_key = "UNKNOWN"
        checks = _failed_checks()
        status = FAILED_CLOSED
        failure_reason = _failure_reason(exc)

    artifact = {
        "artifact_type": GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1,
        "runtime_version": AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_VERSION,
        "acceptance_id": _safe_string(acceptance_id, "UNKNOWN"),
        "created_at": _safe_string(created_at, "UNKNOWN"),
        "acceptance_status": status,
        "implementation_manifest_reference": manifest["manifest_id"],
        "implementation_manifest_artifact_hash": manifest["artifact_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "generated_content_validation_reference": content_validation["validation_id"],
        "generated_content_validation_artifact_hash": content_validation["artifact_hash"],
        "generated_content_validation_hash": content_validation["generated_content_validation_hash"],
        "generated_test_validation_reference": test_validation["validation_id"],
        "generated_test_validation_artifact_hash": test_validation["artifact_hash"],
        "generated_test_validation_hash": test_validation["generated_test_validation_hash"],
        "canonical_chain_id": manifest["canonical_chain_id"],
        "implementation_bundle_id": manifest["implementation_bundle_id"],
        "operation_mode": manifest["operation_mode"],
        "acceptance_lineage_key": acceptance_lineage_key,
        "acceptance_reuse_prohibited": True,
        "acceptance_scope": human["acceptance_scope"],
        "human_actor_id": human["actor_id"],
        "human_decision": human["decision"],
        "human_accepted_at": human["accepted_at"],
        "human_acceptance_statement": human["acceptance_statement"],
        "validation_checks": checks,
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "automatic_approval_inferred": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["generated_content_acceptance_hash"] = _compute_acceptance_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return {
        "generated_content_acceptance_artifact": deepcopy(artifact),
        "generated_content_acceptance_hash": artifact["generated_content_acceptance_hash"],
        "acceptance_lineage_key": artifact["acceptance_lineage_key"],
        "acceptance_status": artifact["acceptance_status"],
        "implementation_manifest_reference": artifact["implementation_manifest_reference"],
        "implementation_bundle_id": artifact["implementation_bundle_id"],
        "read_only": True,
        "replay_visible": True,
        "filesystem_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "automatic_approval_inferred": False,
        "fail_closed": artifact["acceptance_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "final_classification": (
            "AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_STATUS = "
            f"{AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_STATUS}"
        ),
    }


def verify_generated_content_acceptance_artifact(artifact: dict[str, Any]) -> None:
    """Verify a generated-content acceptance artifact hash."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("generated content acceptance artifact must be a JSON object")
    if artifact.get("artifact_type") != GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("generated content acceptance artifact type mismatch")
    actual_acceptance_hash = artifact.get("generated_content_acceptance_hash")
    if actual_acceptance_hash != _compute_acceptance_hash(artifact):
        raise FailClosedRuntimeError("generated content acceptance hash mismatch")
    actual_artifact_hash = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual_artifact_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("generated content acceptance artifact hash mismatch")


def accept_generated_content_from_content_acceptance_decision(
    *, acceptance_id: str, decision_capture: dict[str, Any], binding_capture: dict[str, Any], created_at: str,
    session_root: str | Path, replay_dir: str | Path,) -> dict[str, Any]:
    """Consume one exact V2 ACCEPTED decision through the existing acceptance owner."""
    root, path = Path(session_root).resolve(), Path(replay_dir).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("generated content acceptance decision Replay is cross-session")
    replay_path = path / f"000_{CONTENT_ACCEPTANCE_REPLAY_STEP}.json"
    if replay_path.exists():
        raise FailClosedRuntimeError("generated content acceptance decision destination already exists")
    decision, context, reconstructed = _validated_content_acceptance_decision(decision_capture, binding_capture, root)
    prior_keys = _prior_decision_acceptance_lineage(root, decision["artifact_hash"])
    manifest, content, tests = _replacement_acceptance_inputs(binding_capture)
    acceptance = accept_generated_content(acceptance_id=acceptance_id,
        implementation_manifest_artifact=manifest, generated_content_validation_artifact=content,
        generated_test_validation_artifact=tests,
        human_acceptance_evidence={
            "actor_id": decision["decided_by"], "decision": ACCEPTANCE_DECISION,
            "accepted_at": decision["decided_at"], "acceptance_scope": ACCEPTANCE_SCOPE,
            "acceptance_statement": ACCEPTANCE_STATEMENT},
        created_at=created_at, prior_acceptance_lineage_keys=prior_keys)
    artifact = acceptance["generated_content_acceptance_artifact"]
    verify_generated_content_acceptance_artifact(artifact)
    if acceptance.get("acceptance_status") != GENERATED_CONTENT_ACCEPTED:
        raise FailClosedRuntimeError(acceptance.get("failure_reason") or "generated content acceptance failed closed")
    wrapper = {
        "replay_index": 0, "replay_step": CONTENT_ACCEPTANCE_REPLAY_STEP,
        "event_type": CONTENT_ACCEPTANCE_REPLAY_STEP.upper(), "artifact": deepcopy(artifact),
        "human_decision_reference": decision["human_decision_id"], "human_decision_hash": decision["artifact_hash"],
        "human_decision_replay_reference": decision_capture["human_decision_replay_reference"],
        "human_decision_replay_hash": reconstructed["replay_hash"], "subject_binding_hash": context["subject_binding_hash"],
        "result_accepted": True, "mutation_authorized": False, "main_repository_mutated": False,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path, wrapper)
    capture = deepcopy(acceptance)
    capture.update({"human_decision_reference": decision["human_decision_id"], "human_decision_hash": decision["artifact_hash"],
        "human_decision_replay_reference": decision_capture["human_decision_replay_reference"],
        "acceptance_replay_reference": str(path), "acceptance_replay_hash": wrapper["replay_hash"],
        "result_accepted": True, "mutation_authorized": False, "main_repository_mutated": False})
    return capture


def reconstruct_generated_content_acceptance_from_decision_replay(
    *, acceptance_capture: dict[str, Any], decision_capture: dict[str, Any], binding_capture: dict[str, Any],
    session_root: str | Path,) -> dict[str, Any]:
    """Reconstruct one accepted-result wrapper and its exact human authority."""
    root = Path(session_root).resolve()
    path = Path(acceptance_capture.get("acceptance_replay_reference", "")).resolve()
    if not path.is_relative_to(root):
        raise FailClosedRuntimeError("generated content acceptance Replay is cross-session")
    wrapper = load_json(path / f"000_{CONTENT_ACCEPTANCE_REPLAY_STEP}.json")
    _verify_acceptance_replay_wrapper(wrapper)
    decision, context, reconstructed = _validated_content_acceptance_decision(decision_capture, binding_capture, root)
    artifact = wrapper.get("artifact")
    verify_generated_content_acceptance_artifact(artifact)
    manifest, content, tests = _replacement_acceptance_inputs(binding_capture)
    checks = (acceptance_capture.get("generated_content_acceptance_artifact") == artifact,
        artifact.get("acceptance_status") == GENERATED_CONTENT_ACCEPTED,
        artifact.get("implementation_manifest_artifact_hash") == manifest.get("artifact_hash"),
        artifact.get("generated_content_validation_artifact_hash") == content.get("artifact_hash"),
        artifact.get("generated_test_validation_artifact_hash") == tests.get("artifact_hash"),
        artifact.get("human_actor_id") == decision.get("decided_by"), artifact.get("human_decision") == decision.get("decision_outcome"),
        artifact.get("human_accepted_at") == decision.get("decided_at"),
        wrapper.get("human_decision_reference") == decision.get("human_decision_id"),
        wrapper.get("human_decision_hash") == decision.get("artifact_hash"),
        wrapper.get("human_decision_replay_hash") == reconstructed.get("replay_hash"),
        wrapper.get("subject_binding_hash") == context.get("subject_binding_hash"),
        wrapper.get("result_accepted") is True, wrapper.get("mutation_authorized") is False,
        wrapper.get("main_repository_mutated") is False)
    if not all(checks):
        raise FailClosedRuntimeError("generated content acceptance decision Replay identity mismatch")
    return {"acceptance_id": artifact["acceptance_id"], "acceptance_status": artifact["acceptance_status"],
        "acceptance_lineage_key": artifact["acceptance_lineage_key"],
        "human_decision_reference": decision["human_decision_id"], "result_accepted": True,
        "mutation_authorized": False, "main_repository_mutated": False,
        "replay_artifact_count": 1, "replay_hash": wrapper["replay_hash"]}


def render_generated_content_acceptance_from_decision(
    acceptance_capture: dict[str, Any], binding_capture: dict[str, Any],) -> str:
    """Render accepted content without implying source application."""
    artifact = acceptance_capture.get("generated_content_acceptance_artifact") or {}
    verify_generated_content_acceptance_artifact(artifact)
    manifest, _, _ = _replacement_acceptance_inputs(binding_capture)
    files = manifest["file_entries"]
    return "\n".join(("Generated Content Accepted",
        f"Accepted Result: {artifact['acceptance_id']}", f"Operation: {manifest['operation_mode']}",
        *(f"Target: {item['target_path']} {item['preimage_sha256']} -> {item['postimage_sha256']}" for item in files),
        f"Human Decision: {acceptance_capture['human_decision_reference']}",
        f"Human Decision Replay: {acceptance_capture['human_decision_replay_reference']}",
        f"Acceptance Replay: {acceptance_capture['acceptance_replay_reference']}",
        "Result Accepted: True", "Mutation Authorized: False", "Main Repository Mutated: False",
        "The validated result is accepted; repository mutation has not occurred."))


def _validated_content_acceptance_decision(
    decision_capture: dict[str, Any], binding_capture: dict[str, Any], root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    from aigol.runtime import human_decision_runtime as human_decision
    if not isinstance(decision_capture, dict) or not isinstance(binding_capture, dict): raise FailClosedRuntimeError("exact V2 content-acceptance evidence required")
    reconstructed = human_decision.reconstruct_content_acceptance_decision_replay(
        decision_capture=decision_capture, binding_capture=binding_capture, session_root=root,
    )
    decision = decision_capture.get("human_decision_artifact") or {}
    context = decision_capture.get("content_acceptance_context_artifact") or {}
    _verify_artifact_hash(decision, "human content-acceptance decision")
    _verify_artifact_hash(context, "human content-acceptance context")
    false_fields = ("result_accepted", "mutation_authorized", "main_repository_mutated",
                    "execution_authorized", "provider_invoked", "worker_invoked",
                    "command_executed", "patch_applied", "automatic_approval")
    checks = (decision.get("artifact_type") == human_decision.HUMAN_DECISION_ARTIFACT_V2,
        decision.get("decision_type") == human_decision.CONTENT_ACCEPTANCE,
        decision.get("decision_scope") == human_decision.CONTENT_ACCEPTANCE_ONLY,
        decision.get("decision_outcome") == human_decision.ACCEPTED, reconstructed.get("decision_outcome") == human_decision.ACCEPTED,
        decision.get("context_hash") == context.get("artifact_hash"), decision.get("decided_by") == context.get("human_actor_id"),
        decision.get("subject_binding_hash") == context.get("subject_binding_hash"),
        all(decision.get(field) is False for field in false_fields))
    if not all(checks):
        raise FailClosedRuntimeError("exact V2 ACCEPTED content-acceptance decision required")
    return decision, context, reconstructed


def _replacement_acceptance_inputs(
    binding_capture: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    try:
        manifest = binding_capture["implementation_manifest_capture"]["implementation_manifest_artifact"]
        content = binding_capture["generated_content_validation_capture"]["generated_content_validation_artifact"]
        tests = binding_capture["generated_test_validation_capture"]["generated_test_validation_artifact"]
    except (KeyError, TypeError) as exc:
        raise FailClosedRuntimeError("generated content acceptance binding inputs missing") from exc
    return manifest, content, tests


def _prior_decision_acceptance_lineage(root: Path, decision_hash: str) -> list[str]:
    keys = []
    for path in root.rglob(f"000_{CONTENT_ACCEPTANCE_REPLAY_STEP}.json"):
        wrapper = load_json(path); _verify_acceptance_replay_wrapper(wrapper)
        artifact = wrapper.get("artifact") or {}; verify_generated_content_acceptance_artifact(artifact)
        if wrapper.get("human_decision_hash") == decision_hash:
            raise FailClosedRuntimeError("human content-acceptance decision already consumed")
        keys.append(artifact["acceptance_lineage_key"])
    return keys


def _verify_acceptance_replay_wrapper(wrapper: dict[str, Any]) -> None:
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != CONTENT_ACCEPTANCE_REPLAY_STEP:
        raise FailClosedRuntimeError("generated content acceptance Replay ordering mismatch")
    actual = wrapper.get("replay_hash"); value = deepcopy(wrapper); value.pop("replay_hash", None)
    if actual != replay_hash(value):
        raise FailClosedRuntimeError("generated content acceptance Replay hash mismatch")


def _validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("generated content acceptance failed closed: manifest must be a JSON object")
    manifest = deepcopy(value)
    artifact_type = manifest.get("artifact_type")
    if artifact_type not in {IMPLEMENTATION_MANIFEST_ARTIFACT_V1, IMPLEMENTATION_MANIFEST_ARTIFACT_V2}:
        raise FailClosedRuntimeError("generated content acceptance failed closed: invalid manifest artifact type")
    if manifest.get("manifest_status") != IMPLEMENTATION_MANIFEST_CREATED:
        raise FailClosedRuntimeError("generated content acceptance failed closed: manifest is not created")
    expected_operation = CREATE_ONLY if artifact_type == IMPLEMENTATION_MANIFEST_ARTIFACT_V1 else REPLACE_CONTENT
    if manifest.get("operation_mode") != expected_operation:
        if artifact_type == IMPLEMENTATION_MANIFEST_ARTIFACT_V1:
            raise FailClosedRuntimeError("generated content acceptance failed closed: manifest must be CREATE_ONLY")
        raise FailClosedRuntimeError("generated content acceptance failed closed: manifest must be REPLACE_CONTENT")
    _verify_artifact_hash(manifest, "manifest")
    if manifest.get("implementation_manifest_hash") != _compute_manifest_hash(manifest):
        raise FailClosedRuntimeError("generated content acceptance failed closed: manifest hash mismatch")
    return manifest


def _validate_content_validation(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("generated content acceptance failed closed: content validation missing")
    validation = deepcopy(artifact)
    verify_generated_content_validation_artifact(validation)
    expected_type = (
        GENERATED_CONTENT_VALIDATION_ARTIFACT_V2
        if manifest["operation_mode"] == REPLACE_CONTENT
        else GENERATED_CONTENT_VALIDATION_ARTIFACT_V1
    )
    if validation.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError("generated content acceptance failed closed: invalid content validation artifact")
    if validation.get("validation_status") != GENERATED_CONTENT_VALIDATED:
        raise FailClosedRuntimeError("generated content acceptance failed closed: content validation not successful")
    _require_manifest_binding(validation, manifest, "content validation")
    return validation


def _validate_test_validation(artifact: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("generated content acceptance failed closed: test validation missing")
    validation = deepcopy(artifact)
    verify_generated_test_validation_artifact(validation)
    expected_type = (
        GENERATED_TEST_VALIDATION_ARTIFACT_V2
        if manifest["operation_mode"] == REPLACE_CONTENT
        else GENERATED_TEST_VALIDATION_ARTIFACT_V1
    )
    if validation.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError("generated content acceptance failed closed: invalid test validation artifact")
    if validation.get("validation_status") != GENERATED_TEST_VALIDATED:
        raise FailClosedRuntimeError("generated content acceptance failed closed: test validation not successful")
    _require_manifest_binding(validation, manifest, "test validation")
    return validation


def _require_manifest_binding(validation: dict[str, Any], manifest: dict[str, Any], label: str) -> None:
    if validation.get("implementation_manifest_reference") != manifest["manifest_id"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} manifest reference mismatch")
    if validation.get("implementation_manifest_artifact_hash") != manifest["artifact_hash"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} manifest artifact hash mismatch")
    if validation.get("implementation_manifest_hash") != manifest["implementation_manifest_hash"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} manifest hash mismatch")
    if validation.get("canonical_chain_id") != manifest["canonical_chain_id"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} chain mismatch")
    if validation.get("implementation_bundle_id") != manifest["implementation_bundle_id"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} bundle mismatch")
    if validation.get("operation_mode") != manifest["operation_mode"]:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} operation mismatch")


def _validate_human_acceptance(evidence: dict[str, Any]) -> dict[str, str]:
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("generated content acceptance failed closed: human acceptance evidence missing")
    actor_id = _require_string(evidence.get("actor_id"), "actor_id")
    decision = _require_string(evidence.get("decision"), "decision")
    accepted_at = _require_string(evidence.get("accepted_at"), "accepted_at")
    acceptance_scope = _require_string(evidence.get("acceptance_scope"), "acceptance_scope")
    acceptance_statement = _require_string(evidence.get("acceptance_statement"), "acceptance_statement")
    if decision != ACCEPTANCE_DECISION:
        raise FailClosedRuntimeError("generated content acceptance failed closed: human acceptance decision required")
    if acceptance_scope != ACCEPTANCE_SCOPE:
        raise FailClosedRuntimeError("generated content acceptance failed closed: acceptance scope mismatch")
    if acceptance_statement != ACCEPTANCE_STATEMENT:
        raise FailClosedRuntimeError("generated content acceptance failed closed: explicit acceptance statement required")
    return {
        "actor_id": actor_id,
        "decision": decision,
        "accepted_at": accepted_at,
        "acceptance_scope": acceptance_scope,
        "acceptance_statement": acceptance_statement,
    }


def _acceptance_lineage_key(
    manifest: dict[str, Any],
    content_validation: dict[str, Any],
    test_validation: dict[str, Any],
) -> str:
    return replay_hash(
        {
            "implementation_manifest_hash": manifest["implementation_manifest_hash"],
            "generated_content_validation_hash": content_validation["generated_content_validation_hash"],
            "generated_test_validation_hash": test_validation["generated_test_validation_hash"],
        }
    )


def _validation_checks() -> dict[str, bool]:
    return {
        "manifest_binding_valid": True,
        "content_validation_binding_valid": True,
        "test_validation_binding_valid": True,
        "human_acceptance_explicit": True,
        "acceptance_reuse_prevented": True,
        "lineage_replay_visible": True,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "execution_authorization_absent": True,
        "automatic_approval_inference_absent": True,
    }


def _failed_checks() -> dict[str, bool]:
    return {
        "manifest_binding_valid": False,
        "content_validation_binding_valid": False,
        "test_validation_binding_valid": False,
        "human_acceptance_explicit": False,
        "acceptance_reuse_prevented": False,
        "lineage_replay_visible": True,
        "filesystem_mutation_absent": True,
        "provider_invocation_absent": True,
        "worker_invocation_absent": True,
        "execution_authorization_absent": True,
        "automatic_approval_inference_absent": True,
    }


def _manifest_stub(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            "manifest_id": _safe_string(value.get("manifest_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            "implementation_manifest_hash": _safe_string(value.get("implementation_manifest_hash"), "UNKNOWN"),
            "canonical_chain_id": _safe_string(value.get("canonical_chain_id"), "UNKNOWN"),
            "implementation_bundle_id": _safe_string(value.get("implementation_bundle_id"), "UNKNOWN"),
            "operation_mode": _safe_string(value.get("operation_mode"), "UNKNOWN"),
        }
    return {
        "manifest_id": "UNKNOWN",
        "artifact_hash": "UNKNOWN",
        "implementation_manifest_hash": "UNKNOWN",
        "canonical_chain_id": "UNKNOWN",
        "implementation_bundle_id": "UNKNOWN",
        "operation_mode": "UNKNOWN",
    }


def _validation_stub(value: Any, hash_field: str) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "validation_id": _safe_string(value.get("validation_id"), "UNKNOWN"),
            "artifact_hash": _safe_string(value.get("artifact_hash"), "UNKNOWN"),
            hash_field: _safe_string(value.get(hash_field), "UNKNOWN"),
        }
    return {"validation_id": "UNKNOWN", "artifact_hash": "UNKNOWN", hash_field: "UNKNOWN"}


def _human_stub(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "actor_id": _safe_string(value.get("actor_id"), "UNKNOWN"),
            "decision": _safe_string(value.get("decision"), "UNKNOWN"),
            "accepted_at": _safe_string(value.get("accepted_at"), "UNKNOWN"),
            "acceptance_scope": _safe_string(value.get("acceptance_scope"), "UNKNOWN"),
            "acceptance_statement": _safe_string(value.get("acceptance_statement"), "UNKNOWN"),
        }
    return {
        "actor_id": "UNKNOWN",
        "decision": "UNKNOWN",
        "accepted_at": "UNKNOWN",
        "acceptance_scope": "UNKNOWN",
        "acceptance_statement": "UNKNOWN",
    }


def _compute_acceptance_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    value.pop("generated_content_acceptance_hash", None)
    return replay_hash(value)


def _compute_prerequisite_hash(artifact: dict[str, Any]) -> str:
    value = deepcopy(artifact)
    value.pop("artifact_hash", None)
    value.pop("prerequisite_hash", None)
    return replay_hash(value)


def _compute_manifest_hash(manifest: dict[str, Any]) -> str:
    if manifest.get("artifact_type") == IMPLEMENTATION_MANIFEST_ARTIFACT_V2:
        value = deepcopy(manifest)
        value.pop("implementation_manifest_hash", None)
        value.pop("artifact_hash", None)
        return replay_hash(value)
    return replay_hash(
        {
            "manifest_id": manifest["manifest_id"],
            "canonical_chain_id": manifest["canonical_chain_id"],
            "implementation_bundle_id": manifest["implementation_bundle_id"],
            "source_candidate_reference": manifest["source_candidate_reference"],
            "source_candidate_hash": manifest["source_candidate_hash"],
            "implementation_handoff_reference": manifest["implementation_handoff_reference"],
            "implementation_handoff_hash": manifest["implementation_handoff_hash"],
            "provider_generation_authorization_reference": manifest[
                "provider_generation_authorization_reference"
            ],
            "provider_generation_authorization_hash": manifest["provider_generation_authorization_hash"],
            "provider_response_reference": manifest["provider_response_reference"],
            "provider_response_hash": manifest["provider_response_hash"],
            "target_domain": manifest["target_domain"],
            "target_resource": manifest["target_resource"],
            "target_worker": manifest["target_worker"],
            "operation_mode": manifest["operation_mode"],
            "file_entries": manifest["file_entries"],
            "test_entries": manifest["test_entries"],
            "validation_requirements": manifest["validation_requirements"],
            "forbidden_operations": manifest["forbidden_operations"],
            "known_gaps": manifest["known_gaps"],
            "manifest_status": manifest["manifest_status"],
            "read_only": manifest["read_only"],
            "content_bearing_manifest": manifest["content_bearing_manifest"],
            "filesystem_mutated": manifest["filesystem_mutated"],
            "execution_authorized": manifest["execution_authorized"],
            "provider_invoked": manifest["provider_invoked"],
            "worker_invoked": manifest["worker_invoked"],
            "approval_created": manifest["approval_created"],
            "authority_flags": manifest["authority_flags"],
            "failure_reason": manifest["failure_reason"],
        }
    )


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} artifact hash mismatch")


def _string_list(value: Any, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} must be a list")
    normalized = [_require_string(item, label) for item in value]
    if not allow_empty and not normalized:
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} required")
    return sorted(dict.fromkeys(normalized))


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"generated content acceptance failed closed: {label} missing")
    return value.strip()


def _safe_string(value: Any, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "generated content acceptance failed closed"


__all__ = [
    "ACCEPTANCE_DECISION",
    "ACCEPTANCE_SCOPE",
    "ACCEPTANCE_STATEMENT",
    "AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_STATUS",
    "AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_VERSION",
    "FAILED_CLOSED",
    "ACCEPTANCE_PREREQUISITES_SATISFIED",
    "GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1",
    "GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_ARTIFACT_V2",
    "GENERATED_CONTENT_ACCEPTED",
    "accept_generated_content",
    "accept_generated_content_from_content_acceptance_decision",
    "bind_generated_content_acceptance_prerequisites",
    "reconstruct_generated_content_acceptance_from_decision_replay",
    "render_generated_content_acceptance_from_decision",
    "verify_generated_content_acceptance_artifact",
    "verify_generated_content_acceptance_prerequisite_artifact",
]
