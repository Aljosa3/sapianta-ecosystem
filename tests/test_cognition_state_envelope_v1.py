import json
import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cognition.state_envelope import (
    ARTIFACT_TYPE,
    build_cognition_state_envelope,
    inspect_cognition_input,
)
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact


ROOT = Path(__file__).resolve().parents[1]


def _artifact():
    return generate_ingress_artifact(
        human_request="Inspect bounded cognition state.",
        semantic_intent="Cognition observability proof",
    )


def _artifacts_with_dispatch():
    chain = build_governed_chain(ingress_artifact=_artifact())
    return [
        _artifact(),
        chain["task_package_preview"],
        chain["human_approval"],
        chain["handoff_preview"],
        chain["dispatch_authorization"],
        chain["continuity_preview"],
    ]


def test_envelope_creation_is_deterministic():
    artifacts = _artifacts_with_dispatch()

    first = build_cognition_state_envelope(artifacts)
    second = build_cognition_state_envelope(artifacts)

    assert first == second
    assert first["artifact_type"] == ARTIFACT_TYPE
    assert first["envelope_hash"].startswith("sha256:")


def test_missing_evidence_becomes_unknown_not_guessed():
    envelope = build_cognition_state_envelope()

    assert envelope["replay_identity"] == "UNKNOWN"
    assert envelope["normalized_intent"] == "UNKNOWN"
    assert envelope["admissibility_state"] == "UNKNOWN"
    assert envelope["continuity_status"] == "UNKNOWN"


def test_envelope_never_grants_execution_authority():
    envelope = build_cognition_state_envelope(_artifacts_with_dispatch())

    assert envelope["execution_authority"] is False
    execution_entry = [
        entry for entry in envelope["authority_matrix"]
        if entry["authority_name"] == "execution authority"
    ][0]
    assert execution_entry["allowed"] == []
    assert "automatic execution" in execution_entry["forbidden"]


def test_envelope_never_grants_orchestration_authority():
    envelope = build_cognition_state_envelope(_artifacts_with_dispatch())

    assert envelope["orchestration_authority"] is False
    assert "orchestration" in envelope["forbidden_transitions"]


def test_envelope_never_grants_autonomous_continuation():
    envelope = build_cognition_state_envelope(_artifacts_with_dispatch())

    assert envelope["autonomous_continuation"] is False
    assert "autonomous_continuation" in envelope["forbidden_transitions"]
    assert "hidden_continuation" in envelope["forbidden_transitions"]


def test_envelope_never_grants_mutation_authority():
    envelope = build_cognition_state_envelope(_artifacts_with_dispatch())

    assert envelope["mutation_authority"] is False
    mutation_entry = [
        entry for entry in envelope["authority_matrix"]
        if entry["authority_name"] == "mutation authority"
    ][0]
    assert mutation_entry["status"] == "NOT_GRANTED_BY_ENVELOPE"


def test_authority_matrix_reports_without_granting_authority():
    envelope = build_cognition_state_envelope(_artifacts_with_dispatch())

    dispatch_entry = [
        entry for entry in envelope["authority_matrix"]
        if entry["authority_name"] == "dispatch authority"
    ][0]
    assert dispatch_entry["status"] == "DISPATCH_AUTHORIZED_EVIDENCE_PRESENT"
    assert "execution" in dispatch_entry["forbidden"]
    assert envelope["execution_authority"] is False


def test_cli_inspect_does_not_invoke_provider_or_execution_code(monkeypatch):
    called = {"execution": False}

    def forbidden_execution(*args, **kwargs):
        called["execution"] = True
        raise AssertionError("execution handoff must not run")

    import aigol.cli.aigol_cli as cli

    monkeypatch.setattr(cli, "run_execution_handoff", forbidden_execution)
    parser = build_parser()
    args = parser.parse_args(["cognition", "inspect"])
    result = run_command(args)

    assert result["command"] == "aigol cognition inspect"
    assert called["execution"] is False
    assert result["execution_authority_added"] is False
    assert result["cognition_state_envelope"]["provider_invocation_performed"] is False


def test_json_output_is_stable_and_parseable(tmp_path):
    artifact_path = tmp_path / "ingress.json"
    artifact_path.write_text(json.dumps(_artifact(), sort_keys=True), encoding="utf-8")

    first = inspect_cognition_input(input_path=artifact_path)
    second = inspect_cognition_input(input_path=artifact_path)
    encoded = json.dumps(first, sort_keys=True, separators=(",", ":"))
    parsed = json.loads(encoded)

    assert first == second
    assert parsed["cognition_state_envelope"]["artifact_type"] == ARTIFACT_TYPE


def test_cli_output_file_is_explicit_and_parseable(tmp_path):
    output_path = tmp_path / "cognition_envelope.json"
    parser = build_parser()
    args = parser.parse_args(["cognition", "inspect", "--output", str(output_path)])
    result = run_command(args)

    assert result["output"]["written"] is True
    parsed = json.loads(output_path.read_text(encoding="utf-8"))
    assert parsed["artifact_type"] == ARTIFACT_TYPE
    assert parsed["execution_authority"] is False


def test_forbidden_transitions_include_closed_boundaries_without_evidence():
    envelope = build_cognition_state_envelope([_artifact()])

    assert "execution" in envelope["forbidden_transitions"]
    assert "dispatch" in envelope["forbidden_transitions"]
    assert "orchestration" in envelope["forbidden_transitions"]
    assert "hidden_continuation" in envelope["forbidden_transitions"]


def test_dispatch_forbidden_transition_removed_only_with_explicit_evidence():
    envelope = build_cognition_state_envelope(_artifacts_with_dispatch())

    assert "dispatch" not in envelope["forbidden_transitions"]
    assert "execution" in envelope["forbidden_transitions"]
    assert "controlled_execution_continuity_preview" in envelope["allowed_next_transitions"]


def test_human_readable_render_contains_required_sections():
    result = inspect_cognition_input(artifacts=_artifacts_with_dispatch())
    rendered = render_command_result(result)

    assert "AIGOL COGNITION INSPECT" in rendered
    assert "Semantic State" in rendered
    assert "Authority Matrix" in rendered
    assert "Replay / Lineage State" in rendered
    assert "Forbidden Transitions" in rendered


def test_cli_json_flag_outputs_parseable_json():
    result = subprocess.run(
        ["python", "-m", "aigol.cli.aigol_cli", "cognition", "inspect", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["command"] == "aigol cognition inspect"
    assert parsed["cognition_state_envelope"]["execution_authority"] is False
