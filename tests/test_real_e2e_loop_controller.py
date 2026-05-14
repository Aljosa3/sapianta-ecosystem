import json
import textwrap

from sapianta_bridge.real_e2e_codex_loop.e2e_loop_controller import run_real_e2e_codex_loop
from sapianta_bridge.real_e2e_codex_loop.e2e_loop_request import create_e2e_loop_request


def _write_codex(path, *, body=None):
    path.write_text(
        textwrap.dedent(
            body
            or """\
            #!/usr/bin/env python3
            import json
            import sys
            print(json.dumps({"status":"ok","argv":sys.argv[1:]}, sort_keys=True, separators=(",", ":")))
            """
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | 0o111)


def _request(tmp_path, *, authorized=True, timeout_seconds=30):
    codex = tmp_path / "codex"
    _write_codex(codex)
    return create_e2e_loop_request(
        chatgpt_request="execute governed validation",
        workspace_path=str(tmp_path),
        timeout_seconds=timeout_seconds,
        execution_authorized=authorized,
        approved_by="human",
        codex_executable=str(codex),
    ).to_dict()


def test_first_real_e2e_codex_loop_passes(tmp_path):
    request = _request(tmp_path)

    result = run_real_e2e_codex_loop(request=request)

    assert result["real_e2e_loop_status"] == "SUCCESS"
    response = result["response"]
    assert response["provider_id"] == "codex_cli"
    assert response["chatgpt_response_payload"]["interpretation_ready"] is True
    assert response["manual_copy_paste_required"] is False
    assert result["evidence"]["ingress_bound"] is True
    assert result["evidence"]["nl_to_envelope_bound"] is True
    assert result["evidence"]["execution_gate_bound"] is True
    assert result["evidence"]["bounded_codex_execution_bound"] is True
    assert result["evidence"]["result_return_bound"] is True
    assert result["evidence"]["orchestration_introduced"] is False
    stdout = result["runtime"]["bounded_execution"]["capture"]["stdout"]
    assert json.loads(stdout)["status"] == "ok"


def test_real_e2e_loop_blocks_unauthorized_execution(tmp_path):
    result = run_real_e2e_codex_loop(request=_request(tmp_path, authorized=False))

    assert result["real_e2e_loop_status"] == "BLOCKED"
    assert result["response"] == {}


def test_real_e2e_loop_blocks_workspace_escape(tmp_path):
    request = _request(tmp_path)
    request["workspace_path"] = str(tmp_path / "..")

    result = run_real_e2e_codex_loop(request=request)

    assert result["real_e2e_loop_status"] == "BLOCKED"


def test_real_e2e_loop_blocks_timeout_violation(tmp_path):
    request = _request(tmp_path, timeout_seconds=999)

    result = run_real_e2e_codex_loop(request=request)

    assert result["real_e2e_loop_status"] == "BLOCKED"
