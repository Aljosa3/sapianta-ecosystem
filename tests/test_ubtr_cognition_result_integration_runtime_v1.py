"""Tests for UBTR cognition result integration runtime."""

from __future__ import annotations

import pytest

from aigol.runtime.canonical_semantic_artifact_runtime import create_canonical_semantic_artifact_from_translation
from aigol.runtime.human_to_governance_translation_runtime import translate_human_to_governance
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.ubtr_cognition_result_integration_runtime import (
    INTEGRATION_COMPLETED,
    integrate_ocs_cognition_result_into_canonical_semantic_artifact,
    reconstruct_ubtr_cognition_result_integration_replay,
)
from aigol.runtime.ubtr_ocs_cognition_handoff_runtime import run_ubtr_ocs_cognition_handoff
from aigol.runtime.ubtr_semantic_cognition_orchestration_runtime import orchestrate_ubtr_semantic_cognition


CREATED_AT = "2026-06-27T00:00:00Z"


def _prior_semantic_and_handoff(tmp_path, human_request: str) -> tuple[dict, dict]:
    translation = translate_human_to_governance(
        translation_request_id="TRANSLATION-001",
        human_request=human_request,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "translation",
        session_context={"canonical_chain_id": "CHAIN-001", "prompt_id": "PROMPT-001"},
        available_workflows=["GOVERNED_DEVELOPMENT_WORKFLOW"],
    )
    semantic = create_canonical_semantic_artifact_from_translation(
        semantic_artifact_id="SEMANTIC-001",
        translation_artifact=translation["translation_artifact"],
        conversation_id="CHAIN-001",
        workflow_id=None,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "semantic",
    )
    orchestration = orchestrate_ubtr_semantic_cognition(
        orchestration_id="UBTR-ORCH-001",
        canonical_semantic_artifact=semantic["semantic_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "orchestration",
    )
    handoff = run_ubtr_ocs_cognition_handoff(
        handoff_id="UBTR-OCS-HANDOFF-001",
        ubtr_orchestration_artifact=orchestration["orchestration_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )
    return semantic["semantic_artifact"], handoff["handoff_artifact"]


def test_ocs_cognition_result_produces_integrated_canonical_semantic_artifact(tmp_path) -> None:
    prior, handoff = _prior_semantic_and_handoff(
        tmp_path,
        "Create a governance artifact for the new runtime",
    )

    result = integrate_ocs_cognition_result_into_canonical_semantic_artifact(
        integration_id="UBTR-COGNITION-INTEGRATION-001",
        prior_canonical_semantic_artifact=prior,
        ubtr_ocs_cognition_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration",
    )

    integrated = result["integrated_canonical_semantic_artifact"]

    assert result["integration_status"] == INTEGRATION_COMPLETED
    assert result["prior_canonical_semantic_artifact_hash"] == prior["artifact_hash"]
    assert result["ubtr_ocs_cognition_handoff_hash"] == handoff["artifact_hash"]
    assert result["ocs_cognition_hash"] == handoff["ocs_cognition_hash"]
    assert result["integrated_canonical_semantic_artifact_hash"].startswith("sha256:")
    assert integrated["artifact_type"] == "CANONICAL_SEMANTIC_ARTIFACT_V1"
    assert integrated["replay_identity"]["prior_semantic_artifact_hash"] == prior["artifact_hash"]
    assert integrated["cognition_result_lineage"]["ocs_cognition_hash"] == handoff["ocs_cognition_hash"]
    assert integrated["provider_projection"]["provider_selection_owner"] == "OCS"
    assert integrated["provider_projection"]["provider_invoked"] is False
    assert integrated["authority_flags"]["semantic_authority"] is True
    assert integrated["authority_flags"]["execution_authority"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["execution_authorized"] is False
    assert result["authority_granted"] is False

    reconstructed = reconstruct_ubtr_cognition_result_integration_replay(tmp_path / "integration")
    assert reconstructed["integration_status"] == INTEGRATION_COMPLETED
    assert reconstructed["integrated_canonical_semantic_artifact_hash"] == integrated["artifact_hash"]


def test_cognition_result_integration_fails_closed_on_incomplete_handoff(tmp_path) -> None:
    prior, handoff = _prior_semantic_and_handoff(
        tmp_path,
        "Create a governance artifact for the new runtime",
    )
    handoff["handoff_status"] = "FAILED_CLOSED"
    handoff["artifact_hash"] = "sha256:invalid"

    result = integrate_ocs_cognition_result_into_canonical_semantic_artifact(
        integration_id="UBTR-COGNITION-INTEGRATION-002",
        prior_canonical_semantic_artifact=prior,
        ubtr_ocs_cognition_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration",
    )

    assert result["fail_closed"] is True
    assert result["integrated_canonical_semantic_artifact_hash"] is None
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["execution_authorized"] is False


def test_cognition_result_integration_replay_tampering_fails_closed(tmp_path) -> None:
    prior, handoff = _prior_semantic_and_handoff(
        tmp_path,
        "Create a governance artifact for the new runtime",
    )
    integrate_ocs_cognition_result_into_canonical_semantic_artifact(
        integration_id="UBTR-COGNITION-INTEGRATION-003",
        prior_canonical_semantic_artifact=prior,
        ubtr_ocs_cognition_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration",
    )
    replay_file = tmp_path / "integration" / "000_ubtr_cognition_result_integrated.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["execution_authorized"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_ubtr_cognition_result_integration_replay(tmp_path / "integration")
