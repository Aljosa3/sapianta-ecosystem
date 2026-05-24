import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cognition.semantic_context_state import (
    AMBIGUITY_LOW,
    AMBIGUITY_MODERATE,
    AMBIGUITY_UNKNOWN,
    ARTIFACT_TYPE,
    SEMANTIC_CONTEXT_STABLE,
    UNKNOWN_INSUFFICIENT_EVIDENCE,
    build_semantic_context_state,
    inspect_semantic_context,
    validate_semantic_context_state,
)


def _artifact():
    return generate_ingress_artifact(
        human_request="Preserve semantic context.",
        semantic_intent="Semantic context state proof",
    )


def _stable_artifacts():
    ingress = _artifact()
    chain = build_governed_chain(ingress_artifact=ingress)
    return [
        ingress,
        chain["task_package_preview"],
        chain["human_approval"],
        chain["handoff_preview"],
        chain["dispatch_authorization"],
        chain["continuity_preview"],
    ]


def test_semantic_context_generation_deterministic():
    first = build_semantic_context_state(_stable_artifacts())
    second = build_semantic_context_state(_stable_artifacts())

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["semantic_context_hash"].startswith("sha256:")


def test_semantic_anchors_stable():
    state = build_semantic_context_state(_stable_artifacts())
    anchors = {anchor["anchor_name"]: anchor for anchor in state["semantic_continuity_anchors"]}

    assert anchors["original governance intent"]["value"] == "Preserve semantic context."
    assert anchors["semantic intent"]["value"] == "Semantic context state proof"
    assert anchors["normalized intent"]["value"] != "UNKNOWN"
    assert anchors["replay identity reference"]["replay_visible"] is True
    assert all(anchor["inferred"] is False for anchor in state["semantic_continuity_anchors"])


def test_ambiguity_propagation_deterministic():
    artifacts = _stable_artifacts()
    artifacts[0]["ambiguities"] = ["NO_BLOCKING_AMBIGUITY_DETECTED"]
    artifacts[-1]["ambiguities"] = ["UNRESOLVED_SCOPE"]

    state = build_semantic_context_state(artifacts)

    assert state["ambiguity_state"]["status"] == AMBIGUITY_MODERATE
    assert "UNRESOLVED_SCOPE" in state["ambiguity_state"]["ambiguities"]
    assert state["ambiguity_state"]["resolved_by_context_state"] is False


def test_unknown_handling_works():
    state = build_semantic_context_state()

    assert state["semantic_context_status"] == UNKNOWN_INSUFFICIENT_EVIDENCE
    assert state["ambiguity_state"]["status"] == AMBIGUITY_UNKNOWN
    assert "no semantic artifacts provided" in state["unknowns"]


def test_semantic_boundaries_generated_correctly():
    state = build_semantic_context_state(_stable_artifacts())
    boundary_names = {boundary["boundary_name"] for boundary in state["semantic_boundaries"]}

    assert "authority semantic boundaries" in boundary_names
    assert "execution semantic boundaries" in boundary_names
    assert "governance scope boundaries" in boundary_names
    assert "replay continuity boundaries" in boundary_names
    assert "admissibility semantic boundaries" in boundary_names
    assert all(boundary["descriptive_only"] is True for boundary in state["semantic_boundaries"])


def test_stable_context_has_low_ambiguity():
    state = build_semantic_context_state(_stable_artifacts())

    assert state["semantic_context_status"] == SEMANTIC_CONTEXT_STABLE
    assert state["ambiguity_state"]["status"] == AMBIGUITY_LOW


def test_cli_never_invokes_providers(monkeypatch):
    called = {"execution": False, "provider": False}

    def forbidden_execution(*args, **kwargs):
        called["execution"] = True
        raise AssertionError("execution must not run")

    def forbidden_provider(*args, **kwargs):
        called["provider"] = True
        raise AssertionError("provider must not run")

    import aigol.cli.aigol_cli as cli
    import agol_bridge.providers.codex_cli_provider as provider

    monkeypatch.setattr(cli, "run_execution_handoff", forbidden_execution)
    if hasattr(provider, "run_bounded_codex_cli"):
        monkeypatch.setattr(provider, "run_bounded_codex_cli", forbidden_provider)

    parser = build_parser()
    args = parser.parse_args(["cognition", "semantic-context", "--validate"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False


def test_cli_never_mutates_artifacts():
    artifacts = _stable_artifacts()
    before = json.dumps(artifacts, sort_keys=True)

    build_semantic_context_state(artifacts)

    assert json.dumps(artifacts, sort_keys=True) == before


def test_json_output_parseable_and_stable(tmp_path):
    artifact_path = tmp_path / "artifacts.json"
    output_path = tmp_path / "semantic_context.json"
    artifact_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")

    first = inspect_semantic_context(input_path=artifact_path, output_path=output_path, validate=True)
    second = inspect_semantic_context(input_path=artifact_path, validate=True)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed == first["semantic_context_state"]
    assert first["semantic_context_state"] == second["semantic_context_state"]
    assert first["semantic_context_validation"]["validation_status"] == "VALID"


def test_no_execution_capability_or_hidden_inference_introduced():
    state = build_semantic_context_state(_stable_artifacts())
    validation = validate_semantic_context_state(state)

    assert validation["validation_status"] == "VALID"
    assert state["execution_authority_added"] is False
    assert state["orchestration_authority_added"] is False
    assert state["provider_activation_added"] is False
    assert state["hidden_semantic_inference_added"] is False
    assert state["semantic_reasoning_engine_added"] is False
    assert state["ambiguity_resolution_performed"] is False


def test_cli_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "semantic-context", "--validate"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition semantic-context"
    assert result["semantic_context_validation"]["validation_status"] == "VALID"
    assert "AIGOL COGNITION SEMANTIC CONTEXT" in rendered
    assert "Semantic Context Status" in rendered
    assert "Semantic Continuity Anchors" in rendered
    assert "Semantic Boundaries" in rendered
