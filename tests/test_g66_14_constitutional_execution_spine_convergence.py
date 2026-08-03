from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.cli.aicli import run_reference_uhi_session
from aigol.runtime.governed_termination_runtime import (
    reconstruct_governed_termination_replay,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.post_execution_replay_review_runtime import (
    reconstruct_post_execution_replay_review,
)
from aigol.runtime.replay_certification_runtime import (
    reconstruct_replay_certification_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


SESSION = "G66-14-CONSTITUTIONAL-SPINE"
CREATED = "2026-08-03T20:00:00Z"


def _time(second: int) -> str:
    return f"2026-08-03T20:00:{second:02d}Z"


def _manifest(root: Path) -> dict:
    return create_implementation_manifest(
        manifest_id="MANIFEST-G66-14-000001",
        canonical_chain_id="CHAIN-G66-14-000001",
        implementation_bundle_id="G66_14_EXECUTION_SPINE",
        source_candidate_reference="CANDIDATE-G66-14-000001",
        source_candidate_hash=replay_hash({"source": "G66-14"}),
        implementation_handoff_reference="HANDOFF-G66-14-000001",
        implementation_handoff_hash=replay_hash({"handoff": "G66-14"}),
        provider_generation_authorization_reference="AUTH-G66-14-000001",
        provider_generation_authorization_hash=replay_hash({"auth": "G66-14"}),
        provider_response_reference="RESPONSE-G66-14-000001",
        provider_response_hash=replay_hash({"response": "G66-14"}),
        target_domain="PLATFORM_CORE",
        target_resource="G66_14_EXECUTION_SPINE",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G66-14-000001",
                "target_path": "bounded/g66_14_target.py",
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
        replay_dir=root / "manifest",
    )["implementation_manifest_artifact"]


def _entry(
    root: Path,
    workspace: Path,
    request: str,
    *,
    second: int,
    artifacts: list[dict] | None = None,
) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="aicli",
        session_id=SESSION,
        human_requests=[request],
        created_at=_time(second),
        runtime_root=root,
        workspace=workspace,
        governed_runtime_runner=run_interactive_conversation,
        explicit_canonical_artifacts=artifacts or [],
    )


def _prepare_default_path(tmp_path: Path) -> tuple[Path, Path, dict]:
    root = tmp_path / "runtime"
    workspace = tmp_path / "workspace"
    _entry(root, workspace, "Implement a validator.", second=1)
    captures = [
        _entry(root, workspace, text, second=index)
        for index, text in enumerate(
            (
                "action: Implement and normalize",
                "subject: a repository implementation change",
                "outcome: canonical change evidence",
                "work-type: ANALYSIS",
            ),
            start=2,
        )
    ]
    confirmation = _entry(
        root,
        workspace,
        captures[-1]["canonical_typed_semantic_composition"][
            "expected_confirmation_action"
        ],
        second=6,
    )
    committed = _entry(
        root,
        workspace,
        confirmation["canonical_typed_semantic_composition"][
            "expected_commit_action"
        ],
        second=7,
        artifacts=[_manifest(tmp_path / "artifact")],
    )
    return root, workspace, committed


def test_default_canonical_path_reaches_final_certification(tmp_path: Path) -> None:
    root, workspace, committed = _prepare_default_path(tmp_path)
    prepared = committed["committed_objective_execution_preparation"]

    assert committed["committed_objective_admission"]["admission_status"] == (
        "COMMITTED_OBJECTIVE_ADMITTED_TO_PLATFORM_CORE"
    )
    assert prepared["preparation_status"] == (
        "EXECUTION_PREPARED_AWAITING_AUTHORIZATION"
    )
    assert prepared["execution_ready"]["execution_ready_status_artifact"][
        "execution_status"
    ] == "EXECUTION_READY"
    assert prepared["prepared_artifact"]["authorization_granted"] is False

    authorized = _entry(
        root,
        workspace,
        prepared["expected_authorization_action"],
        second=8,
    )
    completed = authorized["constitutional_execution_spine_completion"]
    assert completed["authorization"]["authorization_status"] == (
        "EXECUTION_AUTHORIZED"
    )
    assert completed["authorization"]["execution_authorization_artifact"][
        "authorized_at"
    ] == _time(8)
    assert completed["worker_assignment"]["assignment_status"] == "WORKER_ASSIGNED"
    assert completed["worker_dispatch"]["dispatch_status"] == "WORKER_DISPATCHED"
    assert completed["worker_invocation"]["invocation_status"] == "WORKER_INVOKED"
    assert completed["worker_assignment"]["worker_family"] == "FILESYSTEM"
    assert completed["execution"]["execution_artifact"]["execution_started"] is True
    assert completed["execution"]["execution_artifact"]["provider_authority"] is False
    assert completed["worker_result_capture"]["result_capture_status"] == (
        "WORKER_RESULT_CAPTURED"
    )
    assert completed["worker_result_validation"]["validation_status"] == (
        "RESULT_VALIDATED"
    )
    assert completed["post_execution_replay_review"]["review_status"] == (
        "REVIEW_COMPLETED"
    )
    assert completed["governed_termination"]["termination_status"] == "TERMINATED"
    assert completed["final_execution_certification"]["binding_status"] == (
        "G31_FINAL_EXECUTION_CERTIFICATION_COMPLETED"
    )
    assert completed["final_execution_certification"]["execution_certified"] is True
    assert len(completed["replay_evidence"]) == 14


def test_wrong_execution_authorization_fails_before_worker(tmp_path: Path) -> None:
    root, workspace, committed = _prepare_default_path(tmp_path)
    integration_root = Path(
        committed["committed_objective_execution_preparation"]["integration_root"]
    )

    with pytest.raises(FailClosedRuntimeError, match="exact /authorize"):
        _entry(
            root,
            workspace,
            "/authorize sha256:" + "0" * 64,
            second=8,
        )

    assert not (integration_root / "authorization").exists()
    assert not (integration_root / "worker_assignment").exists()
    assert not (integration_root / "worker_dispatch").exists()
    assert not (integration_root / "post_execution_replay_review").exists()
    assert not (integration_root / "final_execution_certification").exists()


def test_tampered_preparation_evidence_fails_before_authorization(
    tmp_path: Path,
) -> None:
    root, workspace, committed = _prepare_default_path(tmp_path)
    prepared = committed["committed_objective_execution_preparation"]
    integration_root = Path(prepared["integration_root"])
    summary_path = Path(
        prepared["prepared_artifact"]["execution_summary_reference"]
    )
    summary = load_json(summary_path)
    summary["original_request"] = "tampered after preparation"
    summary_path.write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="execution summary"):
        _entry(
            root,
            workspace,
            prepared["expected_authorization_action"],
            second=8,
        )

    assert not (integration_root / "authorization").exists()
    assert not (integration_root / "worker_assignment").exists()


