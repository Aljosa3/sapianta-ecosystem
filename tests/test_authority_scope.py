from sapianta_bridge.envelopes.authority_scope import (
    authority_scope_rules,
    validate_authority_scope,
)


def test_valid_authority_scope_passes() -> None:
    result = validate_authority_scope(["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"])

    assert result["valid"] is True
    assert result["implicit_authority_allowed"] is False


def test_undefined_authority_fails_closed() -> None:
    result = validate_authority_scope(["ROOT_ACCESS", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"])

    assert result["valid"] is False
    assert {"field": "authority_scope", "reason": "undefined authority scope: ROOT_ACCESS"} in result["errors"]


def test_required_deny_scope_missing_fails_closed() -> None:
    result = validate_authority_scope(["READ_ONLY", "NO_NETWORK"])

    assert result["valid"] is False
    assert {
        "field": "authority_scope",
        "reason": "required deny scope missing: NO_PRIVILEGE_ESCALATION",
    } in result["errors"]


def test_conflicting_authority_scope_fails_closed() -> None:
    result = validate_authority_scope(
        ["READ_ONLY", "PATCH_EXISTING_FILES", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"]
    )

    assert result["valid"] is False
    assert {
        "field": "authority_scope",
        "reason": "conflicting authority scopes: READ_ONLY/PATCH_EXISTING_FILES",
    } in result["errors"]


def test_authority_rules_forbid_implicit_authority() -> None:
    rules = authority_scope_rules()

    assert rules["undefined_authority_policy"] == "FAIL_CLOSED"
    assert rules["implicit_authority_allowed"] is False
