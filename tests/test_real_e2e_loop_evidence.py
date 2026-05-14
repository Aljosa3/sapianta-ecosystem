import textwrap

from sapianta_bridge.real_e2e_codex_loop.e2e_loop_controller import run_real_e2e_codex_loop
from sapianta_bridge.real_e2e_codex_loop.e2e_loop_evidence import validate_e2e_loop_evidence
from sapianta_bridge.real_e2e_codex_loop.e2e_loop_request import create_e2e_loop_request


def _result(tmp_path):
    codex = tmp_path / "codex"
    codex.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            print("real-e2e-ok")
            """
        ),
        encoding="utf-8",
    )
    codex.chmod(codex.stat().st_mode | 0o111)
    request = create_e2e_loop_request(
        chatgpt_request="execute governed validation",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        execution_authorized=True,
        approved_by="human",
        codex_executable=str(codex),
    ).to_dict()
    return run_real_e2e_codex_loop(request=request)


def test_real_e2e_loop_evidence_is_replay_safe(tmp_path):
    evidence = _result(tmp_path)["evidence"]

    assert evidence["validation_name"] == "FIRST_REAL_E2E_CODEX_LOOP_V1"
    assert evidence["provider_id"] == "codex_cli"
    assert evidence["manual_copy_paste_required"] is False
    assert evidence["replay_safe"] is True
    assert validate_e2e_loop_evidence(evidence)["valid"] is True


def test_real_e2e_loop_evidence_rejects_orchestration(tmp_path):
    evidence = _result(tmp_path)["evidence"]
    evidence["orchestration_introduced"] = True

    validation = validate_e2e_loop_evidence(evidence)

    assert validation["valid"] is False
    assert any(error["field"] == "orchestration_introduced" for error in validation["errors"])
