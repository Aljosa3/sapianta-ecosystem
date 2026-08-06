from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.runtime import codex_worker_activation_binding_runtime as activation
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime import (
    governed_termination_to_final_execution_certification_binding_runtime
    as final_certification,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g71_07_constitutional_m13_acceptance_and_provenance_migration import (
    CREATED_AT,
    POSTIMAGE,
    PREIMAGE,
    TARGET,
    _accepted_lineage,
)


ACTOR = "HUMAN_OPERATOR"


def _m14_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> tuple[dict, dict]:
    lineage = _accepted_lineage(tmp_path, name)
    session_root = lineage["session_root"]
    grounding = lineage["grounding"]
    (lineage["workspace"] / TARGET).chmod(0o644)
    activation_binding = {
        "lineage": {"grounding": deepcopy(grounding)},
        "activation_replay_reference": str(session_root / "ACTIVATION"),
        "activation_replay_hash": replay_hash(f"{name}-activation-replay"),
        "activation_approval_artifact": {
            "approval_id": f"{name}-ACTIVATION",
            "artifact_hash": replay_hash(f"{name}-activation-approval"),
        },
    }
    monkeypatch.setattr(
        activation,
        "reconstruct_codex_worker_activation_binding",
        lambda **_kwargs: deepcopy(activation_binding),
    )
    context = decision.prepare_existing_file_mutation_decision_context(
        context_id=f"{name}-MUTATION-DECISION",
        candidate_capture=lineage["candidate"],
        acceptance_capture=lineage["accepted"],
        content_decision_capture=lineage["decision"],
        binding_capture=lineage["binding"],
        repository_grounding_artifact=grounding,
        human_actor_id=ACTOR,
        presented_at=CREATED_AT,
        session_root=session_root,
        replay_dir=session_root / "mutation-decision",
    )
    state = {
        "existing_file_mutation_candidate_capture": lineage["candidate"],
        "existing_file_mutation_candidate_reconstruction": lineage[
            "candidate_reconstruction"
        ],
        "generated_content_acceptance_capture": lineage["accepted"],
        "human_content_acceptance_decision_capture": lineage["decision"],
        "codex_replacement_acceptance_prerequisite_binding_capture": lineage[
            "binding"
        ],
        "repository_grounding_artifact": deepcopy(grounding),
        "codex_worker_activation_capture": {
            "activation_replay_reference": str(session_root / "ACTIVATION")
        },
        "codex_worker_activation_binding_reconstruction": activation_binding,
        "governed_worker_execution_capture": {},
        "worker_execution_candidate_capture": {},
        "result_accepted": True,
        "g31_pending_action": {
            "action_type": entry.G31_MUTATION_DECISION,
            "valid_values": [decision.MUTATION_APPROVED, decision.REJECTED],
            "context": context,
        },
    }
    return lineage, state


def _transport(lineage: dict, state: dict, outcome: str) -> dict:
    session_root = lineage["session_root"]
    return entry.run_human_interface_runtime_entry(
        interface_name="g71_08_authenticated_test_adapter",
        session_id=session_root.name,
        human_requests=[],
        created_at=CREATED_AT,
        runtime_root=session_root.parent,
        workspace=lineage["workspace"],
        governed_runtime_runner=lambda *_args, **_kwargs: {},
        g31_application_state=state,
        g31_human_action=outcome,
        g31_human_actor_id=ACTOR,
    )


def test_authenticated_m13_completion_reaches_terminal_m14_certification(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lineage, state = _m14_state(tmp_path, monkeypatch, "G71-08-POSITIVE")

    result = _transport(lineage, state, decision.MUTATION_APPROVED)

    authorization = result["mutation_authorization_actor_replay_reconstruction"]
    request = result["authenticated_replacement_request_reconstruction"]
    worker_result = result["filesystem_replace_worker_result_capture_reconstruction"]
    validation = result[
        "filesystem_replace_worker_result_validation_reconstruction"
    ]
    termination = result[
        "filesystem_replace_worker_governed_termination_reconstruction"
    ]
    certification = result[
        "filesystem_replace_worker_final_execution_certification"
    ]
    candidate = lineage["candidate"][
        "existing_file_mutation_candidate_artifact"
    ]

    assert authorization["mutation_authorized"] is True
    assert authorization["candidate_hash"] == candidate["artifact_hash"]
    assert request["latest_event"] == "REQUEST_VALIDATED"
    assert result["authorization_consumption_reconstruction"][
        "authorization_consumed"
    ] is True
    assert result["worker_execution_status"] == "EXECUTING"
    assert result["worker_execution_performed"] is True
    assert worker_result["result_created"] is True
    assert validation["result_validated"] is True
    assert termination["termination_status"] == "TERMINATED"
    assert certification["binding_status"] == final_certification.SUCCESS
    assert certification["execution_certified"] is True
    assert result["execution_certified"] is True
    assert result["repository_mutated"] is True
    assert result["main_repository_mutated"] is True
    assert (lineage["workspace"] / TARGET).read_text(encoding="utf-8") == POSTIMAGE
    assert all(
        value == value.strip()
        for value in result["g31_canonical_presentations"]
    )


def test_rejected_m14_decision_stops_before_authorization_or_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lineage, state = _m14_state(tmp_path, monkeypatch, "G71-08-REJECTED")

    result = _transport(lineage, state, decision.REJECTED)

    assert result["human_mutation_decision_recorded"] is True
    assert result["mutation_decision_approved"] is False
    assert result["mutation_authorized"] is False
    assert result["repository_mutated"] is False
    assert result["main_repository_mutated"] is False
    assert "mutation_authorization_capture" not in result
    assert "authenticated_replacement_request" not in result
    assert (lineage["workspace"] / TARGET).read_text(encoding="utf-8") == PREIMAGE


def test_substituted_m13_provenance_fails_before_m14_authorization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lineage, state = _m14_state(tmp_path, monkeypatch, "G71-08-TAMPER")
    state["existing_file_mutation_candidate_capture"] = deepcopy(
        state["existing_file_mutation_candidate_capture"]
    )
    state["existing_file_mutation_candidate_capture"][
        "existing_file_mutation_candidate_artifact"
    ]["candidate_provenance"]["postimage_sha256"] = replay_hash(
        "substituted postimage"
    )

    with pytest.raises(FailClosedRuntimeError):
        _transport(lineage, state, decision.MUTATION_APPROVED)

    assert (lineage["workspace"] / TARGET).read_text(encoding="utf-8") == PREIMAGE
    assert not list(lineage["session_root"].rglob("*MUTATION-AUTHORIZATION*"))


def test_terminal_certification_replay_is_exact_and_non_authoritative(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lineage, state = _m14_state(tmp_path, monkeypatch, "G71-08-CERTIFICATION")

    result = _transport(lineage, state, decision.MUTATION_APPROVED)
    certification = result[
        "filesystem_replace_worker_final_execution_certification"
    ]
    projection = certification["result_validation_compatibility_projection"]
    final = certification["final_execution_certification"][
        "replay_certification_artifact"
    ]

    assert len(certification["ordered_replay_references"]) == 5
    assert projection["replay_references"] == certification[
        "ordered_replay_references"
    ]
    assert projection["replay_hashes"] == certification["ordered_replay_hashes"]
    assert final["source_result_validation_hash"] == projection["artifact_hash"]
    assert final["replay_references"] == projection["replay_references"]
    assert final["replay_hashes"] == projection["replay_hashes"]
    assert all(value is False for value in certification["authority_flags"].values())
    assert certification["governance_mutated"] is False
    assert certification["replay_mutated"] is False
