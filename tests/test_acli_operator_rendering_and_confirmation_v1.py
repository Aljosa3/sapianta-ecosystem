"""Tests for G3 ACLI operator rendering and confirmation classification."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.acli_conversational_development_session import (
    record_conversational_development_turn,
    start_conversational_development_session,
)
from aigol.runtime.acli_development_session_lifecycle import create_acli_development_session
from aigol.runtime.acli_operator_rendering_and_confirmation import (
    ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1,
    ACLI_OPERATOR_RENDERING_ARTIFACT_V1,
    ACLI_UHCL_COMMAND_CONSUMPTION_MIGRATION_VERSION,
    classify_operator_confirmation,
    reconstruct_operator_rendering_confirmation_replay,
    render_operator_response,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-29T00:00:00Z"
TURN_AT = "2026-06-29T00:01:00Z"
RENDERED_AT = "2026-06-29T00:02:00Z"


def _governance_checkpoints() -> dict:
    return {
        "semantic_authority_preserved": True,
        "governance_authority_preserved": True,
        "approval_boundary_preserved": True,
        "provider_boundary_preserved": True,
        "worker_boundary_preserved": True,
        "replay_boundary_preserved": True,
        "execution_boundary_preserved": True,
    }


def _lineage(name: str) -> list[dict]:
    return [
        {
            "replay_reference": f"runtime/g3/operator/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _session(tmp_path) -> dict:
    return create_acli_development_session(
        session_id="ACLI-G3-SESSION-RENDER-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-RENDER-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session-render"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]


def _conversation(tmp_path) -> dict:
    return start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-RENDER-000001",
        session_artifact=_session(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )["conversation_artifact"]


def _conversation_with_turn(tmp_path) -> dict:
    conversation = _conversation(tmp_path)
    return record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id="TURN-RENDER-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "draft a safe proposal"}),
        canonical_semantic_artifact_reference="CSA-TURN-RENDER-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-render"}),
        replay_lineage=_lineage("turn"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CONFIRMATION_REQUIRED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PROPOSAL-RENDER-000001",
        confirmation_request_reference="CONFIRM-RENDER-000001",
    )["conversation_artifact"]


def test_renders_safe_fallback_for_empty_conversation(tmp_path) -> None:
    capture = render_operator_response(
        render_id="RENDER-EMPTY-000001",
        conversation_artifact=_conversation(tmp_path),
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "operator",
    )
    artifact = capture["artifact"]

    assert artifact["artifact_type"] == ACLI_OPERATOR_RENDERING_ARTIFACT_V1
    assert artifact["session_id"] == "ACLI-G3-SESSION-RENDER-000001"
    assert artifact["turn_id"] is None
    assert artifact["safe_fallback_rendered"] is True
    assert artifact["required_operator_action"] == "provide first governed development request"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-SESSION-RENDER-000001"
    assert artifact["uhcl_command_migration_version"] == ACLI_UHCL_COMMAND_CONSUMPTION_MIGRATION_VERSION
    assert artifact["uhcl_consumption"]["command_surface"] == "ACLI_OPERATOR_RESPONSE_RENDERING"
    assert artifact["uhcl_consumption"]["acli_role"] == "PRESENTATION_ADAPTER"
    assert artifact["uhcl_consumption"]["uhcl_source_artifact_hash"].startswith("sha256:")
    assert artifact["uhcl_consumption"]["uhcl_render_artifact_hash"].startswith("sha256:")
    assert artifact["uhcl_consumption"]["explanation_generated_by_acli"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False


def test_renders_turn_state_with_csa_summary_and_required_action(tmp_path) -> None:
    conversation = _conversation_with_turn(tmp_path)
    capture = render_operator_response(
        render_id="RENDER-TURN-000001",
        conversation_artifact=conversation,
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "operator",
    )
    artifact = capture["artifact"]

    assert artifact["turn_id"] == "TURN-RENDER-000001"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-TURN-RENDER-000001"
    assert artifact["current_lifecycle_state"] == "PROPOSAL_PENDING"
    assert artifact["required_operator_action"] == "review proposal summary"
    assert "proposal" in artifact["rendered_sections"]
    assert artifact["replay_lineage"] == _lineage("turn")
    assert any(line.startswith("CSA: CSA-TURN-RENDER-000001") for line in artifact["operator_response_lines"])


def test_classifies_confirmation_reject_clarify_modify_continue_and_unknown(tmp_path) -> None:
    conversation = _conversation_with_turn(tmp_path)
    examples = [
        ("approve this proposal", "confirm"),
        ("reject it", "reject"),
        ("please clarify why", "clarify"),
        ("modify the scope", "modify"),
        ("continue", "continue"),
        ("hmm maybe", "unknown"),
    ]

    for index, (text, expected) in enumerate(examples):
        capture = classify_operator_confirmation(
            classification_id=f"CLASSIFY-{index:06d}",
            conversation_artifact=conversation,
            operator_input=text,
            classified_at=RENDERED_AT,
            replay_dir=tmp_path / f"operator_{index}",
        )
        artifact = capture["artifact"]
        assert artifact["artifact_type"] == ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1
        assert artifact["confirmation_classification"] == expected
        assert artifact["uhcl_command_migration_version"] == ACLI_UHCL_COMMAND_CONSUMPTION_MIGRATION_VERSION
        assert artifact["uhcl_consumption"]["command_surface"] == "ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION"
        assert artifact["uhcl_consumption"]["acli_role"] == "PRESENTATION_ADAPTER"
        assert artifact["uhcl_consumption"]["uhcl_source_artifact_hash"].startswith("sha256:")
        assert artifact["uhcl_consumption"]["uhcl_render_artifact_hash"].startswith("sha256:")
        assert artifact["uhcl_consumption"]["confirmation_logic_performed_by_acli"] is False
        if expected == "unknown":
            assert artifact["canonical_uhcl_response_class"] is None
            assert artifact["uhcl_consumption"]["uhcl_response_capture_status"] == (
                "COMPATIBILITY_UNKNOWN_INPUT_FAILED_CLOSED"
            )
        else:
            assert artifact["canonical_uhcl_response_class"] in artifact["canonical_uhcl_response_class_set"]
            assert artifact["uhcl_consumption"]["uhcl_response_capture_status"] == "CANONICAL_RESPONSE_CAPTURED"
            assert artifact["uhcl_consumption"]["uhcl_response_artifact_hash"].startswith("sha256:")
        assert artifact["confirmation_evidence_only"] is True
        assert artifact["approval_created"] is False
        assert artifact["authorization_created"] is False
        assert artifact["repository_mutated"] is False


def test_reconstructs_rendering_and_confirmation_replay(tmp_path) -> None:
    conversation = _conversation_with_turn(tmp_path)
    render_operator_response(
        render_id="RENDER-RECONSTRUCT-000001",
        conversation_artifact=conversation,
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "operator",
    )
    classify_operator_confirmation(
        classification_id="CLASSIFY-RECONSTRUCT-000001",
        conversation_artifact=conversation,
        operator_input="continue",
        classified_at=RENDERED_AT,
        replay_dir=tmp_path / "operator",
    )
    reconstructed = reconstruct_operator_rendering_confirmation_replay(tmp_path / "operator")

    assert reconstructed["render_count"] == 1
    assert reconstructed["classification_count"] == 1
    assert reconstructed["artifact_count"] == 2
    assert reconstructed["confirmation_classifications"] == ["continue"]
    assert reconstructed["uhcl_consumption_migrated"] is True
    assert len(reconstructed["uhcl_source_artifact_hashes"]) == 2
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False


def test_rendering_replay_tamper_fails_closed(tmp_path) -> None:
    render_operator_response(
        render_id="RENDER-TAMPER-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "operator",
    )
    path = tmp_path / "operator" / "000_acli_operator_response_rendered.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_operator_rendering_confirmation_replay(tmp_path / "operator")


def test_runtime_has_no_provider_worker_product_deployment_or_mutation_surfaces() -> None:
    import aigol.runtime.acli_operator_rendering_and_confirmation as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "write_text(" not in source
