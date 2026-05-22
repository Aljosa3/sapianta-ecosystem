import json
import subprocess
from copy import deepcopy
from pathlib import Path

from agol_bridge.runtime.minimal_end_to_end_bridge import BRIDGE_RESULT_ARTIFACT_TYPE
from agol_bridge.runtime.minimal_explicit_transport_path import (
    REQUEST_ARTIFACT_TYPE,
    REQUEST_AUTHORITY_BOUNDARY,
    REQUEST_SCHEMA_VERSION,
    TRANSPORT_PATH_EXPORTED,
    TRANSPORT_PATH_REJECTED_HASH,
    TRANSPORT_PATH_REJECTED_SCHEMA,
    create_minimal_governed_request_artifact,
    run_minimal_explicit_governed_transport_path,
    run_minimal_explicit_governed_transport_path_file,
)
from agol_bridge.transport.local_governed_transport import canonical_hash


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "agol_bridge" / "runtime" / "minimal_explicit_transport_path.py"
SCRIPT = ROOT / "scripts" / "run_minimal_bridge_transport.py"


def _hash_input(artifact: dict) -> dict:
    artifact_copy = deepcopy(artifact)
    artifact_copy.pop("artifact_hash", None)
    return artifact_copy


def _valid_request() -> dict:
    return create_minimal_governed_request_artifact(
        human_request="Review this explicit governed transport path.",
        session_id="SESSION-EXPLICIT-TRANSPORT-1",
    )


def _mock_codex(monkeypatch):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="explicit bounded codex complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_valid_governed_request_artifact_creates_canonical_result_artifact(monkeypatch, tmp_path):
    _mock_codex(monkeypatch)
    input_path = tmp_path / "governed_request.json"
    output_path = tmp_path / "bridge_result_artifact.json"
    request = _valid_request()
    input_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")

    report = run_minimal_explicit_governed_transport_path_file(
        input_path=input_path,
        output_path=output_path,
    )
    output_artifact = json.loads(output_path.read_text(encoding="utf-8"))

    assert report["status"] == TRANSPORT_PATH_EXPORTED
    assert report["output_path"] == str(output_path)
    assert report["output_artifact_created"] is True
    assert output_artifact == report["result_artifact"]
    assert output_artifact["artifact_type"] == BRIDGE_RESULT_ARTIFACT_TYPE
    assert output_artifact["session_id"] == "SESSION-EXPLICIT-TRANSPORT-1"
    assert output_artifact["governed_chat_return"]["status"] == "ACCEPTED"


def test_request_artifact_input_shape_is_explicit_and_hashed():
    request = _valid_request()

    assert request["artifact_type"] == REQUEST_ARTIFACT_TYPE
    assert request["schema_version"] == REQUEST_SCHEMA_VERSION
    assert request["authority_boundary_statement"] == REQUEST_AUTHORITY_BOUNDARY
    assert request["artifact_hash"] == canonical_hash(_hash_input(request))


def test_invalid_request_is_rejected_without_output_artifact():
    request = _valid_request()
    request.pop("human_request")

    report = run_minimal_explicit_governed_transport_path(request_artifact=request)

    assert report["status"] == TRANSPORT_PATH_REJECTED_SCHEMA
    assert report["output_artifact_created"] is False
    assert report["result_artifact"] == {}
    assert report["governed_return_artifact"]["status"] == "REJECTED"


def test_missing_session_is_rejected_fail_closed(tmp_path):
    request = _valid_request()
    request["session_id"] = ""
    request["artifact_hash"] = canonical_hash(_hash_input(request))
    input_path = tmp_path / "governed_request.json"
    output_path = tmp_path / "bridge_result_artifact.json"
    input_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")

    report = run_minimal_explicit_governed_transport_path_file(
        input_path=input_path,
        output_path=output_path,
    )

    assert report["status"] == TRANSPORT_PATH_REJECTED_SCHEMA
    assert report["output_artifact_created"] is False
    assert not output_path.exists()
    assert "session_id is required" in report["request_validation"]["errors"]


def test_artifact_hash_mismatch_is_rejected():
    request = _valid_request()
    request["human_request"] = "Tampered after hash generation."

    report = run_minimal_explicit_governed_transport_path(request_artifact=request)

    assert report["status"] == TRANSPORT_PATH_REJECTED_HASH
    assert report["request_validation"]["hash_verified"] is False
    assert report["result_artifact"] == {}


def test_output_artifact_is_deterministic(monkeypatch, tmp_path):
    _mock_codex(monkeypatch)
    request = _valid_request()
    input_path = tmp_path / "governed_request.json"
    first_output = tmp_path / "first_bridge_result_artifact.json"
    second_output = tmp_path / "second_bridge_result_artifact.json"
    input_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")

    first = run_minimal_explicit_governed_transport_path_file(input_path=input_path, output_path=first_output)
    second = run_minimal_explicit_governed_transport_path_file(input_path=input_path, output_path=second_output)

    assert first["status"] == TRANSPORT_PATH_EXPORTED
    assert second["status"] == TRANSPORT_PATH_EXPORTED
    assert first["result_artifact"] == second["result_artifact"]
    assert first_output.read_text(encoding="utf-8") == second_output.read_text(encoding="utf-8")
    assert first["result_artifact"]["artifact_hash"] == canonical_hash(_hash_input(first["result_artifact"]))


def test_bounded_provider_execution_without_dispatch_approval_or_orchestration(tmp_path, monkeypatch):
    _mock_codex(monkeypatch)
    request = _valid_request()
    input_path = tmp_path / "governed_request.json"
    output_path = tmp_path / "bridge_result_artifact.json"
    input_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")

    report = run_minimal_explicit_governed_transport_path_file(
        input_path=input_path,
        output_path=output_path,
    )
    guarantees = report["authority_guarantees"]
    codex_result = report["result_artifact"]["codex_cli_result"]

    assert guarantees["provider_calls"] == "CODEX_CLI_ONLY"
    assert guarantees["dispatch"] is False
    assert guarantees["approval"] is False
    assert guarantees["execution"] == "BOUNDED_CODEX_CLI_ONLY"
    assert guarantees["orchestration"] is False
    assert guarantees["autonomous_continuation"] is False
    assert codex_result["provider_invoked"] is True
    assert codex_result["execution_authority_created"] is False
    assert codex_result["orchestration_created"] is False


def test_source_has_no_endpoint_server_listener_or_hidden_transport():
    source = "\n".join((MODULE.read_text(encoding="utf-8"), SCRIPT.read_text(encoding="utf-8"))).lower()

    forbidden = (
        "threadinghttpserver",
        "httpserver",
        "serve_forever",
        "socket",
        "requests.",
        "urllib",
        "websocket",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "orchestrationruntime",
        "autonomouscontinuation",
        "watchdog",
        "while true",
    )
    for token in forbidden:
        assert token not in source


def test_cli_is_explicit_file_path_only():
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'parser.add_argument("input_path"' in source
    assert 'parser.add_argument("output_path"' in source
    assert "run_minimal_explicit_governed_transport_path_file" in source
    assert "print(json.dumps(report" in source
