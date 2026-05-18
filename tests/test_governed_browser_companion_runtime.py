import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _manifest():
    return json.loads((COMPANION / "manifest.json").read_text())


def _popup_js():
    return (COMPANION / "popup.js").read_text()


def test_manifest_uses_minimal_localhost_only_permissions():
    manifest = _manifest()
    assert "permissions" not in manifest
    assert manifest["host_permissions"] == ["http://127.0.0.1:8110/*"]
    assert "<all_urls>" not in json.dumps(manifest)


def test_localhost_only_endpoint_is_enforced_in_popup_contract():
    source = _popup_js()
    assert 'const LOCAL_ENDPOINT = "http://127.0.0.1:8110/governed-invoke";' in source
    assert "0.0.0.0" not in source


def test_artifact_validation_rejects_unsafe_shapes():
    source = _popup_js()
    assert "^[A-Z0-9_-]{1,96}$" in source
    pattern = re.compile(r"^[A-Z0-9_-]{1,96}$")
    assert pattern.fullmatch("TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1")
    for unsafe in ("", "contains space", "slash/name", "http://example.com", '{"x":1}', "A" * 97):
        assert pattern.fullmatch(unsafe) is None


def test_request_builder_is_deterministic_and_bounded():
    source = _popup_js()
    assert "async function buildGovernedRequest" in source
    assert "OPERATOR-GOVERNED-SESSION" in source
    assert "PREVIEW-RUNTIME-REQUEST-" in source
    assert "bounded: true" in source
    assert "canonicalize" in source


def test_response_validator_accepts_only_returned_pass_shape():
    source = _popup_js()
    assert 'response.status === "RETURNED"' in source
    assert 'response.closure === "PASS"' in source
    assert "evidence.localhost_only === true" in source
    assert "evidence.replay_safe === true" in source
    assert "evidence.response_returned === true" in source


def test_response_validator_rejects_hidden_execution():
    assert "evidence.hidden_execution_present === false" in _popup_js()


def test_no_retry_fallback_or_hidden_automation_surface_exists():
    combined = "\n".join(path.read_text() for path in COMPANION.glob("*") if path.is_file())
    lowered = combined.lower()
    assert "retry" not in lowered
    assert "fallback" not in lowered
    assert "content_scripts" not in lowered
    assert "cookies" not in lowered
    assert "nativeMessaging" not in combined


def test_explicit_user_action_is_required():
    html = (COMPANION / "popup.html").read_text()
    source = _popup_js()
    assert 'id="invoke"' in html
    assert 'addEventListener("click", invokeGovernedRuntime)' in source
