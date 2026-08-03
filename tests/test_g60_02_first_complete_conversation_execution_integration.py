from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import human_interface_conversation_execution_integration_v2 as integration_v2
from aigol.runtime import human_interface_conversation_runtime_v2 as hir_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime.execution_authorization_runtime import EXECUTION_AUTHORIZED
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.platform_change_normalization_execution_binding_runtime import (
    CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION,
)
from aigol.runtime.platform_change_normalization_worker_completion_adapter import (
    WORKER_CAPABILITY_COMPLETED,
)
from aigol.runtime.platform_core_objective_commitment_runtime_v2 import (
    ObjectiveCommitmentError,
)
from aigol.runtime.transport.serialization import replay_hash


WORKSPACE = "/workspace/sapianta"
SESSION = "G60-02-COMPLETE-EXECUTION"
CREATED = "2026-08-01T13:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path: Path) -> dict:
    return create_implementation_manifest(
        manifest_id="MANIFEST-G60-02-000001",
        canonical_chain_id="CHAIN-G60-02-000001",
        implementation_bundle_id="G60_02_NORMALIZATION",
        source_candidate_reference="CANDIDATE-G60-02-000001",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G60-02-000001",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G60-02-000001",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G60-02-000001",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="G60_02_COMPLETION",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G60-02-000001",
                "target_path": "bounded/g60_02_target.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "VALUE = 1\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]


def _time(second: int) -> str:
    return f"2026-08-01T13:00:{second:02d}Z"


def _commitment(tmp_path: Path, *, session: str = SESSION) -> dict:
    hir_v2.create_hir_conversation_session_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        human_identity="local-human",
        created_at=CREATED,
    )
    turns = (
        "action: Review and normalize",
        "subject: a repository implementation change",
        "outcome: canonical change evidence",
        "work-type: ANALYSIS",
    )
    result = None
    for index, text in enumerate(turns, start=1):
        result = hir_v2.admit_hir_semantic_turn_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=session,
            source_turn_text=text,
            observed_at=_time(index),
        )
    assert result is not None
    candidate_digest = result["candidate_review"]["presentation"]["candidate_digest"]
    confirmed = hir_v2.confirm_hir_candidate_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        explicit_confirmation_action=f"/confirm {candidate_digest}",
        observed_at=_time(5),
    )
    return hir_v2.create_hir_objective_commitment_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        explicit_commit_action=confirmed["expected_commit_action"],
        observed_at=_time(6),
    )


def _prepare(tmp_path: Path, *, session: str = SESSION) -> dict:
    commitment = _commitment(tmp_path / "conversation", session=session)
    return integration_v2.prepare_committed_objective_execution_v2(
        commitment_record=commitment["commitment_record"],
        explicit_canonical_artifacts=[_manifest(tmp_path / "artifact")],
        runtime_root=tmp_path / "execution",
        workspace=WORKSPACE,
        session_id=session,
        human_actor="local-human",
        created_at=CREATED,
    )


def _execute(prepared: dict) -> dict:
    return integration_v2.authorize_and_execute_prepared_objective_v2(
        prepared,
        explicit_authorization_action=prepared["expected_authorization_action"],
    )


def test_committed_objective_creates_exact_platform_core_objective_and_admission(
    tmp_path: Path,
) -> None:
    prepared = _prepare(tmp_path)

    assert prepared["platform_core_objective"]["objective_status"] == (
        "PROJECT_OBJECTIVE_SUFFICIENT"
    )
    assert prepared["platform_core_objective"]["source_request"] == (
        "work_type: analysis. Review and normalize a repository implementation "
        "change into canonical change evidence."
    )
    assert prepared["platform_core_admission"]["admission_status"] == (
        "EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED"
    )
    assert prepared["handoff_artifact"]["commitment_identity"] == prepared[
        "commitment_record"
    ]["commitment_identity"]


def test_existing_development_governance_and_capability_owners_prepare_execution(
    tmp_path: Path,
) -> None:
    prepared = _prepare(tmp_path)

    assert prepared["execution_ready"]["execution_ready_status_artifact"][
        "execution_status"
    ] == "EXECUTION_READY"
    assert prepared["semantic_capability_route"]["selected_capability_identifier"] == (
        "PLATFORM_CHANGE_NORMALIZATION"
    )
    assert prepared["capability_execution_binding"][
        "capability_execution_binding_artifact"
    ]["binding_status"] == CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION
    assert prepared["prepared_artifact"]["authorization_granted"] is False
    assert prepared["prepared_artifact"]["worker_dispatched"] is False


