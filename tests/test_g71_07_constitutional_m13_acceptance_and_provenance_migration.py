from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import (
    codex_replacement_acceptance_prerequisite_binding_runtime as prerequisites,
)
from aigol.runtime import generated_content_acceptance_runtime as acceptance
from aigol.runtime import human_decision_runtime as human_decision
from aigol.runtime import implementation_manifest_runtime as manifests
from aigol.runtime import platform_core_existing_file_mutation_candidate as provenance
from aigol.runtime.approved_durable_work_repository_scope_grounding import (
    ground_approved_durable_work_repository_scope,
)
from aigol.runtime.approved_durable_work_worker_payload_binding import (
    bind_approved_durable_work_to_worker_payload,
)
from aigol.runtime.generated_content_validation_runtime import (
    GENERATED_CONTENT_VALIDATED,
    validate_generated_content,
)
from aigol.runtime.generated_test_validation_runtime import (
    GENERATED_TEST_VALIDATED,
    validate_generated_tests,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    consume_approved_implementation_turn_binding,
)
from aigol.runtime.transport.serialization import replay_hash
from test_g64_04_constitutional_reuse_proof_production_integration import (
    EXEMPTION_EVIDENCE,
    _baseline,
)


CREATED_AT = "2026-08-06T00:00:00Z"
REQUEST = (
    "Fix the regressed human interface terminal summary and restore its exact "
    "certified presentation behavior. Include focused tests and validation."
)
TARGET = "aigol/runtime/human_interface.py"
FOCUSED_TEST = "tests/test_human_interface.py"
PREIMAGE = "def render_summary(value):\n    return f'Status: {value}'\n"
POSTIMAGE = "def render_summary(value):\n    return f'Summary: {value}'\n"
TEST_CONTENT = (
    "from aigol.runtime.human_interface import render_summary\n\n"
    "def test_render_summary():\n"
    "    assert render_summary('ready') == 'Summary: ready'\n"
)
PATCH = (
    "--- a/aigol/runtime/human_interface.py\n"
    "+++ b/aigol/runtime/human_interface.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def render_summary(value):\n"
    "-    return f'Status: {value}'\n"
    "+    return f'Summary: {value}'\n"
)


def _sha256(value: str) -> str:
    return "sha256:" + sha256(value.encode("utf-8")).hexdigest()


def _git(workspace: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    )


def _workspace(tmp_path: Path, name: str) -> Path:
    workspace = tmp_path / f"{name}-workspace"
    (workspace / "aigol/runtime").mkdir(parents=True)
    (workspace / "tests").mkdir()
    (workspace / "README.md").write_text("authenticated parent\n", encoding="utf-8")
    _git(workspace, "init")
    _git(workspace, "config", "user.name", "G71-07")
    _git(workspace, "config", "user.email", "g71-07@example.invalid")
    _git(workspace, "add", "README.md")
    _git(workspace, "commit", "-m", "authenticated parent")
    (workspace / TARGET).write_text(PREIMAGE, encoding="utf-8")
    (workspace / FOCUSED_TEST).write_text(TEST_CONTENT, encoding="utf-8")
    _git(workspace, "add", TARGET, FOCUSED_TEST)
    _git(workspace, "commit", "-m", "authenticated implementation baseline")
    return workspace


