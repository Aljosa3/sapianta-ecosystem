import json
import textwrap

from sapianta_bridge.interaction_ingress_egress.ingress_request import create_local_ingress_request
from sapianta_bridge.no_copy_paste_validation.no_copy_paste_validation_controller import run_no_copy_paste_validation
from sapianta_bridge.no_copy_paste_validation.no_copy_paste_validation_request import create_validation_request


def _codex(tmp_path):
    path = tmp_path / "codex"
    path.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import sys
        print("SAPIANTA_CODEX_VALIDATION_OK AIGOL_TASK_COMPLETE")
    """), encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)
    return path


def _ingress(tmp_path):
    artifact = create_local_ingress_request(
        "Inspect governance evidence",
        execution_gate_id="PREBOUND-GATE",
        bounded_runtime_id="PREBOUND-RUNTIME",
        result_capture_id="PREBOUND-CAPTURE",
    ).to_dict()
    path = tmp_path / "ingress.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


def test_no_copy_paste_flow_executes_single_bounded_result(tmp_path):
    egress = tmp_path / "egress.json"
    result = run_no_copy_paste_validation(create_validation_request(ingress_path=_ingress(tmp_path), egress_path=egress, workspace_path=tmp_path, codex_executable=_codex(tmp_path)))
    assert result["validation"]["valid"] is True
    assert result["response"]["status"] == "FIRST_OPERATIONAL_NO_COPY_PASTE_GOVERNED_FLOW"
    assert result["execution"]["capture"]["bounded_result_captured"] is True
    assert egress.exists()
    assert result["manual_prompt_relay_present"] is False


def test_no_copy_paste_flow_blocks_missing_lineage(tmp_path):
    path = _ingress(tmp_path)
    artifact = json.loads(path.read_text())
    artifact["result_capture_id"] = ""
    path.write_text(json.dumps(artifact), encoding="utf-8")
    result = run_no_copy_paste_validation(create_validation_request(ingress_path=path, egress_path=tmp_path / "egress.json", workspace_path=tmp_path, codex_executable=_codex(tmp_path)))
    assert result["validation"]["valid"] is False
    assert result["status"] == "BLOCKED"


def test_no_copy_paste_flow_uses_one_egress_artifact(tmp_path):
    egress = tmp_path / "egress.json"
    run_no_copy_paste_validation(create_validation_request(ingress_path=_ingress(tmp_path), egress_path=egress, workspace_path=tmp_path, codex_executable=_codex(tmp_path)))
    assert [path.name for path in tmp_path.glob("egress*.json")] == ["egress.json"]
