from sapianta_bridge.envelopes.workspace_scope import (
    normalize_workspace_path,
    validate_workspace_scope,
    workspace_scope,
)


def test_workspace_scope_passes_for_bounded_roots() -> None:
    scope = workspace_scope(["sapianta_bridge"], forbidden_roots=[".git"])
    result = validate_workspace_scope(scope)

    assert result["valid"] is True
    assert result["workspace_escape_allowed"] is False
    assert result["self_expansion_allowed"] is False


def test_workspace_scope_rejects_absolute_path() -> None:
    result = validate_workspace_scope({"allowed_roots": ["/tmp/outside"], "forbidden_roots": []})

    assert result["valid"] is False
    assert {"field": "workspace_scope.allowed_roots", "reason": "unsafe path: /tmp/outside"} in result["errors"]


def test_workspace_scope_rejects_parent_escape() -> None:
    result = validate_workspace_scope({"allowed_roots": ["../outside"], "forbidden_roots": []})

    assert result["valid"] is False
    assert {"field": "workspace_scope.allowed_roots", "reason": "unsafe path: ../outside"} in result["errors"]


def test_workspace_scope_rejects_allowed_and_forbidden_overlap() -> None:
    result = validate_workspace_scope({"allowed_roots": ["sapianta_bridge"], "forbidden_roots": ["./sapianta_bridge"]})

    assert result["valid"] is False
    assert {"field": "workspace_scope", "reason": "path cannot be both allowed and forbidden"} in result["errors"]


def test_workspace_path_normalization_is_deterministic() -> None:
    assert normalize_workspace_path("./sapianta_bridge/") == "sapianta_bridge"
