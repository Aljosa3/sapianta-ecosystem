from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.runtime.canonical_governed_development_condensation_replay import (
    CANONICAL_CONDENSATION_REPLAY_STEPS,
    reconstruct_canonical_condensation_phase1_replay,
    record_canonical_condensation_phase1_replay,
)
from aigol.runtime.canonical_governed_development_condensation_runtime import (
    G31_CODEX_SYNTHESIS_PREFIX,
    create_canonical_condensation_proposal,
)
from aigol.runtime.canonical_governed_development_condensation_validation_runtime import (
    validate_canonical_condensation_proposal,
    validate_canonical_condensation_validation_result,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


REPRESENTATIONS = {
    "requested_capability": "condense",
    "user_visible_outcome": "bounded task",
    "allowed_operations": "read source",
    "prohibited_operations": "no mutation",
    "architectural_placement": "pre-G31",
    "acceptance_conditions": "all mapped",
    "testing_validation_requirements": "deterministic",
    "explicit_exclusions": "no execution",
    "safety_governance_constraints": "fail closed",
}


def _proposal(
    *,
    body: str | None = None,
    clarification_complete: bool = True,
    clarification_resolved: bool = True,
    no_clarification_required: bool = False,
    unresolved_ambiguities: tuple[str, ...] = (),
    proposal_method: str = "DETERMINISTIC_RULES",
):
    commitments = {
        field: value
        if field
        in {
            "requested_capability",
            "user_visible_outcome",
            "architectural_placement",
        }
        else [value]
        for field, value in REPRESENTATIONS.items()
    }
    requirements = [
        {
            "requirement_id": f"REQ-{index:02d}",
            "requirement_type": field,
            "source_text": f"source requirement for {value}",
        }
        for index, (field, value) in enumerate(REPRESENTATIONS.items(), start=1)
    ]
    mappings = [
        {
            "requirement_id": f"REQ-{index:02d}",
            "target_field": field,
            "exact_condensed_representation": value,
        }
        for index, (field, value) in enumerate(REPRESENTATIONS.items(), start=1)
    ]
    selected_body = body or (
        "runtime validation; "
        + "; ".join(REPRESENTATIONS.values())
    )
    return create_canonical_condensation_proposal(
        original_request_id="REQUEST-35-10",
        original_request="Implement standalone canonical condensation Phase 1.",
        clarification_evidence=[] if no_clarification_required else [
            {
                "question_id": "QUESTION-1",
                "question": "May the capability activate G31?",
                "answer_id": "ANSWER-1",
                "answer": "No; Phase 1 must remain standalone.",
                "resolved": clarification_resolved,
            }
        ],
        clarification_complete=clarification_complete,
        completed_objective_id="OBJECTIVE-35-10",
        completed_objective=(
            "Create proposal, validation, and immutable replay without integration."
        ),
        project_id="SAPIANTA",
        workspace_id="/workspace/sapianta",
        session_id="SESSION-35-10",
        invocation_id="INVOCATION-35-10",
        chain_id="CHAIN-35-10",
        semantic_commitments=commitments,
        source_requirements=requirements,
        requirement_mappings=mappings,
        proposed_synthesis_body=selected_body,
        unresolved_ambiguities=unresolved_ambiguities,
        proposal_method=proposal_method,
    )


def _rehash_proposal(proposal):
    candidate = deepcopy(proposal)
    candidate.pop("condensation_id", None)
    candidate.pop("condensation_hash", None)
    candidate_hash = replay_hash(candidate)
    candidate["condensation_id"] = (
        "CANONICAL-CONDENSATION-"
        f"{candidate_hash.removeprefix('sha256:')[:24]}"
    )
    candidate["condensation_hash"] = candidate_hash
    return candidate


def _rehash_validation(result):
    candidate = deepcopy(result)
    candidate.pop("validation_id", None)
    candidate.pop("validation_hash", None)
    candidate_hash = replay_hash(candidate)
    candidate["validation_id"] = (
        "CANONICAL-CONDENSATION-VALIDATION-"
        f"{candidate_hash.removeprefix('sha256:')[:24]}"
    )
    candidate["validation_hash"] = candidate_hash
    return candidate


def _rewrite_wrapper(path: Path, mutate):
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    mutate(wrapper)
    wrapper.pop("replay_hash", None)
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(
        json.dumps(wrapper, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def test_proposal_is_deterministic_exact_and_non_authoritative():
    first = _proposal()
    second = _proposal()

    assert first == second
    assert first["proposed_projection"] == (
        G31_CODEX_SYNTHESIS_PREFIX + first["proposed_synthesis_body"]
    )
    assert first["projection_prefix_code_point_count"] == 20
    assert first["proposed_projection_code_point_count"] <= 240
    assert first["approval_required"] is True
    assert first["ready_for_human_review"] is False
    assert first["ready_for_g31"] is False
    assert first["authorization_created"] is False
    assert first["worker_invoked"] is False
    assert first["provider_invoked"] is False
    assert first["execution_gate_reached"] is False


def test_proposal_counts_unicode_code_points_and_utf8_bytes_separately():
    body = "runtime validation; " + "; ".join(REPRESENTATIONS.values()) + "; ž"
    proposal = _proposal(body=body)

    assert proposal["proposed_synthesis_body_code_point_count"] == len(body)
    assert proposal["proposed_synthesis_body_utf8_byte_count"] == len(
        body.encode("utf-8")
    )
    assert (
        proposal["proposed_synthesis_body_utf8_byte_count"]
        > proposal["proposed_synthesis_body_code_point_count"]
    )
    assert validate_canonical_condensation_proposal(proposal)[
        "validation_status"
    ] == "PASS"


def test_proposal_rejects_non_utf8_encodable_content():
    with pytest.raises(FailClosedRuntimeError):
        _proposal(body="invalid-surrogate-\ud800")


def test_proposal_rejects_duplicate_requirement_mappings():
    proposal = _proposal()
    mappings = [
        {
            "requirement_id": item["requirement_id"],
            "target_field": item["target_semantic_field"],
            "exact_condensed_representation": item[
                "exact_condensed_representation"
            ],
        }
        for item in proposal["requirement_map"]
    ]
    mappings.append(deepcopy(mappings[0]))

    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_proposal(
            original_request_id="REQUEST-35-10",
            original_request="Request",
            clarification_evidence=[],
            clarification_complete=True,
            completed_objective_id="OBJECTIVE-35-10",
            completed_objective="Objective",
            project_id="SAPIANTA",
            workspace_id="/workspace/sapianta",
            session_id="SESSION-35-10",
            invocation_id=None,
            chain_id=None,
            semantic_commitments=proposal["semantic_commitments"],
            source_requirements=[
                {
                    "requirement_id": item["requirement_id"],
                    "requirement_type": item["requirement_type"],
                    "source_text": item["source_text"],
                }
                for item in proposal["source_requirements"]
            ],
            requirement_mappings=mappings,
            proposed_synthesis_body=proposal["proposed_synthesis_body"],
        )


def test_explicit_no_clarification_resolution_is_deterministic_and_valid():
    proposal = _proposal(no_clarification_required=True)
    resolution = proposal["source_lineage"]["clarification_resolution"]

    assert resolution["resolution_status"] == (
        "COMPLETE_NO_CLARIFICATION_REQUIRED"
    )
    assert resolution["clarification_evidence_count"] == 0
    assert validate_canonical_condensation_proposal(proposal)[
        "validation_status"
    ] == "PASS"


def test_validator_pass_is_deterministic_and_only_enables_later_review():
    proposal = _proposal()
    expected_context = {
        "project_id": "SAPIANTA",
        "workspace_id": "/workspace/sapianta",
        "session_id": "SESSION-35-10",
        "invocation_id": "INVOCATION-35-10",
        "chain_id": "CHAIN-35-10",
    }

    first = validate_canonical_condensation_proposal(
        proposal,
        expected_context=expected_context,
    )
    second = validate_canonical_condensation_proposal(
        proposal,
        expected_context=expected_context,
    )

    assert first == second
    assert first["validation_status"] == "PASS"
    assert first["failure_codes"] == []
    assert first["fail_closed"] is False
    assert first["ready_for_human_review"] is True
    assert first["ready_for_g31"] is False
    assert first["approval_created"] is False
    assert first["execution_authorized"] is False
    assert first["worker_invoked"] is False
    assert first["provider_invoked"] is False
    assert validate_canonical_condensation_validation_result(
        first,
        proposal=proposal,
    ) == first


@pytest.mark.parametrize(
    ("proposal", "failure_code"),
    [
        (
            _proposal(
                clarification_complete=False,
                clarification_resolved=False,
            ),
            "INCOMPLETE_CLARIFICATION",
        ),
        (
            _proposal(unresolved_ambiguities=("Target remains ambiguous.",)),
            "AMBIGUOUS_CONDENSED_OBJECTIVE",
        ),
        (
            _proposal(proposal_method="UNSUPPORTED_MODEL_GENERATION"),
            "UNSUPPORTED_PROPOSAL_METHOD",
        ),
        (
            _proposal(
                body=(
                    "runtime validation; "
                    + "; ".join(REPRESENTATIONS.values())
                    + "; "
                    + ("x" * 240)
                )
            ),
            "EXCESSIVE_CANONICAL_REQUEST_LENGTH",
        ),
        (
            _proposal(
                body=(
                    " runtime validation; "
                    + "; ".join(REPRESENTATIONS.values())
                )
            ),
            "INVALID_SCHEMA",
        ),
    ],
)
def test_validator_fails_closed_for_contract_violations(proposal, failure_code):
    result = validate_canonical_condensation_proposal(proposal)

    assert result["validation_status"] == "FAIL"
    assert result["fail_closed"] is True
    assert failure_code in result["failure_codes"]
    assert result["ready_for_human_review"] is False
    assert result["ready_for_g31"] is False
    assert result["execution_authorized"] is False


def test_validator_fails_closed_for_missing_requirement_mapping():
    proposal = deepcopy(_proposal())
    proposal["requirement_map"].pop()
    proposal = _rehash_proposal(proposal)

    result = validate_canonical_condensation_proposal(proposal)

    assert "MATERIAL_REQUIREMENT_UNMAPPED" in result["failure_codes"]
    assert result["validation_status"] == "FAIL"


def test_validator_fails_closed_for_material_requirement_loss():
    proposal = deepcopy(_proposal())
    proposal["requirement_map"][0]["exact_condensed_representation"] = "other"
    proposal["requirement_map"][0][
        "exact_condensed_representation_sha256"
    ] = "not-the-hash"
    proposal = _rehash_proposal(proposal)

    result = validate_canonical_condensation_proposal(proposal)

    assert "MATERIAL_REQUIREMENT_LOSS" in result["failure_codes"]
    assert result["ready_for_human_review"] is False


def test_validator_fails_closed_for_source_context_mismatch():
    result = validate_canonical_condensation_proposal(
        _proposal(),
        expected_context={"session_id": "OTHER-SESSION"},
    )

    assert result["failure_codes"] == ["SOURCE_HASH_MISMATCH"]
    assert result["validation_status"] == "FAIL"


def test_validator_classifies_missing_nested_source_as_missing_lineage():
    proposal = deepcopy(_proposal())
    proposal["source_lineage"]["original_request"].pop("original_request_id")
    source_seed = deepcopy(proposal["source_lineage"])
    source_seed.pop("source_bundle_hash")
    proposal["source_lineage"]["source_bundle_hash"] = replay_hash(source_seed)
    proposal = _rehash_proposal(proposal)

    result = validate_canonical_condensation_proposal(proposal)

    assert "MISSING_SOURCE_LINEAGE" in result["failure_codes"]
    assert result["validation_status"] == "FAIL"


def test_validator_records_proposal_identity_tampering_as_failure():
    proposal = deepcopy(_proposal())
    proposal["condensation_hash"] = "sha256:" + ("0" * 64)

    result = validate_canonical_condensation_proposal(proposal)

    assert "REPLAY_IDENTITY_MISMATCH" in result["failure_codes"]
    assert result["validation_status"] == "FAIL"


def test_validation_artifact_reconstruction_rejects_self_consistent_forgery():
    proposal = _proposal()
    validation = validate_canonical_condensation_proposal(proposal)
    validation["ready_for_g31"] = True
    validation = _rehash_validation(validation)

    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_validation_result(
            validation,
            proposal=proposal,
        )


@pytest.mark.parametrize("validation_status", ["PASS", "FAIL"])
def test_replay_records_and_reconstructs_pass_and_fail_closed_results(
    tmp_path,
    validation_status,
):
    proposal = (
        _proposal()
        if validation_status == "PASS"
        else _proposal(unresolved_ambiguities=("Unresolved target.",))
    )
    validation = validate_canonical_condensation_proposal(proposal)
    replay_dir = tmp_path / validation_status.lower()

    capture = record_canonical_condensation_phase1_replay(
        proposal=proposal,
        validation_result=validation,
        recorded_at="2026-07-28T12:00:00Z",
        replay_dir=replay_dir,
    )
    reconstructed = reconstruct_canonical_condensation_phase1_replay(replay_dir)

    assert capture["validation_status"] == validation_status
    assert reconstructed["validation_status"] == validation_status
    assert reconstructed["proposal"] == proposal
    assert reconstructed["validation_result"] == validation
    assert len(capture["replay_files"]) == len(
        CANONICAL_CONDENSATION_REPLAY_STEPS
    )
    assert reconstructed["approval_created"] is False
    assert reconstructed["g31_input_binding_created"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_gate_reached"] is False


def test_replay_is_append_only(tmp_path):
    proposal = _proposal()
    validation = validate_canonical_condensation_proposal(proposal)
    replay_dir = tmp_path / "replay"
    arguments = {
        "proposal": proposal,
        "validation_result": validation,
        "recorded_at": "2026-07-28T12:00:00Z",
        "replay_dir": replay_dir,
    }
    record_canonical_condensation_phase1_replay(**arguments)

    with pytest.raises(FailClosedRuntimeError):
        record_canonical_condensation_phase1_replay(**arguments)


def test_replay_reconstruction_rejects_wrapper_tampering(tmp_path):
    proposal = _proposal()
    validation = validate_canonical_condensation_proposal(proposal)
    replay_dir = tmp_path / "replay"
    record_canonical_condensation_phase1_replay(
        proposal=proposal,
        validation_result=validation,
        recorded_at="2026-07-28T12:00:00Z",
        replay_dir=replay_dir,
    )
    validation_path = replay_dir / (
        "002_condensation_validation_recorded.json"
    )
    wrapper = json.loads(validation_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["validation_status"] = "FAIL"
    validation_path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_canonical_condensation_phase1_replay(replay_dir)


def test_replay_reconstruction_rejects_cross_record_substitution(tmp_path):
    proposal = _proposal()
    validation = validate_canonical_condensation_proposal(proposal)
    replay_dir = tmp_path / "replay"
    record_canonical_condensation_phase1_replay(
        proposal=proposal,
        validation_result=validation,
        recorded_at="2026-07-28T12:00:00Z",
        replay_dir=replay_dir,
    )
    source_path = replay_dir / "000_condensation_source_lineage_recorded.json"

    def substitute(wrapper):
        wrapper["artifact"]["condensation_id"] = "OTHER"

    _rewrite_wrapper(source_path, substitute)

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_canonical_condensation_phase1_replay(replay_dir)


def test_replay_reconstruction_requires_exact_family(tmp_path):
    proposal = _proposal()
    validation = validate_canonical_condensation_proposal(proposal)
    replay_dir = tmp_path / "replay"
    record_canonical_condensation_phase1_replay(
        proposal=proposal,
        validation_result=validation,
        recorded_at="2026-07-28T12:00:00Z",
        replay_dir=replay_dir,
    )
    (replay_dir / "unexpected").mkdir()

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_canonical_condensation_phase1_replay(replay_dir)


def test_phase1_modules_do_not_import_or_activate_downstream_boundaries():
    runtime_root = Path(__file__).parents[1] / "aigol" / "runtime"
    module_names = (
        "canonical_governed_development_condensation_runtime.py",
        "canonical_governed_development_condensation_validation_runtime.py",
        "canonical_governed_development_condensation_replay.py",
    )
    forbidden_import_fragments = (
        "aigol.runtime.aicli",
        "human_interface",
        "input_binding",
        "authorization_runtime",
        "worker_runtime",
        "provider_runtime",
        "capability_registry",
        "codex_synthesis",
    )

    for module_name in module_names:
        source = (runtime_root / module_name).read_text(encoding="utf-8")
        import_lines = "\n".join(
            line for line in source.splitlines() if line.startswith(("from ", "import "))
        )
        assert not any(
            fragment in import_lines for fragment in forbidden_import_fragments
        )
