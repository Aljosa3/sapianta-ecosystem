from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sapianta_system.runtime.codex_handoff import create_governed_codex_handoff, create_governed_codex_handoff_request
from sapianta_system.runtime.codex_synthesis import create_governed_codex_task_request, synthesize_governed_codex_task
from sapianta_system.runtime.execution_gate import (
    authorize_downstream_execution,
    create_execution_authorization_request,
    revoke_execution_authority,
)
from sapianta_system.runtime.execution_gate.governed_execution_authorization_validator import validate_authority_token
from sapianta_system.runtime.execution_gate.governed_execution_receipt import create_execution_receipt


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


def _authorization():
    return authorize_downstream_execution(
        create_execution_authorization_request(
            handoff_package=_handoff(),
            approved_by="human",
            approval_timestamp=APPROVAL_TIME,
        )
    )


def test_deterministic_authority_token_and_replay_identity():
    first = _authorization()
    second = _authorization()
    assert first["status"] == "AUTHORIZED"
    assert first["token_id"] == second["token_id"]
    assert first["replay_identity"] == second["replay_identity"]
    assert first["execution_window_seconds"] == 300


def test_authorization_expiration_and_reuse_reject():
    authorization = _authorization()
    expired_at = (datetime.fromisoformat(APPROVAL_TIME.replace("Z", "+00:00")) + timedelta(seconds=301)).astimezone(timezone.utc)
    assert validate_authority_token(authorization, now=expired_at.isoformat().replace("+00:00", "Z"))["valid"] is False
    assert validate_authority_token(
        authorization,
        now="2026-05-18T10:01:00Z",
        used_token_ids={authorization["token_id"]},
    )["valid"] is False


def test_malformed_mutated_and_escalated_authority_fail_closed():
    assert validate_authority_token({}, now="2026-05-18T10:01:00Z")["valid"] is False
    handoff = _handoff()
    request = create_execution_authorization_request(
        handoff_package=handoff,
        approved_by="human",
        approval_timestamp=APPROVAL_TIME,
    )
    request["handoff_package"]["codex_prompt"] = "mutated"
    assert authorize_downstream_execution(request)["status"] == "REJECTED"
    for field in ("shell_execution", "orchestration", "hidden_continuation"):
        handoff = deepcopy(_handoff())
        handoff[field] = True
        assert authorize_downstream_execution(
            create_execution_authorization_request(
                handoff_package=handoff,
                approved_by="human",
                approval_timestamp=APPROVAL_TIME,
            )
        )["status"] == "REJECTED"


def test_revocation_flow_and_receipts():
    authorization = _authorization()
    revoked = revoke_execution_authority(
        token=authorization,
        approval_chain=authorization["approval_chain"],
        revoked_at="2026-05-18T10:02:00Z",
    )
    assert revoked["status"] == "REVOKED"
    assert revoked["future_execution_valid"] is False
    assert revoked["receipt"]["authority_status"] == "REVOKED"
    expired = create_execution_receipt(
        token=authorization,
        authority_status="EXPIRED",
        approval_chain=authorization["approval_chain"],
    )
    assert expired["authority_status"] == "EXPIRED"


def test_replay_visible_approval_chain_and_receipt_generation():
    authorization = _authorization()
    assert [step["step"] for step in authorization["approval_chain"]] == [
        "HANDOFF_PACKAGE_VALIDATED",
        "EXPLICIT_HUMAN_APPROVAL",
        "TEMPORARY_AUTHORITY_TOKEN_ISSUED",
    ]
    assert authorization["receipt"]["authority_status"] == "AUTHORIZED"
    assert authorization["evidence"]["execution_receipts"][0]["token_id"] == authorization["token_id"]


def test_browser_companion_integration_and_no_execution():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'id="authorize"' in html
    assert 'const LOCAL_EXECUTION_AUTHORIZE_ENDPOINT = "http://127.0.0.1:8110/governed-execution-authorize";' in source
    assert "Exported handoff package is required before authorization." in source
    assert "Execution authorization does not execute Codex." in source
    assert "setInterval" not in source
