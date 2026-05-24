import json
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cognition.registry import (
    ARTIFACT_TYPE,
    INVALID,
    VALID,
    build_cognition_registry,
    inspect_cognition_registry,
    validate_cognition_registry,
)


ROOT = Path(__file__).resolve().parents[1]


def _minimal_index():
    return {
        "artifact_type": "COGNITION_PRIMITIVES_INDEX",
        "schema_version": "1.0",
        "cognition_definition": "bounded institutional reasoning inside deterministic governance",
        "primitives": [
            {
                "id": "SEMANTIC_INGRESS",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Indexes semantic ingress evidence.",
                "cognition_category": "semantic_ingress",
                "maturity_level": "documented",
                "replay_relevance": "high",
                "authority_classification": "evidence_no_authority",
                "execution_relevance": "pre_execution_input",
            },
            {
                "id": "REPLAY_MEMORY",
                "source_files": ["COGNITION_PRIMITIVES_INDEX.json"],
                "governance_role": "Indexes replay memory evidence.",
                "cognition_category": "replay_identity",
                "maturity_level": "runtime",
                "replay_relevance": "high",
                "authority_classification": "hashing_no_authority",
                "execution_relevance": "supports_replay_continuity",
            },
        ],
        "summary": {
            "primitive_count": 2,
            "strongest_existing_categories": ["semantic_ingress", "replay_identity"],
            "primary_missing_categories": [],
            "final_assessment": "test registry",
        },
    }


def test_registry_builds_deterministically():
    first = build_cognition_registry(_minimal_index())
    second = build_cognition_registry(_minimal_index())

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["registry_hash"].startswith("sha256:")


def test_registry_indexes_primitives_and_topology():
    registry = build_cognition_registry(_minimal_index())

    assert registry["primitive_count"] == 2
    assert registry["topology"]["categories"]["semantic_ingress"] == ["SEMANTIC_INGRESS"]
    assert registry["topology"]["replay_roles"]["high"] == ["REPLAY_MEMORY", "SEMANTIC_INGRESS"]


def test_registry_preserves_authority_boundaries():
    registry = build_cognition_registry(_minimal_index())
    boundaries = registry["governance_boundaries"]

    assert boundaries["execution_authority"] is False
    assert boundaries["orchestration_authority"] is False
    assert boundaries["autonomous_cognition"] is False
    assert boundaries["autonomous_continuation"] is False
    assert boundaries["mutation_authority"] is False
    assert boundaries["runtime_activation"] is False


def test_registry_validation_passes_for_valid_index():
    registry = build_cognition_registry(_minimal_index())
    validation = validate_cognition_registry(registry)

    assert validation["validation_status"] == VALID
    assert validation["errors"] == []


def test_registry_validation_rejects_duplicate_ids():
    index = _minimal_index()
    index["primitives"].append(dict(index["primitives"][0]))

    registry = build_cognition_registry(index)

    assert registry["validation_summary"]["validation_status"] == INVALID
    assert any("duplicate primitive id" in error for error in registry["validation_summary"]["errors"])


def test_registry_validation_rejects_forbidden_authority_terms():
    index = _minimal_index()
    index["primitives"][0]["authority_classification"] = "self_modifying_governance_authority"

    registry = build_cognition_registry(index)

    assert registry["validation_summary"]["validation_status"] == INVALID
    assert any("forbidden authority term" in error for error in registry["validation_summary"]["errors"])


def test_registry_validation_detects_hash_mismatch():
    registry = build_cognition_registry(_minimal_index())
    registry["primitive_count"] = 999

    validation = validate_cognition_registry(registry)

    assert validation["validation_status"] == INVALID
    assert "registry_hash mismatch" in validation["errors"]


def test_registry_does_not_self_register_or_activate_runtime():
    registry = build_cognition_registry(_minimal_index())

    assert registry["governance_boundaries"]["self_registration"] is False
    assert registry["governance_boundaries"]["dynamic_plugin_loading"] is False
    assert registry["governance_boundaries"]["runtime_activation"] is False


def test_cli_registry_does_not_invoke_provider_or_execution(monkeypatch):
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
    args = parser.parse_args(["cognition", "registry"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_routing_added"] is False
    assert result["runtime_activation_added"] is False


def test_cli_registry_json_output_is_stable_and_parseable(tmp_path):
    index_path = tmp_path / "index.json"
    output_path = tmp_path / "registry.json"
    index_path.write_text(json.dumps(_minimal_index(), sort_keys=True), encoding="utf-8")

    first = inspect_cognition_registry(input_path=index_path, output_path=output_path)
    second = inspect_cognition_registry(input_path=index_path)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert first["cognition_registry"] == second["cognition_registry"]
    assert parsed == first["cognition_registry"]
    assert first["registry_validation"]["validation_status"] == VALID


def test_cli_registry_renders_deterministic_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "registry"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition registry"
    assert "AIGOL COGNITION REGISTRY" in rendered
    assert "Registry Status" in rendered
    assert "Primitive Index" in rendered
    assert "Governance Boundaries" in rendered


def test_repository_primitive_index_validates():
    registry = build_cognition_registry(json.loads((ROOT / "COGNITION_PRIMITIVES_INDEX.json").read_text(encoding="utf-8")))

    assert registry["primitive_count"] >= 38
    assert registry["source_file_status"]["missing_count"] == 0
    assert registry["validation_summary"]["validation_status"] == VALID
