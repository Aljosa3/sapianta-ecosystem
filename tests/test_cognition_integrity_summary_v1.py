import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cognition.integrity_summary import (
    ARTIFACT_TYPE,
    DEGRADED,
    HEALTHY,
    HEALTHY_WITH_UNKNOWN_CONTEXT,
    build_cognition_integrity_summary,
    inspect_cognition_integrity,
    validate_cognition_integrity_summary,
)


def _artifact():
    return generate_ingress_artifact(
        human_request="Audit cognition integrity.",
        semantic_intent="Cognition integrity summary proof",
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


def test_integrity_summary_is_deterministic():
    first = build_cognition_integrity_summary(_stable_artifacts())
    second = build_cognition_integrity_summary(_stable_artifacts())

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["integrity_summary_hash"].startswith("sha256:")


def test_structurally_healthy_without_live_artifacts_is_unknown_context():
    summary = build_cognition_integrity_summary()

    assert summary["integrity_status"] == HEALTHY_WITH_UNKNOWN_CONTEXT
    assert summary["health_summary"]["structural_registry_health"] == "VALID"
    assert summary["health_summary"]["semantic_continuity_health"] == "UNKNOWN_INSUFFICIENT_EVIDENCE"


def test_stable_artifacts_are_healthy():
    summary = build_cognition_integrity_summary(_stable_artifacts())

    assert summary["integrity_status"] == HEALTHY
    assert summary["health_summary"]["semantic_continuity_health"] == "VERIFIED_STABLE"
    assert summary["health_summary"]["governance_guarantees_intact"] is True


def test_semantic_drift_degrades_integrity():
    artifacts = _stable_artifacts()
    artifacts[-1]["execution_authorized"] = True

    summary = build_cognition_integrity_summary(artifacts)

    assert summary["integrity_status"] == DEGRADED
    assert summary["health_summary"]["semantic_continuity_health"] == "AUTHORITY_DRIFT_DETECTED"


def test_integrity_summary_components_present():
    summary = build_cognition_integrity_summary(_stable_artifacts())
    component_names = {component["component_name"] for component in summary["components"]}

    assert component_names == {
        "cognition_state_envelope",
        "semantic_replay_continuity",
        "cognition_registry",
        "cognition_topology_report",
        "cognition_lifecycle_model",
    }


def test_governance_guarantees_preserved():
    summary = build_cognition_integrity_summary(_stable_artifacts())

    assert all(value is False for value in summary["governance_guarantees"].values())
    assert summary["execution_authority_added"] is False
    assert summary["orchestration_authority_added"] is False
    assert summary["autonomous_continuation_added"] is False
    assert summary["provider_activation_added"] is False
    assert summary["continuity_repair_added"] is False


def test_validation_passes_and_detects_hash_mismatch():
    summary = build_cognition_integrity_summary(_stable_artifacts())
    validation = validate_cognition_integrity_summary(summary)

    assert validation["validation_status"] == "VALID"
    summary["component_count"] = 99
    invalid = validate_cognition_integrity_summary(summary)
    assert invalid["validation_status"] == "INVALID"
    assert "integrity_summary_hash mismatch" in invalid["errors"]


def test_cli_never_invokes_provider_or_execution(monkeypatch):
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
    args = parser.parse_args(["cognition", "integrity", "--validate"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False


def test_cli_never_repairs_or_mutates_artifacts():
    artifacts = _stable_artifacts()
    before = json.dumps(artifacts, sort_keys=True)

    build_cognition_integrity_summary(artifacts)

    assert json.dumps(artifacts, sort_keys=True) == before


def test_json_output_parseable_and_stable(tmp_path):
    artifact_path = tmp_path / "artifacts.json"
    output_path = tmp_path / "integrity.json"
    artifact_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")

    first = inspect_cognition_integrity(input_path=artifact_path, output_path=output_path, validate=True)
    second = inspect_cognition_integrity(input_path=artifact_path, validate=True)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed == first["cognition_integrity_summary"]
    assert first["cognition_integrity_summary"] == second["cognition_integrity_summary"]
    assert first["integrity_validation"]["validation_status"] == "VALID"


def test_cli_integrity_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "integrity", "--validate"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition integrity"
    assert result["integrity_validation"]["validation_status"] == "VALID"
    assert "AIGOL COGNITION INTEGRITY" in rendered
    assert "Integrity Status" in rendered
    assert "Cognition Health" in rendered
    assert "Authority Boundaries" in rendered
