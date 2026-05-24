import json
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.cognition.semantic_replay import (
    ARTIFACT_TYPE,
    AUTHORITY_DRIFT_DETECTED,
    INVALID_TRANSITION_CHAIN,
    REPLAY_DISCONTINUITY,
    UNKNOWN_INSUFFICIENT_EVIDENCE,
    VERIFIED_STABLE,
    VERIFIED_WITH_WARNINGS,
    build_semantic_replay_continuity_check,
    inspect_semantic_replay_continuity,
)


def _artifact():
    return generate_ingress_artifact(
        human_request="Verify semantic replay continuity.",
        semantic_intent="Semantic replay continuity proof",
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


def test_stable_replay_chain_is_verified_stable():
    check = build_semantic_replay_continuity_check(_stable_artifacts())

    assert check["artifact_type"] == ARTIFACT_TYPE
    assert check["continuity_status"] == VERIFIED_STABLE
    assert check["semantic_drift_level"] == "NONE_DETECTED"
    assert check["governance_boundary_integrity"]["execution_authority"] is False


def test_missing_lineage_is_replay_discontinuity():
    artifact = _artifact()
    artifact["hashes"] = {}

    check = build_semantic_replay_continuity_check([artifact])

    assert check["continuity_status"] == REPLAY_DISCONTINUITY
    assert "minimum lineage continuity missing" in check["replay_continuity"]["findings"]


def test_authority_escalation_is_detected():
    artifacts = _stable_artifacts()
    artifacts[-1]["execution_authorized"] = True

    check = build_semantic_replay_continuity_check(artifacts)

    assert check["continuity_status"] == AUTHORITY_DRIFT_DETECTED
    assert check["authority_drift_detected"] is True
    assert any("execution_authorized" in finding for finding in check["authority_continuity"]["findings"])


def test_impossible_transitions_are_detected():
    artifacts = _stable_artifacts()
    artifacts.insert(1, {"artifact_type": "BAD_BOUNDARY", "replay_identity": artifacts[0]["replay_identity"], "execution_status": "EXECUTION_COMPLETED"})

    check = build_semantic_replay_continuity_check(artifacts)

    assert check["continuity_status"] == INVALID_TRANSITION_CHAIN
    assert check["transition_continuity"]["findings"]


def test_missing_evidence_is_unknown_insufficient_evidence():
    check = build_semantic_replay_continuity_check()

    assert check["continuity_status"] == UNKNOWN_INSUFFICIENT_EVIDENCE
    assert "no replay-visible artifacts provided" in check["unknowns"]
    assert check["replay_identity"] == "UNKNOWN"


def test_ambiguity_growth_reports_warning_status():
    artifacts = _stable_artifacts()
    artifacts[0]["ambiguities"] = ["NO_BLOCKING_AMBIGUITY_DETECTED"]
    artifacts[-1]["ambiguities"] = ["UNRESOLVED_OPERATOR_SCOPE"]

    check = build_semantic_replay_continuity_check(artifacts)

    assert check["continuity_status"] == VERIFIED_WITH_WARNINGS
    assert check["ambiguity_growth_detected"] is True
    assert check["ambiguity_continuity"]["findings"]


def test_checker_never_invokes_provider_or_execution(monkeypatch):
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
    args = parser.parse_args(["cognition", "continuity-check"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["provider_invocation_added"] is False
    assert result["semantic_replay_continuity_check"]["governance_boundary_integrity"]["provider_invocation_performed"] is False


def test_checker_never_mutates_evidence():
    artifacts = _stable_artifacts()
    before = json.dumps(artifacts, sort_keys=True)

    build_semantic_replay_continuity_check(artifacts)

    assert json.dumps(artifacts, sort_keys=True) == before


def test_json_output_is_deterministic_and_parseable(tmp_path):
    artifacts_path = tmp_path / "artifacts.json"
    output_path = tmp_path / "semantic_replay.json"
    artifacts_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")

    first = inspect_semantic_replay_continuity(input_path=artifacts_path, output_path=output_path)
    second = inspect_semantic_replay_continuity(input_path=artifacts_path)
    parsed = json.loads(output_path.read_text(encoding="utf-8"))

    first_check = first["semantic_replay_continuity_check"]
    second_check = second["semantic_replay_continuity_check"]
    assert first_check == second_check
    assert parsed == first_check
    assert first_check["semantic_replay_check_hash"].startswith("sha256:")


def test_unknown_preferred_over_guessed_meaning():
    artifact = {
        "artifact_type": "PARTIAL_SEMANTIC_EVIDENCE",
        "replay_identity": "replay-unknown-proof",
        "hashes": {"artifact_hash": "sha256:partial"},
    }

    check = build_semantic_replay_continuity_check([artifact])

    assert check["continuity_status"] in {UNKNOWN_INSUFFICIENT_EVIDENCE, REPLAY_DISCONTINUITY}
    assert "normalized_intent" in check["unknowns"]
    assert check["semantic_continuity"]["normalized_intents"] == []


def test_cli_report_contains_required_sections(tmp_path):
    artifacts_path = tmp_path / "artifacts.json"
    artifacts_path.write_text(json.dumps(_stable_artifacts(), sort_keys=True), encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(["cognition", "continuity-check", "--input", str(artifacts_path)])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol cognition continuity-check"
    assert "AIGOL COGNITION CONTINUITY CHECK" in rendered
    assert "Continuity Status" in rendered
    assert "Intent Continuity" in rendered
    assert "Governance Boundary Integrity" in rendered
