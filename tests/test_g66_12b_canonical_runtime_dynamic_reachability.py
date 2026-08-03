"""Dynamic, observation-only validation for the G66-12B canonical spine.

These tests characterize current reachability.  The tracing hook observes
Python call events only; it carries no authority and changes no runtime
decision.
"""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import sys

import pytest

from aigol.cli.aicli import run_reference_uhi_session
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime.grounded_execution_authorization_human_decision_binding import (
    EXECUTION_DECISION_FAILED_CLOSED,
    bind_distinct_human_execution_decision,
)
from aigol.runtime.production_conversation_flow_binding import (
    CFA_DEVELOPMENT_GOVERNANCE,
    CFA_OBJECTIVE_COMMITMENT,
    CFA_PLATFORM_KNOWLEDGE,
    CFA_SELF_KNOWLEDGE,
    reconstruct_production_conversation_flow_binding_v1,
)
from aigol.runtime.worker_invocation_runtime import (
    FAILED_CLOSED,
    invoke_dispatched_worker,
)
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    InMemoryAdapter,
    _pending_state,
)
from test_g66_08_production_human_interaction_stack_e2e import (
    _contexts,
    _reader,
    _submit,
)


CREATED_AT = "2026-08-03T16:00:00Z"
REPOSITORY = Path(__file__).resolve().parents[1]


@contextmanager
def _runtime_call_trace():
    """Collect repository runtime call paths without affecting decisions."""

    paths: set[str] = set()
    previous = sys.gettrace()
    repository_prefix = str(REPOSITORY) + "/"
    path_cache: dict[str, str | None] = {}

    def observe(frame, event, _arg):
        if event == "call":
            filename = frame.f_code.co_filename
            relative = path_cache.get(filename)
            if filename not in path_cache:
                relative = (
                    filename.removeprefix(repository_prefix)
                    if filename.startswith(repository_prefix)
                    else None
                )
                if relative is not None and not relative.startswith(
                    ("aigol/", "runtime/")
                ):
                    relative = None
                path_cache[filename] = relative
            if relative is not None:
                paths.add(relative)
        # Returning no local tracer keeps this hook at call granularity.  It
        # cannot observe or affect line-level execution.
        return None

    sys.settrace(observe)
    try:
        yield paths
    finally:
        sys.settrace(previous)


def _emit(label: str, value) -> None:
    print(f"G66_12B_{label}=" + json.dumps(value, sort_keys=True))


def test_default_channel_reaches_conversation_but_not_platform_admission(
    tmp_path: Path,
) -> None:
    with _runtime_call_trace() as traced:
        self_result = _submit(
            tmp_path, "Show architecture.", session="G66-12B-SELF"
        )
        platform_result = _submit(
            tmp_path,
            "What platform capabilities are available?",
            session="G66-12B-PLATFORM",
        )
        development_result = _submit(
            tmp_path,
            "Implement a validator.",
            session="G66-12B-DEVELOPMENT",
        )

    self_context = self_result["platform_core_project_services_context"]
    platform_context = platform_result["platform_core_project_services_context"]
    development_context = development_result[
        "platform_core_project_services_context"
    ]
    self_binding = self_context["production_conversation_flow_binding"]
    platform_binding = platform_context["production_conversation_flow_binding"]
    development_binding = development_context[
        "production_conversation_flow_binding"
    ]

    assert self_binding["requested_target_flow_id"] == CFA_SELF_KNOWLEDGE
    assert platform_binding["requested_target_flow_id"] == CFA_PLATFORM_KNOWLEDGE
    for context in (self_context, platform_context):
        assert context["project_objective_inference"] is None
        assert context["admission_precedence"] is None
        assert context["constitutional_development_governance"] is None
        assert context["governed_read_only_work_result"][
            "presentation_status"
        ] == "PRESENTATION_READY"
    assert development_binding["requested_target_flow_id"] == (
        CFA_DEVELOPMENT_GOVERNANCE
    )
    assert development_binding["permitted_next_flow_id"] == (
        CFA_OBJECTIVE_COMMITMENT
    )
    assert development_context["project_objective_inference"] is None
    assert development_context["admission_precedence"] is None
    assert development_context["constitutional_development_governance"] is None
    assert development_context["owner_bound_clarification_envelope"][
        "originating_owner"
    ] == "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY"
    assert development_result["runtime_entered"] is False
    assert development_binding["authorization_created"] is False
    assert development_binding["worker_invoked"] is False
    assert development_binding["execution_invoked"] is False

    expected = {
        "aigol/cli/aicli.py",
        "aigol/runtime/human_interface_runtime_entry_service.py",
        "aigol/runtime/production_conversation_flow_binding.py",
        "aigol/runtime/platform_core_conversation_working_memory_runtime_v2.py",
        "aigol/runtime/platform_core_project_services.py",
        "aigol/runtime/platform_query_router.py",
    }
    assert expected <= traced
    assert "aigol/runtime/execution_authorization_runtime.py" not in traced
    assert "aigol/runtime/worker_invocation_runtime.py" not in traced
    assert "aigol/runtime/governed_termination_runtime.py" not in traced
    _emit("DEFAULT_RUNTIME_FILES", sorted(traced))


