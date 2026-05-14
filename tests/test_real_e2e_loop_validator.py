from sapianta_bridge.real_e2e_codex_loop.e2e_loop_request import create_e2e_loop_request
from sapianta_bridge.real_e2e_codex_loop.e2e_loop_validator import validate_e2e_loop_request


def test_real_e2e_loop_validator_fails_closed_invalid_lineage(tmp_path):
    request = create_e2e_loop_request(
        chatgpt_request="execute governed validation",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        execution_authorized=True,
        approved_by="human",
        codex_executable=str(tmp_path / "codex"),
    ).to_dict()
    request["loop_identity"]["request_sha256"] = "mutated"

    validation = validate_e2e_loop_request(request)

    assert validation["valid"] is False
    assert any(error["field"] == "request_sha256" for error in validation["errors"])


def test_real_e2e_loop_validator_rejects_hidden_prompt_rewrite(tmp_path):
    request = create_e2e_loop_request(
        chatgpt_request="execute governed validation",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        execution_authorized=True,
        approved_by="human",
        codex_executable=str(tmp_path / "codex"),
    ).to_dict()
    request["hidden_prompt_rewriting_present"] = True

    validation = validate_e2e_loop_request(request)

    assert validation["valid"] is False
    assert any(error["field"] == "hidden_prompt_rewriting_present" for error in validation["errors"])