def test_authorization_requires_exact_execution_summary_hash_and_has_no_side_effect(
    tmp_path: Path,
) -> None:
    prepared = _prepare(tmp_path)
    with pytest.raises(FailClosedRuntimeError, match="exact /authorize"):
        integration_v2.authorize_and_execute_prepared_objective_v2(
            prepared,
            explicit_authorization_action="/authorize sha256:" + "0" * 64,
        )
    assert not (Path(prepared["integration_root"]) / "authorization").exists()
    assert not (Path(prepared["integration_root"]) / "worker_dispatch").exists()


def test_full_existing_authorization_worker_completion_path_succeeds(
    tmp_path: Path,
) -> None:
    completed = _execute(_prepare(tmp_path))

    assert completed["completion_status"] == (
        integration_v2.COMPLETE_PIPELINE_RETURNED_TO_AICLI
    )
    assert completed["authorization"]["authorization_status"] == EXECUTION_AUTHORIZED
    assert completed["worker_request"]["request_status"] == (
        "WORKER_INVOCATION_REQUEST_CREATED"
    )
    assert completed["worker_assignment"]["assignment_status"] == "WORKER_ASSIGNED"
    assert completed["worker_dispatch"]["dispatch_status"] == "WORKER_DISPATCHED"
    assert completed["worker_invocation"]["invocation_status"] == "WORKER_INVOKED"
    assert completed["execution"]["execution_artifact"]["execution_status"] == (
        "EXECUTING"
    )
    assert completed["worker_result_capture"]["result_capture_status"] == (
        "WORKER_RESULT_CAPTURED"
    )
    assert completed["worker_result_validation"]["validation_status"] == (
        "RESULT_VALIDATED"
    )
    assert completed["worker_completion"]["completion_status"] == (
        WORKER_CAPABILITY_COMPLETED
    )