def _grounding(tmp_path: Path, name: str) -> tuple[dict, Path]:
    workspace = _workspace(tmp_path, name)
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=name,
        message=REQUEST,
        runtime_root=tmp_path / f"{name}-runtime",
        workspace=workspace,
        created_at=CREATED_AT,
        reuse_proof_exemption_code="EXACT_CERTIFIED_BEHAVIOR_REPAIR",
        reuse_proof_exemption_evidence=deepcopy(EXEMPTION_EVIDENCE),
        reuse_proof_authenticated_baseline=_baseline(workspace),
    )
    assert context["reuse_proof_production_admission"]["admission_status"] == (
        "READY_FOR_FRESH_G47"
    )
    turn = context["canonical_implementation_turn_binding"]
    consumption = consume_approved_implementation_turn_binding(
        binding_artifact=turn,
        development_composition_plan_hash=turn["development_composition_plan_hash"],
        durable_governed_work_hash=turn["durable_governed_work_hash"],
        proposal_preview_hash=turn["proposal_preview_hash"],
        approval_request_hash=turn["approval_request_hash"],
        created_at=CREATED_AT,
        replay_dir=turn["replay_reference"],
    )
    payload = bind_approved_durable_work_to_worker_payload(
        implementation_turn_binding=turn,
        approval_consumption_artifact=consumption,
        requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-payload",
    )
    grounding = ground_approved_durable_work_repository_scope(
        worker_payload_binding_artifact=payload,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-grounding",
    )
    assert grounding["grounded_repository_targets"] == [TARGET, FOCUSED_TEST]
    return grounding, workspace


