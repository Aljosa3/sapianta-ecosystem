import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cognition.semantic_relationship_index import (
    ARTIFACT_TYPE,
    RELATIONSHIP_CATEGORIES,
    RELATIONSHIP_INDEX_PARTIAL,
    UNKNOWN_INSUFFICIENT_EVIDENCE,
    build_semantic_relationship_index,
    inspect_semantic_relationships,
    validate_semantic_relationship_index,
)


def _artifact():
    return generate_ingress_artifact(
        human_request="Index semantic relationships.",
        semantic_intent="Semantic relationship index proof",
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


def _by_category(index):
    return {item["relationship_category"]: item for item in index["semantic_relationships"]}


def test_relationship_index_generation_deterministic():
    first = build_semantic_relationship_index(_stable_artifacts())
    second = build_semantic_relationship_index(_stable_artifacts())

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["relationship_index_hash"].startswith("sha256:")


def test_explicit_relationships_are_indexed_correctly():
    index = build_semantic_relationship_index(_stable_artifacts())
    relationships = _by_category(index)

    assert set(RELATIONSHIP_CATEGORIES) == set(relationships)
    assert relationships["intent_to_constraint"]["known"] is True
    assert relationships["intent_to_admissibility"]["known"] is True
    assert relationships["semantic_anchor_to_replay_identity"]["known"] is True
    assert relationships["semantic_context_to_continuity_check"]["known"] is True


def test_missing_evidence_becomes_unknown():
    index = build_semantic_relationship_index()

    assert index["relationship_index_status"] == UNKNOWN_INSUFFICIENT_EVIDENCE
    assert "no semantic artifacts provided" in index["unknowns"]
    assert all(item["known"] is False for item in index["semantic_relationships"])


def test_ambiguity_relationships_are_preserved_not_resolved():
    artifacts = _stable_artifacts()
    artifacts[0]["ambiguities"] = ["NO_BLOCKING_AMBIGUITY_DETECTED"]
    artifacts[-1]["ambiguities"] = ["UNRESOLVED_SCOPE"]

    index = build_semantic_relationship_index(artifacts)
    relationship = _by_category(index)["ambiguity_to_unknown_context"]

    assert relationship["known"] is True
    assert "UNRESOLVED_SCOPE" in relationship["evidence"]
    assert relationship["inferred"] is False
    assert relationship["semantic_truth_certified"] is False


def test_no_hidden_relationship_inference_occurs():
    index = build_semantic_relationship_index(_stable_artifacts())

    assert all(item["inferred"] is False for item in index["semantic_relationships"])
    assert all(item["executable_graph_edge"] is False for item in index["semantic_relationships"])
    assert index["hidden_inference_added"] is False


def test_partial_index_when_some_relationships_missing():
    artifact = _artifact()
    artifact.pop("constraints", None)

    index = build_semantic_relationship_index([artifact])

    assert index["relationship_index_status"] == RELATIONSHIP_INDEX_PARTIAL
    assert "intent_to_constraint" in index["unknowns"]


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
    args = parser.parse_args(["cognition", "semantic-relationships", "--validate"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False


def test_cli_never_mutates_artifacts():
    artifacts = _stable_artifacts()
    before = json.dumps(artifacts, sort_keys=True)

    build_semantic_relationship_index(artifacts)

    assert json.dumps(artifacts, sort_keys=True) == before


def test_json_output_parseable_and_stable(tmp_path):
    artifact_path = tmp_path / "artifacts.json"
    output_path = tmp_path / "relationships.json"
    artifact_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")

    first = inspect_semantic_relationships(input_path=artifact_path, output_path=output_path, validate=True)
    second = inspect_semantic_relationships(input_path=artifact_path, validate=True)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed == first["semantic_relationship_index"]
    assert first["semantic_relationship_index"] == second["semantic_relationship_index"]
    assert first["semantic_relationship_validation"]["validation_status"] == "VALID"


def test_no_execution_capability_or_semantic_reasoning_introduced():
    index = build_semantic_relationship_index(_stable_artifacts())
    validation = validate_semantic_relationship_index(index)

    assert validation["validation_status"] == "VALID"
    assert index["execution_authority_added"] is False
    assert index["provider_activation_added"] is False
    assert index["semantic_reasoning_added"] is False
    assert index["hidden_inference_added"] is False
    assert index["executable_graph_semantics_added"] is False


def test_cli_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "semantic-relationships", "--validate"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition semantic-relationships"
    assert result["semantic_relationship_validation"]["validation_status"] == "VALID"
    assert "AIGOL COGNITION SEMANTIC RELATIONSHIPS" in rendered
    assert "Relationship Index Status" in rendered
    assert "Semantic Relationships" in rendered
    assert "Governance Guarantees" in rendered
