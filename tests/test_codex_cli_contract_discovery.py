from pathlib import Path
import textwrap

from sapianta_bridge.provider_connectors.codex_contract_discovery.codex_cli_probe import probe_codex_cli_contract
from sapianta_bridge.provider_connectors.codex_contract_discovery.codex_contract_evidence import (
    codex_contract_evidence,
    validate_codex_contract_evidence,
)
from sapianta_bridge.provider_connectors.codex_contract_discovery.codex_contract_model import (
    validate_codex_cli_contract,
)


def _fake_codex(path: Path):
    path.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys
            if "--version" in sys.argv:
                print("codex-cli 0.130.0-alpha.5")
                raise SystemExit(0)
            print("Codex CLI")
            print("Commands:")
            print("  exec            Run Codex non-interactively [aliases: e]")
            print("  review          Run a code review non-interactively")
            print("Arguments:")
            print("  [PROMPT]")
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | 0o111)


def test_codex_cli_contract_discovery_uses_safe_probes_only(tmp_path):
    codex = tmp_path / "codex"
    _fake_codex(codex)

    result = probe_codex_cli_contract(codex_executable=str(codex))
    contract = result["contract"]

    assert contract["status"] == "DISCOVERED_PARTIAL"
    assert contract["codex_cli_detected"] is True
    assert contract["non_interactive_supported"] is True
    assert contract["recommended_invocation_vector"] == ["codex", "exec", "<bounded_prompt>"]
    assert contract["shell_used"] is False
    assert contract["task_executed"] is False
    assert {tuple(probe["args"]) for probe in result["probes"]} == {
        ("--help",),
        ("-h",),
        ("run", "--help"),
        ("run", "-h"),
        ("--version",),
    }
    assert validate_codex_cli_contract(contract)["valid"] is True


def test_codex_cli_contract_discovery_blocks_missing_cli():
    result = probe_codex_cli_contract(codex_executable="")
    contract = result["contract"]

    assert contract["status"] == "BLOCKED"
    assert contract["codex_cli_detected"] is False
    assert contract["task_executed"] is False


def test_codex_contract_evidence_rejects_forbidden_task_execution(tmp_path):
    codex = tmp_path / "codex"
    _fake_codex(codex)
    evidence = codex_contract_evidence(discovery_result=probe_codex_cli_contract(codex_executable=str(codex)))
    evidence["task_executed"] = True

    validation = validate_codex_contract_evidence(evidence)

    assert validation["valid"] is False
    assert any(error["field"] == "task_executed" for error in validation["errors"])


def test_checked_in_discovery_report_contract_parses():
    report = Path("sapianta_bridge/provider_connectors/codex_contract_discovery/evidence/CODEX_CLI_DISCOVERY_REPORT.json")
    import json

    contract = json.loads(report.read_text(encoding="utf-8"))

    assert contract["discovery_name"] == "CODEX_CLI_CONTRACT_DISCOVERY_V1"
    assert contract["status"] in {"DISCOVERED", "DISCOVERED_PARTIAL", "BLOCKED", "FAILED"}
    assert contract["shell_used"] is False
    assert contract["task_executed"] is False
    assert validate_codex_cli_contract(contract)["valid"] is True