def test_real_default_aicli_reaches_replay_termination_and_certification(
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "runtime"
    workspace = tmp_path / "workspace"
    _manifest(workspace / "artifact")
    manifest_path = (
        workspace
        / "artifact"
        / "manifest"
        / "000_implementation_manifest_recorded.json"
    )
    outputs: list[str] = []
    fixed = iter(
        [
            "Implement a validator.",
            "/send",
            "action: Implement and normalize",
            "/send",
            "subject: a repository implementation change",
            "/send",
            "outcome: canonical change evidence",
            "/send",
            "work-type: ANALYSIS",
            "/send",
        ]
    )
    phase = 0

    def reader(_prompt: str) -> str:
        nonlocal phase
        try:
            return next(fixed)
        except StopIteration:
            rendered = "\n".join(outputs)
            if phase == 0:
                phase = 1
                return re.findall(r"/confirm sha256:[0-9a-f]{64}", rendered)[-1]
            if phase == 1:
                phase = 2
                return "/send"
            if phase == 2:
                phase = 3
                return re.findall(r"/commit sha256:[0-9a-f]{64}", rendered)[-1]
            if phase == 3:
                phase = 4
                return "/send"
            if phase == 4:
                prepared = list(
                    runtime_root.rglob("001_execution_prepared.json")
                )
                assert len(prepared) == 1
                phase = 5
                return load_json(prepared[0])["expected_authorization_action"]
            if phase == 5:
                phase = 6
                return "/send"
            return "/exit"

    result = run_reference_uhi_session(
        session_id=SESSION,
        created_at=CREATED,
        runtime_root=runtime_root,
        workspace=workspace,
        input_reader=reader,
        output_writer=outputs.append,
        artifact_references=[str(manifest_path)],
    )

    completed_paths = list(runtime_root.rglob("002_execution_completed.json"))
    assert len(completed_paths) == 1
    completed = load_json(completed_paths[0])
    assert completed["execution_certified"] is True
    review_paths = list(runtime_root.rglob("post_execution_replay_review"))
    termination_paths = list(runtime_root.rglob("governed_termination"))
    certification_paths = list(runtime_root.rglob("final_execution_certification"))
    assert len(review_paths) == len(termination_paths) == len(certification_paths) == 1
    assert reconstruct_post_execution_replay_review(review_paths[0])[
        "review_status"
    ] == "REVIEW_COMPLETED"
    assert reconstruct_governed_termination_replay(termination_paths[0])[
        "termination_status"
    ] == "TERMINATED"
    assert reconstruct_replay_certification_replay(certification_paths[0])[
        "certification_status"
    ] == "REPLAY_CERTIFICATION_COMPLETED"
    assert result["runtime_entered"] is False
