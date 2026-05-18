from __future__ import annotations

import http.client
import json
import threading
from copy import deepcopy

import pytest

from sapianta_system.runtime.preview import (
    create_local_preview_server,
    create_preview_runtime_request,
    handle_preview_invoke,
)
from sapianta_system.runtime.preview.governed_preview_runtime_replay import validate_preview_response_replay


def _lineage():
    return {
        "governed_session_id": "GOV-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_operation_envelope_id": "ENV-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _payload(**overrides):
    value = {
        "interaction_identity": "LOCALHOST-INTERACTION-1",
        "interaction_payload": {
            "interaction_intent": "run bounded validation",
            "connector_name": "local_execution",
            "request_payload": {"operation_intent": "run bounded validation", "authorized_execution": True},
            "hidden_continuation_present": False,
            "orchestration_present": False,
            "hidden_routing_present": False,
            "hidden_execution_present": False,
            "hidden_mutable_state_present": False,
        },
    }
    value.update(overrides)
    return value


def _request(**payload_overrides):
    return create_preview_runtime_request(request_payload=_payload(**payload_overrides), lineage=_lineage())


def _activation(authorized=True):
    return {
        "validation": {"valid": True},
        "runtime_activation_gate_binding": {"runtime_activation_gate_id": "GATE-1", "activation_authorized": authorized},
    }


def _operation():
    return {"validation": {"valid": True}, "runtime_operation_evidence": {"runtime_operation_envelope_id": "ENV-1"}}


def _surface(runtime_surface="GOVERNED_PYTEST_RUNTIME_SURFACE"):
    return {
        "validation": {"valid": True},
        "runtime_execution_surface_evidence": {
            "runtime_execution_surface_id": "SURFACE-1",
            "runtime_surface": runtime_surface,
        },
    }


def _transport_lineage():
    return {
        "runtime_activation_gate_id": "GATE-1",
        "runtime_operation_envelope_id": "ENV-1",
        "runtime_execution_surface_id": "SURFACE-1",
        "execution_exchange_session_id": "EXCHANGE-1",
        "execution_relay_session_id": "RELAY-1",
        "runtime_execution_commit_id": "COMMIT-1",
        "response_return_id": "RETURN-1",
    }


def _handle(request=None, **overrides):
    return handle_preview_invoke(
        request=request or _request(),
        host=overrides.pop("host", "127.0.0.1"),
        port=overrides.pop("port", 8010),
        activation_output=overrides.pop("activation_output", _activation()),
        operation_output=overrides.pop("operation_output", _operation()),
        surface_output=overrides.pop("surface_output", _surface()),
        transport_lineage=overrides.pop("transport_lineage", _transport_lineage()),
    )


def test_successful_localhost_invocation_returns_governed_response():
    result = _handle()
    assert result["status"] == "RETURNED"
    assert result["closure"] == "PASS"
    assert result["evidence"]["localhost_only"] is True
    assert result["evidence"]["response_returned"] is True


def test_response_identity_is_deterministic_and_replay_visible():
    first = _handle()
    second = _handle()
    assert first["preview_runtime_response_id"] == second["preview_runtime_response_id"]
    assert first["evidence"] == second["evidence"]
    assert validate_preview_response_replay(response=first, request=_request())["read_only"] is True


def test_invalid_payload_fails_closed():
    broken = _request(interaction_identity="")
    assert _handle(request=broken)["status"] == "BLOCKED"


def test_replay_mismatch_fails_closed():
    broken = deepcopy(_request())
    broken["replay_identity"] = "MISMATCH"
    assert _handle(request=broken)["status"] == "BLOCKED"


def test_hidden_continuation_and_invalid_surface_fail_closed():
    payload = _payload()
    payload["interaction_payload"]["hidden_continuation_present"] = True
    request = create_preview_runtime_request(request_payload=payload, lineage=_lineage())
    assert _handle(request=request)["status"] == "BLOCKED"
    assert _handle(surface_output=_surface("GOVERNED_ARTIFACT_WRITE_SURFACE"))["status"] == "BLOCKED"


def test_lifecycle_closure_is_deterministic():
    first = _handle()
    second = _handle()
    assert first["runtime_closure"]["preview_runtime_closure_id"] == second["runtime_closure"]["preview_runtime_closure_id"]
    assert first["runtime_closure"]["closure"] == "PASS"


def test_localhost_only_binding_is_enforced():
    assert _handle(host="0.0.0.0")["status"] == "BLOCKED"
    with pytest.raises(ValueError):
        create_local_preview_server(host="0.0.0.0", port=8010)


def test_real_localhost_post_invocation():
    server = create_local_preview_server(host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
    body = json.dumps(_request(), sort_keys=True, separators=(",", ":"))
    conn.request("POST", "/governed-invoke", body=body, headers={"Content-Type": "application/json"})
    response = conn.getresponse()
    payload = json.loads(response.read().decode("utf-8"))
    conn.close()
    thread.join(timeout=5)
    server.server_close()
    assert response.status == 200
    assert payload["status"] == "RETURNED"
    assert payload["closure"] == "PASS"
