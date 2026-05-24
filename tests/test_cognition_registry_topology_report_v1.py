import json
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cognition.registry import build_cognition_registry
from aigol.cognition.topology_report import (
    ARTIFACT_TYPE,
    build_cognition_registry_topology_report,
    inspect_cognition_topology,
)


ROOT = Path(__file__).resolve().parents[1]


def _index():
    return {
        "artifact_type": "COGNITION_PRIMITIVES_INDEX",
        "schema_version": "1.0",
        "cognition_definition": "bounded institutional reasoning inside deterministic governance",
        "primitives": [
            {
                "id": "CONSTITUTION",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Constrains all cognition.",
                "cognition_category": "constitutional_reasoning",
                "maturity_level": "documented",
                "replay_relevance": "high",
                "authority_classification": "constitutional_constraint",
                "execution_relevance": "constrains_execution",
            },
            {
                "id": "INGRESS",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Represents semantic input.",
                "cognition_category": "semantic_ingress",
                "maturity_level": "runtime",
                "replay_relevance": "high",
                "authority_classification": "semantic_input_no_authority",
                "execution_relevance": "pre_execution_input",
            },
            {
                "id": "APPROVAL",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Represents human approval evidence.",
                "cognition_category": "human_authority",
                "maturity_level": "runtime",
                "replay_relevance": "high",
                "authority_classification": "human_approval_evidence_not_execution",
                "execution_relevance": "approval_boundary",
            },
            {
                "id": "RETURN",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Represents governed return memory.",
                "cognition_category": "execution_memory",
                "maturity_level": "runtime",
                "replay_relevance": "high",
                "authority_classification": "evidence_persistence_no_replay_mutation",
                "execution_relevance": "post_execution_memory",
            },
        ],
        "summary": {
            "primitive_count": 4,
            "strongest_existing_categories": ["constitutional_reasoning", "semantic_ingress"],
            "primary_missing_categories": [],
            "final_assessment": "test topology",
        },
    }


def test_topology_report_is_deterministic():
    registry = build_cognition_registry(_index())

    first = build_cognition_registry_topology_report(registry)
    second = build_cognition_registry_topology_report(registry)

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["topology_report_hash"].startswith("sha256:")


def test_topology_report_derives_subsystems():
    report = build_cognition_registry_topology_report(build_cognition_registry(_index()))

    assert "constitutional_governance" in report["subsystems"]
    assert "semantic_interpretation" in report["subsystems"]
    assert "authority_boundary" in report["subsystems"]
    assert "replay_and_memory" in report["subsystems"]
    assert report["subsystems"]["constitutional_governance"]["primitive_ids"] == ["CONSTITUTION"]


def test_topology_report_contains_relationships():
    report = build_cognition_registry_topology_report(build_cognition_registry(_index()))

    relationships = {(item["from"], item["to"]) for item in report["relationships"]}
    assert ("constitutional_governance", "semantic_interpretation") in relationships
    assert ("authority_boundary", "provider_execution_boundary") in relationships


def test_topology_report_maps_replay_continuity():
    report = build_cognition_registry_topology_report(build_cognition_registry(_index()))

    replay = report["replay_continuity_map"]
    assert replay["semantic_interpretation"]["replay_visible"] is True
    assert replay["replay_and_memory"]["high_replay_primitives"] == ["RETURN"]


def test_topology_report_maps_authority_transitions_without_granting_authority():
    report = build_cognition_registry_topology_report(build_cognition_registry(_index()))

    transitions = report["authority_transition_map"]
    assert any(item["authority_classification"] == "human_approval_evidence_not_execution" for item in transitions)
    assert all(item["authority_granted_by_report"] is False for item in transitions)


def test_topology_report_preserves_no_authority_guarantees():
    report = build_cognition_registry_topology_report(build_cognition_registry(_index()))
    guarantees = report["integrity_guarantees"]

    assert guarantees["execution_authority"] is False
    assert guarantees["orchestration_authority"] is False
    assert guarantees["autonomous_cognition"] is False
    assert guarantees["planning_authority"] is False
    assert guarantees["runtime_activation"] is False
    assert guarantees["provider_routing"] is False
    assert guarantees["semantic_reasoning"] is False
    assert guarantees["hidden_topology_inference"] is False
    assert guarantees["dynamic_graph_execution"] is False


def test_uncategorized_categories_are_explicit_unknowns():
    index = _index()
    index["primitives"].append(
        {
            "id": "UNKNOWN_PRIMITIVE",
            "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
            "governance_role": "Unknown category proof.",
            "cognition_category": "new_unknown_category",
            "maturity_level": "documented",
            "replay_relevance": "medium",
            "authority_classification": "evidence_no_authority",
            "execution_relevance": "none",
        }
    )
    index["summary"]["primitive_count"] = 5

    report = build_cognition_registry_topology_report(build_cognition_registry(index))

    assert "uncategorized" in report["subsystems"]
    assert "UNKNOWN_PRIMITIVE" in report["subsystems"]["uncategorized"]["primitive_ids"]
    assert "uncategorized primitives present" in report["unknowns"]


def test_cli_topology_does_not_invoke_provider_or_execution(monkeypatch):
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
    args = parser.parse_args(["cognition", "topology"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["runtime_activation_added"] is False
    assert result["provider_routing_added"] is False


def test_cli_topology_json_output_is_stable_and_parseable(tmp_path):
    index_path = tmp_path / "index.json"
    output_path = tmp_path / "topology.json"
    index_path.write_text(json.dumps(_index(), sort_keys=True), encoding="utf-8")

    first = inspect_cognition_topology(input_path=index_path, output_path=output_path)
    second = inspect_cognition_topology(input_path=index_path)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert first["cognition_topology_report"] == second["cognition_topology_report"]
    assert parsed == first["cognition_topology_report"]


def test_cli_topology_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "topology"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition topology"
    assert "AIGOL COGNITION TOPOLOGY" in rendered
    assert "Subsystems" in rendered
    assert "Relationships" in rendered
    assert "Boundary Analysis" in rendered
    assert "Replay Continuity" in rendered
    assert "Integrity Guarantees" in rendered


def test_repository_registry_topology_builds_from_current_index():
    report = build_cognition_registry_topology_report(input_path=ROOT / "COGNITION_PRIMITIVES_INDEX.json")

    assert report["primitive_count"] >= 38
    assert report["source_registry_validation_status"] == "VALID"
    assert report["integrity_guarantees"]["registry_valid"] is True
