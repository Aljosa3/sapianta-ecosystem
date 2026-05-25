import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cognition.authority_propagation import build_authority_propagation_verifier
from aigol.cognition.integrity_summary import build_cognition_integrity_summary
from aigol.cognition.lifecycle_model import build_cognition_lifecycle_model
from aigol.cognition.semantic_boundary_propagation import build_semantic_boundary_propagation
from aigol.cognition.semantic_context_audit_bundle import (
    ARTIFACT_TYPE,
    BUNDLE_COMPLETE,
    UNKNOWN_INSUFFICIENT_EVIDENCE,
    build_semantic_context_audit_bundle,
    inspect_semantic_audit_bundle,
    validate_semantic_context_audit_bundle,
)
from aigol.cognition.semantic_context_diff import build_semantic_context_diff
from aigol.cognition.semantic_context_state import build_semantic_context_state
from aigol.cognition.semantic_relationship_index import build_semantic_relationship_index
from aigol.cognition.topology_report import build_cognition_registry_topology_report


def _artifact():
    return generate_ingress_artifact(
        human_request="Bundle semantic cognition audit evidence.",
        semantic_intent="Semantic audit bundle proof",
    )


def _stable_source_artifacts():
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


def _bundle_artifacts():
    source = _stable_source_artifacts()
    topology = build_cognition_registry_topology_report(input_path="COGNITION_PRIMITIVES_INDEX.json")
    lifecycle = build_cognition_lifecycle_model(topology)
    return [
        build_semantic_context_state(source),
        build_semantic_relationship_index(source),
        build_semantic_boundary_propagation(source),
        build_semantic_context_diff(source, source),
        build_authority_propagation_verifier(source),
        build_cognition_integrity_summary(source),
        lifecycle,
        topology,
    ]


def test_bundle_generation_deterministic():
    first = build_semantic_context_audit_bundle(_bundle_artifacts())
    second = build_semantic_context_audit_bundle(_bundle_artifacts())

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["bundle_hash"].startswith("sha256:")


def test_explicit_artifacts_are_included_correctly():
    bundle = build_semantic_context_audit_bundle(_bundle_artifacts())
    included_types = {artifact["artifact_type"] for artifact in bundle["included_artifacts"]}

    assert bundle["bundle_status"] == BUNDLE_COMPLETE
    assert included_types == set(bundle["bundle_manifest"]["expected_artifact_types"])
    assert bundle["semantic_context_refs"]
    assert bundle["relationship_index_refs"]
    assert bundle["boundary_propagation_refs"]
    assert bundle["semantic_diff_refs"]
    assert bundle["authority_verification_refs"]
    assert bundle["integrity_summary_refs"]
    assert bundle["lifecycle_refs"]
    assert bundle["topology_refs"]


def test_missing_artifacts_become_unknown():
    bundle = build_semantic_context_audit_bundle()

    assert bundle["bundle_status"] == UNKNOWN_INSUFFICIENT_EVIDENCE
    assert "no explicit semantic cognition artifacts provided" in bundle["unknowns"]
    assert bundle["bundle_manifest"]["missing_artifact_types"]
    assert bundle["bundle_manifest"]["missing_artifacts_synthesized"] is False


def test_artifact_hashes_are_deterministic():
    first = build_semantic_context_audit_bundle(_bundle_artifacts())
    second = build_semantic_context_audit_bundle(_bundle_artifacts())

    assert first["artifact_hashes"] == second["artifact_hashes"]
    assert first["artifact_hashes"]
    assert all(value.startswith("sha256:") for value in first["artifact_hashes"].values())


def test_bundle_hash_is_stable_and_validated():
    bundle = build_semantic_context_audit_bundle(_bundle_artifacts())
    validation = validate_semantic_context_audit_bundle(bundle)

    assert validation["validation_status"] == "VALID"
    assert bundle["bundle_hash"] == build_semantic_context_audit_bundle(_bundle_artifacts())["bundle_hash"]


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
    args = parser.parse_args(["cognition", "semantic-audit-bundle", "--validate"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False


def test_cli_never_mutates_source_artifacts():
    artifacts = _bundle_artifacts()
    before = json.dumps(artifacts, sort_keys=True)

    build_semantic_context_audit_bundle(artifacts)

    assert json.dumps(artifacts, sort_keys=True) == before


def test_json_output_parseable_and_stable(tmp_path):
    artifact_path = tmp_path / "semantic_artifacts.json"
    output_path = tmp_path / "semantic_audit_bundle.json"
    artifact_path.write_text(json.dumps(_bundle_artifacts(), sort_keys=True), encoding="utf-8")

    first = inspect_semantic_audit_bundle(input_path=artifact_path, output_path=output_path, validate=True)
    second = inspect_semantic_audit_bundle(input_path=artifact_path, validate=True)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed == first["semantic_context_audit_bundle"]
    assert first["semantic_context_audit_bundle"] == second["semantic_context_audit_bundle"]
    assert first["semantic_audit_bundle_validation"]["validation_status"] == "VALID"


def test_no_execution_capability_introduced():
    bundle = build_semantic_context_audit_bundle(_bundle_artifacts())
    validation = validate_semantic_context_audit_bundle(bundle)

    assert validation["validation_status"] == "VALID"
    assert bundle["execution_authority_added"] is False
    assert bundle["orchestration_authority_added"] is False
    assert bundle["planning_authority_added"] is False
    assert bundle["runtime_activation_added"] is False
    assert bundle["provider_routing_added"] is False
    assert bundle["provider_activation_added"] is False
    assert bundle["executable_semantic_graph_added"] is False


def test_no_semantic_reasoning_introduced():
    bundle = build_semantic_context_audit_bundle(_bundle_artifacts())

    assert bundle["semantic_reasoning_added"] is False
    assert bundle["hidden_inference_added"] is False
    assert bundle["semantic_repair_added"] is False
    assert bundle["ambiguity_resolution_added"] is False
    assert bundle["semantic_optimization_added"] is False
    assert bundle["autonomous_semantic_evolution_added"] is False


def test_cli_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "semantic-audit-bundle", "--validate"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition semantic-audit-bundle"
    assert result["semantic_audit_bundle_validation"]["validation_status"] == "VALID"
    assert "AIGOL COGNITION SEMANTIC AUDIT BUNDLE" in rendered
    assert "Bundle Status" in rendered
    assert "Included Artifacts" in rendered
    assert "Governance Guarantees" in rendered
