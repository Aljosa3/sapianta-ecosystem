import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cognition.lifecycle_model import (
    ARTIFACT_TYPE,
    build_cognition_lifecycle_model,
    inspect_cognition_lifecycle,
    validate_cognition_lifecycle_model,
)
from aigol.cognition.registry import build_cognition_registry
from aigol.cognition.topology_report import build_cognition_registry_topology_report


def _index():
    return {
        "artifact_type": "COGNITION_PRIMITIVES_INDEX",
        "schema_version": "1.0",
        "cognition_definition": "bounded institutional reasoning inside deterministic governance",
        "primitives": [
            {
                "id": "INGRESS",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Semantic ingress evidence.",
                "cognition_category": "semantic_ingress",
                "maturity_level": "runtime",
                "replay_relevance": "high",
                "authority_classification": "semantic_input_no_authority",
                "execution_relevance": "pre_execution_input",
            },
            {
                "id": "AUTHORITY",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Authority boundary evidence.",
                "cognition_category": "human_authority",
                "maturity_level": "runtime",
                "replay_relevance": "high",
                "authority_classification": "human_approval_evidence_not_execution",
                "execution_relevance": "approval_boundary",
            },
            {
                "id": "MEMORY",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Replay memory evidence.",
                "cognition_category": "execution_memory",
                "maturity_level": "runtime",
                "replay_relevance": "high",
                "authority_classification": "evidence_persistence_no_replay_mutation",
                "execution_relevance": "post_execution_memory",
            },
        ],
        "summary": {
            "primitive_count": 3,
            "strongest_existing_categories": ["semantic_ingress", "human_authority"],
            "primary_missing_categories": [],
            "final_assessment": "test lifecycle",
        },
    }


def _topology():
    return build_cognition_registry_topology_report(build_cognition_registry(_index()))


def test_lifecycle_generation_is_deterministic():
    first = build_cognition_lifecycle_model(_topology())
    second = build_cognition_lifecycle_model(_topology())

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["lifecycle_model_hash"].startswith("sha256:")


def test_transition_counts_are_stable():
    model = build_cognition_lifecycle_model(_topology())

    assert model["phase_count"] == 16
    assert model["transition_count"] == 15
    assert model["transition_count"] == len(model["transitions"])


def test_continuity_propagation_paths_generated_correctly():
    model = build_cognition_lifecycle_model(_topology())
    paths = {path["path_name"]: path for path in model["continuity_propagation_paths"]}

    assert "semantic_continuity_propagation" in paths
    assert "authority_continuity_propagation" in paths
    assert "replay_continuity_propagation" in paths
    assert paths["semantic_continuity_propagation"]["authority_granted"] is False


def test_stabilization_stages_generated_correctly():
    model = build_cognition_lifecycle_model(_topology())
    stages = {stage["stage_name"]: stage for stage in model["semantic_stabilization_stages"]}

    assert "semantic_stabilization" in stages
    assert "replay_stabilization" in stages
    assert "governance_stabilization" in stages
    assert "cognition_integrity_stabilization" in stages
    assert all(stage["operational"] is False for stage in stages.values())


def test_epoch_boundaries_generated_correctly():
    model = build_cognition_lifecycle_model(_topology())
    epochs = {epoch["epoch_name"]: epoch for epoch in model["epoch_boundaries"]}

    assert "bounded_cognition_visibility_epoch" in epochs
    assert "governed_execution_substrate_epoch" in epochs
    assert all(epoch["operational"] is False for epoch in epochs.values())
    assert all(epoch["scheduling_enabled"] is False for epoch in epochs.values())


def test_unknown_phase_handling_works():
    index = _index()
    index["primitives"].append(
        {
            "id": "UNCATEGORIZED",
            "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
            "governance_role": "Unknown lifecycle evidence.",
            "cognition_category": "new_unknown_category",
            "maturity_level": "documented",
            "replay_relevance": "medium",
            "authority_classification": "evidence_no_authority",
            "execution_relevance": "none",
        }
    )
    index["summary"]["primitive_count"] = 4
    topology = build_cognition_registry_topology_report(build_cognition_registry(index))

    model = build_cognition_lifecycle_model(topology)

    assert model["phases"][-1]["phase_id"] == "UNKNOWN"
    assert "uncategorized primitives present" in model["unknowns"]


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
    args = parser.parse_args(["cognition", "lifecycle"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False


def test_cli_never_mutates_cognition_artifacts():
    topology = _topology()
    before = json.dumps(topology, sort_keys=True)

    build_cognition_lifecycle_model(topology)

    assert json.dumps(topology, sort_keys=True) == before


def test_json_output_parseable_and_stable(tmp_path):
    output_path = tmp_path / "lifecycle.json"

    first = inspect_cognition_lifecycle(output_path=output_path, validate=True)
    second = inspect_cognition_lifecycle(validate=True)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed == first["cognition_lifecycle_model"]
    assert first["cognition_lifecycle_model"] == second["cognition_lifecycle_model"]
    assert first["lifecycle_validation"]["validation_status"] == "VALID"


def test_no_execution_capability_introduced():
    model = build_cognition_lifecycle_model(_topology())
    validation = validate_cognition_lifecycle_model(model)

    assert validation["validation_status"] == "VALID"
    assert model["execution_authority_added"] is False
    assert model["orchestration_authority_added"] is False
    assert model["autonomous_continuation_added"] is False
    assert model["provider_activation_added"] is False
    assert all(transition["execution_capability"] is False for transition in model["transitions"])


def test_cli_lifecycle_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "lifecycle", "--validate"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition lifecycle"
    assert result["lifecycle_validation"]["validation_status"] == "VALID"
    assert "AIGOL COGNITION LIFECYCLE" in rendered
    assert "Lifecycle Phases" in rendered
    assert "Lifecycle Transitions" in rendered
    assert "Semantic Continuity Paths" in rendered
    assert "Epoch Boundaries" in rendered
