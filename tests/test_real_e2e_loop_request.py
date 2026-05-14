from sapianta_bridge.real_e2e_codex_loop.e2e_loop_request import create_e2e_loop_request
from sapianta_bridge.real_e2e_codex_loop.e2e_loop_validator import validate_e2e_loop_request


def test_real_e2e_loop_request_requires_codex_cli_and_authorization(tmp_path):
    request = create_e2e_loop_request(
        chatgpt_request="execute governed validation",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        execution_authorized=True,
        approved_by="human",
        codex_executable=str(tmp_path / "codex"),
    ).to_dict()

    assert request["provider_id"] == "codex_cli"
    assert request["manual_copy_paste_required"] is False
    assert validate_e2e_loop_request(request)["valid"] is True


def test_real_e2e_loop_request_blocks_unauthorized_execution(tmp_path):
    request = create_e2e_loop_request(
        chatgpt_request="execute governed validation",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        execution_authorized=False,
        approved_by="human",
    ).to_dict()

    validation = validate_e2e_loop_request(request)

    assert validation["valid"] is False
    assert any(error["field"] == "execution_authorized" for error in validation["errors"])


def test_real_e2e_loop_request_blocks_provider_mismatch(tmp_path):
    request = create_e2e_loop_request(
        chatgpt_request="execute governed validation",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        execution_authorized=True,
        approved_by="human",
        provider_id="codex",
    ).to_dict()

    validation = validate_e2e_loop_request(request)

    assert validation["valid"] is False
    assert any(error["field"] == "provider_id" for error in validation["errors"])
