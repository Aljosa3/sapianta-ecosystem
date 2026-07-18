from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil

import pytest

from aigol.cli import aicli
from aigol.runtime import approved_durable_work_repository_scope_grounding as grounding_runtime
from aigol.runtime.approved_durable_work_repository_scope_grounding import (
    REPOSITORY_SCOPE_GROUNDED,
    REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED,
    ground_approved_durable_work_repository_scope,
    reconstruct_approved_durable_work_repository_scope_grounding,
    validate_approved_durable_work_repository_scope_grounding,
)
from aigol.runtime.approved_durable_work_worker_payload_binding import (
    bind_approved_durable_work_to_worker_payload,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    consume_approved_implementation_turn_binding,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-18T00:00:00Z"
GROUNDED_REQUEST = (
    "Improve the human interface summary by proposing a change to "
    "aigol/runtime/human_interface.py for tests/test_human_interface.py. Return a "
    "unified diff only; do not edit files."
)
GENERIC_REQUEST = (
    "Fix the failing addition test in calc.py and test_calc.py. Return a minimal "
    "unified diff only; do not edit files."
)


def _rehash(artifact: dict) -> None:
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )


def _workspace(
    tmp_path: Path,
    *,
    name: str,
    implementation: bool = True,
    test: bool = True,
    mismatched_test: bool = False,
) -> Path:
    workspace = tmp_path / name
    (workspace / ".git").mkdir(parents=True)
    (workspace / "aigol" / "runtime").mkdir(parents=True)
    (workspace / "tests").mkdir()
    if implementation:
        (workspace / "aigol" / "runtime" / "human_interface.py").write_text(
            "def render_summary(value):\n    return f'Status: {value}'\n",
            encoding="utf-8",
        )
    if test:
        test_name = "test_unrelated.py" if mismatched_test else "test_human_interface.py"
        (workspace / "tests" / test_name).write_text(
            "from aigol.runtime.human_interface import render_summary\n\n"
            "def test_render_summary():\n"
            "    assert render_summary('ready') == 'Summary: ready'\n",
            encoding="utf-8",
        )
    return workspace


def _payload(
    tmp_path: Path,
    *,
    request: str,
    workspace: Path,
    session_id: str,
) -> dict:
    binding = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session_id,
        message=request,
        runtime_root=tmp_path / f"runtime-{session_id}",
        workspace=workspace,
        created_at=CREATED_AT,
    )["canonical_implementation_turn_binding"]
    consumption = consume_approved_implementation_turn_binding(
        binding_artifact=binding,
        development_composition_plan_hash=binding["development_composition_plan_hash"],
        durable_governed_work_hash=binding["durable_governed_work_hash"],
        proposal_preview_hash=binding["proposal_preview_hash"],
        approval_request_hash=binding["approval_request_hash"],
        created_at=CREATED_AT,
        replay_dir=binding["replay_reference"],
    )
    return bind_approved_durable_work_to_worker_payload(
        implementation_turn_binding=binding,
        approval_consumption_artifact=consumption,
        requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"payload-{session_id}",
    )


def _ground(
    tmp_path: Path,
    *,
    workspace: Path,
    request: str = GROUNDED_REQUEST,
    session_id: str,
) -> dict:
    payload = _payload(
        tmp_path,
        request=request,
        workspace=workspace,
        session_id=session_id,
    )
    return ground_approved_durable_work_repository_scope(
        worker_payload_binding_artifact=payload,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"grounding-{session_id}",
    )


def test_generic_general_project_goal_remains_rejected(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, name="generic")
    grounding = _ground(
        tmp_path,
        workspace=workspace,
        request=GENERIC_REQUEST,
        session_id="G31-20F-GENERIC",
    )

    assert grounding["canonical_capability_target"] == "general_project_goal"
    assert grounding["grounding_status"] == REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED


def test_one_exact_implementation_test_pair_is_grounded(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, name="exact")
    grounding = _ground(
        tmp_path,
        workspace=workspace,
        session_id="G31-20F-EXACT",
    )

    assert grounding["grounding_status"] == REPOSITORY_SCOPE_GROUNDED
    assert grounding["canonical_capability_target"] == "human_interface"
    assert grounding["repository_cognition_entry"]["implementation"] == [
        "aigol/runtime/human_interface.py"
    ]
    assert grounding["repository_cognition_entry"]["tests"] == [
        "tests/test_human_interface.py"
    ]
    assert grounding["grounded_repository_targets"] == [
        "aigol/runtime/human_interface.py",
        "tests/test_human_interface.py",
    ]


