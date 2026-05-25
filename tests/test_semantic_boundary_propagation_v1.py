import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cognition.semantic_boundary_propagation import (
    ARTIFACT_TYPE,
    BOUNDARY_TYPES,
    PROPAGATION_DRIFT_RISK,
    STABLE_WITH_WARNINGS,
    UNKNOWN_STATUS,
    build_semantic_boundary_propagation,
    inspect_semantic_boundaries,
    validate_semantic_boundary_propagation,
)


def _artifact():
    return generate_ingress_artifact(
        human_request="Propagate semantic boundaries.",
        semantic_intent="Semantic boundary propagation proof",
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


def test_propagation_generation_deterministic():
    first = build_semantic_boundary_propagation(_stable_artifacts())
    second = build_semantic_boundary_propagation(_stable_artifacts())

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["propagation_hash"].startswith("sha256:")


def test_boundary_propagation_paths_stable():
    propagation = build_semantic_boundary_propagation(_stable_artifacts())
    paths = {path["path_name"]: path for path in propagation["propagation_paths"]}

    assert "semantic_context_to_relationship_index" in paths
    assert "relationship_index_to_lifecycle_visibility" in paths
    assert "authority_boundary_to_execution_boundary" in paths
    assert all(path["inferred"] is False for path in paths.values())
    assert all(path["executable_semantic_flow"] is False for path in paths.values())


def test_unknown_propagation_handling_works():
    propagation = build_semantic_boundary_propagation()

    assert propagation["propagation_status"] == UNKNOWN_STATUS
    assert "no semantic boundary artifacts provided" in propagation["unknowns"]
    assert all(boundary["known"] is False for boundary in propagation["semantic_boundaries"])


def test_drift_risks_detected_correctly():
    artifacts = _stable_artifacts()
    artifacts[0]["execution_authority"] = True

    propagation = build_semantic_boundary_propagation(artifacts)

    assert propagation["propagation_status"] == PROPAGATION_DRIFT_RISK
    assert propagation["stability_assessment"]["hidden_semantic_expansion_detected"] is True
    assert propagation["stability_assessment"]["drift_findings"]


def test_explicit_boundaries_preserved_correctly():
    propagation = build_semantic_boundary_propagation(_stable_artifacts())
    boundaries = {boundary["boundary_type"]: boundary for boundary in propagation["semantic_boundaries"]}

    assert set(BOUNDARY_TYPES) == set(boundaries)
    assert boundaries["authority_semantic_boundary"]["known"] is True
    assert boundaries["execution_semantic_boundary"]["known"] is True
    assert boundaries["governance_scope_boundary"]["known"] is True
    assert all(boundary["inferred"] is False for boundary in boundaries.values())
    assert all(boundary["runtime_enforcement_added"] is False for boundary in boundaries.values())


def test_stable_chain_with_missing_ambiguity_is_stable_with_warnings():
    propagation = build_semantic_boundary_propagation(_stable_artifacts())

    assert propagation["propagation_status"] == STABLE_WITH_WARNINGS
    assert "ambiguity_boundary" in propagation["unknowns"]


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
    args = parser.parse_args(["cognition", "semantic-boundaries", "--validate"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False


def test_cli_never_mutates_artifacts():
    artifacts = _stable_artifacts()
    before = json.dumps(artifacts, sort_keys=True)

    build_semantic_boundary_propagation(artifacts)

    assert json.dumps(artifacts, sort_keys=True) == before


def test_json_output_parseable_and_stable(tmp_path):
    artifact_path = tmp_path / "artifacts.json"
    output_path = tmp_path / "boundaries.json"
    artifact_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")

    first = inspect_semantic_boundaries(input_path=artifact_path, output_path=output_path, validate=True)
    second = inspect_semantic_boundaries(input_path=artifact_path, validate=True)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed == first["semantic_boundary_propagation"]
    assert first["semantic_boundary_propagation"] == second["semantic_boundary_propagation"]
    assert first["semantic_boundary_validation"]["validation_status"] == "VALID"


def test_no_execution_capability_or_semantic_reasoning_introduced():
    propagation = build_semantic_boundary_propagation(_stable_artifacts())
    validation = validate_semantic_boundary_propagation(propagation)

    assert validation["validation_status"] == "VALID"
    assert propagation["execution_authority_added"] is False
    assert propagation["provider_activation_added"] is False
    assert propagation["semantic_reasoning_added"] is False
    assert propagation["hidden_inference_added"] is False
    assert propagation["executable_semantic_graphs_added"] is False


def test_cli_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "semantic-boundaries", "--validate"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition semantic-boundaries"
    assert result["semantic_boundary_validation"]["validation_status"] == "VALID"
    assert "AIGOL COGNITION SEMANTIC BOUNDARIES" in rendered
    assert "Propagation Status" in rendered
    assert "Semantic Boundaries" in rendered
    assert "Stability Assessment" in rendered
