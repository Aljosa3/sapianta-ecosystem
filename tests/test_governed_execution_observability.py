from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from sapianta_system.runtime.codex_execution_adapter import create_codex_execution_request, execute_governed_codex
from sapianta_system.runtime.codex_handoff import create_governed_codex_handoff, create_governed_codex_handoff_request
from sapianta_system.runtime.codex_synthesis import create_governed_codex_task_request, synthesize_governed_codex_task
from sapianta_system.runtime.execution_consumer import consume_execution_authority, create_execution_consumer_request
from sapianta_system.runtime.execution_gate import authorize_downstream_execution, create_execution_authorization_request
from sapianta_system.runtime.execution_observability import create_execution_observability_request, observe_governed_execution


ROOT = Path(__file__).resolve().parents[1]
APPROVAL_TIME = "2026-05-18T10:00:00Z"


def _handoff():
    synthesis = synthesize_governed_codex_task(
        create_governed_codex_task_request(natural_language="prepare finalize milestone for replay validation")
    )
    return create_governed_codex_handoff(
        create_governed_codex_handoff_request(
            synthesis_response=synthesis,
            original_human_request="prepare finalize milestone for replay validation",
        )
    )


def _authority():
    return authorize_downstream_execution(
        create_execution_authorization_request(
            handoff_package=_handoff(),
            approved_by="human",
            approval_timestamp=APPROVAL_TIME,
        )
    )


def _consumer(handoff, authority):
    return consume_execution_authority(
        create_execution_consumer_request(
            handoff_package=handoff,
            authority_token=authority,
            now="2026-05-18T10:01:00Z",
        )
    )


def _adapter(handoff, authority):
    def runner(*_args, **_kwargs):
        return SimpleNamespace(returncode=0, stdout="out", stderr="err")

    return execute_governed_codex(
        create_codex_execution_request(
            handoff_package=handoff,
            authority_token=authority,
            now="2026-05-18T10:01:00Z",
        ),
        runner=runner,
    )


def _observe(**overrides):
    handoff = overrides.pop("handoff_package", _handoff())
    authority = overrides.pop("authority_token", _authority())
    consumer = overrides.pop("consumer_response", _consumer(handoff, authority))
    adapter = overrides.pop("adapter_response", _adapter(handoff, authority))
    request = create_execution_observability_request(
        handoff_package=handoff,
        authority_token=authority,
        consumer_response=consumer,
        adapter_response=adapter,
        now=overrides.pop("now", "2026-05-18T10:01:00Z"),
        revoked_token_ids=overrides.pop("revoked_token_ids", set()),
    )
    return observe_governed_execution(request)


def test_observability_is_read_only_and_deterministic():
    first = _observe()
    second = _observe()
    assert first["status"] == "OBSERVED"
    assert first["read_only"] is True
    assert first["execution_triggered"] is False
    assert first["trace"]["execution_trace_id"] == second["trace"]["execution_trace_id"]
    assert first["trace"]["replay_identity"] == second["trace"]["replay_identity"]


def test_authority_receipts_and_hashes_are_inspected():
    result = _observe()
    trace = result["trace"]
    assert trace["authority_token_id"].startswith("EXEC-AUTH-")
    assert trace["consumer_receipt_status"] == "MOCK_EXECUTION_ACCEPTED"
    assert trace["adapter_receipt_status"] == "EXECUTION_ACCEPTED"
    assert trace["stdout_hash"]
    assert trace["stderr_hash"]
    assert result["summary"]["blocked_capabilities"]


def test_revoked_and_expired_states_are_visible():
    authority = _authority()
    assert _observe(authority_token=authority, now="2026-05-18T10:05:01Z")["trace"]["expiration_status"] == "EXPIRED"
    assert _observe(authority_token=authority, revoked_token_ids={authority["token_id"]})["trace"]["revocation_status"] == "REVOKED"


def test_malformed_trace_fails_closed():
    handoff = _handoff()
    authority = _authority()
    consumer = _consumer(handoff, authority)
    malformed = deepcopy(_adapter(handoff, authority))
    malformed.pop("receipt")
    result = _observe(
        handoff_package=handoff,
        authority_token=authority,
        consumer_response=consumer,
        adapter_response=malformed,
    )
    assert result["status"] == "BLOCKED"
    assert result["execution_triggered"] is False


def test_browser_companion_integration_and_no_execution_trigger():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'id="observe"' in html
    assert 'const LOCAL_EXECUTION_OBSERVE_ENDPOINT = "http://127.0.0.1:8110/governed-execution-observe";' in source
    assert "Completed governed execution receipts are required before inspection." in source
    assert "execution_triggered" in source


def test_observability_module_contains_no_subprocess_or_codex_dispatch():
    package = ROOT / "sapianta_system/runtime/execution_observability"
    source = "\n".join(path.read_text() for path in package.glob("*.py"))
    assert "subprocess" not in source
    assert "execute_governed_codex" not in source