def test_replay_reconstructs_every_capability_through_completion_owner(
    tmp_path: Path,
) -> None:
    replay = _execute(_prepare(tmp_path))["replay_evidence"]

    assert len(replay) == 14
    assert replay["capability_route"]["route_status"] == (
        "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    )
    assert replay["authorization"]["authorization_status"] == EXECUTION_AUTHORIZED
    assert replay["worker_dispatch"]["dispatch_status"] == "WORKER_DISPATCHED"
    assert replay["worker_invocation"]["invocation_status"] == "WORKER_INVOKED"
    assert replay["completion"]["completion_status"] == WORKER_CAPABILITY_COMPLETED
    assert replay["post_execution_replay_review"]["review_status"] == (
        "REVIEW_COMPLETED"
    )
    assert replay["governed_termination"]["termination_status"] == "TERMINATED"
    assert replay["final_execution_certification"]["certification_status"] == (
        "REPLAY_CERTIFICATION_COMPLETED"
    )


def test_completion_returns_through_hir_and_remains_non_authoritative_in_aicli(
    tmp_path: Path,
) -> None:
    completed = _execute(_prepare(tmp_path))
    visible = completed["human_visible_completion_result"]

    assert completed["hir_return"]["human_interface_completion_returned"] is True
    assert visible["selected_capability_identifier"] == "PLATFORM_CHANGE_NORMALIZATION"
    assert "authenticated Worker path" in visible["message"]
    assert completed["aicli_authorizes"] is False
    assert completed["aicli_executes"] is False
    assert completed["aicli_owns_replay"] is False


def test_tampered_commitment_record_is_rejected_before_platform_core(tmp_path: Path) -> None:
    commitment = _commitment(tmp_path / "conversation")
    tampered = deepcopy(commitment["commitment_record"])
    tampered["candidate_objective_digest"] = "sha256:" + "0" * 64

    with pytest.raises(ObjectiveCommitmentError):
        integration_v2.prepare_committed_objective_execution_v2(
            commitment_record=tampered,
            explicit_canonical_artifacts=[_manifest(tmp_path / "artifact")],
            runtime_root=tmp_path / "execution",
            workspace=WORKSPACE,
            session_id=SESSION,
            human_actor="local-human",
            created_at=CREATED,
        )
    assert not (tmp_path / "execution" / "conversation_execution_v2").exists()


def test_missing_or_multiple_canonical_artifacts_fail_closed(tmp_path: Path) -> None:
    record = _commitment(tmp_path / "conversation")["commitment_record"]
    for artifacts in ([], [{}, {}]):
        with pytest.raises(FailClosedRuntimeError, match="exactly one"):
            integration_v2.prepare_committed_objective_execution_v2(
                commitment_record=record,
                explicit_canonical_artifacts=artifacts,
                runtime_root=tmp_path / "execution",
                workspace=WORKSPACE,
                session_id=SESSION,
                human_actor="local-human",
                created_at=CREATED,
            )


def test_deterministic_repetition_preserves_objective_and_selection_hashes(
    tmp_path: Path,
) -> None:
    left = _prepare(tmp_path / "left", session="G60-02-DETERMINISTIC")
    right = _prepare(tmp_path / "right", session="G60-02-DETERMINISTIC")

    assert left["commitment_record"]["commitment_identity"] == right[
        "commitment_record"
    ]["commitment_identity"]
    assert left["platform_core_objective"]["artifact_hash"] == right[
        "platform_core_objective"
    ]["artifact_hash"]
    assert left["semantic_capability_route"]["selection_hash"] == right[
        "semantic_capability_route"
    ]["selection_hash"]


def test_real_terminal_orchestration_is_complete_and_human_readable(
    tmp_path: Path,
) -> None:
    fixed = iter(
        [
            "action: Review and normalize",
            "subject: a repository implementation change",
            "outcome: canonical change evidence",
            "work-type: ANALYSIS",
        ]
    )
    outputs: list[str] = []
    index = 0

    def reader(prompt: str) -> str:
        nonlocal index
        if index < 4:
            value = next(fixed)
        else:
            value = next(
                item.removeprefix("next: ")
                for item in reversed(outputs)
                if item.startswith("next: ")
            )
        index += 1
        outputs.append(prompt + value)
        return value

    completed = integration_v2.run_complete_conversation_execution_terminal_v2(
        runtime_root=tmp_path / "runtime",
        workspace=WORKSPACE,
        session_id=SESSION,
        human_identity="local-human",
        created_at=CREATED,
        explicit_canonical_artifacts=[_manifest(tmp_path / "artifact")],
        input_reader=reader,
        output_writer=outputs.append,
    )
    transcript = "\n".join(outputs)

    for evidence in (
        "platform_core_objective: PROJECT_OBJECTIVE_SUFFICIENT",
        "platform_core_admission: EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED",
        "development_governance: EXECUTION_READY",
        "capability_selection: PLATFORM_CHANGE_NORMALIZATION",
        "authorization: EXECUTION_AUTHORIZED",
        "worker_dispatch: WORKER_DISPATCHED",
        "worker_invocation: WORKER_INVOKED",
        "completion: WORKER_CAPABILITY_COMPLETED",
        "post_execution_replay_review: REVIEW_COMPLETED",
        "governed_termination: TERMINATED",
        "final_certification: G31_FINAL_EXECUTION_CERTIFICATION_COMPLETED",
        "replay_evidence: 14 stages reconstructed",
        "pipeline_status: COMPLETE_PIPELINE_RETURNED_TO_AICLI",
    ):
        assert evidence in transcript
    assert "human_completion: Platform change normalization completed" in transcript
    assert completed["completion_status"] == (
        integration_v2.COMPLETE_PIPELINE_RETURNED_TO_AICLI
    )


def test_aicli_mode_transports_one_canonical_artifact_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _manifest(tmp_path / "artifact")
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    captured = {}

    def fake_runner(**kwargs):
        captured.update(kwargs)
        return {"completion_status": integration_v2.COMPLETE_PIPELINE_RETURNED_TO_AICLI}

    monkeypatch.setattr(aicli, "run_complete_conversation_execution_terminal_v2", fake_runner)
    assert aicli.main(
        [
            "--session-id",
            SESSION,
            "--created-at",
            CREATED,
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            WORKSPACE,
            "--canonical-artifact-path",
            str(path),
            "conversation-execute-v2",
        ]
    ) == 0
    assert captured["explicit_canonical_artifacts"] == [manifest]


def test_aicli_artifact_transport_rejects_non_object_json(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text("[]", encoding="utf-8")
    args = aicli.build_parser().parse_args(
        ["--canonical-artifact-path", str(path), "conversation-execute-v2"]
    )
    with pytest.raises(FailClosedRuntimeError, match="must be a JSON object"):
        aicli._conversation_execution_artifacts(args)


def test_integration_defines_no_duplicate_execution_owner_functions() -> None:
    source = Path(integration_v2.__file__).read_text(encoding="utf-8")
    for forbidden_definition in (
        "def authorize_execution_ready(",
        "def dispatch_assigned_worker(",
        "def invoke_dispatched_worker(",
        "def start_execution(",
        "def capture_worker_result(",
        "def validate_worker_result(",
        "def complete_platform_change_normalization_worker_capability(",
    ):
        assert forbidden_definition not in source