def test_clarification_and_typed_turns_reuse_state_without_admission(
    tmp_path: Path,
) -> None:
    session = "G66-12B-MULTI-TURN"
    with _runtime_call_trace() as traced:
        result = run_reference_uhi_session(
            session_id=session,
            created_at=CREATED_AT,
            runtime_root=tmp_path,
            workspace=".",
            input_reader=_reader(
                [
                    "Implement a validator.",
                    "/send",
                    "/reply action: implement",
                    "/send",
                    "subject: validator",
                    "/send",
                    "outcome: validated requests",
                    "/send",
                    "work-type: implementation",
                    "/send",
                    "/confirm",
                    "/send",
                    "/commit",
                    "/send",
                    "/approve",
                    "/exit",
                ]
            ),
            output_writer=lambda _line: None,
        )

    contexts = _contexts(tmp_path, session)
    assert len(contexts) == 7
    bindings = [item["production_conversation_flow_binding"] for item in contexts]
    first = bindings[0]
    assert all(binding == first for binding in bindings)
    assert all(binding["cwm_revision"] == 1 for binding in bindings)
    assert all(item["project_objective_inference"] is None for item in contexts)
    assert all(item["admission_precedence"] is None for item in contexts)
    assert result["approval_count"] == 0
    assert result["runtime_entered"] is False
    assert not list(tmp_path.rglob("*objective_commitment*.json"))
    assert not list(tmp_path.rglob("*execution_authorization*.json"))
    assert not list(tmp_path.rglob("*worker_invocation*.json"))
    replay_root = Path(first["owner_local_replay_references"][0]).parent
    before = reconstruct_production_conversation_flow_binding_v1(replay_root)
    after = reconstruct_production_conversation_flow_binding_v1(replay_root)
    assert before == after
    _emit(
        "MULTI_TURN",
        {
            "context_count": len(contexts),
            "conversation_identity": first["conversation_identity"],
            "cwm_revision": first["cwm_revision"],
            "binding_hash": first["artifact_hash"],
            "admission_executed": False,
            "authorization_executed": False,
            "runtime_files": sorted(traced),
        },
    )


def test_preconstructed_g31_state_reaches_late_spine_but_is_not_default_provenance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "G66-12B-LATE-SPINE")
    with _runtime_call_trace() as traced:
        result = InMemoryAdapter(root).transport(
            state,
            decision.MUTATION_APPROVED,
        )

    assert result["repository_mutated"] is True
    assert result["terminated"] is True
    assert result["execution_certified"] is True
    assert result["filesystem_replace_worker_governed_termination"][
        "termination_status"
    ] == "TERMINATED"
    certification = result[
        "filesystem_replace_worker_final_execution_certification"
    ]
    assert certification["certification_called"] is True
    assert certification["execution_certified"] is True
    for required in (
        "aigol/runtime/human_interface_runtime_entry_service.py",
        "aigol/runtime/worker_invocation_runtime.py",
        "aigol/runtime/worker_result_capture_runtime.py",
        "aigol/runtime/post_execution_replay_review_runtime.py",
        "aigol/runtime/governed_termination_runtime.py",
        "aigol/runtime/governed_termination_to_final_execution_certification_binding_runtime.py",
    ):
        assert required in traced
    _emit("PRECONSTRUCTED_G31_RUNTIME_FILES", sorted(traced))


