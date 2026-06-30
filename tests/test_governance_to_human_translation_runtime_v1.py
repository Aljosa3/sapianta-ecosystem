"""Tests for GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.governance_to_human_translation_runtime import (
    GOVERNANCE_TO_HUMAN,
    MATERIAL_AMBIGUITY,
    NO_AMBIGUITY,
    reconstruct_governance_to_human_translation_replay,
    translate_governance_to_human,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.universal_translation_artifact_schema import translation_artifact_hash


CREATED_AT = "2026-06-25T00:00:00Z"


def _governance_state() -> dict:
    return {
        "workflow": "GOVERNED_DEVELOPMENT_WORKFLOW",
        "workflow_state": "WAITING_FOR_APPROVAL",
        "intent_family": "GOVERNANCE_CREATE_INTENT",
        "decision": "PROPOSAL_CREATED",
        "approval_required": True,
    }


def _replay_evidence() -> dict:
    return {
        "replay_reference": "/tmp/aigol/replay/governed-development-001",
        "replay_status": "RECORDED",
    }


def _proposal_state() -> dict:
    return {
        "proposal_id": "proposal-001",
        "artifact_identifier": "ACLI_OPERATOR_GUIDE_V1",
        "proposal_hash": "sha256:proposal",
        "target_paths": ["docs/governance/ACLI_OPERATOR_GUIDE_V1.md"],
    }


def _approval_state() -> dict:
    return {
        "approval_id": "approval-001",
        "approval_status": "PENDING_APPROVAL",
    }


def test_translates_governance_state_to_human_readable_universal_artifact(tmp_path) -> None:
    result = translate_governance_to_human(
        translation_request_id="GTH-001",
        governance_state=_governance_state(),
        replay_evidence=_replay_evidence(),
        proposal_state=_proposal_state(),
        approval_state=_approval_state(),
        worker_results={"execution_status": "NOT_EXECUTED"},
        validation_results={"validation_status": "PASSED"},
        err_evidence={"err_id": "ERR-001", "err_status": "RECORDED"},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )

    artifact = result["translation_artifact"]
    payload = artifact["human_readable_payload"]

    assert result["translation_status"] == "TRANSLATED"
    assert artifact["source_direction"] == GOVERNANCE_TO_HUMAN
    assert artifact["translated_governance_payload"] == {}
    assert artifact["confidence"] == "GOVERNANCE_ONLY"
    assert payload["approval_explanation"] == "Approval state is PENDING_APPROVAL."
    assert payload["worker_execution_status"] == "No worker execution occurred."
    assert payload["validation_summary"] == "Validation passed."
    assert payload["err_summary"] == "ERR evidence ERR-001 has status RECORDED."
    assert "ACLI_OPERATOR_GUIDE_V1" in payload["proposal_summary"]
    assert "GOVERNANCE STATE EXPLANATION" in payload["rendered_explanation"]
    assert artifact["provider_metadata"]["provider_used"] is False
    assert artifact["authority_flags"]["authority_granted"] is False
    assert result["provider_invoked"] is False
    assert result["workflow_executed"] is False
    assert result["governance_mutated"] is False
    assert result["approval_granted"] is False
    assert result["uhcl_wrapper_wiring"]["uhcl_consumed"] is True
    assert result["uhcl_wrapper_wiring"]["legacy_contract_preserved"] is True


def test_authoritative_references_preserve_source_state_hashes(tmp_path) -> None:
    governance = _governance_state()
    replay = _replay_evidence()
    proposal = _proposal_state()
    result = translate_governance_to_human(
        translation_request_id="GTH-002",
        governance_state=governance,
        replay_evidence=replay,
        proposal_state=proposal,
        approval_state=_approval_state(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )

    references = result["human_readable_payload"]["authoritative_state_references"]

    assert references["governance_state_hash"].startswith("sha256:")
    assert references["replay_evidence_hash"].startswith("sha256:")
    assert references["proposal_state_hash"].startswith("sha256:")
    assert references["replay_reference"] == replay["replay_reference"]
    assert references["proposal_reference"] == proposal["proposal_id"]
    assert references["approval_reference"] == "approval-001"


def test_translation_replay_reconstructs_and_preserves_hash(tmp_path) -> None:
    result = translate_governance_to_human(
        translation_request_id="GTH-003",
        governance_state=_governance_state(),
        replay_evidence=_replay_evidence(),
        proposal_state=_proposal_state(),
        approval_state=_approval_state(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )

    reconstructed = reconstruct_governance_to_human_translation_replay(tmp_path / "translation")

    assert reconstructed["translation_artifact"] == result["translation_artifact"]
    assert reconstructed["artifact_hash"] == translation_artifact_hash(result["translation_artifact"])
    assert reconstructed["uhcl_wrapper_wiring"]["uhcl_consumed"] is True
    assert reconstructed["rendered_explanation"] == result["rendered_explanation"]
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["governance_mutated"] is False


def test_translation_output_is_deterministic_except_replay_location(tmp_path) -> None:
    kwargs = {
        "translation_request_id": "GTH-004",
        "governance_state": _governance_state(),
        "replay_evidence": _replay_evidence(),
        "proposal_state": _proposal_state(),
        "approval_state": _approval_state(),
        "created_at": CREATED_AT,
    }
    first = translate_governance_to_human(replay_dir=tmp_path / "first", **kwargs)
    second = translate_governance_to_human(replay_dir=tmp_path / "second", **kwargs)

    first_artifact = deepcopy(first["translation_artifact"])
    second_artifact = deepcopy(second["translation_artifact"])
    first_artifact.pop("artifact_hash")
    second_artifact.pop("artifact_hash")
    first_artifact.pop("replay_reference")
    second_artifact.pop("replay_reference")

    assert first_artifact == second_artifact
    assert first["human_readable_payload"] == second["human_readable_payload"]


def test_missing_approval_state_is_explained_as_material_ambiguity(tmp_path) -> None:
    result = translate_governance_to_human(
        translation_request_id="GTH-005",
        governance_state=_governance_state(),
        replay_evidence=_replay_evidence(),
        proposal_state=_proposal_state(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )

    artifact = result["translation_artifact"]
    payload = artifact["human_readable_payload"]

    assert artifact["ambiguity_flags"]["ambiguity_status"] == MATERIAL_AMBIGUITY
    assert artifact["ambiguity_flags"]["clarification_required"] is True
    assert "no approval decision" in payload["approval_explanation"]
    assert "Review the missing or unclear governance evidence" in payload["operator_action_required"]


def test_complete_state_has_no_material_ambiguity(tmp_path) -> None:
    result = translate_governance_to_human(
        translation_request_id="GTH-006",
        governance_state=_governance_state(),
        replay_evidence=_replay_evidence(),
        proposal_state=_proposal_state(),
        approval_state=_approval_state(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
    )

    assert result["ambiguity_flags"]["ambiguity_status"] == NO_AMBIGUITY
    assert result["ambiguity_flags"]["clarification_required"] is False


def test_malformed_governance_state_fails_closed_before_replay_write(tmp_path) -> None:
    replay_dir = tmp_path / "translation"

    with pytest.raises(FailClosedRuntimeError, match="governance_state must be a non-empty JSON object"):
        translate_governance_to_human(
            translation_request_id="GTH-007",
            governance_state={},
            replay_evidence=_replay_evidence(),
            created_at=CREATED_AT,
            replay_dir=replay_dir,
        )

    assert not replay_dir.exists()


def test_malformed_optional_state_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="proposal_state must be a JSON object"):
        translate_governance_to_human(
            translation_request_id="GTH-008",
            governance_state=_governance_state(),
            replay_evidence=_replay_evidence(),
            proposal_state=["not", "a", "mapping"],
            created_at=CREATED_AT,
            replay_dir=tmp_path / "translation",
        )


def test_replay_tampering_fails_closed(tmp_path) -> None:
    replay_dir = tmp_path / "translation"
    translate_governance_to_human(
        translation_request_id="GTH-009",
        governance_state=_governance_state(),
        replay_evidence=_replay_evidence(),
        proposal_state=_proposal_state(),
        approval_state=_approval_state(),
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    replay_file = replay_dir / "000_governance_to_human_translation_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["human_readable_payload"]["summary"] = "Tampered."
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_governance_to_human_translation_replay(replay_dir)