@pytest.mark.parametrize(
    ("implementation", "test", "mismatched_test"),
    ((False, True, False), (True, False, False), (True, True, True)),
)
def test_missing_or_mismatched_capability_evidence_fails_closed(
    tmp_path: Path,
    implementation: bool,
    test: bool,
    mismatched_test: bool,
) -> None:
    workspace = _workspace(
        tmp_path,
        name=f"missing-{implementation}-{test}-{mismatched_test}",
        implementation=implementation,
        test=test,
        mismatched_test=mismatched_test,
    )
    grounding = _ground(
        tmp_path,
        workspace=workspace,
        session_id=f"G31-20F-MISSING-{implementation}-{test}-{mismatched_test}",
    )

    assert grounding["grounding_status"] == REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED
    assert grounding["grounded_repository_targets"] == []


def test_multiple_implementation_candidates_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = _workspace(tmp_path, name="multiple-implementation")
    monkeypatch.setattr(
        grounding_runtime,
        "detect_capabilities",
        lambda _root: {
            "human_interface": {
                "key": "human_interface",
                "implementation": [
                    "aigol/runtime/human_interface.py",
                    "aigol/runtime/second.py",
                ],
                "tests": ["tests/test_human_interface.py"],
            }
        },
    )
    grounding = _ground(
        tmp_path,
        workspace=workspace,
        session_id="G31-20F-MULTIPLE-IMPLEMENTATION",
    )

    assert grounding["grounding_status"] == REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED
    assert "ambiguous" in grounding["failure_reason"]


def test_multiple_same_capability_test_candidates_fail_closed(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, name="multiple-tests")
    nested = workspace / "tests" / "nested"
    nested.mkdir()
    shutil.copyfile(
        workspace / "tests" / "test_human_interface.py",
        nested / "test_human_interface.py",
    )
    grounding = _ground(
        tmp_path,
        workspace=workspace,
        session_id="G31-20F-MULTIPLE-TESTS",
    )

    assert grounding["grounding_status"] == REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED
    assert "ambiguous" in grounding["failure_reason"]


def test_changed_repository_content_invalidates_grounding(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, name="changed-content")
    grounding = _ground(
        tmp_path,
        workspace=workspace,
        session_id="G31-20F-CHANGED-CONTENT",
    )
    (workspace / "aigol" / "runtime" / "human_interface.py").write_text(
        "def render_summary(value):\n    return value.upper()\n",
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="stale or substituted"):
        reconstruct_approved_durable_work_repository_scope_grounding(
            grounding["replay_reference"],
            workspace=workspace,
        )


def test_identical_cross_session_workspace_grounding_fails_closed(tmp_path: Path) -> None:
    workspace_a = _workspace(tmp_path, name="session-a")
    grounding = _ground(
        tmp_path,
        workspace=workspace_a,
        session_id="G31-20F-SESSION-A",
    )
    workspace_b = _workspace(tmp_path, name="session-b")

    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        validate_approved_durable_work_repository_scope_grounding(
            grounding,
            workspace=workspace_b,
        )


@pytest.mark.parametrize("substitution", ("capability", "target"))
def test_capability_and_target_substitution_fail_closed(
    tmp_path: Path, substitution: str
) -> None:
    workspace = _workspace(tmp_path, name=f"substitution-{substitution}")
    grounding = _ground(
        tmp_path,
        workspace=workspace,
        session_id=f"G31-20F-SUBSTITUTION-{substitution}",
    )
    changed = deepcopy(grounding)
    if substitution == "capability":
        changed["canonical_capability_target"] = "replay"
    else:
        changed["target_evidence"][0]["target_path"] = (
            "aigol/runtime/substituted.py"
        )
    _rehash(changed)

    with pytest.raises(FailClosedRuntimeError):
        validate_approved_durable_work_repository_scope_grounding(
            changed,
            workspace=workspace,
        )


def test_worker_never_starts_before_successful_grounding(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, name="aicli-generic")
    values = iter(
        [GENERIC_REQUEST, "/send", "/approve", "/approve", "/approve", "/exit"]
    )

    def forbidden_process(*_args, **_kwargs):
        raise AssertionError("Worker process started before repository grounding")

    result = aicli.run_reference_uhi_session(
        session_id="G31-20F-NO-WORKER",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "no-worker-runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(values),
        output_writer=lambda _line: None,
        worker_process_runner=forbidden_process,
    )

    assert result["approval_count"] == 1
    assert result["process_start_count"] == 0
    assert result["runtime_result"]["repository_scope_grounding_status"] == (
        REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED
    )
