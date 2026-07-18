"""Focused deterministic coverage for the G31-23B replacement prerequisite boundary."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

import aigol.runtime.codex_replacement_acceptance_prerequisite_binding_runtime as binding_module
from aigol.runtime.codex_replacement_acceptance_prerequisite_binding_runtime import (
    BINDING_COMPLETED,
    bind_codex_replacement_acceptance_prerequisites,
    reconstruct_codex_replacement_acceptance_prerequisite_binding,
)
from aigol.runtime.generated_content_acceptance_runtime import (
    ACCEPTANCE_PREREQUISITES_SATISFIED,
    GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_ARTIFACT_V2,
)
from aigol.runtime.generated_content_validation_runtime import (
    FAILED_CLOSED,
    GENERATED_CONTENT_VALIDATION_ARTIFACT_V2,
    _compute_manifest_hash,
    validate_generated_content,
)
from aigol.runtime.generated_test_validation_runtime import GENERATED_TEST_VALIDATION_ARTIFACT_V2
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V2,
    REPLACE_CONTENT,
    create_implementation_manifest,
    reconstruct_implementation_manifest_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from test_g31_23a_canonical_disposable_patch_application_and_test_validation_boundary import (
    CREATED_AT,
    _application_decision,
    _execute,
    _fixture,
    _prepare,
    _task_decision,
)


def _successful(tmp_path: Path, session: str = "G31-23B") -> dict:
    values = _fixture(tmp_path, session)
    task_decision = _task_decision(values)
    review = _prepare(values, task_decision)
    application_decision = _application_decision(values, task_decision, review)
    outcome = _execute(values, task_decision, review, application_decision)
    return {
        "values": values,
        "task_decision": task_decision,
        "review": review,
        "application_decision": application_decision,
        "outcome": outcome,
    }


def _bind(lineage: dict, *, name: str = "replacement-prerequisites") -> dict:
    values = lineage["values"]
    runtime = values["runtime"]
    return bind_codex_replacement_acceptance_prerequisites(
        disposable_validation_outcome_capture=lineage["outcome"],
        disposable_validation_review_capture=lineage["review"],
        application_decision_capture=lineage["application_decision"],
        task_outcome_decision_capture=lineage["task_decision"],
        task_outcome_review_capture=values["review"],
        result_capture_binding_capture=values["capture"],
        governance_validation_binding_capture=values["validation"],
        activation_capture=values["activation"],
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=values["root"],
        source_workspace=values["workspace"],
        created_at=CREATED_AT,
        replay_dir=values["root"] / name,
    )


def test_successful_v2_replacement_prerequisites_are_ready_but_not_accepted(tmp_path: Path) -> None:
    lineage = _successful(tmp_path)
    before = {path: path.read_bytes() for path in lineage["values"]["workspace"].rglob("*") if path.is_file()}
    capture = _bind(lineage)
    reconstructed = reconstruct_codex_replacement_acceptance_prerequisite_binding(
        binding_capture=capture,
        session_root=lineage["values"]["root"],
    )
    manifest = capture["implementation_manifest_capture"]["implementation_manifest_artifact"]
    content = capture["generated_content_validation_capture"]["generated_content_validation_artifact"]
    tests = capture["generated_test_validation_capture"]["generated_test_validation_artifact"]
    prerequisites = capture["acceptance_prerequisite_capture"]["acceptance_prerequisite_artifact"]

    assert capture["binding_status"] == BINDING_COMPLETED
    assert manifest["artifact_type"] == IMPLEMENTATION_MANIFEST_ARTIFACT_V2
    assert manifest["operation_mode"] == REPLACE_CONTENT
    assert manifest["manifest_contract_version"] == "V2"
    assert content["artifact_type"] == GENERATED_CONTENT_VALIDATION_ARTIFACT_V2
    assert tests["artifact_type"] == GENERATED_TEST_VALIDATION_ARTIFACT_V2
    assert prerequisites["artifact_type"] == GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_ARTIFACT_V2
    assert prerequisites["prerequisite_status"] == ACCEPTANCE_PREREQUISITES_SATISFIED
    assert capture["acceptance_prerequisites_satisfied"] is True
    assert capture["ready_for_acceptance"] is True
    assert capture["result_accepted"] is False
    assert capture["main_repository_mutated"] is False
    assert capture["mutation_authorized"] is False
    assert reconstructed["replay_artifact_count"] == 1
    after = {path: path.read_bytes() for path in lineage["values"]["workspace"].rglob("*") if path.is_file()}
    assert before == after


def test_historic_create_only_manifest_reconstructs_identically(tmp_path: Path) -> None:
    capture = create_implementation_manifest(
        manifest_id="HISTORIC-CREATE-ONLY",
        canonical_chain_id="HISTORIC-CHAIN",
        implementation_bundle_id="HISTORIC-BUNDLE",
        source_candidate_reference="CANDIDATE",
        source_candidate_hash=replay_hash({"source": "candidate"}),
        implementation_handoff_reference="HANDOFF",
        implementation_handoff_hash=replay_hash({"source": "handoff"}),
        provider_generation_authorization_reference="AUTH",
        provider_generation_authorization_hash=replay_hash({"source": "auth"}),
        provider_response_reference="RESPONSE",
        provider_response_hash=replay_hash({"source": "response"}),
        target_domain="TRADING",
        target_resource="WORKER",
        target_worker="HISTORIC",
        generated_files=[{
            "target_path": "aigol/runtime/historic.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "VALUE = 1\n",
        }],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "historic",
    )
    reconstructed = reconstruct_implementation_manifest_replay(tmp_path / "historic")
    assert capture["implementation_manifest_artifact"]["artifact_type"] == IMPLEMENTATION_MANIFEST_ARTIFACT_V1
    assert capture["implementation_manifest_artifact"]["operation_mode"] == CREATE_ONLY
    assert reconstructed["implementation_manifest_hash"] == capture["implementation_manifest_hash"]


def test_v1_and_unsatisfied_outcome_substitution_remain_ineligible(
    tmp_path: Path,
) -> None:
    lineage = _successful(tmp_path, "INELIGIBLE")
    for field, value in (
        ("task_outcome_criteria_version", "V1"),
        ("task_outcome_satisfied", False),
    ):
        substituted = deepcopy(lineage)
        substituted["outcome"] = deepcopy(lineage["outcome"])
        substituted["outcome"]["outcome_artifact"][field] = value
        substituted["outcome"]["outcome_artifact"]["artifact_hash"] = replay_hash({
            key: item for key, item in substituted["outcome"]["outcome_artifact"].items()
            if key != "artifact_hash"
        })
        substituted["outcome"]["capture_hash"] = replay_hash({
            key: item for key, item in substituted["outcome"].items() if key != "capture_hash"
        })
        with pytest.raises(FailClosedRuntimeError):
            _bind(substituted, name=f"ineligible-{field}")


@pytest.mark.parametrize("location", ["source", "disposable"])
def test_missing_or_substituted_preimage_and_postimage_bytes_fail_closed(
    tmp_path: Path, location: str,
) -> None:
    lineage = _successful(tmp_path, f"BYTE-SUBSTITUTION-{location}")
    root = lineage["values"]["workspace"] if location == "source" else lineage["values"]["disposable"]
    (root / "aigol/runtime/human_interface.py").write_text("SUBSTITUTED = True\n", encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="drift|postimage|lineage|stale|substituted"):
        _bind(lineage)


def test_failed_content_application_and_failed_focused_test_are_not_ready(tmp_path: Path) -> None:
    invalid_patch = "diff --git a/aigol/runtime/human_interface.py b/aigol/runtime/human_interface.py\ninvalid\n"
    content_values = _fixture(tmp_path, "FAILED-CONTENT", patch=invalid_patch)
    with pytest.raises(FailClosedRuntimeError):
        _task_decision(content_values)

    test_values = _fixture(tmp_path, "FAILED-TEST", failing_test=True)
    test_task = _task_decision(test_values)
    test_review = _prepare(test_values, test_task)
    test_approval = _application_decision(test_values, test_task, test_review)
    test_outcome = _execute(test_values, test_task, test_review, test_approval)
    assert test_outcome["grounded_test_validation_passed"] is False
    lineage = {
        "values": test_values,
        "task_decision": test_task,
        "review": test_review,
        "application_decision": test_approval,
        "outcome": test_outcome,
    }
    with pytest.raises(FailClosedRuntimeError, match="successful G31-23A"):
        _bind(lineage)


def test_replacement_manifest_forbidden_semantics_fail_content_validation(
    tmp_path: Path,
) -> None:
    capture = _bind(_successful(tmp_path, "FORBIDDEN-SEMANTICS"))
    original = capture["implementation_manifest_capture"]["implementation_manifest_artifact"]
    for field, value in (
        ("delete_allowed", True),
        ("rename_allowed", True),
        ("binary_patch_allowed", True),
        ("symlink_allowed", True),
        ("submodule_allowed", True),
        ("path_traversal_allowed", True),
        ("postimage_file_mode", 0o755),
        ("postimage_file_type", "SYMLINK"),
    ):
        manifest = deepcopy(original)
        manifest["file_entries"][0][field] = value
        manifest["file_entries"][0]["file_entry_hash"] = replay_hash({
            key: item for key, item in manifest["file_entries"][0].items() if key != "file_entry_hash"
        })
        manifest["implementation_manifest_hash"] = _compute_manifest_hash(manifest)
        manifest["artifact_hash"] = replay_hash({
            key: item for key, item in manifest.items() if key != "artifact_hash"
        })
        validation = validate_generated_content(
            validation_id=f"FORBIDDEN-REPLACEMENT-{field}",
            implementation_manifest_artifact=manifest,
            created_at=CREATED_AT,
        )
        assert validation["validation_status"] == FAILED_CLOSED

    for invalid_path in ("../escape.py", "/absolute.py", "unknown/ungrounded.py"):
        manifest = deepcopy(original)
        manifest["file_entries"][0]["target_path"] = invalid_path
        manifest["file_entries"][0]["file_entry_hash"] = replay_hash({
            key: item for key, item in manifest["file_entries"][0].items() if key != "file_entry_hash"
        })
        manifest["implementation_manifest_hash"] = _compute_manifest_hash(manifest)
        manifest["artifact_hash"] = replay_hash({
            key: item for key, item in manifest.items() if key != "artifact_hash"
        })
        assert validate_generated_content(
            validation_id="INVALID-REPLACEMENT-PATH",
            implementation_manifest_artifact=manifest,
            created_at=CREATED_AT,
        )["validation_status"] == FAILED_CLOSED

    duplicate = deepcopy(original)
    duplicate["file_entries"].append(deepcopy(duplicate["file_entries"][0]))
    duplicate["file_count"] = 2
    duplicate["implementation_manifest_hash"] = _compute_manifest_hash(duplicate)
    duplicate["artifact_hash"] = replay_hash({
        key: item for key, item in duplicate.items() if key != "artifact_hash"
    })
    assert validate_generated_content(
        validation_id="DUPLICATE-REPLACEMENT-PATH",
        implementation_manifest_artifact=duplicate,
        created_at=CREATED_AT,
    )["validation_status"] == FAILED_CLOSED

    create_substitution = deepcopy(original)
    create_substitution["operation_mode"] = CREATE_ONLY
    create_substitution["implementation_manifest_hash"] = _compute_manifest_hash(create_substitution)
    create_substitution["artifact_hash"] = replay_hash({
        key: item for key, item in create_substitution.items() if key != "artifact_hash"
    })
    assert validate_generated_content(
        validation_id="CREATE-ONLY-SUBSTITUTION",
        implementation_manifest_artifact=create_substitution,
        created_at=CREATED_AT,
    )["validation_status"] == FAILED_CLOSED


def test_patch_and_postimage_manifest_byte_substitution_fails_closed(
    tmp_path: Path,
) -> None:
    capture = _bind(_successful(tmp_path, "MANIFEST-BYTES"))
    original = capture["implementation_manifest_capture"]["implementation_manifest_artifact"]
    for substitution in ("patch-missing", "patch-changed", "preimage-changed", "postimage-changed"):
        manifest = deepcopy(original)
        if substitution == "patch-missing":
            manifest["exact_patch"] = ""
        elif substitution == "patch-changed":
            manifest["exact_patch"] += "\n# substituted\n"
        elif substitution == "preimage-changed":
            manifest["file_entries"][0]["preimage_content"] += "\n# substituted\n"
            manifest["file_entries"][0]["file_entry_hash"] = replay_hash({
                key: item for key, item in manifest["file_entries"][0].items()
                if key != "file_entry_hash"
            })
        else:
            manifest["file_entries"][0]["postimage_content"] += "\n# substituted\n"
            manifest["file_entries"][0]["file_entry_hash"] = replay_hash({
                key: item for key, item in manifest["file_entries"][0].items()
                if key != "file_entry_hash"
            })
        manifest["implementation_manifest_hash"] = _compute_manifest_hash(manifest)
        manifest["artifact_hash"] = replay_hash({
            key: item for key, item in manifest.items() if key != "artifact_hash"
        })
        validation = validate_generated_content(
            validation_id=f"SUBSTITUTED-REPLACEMENT-{substitution}",
            implementation_manifest_artifact=manifest,
            created_at=CREATED_AT,
        )
        assert validation["validation_status"] == FAILED_CLOSED


def test_main_repository_drift_symlink_and_ungrounded_path_fail_before_readiness(tmp_path: Path) -> None:
    drift = _successful(tmp_path, "MAIN-DRIFT")
    (drift["values"]["workspace"] / "README.md").write_text("drift\n", encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="drift|workspace|identity"):
        _bind(drift)

    symlink = _successful(tmp_path, "SYMLINK")
    target = symlink["values"]["disposable"] / "aigol/runtime/human_interface.py"
    target.unlink()
    target.symlink_to(symlink["values"]["disposable"] / "tests/test_human_interface.py")
    with pytest.raises(FailClosedRuntimeError):
        _bind(symlink)

    ungrounded = _successful(tmp_path, "UNGROUNDED")
    substituted_review = deepcopy(ungrounded["review"])
    substituted_review["disposable_patch_validation_plan_artifact"]["changed_paths"] = ["../escape.py"]
    ungrounded["review"] = substituted_review
    with pytest.raises(FailClosedRuntimeError):
        _bind(ungrounded)


def test_cross_session_replay_and_manifest_substitution_fail_closed(tmp_path: Path) -> None:
    first = _successful(tmp_path, "CROSS-A")
    second = _successful(tmp_path, "CROSS-B")
    first["application_decision"] = second["application_decision"]
    with pytest.raises(FailClosedRuntimeError, match="cross-session|exact unused human approval"):
        _bind(first)

    clean = _successful(tmp_path, "REPLAY-SUBSTITUTION")
    capture = _bind(clean)
    capture["implementation_manifest_capture"]["implementation_manifest_artifact"]["patch_sha256"] = (
        "sha256:" + "0" * 64
    )
    with pytest.raises(FailClosedRuntimeError):
        reconstruct_codex_replacement_acceptance_prerequisite_binding(
            binding_capture=capture,
            session_root=clean["values"]["root"],
        )


def test_duplicate_destination_and_repeated_consumption_fail_closed(tmp_path: Path) -> None:
    lineage = _successful(tmp_path, "DUPLICATE")
    _bind(lineage)
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        _bind(lineage)
    with pytest.raises(FailClosedRuntimeError, match="already consumed"):
        _bind(lineage, name="second-replacement-prerequisites")


def test_acceptance_and_main_mutation_owners_are_not_called(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import aigol.runtime.generated_content_acceptance_runtime as acceptance_runtime
    import aigol.runtime.governed_repository_mutation_runtime as mutation_runtime

    lineage = _successful(tmp_path, "NO-OWNERS-CALLED")

    def forbidden(*_args, **_kwargs):
        raise AssertionError("acceptance or main mutation owner was called")

    monkeypatch.setattr(acceptance_runtime, "accept_generated_content", forbidden)
    monkeypatch.setattr(mutation_runtime, "execute_governed_repository_mutation", forbidden)
    capture = _bind(lineage)
    assert capture["result_accepted"] is False
    assert capture["main_repository_mutated"] is False
    assert capture["mutation_authorized"] is False
    assert "accept_generated_content(" not in Path(binding_module.__file__).read_text(encoding="utf-8")
    assert "governed_repository_mutation_runtime" not in Path(binding_module.__file__).read_text(encoding="utf-8")
