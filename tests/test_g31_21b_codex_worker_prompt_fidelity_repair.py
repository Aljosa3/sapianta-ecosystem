from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.codex_worker_activation_binding_runtime import (
    reconstruct_codex_worker_activation_replay,
)
from aigol.runtime.transport.serialization import replay_hash
from sapianta_system.runtime.codex_synthesis import (
    create_governed_codex_task_request,
    create_governed_codex_worker_execution_contract,
    synthesize_governed_codex_task,
)
from test_g31_17b_governed_execution_to_codex_worker_activation_binding import (
    RecordingRunner,
    _activate_direct,
)
from test_g31_20f_disposable_repository_scope_grounding_fixture_contract import (
    CREATED_AT,
    GROUNDED_REQUEST,
    _workspace,
)


def _two_decisions(tmp_path: Path, session: str) -> tuple[dict, Path, Path]:
    workspace = _workspace(tmp_path, name=f"{session}-workspace")
    runtime_root = tmp_path / "runtime"
    values = iter([GROUNDED_REQUEST, "/send", "/approve", "/approve", "/exit"])
    previous = Path.cwd()
    os.chdir(workspace)
    try:
        result = aicli.run_reference_uhi_session(
            session_id=session,
            created_at=CREATED_AT,
            runtime_root=runtime_root,
            workspace=workspace,
            input_reader=lambda _prompt: next(values),
            output_writer=lambda _value: None,
        )
    finally:
        os.chdir(previous)
    return result["runtime_result"], runtime_root / session, workspace


def _contract() -> dict:
    return create_governed_codex_worker_execution_contract(
        authorized_task=GROUNDED_REQUEST,
        grounded_targets=[
            {
                "target_role": "IMPLEMENTATION",
                "target_path": "aigol/runtime/human_interface.py",
                "target_evidence_hash": "sha256:implementation",
            },
            {
                "target_role": "FOCUSED_TEST",
                "target_path": "tests/test_human_interface.py",
                "target_evidence_hash": "sha256:test",
            },
        ],
        requested_output_type="UNIFIED_DIFF",
    )


def test_grounded_activation_prompt_preserves_exact_task_targets_output_and_role(
    tmp_path: Path,
) -> None:
    runtime, _, _ = _two_decisions(tmp_path, "G31-21B-PROMPT")
    admission = runtime["codex_synthesis_preflight_capture"]
    final = runtime["codex_worker_activation_synthesis_preflight_capture"]
    prompt = final["bounded_codex_prompt"]
    contract = final["worker_execution_contract"]

    assert admission["worker_execution_contract"] is None
    assert admission["final_character_count"] <= 240
    assert final["final_character_count"] <= 240
    assert contract["authorized_task"] == GROUNDED_REQUEST
    assert f"PRIMARY AUTHORIZED TASK:\n{json.dumps(GROUNDED_REQUEST)}" in prompt
    assert "You are CODEX, the selected Worker" in prompt
    assert '"aigol/runtime/human_interface.py"' in prompt
    assert '"tests/test_human_interface.py"' in prompt
    assert "Output type: UNIFIED_DIFF." in prompt
    assert "Return only a minimal unified diff through stdout" in prompt
    assert "Do not mutate files" in prompt
    assert "Prepare a bounded runtime validation task." not in prompt
    assert "Preview-only downstream Codex task formation" not in prompt
    assert final["worker_prompt_fidelity_verified"] is True
    assert final["file_mutation_allowed"] is False
    assert final["bounded_codex_prompt_sha256"] == sha256(prompt.encode()).hexdigest()


def test_exact_prompt_and_hash_are_identical_across_review_approval_request_receipt_and_process(
    tmp_path: Path,
) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-21B-CHAIN")
    final = runtime["codex_worker_activation_synthesis_preflight_capture"]
    prompt = final["bounded_codex_prompt"]
    prompt_hash = final["bounded_codex_prompt_sha256"]
    runner = RecordingRunner(stdout="bounded unaccepted Worker output")
    activation = _activate_direct(
        runtime, root, workspace, root / "activation", runner
    )
    review = activation["activation_review_artifact"]["interpreted_intent"]
    approval = activation["activation_approval_artifact"]
    request = activation["codex_execution_request"]
    receipt = activation["codex_transport_receipt"]

    assert review["bounded_codex_prompt_sha256"] == prompt_hash
    assert approval["bounded_codex_prompt_sha256"] == prompt_hash
    assert request["bounded_prompt_sha256"] == prompt_hash
    assert request["handoff_package"]["codex_prompt"] == prompt
    assert request["handoff_package"]["bounded_prompt_sha256"] == prompt_hash
    assert receipt["bounded_prompt_sha256"] == prompt_hash
    replay = reconstruct_codex_worker_activation_replay(
        activation["activation_replay_reference"]
    )
    assert replay["bounded_codex_prompt_sha256"] == prompt_hash
    assert runner.calls == [
        (
            ["codex", "exec", prompt],
            {
                "capture_output": True,
                "text": True,
                "shell": False,
                "timeout": 60,
            },
        )
    ]
    assert activation["worker_prompt_fidelity_verified"] is True
    assert activation["semantic_worker_result_captured"] is False
    assert activation["result_accepted"] is False
    assert activation["repository_mutated"] is False


@pytest.mark.parametrize(
    ("field", "change"),
    (
        ("authorized_task", lambda value: value + " substituted"),
        (
            "grounded_targets",
            lambda value: [
                {**value[0], "target_path": value[1]["target_path"]},
                value[1],
            ],
        ),
        ("requested_output_type", lambda _value: "PLAN"),
        ("worker_role", lambda _value: "PROVIDER"),
        ("constraints", lambda value: {**value, "file_mutation_allowed": True}),
    ),
)
def test_task_target_output_role_and_constraint_substitution_fail_closed(
    field: str,
    change,
) -> None:
    contract = _contract()
    contract[field] = change(contract[field])
    request = create_governed_codex_task_request(
        natural_language=f"runtime validation: {GROUNDED_REQUEST}",
        worker_execution_contract=contract,
    )
    response = synthesize_governed_codex_task(request)

    assert response["status"] == "BLOCKED"
    assert response["allowed_to_execute_automatically"] is False


def test_prompt_hash_substitution_after_review_fails_before_process(
    tmp_path: Path,
) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-21B-SUBSTITUTION")
    review = deepcopy(
        runtime["codex_worker_activation_review_capture"]["activation_review_artifact"]
    )
    review["interpreted_intent"]["bounded_codex_prompt_sha256"] = "0" * 64
    review["artifact_hash"] = replay_hash(
        {key: value for key, value in review.items() if key != "artifact_hash"}
    )
    runtime["codex_worker_activation_review_capture"]["activation_review_artifact"] = review
    runner = RecordingRunner()

    with pytest.raises(FailClosedRuntimeError, match="review or lineage"):
        _activate_direct(runtime, root, workspace, root / "activation", runner)
    assert runner.calls == []