def test_missing_worker_predecessor_fails_closed_without_invocation(
    tmp_path: Path,
) -> None:
    capture = invoke_dispatched_worker(
        worker_invocation_id="G66-12B-MISSING-PREDECESSOR",
        worker_dispatch_artifact={},
        worker_dispatch_replay_reference=str(tmp_path / "missing-dispatch"),
        invoked_by="G66-12B_VALIDATION",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / "worker-invocation",
    )

    assert capture["invocation_status"] == FAILED_CLOSED
    assert capture["worker_invoked"] is False
    assert capture["worker_invocation_artifact"] is None
    assert capture["invocation_result_artifact"]["failure_reason"]
    assert not (tmp_path / "worker-invocation/002_invocation_artifact_recorded.json").exists()


def test_proposal_approval_artifact_cannot_substitute_for_execution_authorization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(
        tmp_path, monkeypatch, "G66-12B-PROPOSAL-NOT-AUTHORIZATION"
    )
    proposal_approval = state["codex_worker_activation_binding_reconstruction"][
        "activation_approval_artifact"
    ]
    result = bind_distinct_human_execution_decision(
        authorization_review_artifact=proposal_approval,
        human_decision="APPROVE",
        session_id=root.name,
        decided_by="HUMAN_OPERATOR",
        decided_at=CREATED_AT,
        workspace=state["repository_grounding_artifact"]["workspace_root"],
        session_root=root,
        replay_dir=root / "INVALID-PROPOSAL-AS-EXECUTION-AUTHORIZATION",
    )

    assert result["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED
    assert result["execution_authorized"] is False
    assert result["human_confirmation_artifact"] is None


def test_dynamic_files_are_compared_with_frozen_pcbv31_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with _runtime_call_trace() as traced:
        _submit(tmp_path, "Implement a validator.", session="G66-12B-BASELINE")
        root, state = _pending_state(
            tmp_path, monkeypatch, "G66-12B-BASELINE-LATE"
        )
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)

    record = json.loads(
        (
            REPOSITORY
            / ".github/governance/specs/PCBV31_BASELINE_IDENTITY_RECORD_V1.json"
        ).read_text(encoding="utf-8")
    )
    baseline = record["authoritative_identity"]["source_commit"]
    dispositions = {
        path: group["disposition"]
        for group in record["complete_reviewed_inventory"]["dispositions"]
        for path in group["source_paths"]
    }
    drift: list[dict[str, str | None]] = []
    for path in sorted(traced):
        baseline_blob = subprocess.run(
            ["git", "rev-parse", f"{baseline}:{path}"],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
            check=False,
        )
        current_blob = subprocess.run(
            ["git", "hash-object", path],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        baseline_hash = (
            baseline_blob.stdout.strip() if baseline_blob.returncode == 0 else None
        )
        if baseline_hash != current_blob:
            drift.append(
                {
                    "path": path,
                    "baseline_disposition": dispositions.get(path),
                    "baseline_blob": baseline_hash,
                    "current_blob": current_blob,
                    "drift": "CHANGED_BLOB"
                    if baseline_hash is not None
                    else "NOT_PRESENT_IN_PCBV31",
                }
            )

    assert any(
        item["path"] == "aigol/runtime/human_interface_runtime_entry_service.py"
        and item["drift"] == "CHANGED_BLOB"
        for item in drift
    )
    assert any(
        item["path"] == "aigol/runtime/production_conversation_flow_binding.py"
        and item["drift"] == "NOT_PRESENT_IN_PCBV31"
        for item in drift
    )
    _emit(
        "PCBV31_DYNAMIC_DRIFT",
        {
            "baseline_commit": baseline,
            "dynamic_file_count": len(traced),
            "unauthenticated_current_blob_count": len(drift),
            "files": drift,
        },
    )
