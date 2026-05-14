from sapianta_bridge.providers.provider_identity import (
    create_provider_identity,
    normalize_provider_id,
    validate_provider_identity,
)


def test_provider_identity_normalization_is_deterministic() -> None:
    assert normalize_provider_id("Claude-Code") == "claude_code"


def test_provider_identity_is_replay_safe_and_non_authoritative() -> None:
    identity = create_provider_identity("codex", "REMOTE_LLM")
    result = validate_provider_identity(identity)

    assert result["valid"] is True
    assert result["provider_identity_affects_governance"] is False
    assert result["provider_identity_affects_validation"] is False
    assert result["provider_identity_affects_replay"] is False


def test_provider_identity_rejects_unnormalized_id() -> None:
    result = validate_provider_identity({"provider_id": "Codex", "provider_type": "REMOTE_LLM"})

    assert result["valid"] is False
    assert {"field": "provider_id", "reason": "provider_id must be normalized"} in result["errors"]
