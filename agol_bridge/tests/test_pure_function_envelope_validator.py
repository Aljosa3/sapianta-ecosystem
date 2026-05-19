from copy import deepcopy
from pathlib import Path

from agol_bridge.continuity.envelope_validator import (
    AUTHORITY_BOUNDARY_VIOLATION,
    HASH_MISMATCH,
    INVALID_SCHEMA,
    LIFECYCLE_REFERENCE_INVALID,
    MISSING_REFERENCE,
    NEXT_STEP_APPROVAL_CONFUSION,
    PROVIDER_BOUNDARY_VIOLATION,
    REPLAY_REFERENCE_INVALID,
    SEMANTIC_REPLAY_OVERCLAIM,
    VALID,
    canonical_envelope_hash,
    canonical_hash,
    validate_envelope,
)


def _task_package():
    return {
        "task_id": "TASK-1",
        "governance_mode": "governed_execution_bridge",
        "risk_class": "bounded",
        "approval_required": True,
        "codex_prompt": "Run bounded validation.",
        "constraints": ["no hidden execution"],
        "expected_outputs": ["summary"],
        "metadata": {"lifecycle_state": "DISPATCHED"},
    }


def _result_package():
    return {
        "status": "EXECUTION_ACCEPTED",
        "tests": [{"command": "python -B -m pytest agol_bridge/tests", "status": "PASS"}],
        "files_changed": [],
        "artifacts": [],
        "summary": "Bounded validation completed.",
        "requires_human_review": True,
    }


def _replay_records():
    return {
        "AGOL-REPLAY-APPROVED": {"event_type": "APPROVED"},
        "AGOL-REPLAY-DISPATCHED": {"event_type": "DISPATCHED"},
        "AGOL-REPLAY-RETURNED": {"event_type": "RETURNED"},
    }


def _lifecycle_records():
    return [
        {"previous_state": "WAITING_FOR_APPROVAL", "next_state": "APPROVED"},
        {"previous_state": "APPROVED", "next_state": "DISPATCHED"},
        {"previous_state": "DISPATCHED", "next_state": "RETURNED"},
    ]


def _artifact_map():
    return {
        "task_packages": {"TASK-1": _task_package()},
        "result_packages": {"RESULT-1": _result_package()},
        "replay_records": _replay_records(),
        "lifecycle_records": _lifecycle_records(),
    }


def _envelope():
    task = _task_package()
    result = _result_package()
    envelope = {
        "loop_id": "LOOP-1",
        "originating_human_request_ref": {"request_id": "REQ-1"},
        "semantic_context_ref": {
            "source": "ChatGPT / LLM",
            "reasoning_determinism": "NON_DETERMINISTIC_MODEL_NATIVE",
        },
        "task_package_ref": {"task_id": "TASK-1", "package_hash": canonical_hash(task)},
        "result_package_ref": {"result_id": "RESULT-1", "originating_task_id": "TASK-1", "package_hash": canonical_hash(result)},
        "lineage_id": "LINEAGE-1",
        "execution_provider_ref": {
            "provider_id": "codex",
            "provider_role": "EXECUTION_ONLY",
            "governance_authority": False,
            "approval_authority": False,
            "replay_mutation_authority": False,
            "transport_requirement": "governed transport only",
        },
        "governance_state_ref": {"lifecycle_state": "RETURNED"},
        "replay_refs": [
            {"replay_id": "AGOL-REPLAY-APPROVED", "reference_status": "REFERENCED_NOT_MUTATED"},
            {"replay_id": "AGOL-REPLAY-DISPATCHED", "reference_status": "REFERENCED_NOT_MUTATED"},
            {"replay_id": "AGOL-REPLAY-RETURNED", "reference_status": "REFERENCED_NOT_MUTATED"},
        ],
        "lifecycle_refs": [
            {
                "previous_state": "WAITING_FOR_APPROVAL",
                "next_state": "APPROVED",
                "reference_status": "VISIBLE_APPEND_ONLY_REFERENCE",
            },
            {"previous_state": "APPROVED", "next_state": "DISPATCHED", "reference_status": "VISIBLE_APPEND_ONLY_REFERENCE"},
            {"previous_state": "DISPATCHED", "next_state": "RETURNED", "reference_status": "VISIBLE_APPEND_ONLY_REFERENCE"},
        ],
        "semantic_interpretation_boundary": {
            "interpretation_status": "NON_AUTHORITATIVE",
            "semantic_replay_determinism": False,
        },
        "next_step_ref": {"status": "PROPOSED_NOT_APPROVED", "approval_granted": False},
        "authority_boundary_statement": (
            "ChatGPT / LLMs provide semantic cognition only; AiGOL / AGOL governs admissibility, "
            "lifecycle, replay, and boundaries; Codex/providers execute only through governed transport; "
            "sidepanel observes only."
        ),
        "created_at": "1970-01-01T00:00:00Z",
    }
    envelope["envelope_hash"] = canonical_envelope_hash(envelope)
    return envelope


