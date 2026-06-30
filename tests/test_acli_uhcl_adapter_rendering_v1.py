"""Tests for ACLI UHCL adapter rendering."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.acli_uhcl_adapter_rendering import (
    ACLI_UHCL_HUMAN_RESPONSE_ARTIFACT_V1,
    ACLI_UHCL_RENDER_ARTIFACT_V1,
    capture_uhcl_human_response,
    reconstruct_acli_uhcl_adapter_replay,
    render_uhcl_artifact_for_acli,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash
from aigol.runtime.ubtr_human_communication_model_runtime import (
    LEVEL_STANDARD,
    RECOVERY_GUIDANCE_ARTIFACT_TYPE,
    RESPONSE_CLARIFICATION,
    RESPONSE_CONFIRMATION,
    RESPONSE_CONTINUATION,
    RESPONSE_MODIFICATION,
    RESPONSE_REJECTION,
    SHARED_CONFIRMATION_ARTIFACT_TYPE,
    SOURCE_COMPONENT_GOVERNANCE,
    create_recovery_guidance_model,
    create_shared_confirmation_model,
)


CREATED_AT = "2026-06-30T00:00:00Z"
RENDERED_AT = "2026-06-30T00:01:00Z"
CAPTURED_AT = "2026-06-30T00:02:00Z"


def _lineage(name: str) -> list[dict]:
    return [
        {
            "replay_reference": f"runtime/acli-uhcl/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _shared_confirmation(tmp_path) -> dict:
    return create_shared_confirmation_model(
        confirmation_id="ACLI-UHCL-CONFIRMATION-001",
        source_component=SOURCE_COMPONENT_GOVERNANCE,
        target_human_context="ACLI_OPERATOR",
        communication_level=LEVEL_STANDARD,
        confirmation_prompt="Review the UHCL artifact and choose a response.",
        required_human_action="choose a canonical confirmation response",
        evidence_references=[
            {
                "evidence_reference": "ACLI-UHCL-GOVERNANCE-001",
                "evidence_hash": replay_hash({"governance": "acli-uhcl"}),
                "evidence_role": "GOVERNANCE_SOURCE",
            }
        ],
        source_evidence_bindings={
            "specific_sources": {
                "governance": {
                    "reference": "ACLI-UHCL-GOVERNANCE-001",
                    "hash": replay_hash({"governance": "acli-uhcl"}),
                }
            }
        },
        replay_lineage=_lineage("shared-confirmation"),
        rollback_reference="ROLLBACK-ACLI-UHCL-CONFIRMATION-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "shared_confirmation",
    )["shared_confirmation_artifact"]


def _recovery_guidance(tmp_path) -> dict:
    return create_recovery_guidance_model(
        recovery_id="ACLI-UHCL-RECOVERY-001",
        source_component=SOURCE_COMPONENT_GOVERNANCE,
        target_human_context="ACLI_OPERATOR",
        communication_level=LEVEL_STANDARD,
        blocked_operation="Worker execution cannot continue.",
        cannot_continue_reason="Worker readiness evidence is missing.",
        missing_prerequisites=[
            {
                "prerequisite_id": "WORKER-READINESS-EVIDENCE",
                "description": "Worker readiness evidence must be available.",
                "evidence_reference": "ACLI-UHCL-WORKER-READINESS-001",
                "evidence_hash": replay_hash({"worker": "readiness"}),
            }
        ],
        available_recovery_actions=[
            {
                "action_id": "REQUEST_WORKER_READINESS_EVIDENCE",
                "description": "Ask for worker readiness evidence.",
            }
        ],
        recommended_next_action={
            "action_id": "REQUEST_WORKER_READINESS_EVIDENCE",
            "reason": "The missing worker readiness evidence blocks continuation.",
        },
        evidence_references=[
            {
                "evidence_reference": "ACLI-UHCL-WORKER-READINESS-001",
                "evidence_hash": replay_hash({"worker": "readiness"}),
                "evidence_role": "WORKER_SOURCE",
            }
        ],
        source_evidence_bindings={
            "specific_sources": {
                "governance": {
                    "reference": "ACLI-UHCL-GOVERNANCE-RECOVERY-001",
                    "hash": replay_hash({"governance": "recovery"}),
                }
            }
        },
        replay_lineage=_lineage("recovery-guidance"),
        rollback_reference="ROLLBACK-ACLI-UHCL-RECOVERY-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "recovery_guidance",
    )["recovery_guidance_artifact"]


def test_renders_shared_confirmation_uhcl_artifact_without_platform_semantics(tmp_path) -> None:
    source = _shared_confirmation(tmp_path)

    capture = render_uhcl_artifact_for_acli(
        render_id="ACLI-UHCL-RENDER-001",
        uhcl_artifact=source,
        communication_level=LEVEL_STANDARD,
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "adapter",
    )
    artifact = capture["artifact"]

    assert artifact["artifact_type"] == ACLI_UHCL_RENDER_ARTIFACT_V1
    assert artifact["source_artifact_type"] == SHARED_CONFIRMATION_ARTIFACT_TYPE
    assert artifact["source_artifact_hash"] == source["artifact_hash"]
    assert artifact["terminal_format"] == "PLAIN_TEXT_CARD"
    assert artifact["render_text_hash"].startswith("sha256:")
    assert "confirmation_section" in artifact["rendered_sections"]
    assert artifact["semantic_translation_performed"] is False
    assert artifact["explanation_generated"] is False
    assert artifact["confirmation_logic_performed"] is False
    assert artifact["provider_orchestration_performed"] is False
    assert artifact["worker_orchestration_performed"] is False
    assert artifact["governance_performed"] is False
    assert artifact["replay_logic_performed"] is False
    assert artifact["repository_mutated"] is False


def test_captures_human_responses_as_canonical_confirmation_classes(tmp_path) -> None:
    render = render_uhcl_artifact_for_acli(
        render_id="ACLI-UHCL-RENDER-RESPONSES-001",
        uhcl_artifact=_shared_confirmation(tmp_path),
        communication_level=LEVEL_STANDARD,
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "adapter",
    )["artifact"]
    examples = [
        ("confirm this", RESPONSE_CONFIRMATION),
        ("please clarify", RESPONSE_CLARIFICATION),
        ("modify scope", RESPONSE_MODIFICATION),
        ("reject it", RESPONSE_REJECTION),
        ("continue", RESPONSE_CONTINUATION),
    ]

    for index, (operator_input, expected) in enumerate(examples):
        capture = capture_uhcl_human_response(
            response_id=f"ACLI-UHCL-RESPONSE-{index:03d}",
            rendered_artifact=render,
            operator_input=operator_input,
            captured_at=CAPTURED_AT,
            replay_dir=tmp_path / f"adapter_response_{index}",
        )
        artifact = capture["artifact"]

        assert artifact["artifact_type"] == ACLI_UHCL_HUMAN_RESPONSE_ARTIFACT_V1
        assert artifact["canonical_response_class"] == expected
        assert artifact["confirmation_evidence_only"] is True
        assert artifact["approval_created"] is False
        assert artifact["authorization_created"] is False
        assert artifact["execution_authorized"] is False


def test_reconstructs_acli_uhcl_render_and_response_replay(tmp_path) -> None:
    source = _recovery_guidance(tmp_path)
    render = render_uhcl_artifact_for_acli(
        render_id="ACLI-UHCL-RENDER-REPLAY-001",
        uhcl_artifact=source,
        communication_level=LEVEL_STANDARD,
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "adapter",
    )["artifact"]
    capture_uhcl_human_response(
        response_id="ACLI-UHCL-RESPONSE-REPLAY-001",
        rendered_artifact=render,
        operator_input="continue",
        captured_at=CAPTURED_AT,
        replay_dir=tmp_path / "adapter",
    )

    reconstructed = reconstruct_acli_uhcl_adapter_replay(tmp_path / "adapter")

    assert reconstructed["render_count"] == 1
    assert reconstructed["response_count"] == 1
    assert reconstructed["artifact_count"] == 2
    assert reconstructed["canonical_response_classes"] == [RESPONSE_CONTINUATION]
    assert reconstructed["source_artifact_hashes"] == [source["artifact_hash"]]
    assert reconstructed["semantic_translation_performed"] is False
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["repository_mutated"] is False


def test_rejects_unknown_human_response_without_inventing_semantics(tmp_path) -> None:
    render = render_uhcl_artifact_for_acli(
        render_id="ACLI-UHCL-RENDER-UNKNOWN-001",
        uhcl_artifact=_shared_confirmation(tmp_path),
        communication_level=LEVEL_STANDARD,
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "adapter_unknown",
    )["artifact"]

    with pytest.raises(FailClosedRuntimeError, match="does not map"):
        capture_uhcl_human_response(
            response_id="ACLI-UHCL-RESPONSE-UNKNOWN-001",
            rendered_artifact=render,
            operator_input="maybe later",
            captured_at=CAPTURED_AT,
            replay_dir=tmp_path / "adapter_unknown",
        )


def test_render_replay_tampering_fails_closed(tmp_path) -> None:
    render_uhcl_artifact_for_acli(
        render_id="ACLI-UHCL-RENDER-TAMPER-001",
        uhcl_artifact=_recovery_guidance(tmp_path),
        communication_level=LEVEL_STANDARD,
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "adapter_tamper",
    )
    replay_file = tmp_path / "adapter_tamper" / "000_acli_uhcl_artifact_rendered.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["provider_invoked"] = True
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_acli_uhcl_adapter_replay(tmp_path / "adapter_tamper")


def test_runtime_has_no_platform_execution_or_generation_surfaces() -> None:
    import aigol.runtime.acli_uhcl_adapter_rendering as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "semantic_translation(" not in source
    assert "generate_explanation(" not in source
