import hashlib
import json
from pathlib import Path


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


def _canonical_hash(value):
    copied = json.loads(json.dumps(value))
    copied.pop("artifact_hash", None)
    encoded = json.dumps(copied, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def test_valid_fixture_hash_is_accepted_by_canonical_semantics():
    fixture = _fixture()

    assert fixture["artifact_hash"] == _canonical_hash(fixture)
    assert fixture["proposed_mode"] == "REVIEW_ONLY"
    assert fixture["certification"]["certification_status"] == "CERTIFIED_FOR_CONTINUITY_INGESTION"
    assert fixture["certification"]["approved"] is False
    assert fixture["certification"]["dispatchable"] is False
    assert fixture["certification"]["executable"] is False


def test_hash_verification_ui_renders_integrity_status():
    html = _html()

    assert "Semantic Proposal Hash Verification" in html
    assert 'id="semantic-proposal-hash-verification-status"' in html
    assert "HASH VERIFIED is not approval, dispatch, execution, or continuation authority" in html


def test_hash_recomputation_excludes_artifact_hash_and_uses_sha256():
    source = _js()

    assert "function semanticProposalHashInput(proposal)" in source
    assert "const { artifact_hash: artifactHash, ...hashInput } = canonicalProposal;" in source
    assert "JSON.stringify(semanticProposalHashInput(proposal))" in source
    assert 'crypto.subtle.digest("SHA-256", bytes)' in source
    assert "`sha256:${Array.from(new Uint8Array(digest))" in source


def test_mismatched_hash_missing_hash_and_malformed_hash_are_rejected():
    source = _js()

    assert 'status: "HASH_MISMATCH"' in source
    assert 'errors: ["artifact_hash mismatch"]' in source
    assert 'status: "HASH_MISSING"' in source
    assert 'errors: ["missing artifact_hash"]' in source
    assert 'status: "HASH_INVALID"' in source
    assert 'errors: ["malformed artifact_hash"]' in source
    assert "hashVerification.status !== \"HASH_VERIFIED\"" in source
    assert "errors.push(...hashVerification.errors)" in source


def test_malformed_canonical_structure_is_rejected():
    source = _js()

    assert "malformed canonical structure" in source
    assert "!proposal || typeof proposal !== \"object\" || Array.isArray(proposal)" in source
    assert "replay_safe_integrity: false" in source


def test_artifact_is_not_mutated_or_rewritten():
    source = _js()

    assert "const canonicalProposal = canonicalize(proposal);" in source
    assert "const { artifact_hash: artifactHash, ...hashInput } = canonicalProposal;" in source
    forbidden = (
        "delete proposal.artifact_hash",
        "proposal.artifact_hash =",
        "validation.proposal.artifact_hash =",
        "artifact_hash: computedHash",
        "hash repair",
        "repairHash",
        "rewriteArtifact",
        "normalizeArtifact",
    )
    for token in forbidden:
        assert token not in source


def test_hash_verification_result_is_deterministically_rendered():
    source = _js()

    assert "function semanticProposalHashVerificationSummary(entry)" in source
    assert "`status: ${compactValue(verification.status)}`" in source
    assert "`artifact_hash: ${compactValue(verification.artifact_hash)}`" in source
    assert "`computed_hash: ${compactValue(verification.computed_hash)}`" in source
    assert "`artifact_identity: ${compactValue(verification.artifact_identity)}`" in source
    assert "semanticProposalHashVerificationSummary(latest)" in source
    assert "node.textContent = value;" in source
    assert "innerHTML" not in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source


def test_no_replay_rewrite_provider_dispatch_approval_or_execution_path_is_added():
    lowered = _combined().lower()
    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
        "append_replay",
        "mutatereplay",
        "rewritereplay",
        "repairreplay",
        "transitionlifecycle",
        "setinterval",
        "settimeout",
    )
    for token in forbidden:
        assert token not in lowered
    assert "provider_calls: false" in _js()
    assert "dispatch: false" in _js()
    assert "approval: false" in _js()
    assert "execution: false" in _js()
