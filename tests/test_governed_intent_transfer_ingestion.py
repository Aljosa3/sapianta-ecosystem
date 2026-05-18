from copy import deepcopy
from pathlib import Path

from sapianta_system.runtime.chatgpt_bridge_v2 import bridge_chatgpt_conversation, create_chatgpt_bridge_request
from sapianta_system.runtime.intent_transfer import create_governed_intent_transfer, create_intent_transfer_request
from sapianta_system.runtime.intent_transfer_ingestion import (
    create_intent_transfer_ingestion_request,
    ingest_governed_intent_transfer,
)
from sapianta_system.runtime.preview.governed_preview_runtime_validator import validate_preview_binding


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_STATEMENT = "Governed transfer ingestion validates transfer admissibility but does not grant execution authority."


def _package():
    bridge = bridge_chatgpt_conversation(create_chatgpt_bridge_request(conversational_input="prepare finalize milestone"))
    transfer = create_governed_intent_transfer(
        create_intent_transfer_request(
            conversational_input="prepare finalize milestone",
            normalized_governed_request=bridge["normalized_request"],
            governance_mode=bridge["governance_mode"],
            replay_identity=bridge["replay_identity"],
        )
    )
    return transfer["package"]


def _ingest(package=None, **overrides):
    package = _package() if package is None else package
    request = create_intent_transfer_ingestion_request(
        transfer_package=package,
        replay_identity=overrides.pop("replay_identity", package.get("replay_identity", "")),
        transfer_identity=overrides.pop("transfer_identity", package.get("transfer_identity", "")),
    )
    return ingest_governed_intent_transfer(request)


def test_deterministic_ingestion_receipt_generation_and_identity_stability():
    first = _ingest()
    second = _ingest()
    assert first["ingestion_status"] == "INGESTED_PREVIEW_READY"
    assert first["ingestion_identity"] == second["ingestion_identity"]
    assert first["replay_identity"] == second["replay_identity"]
    assert first["timeline_state"] == ["TRANSFER_VALIDATED", "REPLAY_CONTINUITY_VALIDATED", "PREVIEW_READY"]


def test_preview_confirmation_and_no_authority_are_preserved():
    result = _ingest()
    assert result["preview_required"] is True
    assert result["confirmation_required"] is True
    assert result["authority_validated"] is True
    assert result["authority_granted"] is False
    assert result["ingestion_boundary_statement"] == BOUNDARY_STATEMENT


def test_replay_and_transfer_identity_continuity_fail_closed():
    package = _package()
    assert _ingest(package, replay_identity="MISMATCH")["ingestion_status"] == "BLOCKED"
    assert _ingest(package, transfer_identity="MISMATCH")["ingestion_status"] == "BLOCKED"


def test_blocked_ingestion_escalations_fail_closed():
    cases = []
    for field in ("execution_authority", "chatgpt_authority"):
        package = deepcopy(_package())
        package[field] = True
        cases.append(package)
    for field in ("automatic_dispatch", "orchestration", "hidden_continuation"):
        package = deepcopy(_package())
        package["boundary_state"][field] = True
        cases.append(package)
    package = deepcopy(_package())
    package["requires_preview"] = False
    cases.append(package)
    package = deepcopy(_package())
    package["requires_confirmation"] = False
    cases.append(package)
    package = deepcopy(_package())
    package["blocked_capabilities"] = []
    cases.append(package)
    for package in cases:
        assert _ingest(package)["ingestion_status"] == "BLOCKED"


def test_replay_visibility_and_boundary_state():
    result = _ingest()
    evidence = result["evidence"]
    assert evidence["transfer_package"]["transfer_identity"] == result["transfer_identity"]
    assert evidence["ingestion_identity"] == result["ingestion_identity"]
    assert evidence["ingestion_validation_outcome"]["valid"] is True
    assert result["boundary_state"] == {
        "chatgpt_authority": False,
        "execution_authority": False,
        "authority_granted": False,
        "automatic_dispatch": False,
        "orchestration": False,
        "hidden_continuation": False,
        "preview_required": True,
        "confirmation_required": True,
        "ingestion_boundary_statement": BOUNDARY_STATEMENT,
    }


def test_browser_companion_integration_and_localhost_only_endpoint():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'id="transfer-ingest"' in html
    assert 'const LOCAL_INTENT_TRANSFER_INGEST_ENDPOINT = "http://127.0.0.1:8110/governed-intent-transfer-ingest";' in source
    assert "Exported governed transfer package is required before ingestion." in source
    assert BOUNDARY_STATEMENT in source
    assert validate_preview_binding(host="127.0.0.1")["valid"] is True
    assert validate_preview_binding(host="0.0.0.0")["valid"] is False


def test_fail_closed_malformed_package_and_no_execution_path():
    assert _ingest({})["ingestion_status"] == "BLOCKED"
    package = ROOT / "sapianta_system/runtime/intent_transfer_ingestion"
    source = "\n".join(path.read_text() for path in package.glob("*.py"))
    assert "execute_governed_codex" not in source
    assert "subprocess" not in source
