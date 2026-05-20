import json
from pathlib import Path

from agol_bridge.transport.local_governed_transport import (
    TRANSPORT_ACCEPTED,
    handle_local_governed_transport,
)


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"
FIXTURE = ROOT / ".github/governance/fixtures/semantic_proposal_v1.json"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def _fixture():
    return json.loads(FIXTURE.read_text())


def _transport_envelope():
    proposal = _fixture()
    return {
        "transport_id": "LOCAL-TRANSPORT-TEST",
        "session_id": "LOCAL-GOVERNED-TRANSPORT-SESSION-V1",
        "proposal_id": proposal["proposal_id"],
        "artifact_hash": proposal["artifact_hash"],
        "created_at_policy": "EXPLICIT_SIDE_PANEL_OPERATOR_TRIGGER",
        "source_label": "CHATGPT_LOCAL_ARTIFACT",
        "semantic_proposal": proposal,
        "authority_boundary_statement": (
            "Semantic transport only; transport success is not approval, not dispatch, "
            "not execution, and not continuation authority."
        ),
        "replay_policy": {
            "append_only": True,
            "visibility_only": True,
            "rewrite_allowed": False,
            "repair_allowed": False,
            "mutation_allowed": False,
            "inference_allowed": False,
            "durable_backend": False,
        },
        "lifecycle_policy": {
            "visibility_only": True,
            "execution_transition": False,
            "mutation_allowed": False,
        },
    }


def _session_registry():
    return {
        "LOCAL-GOVERNED-TRANSPORT-SESSION-V1": {
            "operator_visible": True,
            "ambiguous": False,
            "continuation_requested": False,
            "cross_session_mutation": False,
        }
    }


def test_explicit_operator_trigger_controls_exist():
    html = _html()

    assert 'id="local-transport-session-id"' in html
    assert 'value="LOCAL-GOVERNED-TRANSPORT-SESSION-V1"' in html
    assert 'id="attach-local-governed-transport"' in html
    assert "Attach Governed Transport" in html
    assert "Explicit operator-triggered attachment only" in html
    assert 'id="local-transport-runtime-status"' in html


def test_invocation_is_explicit_and_not_automatic():
    source = _js()

    assert "function attachLocalGovernedTransportFromSidepanel()" in source
    assert 'document.getElementById("attach-local-governed-transport")' in source
    assert "attachLocalGovernedTransportButton.onclick = attachLocalGovernedTransportFromSidepanel;" in source
    assert "handle_local_governed_transport({" in source
    assert "addEventListener" not in source
    assert "setInterval" not in source
    assert "setTimeout" not in source


def test_runtime_invocation_bridge_uses_explicit_session_binding():
    source = _js()

    assert 'const LOCAL_GOVERNED_TRANSPORT_SESSION_ID = "LOCAL-GOVERNED-TRANSPORT-SESSION-V1";' in source
    assert "function localTransportSessionRegistry(sessionId)" in source
    assert "session_id is missing or unknown" in source
    assert "session_attachment_visible" in source
    assert "cross_session_mutation: false" in source
    assert "automatic_ingestion: false" in source
    assert "hidden_invocation: false" in source
    assert "background_attach: false" in source


def test_python_runtime_accepts_certified_fixture_transport_envelope():
    report = handle_local_governed_transport(envelope=_transport_envelope(), session_registry=_session_registry())

    assert report["status"] == TRANSPORT_ACCEPTED
    assert report["session_id"] == "LOCAL-GOVERNED-TRANSPORT-SESSION-V1"
    assert report["proposal_id"] == _fixture()["proposal_id"]
    assert report["hash_verification_status"] == "HASH_VERIFIED"
    assert report["transport_event"]["visibility_scope"] == "SESSION_LOCAL_APPEND_CANDIDATE_ONLY"


def test_accepted_transport_rendering_is_visible():
    source = _js()

    assert "function localTransportRuntimeSummary(entry)" in source
    assert "transport_status:" in source
    assert "replay_event_id:" in source
    assert "session_id:" in source
    assert "proposal_id:" in source
    assert "authority_label:" in source
    assert "hash_status:" in source
    assert "append_candidate:" in source
    assert "non_authority_guarantees:" in source
    assert "setCockpitText(COCKPIT_IDS.localTransportRuntimeStatus, localTransportRuntimeSummary(latest));" in source


def test_rejected_transport_rendering_uses_compact_rejection_labels():
    source = _js()

    assert "function compactLocalTransportRejection(status)" in source
    assert 'TRANSPORT_REJECTED_SCHEMA: "SCHEMA_REJECTED"' in source
    assert 'TRANSPORT_REJECTED_HASH: "HASH_MISMATCH"' in source
    assert 'TRANSPORT_REJECTED_SESSION: "UNKNOWN_SESSION"' in source
    assert 'TRANSPORT_REJECTED_UNSAFE_MODE: "UNSAFE_MODE"' in source
    assert 'TRANSPORT_REJECTED_AUTHORITY: "AUTHORITY_REJECTED"' in source
    assert 'TRANSPORT_REJECTED_REPLAY_POLICY: "REPLAY_POLICY_REJECTED"' in source
    assert "compact_rejection:" in source


def test_replay_append_candidate_visibility_is_preserved():
    source = _js()

    assert 'visibility_scope: "SESSION_LOCAL_APPEND_CANDIDATE_ONLY"' in source
    assert "deterministicId(\"TRANSPORT-REPLAY\", eventSeed)" in source
    assert "replaySessionEntries.push(replaySessionEntry(canonicalSummary, replaySessionEntries.length));" in source
    assert "append_candidate:" in source


def test_no_endpoint_provider_execution_or_orchestration_behavior_is_added():
    lowered = _combined().lower()

    forbidden = (
        "governed-semantic-transport",
        "http://localhost",
        "http://127.0.0.1",
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "serviceworker",
        "runtime.onmessage",
        "tabs.onupdated",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "orchestrationruntime",
        "autonomouscontinuation",
    )
    for token in forbidden:
        assert token not in lowered


def test_no_durable_persistence_or_hidden_runtime_behavior_is_added():
    lowered = _combined().lower()

    forbidden = (
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
        "showdirectorypicker",
        "createwritestream",
        "writefile",
        "appendfile",
        "backgroundlistenerenabled",
        "hiddenbackgroundimportenabled",
    )
    for token in forbidden:
        assert token not in lowered
    assert "durable_persistence: false" in _js()
    assert "provider_dispatch: false" in _js()
    assert "approval: false" in _js()
    assert "execution: false" in _js()
    assert "orchestration: false" in _js()
