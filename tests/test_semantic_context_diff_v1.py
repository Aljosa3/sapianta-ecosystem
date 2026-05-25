import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cognition.semantic_context_diff import (
    ARTIFACT_TYPE,
    BOUNDARY_DRIFT_RISK,
    UNKNOWN_STATUS,
    build_semantic_context_diff,
    inspect_semantic_diff,
    validate_semantic_context_diff,
)


def _artifact(human_request="Diff semantic context.", semantic_intent="Semantic context diff proof"):
    return generate_ingress_artifact(
        human_request=human_request,
        semantic_intent=semantic_intent,
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


def test_diff_generation_deterministic():
    source = _stable_artifacts()
    target = _stable_artifacts()

    first = build_semantic_context_diff(source, target)
    second = build_semantic_context_diff(source, target)

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["diff_hash"].startswith("sha256:")


def test_explicit_semantic_deltas_detected_correctly():
    source = [_artifact()]
    target = [_artifact()]
    target[0]["constraints"] = list(target[0]["constraints"]) + ["new explicit constraint"]

    diff = build_semantic_context_diff(source, target)

    assert "new explicit constraint" in json.dumps(diff["added_constraints"])
    assert any(delta["diff_type"] == "semantic_constraint_added" and delta["changed"] for delta in diff["semantic_deltas"])


def test_missing_evidence_becomes_unknown():
    diff = build_semantic_context_diff()

    assert diff["diff_status"] == UNKNOWN_STATUS
    assert "source_artifacts" in diff["unknowns"]
    assert "target_artifacts" in diff["unknowns"]


def test_boundary_changes_detected_correctly():
    source = [_artifact()]
    target = [_artifact()]
    target[0].pop("authority_boundary", None)

    diff = build_semantic_context_diff(source, target)

    assert diff["diff_status"] == BOUNDARY_DRIFT_RISK
    assert diff["boundary_deltas"]
    assert any(delta["diff_type"] == "authority_boundary_changed" and delta["changed"] for delta in diff["authority_deltas"])


def test_unchanged_anchors_preserved_correctly():
    source = _stable_artifacts()
    target = _stable_artifacts()

    diff = build_semantic_context_diff(source, target)
    unchanged = {anchor["anchor_name"]: anchor["value"] for anchor in diff["unchanged_anchors"]}

    assert unchanged["original governance intent"] == "Diff semantic context."
    assert unchanged["semantic intent"] == "Semantic context diff proof"
    assert "normalized intent" in unchanged


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
    args = parser.parse_args(["cognition", "semantic-diff", "--validate"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False


def test_cli_never_mutates_artifacts():
    source = _stable_artifacts()
    target = _stable_artifacts()
    before_source = json.dumps(source, sort_keys=True)
    before_target = json.dumps(target, sort_keys=True)

    build_semantic_context_diff(source, target)

    assert json.dumps(source, sort_keys=True) == before_source
    assert json.dumps(target, sort_keys=True) == before_target


def test_json_output_parseable_and_stable(tmp_path):
    source_path = tmp_path / "source.json"
    target_path = tmp_path / "target.json"
    output_path = tmp_path / "diff.json"
    source_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")
    target_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")

    first = inspect_semantic_diff(source_path=source_path, target_path=target_path, output_path=output_path, validate=True)
    second = inspect_semantic_diff(source_path=source_path, target_path=target_path, validate=True)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed == first["semantic_context_diff"]
    assert first["semantic_context_diff"] == second["semantic_context_diff"]
    assert first["semantic_diff_validation"]["validation_status"] == "VALID"


def test_no_execution_capability_introduced():
    diff = build_semantic_context_diff(_stable_artifacts(), _stable_artifacts())
    validation = validate_semantic_context_diff(diff)

    assert validation["validation_status"] == "VALID"
    assert diff["execution_authority_added"] is False
    assert diff["orchestration_authority_added"] is False
    assert diff["provider_activation_added"] is False
    assert diff["executable_semantic_graph_semantics_added"] is False


def test_no_semantic_reasoning_introduced():
    diff = build_semantic_context_diff(_stable_artifacts(), _stable_artifacts())

    assert diff["semantic_reasoning_added"] is False
    assert diff["hidden_inference_added"] is False
    assert diff["semantic_repair_added"] is False
    assert diff["ambiguity_resolution_added"] is False
    for section in ("semantic_deltas", "boundary_deltas", "continuity_deltas", "ambiguity_deltas", "authority_deltas"):
        assert all(delta["inferred"] is False for delta in diff[section])


def test_cli_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "semantic-diff", "--validate"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition semantic-diff"
    assert result["semantic_diff_validation"]["validation_status"] == "VALID"
    assert "AIGOL COGNITION SEMANTIC DIFF" in rendered
    assert "Semantic Diff Status" in rendered
    assert "Boundary Deltas" in rendered
    assert "Continuity Deltas" in rendered
