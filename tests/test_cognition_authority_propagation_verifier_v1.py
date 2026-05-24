import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cognition.authority_propagation import (
    ARTIFACT_TYPE,
    AUTHORITY_PROPAGATION_RISK,
    AUTHORITY_STABLE,
    HIDDEN_AUTHORITY_ESCALATION,
    UNKNOWN_INSUFFICIENT_EVIDENCE,
    build_authority_propagation_verifier,
    inspect_authority_propagation,
    validate_authority_propagation_verifier,
)


def _artifact():
    return generate_ingress_artifact(
        human_request="Verify authority propagation.",
        semantic_intent="Authority propagation proof",
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


def test_stable_authority_chain_is_stable():
    artifact = build_authority_propagation_verifier(_stable_artifacts())

    assert artifact["artifact_type"] == ARTIFACT_TYPE
    assert artifact["authority_propagation_status"] == AUTHORITY_STABLE
    assert artifact["violations"] == []
    assert artifact["warnings"] == []


def test_chatgpt_authority_escalation_is_hidden_escalation():
    artifacts = _stable_artifacts()
    artifacts[0]["execution_authority"] = True

    artifact = build_authority_propagation_verifier(artifacts)

    assert artifact["authority_propagation_status"] == HIDDEN_AUTHORITY_ESCALATION
    assert any("ChatGPT semantic input gained authority" in item for item in artifact["violations"])


def test_approval_treated_as_execution_is_risk():
    artifacts = _stable_artifacts()
    artifacts[2]["execution_authorized"] = True

    artifact = build_authority_propagation_verifier(artifacts)

    assert artifact["authority_propagation_status"] == AUTHORITY_PROPAGATION_RISK
    assert "human approval treated as execution authority" in artifact["warnings"]


def test_dispatch_treated_as_execution_is_risk():
    artifacts = _stable_artifacts()
    artifacts[4]["execution_authorized"] = True

    artifact = build_authority_propagation_verifier(artifacts)

    assert artifact["authority_propagation_status"] == AUTHORITY_PROPAGATION_RISK
    assert "dispatch authorization treated as execution" in artifact["warnings"]


def test_reflection_execution_authority_is_hidden_escalation():
    artifact = build_authority_propagation_verifier(
        [
            {
                "artifact_type": "REFLECTION_ARTIFACT_V1",
                "reflection_id": "reflection-1",
                "execution_authority": True,
            }
        ]
    )

    assert artifact["authority_propagation_status"] == HIDDEN_AUTHORITY_ESCALATION
    assert any("reflection gained execution authority" in item for item in artifact["violations"])


def test_missing_evidence_is_unknown():
    artifact = build_authority_propagation_verifier()

    assert artifact["authority_propagation_status"] == UNKNOWN_INSUFFICIENT_EVIDENCE
    assert "no replay-visible authority evidence provided" in artifact["unknowns"]


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
    args = parser.parse_args(["cognition", "authority", "--validate"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False
    assert result["authority_repair_added"] is False


def test_cli_never_mutates_artifacts():
    artifacts = _stable_artifacts()
    before = json.dumps(artifacts, sort_keys=True)

    build_authority_propagation_verifier(artifacts)

    assert json.dumps(artifacts, sort_keys=True) == before


def test_json_output_is_deterministic(tmp_path):
    artifact_path = tmp_path / "artifacts.json"
    output_path = tmp_path / "authority.json"
    artifact_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")

    first = inspect_authority_propagation(input_path=artifact_path, output_path=output_path, validate=True)
    second = inspect_authority_propagation(input_path=artifact_path, validate=True)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    assert parsed == first["authority_propagation_verifier"]
    assert first["authority_propagation_verifier"] == second["authority_propagation_verifier"]
    assert first["authority_validation"]["validation_status"] == "VALID"


def test_no_execution_capability_introduced():
    artifact = build_authority_propagation_verifier(_stable_artifacts())
    validation = validate_authority_propagation_verifier(artifact)

    assert validation["validation_status"] == "VALID"
    assert artifact["governance_guarantees"]["execution_authority_issued"] is False
    assert artifact["governance_guarantees"]["orchestration_authority_issued"] is False
    assert artifact["governance_guarantees"]["provider_routing_issued"] is False
    assert artifact["governance_guarantees"]["authority_repair_performed"] is False


def test_cli_authority_renders_required_sections():
    parser = build_parser()
    args = parser.parse_args(["cognition", "authority", "--validate"])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition authority"
    assert result["authority_validation"]["validation_status"] == "VALID"
    assert "AIGOL COGNITION AUTHORITY" in rendered
    assert "Authority Propagation Status" in rendered
    assert "Authority Transitions" in rendered
    assert "Governance Guarantees" in rendered
