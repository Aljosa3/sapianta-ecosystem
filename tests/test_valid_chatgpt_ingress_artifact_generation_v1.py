from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import (
    ACCEPTED_FOR_GOVERNED_PREVIEW,
    ACCEPTED_FOR_STRUCTURAL_IMPORT,
    STRUCTURAL_CANDIDATE_ONLY,
    create_chatgpt_ingress_artifact,
    evaluate_chatgpt_ingress_acceptance_gate,
    generate_valid_chatgpt_ingress_artifact,
    import_chatgpt_ingress_artifact,
    validate_chatgpt_ingress_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "browser_companion" / "sidepanel.html"
JS = ROOT / "browser_companion" / "sidepanel.js"


def _generated():
    return generate_valid_chatgpt_ingress_artifact(
        human_request="Echo hello world",
        semantic_intent="Minimal governed execution continuity test",
    )


def _manual():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-MANUAL-IMPORT-SESSION",
        human_request="Review manual import path.",
        chatgpt_semantic_output="The request asks for manual import continuity.",
        normalized_intent="REVIEW_MANUAL_IMPORT_PATH",
        expected_artifacts=["manual import report"],
        constraints=["import only", "no execution"],
        forbidden_operations=["execution authorization", "provider dispatch"],
        provenance={"source_conversation_id": "CONV-MANUAL-IMPORT"},
    )


def test_minimal_human_request_generates_valid_artifact():
    artifact = _generated()

    assert artifact["artifact_type"] == "CHATGPT_INGRESS_ARTIFACT_V1"
    assert artifact["human_request"] == "Echo hello world"
    assert artifact["semantic_intent"] == "Minimal governed execution continuity test"
    assert artifact["validation_status"] == STRUCTURAL_CANDIDATE_ONLY
    assert validate_chatgpt_ingress_artifact(artifact)["valid"] is True


def test_generated_artifact_passes_ingress_validation():
    validation = validate_chatgpt_ingress_artifact(_generated())

    assert validation["valid"] is True
    assert validation["artifact_hash"].startswith("sha256:")


def test_generated_artifact_reaches_accepted_for_governed_preview():
    gate = evaluate_chatgpt_ingress_acceptance_gate(_generated())

    assert gate["decision_evidence"]["gate_status"] == ACCEPTED_FOR_GOVERNED_PREVIEW


def test_generated_artifact_import_reaches_structural_import():
    imported = import_chatgpt_ingress_artifact(_generated())

    assert imported["status"] == ACCEPTED_FOR_STRUCTURAL_IMPORT
    assert imported["governance_acceptance_report"]["status"] == ACCEPTED_FOR_STRUCTURAL_IMPORT


def test_replay_identity_deterministic():
    assert _generated()["replay_identity"] == _generated()["replay_identity"]


def test_hash_generation_deterministic():
    first = _generated()["hashes"]
    second = _generated()["hashes"]

    assert first == second
    assert first["artifact_hash"].startswith("sha256:")


def test_provenance_generated():
    provenance = _generated()["provenance"]

    assert provenance["generation_milestone"] == "VALID_CHATGPT_INGRESS_ARTIFACT_GENERATION_V1"
    assert provenance["minimal_operator_input"] is True
    assert provenance["aigol_governance_required"] is True


def test_authority_boundaries_preserved_fail_closed():
    boundary = _generated()["authority_boundary"]

    assert boundary["execution_authority"] is False
    assert boundary["governance_authority"] is False
    assert boundary["semantic_correctness_verified"] is False
    assert boundary["autonomous_continuation_authorized"] is False


def test_execution_authority_remains_false():
    assert _generated()["authority_boundary"]["execution_authority"] is False


def test_governance_authority_remains_false():
    assert _generated()["authority_boundary"]["governance_authority"] is False


def test_semantic_correctness_remains_unverified():
    artifact = _generated()
    assert artifact["authority_boundary"]["semantic_correctness_verified"] is False
    assert artifact["provenance"]["semantic_correctness_verified"] is False


def test_autonomous_continuation_remains_false():
    artifact = _generated()
    assert artifact["authority_boundary"]["autonomous_continuation_authority"] is False
    assert artifact["authority_boundary"]["autonomous_continuation_authorized"] is False


def test_generated_artifact_survives_rerender_continuity():
    source = JS.read_text(encoding="utf-8")

    assert "function generatedChatgptIngressArtifact" in source
    assert "renderChatgptIngressPreview(chatgptIngressPreviewImport(artifact));" in source
    assert "artifactInput.value = artifactJson(artifact);" in source


def test_manual_import_path_still_works():
    imported = import_chatgpt_ingress_artifact(_manual())

    assert imported["status"] == ACCEPTED_FOR_STRUCTURAL_IMPORT


def test_invalid_generated_artifacts_still_fail_closed():
    artifact = deepcopy(_generated())
    artifact["authority_boundary"]["execution_authority"] = True

    validation = validate_chatgpt_ingress_artifact(artifact)
    gate = evaluate_chatgpt_ingress_acceptance_gate(artifact)

    assert validation["valid"] is False
    assert gate["decision_evidence"]["gate_status"] != ACCEPTED_FOR_GOVERNED_PREVIEW


def test_no_execution_triggered_during_generation():
    source = JS.read_text(encoding="utf-8")
    generator_start = source.index("function generatedChatgptIngressArtifact")
    generator_end = source.index("function legacyChatgptIngressPreviewArtifact", generator_start)
    generator_source = source[generator_start:generator_end]

    assert "sendNativeMessage" not in generator_source
    assert "chrome.runtime.sendMessage" not in generator_source
    assert "executeControlledHandoff" not in generator_source


def test_no_native_messaging_call_triggered():
    source = JS.read_text(encoding="utf-8")
    handler_start = source.index("function generateChatgptIngressArtifactFromSidepanel")
    handler_end = source.index("function rejectedChatgptIngressPreview", handler_start)
    handler_source = source[handler_start:handler_end]

    assert "RUN_NATIVE_BRIDGE" not in handler_source
    assert "sendNativeMessage" not in handler_source


def test_no_provider_invocation_triggered():
    module = Path("agol_bridge/chatgpt_ingress/chatgpt_ingress_artifact.py").read_text(encoding="utf-8")

    assert "run_bounded_codex_cli_task" not in module
    assert "subprocess" not in module
    assert "handle_native_message" not in module


def test_cockpit_adds_generation_controls_without_removing_manual_import():
    html = HTML.read_text(encoding="utf-8")

    assert 'id="generate-chatgpt-ingress-artifact"' in html
    assert 'id="chatgpt-ingress-semantic-intent"' in html
    assert 'id="chatgpt-ingress-artifact-json"' in html
    assert 'id="preview-chatgpt-ingress-import-only"' in html