def test_valid_fixture_returns_valid():
    assert validate_envelope(_envelope(), _artifact_map())["status"] == VALID


def test_missing_required_fields_return_invalid_schema():
    envelope = _envelope()
    envelope.pop("lineage_id")
    assert validate_envelope(envelope, _artifact_map())["status"] == INVALID_SCHEMA


def test_missing_task_result_replay_and_lifecycle_references_are_detected():
    envelope = _envelope()
    artifacts = _artifact_map()
    artifacts["task_packages"].pop("TASK-1")
    assert validate_envelope(envelope, artifacts)["status"] == MISSING_REFERENCE

    artifacts = _artifact_map()
    artifacts["result_packages"].pop("RESULT-1")
    assert validate_envelope(envelope, artifacts)["status"] == MISSING_REFERENCE

    artifacts = _artifact_map()
    artifacts["replay_records"].pop("AGOL-REPLAY-RETURNED")
    assert validate_envelope(envelope, artifacts)["status"] == MISSING_REFERENCE

    artifacts = _artifact_map()
    artifacts["lifecycle_records"] = artifacts["lifecycle_records"][:-1]
    assert validate_envelope(envelope, artifacts)["status"] == LIFECYCLE_REFERENCE_INVALID


def test_hash_mismatch_is_detected():
    envelope = _envelope()
    envelope["task_package_ref"]["package_hash"] = "sha256:wrong"
    envelope["envelope_hash"] = canonical_envelope_hash(envelope)
    assert validate_envelope(envelope, _artifact_map())["status"] == HASH_MISMATCH


def test_envelope_hash_mismatch_is_detected():
    envelope = _envelope()
    envelope["envelope_hash"] = "sha256:wrong"
    assert validate_envelope(envelope, _artifact_map())["status"] == HASH_MISMATCH


def test_replay_reference_invalid_is_detected():
    envelope = _envelope()
    envelope["replay_refs"][0]["reference_status"] = "MUTABLE"
    envelope["envelope_hash"] = canonical_envelope_hash(envelope)
    assert validate_envelope(envelope, _artifact_map())["status"] == REPLAY_REFERENCE_INVALID


def test_semantic_replay_overclaim_is_detected():
    envelope = _envelope()
    envelope["semantic_interpretation_boundary"]["semantic_replay_determinism"] = True
    envelope["envelope_hash"] = canonical_envelope_hash(envelope)
    assert validate_envelope(envelope, _artifact_map())["status"] == SEMANTIC_REPLAY_OVERCLAIM


def test_next_step_marked_as_approval_is_detected():
    envelope = _envelope()
    envelope["next_step_ref"]["approval_granted"] = True
    envelope["envelope_hash"] = canonical_envelope_hash(envelope)
    assert validate_envelope(envelope, _artifact_map())["status"] == NEXT_STEP_APPROVAL_CONFUSION


def test_provider_boundary_violation_is_detected():
    envelope = _envelope()
    envelope["execution_provider_ref"]["approval_authority"] = True
    envelope["envelope_hash"] = canonical_envelope_hash(envelope)
    assert validate_envelope(envelope, _artifact_map())["status"] == PROVIDER_BOUNDARY_VIOLATION


def test_authority_boundary_violation_is_detected():
    envelope = _envelope()
    envelope["authority_boundary_statement"] = "ChatGPT executes everything."
    envelope["envelope_hash"] = canonical_envelope_hash(envelope)
    assert validate_envelope(envelope, _artifact_map())["status"] == AUTHORITY_BOUNDARY_VIOLATION


def test_input_envelope_and_artifact_map_are_not_mutated():
    envelope = _envelope()
    artifacts = _artifact_map()
    before_envelope = deepcopy(envelope)
    before_artifacts = deepcopy(artifacts)
    validate_envelope(envelope, artifacts)
    assert envelope == before_envelope
    assert artifacts == before_artifacts


def test_output_is_deterministic():
    envelope = _envelope()
    artifacts = _artifact_map()
    assert validate_envelope(envelope, artifacts) == validate_envelope(envelope, artifacts)


def test_no_filesystem_network_subprocess_provider_sidepanel_runtime_calls_are_introduced():
    source = (Path(__file__).resolve().parents[1] / "continuity/envelope_validator.py").read_text()
    forbidden = (
        "open(",
        "Path(",
        "read_text",
        "write_text",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "threading",
        "Timer",
        "fetch",
        "chrome.",
        "provider.call",
        "dispatch_task",
        "approve_task",
    )
    for token in forbidden:
        assert token not in source
