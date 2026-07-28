"""Deterministic certification coverage for G43-01."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.constitutional_development_supervisor_runtime import (
    BLOCKER_DIAGNOSED,
    FAILED_CLOSED,
    NO_CONSTITUTIONAL_BLOCKER,
    WORKFLOW_HEALTHY,
    reconstruct_constitutional_development_supervisor_replay,
    supervise_constitutional_development_workflow,
    validate_constitutional_development_supervisor_diagnosis_artifact,
)
from aigol.runtime.constitutional_development_workflow_integration_runtime import (
    plan_constitutional_development_validation,
)
from aigol.runtime.governed_validation_runtime import (
    create_governed_validation_approval,
    create_governed_validation_candidate,
    execute_governed_validation,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.intelligent_validation_orchestrator_v4 import (
    FAILURE_REVALIDATION_PLANNING,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_change_normalization_runtime import (
    normalize_platform_change,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-28T00:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _normalized_change(tmp_path) -> dict:
    targets = (
        (
            "aigol/runtime/constitutional_development_supervisor_runtime.py",
            "PYTHON_RUNTIME_MODULE",
        ),
        (
            "tests/test_g43_01_constitutional_development_supervisor.py",
            "PYTHON_TEST_MODULE",
        ),
    )
    manifest = create_implementation_manifest(
        manifest_id="MANIFEST-G43-01",
        canonical_chain_id="CHAIN-G43-01",
        implementation_bundle_id="G43_01_DEVELOPMENT_SUPERVISOR",
        source_candidate_reference="CANDIDATE-G43-01",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G43-01",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G43-01",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G43-01",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": f"FILE-G43-01-{index:06d}",
                "target_path": target_path,
                "artifact_type": artifact_type,
                "operation": CREATE_ONLY,
                "content": f"G43-01 deterministic content {index}\n",
                "validation_requirements": [],
            }
            for index, (target_path, artifact_type) in enumerate(
                targets,
                start=1,
            )
        ],
        generated_tests=[],
        validation_requirements=[
            "python -m pytest "
            "tests/test_g43_01_constitutional_development_supervisor.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]
    return normalize_platform_change(
        normalization_id="NORMALIZATION-G43-01",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "normalization",
    )["normalized_change_artifact"]


def _workflow(
    tmp_path,
    source: dict,
    *,
    name: str = "workflow",
    normalized_hash: str | None = None,
    planning_mode: str | None = None,
    failure_context: dict | None = None,
) -> tuple[dict, object]:
    arguments = {
        "workflow_id": "WORKFLOW-G43-01",
        "session_id": "SESSION-G43-01",
        "normalized_change_artifact": source,
        "normalized_change_reference": source["normalization_id"],
        "normalized_change_hash": (
            source["normalized_change_hash"]
            if normalized_hash is None
            else normalized_hash
        ),
        "created_by": "PLATFORM_CORE_VALIDATION_PLANNING",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / name,
        "failure_context": failure_context,
    }
    if planning_mode is not None:
        arguments["planning_mode"] = planning_mode
    capture = plan_constitutional_development_validation(**arguments)
    return (
        capture[
            "constitutional_development_validation_workflow_artifact"
        ],
        tmp_path / name,
    )


def _failed_validation(tmp_path) -> dict:
    candidate = create_governed_validation_candidate(
        candidate_id="CANDIDATE-G43-01-FAILED",
        session_id="SESSION-G43-01",
        command_id="PYTHON_VALIDATION_FAILS_FOR_TEST",
        validation_purpose="existing failed validation evidence for G43",
        created_by="PLATFORM_CORE",
        created_at=CREATED_AT,
    )
    approval = create_governed_validation_approval(
        approval_id="APPROVAL-G43-01-FAILED",
        candidate_artifact=candidate,
        confirmation_text=(
            f"confirm validation {candidate['candidate_id']} "
            f"{candidate['artifact_hash']}"
        ),
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )
    return execute_governed_validation(
        execution_id="EXECUTION-G43-01-FAILED",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "failed_validation",
    )["validation_result_artifact"]


def _supervise(
    tmp_path,
    workflow: dict,
    workflow_replay_dir,
    *,
    name: str = "supervisor",
) -> dict:
    return supervise_constitutional_development_workflow(
        diagnosis_id="DIAGNOSIS-G43-01",
        workflow_artifact=workflow,
        workflow_reference=workflow["workflow_id"],
        workflow_hash=workflow["workflow_hash"],
        workflow_artifact_hash=workflow["artifact_hash"],
        workflow_replay_dir=workflow_replay_dir,
        observed_by="PLATFORM_CORE_DEVELOPMENT_SUPERVISION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_healthy_workflow_has_no_blocker_and_preserves_ive_scope(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    workflow, workflow_replay = _workflow(tmp_path, source)
    original = deepcopy(workflow)
    capture = _supervise(tmp_path, workflow, workflow_replay)
    diagnosis = capture[
        "constitutional_development_supervisor_diagnosis_artifact"
    ]
    bundle = workflow["ive_4_planning_bundle_artifact"]

    assert diagnosis["diagnosis_status"] == WORKFLOW_HEALTHY
    assert diagnosis["earliest_constitutional_blocker"]["boundary"] == (
        NO_CONSTITUTIONAL_BLOCKER
    )
    assert diagnosis["missing_evidence"] == []
    assert diagnosis["affected_certified_capability"] is None
    assert diagnosis["minimal_repair_boundary"]["repair_status"] == (
        "NO_REPAIR_REQUIRED"
    )
    revalidation = diagnosis["minimal_revalidation_scope"]
    assert revalidation["recommendation"] == (
        bundle["current_planning_recommendation"]
    )
    assert revalidation["full_regression"] == bundle["full_regression"]
    assert revalidation["certified_scope_claim_allowed"] is True
    assert revalidation["reduced_scope_claim_allowed"] is False
    assert workflow == original


def test_supervisor_identifies_g42_input_binding_as_earliest_blocker(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    workflow, workflow_replay = _workflow(
        tmp_path,
        source,
        normalized_hash=_hash("wrong-normalized-binding"),
    )
    diagnosis = _supervise(tmp_path, workflow, workflow_replay)[
        "constitutional_development_supervisor_diagnosis_artifact"
    ]

    assert diagnosis["diagnosis_status"] == BLOCKER_DIAGNOSED
    blocker = diagnosis["earliest_constitutional_blocker"]
    assert blocker["boundary"] == "G42_WORKFLOW_INPUT_BINDING"
    assert blocker["boundary_rank"] == 1
    assert blocker["evidence_status"] == "BINDING_MISMATCH"
    affected = diagnosis["affected_certified_capability"]
    assert affected["capability_identifier"] == (
        "CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION"
    )
    assert affected["certification_milestone"] == "G42-01"
    assert diagnosis["missing_evidence"][0]["required_evidence"]
    assert diagnosis["minimal_repair_boundary"]["repair_status"] == (
        "EVIDENCE_BOUNDARY_REPAIR_RECOMMENDED"
    )
    assert diagnosis["minimal_repair_boundary"][
        "implementation_change_authorized"
    ] is False
    assert diagnosis["minimal_revalidation_scope"]["full_regression"][
        "required"
    ] is True


def test_supervisor_identifies_missing_ive_4_mode_evidence(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    workflow, workflow_replay = _workflow(
        tmp_path,
        source,
        planning_mode=FAILURE_REVALIDATION_PLANNING,
    )
    diagnosis = _supervise(tmp_path, workflow, workflow_replay)[
        "constitutional_development_supervisor_diagnosis_artifact"
    ]

    assert diagnosis["diagnosis_status"] == BLOCKER_DIAGNOSED
    blocker = diagnosis["earliest_constitutional_blocker"]
    assert blocker["boundary"] == "IVE_4_ORCHESTRATION_INPUT_BINDING"
    assert blocker["boundary_rank"] == 2
    assert blocker["evidence_status"] == "UNAVAILABLE"
    assert diagnosis["affected_certified_capability"][
        "capability_identifier"
    ] == "INTELLIGENT_VALIDATION_ORCHESTRATOR_V4"
    assert diagnosis["missing_evidence"][0]["observed_evidence_status"] == (
        "UNAVAILABLE"
    )
    assert diagnosis["minimal_revalidation_scope"][
        "reduced_scope_claim_allowed"
    ] is False


def test_supervisor_preserves_certified_ive_3_revalidation_scope(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    initial, _ = _workflow(tmp_path, source, name="initial_workflow")
    schedule = initial["ive_4_planning_bundle_artifact"][
        "stage_artifacts"
    ]["ive_2"]
    group = next(
        item
        for item in schedule["groups"]
        if item["group_kind"] == "VALIDATION_SUBJECT"
    )
    result = _failed_validation(tmp_path)
    context = {
        "validation_result_artifact": result,
        "validation_result_reference": result["execution_id"],
        "validation_result_hash": result["artifact_hash"],
        "validation_replay_dir": tmp_path / "failed_validation",
        "failed_group_id": group["group_id"],
        "failed_group_hash": group["group_hash"],
        "failed_requirement_hashes": group["requirement_hashes"][:1],
        "observed_by": "HUMAN_OPERATOR",
    }
    workflow, workflow_replay = _workflow(
        tmp_path,
        source,
        name="failure_workflow",
        planning_mode=FAILURE_REVALIDATION_PLANNING,
        failure_context=context,
    )
    diagnosis = _supervise(
        tmp_path,
        workflow,
        workflow_replay,
    )["constitutional_development_supervisor_diagnosis_artifact"]

    assert diagnosis["diagnosis_status"] == WORKFLOW_HEALTHY
    recommendation = diagnosis["minimal_revalidation_scope"][
        "recommendation"
    ]
    assert recommendation["recommendation_type"] == (
        "IVE_3_FAILURE_REVALIDATION_SCOPE"
    )
    assert recommendation == workflow["ive_4_planning_bundle_artifact"][
        "current_planning_recommendation"
    ]
    assert recommendation["recommended_revalidation_groups"]
    assert diagnosis["validation_executed"] is False
    assert diagnosis["automatic_repair_performed"] is False


def test_supervisor_is_deterministic_for_identical_evidence(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    workflow, workflow_replay = _workflow(tmp_path, source)
    first = _supervise(
        tmp_path,
        workflow,
        workflow_replay,
        name="first",
    )["constitutional_development_supervisor_diagnosis_artifact"]
    second = _supervise(
        tmp_path,
        workflow,
        workflow_replay,
        name="second",
    )["constitutional_development_supervisor_diagnosis_artifact"]

    assert first == second


def test_incomplete_workflow_replay_fails_closed_without_diagnosis_claim(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    workflow, workflow_replay = _workflow(tmp_path, source)
    replay_file = (
        workflow_replay
        / "002_constitutional_development_validation_workflow_recorded.json"
    )
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["validation_executed"] = True
    replay_file.write_text(
        json.dumps(wrapper, sort_keys=True),
        encoding="utf-8",
    )
    diagnosis = _supervise(tmp_path, workflow, workflow_replay)[
        "constitutional_development_supervisor_diagnosis_artifact"
    ]

    assert diagnosis["diagnosis_status"] == FAILED_CLOSED
    assert diagnosis["affected_certified_capability"] is None
    assert diagnosis["missing_evidence"] == []
    assert diagnosis["earliest_constitutional_blocker"]["boundary"] == (
        "UNKNOWN_INCOMPLETE_DIAGNOSIS_EVIDENCE"
    )
    assert diagnosis["minimal_revalidation_scope"]["full_regression"][
        "required"
    ] is True
    assert diagnosis["automatic_repair_performed"] is False


def test_supervisor_replay_reconstructs_diagnosis(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    workflow, workflow_replay = _workflow(tmp_path, source)
    diagnosis = _supervise(tmp_path, workflow, workflow_replay)[
        "constitutional_development_supervisor_diagnosis_artifact"
    ]
    reconstructed = reconstruct_constitutional_development_supervisor_replay(
        tmp_path / "supervisor"
    )

    assert reconstructed["diagnosis_hash"] == diagnosis["diagnosis_hash"]
    assert reconstructed["diagnosis_status"] == WORKFLOW_HEALTHY
    assert reconstructed["earliest_constitutional_blocker"] == (
        diagnosis["earliest_constitutional_blocker"]
    )
    assert reconstructed["validation_executed"] is False
    assert reconstructed["automatic_repair_performed"] is False


def test_supervisor_replay_tamper_is_rejected(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    workflow, workflow_replay = _workflow(tmp_path, source)
    _supervise(tmp_path, workflow, workflow_replay)
    replay_file = (
        tmp_path
        / "supervisor/"
        "002_constitutional_development_supervisor_diagnosis_recorded.json"
    )
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["automatic_repair_performed"] = True
    replay_file.write_text(
        json.dumps(wrapper, sort_keys=True),
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_constitutional_development_supervisor_replay(
            tmp_path / "supervisor"
        )


def test_public_validator_rejects_rehashed_authority_escalation(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    workflow, workflow_replay = _workflow(tmp_path, source)
    diagnosis = _supervise(tmp_path, workflow, workflow_replay)[
        "constitutional_development_supervisor_diagnosis_artifact"
    ]
    diagnosis["authority_flags"]["performs_automatic_repair"] = True
    diagnosis["diagnosis_hash"] = replay_hash(
        {
            key: value
            for key, value in diagnosis.items()
            if key not in {"diagnosis_hash", "artifact_hash"}
        }
    )
    diagnosis["artifact_hash"] = replay_hash(
        {
            key: value
            for key, value in diagnosis.items()
            if key != "artifact_hash"
        }
    )

    with pytest.raises(FailClosedRuntimeError, match="supervision policy"):
        validate_constitutional_development_supervisor_diagnosis_artifact(
            diagnosis
        )


def test_supervisor_has_no_execution_or_repair_dependencies() -> None:
    module = __import__(
        "aigol.runtime.constitutional_development_supervisor_runtime",
        fromlist=["unused"],
    )
    runtime_source = open(module.__file__, encoding="utf-8").read()

    assert "reconstruct_intelligent_validation_orchestration_replay" in (
        runtime_source
    )
    assert "execute_governed_validation" not in runtime_source
    assert "compose_platform_validation_candidate" not in runtime_source
    assert "orchestrate_intelligent_validation_planning(" not in (
        runtime_source
    )
    assert "analyze_failed_validation(" not in runtime_source
    assert "import subprocess" not in runtime_source
    assert "import pytest" not in runtime_source
    assert "aigol.provider" not in runtime_source
    assert "aigol.cli" not in runtime_source
    assert "apply_patch" not in runtime_source


def test_g43_capability_is_certified_metadata_only() -> None:
    capability_id = "CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR"
    record = lookup_platform_capability_certification(capability_id)

    assert is_platform_capability_certified(capability_id) is True
    assert record["certification_milestone"] == "G43-01"
    assert record["implementation_owner"] == (
        "aigol.runtime.constitutional_development_supervisor_runtime"
    )
    assert record["architectural_owner"] == "PLATFORM_CORE"
