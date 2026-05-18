from copy import deepcopy
from pathlib import Path

from sapianta_system.runtime.codex_handoff import create_governed_codex_handoff, create_governed_codex_handoff_request
from sapianta_system.runtime.codex_synthesis import create_governed_codex_task_request, synthesize_governed_codex_task
from sapianta_system.runtime.execution_consumer import consume_execution_authority, create_execution_consumer_request
from sapianta_system.runtime.execution_gate import authorize_downstream_execution, create_execution_authorization_request


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


def _consume(**overrides):
    handoff = overrides.pop("handoff_package", _handoff())
    authority = overrides.pop("authority_token", _authority())
    request = create_execution_consumer_request(
        handoff_package=handoff,
        authority_token=authority,
        now=overrides.pop("now", "2026-05-18T10:01:00Z"),
        revoked_token_ids=overrides.pop("revoked_token_ids", set()),
    )
    return consume_execution_authority(request)


def test_deterministic_mock_dispatch_and_replay_identity():
    first = _consume()
    second = _consume()
    assert first["status"] == "MOCK_EXECUTION_ACCEPTED"
    assert first["dispatch"] == {
        "dispatch_status": "MOCK_DISPATCH_ACCEPTED",
        "dispatch_mode": "DETERMINISTIC_PRE_EXECUTION_SIMULATION",
        "execution_performed": False,
    }
    assert first["replay_identity"] == second["replay_identity"]


def test_authority_expiration_and_revocation_reject():
    assert _consume(now="2026-05-18T10:05:01Z")["status"] == "AUTHORITY_EXPIRED"
    authority = _authority()
    assert _consume(authority_token=authority, revoked_token_ids={authority["token_id"]})["status"] == "AUTHORITY_REVOKED"


def test_replay_or_integrity_mismatch_rejects():
    handoff = deepcopy(_handoff())
    handoff["codex_prompt"] = "mutated"
    assert _consume(handoff_package=handoff)["status"] == "HANDOFF_MISMATCH"


def test_blocked_capability_mutations_reject():
    for field in ("orchestration", "shell_execution", "hidden_continuation"):
        handoff = deepcopy(_handoff())
        handoff[field] = True
        assert _consume(handoff_package=handoff)["status"] in {"HANDOFF_MISMATCH", "BLOCKED_CAPABILITY_DETECTED"}


def test_receipt_generation_enforces_execution_performed_false():
    result = _consume()
    assert result["receipt"]["execution_performed"] is False
    assert result["receipt"]["constitutional_statement"] == (
        "Mock execution authorization consumption does not constitute downstream execution."
    )
    assert result["evidence"]["mock_dispatch_receipt"]["receipt_id"] == result["receipt"]["receipt_id"]


def test_browser_companion_integration_and_no_codex_or_subprocess():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'id="consume"' in html
    assert 'const LOCAL_EXECUTION_CONSUME_ENDPOINT = "http://127.0.0.1:8110/governed-execution-consume";' in source
    assert "Authorization is required before mock execution consumption." in source
    assert "Mock execution consumer failed governed validation." in source
    assert "subprocess" not in source
    assert "codex api" not in source.lower()