def _m12_completion_binding(tmp_path: Path, name: str) -> tuple[dict, dict, Path, Path]:
    grounding, workspace = _grounding(tmp_path, name)
    session_root = tmp_path / name
    session_root.mkdir()
    disposable = tmp_path / f"{name}-disposable"
    (disposable / "aigol/runtime").mkdir(parents=True)
    (disposable / "tests").mkdir()
    (disposable / TARGET).write_text(POSTIMAGE, encoding="utf-8")
    (disposable / FOCUSED_TEST).write_text(TEST_CONTENT, encoding="utf-8")

    validation_result = {
        "artifact_type": "VALIDATION_COMMAND_RESULT_ARTIFACT_V1",
        "runtime_version": "AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_V1",
        "result_id": f"{name}-FOCUSED-RESULT",
        "command_status": "VALIDATION_COMMAND_COMPLETED",
        "command": ["python", "-m", "pytest", FOCUSED_TEST],
        "cwd": str(disposable),
        "exit_code": 0,
        "stdout": "1 passed",
        "stderr": "",
        "shell_execution_used": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "repair_invoked": False,
        "created_at": CREATED_AT,
    }
    validation_result["artifact_hash"] = replay_hash(validation_result)
    patch_hash = _sha256(PATCH)
    manifest_capture = manifests.create_replacement_implementation_manifest(
        manifest_id=f"{name}-MANIFEST",
        canonical_chain_id=f"{name}-CHAIN",
        implementation_bundle_id=f"{name}-BUNDLE",
        canonical_session_id=name,
        source_review_reference=f"{name}-REVIEW",
        source_review_hash=replay_hash(f"{name}-review"),
        source_review_replay_reference=str(session_root / "review"),
        source_review_replay_hash=replay_hash(f"{name}-review-replay"),
        source_decision_reference=f"{name}-TASK-DECISION",
        source_decision_hash=replay_hash(f"{name}-task-decision"),
        source_decision_replay_reference=str(session_root / "task-decision"),
        source_decision_replay_hash=replay_hash(f"{name}-task-decision-replay"),
        application_decision_reference=f"{name}-APPLICATION-DECISION",
        application_decision_hash=replay_hash(f"{name}-application-decision"),
        application_decision_replay_reference=str(session_root / "application-decision"),
        application_decision_replay_hash=replay_hash(
            f"{name}-application-decision-replay"
        ),
        disposable_validation_reference=f"{name}-M12-OUTCOME",
        disposable_validation_hash=replay_hash(f"{name}-M12-completed"),
        disposable_validation_replay_reference=str(session_root / "M12-outcome"),
        disposable_validation_replay_hash=replay_hash(f"{name}-M12-replay"),
        source_workspace=str(workspace),
        disposable_workspace=str(disposable),
        exact_patch=PATCH,
        patch_sha256=patch_hash,
        replacement_files=[
            {
                "file_entry_id": "REPLACEMENT-FILE-000001",
                "target_path": TARGET,
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "preimage_content": PREIMAGE,
                "preimage_sha256": _sha256(PREIMAGE),
                "postimage_content": POSTIMAGE,
                "postimage_sha256": _sha256(POSTIMAGE),
                "patch_sha256": patch_hash,
                "file_mode": 0o644,
                "postimage_file_mode": 0o644,
            }
        ],
        focused_test_evidence={
            "test_entry_id": "EXISTING-FOCUSED-TEST-000001",
            "target_path": FOCUSED_TEST,
            "content": TEST_CONTENT,
            "content_sha256": _sha256(TEST_CONTENT),
            "file_mode": 0o644,
            "validation_command": ["python", "-m", "pytest", FOCUSED_TEST],
            "validation_result_artifact": validation_result,
            "validation_replay_reference": str(session_root / "focused-validation"),
            "validation_replay_hash": replay_hash(f"{name}-focused-replay"),
        },
        validation_requirements=["EXACT_M12_VALIDATED_REPLACEMENT"],
        known_gaps=["Human generated-content acceptance not yet performed."],
        created_at=CREATED_AT,
        replay_dir=session_root / "manifest",
    )
    manifest = manifest_capture["implementation_manifest_artifact"]
    assert manifest_capture["manifest_status"] == manifests.IMPLEMENTATION_MANIFEST_CREATED
    manifest_replay = manifests.reconstruct_implementation_manifest_replay(
        manifest_capture["implementation_manifest_replay_reference"]
    )
    content_capture = validate_generated_content(
        validation_id=f"{name}-CONTENT-VALIDATION",
        implementation_manifest_artifact=manifest,
        created_at=CREATED_AT,
    )
    test_capture = validate_generated_tests(
        validation_id=f"{name}-TEST-VALIDATION",
        implementation_manifest_artifact=manifest,
        generated_test_bundle=deepcopy(manifest["test_entries"]),
        created_at=CREATED_AT,
    )
    assert content_capture["validation_status"] == GENERATED_CONTENT_VALIDATED
    assert test_capture["validation_status"] == GENERATED_TEST_VALIDATED
    prerequisite_capture = acceptance.bind_generated_content_acceptance_prerequisites(
        prerequisite_id=f"{name}-ACCEPTANCE-PREREQUISITES",
        implementation_manifest_artifact=manifest,
        generated_content_validation_artifact=content_capture[
            "generated_content_validation_artifact"
        ],
        generated_test_validation_artifact=test_capture[
            "generated_test_validation_artifact"
        ],
        created_at=CREATED_AT,
    )
    outcome = {
        "outcome_id": f"{name}-M12-OUTCOME",
        "artifact_hash": manifest["disposable_validation_hash"],
    }
    binding = prerequisites._binding_artifact(
        identity=replay_hash(f"{name}-M12-to-M13"),
        outcome=outcome,
        manifest=manifest,
        manifest_replay=manifest_replay,
        content=content_capture["generated_content_validation_artifact"],
        tests=test_capture["generated_test_validation_artifact"],
        prerequisites=prerequisite_capture["acceptance_prerequisite_artifact"],
        disposable_workspace=str(disposable),
        created_at=CREATED_AT,
    )
    binding_replay = session_root / "acceptance-prerequisite-binding"
    prerequisites._persist_binding(binding_replay, binding)
    capture = {
        "runtime_version": prerequisites.RUNTIME_VERSION,
        "binding_status": prerequisites.BINDING_COMPLETED,
        "binding_artifact": deepcopy(binding),
        "implementation_manifest_capture": deepcopy(manifest_capture),
        "generated_content_validation_capture": deepcopy(content_capture),
        "generated_test_validation_capture": deepcopy(test_capture),
        "acceptance_prerequisite_capture": deepcopy(prerequisite_capture),
        "binding_replay_reference": str(binding_replay),
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
    reconstructed = (
        prerequisites.reconstruct_codex_replacement_acceptance_prerequisite_binding(
            binding_capture=capture,
            session_root=session_root,
        )
    )
    assert reconstructed["ready_for_acceptance"] is True
    return capture, grounding, session_root, workspace


def _accepted_lineage(tmp_path: Path, name: str) -> dict:
    binding, grounding, session_root, workspace = _m12_completion_binding(
        tmp_path, name
    )
    context = human_decision.prepare_content_acceptance_decision_context(
        context_id=f"{name}-CONTENT-ACCEPTANCE",
        binding_capture=binding,
        human_actor_id="HUMAN_OPERATOR",
        presented_at=CREATED_AT,
        session_root=session_root,
        replay_dir=session_root / "content-decision",
    )
    decision = human_decision.record_content_acceptance_decision(
        context_capture=context,
        binding_capture=binding,
        decision_outcome=human_decision.ACCEPTED,
        decided_by="HUMAN_OPERATOR",
        decided_at=CREATED_AT,
        session_root=session_root,
    )
    decision_reconstruction = (
        human_decision.reconstruct_content_acceptance_decision_replay(
            decision_capture=decision,
            binding_capture=binding,
            session_root=session_root,
        )
    )
    accepted = acceptance.accept_generated_content_from_content_acceptance_decision(
        acceptance_id=f"{name}-ACCEPTED-CONTENT",
        decision_capture=decision,
        binding_capture=binding,
        created_at=CREATED_AT,
        session_root=session_root,
        replay_dir=session_root / "generated-content-acceptance",
    )
    accepted_reconstruction = (
        acceptance.reconstruct_generated_content_acceptance_from_decision_replay(
            acceptance_capture=accepted,
            decision_capture=decision,
            binding_capture=binding,
            session_root=session_root,
        )
    )
    candidate = provenance.create_g31_accepted_existing_file_mutation_candidate(
        candidate_id=f"{name}-PROVENANCE",
        acceptance_capture=accepted,
        decision_capture=decision,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        session_root=session_root,
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=session_root / "accepted-content-provenance",
    )
    candidate_reconstruction = (
        provenance.reconstruct_g31_accepted_existing_file_mutation_candidate_replay(
            candidate_capture=candidate,
            acceptance_capture=accepted,
            decision_capture=decision,
            binding_capture=binding,
            repository_grounding_artifact=grounding,
            session_root=session_root,
        )
    )
    return {
        "binding": binding,
        "grounding": grounding,
        "session_root": session_root,
        "workspace": workspace,
        "context": context,
        "decision": decision,
        "decision_reconstruction": decision_reconstruction,
        "accepted": accepted,
        "accepted_reconstruction": accepted_reconstruction,
        "candidate": candidate,
        "candidate_reconstruction": candidate_reconstruction,
    }


def test_authenticated_m13_owner_chain_accepts_and_reconstructs_exact_provenance(
    tmp_path: Path,
) -> None:
    lineage = _accepted_lineage(tmp_path, "G71-07-POSITIVE")
    decision = lineage["decision"]["human_decision_artifact"]
    accepted = lineage["accepted"]["generated_content_acceptance_artifact"]
    candidate = lineage["candidate"]["existing_file_mutation_candidate_artifact"]
    provenance_binding = candidate["candidate_provenance"]

    assert decision["decision_outcome"] == human_decision.ACCEPTED
    assert lineage["decision_reconstruction"]["replay_artifact_count"] == 4
    assert accepted["acceptance_status"] == acceptance.GENERATED_CONTENT_ACCEPTED
    assert lineage["accepted_reconstruction"]["result_accepted"] is True
    assert accepted["implementation_manifest_artifact_hash"] == (
        lineage["binding"]["implementation_manifest_capture"]
        ["implementation_manifest_artifact"]["artifact_hash"]
    )
    assert provenance_binding["accepted_result_hash"] == accepted["artifact_hash"]
    assert provenance_binding["content_decision_hash"] == decision["artifact_hash"]
    assert provenance_binding["repository_grounding_hash"] == (
        lineage["grounding"]["grounding_evidence_hash"]
    )
    assert lineage["candidate_reconstruction"]["replay_artifact_count"] == 3
    assert lineage["candidate_reconstruction"]["result_accepted"] is True
    assert candidate["human_mutation_decision_recorded"] is False
    assert candidate["mutation_authorized"] is False
    assert candidate["main_repository_mutated"] is False
    assert subprocess.run(
        ["git", "status", "--short"],
        cwd=lineage["workspace"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout == ""


def test_rejected_or_generic_content_evidence_cannot_reach_acceptance_owner(
    tmp_path: Path,
) -> None:
    binding, _, session_root, _ = _m12_completion_binding(
        tmp_path, "G71-07-REJECT"
    )
    context = human_decision.prepare_content_acceptance_decision_context(
        context_id="G71-07-REJECT-CONTEXT",
        binding_capture=binding,
        human_actor_id="HUMAN_OPERATOR",
        presented_at=CREATED_AT,
        session_root=session_root,
        replay_dir=session_root / "content-decision",
    )
    rejected = human_decision.record_content_acceptance_decision(
        context_capture=context,
        binding_capture=binding,
        decision_outcome=human_decision.REJECTED,
        decided_by="HUMAN_OPERATOR",
        decided_at=CREATED_AT,
        session_root=session_root,
    )
    with pytest.raises(FailClosedRuntimeError, match="exact V2 ACCEPTED"):
        acceptance.accept_generated_content_from_content_acceptance_decision(
            acceptance_id="G71-07-REJECTED",
            decision_capture=rejected,
            binding_capture=binding,
            created_at=CREATED_AT,
            session_root=session_root,
            replay_dir=session_root / "rejected-acceptance",
        )
    with pytest.raises(
        FailClosedRuntimeError, match="exact V2 content-acceptance evidence"
    ):
        acceptance.accept_generated_content_from_content_acceptance_decision(
            acceptance_id="G71-07-GENERIC",
            decision_capture=True,
            binding_capture=binding,
            created_at=CREATED_AT,
            session_root=session_root,
            replay_dir=session_root / "generic-acceptance",
        )


def test_acceptance_and_provenance_tamper_or_reuse_fail_closed(
    tmp_path: Path,
) -> None:
    lineage = _accepted_lineage(tmp_path, "G71-07-TAMPER")
    changed_acceptance = deepcopy(lineage["accepted"])
    changed_acceptance["generated_content_acceptance_artifact"][
        "human_actor_id"
    ] = "SUBSTITUTED_ACTOR"
    with pytest.raises(FailClosedRuntimeError):
        provenance.create_g31_accepted_existing_file_mutation_candidate(
            candidate_id="G71-07-TAMPERED-PROVENANCE",
            acceptance_capture=changed_acceptance,
            decision_capture=lineage["decision"],
            binding_capture=lineage["binding"],
            repository_grounding_artifact=lineage["grounding"],
            session_root=lineage["session_root"],
            created_by="HUMAN_OPERATOR",
            created_at=CREATED_AT,
            replay_dir=lineage["session_root"] / "tampered-provenance",
        )
    with pytest.raises(FailClosedRuntimeError, match="already consumed"):
        provenance.create_g31_accepted_existing_file_mutation_candidate(
            candidate_id="G71-07-SECOND-PROVENANCE",
            acceptance_capture=lineage["accepted"],
            decision_capture=lineage["decision"],
            binding_capture=lineage["binding"],
            repository_grounding_artifact=lineage["grounding"],
            session_root=lineage["session_root"],
            created_by="HUMAN_OPERATOR",
            created_at=CREATED_AT,
            replay_dir=lineage["session_root"] / "second-provenance",
        )


def test_m13_discharge_stops_before_m14_authority(tmp_path: Path) -> None:
    lineage = _accepted_lineage(tmp_path, "G71-07-BOUNDARY")
    candidate = lineage["candidate"]
    assert candidate["result_accepted"] is True
    assert candidate["human_mutation_decision_recorded"] is False
    assert candidate["mutation_authorized"] is False
    assert candidate["main_repository_mutated"] is False
    assert not list(lineage["session_root"].rglob("*mutation_authorization*"))
    assert not list(lineage["session_root"].rglob("*filesystem_replace*"))
